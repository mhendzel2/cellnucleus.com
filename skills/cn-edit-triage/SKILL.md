---
name: cn-edit-triage
description: "Use this skill when CellNucleus receives edit requests, correction suggestions, or page-quality reports that should be verified by the agent taskforce first. It covers structured intake, evidence review against site pages and source documents, direct fixes for confirmed issues, and escalation to the site owner only when agents cannot confirm the right change."
---

# Edit Triage

## Overview

This skill governs how edits enter the queue and how agents decide whether to fix, reject, or escalate them.

## Workflow

1. Intake requests through the admin queue, not personal email.
   The site intake points are:
   - `admin/taskforce.php`
   - `taskforce_submit.php`
   - `review_source_viewer.html`

2. Verify against the strongest local evidence first.
   Typical sources:
   - live HTML page in the repo
   - matched `.docx` in `Reviews_useredit/`
   - audit scripts and generated reports

3. Resolve what can be confirmed.
   Agents should directly fix:
   - broken links
   - navigation regressions
   - clear template carryover
   - source-mismatch corrections
   - obvious metadata and formatting defects

4. Escalate only unresolved or conflicting cases.
   Pass to the site owner only when:
   - evidence conflicts
   - the requested change is scientifically uncertain
   - multiple source documents disagree
   - the request is strategic rather than factual

5. Keep requests traceable.
   Store the structured payload and preserve page path, source document, evidence URL, and escalation state.

## Repo-Specific Notes

- `review_source_viewer.html` should submit to the taskforce queue instead of opening a mail client.
- Pair this skill with `cn-review-refresh` when an edit implies a wrong review-to-source mapping.
- Pair this skill with `cn-site-ops` when the request is structural rather than scientific.
