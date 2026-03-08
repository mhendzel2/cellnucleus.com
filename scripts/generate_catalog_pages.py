#!/usr/bin/env python3
"""Generate consistent category and directory pages for the review catalog."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "nuclear_biology_reviews" / "reviews"
MAPPING_PATH = ROOT / "docs" / "file-mapping.json"


@dataclass(frozen=True)
class Category:
    key: str
    filename: str
    title: str
    subtitle: str
    intro: str
    icon: str
    accent: str
    surface: str
    border: str
    text: str
    keywords: tuple[str, ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        key="chromatin",
        filename="chromatin_architecture_dynamics_category.html",
        title="Chromatin Architecture & Dynamics",
        subtitle="Genome folding, chromatin states, and higher-order nuclear organization",
        intro=(
            "Reviews in this section focus on how chromatin is folded, remodeled, and "
            "interpreted across scales, from nucleosomes to whole-genome architecture."
        ),
        icon="fa-dna",
        accent="from-cyan-600 via-sky-600 to-blue-700",
        surface="bg-cyan-50",
        border="border-cyan-200",
        text="text-cyan-700",
        keywords=(
            "chromatin",
            "chromosome",
            "genome",
            "nucleome",
            "euchromatin",
            "heterochromatin",
            "comparative-nuclear-organization",
            "computational-cell-nucleus-modeling",
        ),
    ),
    Category(
        key="epigenetics",
        filename="epigenetics_gene_regulation_category.html",
        title="Epigenetics & Gene Regulation",
        subtitle="Histone regulation, transcription control, and epigenetic inheritance",
        intro=(
            "This group collects reviews on histone modification systems, epigenetic "
            "memory, transcriptional regulation, and gene expression control in the nucleus."
        ),
        icon="fa-pen-nib",
        accent="from-emerald-600 via-green-600 to-lime-600",
        surface="bg-emerald-50",
        border="border-emerald-200",
        text="text-emerald-700",
        keywords=(
            "histone",
            "epigenetic",
            "gene-expression",
            "transcriptional-condensates",
            "pol-ii-condensate",
            "hdac",
            "h1-pcg",
            "nuclear-metabolism",
        ),
    ),
    Category(
        key="bodies",
        filename="nuclear_bodies_compartments_category.html",
        title="Nuclear Bodies & Compartments",
        subtitle="Membraneless organelles, condensates, and nuclear compartmentalization",
        intro=(
            "These reviews cover classical nuclear bodies, phase-separated compartments, "
            "and the structural logic of membraneless organization inside the nucleus."
        ),
        icon="fa-circle-nodes",
        accent="from-fuchsia-600 via-purple-600 to-indigo-700",
        surface="bg-fuchsia-50",
        border="border-fuchsia-200",
        text="text-fuchsia-700",
        keywords=(
            "cajal",
            "speckles",
            "paraspeckles",
            "nucleolus",
            "pml",
            "nuclear-bodies",
            "nuclear-body",
            "condensates",
            "phase-separation",
            "compartmentalization",
            "paraspeckles-standardized",
            "nucleolus_standardized",
            "nuclear_bodies_standardized",
        ),
    ),
    Category(
        key="dna",
        filename="dna_repair_replication_category.html",
        title="DNA Repair & Replication",
        subtitle="Replication timing, DNA damage response, and genome maintenance",
        intro=(
            "This category brings together repair, replication, checkpoint, and genome "
            "stability reviews spanning basal pathways through disease-relevant stress states."
        ),
        icon="fa-shield-halved",
        accent="from-rose-600 via-red-600 to-orange-600",
        surface="bg-rose-50",
        border="border-rose-200",
        text="text-rose-700",
        keywords=(
            "dna",
            "repair",
            "replication",
            "dsb",
            "parylation",
            "fork",
            "fpc",
            "base-excision",
            "current_dna_repair",
        ),
    ),
    Category(
        key="envelope",
        filename="nuclear_envelope_lamins_category.html",
        title="Nuclear Envelope & Lamins",
        subtitle="Boundary systems, pore architecture, and lamina-linked organization",
        intro=(
            "Envelope-centered reviews explore the mechanics and signaling roles of the "
            "nuclear boundary, lamins, and pore assemblies that shape nuclear identity."
        ),
        icon="fa-layer-group",
        accent="from-amber-500 via-orange-500 to-red-600",
        surface="bg-amber-50",
        border="border-amber-200",
        text="text-amber-700",
        keywords=(
            "envelope",
            "lamina",
            "lamin",
            "pore-complex",
            "pore_complex",
        ),
    ),
    Category(
        key="transport",
        filename="nuclear_transport_dynamics_category.html",
        title="Nuclear Transport & Dynamics",
        subtitle="Intranuclear trafficking, RNA transport, and dynamic compartment exchange",
        intro=(
            "Reviews here focus on molecular traffic through and within the nucleus, "
            "including RNA transport, live-cell dynamics, and transport-linked organization."
        ),
        icon="fa-arrow-right-arrow-left",
        accent="from-indigo-600 via-blue-600 to-cyan-600",
        surface="bg-indigo-50",
        border="border-indigo-200",
        text="text-indigo-700",
        keywords=(
            "transport",
            "intranuclear",
            "mrna",
            "rna",
            "rnp",
            "live-cell",
            "imaging",
            "compartment-dynamics",
        ),
    ),
    Category(
        key="biophysics",
        filename="nuclear_biophysics_mechanics_category.html",
        title="Nuclear Biophysics & Mechanics",
        subtitle="Material properties, force transmission, and physical nuclear behavior",
        intro=(
            "These reviews emphasize physical models, rheology, mechanics, crowding, "
            "and other quantitative frameworks for nuclear structure and function."
        ),
        icon="fa-atom",
        accent="from-violet-600 via-purple-600 to-pink-600",
        surface="bg-violet-50",
        border="border-violet-200",
        text="text-violet-700",
        keywords=(
            "biophysics",
            "biophysical",
            "microrheology",
            "viscosity",
            "crowding",
            "mechanics",
            "polymer",
            "actin",
            "esi-nuclear-analysis",
            "metabolism",
            "body_biophysics",
        ),
    ),
    Category(
        key="disease",
        filename="disease_pathology_category.html",
        title="Disease & Pathology",
        subtitle="Nuclear dysfunction, disease mechanisms, and translational perspectives",
        intro=(
            "This section groups disease-facing reviews on aging, cancer, pathology, "
            "stress biology, host-pathogen interaction, and clinically relevant nuclear defects."
        ),
        icon="fa-stethoscope",
        accent="from-slate-700 via-gray-800 to-zinc-900",
        surface="bg-slate-50",
        border="border-slate-200",
        text="text-slate-700",
        keywords=(
            "disease",
            "diseases",
            "pathology",
            "pathologies",
            "cancer",
            "neurodegeneration",
            "laminopathies",
            "aging",
            "mutants",
            "virus-host",
            "stress-response",
            "controversies",
            "chromatinopathies",
        ),
    ),
)

CATEGORY_BY_KEY = {category.key: category for category in CATEGORIES}

MANUAL_OVERRIDES = {
    "4d-genome-organization-comprehensive-review.html": "chromatin",
    "4d-nucleome-critical-review.html": "chromatin",
    "comparative-nuclear-organization-complete.html": "chromatin",
    "comparative-nuclear-organization-comprehensive-review.html": "chromatin",
    "comparative-nuclear-organization-species-updated.html": "chromatin",
    "computational-cell-nucleus-modeling-enhanced-review.html": "chromatin",
    "current_dna_repair_review.html": "dna",
    "dna_repair_crosstalk_standardized_review.html": "dna",
    "enhanced_nuclear_biophysics_comprehensive_review.html": "biophysics",
    "hdac_superfamily_standardized_review.html": "epigenetics",
    "intranuclear_transport_comprehensive_review.html": "transport",
    "lamin-a-mutants-aging-research-review.html": "disease",
    "laminopathies-nuclear-envelope-diseases-review.html": "disease",
    "nuclear_actin_comprehensive_review.html": "biophysics",
    "nuclear_body_biophysics_comprehensive_review.html": "bodies",
    "nuclear_biophysics_comprehensive_review.html": "biophysics",
    "nuclear-condensates-disease-pathologies-review.html": "disease",
    "nuclear-mechanics-disease-review.html": "disease",
    "nuclear_metabolism_standardized_review.html": "epigenetics",
    "nuclear_pore_complex_standardized_review.html": "envelope",
    "nuclear-stress-response-review.html": "disease",
    "nuclear-virus-host-interactions-review.html": "disease",
    "nucleolus_standardized_review.html": "bodies",
    "phase-separation-nucleus-review.html": "bodies",
    "pol-ii-condensate-review.html": "epigenetics",
    "replication-fork-cancer-review.html": "disease",
    "histone-ptms-neurodegeneration-review.html": "disease",
    "chromatinopathies-mechanisms-therapies-review.html": "disease",
}

NAV_LINKS = (
    ("Home", "index.html"),
    ("All Reviews", "reviews_index.html"),
    ("Research Directory", "research_reviews_directory.html"),
    ("Downloads", "downloads.html"),
)


def slug_from_name(name: str) -> str:
    return name[:-5] if name.endswith(".html") else name


def tokens_for_name(name: str) -> list[str]:
    return re.split(r"[-_]+", slug_from_name(name).lower())


def title_from_filename(name: str) -> str:
    slug = slug_from_name(name).replace("_", "-")
    replacements = {
        "4d": "4D",
        "dna": "DNA",
        "dsb": "DSB",
        "hdac": "HDAC",
        "h1": "H1",
        "h3k27me3": "H3K27me3",
        "mrna": "mRNA",
        "rna": "RNA",
        "rnp": "RNP",
        "pml": "PML",
        "pcg": "PcG",
        "ptms": "PTMs",
        "pol": "Pol",
        "ii": "II",
        "fpc": "FPC",
        "esi": "ESI",
    }
    words = []
    for token in slug.split("-"):
        words.append(replacements.get(token, token.capitalize()))
    title = " ".join(words)
    title = re.sub(r"\bAnd\b", "and", title)
    title = title.replace("Review Updated", "Review (Updated)")
    title = title.replace("Comprehensive Review Timeline", "Comprehensive Review Timeline")
    title = title.replace("Standardized Review", "Standardized Review")
    return title


def summary_from_title(title: str) -> str:
    cleaned = re.sub(
        r"\b(Comprehensive|Critical|Detailed|Enhanced|Standardized|Updated|Complete|Corrected)\b",
        "",
        title,
    )
    cleaned = re.sub(r"\bReview\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    if not cleaned:
        cleaned = title
    return f"Open the full review page for {cleaned.lower()}."


def badges_for_name(name: str) -> list[str]:
    slug = slug_from_name(name).lower()
    badges: list[str] = []
    if "standardized" in slug:
        badges.append("Standardized")
    if "enhanced" in slug:
        badges.append("Enhanced")
    if "timeline" in slug:
        badges.append("Timeline")
    if "updated" in slug:
        badges.append("Updated")
    if "complete" in slug:
        badges.append("Complete")
    if "corrected" in slug:
        badges.append("Corrected")
    if "comprehensive" in slug and not badges:
        badges.append("Comprehensive")
    return badges[:2]


def is_primary_review(name: str, mapping_values: set[str]) -> bool:
    return name in mapping_values


def category_for_file(name: str) -> str:
    if name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[name]

    slug = slug_from_name(name).replace("_", "-").lower()
    for category in CATEGORIES:
        if any(keyword in slug for keyword in category.keywords):
            return category.key
    return "chromatin"


def review_records() -> list[dict[str, object]]:
    mapping_values = set(json.loads(MAPPING_PATH.read_text(encoding="utf-8")).values())
    reviews: list[dict[str, object]] = []
    for path in sorted(REVIEW_DIR.glob("*.html")):
        name = path.name
        title = title_from_filename(name)
        reviews.append(
            {
                "name": name,
                "title": title,
                "summary": summary_from_title(title),
                "href": f"nuclear_biology_reviews/reviews/{name}",
                "category": category_for_file(name),
                "badges": badges_for_name(name),
                "primary": is_primary_review(name, mapping_values),
            }
        )
    return reviews


def page_shell(
    *,
    title: str,
    subtitle: str,
    body: str,
    accent: str,
    icon: str,
    stat_line: str,
) -> str:
    nav_html = "".join(
        f'<a href="{href}" class="text-sm font-medium text-slate-700 transition hover:text-slate-950">{label}</a>'
        for label, href in NAV_LINKS
    )
    return rf"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} | CellNucleus.com</title>
    <meta name="description" content="{html.escape(subtitle)}">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        :root {{
            --page-ink: #0f172a;
            --page-muted: #475569;
            --page-border: #cbd5e1;
        }}
        body {{
            background:
                radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 26%),
                radial-gradient(circle at top right, rgba(244, 114, 182, 0.12), transparent 22%),
                linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
            color: var(--page-ink);
        }}
        /* Local file browsing often hits pages without Tailwind v3 utilities.
           Provide the few missing classes used by these generated catalog pages. */
        .glass {{
            background: rgba(255, 255, 255, 0.94);
            border-color: rgba(255, 255, 255, 0.72);
            -webkit-backdrop-filter: blur(18px);
            backdrop-filter: blur(18px);
        }}
        .catalog-card {{
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }}
        .catalog-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
            border-color: #94a3b8;
        }}
        .bg-gradient-to-br {{
            background-color: var(--gradient-from, #0f172a);
            background-image: linear-gradient(
                135deg,
                var(--gradient-from, #0f172a) 0%,
                var(--gradient-via, var(--gradient-from, #0f172a)) 52%,
                var(--gradient-to, #312e81) 100%
            );
        }}
        .bg-white\/85 {{ background-color: rgba(255, 255, 255, 0.92); }}
        .bg-white\/70 {{ background-color: rgba(255, 255, 255, 0.78); }}
        .bg-white\/15 {{ background-color: rgba(255, 255, 255, 0.18); }}
        .text-white\/85 {{ color: rgba(255, 255, 255, 0.92); }}
        .text-white\/90 {{ color: rgba(255, 255, 255, 0.95); }}
        .border-white\/60 {{ border-color: rgba(255, 255, 255, 0.6); }}
        .border-white\/30 {{ border-color: rgba(255, 255, 255, 0.3); }}
        .hover\:bg-white\/10:hover {{ background-color: rgba(255, 255, 255, 0.1); }}
        .backdrop-filter,
        .backdrop-blur {{
            -webkit-backdrop-filter: blur(16px);
            backdrop-filter: blur(16px);
        }}
        .rounded-3xl {{ border-radius: 1.5rem; }}
        .scroll-mt-24 {{ scroll-margin-top: 6rem; }}
        .tracking-\[0\.2em\] {{ letter-spacing: 0.2em; }}
        .tracking-\[0\.18em\] {{ letter-spacing: 0.18em; }}
        .text-slate-950 {{ color: #020617; }}
        .text-slate-900 {{ color: #0f172a; }}
        .text-slate-700 {{ color: #334155; }}
        .text-slate-600 {{ color: #475569; }}
        .text-slate-500 {{ color: #64748b; }}
        .bg-slate-900 {{ background-color: #0f172a; }}
        .bg-slate-200 {{ background-color: #e2e8f0; }}
        .bg-slate-50 {{ background-color: #f8fafc; }}
        .border-slate-200 {{ border-color: #e2e8f0; }}
        .border-slate-300 {{ border-color: #cbd5e1; }}
        .border-slate-400 {{ border-color: #94a3b8; }}
        .text-cyan-700 {{ color: #0e7490; }}
        .text-emerald-700 {{ color: #047857; }}
        .text-fuchsia-700 {{ color: #a21caf; }}
        .text-rose-700 {{ color: #be123c; }}
        .text-amber-700 {{ color: #b45309; }}
        .text-indigo-700 {{ color: #4338ca; }}
        .text-violet-700 {{ color: #6d28d9; }}
        .bg-cyan-50 {{ background-color: #ecfeff; }}
        .bg-emerald-50 {{ background-color: #ecfdf5; }}
        .bg-fuchsia-50 {{ background-color: #fdf4ff; }}
        .bg-rose-50 {{ background-color: #fff1f2; }}
        .bg-amber-50 {{ background-color: #fffbeb; }}
        .bg-indigo-50 {{ background-color: #eef2ff; }}
        .bg-violet-50 {{ background-color: #f5f3ff; }}
        .border-cyan-200 {{ border-color: #a5f3fc; }}
        .border-emerald-200 {{ border-color: #a7f3d0; }}
        .border-fuchsia-200 {{ border-color: #f5d0fe; }}
        .border-rose-200 {{ border-color: #fecdd3; }}
        .border-amber-200 {{ border-color: #fde68a; }}
        .border-indigo-200 {{ border-color: #c7d2fe; }}
        .border-violet-200 {{ border-color: #ddd6fe; }}
        .from-cyan-600 {{ --gradient-from: #0891b2; }}
        .via-sky-600 {{ --gradient-via: #0284c7; }}
        .to-blue-700 {{ --gradient-to: #1d4ed8; }}
        .from-emerald-600 {{ --gradient-from: #059669; }}
        .via-green-600 {{ --gradient-via: #16a34a; }}
        .to-lime-600 {{ --gradient-to: #65a30d; }}
        .from-fuchsia-600 {{ --gradient-from: #c026d3; }}
        .via-purple-600 {{ --gradient-via: #9333ea; }}
        .to-indigo-700 {{ --gradient-to: #4338ca; }}
        .from-rose-600 {{ --gradient-from: #e11d48; }}
        .via-red-600 {{ --gradient-via: #dc2626; }}
        .to-orange-600 {{ --gradient-to: #ea580c; }}
        .from-amber-500 {{ --gradient-from: #f59e0b; }}
        .via-orange-500 {{ --gradient-via: #f97316; }}
        .to-red-600 {{ --gradient-to: #dc2626; }}
        .from-indigo-600 {{ --gradient-from: #4f46e5; }}
        .via-blue-600 {{ --gradient-via: #2563eb; }}
        .to-cyan-600 {{ --gradient-to: #0891b2; }}
        .from-violet-600 {{ --gradient-from: #7c3aed; }}
        .to-pink-600 {{ --gradient-to: #db2777; }}
        .from-slate-700 {{ --gradient-from: #334155; }}
        .via-gray-800 {{ --gradient-via: #1f2937; }}
        .to-zinc-900 {{ --gradient-to: #18181b; }}
        .from-slate-900 {{ --gradient-from: #0f172a; }}
        .via-blue-900 {{ --gradient-via: #1e3a8a; }}
        .to-indigo-900 {{ --gradient-to: #312e81; }}
        .from-sky-700 {{ --gradient-from: #0369a1; }}
        .via-blue-700 {{ --gradient-via: #1d4ed8; }}
        .to-indigo-800 {{ --gradient-to: #3730a3; }}
        @media (min-width: 1024px) {{
            .lg\:grid-cols-\[minmax\(0\,1fr\)_320px\] {{
                grid-template-columns: minmax(0, 1fr) 320px;
            }}
            .lg\:grid-cols-\[minmax\(0\,1fr\)_260px\] {{
                grid-template-columns: minmax(0, 1fr) 260px;
            }}
        }}
    </style>
</head>
<body class="min-h-screen">
    <header class="border-b border-slate-200 bg-white/85 backdrop-filter backdrop-blur">
        <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <a href="index.html" class="flex items-center gap-3 text-slate-950">
                <span class="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-white">
                    <i class="fas fa-atom"></i>
                </span>
                <span class="text-lg font-semibold">CellNucleus.com</span>
            </a>
            <nav class="hidden items-center gap-6 md:flex">
                {nav_html}
            </nav>
        </div>
    </header>
    <main>
        <section class="bg-gradient-to-br {accent} text-white">
            <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
                <div class="max-w-4xl">
                    <div class="mb-5 inline-flex items-center gap-3 rounded-full bg-white/15 px-4 py-2 text-sm font-medium">
                        <i class="fas {icon}"></i>
                        <span>{html.escape(stat_line)}</span>
                    </div>
                    <h1 class="text-4xl font-bold tracking-tight sm:text-5xl">{html.escape(title)}</h1>
                    <p class="mt-4 max-w-3xl text-lg text-white/85">{html.escape(subtitle)}</p>
                </div>
            </div>
        </section>
        {body}
    </main>
    <footer class="border-t border-slate-200 bg-white/85">
        <div class="mx-auto max-w-7xl px-4 py-8 text-sm text-slate-600 sm:px-6 lg:px-8">
            <p>CellNucleus.com review catalog. Static HTML index generated from the local review inventory.</p>
        </div>
    </footer>
</body>
</html>
"""


