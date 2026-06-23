# Project 08 — De Novo Binder vs KRAS (the "Undruggable" Oncotarget)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed binder design · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
**KRAS** is mutated in roughly a quarter of all human cancers (pancreatic, colorectal, lung) and was
considered **"undruggable"** for three decades: a small, smooth, highly charged GTPase surface with no
obvious small-molecule pocket. The covalent **G12C inhibitors** (sotorasib, adagrasib) finally broke
that barrier — but they exploit one specific mutant cysteine, and **most KRAS alleles (e.g. G12D, the
most common) remain hard**, as do the other RAS isoforms. De novo **binders** to the **switch I/II
regions** or to **allele-specific surfaces** are a frontier alternative: a protein binder can read a
larger, shape-complementary epitope than a small molecule can. **This is a human oncotarget; the
framing is therapeutic/diagnostic — inhibitory binders to a cancer driver.**

## What you will do
By the end you will have run an end-to-end de novo binder campaign against a chosen KRAS surface (a
specific **allele** in a specific **nucleotide state**) with **two** paradigms (BindCraft and
RFdiffusion-binder + ProteinMPNN), triaged both pools with the shared multi-layer in-silico filter
(`design_type="binder"`), reasoned about **isoform selectivity vs HRAS/NRAS** and **allele
selectivity**, benchmarked the paradigms head-to-head, and produced a costed validation plan whose
centerpiece is an **isoform-specificity panel** with scrambled-interface and nucleotide-state controls
— all reproducibly, degrading gracefully when only a free T4 is available.

## Learning objectives
1. Select a KRAS **surface/allele** (switch I/II or a mutant-specific pocket) **and the right
   nucleotide state** (GDP "off" vs GTP/analog "on"), and justify the choice.
2. Run BindCraft (or FreeBindCraft) and RFdiffusion binder mode + ProteinMPNN against that epitope.
3. Apply the shared 4-layer filter with binder cutoffs (`pae_interaction` is the key binder metric)
   and report an honest hit rate.
4. Reason about **specificity** — model the binder vs **HRAS/NRAS** (isoform selectivity) and across
   alleles — and design a controlled validation plan (SPR/BLI + isoform panel + nucleotide-state test).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
BindCraft (or FreeBindCraft) for one-shot hallucination-based binders; RFdiffusion **binder mode** +
ProteinMPNN for diffusion-then-sequence binders; AF2-Multimer (ColabFold) for interface confidence
(`pae_interaction`) **and the isoform-specificity panel**; **structural alignment** (Biopython) for
KRAS-vs-HRAS/NRAS isoform analysis; the shared `filtering_pipeline.py` (`design_type="binder"`);
py3Dmol. Optional stretch: Boltz-2 affinity prediction on top hits (scaffold only — never a fabricated K_D).

## Data
KRAS structure(s) in the chosen allele + nucleotide state — candidate accessions **4OBE** (WT) and
**6OIM** (G12C) (**candidate — verify on RCSB**) — plus **HRAS/NRAS** structures for the
isoform-specificity panel. The binder targets a KRAS surface (switch I/II or an allele pocket) in a
defined nucleotide state. Exact accessions, sizes, licenses, and the nucleotide-state note are in
`data/README.md`. **Verify every accession on RCSB in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + epitope/allele/nucleotide-state choice + target prep + reproduced mock mini-run |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Two-paradigm design pool (BindCraft + RFdiffusion) + design log + interim report |
| D3 | P3 (13–18) | Ranked top 10–20 each + benchmark figures + **isoform-specificity analysis** + filtering report |
| D4 | P4 (19–22) | Validation report + costed SPR/BLI + **isoform-specificity panel** + controls (incl. nucleotide-state test) |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** allele/isoform-specificity analysis + a binder campaign (top 10–20 each paradigm) + a validation plan with an **SPR/BLI + isoform-specificity panel + scrambled-interface negative + nucleotide-state test** |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
KRAS is a **hard** target: a small, relatively featureless, highly charged surface, and the real
challenge is **selectivity** — both across **alleles** and across the **HRAS/NRAS isoforms** (nearly
identical across the switch regions). In-silico binder "hit rates" vary **enormously** by target and
tool, and the **great majority of in-silico hits still fail experimentally** — expect KRAS to sit at
the harder end. A designed binder that passes every filter is a **hypothesis**, not a drug:
`pae_interaction` low does **not** mean it binds, a low isoform `pae` delta does **not** prove
selectivity, and SPR/BLI plus an isoform panel are mandatory. **You are graded on rigor, reasoning,
and reproducibility — not on whether the binder works.** A meticulous campaign with a low hit rate and
sharp failure analysis is an excellent capstone. Any example numbers in the notebooks are labeled
`EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as real — and there are **no fabricated K_D
values** anywhere.

## Responsible research
This project designs **inhibitory/blocking** binders to **KRAS**, a human **oncotarget**, for **cancer
therapeutics and diagnostics** — a defensible, in-scope therapeutic/diagnostic purpose under
`MASTER_BLUEPRINT.md §7`. It is framed for oncology only. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause harm. Real
gene-synthesis orders must go through a biosecurity-screening provider (IGSC member); wet-lab work
requires institutional biosafety/ethics approval. If your chosen target raises dual-use concern,
discuss a defensible neutralizing/diagnostic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project reuses the **binder-family template**
(Project 06): the BindCraft/RFdiffusion-binder + AF2-Multimer + shared-filter pattern, with a
KRAS-specific **isoform-specificity** layer added on top.
