# Project 17 — Nanobody (VHH) vs a Tumor-Associated Antigen (HER2 / EGFR / Mesothelin)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo nanobody / antibody design · **Compute tier:** A100 recommended (free-tier = a tiny RFantibody demo only)

## The problem (and why it matters now)
Nanobodies — the ~15 kDa single variable domains (VHH) of camelid heavy-chain-only antibodies — are
small, stable, cheap, and penetrate tissue deeply, which is exactly why they power **tumor-imaging
agents** and **CAR / bispecific binder modules**. De novo VHH design to a *defined, validated*
tumor-associated antigen (TAA) epitope — newly feasible with RFantibody and BoltzGen — is a real
translational pipeline. It is also **hard**: de novo antibody hit rates are low, so the realistic
output is a *diverse, filtered pool* fed into an experimental **display screen**, not a finished binder.

## What you will do
By the end you will have run an end-to-end de novo **VHH design campaign** against a TAA epitope of your
choice (overlapping vs non-overlapping with an approved mAb), triaged it with the shared multi-layer
filter using **antibody-aware** cutoffs and developability/humanness checks, assessed **specificity
within the receptor family**, and produced a costed **display-screen plan** plus a downstream construct
(VHH-Fc for imaging, or a CAR binder) — all reproducibly, with a deterministic mock path that runs
anywhere and a clearly-marked real (A100) path.

## Learning objectives
1. Choose and justify a TAA epitope (overlapping vs non-overlapping with an approved mAb) with measurable success criteria.
2. Design VHH CDRs de novo with RFantibody (or BoltzGen nanobody mode) on a fixed humanized framework.
3. Filter with antibody-aware metrics (scRMSD, pLDDT, pae_interaction, CDR geometry) + developability/humanness, and assess receptor-family specificity.
4. Plan a pooled display screen + a downstream format (imaging or CAR) with mandatory controls.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following the timeline (everything runs on the `mock` backend with no GPU).

## Tools
RFantibody (RFdiffusion-Ab + ProteinMPNN), BoltzGen nanobody mode, AF2-Multimer (ColabFold) /
IgFold / ImmuneBuilder (NanoBodyBuilder2), developability filters (TAP / CamSol / humanness — used as
teaching heuristics here, swap in the real tools for any claim), and the shared
`shared/filtering_pipeline.py` (`design_type="antibody"`).

## Data
TAA structures — HER2 (candidate `1N8Z`, trastuzumab–HER2), EGFR (candidate `1IVO`), or a mesothelin
**model** — plus the HER-family receptor panel for specificity — exact accessions and licenses are in
`data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement (TAA + epitope choice + success criteria) + reproduced mock VHH hello-world |
| D1 | P1 (3–6)   | Working minimal VHH pipeline + first (mock/tiny-real) design batch + repo |
| D2 | P2 (7–12)  | Full VHH design pool (`campaign.csv`) + design log + interim report |
| D3 | P3 (13–18) | Antibody-filtered ranked candidates + epitope/specificity/developability figures + filtering report |
| D4 | P4 (19–22) | Display-screen plan + downstream format + specificity panel + costed experimental plan |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a VHH campaign + a developability-filtered top set + a display-screen plan + a downstream format (VHH-Fc imaging or a CAR binder) + a receptor-family specificity panel + controls |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo antibody/nanobody hit rates are **LOW**. Generate many (500+ where feasible), filter
aggressively, and frame survivors as **display-screen inputs**, not finished binders — display
screening of the pool is what actually produces real binders. pLDDT is not affinity; a low
`pae_interaction` is not binding; expression is not function. Any synthetic teaching numbers in the
notebooks are labelled `SYNTHETIC` / `EXAMPLE_DATA` and must never be reported as real. **You are graded
on rigor, reasoning, and reproducibility — not on whether the protein works.** A meticulous campaign
with a low hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is a **therapeutic/diagnostic oncology** project: a designed nanobody against a human tumor antigen
for imaging or as a CAR binder. It is framed for that legitimate purpose. Out of scope: enhancing
pathogen transmissibility/virulence, toxins, or any design intended to cause harm. Real gene-synthesis
orders must go through a biosecurity-screening provider; wet-lab work (including CAR-T) requires
institutional biosafety/ethics approval. If your chosen target raises dual-use concern, discuss a
defensible diagnostic/therapeutic framing with your advisor before proceeding. See `MASTER_BLUEPRINT.md §7`.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project is the **antibody-family template** —
Projects 14–16 reuse its structure (RFantibody/BoltzGen → AF2-Multimer/IgFold → developability →
`design_type="antibody"` filter → display screen).
