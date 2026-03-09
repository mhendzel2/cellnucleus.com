#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "workforce_naming.json"
TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".md",
    ".php",
    ".py",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {
    ".git",
    ".secrets",
    "__pycache__",
    "backup",
    "taskforce_submissions",
}
EXCLUDED_PATHS = {
    CONFIG_PATH.relative_to(REPO_ROOT),
}


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if rel_path in EXCLUDED_PATHS:
            continue
        if any(part in EXCLUDED_PARTS for part in rel_path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        yield rel_path


def build_banned_strings(config: dict) -> list[str]:
    banned = list(config["banned_public_labels"])
    for skill in config["skills"].values():
        banned.extend(skill["legacy_ids"])
    banned.extend(config["queues"]["legacy_aliases"].keys())
    return sorted(set(banned))


def main() -> int:
    config = load_config()
    banned_strings = build_banned_strings(config)
    problems: list[tuple[Path, list[str]]] = []

    for rel_path in iter_text_files(REPO_ROOT):
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8", errors="ignore")
        hits = [token for token in banned_strings if token in text]
        if hits:
            problems.append((rel_path, hits))

    if problems:
        print("workforce_naming_audit: stale names found")
        for rel_path, hits in problems:
            print(f"- {rel_path}: {', '.join(hits)}")
        return 1

    print("workforce_naming_audit: ok")
    print(f"checked_files {sum(1 for _ in iter_text_files(REPO_ROOT))}")
    print(f"canonical_skill_ids {len(config['skills'])}")
    print(f"canonical_queues {len(config['queues']['canonical'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
