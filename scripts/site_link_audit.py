#!/usr/bin/env python3
"""Audit local HTML links and review-page discoverability."""

from __future__ import annotations

from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "nuclear_biology_reviews" / "reviews"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"a", "link"} and attrs_dict.get("href"):
            self.links.append(("href", attrs_dict["href"]))
        if tag in {"img", "script", "iframe", "source"} and attrs_dict.get("src"):
            self.links.append(("src", attrs_dict["src"]))


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "backup" not in path.parts
    )


def parse_links(path: Path) -> list[tuple[str, str]]:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser.links


def is_local_reference(ref: str) -> bool:
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return False
    parsed = urlparse(ref)
    return parsed.scheme == ""


def audit() -> tuple[list[tuple[str, str, str]], dict[str, int], list[str]]:
    issues: list[tuple[str, str, str]] = []
    linked_reviews: set[str] = set()
    placeholder_counter: Counter[str] = Counter()

    for path in html_files():
        for kind, ref in parse_links(path):
            if ref == "#":
                placeholder_counter[str(path.relative_to(ROOT))] += 1
                continue
            if not is_local_reference(ref):
                continue

            target = (path.parent / unquote(urlparse(ref).path)).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                issues.append((str(path.relative_to(ROOT)), ref, "outside-root"))
                continue

            if not target.exists():
                issues.append((str(path.relative_to(ROOT)), ref, "missing"))
                continue

            if target.is_relative_to(REVIEW_DIR):
                linked_reviews.add(target.name)

    orphaned_reviews = sorted(
        path.name for path in REVIEW_DIR.glob("*.html") if path.name not in linked_reviews
    )

    return issues, dict(placeholder_counter), orphaned_reviews


def main() -> None:
    issues, placeholders, orphaned_reviews = audit()
    print(f"HTML files audited: {len(html_files())}")
    print(f"Local link issues: {len(issues)}")
    print(f"Files with '#' placeholders: {len(placeholders)}")
    print(f"Orphaned review pages: {len(orphaned_reviews)}")

    if issues:
        print("\nLocal link issues:")
        for file_path, ref, issue_type in issues:
            print(f"- {file_path}: {ref} [{issue_type}]")

    if placeholders:
        print("\nPlaceholder links by file:")
        for file_path, count in sorted(placeholders.items()):
            print(f"- {file_path}: {count}")

    if orphaned_reviews:
        print("\nOrphaned review pages:")
        for name in orphaned_reviews:
            print(f"- {name}")


if __name__ == "__main__":
    main()
