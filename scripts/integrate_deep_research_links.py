#!/usr/bin/env python3
"""Integrate Deep Research source links into review pages.

This script:
1) Reads the existing page-to-review mapping YAML.
2) Updates each mapped review page with:
   - Online "Read & Suggest" link to the source DOCX viewer.
   - Direct DOCX download link for the full review.
3) Injects a Deep Research source action panel for pages that do not use
   the shared collaboration block template.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote, urlencode

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "nuclear_biology_reviews" / "reviews"
DEFAULT_MAP_PATH = Path("/mnt/c/Users/mjhen/Github/Agent0/agent-zero/usr/workdir/cellnucleus_site/review_page_match_map.yaml")

MAP_ENTRY_RE = re.compile(
    r'^\s*-\s*page_path:\s*"([^"]+)"\s*\n'
    r'\s*matched_review_document:\s*"([^"]+)"\s*\n'
    r"\s*confidence:\s*([a-z]+)",
    re.MULTILINE,
)

TEMPLATE_EDIT_RE = re.compile(
    r'(<a href=")[^"]*(" class="inline-flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors")'
)
TEMPLATE_DOWNLOAD_RE = re.compile(
    r'(<a href=")[^"]*(" class="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors")'
)

ACTIN_EDIT_RE = re.compile(
    r'(<a href=")[^"]*("(\s*\n\s*)class="bg-white text-blue-600 px-4 py-2 rounded font-medium hover:bg-gray-100")'
)
ACTIN_SUGGEST_BUTTON_RE = re.compile(
    r'<button class="bg-blue-700 px-4 py-2 rounded font-medium hover:bg-blue-800">\s*'
    r'<i class="fas fa-comments mr-2"></i>Suggest Changes\s*</button>',
    re.DOTALL,
)


def _win_path_name(raw: str) -> str:
    return raw.replace("\\", "/").split("/")[-1]


def load_mapping(map_path: Path) -> dict[str, dict[str, str]]:
    text = map_path.read_text(encoding="utf-8", errors="ignore")
    mapping: dict[str, dict[str, str]] = {}
    for page_path, review_doc_path, confidence in MAP_ENTRY_RE.findall(text):
        page_name = _win_path_name(page_path)
        doc_name = _win_path_name(review_doc_path)
        mapping[page_name] = {
            "doc_name": doc_name,
            "confidence": confidence.lower(),
            "page_rel": f"nuclear_biology_reviews/reviews/{page_name}",
        }
    return mapping


def build_links(page_name: str, doc_name: str, confidence: str) -> tuple[str, str]:
    doc_rel = f"Reviews_useredit/{doc_name}"
    query = urlencode(
        {
            "doc": doc_rel,
            "page": f"nuclear_biology_reviews/reviews/{page_name}",
            "confidence": confidence,
            "source": "deep_research",
        }
    )
    viewer_href = f"../../review_source_viewer.html?{query}"
    download_href = f"../../{quote(doc_rel, safe='/')}"
    return viewer_href, download_href


def inject_ai_source_note(text: str, viewer_href: str, download_href: str, confidence: str) -> tuple[str, bool]:
    if "Deep Research source document:" in text:
        return text, False

    marker = "All scientific interpretations remain under expert human supervision."
    marker_index = text.find(marker)
    if marker_index == -1:
        return text, False

    p_close = text.find("</p>", marker_index)
    if p_close == -1:
        return text, False

    note = (
        '\n                    <p class="mt-3 text-purple-700">\n'
        "                        <strong>Deep Research source document:</strong>\n"
        f'                        <a href="{viewer_href}" class="underline">Read online</a>\n'
        '                        <span class="mx-1">|</span>\n'
        f'                        <a href="{download_href}" class="underline" download>Download .docx</a>\n'
        '                        <span class="mx-1">|</span>\n'
        f"                        Match confidence: {confidence}\n"
        "                    </p>"
    )
    updated = text[: p_close + 4] + note + text[p_close + 4 :]
    return updated, True


def patch_template_block(text: str, viewer_href: str, download_href: str) -> tuple[str, bool]:
    changed = False
    text, n1 = TEMPLATE_EDIT_RE.subn(rf"\1{viewer_href}\2", text, count=1)
    if n1:
        changed = True
        text = text.replace("Edit in Google Docs", "Read & Suggest Online", 1)
        text = text.replace("Edit Document", "Read & Suggest Online", 1)

    text, n2 = TEMPLATE_DOWNLOAD_RE.subn(rf"\1{download_href}\2", text, count=1)
    if n2:
        changed = True
        text = text.replace("Download PDF", "Download Full Review (.docx)", 1)
        text = text.replace("Download Full Review (.docx) (.docx)", "Download Full Review (.docx)")

    return text, changed


def patch_actin_banner(text: str, viewer_href: str, download_href: str) -> tuple[str, bool]:
    if "Community Editing Available" not in text:
        return text, False

    changed = False
    text, n1 = ACTIN_EDIT_RE.subn(rf'\1{viewer_href}\2', text, count=1)
    if n1:
        changed = True
        text = text.replace("Edit Document", "Read & Suggest Online", 1)

    replacement = (
        f'<a href="{viewer_href}#suggestion-form" class="bg-blue-700 px-4 py-2 rounded font-medium hover:bg-blue-800">\n'
        '                        <i class="fas fa-comments mr-2"></i>Suggest Correction\n'
        "                    </a>\n"
        f'                    <a href="{download_href}" download class="bg-blue-800 px-4 py-2 rounded font-medium hover:bg-blue-900">\n'
        '                        <i class="fas fa-download mr-2"></i>Download Full Review (.docx)\n'
        "                    </a>"
    )
    text, n2 = ACTIN_SUGGEST_BUTTON_RE.subn(replacement, text, count=1)
    if n2:
        changed = True

    # Keep footer action consistent with source file download.
    if "Download PDF" in text:
        text = text.replace('href="../../downloads.html" class="text-gray-400 hover:text-white">\n                    <i class="fas fa-download mr-2"></i>Download PDF', f'href="{download_href}" class="text-gray-400 hover:text-white">\n                    <i class="fas fa-download mr-2"></i>Download Full Review (.docx)', 1)
        changed = True

    return text, changed


def inject_fallback_action_panel(
    text: str,
    page_name: str,
    viewer_href: str,
    download_href: str,
    doc_name: str,
    confidence: str,
) -> tuple[str, bool]:
    if "id=\"deep-research-actions\"" in text or "Deep Research source document:" in text:
        return text, False

    panel = f"""

    <!-- Deep Research Source Actions -->
    <section id="deep-research-actions" class="bg-white border-b border-slate-200">
        <div class="max-w-6xl mx-auto px-4 py-5">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <h2 class="text-lg font-semibold text-slate-900">Deep Research Source Review</h2>
                <p class="mt-2 text-sm text-slate-700">
                    This page is linked to its matched long-form source review. Read online and submit correction suggestions, or download the full document.
                </p>
                <p class="mt-2 text-xs text-slate-600">
                    Source file: {doc_name} | Match confidence: {confidence}
                </p>
                <div class="mt-4 flex flex-wrap gap-3">
                    <a href="{viewer_href}" class="inline-flex items-center rounded-md bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700">
                        <i class="fas fa-book-open mr-2"></i>Read & Suggest Online
                    </a>
                    <a href="{viewer_href}#suggestion-form" class="inline-flex items-center rounded-md border border-emerald-700 px-3 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50">
                        <i class="fas fa-pen-to-square mr-2"></i>Suggest Correction
                    </a>
                    <a href="{download_href}" download class="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700">
                        <i class="fas fa-download mr-2"></i>Download Full Review (.docx)
                    </a>
                </div>
            </div>
        </div>
    </section>
