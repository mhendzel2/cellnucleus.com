#!/usr/bin/env python3
"""Regenerate thin review pages from their matched Word review sources."""

from __future__ import annotations

import argparse
import difflib
import html
import math
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "nuclear_biology_reviews" / "reviews"
DOC_DIR = ROOT / "Reviews_useredit"
REPORT_PATH = ROOT / "reports" / "review_content_audit.md"

PLACEHOLDER_TITLE = "Nuclear Bodies: Architecture and Function"
WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

STOPWORDS = {
    "a",
    "about",
    "academic",
    "across",
    "analysis",
    "and",
    "biology",
    "cell",
    "cells",
    "complete",
    "comprehensive",
    "corrected",
    "critical",
    "detailed",
    "edited",
    "edit",
    "enhanced",
    "evaluation",
    "for",
    "from",
    "full",
    "function",
    "functions",
    "in",
    "literature",
    "mechanisms",
    "mechanism",
    "of",
    "outline",
    "overview",
    "paper",
    "pathways",
    "principles",
    "regulation",
    "report",
    "review",
    "standardized",
    "standardised",
    "structure",
    "summary",
    "the",
    "through",
    "update",
    "updated",
}

TOKEN_REPLACEMENTS = {
    "bodies": "body",
    "body": "body",
    "cells": "cell",
    "condensates": "condensate",
    "controversial": "controversy",
    "controversies": "controversy",
    "diseases": "disease",
    "dynamics": "dynamic",
    "genes": "gene",
    "interactions": "interaction",
    "lamins": "lamin",
    "nuclei": "nuclear",
    "nucleus": "nuclear",
    "organelles": "organelle",
    "paraspeckles": "paraspeckle",
    "pathologies": "pathology",
    "properties": "property",
    "reviews": "review",
    "rnps": "rnp",
    "speckles": "speckle",
    "structures": "structure",
    "therapies": "therapy",
}

MANUAL_DOC_MAP = {
    "chromatin-architecture-dynamics-review.html": "Chromatin Dynamics in Health, Cancer.docx",
    "chromatin_architecture_standardized_review.html": "Chromatin Dynamics in Health, Cancer.docx",
    "cajal-bodies-comprehensive-review.html": "Cajal Bodies_ Comprehensive Academic Review_.docx",
    "current_dna_repair_review.html": "DNA Repair Pathway Crosstalk Review.docx",
    "enhanced_nuclear_biophysics_comprehensive_review.html": "Nuclear Biophysics Comprehensive Review_.docx",
    "hdac_superfamily_standardized_review.html": "HDAC Review and Infographic Generation_.docx",
    "heterochromatin-comprehensive-review.html": "Heterochromatin Review_ Depth and Citations.docx",
    "heterochromatin-comprehensive-review-timeline.html": "Heterochromatin Review_ Depth and Citations.docx",
    "h1-pcg-h3k27me3-regulation-review.html": "H1, PcG, and H3K27me3 Regulation.docx",
    "histone-ptms-neurodegeneration-review.html": "Histone PTMs in Neurodegeneration_.docx",
    "live-cell-transcription-imaging-review.html": "Live-cell imaging of transcription.docx",
    "nuclear-biophysical-properties-review.html": "Nuclear Biophysics_ Recent Decade Review_.docx",
    "nuclear-biology-controversies-review.html": "Controversies in Cell Nucleus Biology.docx",
    "nuclear-bodies-comprehensive-review.html": "Nuclear Bodies_ Review and Update_.docx",
    "nuclear-bodies-standardized.html": "Nuclear Bodies_ Review and Update_.docx",
    "nuclear-envelope-comprehensive-review.html": "Nuclear Envelope_ Structure and Dynamics.docx",
    "nuclear-lamina-comprehensive-review.html": "Lamina_ Structure, Function, and Disease_.docx",
    "nuclear-stress-response-review.html": "Nuclear Stress Response Review.docx",
    "nuclear_biophysics_comprehensive_review.html": "Nuclear Biophysics Comprehensive Review_.docx",
    "nuclear_body_biophysics_comprehensive_review.html": "Nuclear Body Biophysics Review_.docx",
    "nuclear_bodies_standardized_review.html": "Nuclear Bodies_ Review and Update_.docx",
    "nucleolus-comprehensive-review.html": "Nucleolus_ Cell Biology and Biochemistry.docx",
    "nucleolus_standardized_review.html": "Nucleolus_ Cell Biology and Biochemistry.docx",
    "paraspeckles-comprehensive-review.html": "Paraspeckle Biology, Function, Regulation.docx",
    "paraspeckles-standardized.html": "Paraspeckle Biology, Function, Regulation.docx",
    "parylation-dynamics-interactions-review.html": "PARylation Dynamics and Interactions_.docx",
    "phase-separation-nucleus-review.html": "Phase Separation in the Nucleus.docx",
    "pml-nuclear-bodies-comprehensive-review.html": "PML Bodies_ Biology and Function.docx",
    "pol-ii-condensate-review.html": "Pol II Condensate Review Outline_.docx",
    "transcriptional-condensates-comprehensive-review.html": "Transcriptional Condensates_ Models and Functions.docx",
}