def related_category_chips(current_key: str) -> str:
    chips = []
    for category in CATEGORIES:
        if category.key == current_key:
            continue
        chips.append(
            f'<a href="{category.filename}" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:text-slate-950">{html.escape(category.title)}</a>'
        )
    return "".join(chips)


def render_review_card(review: dict[str, object], category: Category) -> str:
    badge_html = "".join(
        f'<span class="rounded-full bg-white/70 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">{html.escape(str(badge))}</span>'
        for badge in review["badges"]
    )
    primary_badge = (
        '<span class="rounded-full bg-slate-900 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-white">Primary</span>'
        if review["primary"]
        else '<span class="rounded-full bg-slate-200 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">Variant</span>'
    )
    return f"""
        <article class="catalog-card rounded-3xl border {category.border} bg-white p-6 shadow-sm">
            <div class="flex flex-wrap gap-2">
                {primary_badge}
                {badge_html}
            </div>
            <h3 class="mt-4 text-xl font-semibold text-slate-950">{html.escape(str(review["title"]))}</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">{html.escape(str(review["summary"]))}</p>
            <div class="mt-5 flex items-center justify-between gap-4">
                <span class="text-xs font-medium uppercase tracking-[0.18em] {category.text}">{html.escape(category.title)}</span>
                <a href="{review["href"]}" class="inline-flex items-center gap-2 text-sm font-semibold text-slate-950 transition hover:text-slate-700">
                    Open review
                    <i class="fas fa-arrow-right text-xs"></i>
                </a>
            </div>
        </article>
    """


