---
name: cellnucleus-review-refresh
description: Use this skill when nuclear review pages are thin, inaccurate, mismatched to the wrong Word document, or still read like placeholders. It covers mapping HTML review pages to the correct source `.docx`, regenerating summary pages from source documents, and fixing page-specific review templates that need richer summaries.
---

# CellNucleus Review Refresh

## Overview

This skill handles review-page content quality. Use it when a review page is too limited, reflects the wrong topic, or needs to be rebuilt from the corresponding full Word review.

## Workflow

1. Audit the current mapping before editing content.
   Use:
   - `python3 scripts/review_template_audit.py`
   - `python3 scripts/regenerate_review_summaries.py --dry-run`

2. Prefer source-driven regeneration over hand-editing long summaries.
   The main inputs are:
   - `Reviews_useredit/*.docx`
   - `docs/file-mapping.json`
   - manual overrides in `scripts/regenerate_review_summaries.py`

3. If a page maps to the wrong document, update the mapping or manual override first.
   Regenerate the page only after the source match is defensible.

4. If a page is intentionally shorter than the full review, make that explicit.
   Summary pages should read as concise overviews and should link readers toward fuller coverage where available.

5. Re-run the dry-run audit until placeholder carryover, wrong-source corrections, and low-confidence matches are gone.

## Repo-Specific Notes

- The known failure mode in this repo is generic placeholder review structure being reused across unrelated topics.
- `scripts/regenerate_review_summaries.py` is the primary mechanism for replacing those thin pages with document-derived summaries.
- Keep review copy aligned with the matched `.docx`; do not invent unsupported details to make a page look longer.