@dataclass
class Paragraph:
    style: str
    text: str


@dataclass
class Section:
    heading: str
    anchor: str
    summary: list[str] = field(default_factory=list)
    subheadings: list[str] = field(default_factory=list)


@dataclass
class DocMeta:
    path: Path
    filename: str
    title: str
    display_title: str
    subtitle: str
    abstract: list[str]
    sections: list[Section]
    tokens: set[str]
    word_count: int


@dataclass
class PageResult:
    page: str
    placeholder: bool
    previous_doc: str
    selected_doc: str
    confidence: str
    action: str
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Inspect and report without writing files.")
    return parser.parse_args()


def normalize_token(token: str) -> str:
    token = token.lower().strip("._- ")
    token = TOKEN_REPLACEMENTS.get(token, token)
    if len(token) > 4 and token.endswith("ies"):
        token = token[:-3] + "y"
    elif len(token) > 4 and token.endswith("es"):
        token = token[:-2]
    elif len(token) > 4 and token.endswith("s"):
        token = token[:-1]
    return TOKEN_REPLACEMENTS.get(token, token)


def tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9]+", text.replace("H3K27me3", "H3K27me3 ").replace("mRNA", "mRNA "))
    tokens: list[str] = []
    for raw in raw_tokens:
        token = normalize_token(raw)
        if not token or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def slug_topic(page_name: str) -> str:
    stem = Path(page_name).stem
    stem = re.sub(
        r"(?i)(?:[-_](?:comprehensive|critical|complete|updated|enhanced|standardized|standardised|corrected|review))+$",
        "",
        stem,
    )
    return stem.replace("_", " ").replace("-", " ")


def title_case_slug(page_name: str) -> str:
    replacements = {
        "4d": "4D",
        "3d": "3D",
        "dna": "DNA",
        "rna": "RNA",
        "mrna": "mRNA",
        "rnp": "RNP",
        "pml": "PML",
        "ii": "II",
        "hdac": "HDAC",
        "h1": "H1",
        "h3k27me3": "H3K27me3",
        "pcg": "PcG",
        "esi": "ESI",
        "fpc": "FPC",
    }
    words = slug_topic(page_name).split()
    titled: list[str] = []
    for word in words:
        lowered = word.lower()
        titled.append(replacements.get(lowered, word.capitalize()))
    return " ".join(titled)


def sentence_trim(text: str, max_chars: int = 1800, max_sentences: int = 8) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        return " ".join(sentences[:max_sentences]).strip()
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    selected = " ".join(sentences[:max_sentences]).strip()
    if len(selected) <= max_chars:
        return selected
    truncated = selected[: max_chars - 1].rsplit(" ", 1)[0].rstrip(" ,;:")
    return truncated + "..."


def extract_paragraphs(doc_path: Path) -> list[Paragraph]:
    with ZipFile(doc_path) as docx_zip:
        root = ET.fromstring(docx_zip.read("word/document.xml"))
    paragraphs: list[Paragraph] = []
    for paragraph in root.findall(".//w:body/w:p", WORD_NS):
        style = ""
        p_props = paragraph.find("w:pPr", WORD_NS)
        if p_props is not None:
            style_el = p_props.find("w:pStyle", WORD_NS)
            if style_el is not None:
                style = style_el.attrib.get(f"{{{WORD_NS['w']}}}val", "")
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NS)).strip()
        text = " ".join(text.split())
        if text:
            paragraphs.append(Paragraph(style=style, text=text))
    return paragraphs


