---
name: cellnucleus-site-ops
description: Use this skill when working on cellnucleus.com static-site operations: rescanning links after local edits, fixing navigation or contrast regressions, correcting page-specific template issues, regenerating catalog pages, and deploying the site to Aplus while preserving the separate graduate-studies-in-cancer-research.org directory.
---

# CellNucleus Site Ops

## Overview

This skill is for end-to-end maintenance of the static CellNucleus site. Use it for fresh rescans, navigation repair, contrast cleanup, generator reruns, deployment to Aplus, and live verification.

## Workflow

1. Start from the current tree, not prior reports.
   Run `python3 scripts/site_link_audit.py` after any user edits.
   If links are clean but navigation complaints remain, inspect the affected pages directly.

2. Prefer fixing generators and shared templates before patching generated HTML.
   The main shared generators are:
   - `scripts/generate_catalog_pages.py`
   - `scripts/regenerate_review_summaries.py`
   - `scripts/review_template_audit.py`

3. For page-specific failures, patch the page only when the issue is intentionally local.
   Typical local issues in this repo are:
   - missing or weak `Home` navigation
   - broken relative links
   - washed-out hero text caused by unsupported utility classes
   - stale placeholders or truncated “draft-like” copy

4. Treat Aplus deployment as static-file publishing.
   Use `scripts/deploy_to_aplus.py`.
   Secrets are loaded from `.secrets/.env` by `scripts/aplus_secrets.py`.
   The live CellNucleus document root is `/public`.
   Do not touch the separate `graduate-studies-in-cancer-research.org` sibling directory.

5. Verify after changes.
   Minimum checks:
   - rerun `python3 scripts/site_link_audit.py`
   - confirm the affected pages still navigate back to the home page
   - when deploying, verify live HTTP routes such as `/`, `/reviews_index.html`, and one changed review page

## Repo-Specific Notes

- This site is static HTML with client-side JavaScript only. There is no Node or server-side build dependency to preserve.
- If contrast breaks on catalog pages, inspect for Tailwind v3-style classes being used against the local Tailwind 2 stylesheet.
- Keep `.secrets/` untracked.
- HTTPS problems on Aplus are panel-side TLS issues unless the deployed HTTP content is also broken.
