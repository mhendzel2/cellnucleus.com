#!/usr/bin/env python3
"""Repair recurring stale links and placeholder snippets across the static site."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "nuclear_biology_reviews" / "reviews"
MAPPING = json.loads((ROOT / "docs" / "file-mapping.json").read_text(encoding="utf-8"))

DELETIONS_MAPPING = {
    "4d-genome-organization-comprehensive-review.html": "4d-nucleome-critical-review.html",
    "chromatin-architecture-dynamics-review.html": "chromatin_architecture_standardized_review.html",
    "chromatin-biophysics-function-review.html": "chromatin_biophysics_comprehensive_review.html",
    "nuclear-biophysical-properties-review.html": "nuclear_biophysics_comprehensive_review.html",
    "enhanced_nuclear_biophysics_comprehensive_review.html": "nuclear_biophysics_comprehensive_review.html",
    "heterochromatin-comprehensive-review-timeline.html": "heterochromatin-comprehensive-review.html",
    "comparative-nuclear-organization-complete.html": "comparative-nuclear-organization-species-updated.html",
    "comparative-nuclear-organization-comprehensive-review.html": "comparative-nuclear-organization-species-updated.html",
    "dna-repair-pathway-crosstalk-complete.html": "dna_repair_crosstalk_standardized_review.html",
    "dna-repair-pathway-crosstalk-review-updated.html": "dna_repair_crosstalk_standardized_review.html",
    "epigenetic-inheritance-complete.html": "epigenetic-inheritance-mechanisms-review-updated.html",
    "epigenetic-inheritance-comprehensive-review.html": "epigenetic-inheritance-mechanisms-review-updated.html",
    "histone-h1-family-comprehensive-review.html": "histone-h1-family-enhanced-comprehensive-review.html",
    "intranuclear-mrna-transport-review.html": "intranuclear_transport_comprehensive_review.html",
    "intranuclear-rna-transport-imaging-review.html": "intranuclear_transport_comprehensive_review.html",
    "nuclear-bodies-standardized.html": "nuclear-bodies-comprehensive-review.html",
    "nuclear_bodies_standardized_review.html": "nuclear-bodies-comprehensive-review.html",
    "nuclear-speckles-standardized.html": "nuclear-speckles-comprehensive-review.html",
    "paraspeckles-standardized.html": "paraspeckles-comprehensive-review.html",
    "nucleolus-comprehensive-review.html": "nucleolus_standardized_review.html",
    "nuclear-microrheology-detailed-review.html": "nuclear-microrheology-enhanced-graphics.html",
    "nuclear-pore-complex-comprehensive-review.html": "nuclear_pore_complex_standardized_review.html"
}

MAPPING.update(DELETIONS_MAPPING)

ROOT_HTML_FILES = [
    path
    for path in ROOT.rglob("*.html")
    if ".git" not in path.parts and "backup" not in path.parts
]

GENSPARK_BADGE_RE = re.compile(
    r"\s*<script id=\"html_badge_script1\">.*?</script>\s*<script id=\"html_notice_dialog_script\".*?</script>\s*",
    re.DOTALL,
)

GENSPARK_NOTICE_ONLY_RE = re.compile(
    r"\s*<script id=\"html_notice_dialog_script\".*?</script>\s*",
    re.DOTALL,
)


def strip_genspark(text: str) -> str:
    text = GENSPARK_BADGE_RE.sub("\n", text)
    return GENSPARK_NOTICE_ONLY_RE.sub("\n", text)


def replace_root_review_links(text: str) -> str:
    for old_name, new_name in MAPPING.items():
        text = text.replace(
            f'nuclear_biology_reviews/reviews/{old_name}',
            f'nuclear_biology_reviews/reviews/{new_name}',
        )
        text = text.replace(
            f'href="{old_name}"',
            f'href="nuclear_biology_reviews/reviews/{new_name}"',
        )
        text = text.replace(
            f'src="{old_name}"',
            f'src="nuclear_biology_reviews/reviews/{new_name}"',
        )
        text = text.replace(
            f'href="reviews/{old_name}"',
            f'href="nuclear_biology_reviews/reviews/{new_name}"',
        )
    text = text.replace('href="complete_reviews_index_final.html"', 'href="reviews_index.html"')
    text = text.replace('href="nuclear_biology_reviews_index.html"', 'href="reviews_index.html"')
    text = text.replace('href="enhanced_structures_database.html"', 'href="structures_enhanced.html"')
    text = text.replace(
        'href="nuclear_speckles_enhanced_visual_review.html"',
        'href="nuclear_biology_reviews/reviews/nuclear-speckles-comprehensive-review.html"',
    )
    text = text.replace('href="/"', 'href="index.html"')
    return text


def replace_review_local_links(text: str) -> str:
    text = re.sub(r'href="reviews/([^"]+\.html)"', r'href="\1"', text)
    for old_name, new_name in MAPPING.items():
        text = text.replace(old_name, new_name)
    text = text.replace('href="complete_reviews_index_final.html"', 'href="../../reviews_index.html"')
    text = text.replace('href="nuclear_biology_reviews_index.html"', 'href="../../reviews_index.html"')
    text = text.replace('href="enhanced_structures_database.html"', 'href="../../structures_enhanced.html"')
    return text


def repair_review_placeholders(text: str) -> str:
    replacements = {
        (
            'href="#" class="inline-flex items-center px-3 py-2 bg-green-600 text-white '
            'rounded-md hover:bg-green-700 transition-colors">\n'
            '                                <i class="fab fa-google-drive mr-2"></i>Edit in Google Docs'
        ): (
            'href="../../downloads.html" class="inline-flex items-center px-3 py-2 bg-green-600 text-white '
            'rounded-md hover:bg-green-700 transition-colors">\n'
            '                                <i class="fab fa-google-drive mr-2"></i>Edit in Google Docs'
        ),
        (
            'href="#" class="inline-flex items-center px-3 py-2 bg-blue-600 text-white '
            'rounded-md hover:bg-blue-700 transition-colors">\n'
            '                                <i class="fas fa-download mr-2"></i>Download PDF'
        ): (
            'href="../../downloads.html" class="inline-flex items-center px-3 py-2 bg-blue-600 text-white '
            'rounded-md hover:bg-blue-700 transition-colors">\n'
            '                                <i class="fas fa-download mr-2"></i>Download PDF'
        ),
        (
            'href="#" class="inline-flex items-center px-3 py-2 border border-green-600 text-green-600 '
            'rounded-md hover:bg-green-50 transition-colors">\n'
            '                                <i class="fas fa-plus mr-2"></i>Submit Research'
        ): (
            'href="../../research_reviews_directory.html" class="inline-flex items-center px-3 py-2 border border-green-600 text-green-600 '
            'rounded-md hover:bg-green-50 transition-colors">\n'
            '                                <i class="fas fa-plus mr-2"></i>Submit Research'
        ),
        (
            'href="#" class="inline-flex items-center px-3 py-2 border border-green-600 text-green-600 '
            'rounded-md hover:bg-green-50 transition-colors">\n'
            '                                <i class="fas fa-comment mr-2"></i>Discussion Forum'
        ): (
            'href="../../reviews_index.html" class="inline-flex items-center px-3 py-2 border border-green-600 text-green-600 '
            'rounded-md hover:bg-green-50 transition-colors">\n'
            '                                <i class="fas fa-comment mr-2"></i>Discussion Forum'
        ),
        'href="#" class="text-gray-600 hover:text-gray-900">Home</a>':
            'href="../../index.html" class="text-gray-600 hover:text-gray-900">Home</a>',
        'href="#" class="text-gray-600 hover:text-gray-900">Reviews</a>':
            'href="../../reviews_index.html" class="text-gray-600 hover:text-gray-900">Reviews</a>',
        'href="#" class="text-gray-600 hover:text-gray-900">Categories</a>':
            'href="../../research_reviews_directory.html" class="text-gray-600 hover:text-gray-900">Categories</a>',
        'href="#" class="text-gray-600 hover:text-gray-900">About</a>':
            'href="../../index.html" class="text-gray-600 hover:text-gray-900">About</a>',
        'href="#" class="text-gray-500 hover:text-gray-700"><i class="fas fa-home mr-1"></i>Home</a>':
            'href="../../index.html" class="text-gray-500 hover:text-gray-700"><i class="fas fa-home mr-1"></i>Home</a>',
        'href="#" class="text-gray-600 hover:text-gray-900 transition duration-300">Home</a>':
            'href="../../index.html" class="text-gray-600 hover:text-gray-900 transition duration-300">Home</a>',
        'href="#" class="text-gray-600 hover:text-gray-900 transition duration-300">Reviews</a>':
            'href="../../reviews_index.html" class="text-gray-600 hover:text-gray-900 transition duration-300">Reviews</a>',
        'href="#" class="text-gray-600 hover:text-gray-900 transition duration-300">Categories</a>':
            'href="../../research_reviews_directory.html" class="text-gray-600 hover:text-gray-900 transition duration-300">Categories</a>',
        'href="#" class="text-gray-600 hover:text-gray-900 transition duration-300">About</a>':
            'href="../../index.html" class="text-gray-600 hover:text-gray-900 transition duration-300">About</a>',
        'href="#" class="hover:text-gray-900">Home</a>':
            'href="../../index.html" class="hover:text-gray-900">Home</a>',
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text


def cleanup_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def main() -> None:
    for path in ROOT_HTML_FILES:
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        text = strip_genspark(text)
        if path.is_relative_to(REVIEW_DIR):
            text = replace_review_local_links(text)
            text = repair_review_placeholders(text)
        else:
            text = replace_root_review_links(text)
        text = cleanup_whitespace(text)
        if text != original:
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