def split_title(title: str, page_name: str) -> tuple[str, str]:
    cleaned = re.sub(
        r"^(?:An|A|The)\s+(?:Academic|Comprehensive|Critical)?\s*Review\s+of(?:\s+the)?\s+",
        "",
        title,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"^(?:An|A)\s+Academic\s+Review\s+of(?:\s+the)?\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(?:Comprehensive|Critical)\s+Review\s+of(?:\s+the)?\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" :")
    if ":" in cleaned:
        head, tail = [part.strip() for part in cleaned.split(":", 1)]
        if head and tail:
            return head, tail
    return cleaned or title_case_slug(page_name), ""


def doc_sort_key(path: Path) -> tuple[int, int, int, str]:
    name = path.name
    return (
        "(1)" in name or "(2)" in name,
        name.count("_"),
        len(name),
        name.lower(),
    )


def extract_doc_meta(doc_path: Path, page_name: str) -> DocMeta:
    paragraphs = extract_paragraphs(doc_path)
    title = next((p.text for p in paragraphs if p.style == "Heading1"), "")
    if not title and paragraphs:
        title = paragraphs[0].text
    display_title, subtitle = split_title(title, page_name)

    abstract: list[str] = []
    abstract_started = False
    for index, paragraph in enumerate(paragraphs):
        if paragraph.text.lower() == "abstract":
            abstract_started = True
            continue
        if abstract_started and paragraph.style.startswith("Heading"):
            break
        if abstract_started:
            abstract.append(sentence_trim(paragraph.text, max_chars=1600, max_sentences=8))
        if len(abstract) >= 2:
            break
    if not abstract:
        body_paragraphs = [p.text for p in paragraphs if not p.style.startswith("Heading")]
        abstract = [sentence_trim(text, max_chars=1600, max_sentences=8) for text in body_paragraphs[:2]]

    sections: list[Section] = []
    current: Section | None = None
    intro_buffer: list[str] = []
    subsection_buffer: list[str] = []
    for paragraph in paragraphs:
        if paragraph.style == "Heading2":
            if current:
                current.summary = [sentence_trim(text) for text in intro_buffer[:2]]
                current.subheadings = subsection_buffer[:6]
                sections.append(current)
            current = Section(heading=paragraph.text, anchor=slugify(paragraph.text))
            intro_buffer = []
            subsection_buffer = []
            continue
        if paragraph.style == "Heading3":
            if current:
                subsection_buffer.append(paragraph.text)
            continue
        if current and not paragraph.style.startswith("Heading"):
            intro_buffer.append(paragraph.text)
    if current:
        current.summary = [sentence_trim(text) for text in intro_buffer[:2]]
        current.subheadings = subsection_buffer[:6]
        sections.append(current)

    filtered_sections = [section for section in sections if section.summary or section.subheadings]
    tokens = set(tokenize(doc_path.stem + " " + title + " " + display_title))
    word_count = sum(len(paragraph.text.split()) for paragraph in paragraphs)
    return DocMeta(
        path=doc_path,
        filename=doc_path.name,
        title=title or title_case_slug(page_name),
        display_title=display_title or title_case_slug(page_name),
        subtitle=subtitle,
        abstract=abstract[:2],
        sections=filtered_sections[:8],
        tokens=tokens,
        word_count=word_count,
    )


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def candidate_docs() -> dict[str, DocMeta]:
    metas: dict[str, DocMeta] = {}
    for doc_path in sorted(DOC_DIR.glob("*.docx"), key=doc_sort_key):
        metas[doc_path.name] = extract_doc_meta(doc_path, page_name="")
    return metas


def current_doc_name(page_text: str) -> str:
    viewer_match = re.search(r"review_source_viewer\.html\?[^\"']*doc=([^&\"'#]+)", page_text)
    if viewer_match:
        return Path(urllib.parse.unquote_plus(viewer_match.group(1))).name
    download_match = re.search(r"Reviews_useredit/([^\"']+\.docx)", page_text)
    if download_match:
        return Path(urllib.parse.unquote_plus(download_match.group(1))).name
    return ""


def extract_html_title_and_h1(page_text: str) -> tuple[str, str]:
    title_match = re.search(r"<title>(.*?)</title>", page_text, flags=re.IGNORECASE | re.DOTALL)
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", page_text, flags=re.IGNORECASE | re.DOTALL)
    title = html.unescape(re.sub(r"<[^>]+>", "", title_match.group(1))).strip() if title_match else ""
    h1 = html.unescape(re.sub(r"<[^>]+>", "", h1_match.group(1))).strip() if h1_match else ""
    return title, h1


def is_placeholder_page(page_text: str) -> bool:
    if "Source-Based Review Summary" in page_text and "This page now summarizes the matched Word review" in page_text:
        return False
    title, h1 = extract_html_title_and_h1(page_text)
    body_words = len(re.sub(r"<[^>]+>", " ", page_text).split())
    return (
        PLACEHOLDER_TITLE.lower() in title.lower()
        or PLACEHOLDER_TITLE.lower() in h1.lower()
        or ("Additional content would go here" in page_text)
        or body_words < 550
    )


def score_doc(page_name: str, doc: DocMeta) -> float:
    manual_doc = MANUAL_DOC_MAP.get(page_name)
    if manual_doc and manual_doc == doc.filename:
        return 100.0

    page_tokens = set(tokenize(slug_topic(page_name)))
    if not page_tokens:
        return 0.0

    overlap = len(page_tokens & doc.tokens)
    coverage = overlap / len(page_tokens)
    ordered_page = " ".join(tokenize(slug_topic(page_name)))
    ordered_doc = " ".join(tokenize(doc.filename + " " + doc.title))
    ratio = difflib.SequenceMatcher(None, ordered_page, ordered_doc).ratio()
    return coverage * 10 + ratio * 4 + overlap


def match_doc(page_name: str, docs: dict[str, DocMeta]) -> tuple[DocMeta, str, float]:
    if MANUAL_DOC_MAP.get(page_name):
        doc = docs[MANUAL_DOC_MAP[page_name]]
        return doc, "high", 100.0

    ranked = sorted(((score_doc(page_name, doc), doc) for doc in docs.values()), key=lambda item: item[0], reverse=True)
    best_score, best_doc = ranked[0]
    confidence = "low"
    if best_score >= 12:
        confidence = "high"
    elif best_score >= 8:
        confidence = "medium"
    return best_doc, confidence, best_score


def meta_description(doc: DocMeta) -> str:
    if doc.abstract:
        return sentence_trim(" ".join(doc.abstract), max_chars=155, max_sentences=2)
    return sentence_trim(doc.title, max_chars=155, max_sentences=1)


def build_links(page_name: str, doc_name: str, confidence: str) -> tuple[str, str, str]:
    doc_rel = f"Reviews_useredit/{doc_name}"
    viewer_query = urllib.parse.urlencode(
        {
            "doc": doc_rel,
            "page": f"nuclear_biology_reviews/reviews/{page_name}",
            "confidence": confidence,
            "source": "deep_research",
        }
    )
    viewer_href = f"../../review_source_viewer.html?{viewer_query}"
    suggest_href = viewer_href + "#suggestion-form"
    download_href = f"../../{urllib.parse.quote(doc_rel, safe='/')}"
    return viewer_href, suggest_href, download_href


def render_summary_page(page_name: str, doc: DocMeta, confidence: str) -> str:
    viewer_href, suggest_href, download_href = build_links(page_name, doc.filename, confidence)
    description = meta_description(doc)
    section_links = "\n".join(
        f'                            <a href="#{section.anchor}" class="rounded-full border border-slate-300 px-3 py-1 text-sm text-slate-700 hover:border-teal-600 hover:text-teal-700">{html.escape(section.heading)}</a>'
        for section in doc.sections
    )
    section_blocks = []
    for index, section in enumerate(doc.sections, start=1):
        summary_html = "\n".join(
            f'                            <p class="text-slate-700 leading-7">{html.escape(paragraph)}</p>'
            for paragraph in section.summary[:2]
        )
        subsection_html = ""
        if section.subheadings:
            chips = "\n".join(
                f'                                <li class="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">{html.escape(subheading)}</li>'
                for subheading in section.subheadings
            )
            subsection_html = f"""
                        <div class="mt-5">
                            <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Key subtopics</h3>
                            <ul class="mt-3 flex flex-wrap gap-2">
{chips}
                            </ul>
                        </div>"""
        section_blocks.append(
            f"""
                <section id="{section.anchor}" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div class="flex items-start justify-between gap-4">
                        <div>
                            <p class="text-sm font-semibold uppercase tracking-wide text-teal-700">Section {index}</p>
                            <h2 class="mt-2 text-2xl font-semibold text-slate-900">{html.escape(section.heading)}</h2>
                        </div>
                    </div>
                    <div class="mt-5 space-y-4">
{summary_html}
                    </div>{subsection_html}
                </section>"""
        )
    section_markup = "\n".join(section_blocks)
    abstract_markup = "\n".join(
        f'                        <p class="text-slate-700 leading-7">{html.escape(paragraph)}</p>' for paragraph in doc.abstract
    )
    reading_time = max(1, math.ceil(doc.word_count / 250))
    subtitle = doc.subtitle or "Concise summary of the matched long-form review document"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(doc.display_title)} | Nuclear Biology Reviews</title>
    <meta name="description" content="{html.escape(description)}">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .hero-gradient {{ background: linear-gradient(135deg, #0f766e 0%, #164e63 55%, #1e293b 100%); }}
        .section-grid {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900">
    <header class="hero-gradient text-white">
        <div class="mx-auto max-w-6xl px-4 py-10">
            <nav class="flex flex-wrap items-center gap-4 text-sm text-teal-100">
                <a href="../../index.html" class="hover:text-white">Home</a>
                <a href="../../reviews_index.html" class="hover:text-white">Reviews</a>
                <a href="../../research_reviews_directory.html" class="hover:text-white">Categories</a>
            </nav>
            <div class="mt-8 max-w-4xl">
                <p class="inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-sm font-medium text-teal-50">
                    <i class="fas fa-file-lines mr-2"></i>Source-Based Review Summary
                </p>
                <h1 class="mt-5 text-4xl font-bold leading-tight md:text-5xl">{html.escape(doc.display_title)}</h1>
                <p class="mt-4 text-lg text-slate-100">{html.escape(subtitle)}</p>
                <div class="mt-6 flex flex-wrap gap-3 text-sm text-teal-100">
                    <span class="rounded-full bg-white/10 px-3 py-1"><i class="fas fa-book-open mr-2"></i>{html.escape(doc.filename)}</span>
                    <span class="rounded-full bg-white/10 px-3 py-1"><i class="fas fa-list mr-2"></i>{len(doc.sections)} major sections</span>
                    <span class="rounded-full bg-white/10 px-3 py-1"><i class="fas fa-clock mr-2"></i>Source review approx. {reading_time} min</span>
                </div>
            </div>
        </div>
    </header>

    <section class="border-b border-slate-200 bg-white">
        <div class="mx-auto max-w-6xl px-4 py-5">
            <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <h2 class="text-lg font-semibold text-slate-900">Deep Research Source Review</h2>
                <p class="mt-2 text-sm text-slate-700">
                    This page is a concise summary of the full source review. Read online for the long-form version, submit corrections, or download the original document.
                </p>
                <p class="mt-2 text-xs text-slate-600">
                    Source file: {html.escape(doc.filename)} | Match confidence: {html.escape(confidence)}
                </p>
                <div class="mt-4 flex flex-wrap gap-3">
                    <a href="{viewer_href}" class="inline-flex items-center rounded-md bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700">
                        <i class="fas fa-book-open mr-2"></i>Read Full Review Online
                    </a>
                    <a href="{suggest_href}" class="inline-flex items-center rounded-md border border-emerald-700 px-3 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50">
                        <i class="fas fa-pen-to-square mr-2"></i>Suggest Correction
                    </a>
                    <a href="{download_href}" download class="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700">
                        <i class="fas fa-download mr-2"></i>Download Full Review (.docx)
                    </a>
                </div>
            </div>
        </div>
    </section>

    <main class="mx-auto max-w-6xl px-4 py-10">
        <section class="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
            <article class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-teal-700">
                    <i class="fas fa-circle-info"></i>
                    <span>Overview</span>
                </div>
                <div class="mt-4 space-y-4">
{abstract_markup}
                </div>
            </article>
            <aside class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 class="text-lg font-semibold text-slate-900">What This Summary Covers</h2>
                <div class="mt-4 grid gap-3 section-grid">
{section_links}
                </div>
            </aside>
        </section>

        <section class="mt-10 rounded-2xl border border-amber-200 bg-amber-50 p-5">
            <p class="text-sm text-amber-900">
                This page now summarizes the matched Word review rather than relying on the generic placeholder template. The detailed evidence base, full argumentation, and reference trail remain in the source document.
            </p>
        </section>

        <div class="mt-10 space-y-6">
{section_markup}
        </div>
    </main>

    <footer class="border-t border-slate-200 bg-white">
        <div class="mx-auto max-w-6xl px-4 py-8 text-sm text-slate-600">
            <p>&copy; 2026 Nuclear Biology Reviews. Source-linked educational summaries for research use.</p>
        </div>
    </footer>
</body>
</html>
"""


def rewrite_source_links(page_text: str, page_name: str, doc_name: str, confidence: str) -> str:
    viewer_href, suggest_href, download_href = build_links(page_name, doc_name, confidence)
    text = re.sub(
        r"\.\./\.\./review_source_viewer\.html\?[^\"'#]+#suggestion-form",
        suggest_href,
        page_text,
    )
    text = re.sub(
        r"\.\./\.\./review_source_viewer\.html\?[^\"'#]+",
        viewer_href,
        text,
    )
    text = re.sub(r"\.\./\.\./Reviews_useredit/[^\"']+\.docx", download_href, text)
    text = re.sub(r"(Source file:\s*)([^|<]+)", rf"\1{doc_name} ", text)
    text = re.sub(r"(Match confidence:\s*)([a-z]+)", rf"\1{confidence}", text)
    text = re.sub(r"(\.docx)\|\s*(Match confidence:)", r"\1 | \2", text)
    return text


def write_report(results: list[PageResult]) -> None:
    regenerated = [result for result in results if result.action == "regenerated"]
    relinked = [result for result in results if result.action == "updated-source-link"]
    flagged = [result for result in results if result.action == "flagged"]
    lines = [
        "# Review Content Audit",
        "",
        "Generated by `scripts/regenerate_review_summaries.py`.",
        "",
        "## Summary",
        "",
        f"- Review pages scanned: **{len(results)}**",
        f"- Placeholder or limited pages regenerated: **{len(regenerated)}**",
        f"- Existing pages with corrected source links: **{len(relinked)}**",
        f"- Pages still flagged for manual review: **{len(flagged)}**",
        "",
        "## Page Actions",
        "",
        "| Page | Placeholder | Previous Doc | Selected Doc | Confidence | Action | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in sorted(results, key=lambda item: item.page):
        lines.append(
            "| {page} | {placeholder} | {previous_doc} | {selected_doc} | {confidence} | {action} | {note} |".format(
                page=result.page,
                placeholder="yes" if result.placeholder else "no",
                previous_doc=result.previous_doc or "(none)",
                selected_doc=result.selected_doc or "(none)",
                confidence=result.confidence,
                action=result.action,
                note=result.note.replace("|", r"\|"),
            )
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    docs = candidate_docs()
    results: list[PageResult] = []

    for page_path in sorted(REVIEW_DIR.glob("*.html")):
        page_text = page_path.read_text(encoding="utf-8", errors="ignore")
        placeholder = is_placeholder_page(page_text)
        previous_doc = current_doc_name(page_text)
        selected_doc, confidence, score = match_doc(page_path.name, docs)
        new_text = page_text
        action = "none"
        note = f"match score {score:.2f}"

        if placeholder:
            new_text = render_summary_page(page_path.name, selected_doc, confidence)
            action = "regenerated"
            note = "replaced placeholder or limited content with source-based summary"
        elif previous_doc and previous_doc != selected_doc.filename and confidence != "low":
            new_text = rewrite_source_links(page_text, page_path.name, selected_doc.filename, confidence)
            action = "updated-source-link"
            note = "kept existing content and corrected source review link"
        elif confidence == "low":
            action = "flagged"
            note = "best document match is low confidence"

        if not args.dry_run and new_text != page_text:
            page_path.write_text(new_text.rstrip() + "\n", encoding="utf-8")

        results.append(
            PageResult(
                page=page_path.name,
                placeholder=placeholder,
                previous_doc=previous_doc,
                selected_doc=selected_doc.filename,
                confidence=confidence,
                action=action,
                note=note,
            )
        )

    write_report(results)
    print(f"Scanned {len(results)} review pages")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
