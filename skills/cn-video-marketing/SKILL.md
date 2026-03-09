---
name: cn-video-marketing
description: "Use this skill when planning website and YouTube marketing for CellNucleus.com, especially when generating YouTube video ideas, converting review content into Gemini deep-research prompts, preparing NotebookLM input packets, drafting cinematic scripts and shot lists, creating companion web pages, and aligning video metadata with site content."
---

# Video Marketing

## Overview

This skill covers the marketing workflow that turns CellNucleus review content into YouTube-ready educational videos and companion website pages.

## Workflow

1. Start from a specific review, topic cluster, or scientific question.
   Pull the best source page and, when needed, the matched `.docx` from `Reviews_useredit/`.

2. Build a research packet before drafting.
   The default pipeline is:
   - review page summary
   - matched `.docx` source
   - Gemini deep-research brief
   - NotebookLM verification packet

3. Produce video outputs as a set, not one artifact at a time.
   Minimum bundle:
   - title and angle
   - hook and audience level
   - full script or beat sheet
   - visual storyboard and animation prompts
   - thumbnail/title/description/chapters
   - companion website page or page update

4. Keep claims sourceable.
   NotebookLM or source-review verification should happen before a script is treated as publishable.

5. Route new ideas and production requests through the taskforce intake.
   Use `agent_taskforce.html` and `taskforce_submit.php` for queueing new video briefs and cross-channel marketing requests.

## Repo-Specific Notes

- `google_ultra_youtube_prompts.html` is the main on-site YouTube workflow page.
- `review_source_viewer.html` and `Reviews_useredit/` are the fastest way to assemble evidence-backed source material.
- When a video request depends on unresolved scientific claims, hand it to edit triage first instead of scripting around uncertainty.