def render_category_page(category: Category, reviews: list[dict[str, object]], total_reviews: int) -> str:
    cards = "\n".join(render_review_card(review, category) for review in reviews)
    body = f"""
        <section class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
                <div class="space-y-6">
                    <section class="glass rounded-3xl border border-white/60 p-8 shadow-sm">
                        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Category overview</p>
                        <p class="mt-4 max-w-3xl text-base leading-7 text-slate-700">{html.escape(category.intro)}</p>
                    </section>
                    <section>
                        <div class="mb-6 flex items-center justify-between gap-4">
                            <h2 class="text-2xl font-bold text-slate-950">Review Pages in This Category</h2>
                            <p class="text-sm text-slate-500">{len(reviews)} linked review pages</p>
                        </div>
                        <div class="grid gap-5 md:grid-cols-2">
                            {cards}
                        </div>
                    </section>
                </div>
                <aside class="space-y-6">
                    <section class="glass rounded-3xl border border-white/60 p-6 shadow-sm">
                        <h2 class="text-lg font-semibold text-slate-950">Quick Links</h2>
                        <div class="mt-4 space-y-3 text-sm">
                            <a href="reviews_index.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Browse full review index</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                            <a href="research_reviews_directory.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Open research directory</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                            <a href="downloads.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Source downloads</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                        </div>
                    </section>
                    <section class="glass rounded-3xl border border-white/60 p-6 shadow-sm">
                        <h2 class="text-lg font-semibold text-slate-950">Inventory</h2>
                        <dl class="mt-4 space-y-3 text-sm text-slate-600">
                            <div class="flex items-center justify-between">
                                <dt>Category pages</dt>
                                <dd class="font-semibold text-slate-950">{len(CATEGORIES)}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>All linked review pages</dt>
                                <dd class="font-semibold text-slate-950">{total_reviews}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>This category</dt>
                                <dd class="font-semibold text-slate-950">{len(reviews)}</dd>
                            </div>
                        </dl>
                    </section>
                    <section class="glass rounded-3xl border border-white/60 p-6 shadow-sm">
                        <h2 class="text-lg font-semibold text-slate-950">Related Categories</h2>
                        <div class="mt-4 flex flex-wrap gap-3">
                            {related_category_chips(category.key)}
                        </div>
                    </section>
                </aside>
            </div>
        </section>
    """
    stat_line = f"{len(reviews)} linked review pages"
    return page_shell(
        title=category.title,
        subtitle=category.subtitle,
        body=body,
        accent=category.accent,
        icon=category.icon,
        stat_line=stat_line,
    )


