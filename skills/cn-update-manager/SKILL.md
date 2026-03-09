---
name: cn-update-manager
description: "Use this skill when pages, source documents, templates, or routing files have changed and the website needs to stay synchronized. It covers detecting changed files, deciding which generators and audits must run, refreshing dependent pages, and preparing the site for deployment after edits."
---

# Update Manager

## Overview

This skill manages change propagation after edits. Use it when files have changed and the site needs follow-up work so indexes, generated pages, review summaries, audits, and deployment state stay aligned.

## Workflow

1. Start with the actual changed files.
   Use `python3 scripts/site_update_manager.py` with explicit paths or let it inspect the current git worktree.

2. Let the manager determine the required follow-up.
   Typical actions include:
   - regenerating catalog and category pages
   - refreshing review pages from `.docx` sources
   - rerunning review-template checks
   - rerunning link audits
   - linting PHP endpoints when PHP is available

3. Apply orchestrated updates before deployment.
   Use `python3 scripts/site_update_manager.py --run` to execute the recommended tasks in sequence.

4. Deploy only after the update pass is clean.
   If the changes are ready for publish, use `python3 scripts/site_update_manager.py --run --deploy`.

## Repo-Specific Notes

- Source review changes usually come from `Reviews_useredit/` or `docs/file-mapping.json`.
- Catalog/index changes are usually driven by `scripts/generate_catalog_pages.py` and the review-page inventory.
- Structural page edits should always be followed by `scripts/site_link_audit.py`.
- If `.php` files changed and PHP is missing locally, the manager should report that linting could not be performed.
