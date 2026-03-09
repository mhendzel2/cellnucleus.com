<?php
declare(strict_types=1);

require __DIR__ . '/admin_auth.php';
require_admin_auth();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Taskforce Admin | CellNucleus.com</title>
    <meta name="description" content="Administrative intake console for review edits, video briefs, site updates, site issues, and SEO work.">
    <meta name="robots" content="noindex,nofollow,noarchive">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        body {
            background:
                radial-gradient(circle at top left, rgba(29, 78, 216, 0.12), transparent 24%),
                radial-gradient(circle at top right, rgba(5, 150, 105, 0.12), transparent 22%),
                #f8fafc;
        }
        .bg-white\/90 { background-color: rgba(255, 255, 255, 0.92); }
        .bg-slate-50 { background-color: #f8fafc; }
        .bg-slate-900 { background-color: #0f172a; }
        .text-slate-950 { color: #020617; }
        .text-slate-900 { color: #0f172a; }
        .text-slate-800 { color: #1e293b; }
        .text-slate-700 { color: #334155; }
        .text-slate-500 { color: #64748b; }
        .border-slate-300 { border-color: #cbd5e1; }
        .border-slate-200 { border-color: #e2e8f0; }
        .rounded-3xl { border-radius: 1.5rem; }
        .card {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(10px);
        }
        @media (min-width: 1024px) {
            .lg\:grid-cols-\[minmax\(0\,1fr\)_340px\] {
                grid-template-columns: minmax(0, 1fr) 340px;
            }
        }
    </style>
</head>
<body class="min-h-screen text-slate-900">
    <header class="border-b border-slate-200 bg-white/90">
        <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <a href="../index.html" class="inline-flex items-center gap-3">
                <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-white">
                    <i class="fas fa-atom"></i>
                </span>
                <span class="text-lg font-semibold">CellNucleus.com</span>
            </a>
            <nav class="flex flex-wrap items-center gap-5 text-sm font-medium text-slate-700">
                <a href="../index.html" class="hover:text-slate-950">Home</a>
                <a href="../reviews_index.html" class="hover:text-slate-950">All Reviews</a>
                <a href="../google_ultra_youtube_prompts.html" class="hover:text-slate-950">YouTube Studio</a>
                <a href="taskforce.php" class="text-blue-700">Admin Intake</a>
            </nav>
        </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <section class="card rounded-3xl border border-slate-200 p-8 shadow-sm">
            <div class="flex flex-wrap items-start justify-between gap-6">
                <div class="max-w-3xl">
                    <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Administration</p>
                    <h1 class="mt-3 text-4xl font-bold text-slate-950">Agent Taskforce</h1>
                    <p class="mt-4 text-lg text-slate-700">
                        Route review edits, site issues, SEO work, and video briefs through the internal administration console.
                        Agents verify what they can, fix confirmed issues directly, and escalate only the items they cannot confirm.
                    </p>
                </div>
                <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
                    <p class="font-semibold">Default escalation policy</p>
                    <p class="mt-1">Only pass to the site owner when the evidence is incomplete, conflicting, or strategic.</p>
                </div>
            </div>
        </section>

        <section class="mt-8 grid gap-6 md:grid-cols-3">
            <article class="card rounded-3xl border border-slate-200 p-6 shadow-sm">
                <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white">
                    <i class="fas fa-file-medical"></i>
                </div>
                <h2 class="mt-4 text-xl font-bold text-slate-950">Edit Triage</h2>
                <p class="mt-3 text-sm text-slate-700">
                    Validate claims against the matched review page and source `.docx`, then hand confirmed issues to Review Refresh or direct page repair.
                </p>
            </article>
            <article class="card rounded-3xl border border-slate-200 p-6 shadow-sm">
                <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-600 text-white">
                    <i class="fab fa-youtube"></i>
                </div>
                <h2 class="mt-4 text-xl font-bold text-slate-950">Video Marketing</h2>
                <p class="mt-3 text-sm text-slate-700">
                    Turn review topics into Gemini deep-research briefs, NotebookLM evidence packs, cinematic scripts, storyboards, and companion web pages.
                </p>
            </article>
            <article class="card rounded-3xl border border-slate-200 p-6 shadow-sm">
                <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white">
                    <i class="fas fa-sitemap"></i>
                </div>
                <h2 class="mt-4 text-xl font-bold text-slate-950">Site Ops</h2>
                <p class="mt-3 text-sm text-slate-700">
                    Handle navigation defects, page-specific rendering issues, SEO Audit work, Update Manager follow-through, and static-site publishing without routing through personal email.
                </p>
            </article>
        </section>

        <section class="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div class="card rounded-3xl border border-slate-200 p-6 shadow-sm">
                <h2 class="text-2xl font-bold text-slate-950">Submit A Task</h2>
                <p class="mt-2 text-sm text-slate-700">
                    Use this form for review edits, video briefs, site updates, site issues, and SEO work. The taskforce will review the request before escalating anything unresolved.
                </p>

                <form id="taskforceForm" action="../taskforce_submit.php" method="post" class="mt-6 space-y-5">
                    <div class="grid gap-5 md:grid-cols-2">
                        <div>
                            <label for="queue" class="block text-sm font-semibold text-slate-800">Queue</label>
                            <select id="queue" name="queue" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                                <option value="review_edit">Review edit</option>
                                <option value="video_brief">Video brief</option>
                                <option value="site_update">Site update</option>
                                <option value="site_issue">Site issue</option>
                                <option value="seo">SEO</option>
                                <option value="general">General</option>
                            </select>
                        </div>
                        <div>
                            <label for="requestTitle" class="block text-sm font-semibold text-slate-800">Task title</label>
                            <input id="requestTitle" name="request_title" type="text" placeholder="Short title for the request" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                        </div>
                    </div>

                    <div class="grid gap-5 md:grid-cols-2">
                        <div>
                            <label for="pagePath" class="block text-sm font-semibold text-slate-800">Related page</label>
                            <input id="pagePath" name="page_path" type="text" placeholder="reviews_index.html or full page path" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                        </div>
                        <div>
                            <label for="docPath" class="block text-sm font-semibold text-slate-800">Related source document</label>
                            <input id="docPath" name="doc_path" type="text" placeholder="Reviews_useredit/example.docx" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                        </div>
                    </div>

                    <div>
                        <label for="requestDetails" class="block text-sm font-semibold text-slate-800">Details</label>
                        <textarea id="requestDetails" name="request_details" rows="8" placeholder="Describe the issue or requested output. For YouTube briefs, include the topic, target audience, desired runtime, and visual style. For scientific edits, include the exact section and what appears incorrect." class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"></textarea>
                    </div>

                    <div class="grid gap-5 md:grid-cols-2">
                        <div>
                            <label for="evidenceUrl" class="block text-sm font-semibold text-slate-800">Evidence URL</label>
                            <input id="evidenceUrl" name="evidence_url" type="url" placeholder="https://doi.org/... or supporting page URL" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                        </div>
                        <div>
                            <label for="preferredContact" class="block text-sm font-semibold text-slate-800">Optional follow-up contact</label>
                            <input id="preferredContact" name="preferred_contact" type="text" placeholder="Optional email or handle for follow-up" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                        </div>
                    </div>

                    <div>
                        <label for="escalationPolicy" class="block text-sm font-semibold text-slate-800">Escalation policy</label>
                        <select id="escalationPolicy" name="escalation_policy" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                            <option value="agent_only_unless_unverified">Escalate only if agents cannot confirm the change</option>
                            <option value="agent_review_then_owner_summary">Review first, then summarize for owner</option>
                            <option value="owner_review_requested">Owner review requested even if agents can confirm</option>
                        </select>
                    </div>

                    <input id="sourcePage" name="source_page" type="hidden">

                    <div class="flex flex-wrap gap-3">
                        <button type="submit" class="inline-flex items-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">
                            <i class="fas fa-paper-plane mr-2"></i>Send To Taskforce
                        </button>
                        <a href="../google_ultra_youtube_prompts.html" class="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                            <i class="fab fa-youtube mr-2"></i>Open YouTube Studio
                        </a>
                    </div>
                </form>
            </div>

            <aside class="card rounded-3xl border border-slate-200 p-6 shadow-sm">
                <h2 class="text-xl font-bold text-slate-950">How Requests Are Handled</h2>
                <ol class="mt-4 space-y-4 text-sm text-slate-700">
                    <li><strong>1. Intake:</strong> the request enters the taskforce queue with page, document, and evidence metadata.</li>
                    <li><strong>2. Verification:</strong> agents compare the request against the page, source review, and audit outputs.</li>
                    <li><strong>3. Resolution:</strong> confirmed fixes are applied directly; uncertain issues are summarized for owner review.</li>
                </ol>

                <div class="mt-6 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
                    <p class="font-semibold">YouTube brief checklist</p>
                    <ul class="mt-2 list-disc space-y-1 pl-5">
                        <li>Topic or source review</li>
                        <li>Audience level and runtime</li>
                        <li>Desired tone or cinematic style</li>
                        <li>Need for a companion web page</li>
                    </ul>
                </div>
                <div class="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                    <p class="font-semibold">Site update</p>
                    <p class="mt-2">Use this queue when page edits should trigger follow-up updates to indexes, category pages, review refreshes, audits, or deployment checks.</p>
                </div>
            </aside>
        </section>
    </main>

    <script>
        const canonicalQueues = new Set([
            "review_edit",
            "video_brief",
            "site_update",
            "site_issue",
            "seo",
            "general",
        ]);

        function normalizeQueue(rawQueue) {
            const value = (rawQueue || "").trim().toLowerCase();
            if (!value) return "";
            if (canonicalQueues.has(value)) return value;

            if (value.endsWith("_request")) {
                const requestCandidate = value.replace(/_request$/, "");
                if (canonicalQueues.has(requestCandidate)) return requestCandidate;
            }

            if (value.startsWith("review_")) return "review_edit";
            if (value.endsWith("video_brief")) return "video_brief";
            if (value.startsWith("site_update")) return "site_update";

            return "";
        }

        function applyPrefill() {
            const params = new URLSearchParams(window.location.search);
            const queue = normalizeQueue(params.get("queue"));
            const page = params.get("page");
            const doc = params.get("doc");
            const title = params.get("title");
            const details = params.get("details");

            if (queue) document.getElementById("queue").value = queue;
            if (page) document.getElementById("pagePath").value = page;
            if (doc) document.getElementById("docPath").value = doc;
            if (title) document.getElementById("requestTitle").value = title;
            if (details) document.getElementById("requestDetails").value = details;
            document.getElementById("sourcePage").value = window.location.href;
        }

        window.addEventListener("DOMContentLoaded", applyPrefill);
    </script>
</body>
</html>