def render_reviews_index(groups: dict[str, list[dict[str, object]]], reviews: list[dict[str, object]]) -> str:
    sections = []
    for category in CATEGORIES:
        cards = "\n".join(render_review_card(review, category) for review in groups[category.key])
        sections.append(
            f"""
            <section id="{category.key}" class="scroll-mt-24">
                <div class="mb-6 flex items-end justify-between gap-4">
                    <div>
                        <p class="text-sm font-semibold uppercase tracking-[0.2em] {category.text}">{html.escape(category.title)}</p>
                        <h2 class="mt-2 text-2xl font-bold text-slate-950">{html.escape(category.subtitle)}</h2>
                    </div>
                    <a href="{category.filename}" class="text-sm font-semibold text-slate-700 transition hover:text-slate-950">Open category page</a>
                </div>
                <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                    {cards}
                </div>
            </section>
            """
        )
    filter_links = "".join(
        f'<a href="#{category.key}" class="rounded-full border border-white/30 px-4 py-2 text-sm font-medium text-white/90 transition hover:bg-white/10">{html.escape(category.title)}</a>'
        for category in CATEGORIES
    )
    body = f"""
        <section class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <div class="glass rounded-3xl border border-white/60 p-8 shadow-sm">
                <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_260px]">
                    <div>
                        <label for="catalog-search" class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Search review titles</label>
                        <input id="catalog-search" type="search" placeholder="Search by topic, process, or keyword" class="mt-3 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-950 outline-none transition focus:border-slate-500">
                    </div>
                    <div class="rounded-3xl border border-slate-200 bg-white p-6">
                        <dl class="space-y-3 text-sm text-slate-600">
                            <div class="flex items-center justify-between">
                                <dt>Total review pages</dt>
                                <dd class="font-semibold text-slate-950">{len(reviews)}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Primary mapped reviews</dt>
                                <dd class="font-semibold text-slate-950">{sum(1 for review in reviews if review["primary"])}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Specialized variants</dt>
                                <dd class="font-semibold text-slate-950">{sum(1 for review in reviews if not review["primary"])}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Categories</dt>
                                <dd class="font-semibold text-slate-950">{len(CATEGORIES)}</dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </div>
            <div class="mt-10 space-y-14">
                {"".join(sections)}
            </div>
        </section>
        <script>
            const searchInput = document.getElementById("catalog-search");
            const cards = Array.from(document.querySelectorAll(".catalog-card"));
            searchInput.addEventListener("input", () => {{
                const term = searchInput.value.trim().toLowerCase();
                cards.forEach((card) => {{
                    const text = card.textContent.toLowerCase();
                    card.style.display = !term || text.includes(term) ? "" : "none";
                }});
            }});
        </script>
    """
    return page_shell(
        title="Complete Nuclear Biology Review Index",
        subtitle="A complete local index of every review page currently present in the repository, grouped by category.",
        body=body,
        accent="from-slate-900 via-blue-900 to-indigo-900",
        icon="fa-book-open",
        stat_line=f"{len(reviews)} review pages across {len(CATEGORIES)} categories",
    ).replace(
        "</section>\n        {body}",
        "",
    )


