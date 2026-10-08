# CellNucleus local replacement candidate

CellNucleus.com is a nuclear biology education project owned and operated by Gnometrix Labs. The public contact address is [cellnucleus@gnometrix.com](mailto:cellnucleus@gnometrix.com). This tree is a local candidate for later review and replacement; preparing it does not publish the site or change domain, accounts, or mail settings.

The main research index contains **62 pages: 59 core reviews and 3 additional editions**. The hypothesis index contains **17 reviews**. Six further undergraduate and public reading-level variants make **85 HTML files in the two review directories**; they are additional formats, not six new research topics. The indexed total is 79 pages.

The site contains educational summaries of published literature, with AI assistance in preparation. These summaries are not themselves journal peer-reviewed articles. Scientific audit coverage is recorded per page in the accompanying audit matrix; unchanged or partially reviewed pages must not be treated as fully validated.

## Local preview

From this directory:

```powershell
python scripts/preview_candidate.py --root . --port 8000
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and [the About page](http://127.0.0.1:8000/about.html). `npm start` is an equivalent shortcut when Node.js is available. The preview server binds to the local computer and serves public site assets, while blocking private directories, source scripts/configuration, PHP, and archived Genspark exports. The site uses plain HTML, CSS, and JavaScript; no bundler or Node dependency install is required for preview. External stylesheet and literature links require network access.

The preview server does **not** execute or expose PHP. Do not submit the correction form through it. The static candidate retains the source-viewer form and its PHP endpoint for comparison, but the administrative PHP application is deliberately excluded from this candidate.

## Structure and maintenance

- `index.html`, `about.html`: project overview, ownership, editorial approach, and contact.
- `reviews_index.html`, `research_reviews_directory.html`: research catalog entry points.
- `nuclear_biology_reviews/reviews/`: 68 research and reading-level pages.
- `hypothesis_reviews_index.html`, `hypothesis_reviews/`: 17 hypothesis reviews.
- `assets/css/`, `assets/js/`: shared styling, navigation, and client-side behavior.
- `scripts/`: catalog generation and local audit utilities.
- `taskforce_submit.php`, `review_source_viewer.html`: correction queue interface, requiring PHP hosting for submissions.

The historical Jekyll configuration is optional metadata. This candidate is validated as a static site, not as an authenticated administration service.

Prefer updating shared generators and templates when changing generated navigation or footers. `scripts/apply_branding_contacts.py` updates ownership and contact shell text without editing scientific prose. Regeneration and audits are local operations; deployment scripts in the source repository are outside the authorized scope of this work.

## Validation and review limits

Run the repository link scan after edits:

```powershell
python scripts/site_link_audit.py
```

For the candidate's strict local structural checks and JavaScript syntax checks:

```powershell
npm run build
npm test
```

These commands run `scripts/validate_candidate.py` and write JSON reports under `reports/`; they require Python and Node.js but no Node package installation. `build` validates the static tree and does not bundle, publish, or deploy it.

The accompanying validation report records the checks actually performed on this candidate, including local links and fragments, navigation, representative responsive browser behavior, and accessibility findings. A structural pass does not establish scientific correctness. Scientific evidence checks and citation corrections are documented separately, per review.

No blanket WCAG conformance, Lighthouse score, loading-time guarantee, or journal peer-review status is asserted. Such claims require their own measurements and review. Some historical templates and variants may still need further scientific or editorial work; consult the audit matrix before treating any page as complete.

## Contact and correction routing

All public site contact links use `mailto:cellnucleus@gnometrix.com`. A `mailto:` link opens the visitor's configured email application; changing it does not create a mailbox or validate delivery.

`taskforce_submit.php` accepts a form POST, sanitizes the payload, and writes a JSON file in `taskforce_submissions/`. It has no SMTP or `mail()` delivery code. `admin/taskforce.php` in the original repository is an authenticated intake UI that posts to the same endpoint; it was inspected read-only and is not copied here. The queue is separate from email.

Before a future replacement can support live submissions, separately validate PHP execution, storage permissions, the administrative service, and how queue entries are processed. Mailbox provisioning, email forwarding or notifications, DNS, and delivery testing require separate setup. No such changes were made during local preparation.

Founder-background wording is adapted from the Gnometrix source tree. It identifies Michael Hendzel as a cell biologist and University of Alberta principal investigator; it does not add degrees, citation metrics, corporate-founder credentials, or university endorsement.

## Scientific appraisal checkpoint — 3 October 2026

83 of 85 HTML review scopes have primary-source-backed text/reference appraisals completed at the access depth in the audit; 2 remain partial after a platform restriction. 0 whole packages are fully validated. Unsupported inherited scope was withdrawn with ledgers. The 100 original DOCX are byte-identical and scientifically unrevalidated: regenerating from them can overwrite the HTML editorial overrides. Consult `reports/replacement-candidate-2026-10-03/review-audit-matrix.csv` and the final comparison report. Technical passes do not upgrade scientific status.

## Archived Word status correction

Archived Word draft — not reconciled with the revised HTML; scientific validation incomplete. All public Word actions use archive labels and visible status; the viewer warning exists without URL parameters. Source mapping confidence remains distinct. No original DOCX or scientific assertions were changed; the two restricted review files remain unopened and byte-identical.
