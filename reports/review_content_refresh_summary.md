# Review Content Refresh Summary

Generated after rebuilding placeholder review pages from their linked Word review sources.

## What Was Wrong

- 70 review pages in `nuclear_biology_reviews/reviews/` were still thin placeholder pages built from the generic "Nuclear Bodies: Architecture and Function" template.
- Several pages also pointed at the wrong source `.docx`, which made the page title, page body, and downloadable full review disagree.

## What Changed

- Regenerated 70 placeholder or limited review pages as concise, source-based summaries.
- Each regenerated page now uses the matched review title, abstract, major section headings, and section-level summary paragraphs extracted from the related `.docx`.
- Corrected source review links for 4 non-placeholder pages that already had substantial content but referenced the wrong full review document.
- Added a reusable regeneration script at [scripts/regenerate_review_summaries.py](/mnt/c/Users/mjhen/Github/cellnucleus.com/scripts/regenerate_review_summaries.py).

## Representative Fixes

- `cajal-bodies-comprehensive-review.html` now summarizes `Cajal Bodies_ Comprehensive Academic Review_.docx`.
- `nucleolus-comprehensive-review.html` now summarizes `Nucleolus_ Cell Biology and Biochemistry.docx`.
- `paraspeckles-comprehensive-review.html` now summarizes `Paraspeckle Biology, Function, Regulation.docx`.
- `nuclear-speckles-comprehensive-review.html` now summarizes `Nuclear Speckles_ Biology and Function.docx`.
- `pml-nuclear-bodies-comprehensive-review.html` now summarizes `PML Bodies_ Biology and Function.docx`.
- `transcriptional-condensates-comprehensive-review.html` now summarizes `Transcriptional Condensates_ Models and Functions.docx`.
- `live-cell-transcription-imaging-review.html` now summarizes `Live-cell imaging of transcription.docx`.
- `nuclear-envelope-comprehensive-review.html` now summarizes `Nuclear Envelope_ Structure and Dynamics.docx`.
- `nuclear-lamina-comprehensive-review.html` now summarizes `Lamina_ Structure, Function, and Disease_.docx`.
- `nuclear-biology-controversies-review.html` now summarizes `Controversies in Cell Nucleus Biology.docx`.

## Validation

- The regeneration script now reruns cleanly in dry-run mode without reporting more placeholder pages, mismatched source links, or unresolved low-confidence matches.
- The current stable audit output is stored in [reports/review_content_audit.md](/mnt/c/Users/mjhen/Github/cellnucleus.com/reports/review_content_audit.md).
