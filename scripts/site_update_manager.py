#!/usr/bin/env python3
"""Plan and execute website follow-up actions after local file changes."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = Path("nuclear_biology_reviews/reviews")
IGNORE_PREFIXES = (
    ".git/",
    ".secrets/",
    "backup/",
    "reports/",
    "__pycache__/",
    "taskforce_submissions/",
    "skills/",
)
CATEGORY_PAGES = {
    "chromatin_architecture_dynamics_category.html",
    "epigenetics_gene_regulation_category.html",
    "nuclear_bodies_compartments_category.html",
    "dna_repair_replication_category.html",
    "nuclear_envelope_lamins_category.html",
    "nuclear_transport_dynamics_category.html",
    "nuclear_biophysics_mechanics_category.html",
    "disease_pathology_category.html",
    "reviews_index.html",
    "research_reviews_directory.html",
}
PAGE_EXTENSIONS = {".html", ".php", ".css", ".js", ".xml"}


@dataclass(frozen=True)
class PlannedAction:
    key: str
    title: str
    reason: str
    command: tuple[str, ...] | None = None
    writes_files: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--files",
        nargs="*",
        help="Explicit list of changed files, relative to the repo root. If omitted, inspect the current git worktree.",
    )
    parser.add_argument("--run", action="store_true", help="Run the planned actions instead of only printing the plan.")
    parser.add_argument("--deploy", action="store_true", help="After successful checks, deploy to Aplus.")
    return parser.parse_args()


def git_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    changed: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        changed.append(path_text)
    return changed


def normalize_paths(paths: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in paths:
        candidate = raw.strip()
        if not candidate:
            continue
        candidate = candidate.replace("\\", "/")
        while candidate.startswith("./"):
            candidate = candidate[2:]
        if candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def is_relevant_change(path: str) -> bool:
    if any(path.startswith(prefix) for prefix in IGNORE_PREFIXES):
        return False
    if path == "docs/file-mapping.json":
        return True
    if path.startswith("Reviews_useredit/"):
        return True
    if path.startswith("scripts/"):
        return True
    if path.startswith("nuclear_biology_reviews/reviews/"):
        return True
    if path == "robots.txt":
        return True
    if "/" not in path and Path(path).suffix.lower() in PAGE_EXTENSIONS:
        return True
    return False


def split_relevant_changes(paths: list[str]) -> tuple[list[str], list[str]]:
    relevant: list[str] = []
    ignored: list[str] = []
    for path in paths:
        if is_relevant_change(path):
            relevant.append(path)
        else:
            ignored.append(path)
    return relevant, ignored


def has_prefix(paths: list[str], prefix: str) -> bool:
    return any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for path in paths)


def any_suffix(paths: list[str], suffixes: set[str]) -> bool:
    return any(Path(path).suffix.lower() in suffixes for path in paths)


def add_action(actions: list[PlannedAction], seen: set[str], action: PlannedAction) -> None:
    if action.key in seen:
        return
    seen.add(action.key)
    actions.append(action)


def build_plan(changed_files: list[str], deploy_requested: bool) -> list[PlannedAction]:
    actions: list[PlannedAction] = []
    seen: set[str] = set()

    page_change = any_suffix(changed_files, PAGE_EXTENSIONS)
    review_page_change = has_prefix(changed_files, str(REVIEW_DIR))
    source_doc_change = has_prefix(changed_files, "Reviews_useredit")
    mapping_change = "docs/file-mapping.json" in changed_files
    catalog_generator_change = "scripts/generate_catalog_pages.py" in changed_files
    summary_generator_change = "scripts/regenerate_review_summaries.py" in changed_files
    template_audit_change = "scripts/review_template_audit.py" in changed_files
    link_audit_change = "scripts/site_link_audit.py" in changed_files
    php_change = any(Path(path).suffix.lower() == ".php" for path in changed_files)
    direct_catalog_page_change = any(Path(path).name in CATEGORY_PAGES for path in changed_files)

    if source_doc_change or mapping_change or summary_generator_change:
        add_action(
            actions,
            seen,
            PlannedAction(
                key="review-refresh",
                title="Refresh review summaries from Word sources",
                reason="Source documents, mapping rules, or the review regeneration script changed.",
                command=(sys.executable, "scripts/regenerate_review_summaries.py"),
                writes_files=True,
            ),
        )
        add_action(
            actions,
            seen,
            PlannedAction(
                key="review-template-audit",
                title="Audit review template/topic consistency",
                reason="Source-linked review pages may need a post-refresh template check.",
                command=(sys.executable, "scripts/review_template_audit.py"),
            ),
        )

    if review_page_change or catalog_generator_change or direct_catalog_page_change:
        add_action(
            actions,
            seen,
            PlannedAction(
                key="catalog-regeneration",
                title="Regenerate catalog and category pages",
                reason="Review pages, category pages, or the catalog generator changed.",
                command=(sys.executable, "scripts/generate_catalog_pages.py"),
                writes_files=True,
            ),
        )

    if page_change or source_doc_change or mapping_change or link_audit_change or catalog_generator_change:
        add_action(
            actions,
            seen,
            PlannedAction(
                key="link-audit",
                title="Audit site links and page discoverability",
                reason="Public-facing files or generators changed, so navigation and local links should be rechecked.",
                command=(sys.executable, "scripts/site_link_audit.py"),
            ),
        )

    if php_change:
        if shutil.which("php"):
            for path in changed_files:
                if Path(path).suffix.lower() != ".php":
                    continue
                add_action(
                    actions,
                    seen,
                    PlannedAction(
                        key=f"php-lint:{path}",
                        title=f"Lint PHP endpoint {path}",
                        reason="PHP file changed and local PHP is available.",
                        command=("php", "-l", path),
                    ),
                )
        else:
            add_action(
                actions,
                seen,
                PlannedAction(
                    key="php-lint-unavailable",
                    title="Manual PHP syntax check required",
                    reason="A PHP file changed but `php` is not installed in this environment.",
                ),
            )

    if deploy_requested:
        add_action(
            actions,
            seen,
            PlannedAction(
                key="deploy",
                title="Deploy the updated site to Aplus",
                reason="Deployment was explicitly requested.",
                command=(sys.executable, "scripts/deploy_to_aplus.py"),
            ),
        )

    return actions


def print_plan(changed_files: list[str], ignored_files: list[str], actions: list[PlannedAction]) -> None:
    print(f"Relevant changed files detected: {len(changed_files)}")
    for path in changed_files:
        print(f"- {path}")
    if ignored_files:
        print(f"\nIgnored non-site changes: {len(ignored_files)}")

    if not actions:
        print("\nNo follow-up actions were triggered.")
        return

    print(f"\nPlanned actions: {len(actions)}")
    for index, action in enumerate(actions, start=1):
        write_label = "writes files" if action.writes_files else "check only"
        print(f"{index}. {action.title} [{write_label}]")
        print(f"   Reason: {action.reason}")
        if action.command:
            print("   Command: " + " ".join(action.command))
        else:
            print("   Command: manual review")


def run_actions(actions: list[PlannedAction]) -> int:
    for action in actions:
        if not action.command:
            print(f"\nSKIP: {action.title}")
            print(action.reason)
            continue

        print(f"\nRUN: {action.title}")
        result = subprocess.run(action.command, cwd=ROOT)
        if result.returncode != 0:
            print(f"Action failed with exit code {result.returncode}: {' '.join(action.command)}")
            return result.returncode
    return 0


def main() -> int:
    args = parse_args()
    changed_files, ignored_files = split_relevant_changes(normalize_paths(args.files or git_changed_files()))
    actions = build_plan(changed_files, args.deploy)
    print_plan(changed_files, ignored_files, actions)

    if not args.run:
        return 0
    return run_actions(actions)


if __name__ == "__main__":
    raise SystemExit(main())
