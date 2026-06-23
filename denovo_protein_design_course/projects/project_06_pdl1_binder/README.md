# Project 06 — De Novo Mini-Binder vs PD-L1 (Checkpoint Blockade)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed binder design · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
PD-1/PD-L1 checkpoint blockade transformed oncology, but the approved drugs are **monoclonal
antibodies** — large (~150 kDa), expensive to manufacture, slow to clear, and limited in solid-tumor
penetration. Small **de novo mini-binders** (40–80 residues) to the PD-1-binding face of PD-L1 are an
active, real alternative: better tumor penetration, cheaper microbial manufacture, easy formatting
into multivalent or imaging constructs. This project designs such binders computationally and
compares the two dominant generative paradigms head-to-head. **This is a therapeutic/diagnostic
checkpoint-blockade project; framing is oncology-only.**

## What you will do
By the end you will have run an end-to-end de novo binder campaign against PD-L1 with **two**
paradigms (BindCraft and RFdiffusion-binder + ProteinMPNN), triaged both pools with the shared
multi-layer in-silico filter (`design_type="binder"`), benchmarked them head-to-head, and produced a
costed SPR/BLI experimental validation plan with PD-1-competition and scrambled-interface controls —
all reproducibly, degrading gracefully when only a free T4 is available.

## Learning objectives
1. Prepare a target structure and select **hotspots on the PD-1-binding (competitive) face** of PD-L1.
2. Run BindCraft (or FreeBindCraft) and RFdiffusion binder mode + ProteinMPNN against that epitope.
3. Apply the shared 4-layer filter with binder cutoffs (`pae_interaction` is the key binder metric) and report an honest hit rate.
4. Compare the two paradigms (hit rate, interface energy, diversity, novelty) and design a controlled wet-lab validation plan.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
BindCraft (or FreeBindCraft) for one-shot hallucination-based binders; RFdiffusion **binder mode** +
ProteinMPNN for diffusion-then-sequence binders; AF2-Multimer (ColabFold) for interface confidence
(`pae_interaction`); the shared `filtering_pipeline.py` (`design_type="binder"`); Biopython, py3Dmol.
Optional stretch: Boltz-2 affinity prediction on top hits (scaffold only — never a fabricated K_D).

## Data
PD-1/PD-L1 complex structures to define the competitive epitope and hotspots — candidate accessions
**4ZQK** and **5O45** (**candidate — verify on RCSB**). The binder targets the PD-L1 ectodomain face
that PD-1 engages. Exact accessions, sizes, and licenses are in `data/README.md`. **Verify every
accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + target prep + reproduced BindCraft mini-run |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Two-paradigm design pool (BindCraft + RFdiffusion) + design log + interim report |
| D3 | P3 (13–18) | Ranked top 10–20 each + BindCraft-vs-RFdiffusion benchmark figures + filtering report |
| D4 | P4 (19–22) | Validation report + costed SPR/BLI + PD-1-competition plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** binder design report + **head-to-head BindCraft-vs-RFdiffusion comparison** + top 10–20 each with an SPR/BLI + PD-1-competition + scrambled-interface-negative validation plan |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
In-silico binder "hit rates" vary **enormously** by target and tool — anywhere from single-digit to
tens of percent passing the filter, and the **great majority of in-silico hits still fail
experimentally**. A designed binder that passes every filter is a **hypothesis**, not a drug:
`pae_interaction` low does **not** mean it binds, and SPR/BLI validation is mandatory. **You are
graded on rigor, reasoning, and reproducibility — not on whether the binder works.** A meticulous
campaign with a low hit rate and sharp failure analysis is an excellent capstone. Any example numbers
in the notebooks are labeled `EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as real.

## Responsible research
This project designs **inhibitory/blocking** binders to a human checkpoint protein (PD-L1) for
**cancer immunotherapy and diagnostics** — a defensible, in-scope therapeutic/diagnostic purpose. It
is framed for checkpoint-blockade oncology only. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause harm. Real
gene-synthesis orders must go through a biosecurity-screening provider (IGSC member); wet-lab work
requires institutional biosafety/ethics approval. If your chosen target raises dual-use concern,
discuss a defensible neutralizing/diagnostic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project is the **binder-family template** (Projects
07–13, 23 reuse its workflow): keep the BindCraft/RFdiffusion-binder + AF2-Multimer + shared-filter
pattern clean.