def render_directory_page(groups: dict[str, list[dict[str, object]]], reviews: list[dict[str, object]]) -> str:
    category_cards = []
    for category in CATEGORIES:
        category_cards.append(
            f"""
            <article class="catalog-card rounded-3xl border {category.border} {category.surface} p-6 shadow-sm">
                <div class="flex items-center gap-3">
                    <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-slate-900 shadow-sm">
                        <i class="fas {category.icon}"></i>
                    </span>
                    <div>
                        <h2 class="text-xl font-semibold text-slate-950">{html.escape(category.title)}</h2>
                        <p class="text-sm text-slate-600">{len(groups[category.key])} linked review pages</p>
                    </div>
                </div>
                <p class="mt-4 text-sm leading-6 text-slate-700">{html.escape(category.intro)}</p>
                <div class="mt-5 flex items-center justify-between gap-4">
                    <a href="{category.filename}" class="text-sm font-semibold text-slate-950 transition hover:text-slate-700">Open category page</a>
                    <a href="reviews_index.html#{category.key}" class="text-sm font-medium text-slate-600 transition hover:text-slate-950">See reviews</a>
                </div>
            </article>
            """
        )
    featured = sorted(
        reviews,
        key=lambda item: (
            not item["primary"],
            "Enhanced" not in item["badges"],
            "Updated" not in item["badges"],
            item["title"],
        ),
    )[:8]
    featured_cards = []
    for review in featured:
        category = CATEGORY_BY_KEY[str(review["category"])]
        featured_cards.append(render_review_card(review, category))
    body = f"""
        <section class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
                <div class="space-y-8">
                    <section class="glass rounded-3xl border border-white/60 p-8 shadow-sm">
                        <h2 class="text-2xl font-bold text-slate-950">Repository Review Inventory</h2>
                        <p class="mt-4 max-w-3xl text-base leading-7 text-slate-700">
                            This directory now reflects the review pages actually present in the repository instead of the older 36-review subset. It links every discovered review page and keeps the category landing pages aligned with the same catalog.
                        </p>
                    </section>
                    <section>
                        <div class="mb-6 flex items-center justify-between gap-4">
                            <h2 class="text-2xl font-bold text-slate-950">Category Directory</h2>
                            <a href="reviews_index.html" class="text-sm font-semibold text-slate-700 transition hover:text-slate-950">Open complete review index</a>
                        </div>
                        <div class="grid gap-5 md:grid-cols-2">
                            {"".join(category_cards)}
                        </div>
                    </section>
                    <section>
                        <div class="mb-6">
                            <h2 class="text-2xl font-bold text-slate-950">Featured Review Pages</h2>
                            <p class="mt-2 text-sm text-slate-600">Highlighted pages from the local inventory, prioritizing primary, enhanced, and updated entries.</p>
                        </div>
                        <div class="grid gap-5 md:grid-cols-2">
                            {"".join(featured_cards)}
                        </div>
                    </section>
                </div>
                <aside class="space-y-6">
                    <section class="glass rounded-3xl border border-white/60 p-6 shadow-sm">
                        <h2 class="text-lg font-semibold text-slate-950">Summary</h2>
                        <dl class="mt-4 space-y-3 text-sm text-slate-600">
                            <div class="flex items-center justify-between">
                                <dt>Review pages linked</dt>
                                <dd class="font-semibold text-slate-950">{len(reviews)}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Primary mapped pages</dt>
                                <dd class="font-semibold text-slate-950">{sum(1 for review in reviews if review["primary"])}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Additional variants</dt>
                                <dd class="font-semibold text-slate-950">{sum(1 for review in reviews if not review["primary"])}</dd>
                            </div>
                            <div class="flex items-center justify-between">
                                <dt>Category pages</dt>
                                <dd class="font-semibold text-slate-950">{len(CATEGORIES)}</dd>
                            </div>
                        </dl>
                    </section>
                    <section class="glass rounded-3xl border border-white/60 p-6 shadow-sm">
                        <h2 class="text-lg font-semibold text-slate-950">Next Steps</h2>
                        <div class="mt-4 space-y-3 text-sm">
                            <a href="downloads.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Open downloads</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                            <a href="working_navigation_hub.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Legacy navigation hub</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                            <a href="structures_enhanced.html" class="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:text-slate-950">
                                <span>Structures resource</span>
                                <i class="fas fa-arrow-right text-xs"></i>
                            </a>
                        </div>
                    </section>
                </aside>
            </div>
        </section>
    """
    return page_shell(
        title="Research Reviews Directory",
        subtitle="A consistent directory view of the local nuclear biology review catalog.",
        body=body,
        accent="from-sky-700 via-blue-700 to-indigo-800",
        icon="fa-compass",
        stat_line=f"{len(reviews)} linked review pages in the local repository",
    )


def render_page(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    reviews = review_records()
    groups = {category.key: [] for category in CATEGORIES}
    for review in reviews:
        groups[str(review["category"])].append(review)
    for category in CATEGORIES:
        groups[category.key].sort(key=lambda item: str(item["title"]).lower())
        render_page(
            ROOT / category.filename,
            render_category_page(category, groups[category.key], len(reviews)),
        )
    render_page(ROOT / "reviews_index.html", render_reviews_index(groups, reviews))
    render_page(ROOT / "research_reviews_directory.html", render_directory_page(groups, reviews))


if __name__ == "__main__":
    main()
