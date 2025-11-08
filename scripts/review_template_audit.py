#!/usr/bin/env python3
"""Audit review template usage and original page coverage.

This script inspects the mapping in ``docs/file-mapping.json`` and evaluates
whether each mapped review file in ``reviews/`` appears to use a unique topic
rather than the placeholder "Nuclear Bodies" template. It also checks that the
legacy filenames referenced in the mapping still exist so that original
content remains accessible for redirects.

Outputs a Markdown report at ``reports/review_template_audit.md`` summarising
findings.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "docs" / "file-mapping.json"
REVIEWS_DIR = ROOT / "reviews"
REPORT_PATH = ROOT / "reports" / "review_template_audit.md"

PLACEHOLDER_TITLE = "Nuclear Bodies: Architecture and Function"
STOPWORDS = {
    "html",
    "review",
    "reviews",
    "comprehensive",
    "critical",
    "complete",
    "updated",
    "enhanced",
    "standardized",
    "standardised",
    "standard",
    "cell",
    "cells",
    "nuclear",
    "nucleus",
    "biology",
    "biological",
    "and",
    "of",
    "the",
    "for",
    "with",
    "mechanisms",
    "mechanism",
    "processes",
    "pathways",
    "proteins",
    "diseases",
    "disease",
    "analysis",
    "comprehensive",
    "complete",
    "dynamics",
}


def load_mapping() -> dict[str, str]:
    if not MAPPING_PATH.exists():
        raise SystemExit(f"Mapping file not found: {MAPPING_PATH}")
    return json.loads(MAPPING_PATH.read_text())


def slug_keywords(slug: str) -> List[str]:
    tokens = re.split(r"[-_]+", slug)
    keywords: List[str] = []
    for token in tokens:
        token = token.strip().lower()
        if not token or token in STOPWORDS:
            continue
        if token not in keywords:
            keywords.append(token)
    return keywords


def extract_tag(text: str, tag: str) -> str:
    pattern = re.compile(rf"<{tag}[^>]*>(.*?)</{tag}>", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return ""
    inner = re.sub(r"<[^>]+>", "", match.group(1))
    return " ".join(inner.split())


@dataclass
class PageIssues:
    original: str
    target: str
    title: str = ""
    h1: str = ""
    missing_keywords: List[str] | None = None
    problems: List[str] | None = None

    def add_problem(self, message: str) -> None:
        if self.problems is None:
            self.problems = []
        self.problems.append(message)


def analyse_pages(mapping: dict[str, str]) -> dict[str, List[PageIssues]]:
    placeholder_pages: List[PageIssues] = []
    keyword_mismatches: List[PageIssues] = []
    missing_targets: List[PageIssues] = []
    missing_originals: List[PageIssues] = []

    for original, target in sorted(mapping.items()):
        issues = PageIssues(original=original, target=target)

        original_path = ROOT / original
        if not original_path.exists():
            missing_originals.append(issues)

        target_path = REVIEWS_DIR / target
        if not target_path.exists():
            issues.add_problem("Target review file is missing")
            missing_targets.append(issues)
            continue

        content = target_path.read_text(encoding="utf-8", errors="ignore")
        title = extract_tag(content, "title")
        h1 = extract_tag(content, "h1")
        issues.title = title
        issues.h1 = h1

        if PLACEHOLDER_TITLE.lower() in title.lower() or PLACEHOLDER_TITLE.lower() in h1.lower():
            issues.add_problem("Title or heading still uses placeholder Nuclear Bodies copy")
            placeholder_pages.append(issues)

        keywords = slug_keywords(target)
        missing = [kw for kw in keywords if kw not in title.lower() and kw not in h1.lower()]
        seen = len(keywords) - len(missing)
        if keywords and seen < max(1, len(keywords) // 2):
            issues.missing_keywords = missing
            issues.add_problem("Key topic keywords from filename are missing in title and heading")
            keyword_mismatches.append(issues)

    return {
        "placeholder": placeholder_pages,
        "keyword_mismatches": keyword_mismatches,
        "missing_targets": missing_targets,
        "missing_originals": missing_originals,
    }




def sanitise_cell(value: str) -> str:
    return value.replace('|', r'\|')

def render_table(rows: Iterable[List[str]]) -> List[str]:
    rows = list(rows)
    if not rows:
        return ["(none)"]
    header = [sanitise_cell(cell) for cell in rows[0]]
    lines = ['|' + '|'.join(header) + '|', '|' + '|'.join(['---'] * len(header)) + '|' ]
    for row in rows[1:]:
        sanitized = [sanitise_cell(cell) for cell in row]
        lines.append('|' + '|'.join(sanitized) + '|')
    return lines


def write_report(issues: dict[str, List[PageIssues]]) -> None:
    total_mapped = len(load_mapping())
    lines: List[str] = []
    lines.append("# Review Template Consistency Audit")
    lines.append("")
    lines.append("Generated by `scripts/review_template_audit.py`.\n")

    placeholder = issues["placeholder"]
    keyword_mismatches = issues["keyword_mismatches"]
    missing_targets = issues["missing_targets"]
    missing_originals = issues["missing_originals"]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total mapped pages analysed: **{total_mapped}**")
    lines.append(f"- Pages still using placeholder copy: **{len(placeholder)}**")
    lines.append(f"- Pages with missing topic keywords: **{len(keyword_mismatches)}**")
    lines.append(f"- Missing review targets: **{len(missing_targets)}**")
    lines.append(f"- Missing original source files: **{len(missing_originals)}**")
    lines.append("")

    def section(title: str, entries: List[PageIssues], include_keywords: bool = False) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if not entries:
            lines.append("No issues detected.\n")
            return
        header = ["Original", "Target", "Title", "H1", "Notes"]
        table_rows = [header]
        for item in entries:
            note_parts: List[str] = []
            if item.problems:
                note_parts.extend(item.problems)
            if include_keywords and item.missing_keywords:
                note_parts.append("Missing keywords: " + ", ".join(sorted(item.missing_keywords)))
            notes = "; ".join(note_parts)
            table_rows.append(
                [
                    item.original,
                    f"reviews/{item.target}",
                    item.title or "(no title)",
                    item.h1 or "(no h1)",
                    notes or "",
                ]
            )
        lines.extend(render_table(table_rows))
        lines.append("")

    section("Placeholder Nuclear Bodies Templates", placeholder)
    section("Keyword Mismatches", keyword_mismatches, include_keywords=True)
    section("Missing Review Targets", missing_targets)
    section("Missing Original Source Files", missing_originals)

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    mapping = load_mapping()
    issues = analyse_pages(mapping)
    write_report(issues)


if __name__ == "__main__":
    main()
