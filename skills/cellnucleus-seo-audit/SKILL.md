---
name: cellnucleus-seo-audit
description: Use this skill when auditing or improving SEO for cellnucleus.com pages, including metadata coverage, canonical links, robots and sitemap correctness, review-directory discoverability, and page-level revisions needed to make the static site more search-friendly without breaking navigation or content accuracy.
---

# CellNucleus SEO Audit

## Overview

This skill is for a real SEO pass on the static site. Use it when the user asks for an SEO audit, metadata cleanup, sitemap or robots fixes, or page-level revisions aimed at search visibility.

## Workflow

1. Audit the current site state from files, not assumptions.
   Check:
   - `robots.txt`
   - root-level sitemap presence
   - title and meta description coverage on major HTML pages
   - canonical consistency across review and directory pages

2. Fix obvious sitewide errors first.
   In this repo, examples include:
   - stale `robots.txt` references to old GitHub-hosted sitemap paths
   - missing root `sitemap.xml`
   - inconsistent metadata across generated and hand-edited pages

3. When many pages share the same issue, repair the generator or template before editing individual outputs.

4. Keep SEO changes honest.
   Improve titles, descriptions, and structured discoverability without overstating content or adding misleading claims.

5. After SEO edits, rerun the normal site QA.
   SEO changes must not introduce broken links, missing navigation, or degraded readability.

## Repo-Specific Notes

- This repo shows partial SEO work but not a finished, trustworthy sitewide audit.
- Pair this skill with `scripts/site_link_audit.py` whenever metadata edits touch many pages.
- If repeated SEO checks become common, add or extend a deterministic audit script instead of repeating the same manual inventory.