"""

    insert_points = [
        "</header>",
        "<main",
    ]
    for marker in insert_points:
        idx = text.find(marker)
        if idx != -1:
            if marker == "</header>":
                return text[: idx + len(marker)] + panel + text[idx + len(marker) :], True
            return text[:idx] + panel + text[idx:], True

    body_match = re.search(r"<body[^>]*>", text)
    if body_match:
        idx = body_match.end()
        return text[:idx] + panel + text[idx:], True

    return text, False


def normalize(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def process_page(page_path: Path, page_meta: dict[str, str], dry_run: bool) -> tuple[bool, str]:
    page_name = page_path.name
    doc_name = page_meta["doc_name"]
    confidence = page_meta["confidence"]
    viewer_href, download_href = build_links(page_name, doc_name, confidence)

    original = page_path.read_text(encoding="utf-8", errors="ignore")
    text = original
    changed = False
    update_mode = "fallback"

    if "Community Research & Collaboration" in text:
        text, c1 = patch_template_block(text, viewer_href, download_href)
        text, c2 = inject_ai_source_note(text, viewer_href, download_href, confidence)
        changed = c1 or c2
        update_mode = "template"
    else:
        text, c3 = patch_actin_banner(text, viewer_href, download_href)
        changed = c3
        update_mode = "actin_banner" if c3 else "fallback"

    if not changed:
        text, c4 = inject_fallback_action_panel(
            text,
            page_name=page_name,
            viewer_href=viewer_href,
            download_href=download_href,
            doc_name=doc_name,
            confidence=confidence,
        )
        changed = c4
        if c4:
            update_mode = "fallback"

    text = normalize(text)
    if changed and text != original and not dry_run:
        page_path.write_text(text, encoding="utf-8")
    return changed and text != original, update_mode


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject deep research source links into review pages.")
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP_PATH, help="Path to review_page_match_map.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes")
    args = parser.parse_args()

    if not args.map.exists():
        raise FileNotFoundError(f"Mapping file not found: {args.map}")

    mapping = load_mapping(args.map)
    if not mapping:
        raise RuntimeError(f"No mappings parsed from: {args.map}")

    changed_count = 0
    missing_count = 0
    mode_counts: dict[str, int] = {"template": 0, "actin_banner": 0, "fallback": 0}

    for page_name, meta in sorted(mapping.items()):
        page_path = REVIEW_DIR / page_name
        if not page_path.exists():
            missing_count += 1
            continue
        changed, mode = process_page(page_path, meta, dry_run=args.dry_run)
        if changed:
            changed_count += 1
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

    print(
        f"processed={len(mapping)} changed={changed_count} missing={missing_count} "
        f"template={mode_counts.get('template', 0)} "
        f"actin_banner={mode_counts.get('actin_banner', 0)} "
        f"fallback={mode_counts.get('fallback', 0)}"
    )


if __name__ == "__main__":
    main()
