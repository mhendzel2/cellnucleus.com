#!/usr/bin/env python3
"""Read-only static validation of a CellNucleus candidate; Python stdlib only.

Usage: python validate_candidate.py --root cellnucleus-candidate --output audit.json
Exit status records execution success, not an assertion of full accessibility or
scientific validation. The JSON summary contains the actual findings.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
EXCLUDED = {".git", "node_modules", ".agents", ".codex", ".aws", ".venv", ".secrets", "admin", "output", "inbox", "skills", "docs", "reports", "config", "scripts", "backup", "backups", "__pycache__"}


def is_public_path(path, root):
    parts = path.relative_to(root).parts
    return not any(part.startswith(".") or part in EXCLUDED or "genspark" in part.lower() for part in parts) and not (parts and parts[0].lower().startswith("nuclear speckles_"))


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "line": self.getpos()[0], "text": ""}
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for node in self.stack:
            node["text"] += data


def clean(text):
    return " ".join(text.split())


def audit(root):
    root = root.resolve()
    files = list(root.glob("*.html"))
    for folder in ["nuclear_biology_reviews/reviews", "hypothesis_reviews"]:
        files.extend((root / folder).rglob("*.html"))
    files = sorted(p for p in files if is_public_path(p, root))
    docs = {p: Document(p.read_text(encoding="utf-8", errors="replace")) for p in files}
    ids = {p: {n["attrs"]["id"] for n in d.nodes if n["attrs"].get("id")} | {n["attrs"]["name"] for n in d.nodes if n["tag"] == "a" and n["attrs"].get("name")} for p, d in docs.items()}
    findings = []
    pages = []
    referenced = defaultdict(set)
    external = defaultdict(set)
    citation_urls = defaultdict(set)
    stats = Counter()

    def add(path, code, detail, node=None, ref=None):
        issue = {"file": path.relative_to(root).as_posix(), "code": code, "detail": detail}
        if node:
            issue["line"] = node["line"]
        if ref is not None:
            issue["reference"] = ref
        findings.append(issue)

    for path, doc in docs.items():
        rel = path.relative_to(root).as_posix()
        title = [clean(n["text"]) for n in doc.nodes if n["tag"] == "title"]
        h1 = [clean(n["text"]) for n in doc.nodes if n["tag"] == "h1"]
        headings = [int(n["tag"][1]) for n in doc.nodes if re.fullmatch(r"h[1-6]", n["tag"])]
        if len(title) != 1 or not title[0]:
            add(path, "title", f"Expected one nonempty title; found {len(title)}")
        if len(h1) != 1:
            add(path, "h1_count", f"Expected one H1; found {len(h1)}")
        is_redirect = any(n["tag"] == "meta" and n["attrs"].get("http-equiv", "").lower() == "refresh" and "url=" in n["attrs"].get("content", "").lower() for n in doc.nodes)
        if not is_redirect and not any(n["tag"] == "main" or n["attrs"].get("role", "").lower() == "main" for n in doc.nodes):
            add(path, "missing_main_landmark", "Nonredirect page lacks a main element or role=main landmark")
        html = next((n for n in doc.nodes if n["tag"] == "html"), None)
        if not html or not html["attrs"].get("lang"):
            add(path, "missing_lang", "HTML language attribute missing")
        if not any(n["tag"] == "meta" and n["attrs"].get("name", "").lower() == "viewport" for n in doc.nodes):
            add(path, "missing_viewport", "No viewport metadata")
        for first, second in zip(headings, headings[1:]):
            if second > first + 1:
                add(path, "heading_skip", f"Heading sequence jumps H{first} to H{second}")
        for ident, count in Counter(n["attrs"]["id"] for n in doc.nodes if n["attrs"].get("id")).items():
            if count > 1:
                add(path, "duplicate_id", f"id={ident!r} occurs {count} times")
        labels = {n["attrs"].get("for") for n in doc.nodes if n["tag"] == "label" and clean(n["text"])}
        image_count = jsonld_count = 0
        for node in doc.nodes:
            tag, a = node["tag"], node["attrs"]
            if tag == "img":
                image_count += 1
                if "alt" not in a:
                    add(path, "image_alt", "Image has no alt attribute", node, a.get("src"))
            if tag == "button" and not (clean(node["text"]) or a.get("aria-label") or a.get("aria-labelledby") or a.get("title")):
                add(path, "button_name", "Button lacks a detectable accessible name", node)
            if tag in {"input", "select", "textarea"} and a.get("type", "").lower() not in {"hidden", "submit", "button", "reset", "image"}:
                if not (a.get("aria-label") or a.get("aria-labelledby") or a.get("id") in labels):
                    # Nested labels are a valid alternative; check raw text source via DOM stack is outside this lightweight check.
                    add(path, "control_label_check", "Control needs manual check for an associated accessible label", node)
            if tag == "script" and a.get("type", "").lower() == "application/ld+json":
                jsonld_count += 1
                try:
                    json.loads(node["text"])
                except (ValueError, TypeError) as exc:
                    add(path, "invalid_jsonld", str(exc), node)
            refs = []
            for attr in {"href", "src", "poster", "action", "data"}:
                if a.get(attr) and (attr != "data" or tag == "object"):
                    refs.append((attr, a[attr]))
            if a.get("srcset"):
                refs.extend(("srcset", item.strip().split()[0]) for item in a["srcset"].split(",") if item.strip())
            style_text = node["text"] if tag == "style" else a.get("style", "")
            refs.extend(("css_url", match.group(1).strip()) for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", style_text, re.I) if not match.group(1).strip().startswith("#"))
            for attr, ref in refs:
                stats["references"] += 1
                parsed = urlsplit(ref)
                if parsed.scheme in {"mailto", "tel", "javascript", "data", "blob"}:
                    stats[parsed.scheme + "_references"] += 1
                    continue
                if parsed.scheme or parsed.netloc:
                    external[ref].add(rel)
                    if re.search(r"doi\.org|pubmed\.ncbi\.nlm\.nih\.gov|pmc\.ncbi\.nlm\.nih\.gov|ncbi\.nlm\.nih\.gov/(?:pubmed|pmc)", ref, re.I):
                        citation_urls[ref].add(rel)
                    continue
                if ref == "#":
                    add(path, "placeholder_link", "Bare # link needs a working destination or explicit button behavior", node, ref)
                    continue
                urlpath = unquote(parsed.path)
                target = ((root / urlpath.lstrip("/")) if urlpath.startswith("/") else (path.parent / urlpath)) if urlpath else path
                target = target.resolve()
                try:
                    target.relative_to(root)
                except ValueError:
                    add(path, "outside_root", "Local reference escapes site root", node, ref)
                    continue
                if not target.exists():
                    add(path, "missing_target", "Local target does not exist", node, ref)
                    continue
                if target.is_dir():
                    target = target / "index.html"
                    if not target.exists():
                        stats["directory_references"] += 1
                        continue
                referenced[target].add(path)
                if parsed.fragment and target.suffix.lower() == ".html":
                    fragment = unquote(parsed.fragment)
                    if fragment not in ids.get(target, set()):
                        add(path, "missing_anchor", f"Anchor #{fragment} absent in {target.relative_to(root).as_posix()}", node, ref)
        pages.append({"file": rel, "title": title[0] if title else "", "h1": h1, "images": image_count, "jsonld_blocks": jsonld_count, "citation_link_count": sum(rel in refs for refs in citation_urls.values()), "incoming_local_files": 0})
    for page in pages:
        page["incoming_local_files"] = len(referenced[root / page["file"]])
    review_pages = [p for p in pages if p["file"].startswith(("nuclear_biology_reviews/reviews/", "hypothesis_reviews/"))]
    # Also inspect local CSS resource dependencies (font/image URLs, imports).
    for css in (root / "assets").rglob("*.css"):
        if not is_public_path(css, root):
            continue
        content = css.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", content, re.I):
            ref = match.group(1).strip()
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or ref.startswith("#"):
                continue
            target = ((root / unquote(parsed.path).lstrip("/")) if parsed.path.startswith("/") else (css.parent / unquote(parsed.path))).resolve()
            if not target.exists():
                add(css, "missing_css_target", "CSS resource target does not exist", ref=ref)
    counts = Counter(f["code"] for f in findings)
    svg_checks = []
    for path in (root / "assets").rglob("*.svg"):
        if not is_public_path(path, root):
            continue
        try:
            svg = ElementTree.parse(path).getroot()
            valid = svg.tag == "{http://www.w3.org/2000/svg}svg"
            if not valid:
                add(path, "invalid_svg_namespace", "Standalone SVG lacks the required SVG namespace")
        except (ElementTree.ParseError, OSError) as exc:
            valid = False
            add(path, "invalid_svg_xml", str(exc))
        svg_checks.append({"file": path.relative_to(root).as_posix(), "valid_xml_and_namespace": valid})
    counts = Counter(f["code"] for f in findings)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(), "root": str(root),
        "scope": "Public root HTML, nuclear_biology_reviews/reviews HTML, hypothesis_reviews HTML, and assets CSS. Saved Genspark/Nuclear Speckles exports and private/admin/dependency/output/documentation directories excluded. Local links include fragments. Static heuristics do not establish WCAG conformance or scientific validity.",
        "summary": {"html_pages": len(files), "review_pages": len(review_pages), "core_review_pages": sum(p["file"].startswith("nuclear_biology_reviews/reviews/") for p in pages), "hypothesis_review_pages": sum(p["file"].startswith("hypothesis_reviews/") for p in pages), "findings": len(findings), "by_code": dict(sorted(counts.items())), "unique_external_references": len(external), "unique_citation_urls": len(citation_urls), **dict(stats)},
        "findings": findings, "pages": pages, "svg_checks": svg_checks,
        "unreferenced_review_pages": [p["file"] for p in review_pages if p["incoming_local_files"] == 0],
        "citation_urls": [{"url": u, "files": sorted(p)} for u, p in sorted(citation_urls.items())],
        "external_urls": [{"url": u, "files": sorted(p)} for u, p in sorted(external.items())],
        "limitations": ["No HTTP verification of external links or citations in this static run", "Citation URL presence is not bibliographic identity or claim support validation", "No color contrast, keyboard, visual, or assistive technology conformance assertion", "Server-side PHP execution and actual mail delivery are not tested", "Heading/control warnings require interpretation of intended page semantics"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path(__file__).parent / "cellnucleus-candidate"
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true", help="Exit 1 for critical static errors; semantic heuristics remain warnings")
    parser.add_argument("--check-js", action="store_true", help="Parse-check all local asset JavaScript with installed Node")
    args = parser.parse_args()
    result = audit(args.root)
    critical = {"missing_target", "missing_anchor", "outside_root", "missing_css_target", "duplicate_id", "invalid_jsonld", "invalid_svg_namespace", "invalid_svg_xml", "title", "missing_lang", "missing_viewport", "image_alt"}
    result["critical_finding_count"] = sum(f["code"] in critical for f in result["findings"])
    if args.check_js:
        node = shutil.which("node")
        checks = []
        if node:
            for path in sorted((args.root / "assets").rglob("*.js")):
                check = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
                checks.append({"file": path.relative_to(args.root).as_posix(), "exit_code": check.returncode, "diagnostic": check.stderr.strip()})
        result["javascript_syntax"] = {"runtime": node, "checks": checks, "available": bool(node), "pass": bool(node) and all(c["exit_code"] == 0 for c in checks)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    if args.check_js:
        print(f"JavaScript syntax checks: {len(result['javascript_syntax']['checks'])}; pass={result['javascript_syntax']['pass']}")
    if args.strict and (result["critical_finding_count"] or (args.check_js and not result["javascript_syntax"]["pass"])):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
