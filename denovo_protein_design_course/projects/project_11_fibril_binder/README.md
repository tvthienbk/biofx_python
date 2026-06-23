# Project 11 — Conformation-Specific Binder vs Tau / α-Synuclein

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed binder design (conformation-selective) · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
Alzheimer's disease (tau) and Parkinson's disease (α-synuclein) are defined by pathological protein
**aggregates** — amyloid **fibrils** with an ordered cross-β core, now solved at near-atomic
resolution by cryo-EM. A binder that recognizes a **specific aggregated/fibril conformation** — and
**ignores the abundant, intrinsically disordered monomer** — is the basis of real tools: diagnostic
**PET tracers** and fibril-detection assays, and aggregation **modulators**. The hard part is not
making a binder; it is making one that **discriminates two conformations of the same protein**. This
project designs such binders computationally and tests their conformational selectivity head-to-head.
**This is a neurodegeneration diagnostic-tracer / therapeutic-modulator project; framing is
diagnostic/therapeutic, low dual-use.**

## What you will do
By the end you will have run an end-to-end de novo binder campaign against an **amyloid fibril surface**
(tau PHF or α-synuclein fibril) with **two** paradigms (BindCraft and RFdiffusion-binder +
ProteinMPNN), triaged both pools with the shared multi-layer in-silico filter (`design_type="binder"`),
and — the project's signature step — run a **conformational-specificity test** (model each binder vs
the **monomer** and the **fibril**; it must **prefer the fibril**), with a cross-amyloid
(tau-vs-α-syn) extension. You will produce a costed **fibril-vs-monomer ELISA/SPR** validation plan
with the mandatory controls and a diagnostic-tracer framing — all reproducibly, degrading gracefully
when only a free T4 is available.

## Learning objectives
1. Distinguish the **monomer** vs **fibril** conformations of an amyloid protein, and choose a target conformation + fibril-surface epitope from a cryo-EM structure.
2. Run BindCraft (or FreeBindCraft) and RFdiffusion binder mode + ProteinMPNN against that fibril surface.
3. Apply the shared 4-layer filter with binder cutoffs (`pae_interaction` is the key binder metric) and report an honest hit rate.
4. **Reason about conformational specificity (the hard part):** model the binder vs monomer vs fibril, require it to prefer the fibril, and design a fibril-vs-monomer specificity assay.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
BindCraft (or FreeBindCraft) for one-shot hallucination-based binders; RFdiffusion **binder mode** +
ProteinMPNN for diffusion-then-sequence binders; AF2-Multimer (ColabFold) for interface confidence
(`pae_interaction`) — run **per conformer** (fibril and monomer) for the specificity test; the shared
`filtering_pipeline.py` (`design_type="binder"`); cryo-EM fibril structures; Biopython, py3Dmol.
Optional stretch: Boltz-2 affinity prediction on top hits (scaffold only — never a fabricated K_D).

## Data
Cryo-EM **fibril** structures to design against and read the exposed surface epitope from — candidate
accessions **5O3L / 5O3T** (tau PHF) and **6CU7 / 6H6B** (α-synuclein fibril) (**candidate — verify on
RCSB**) — plus a **monomer model** (e.g., from the AlphaFold DB / a disordered-ensemble model) for the
specificity counter-test. The binder targets the ordered cross-β fibril surface. Exact accessions,
sizes, and licenses are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1;
entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + target-conformation choice + fibril-surface prep + reproduced mini-run |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Two-paradigm design pool (BindCraft + RFdiffusion) against the fibril + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + **conformational-specificity** analysis + BindCraft-vs-RFdiffusion benchmark + filtering report |
| D4 | P4 (19–22) | Validation report + costed **fibril-vs-monomer** ELISA/SPR plan with controls + diagnostic-tracer framing |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a **fibril-vs-monomer conformational-specificity analysis** + a fibril-selective **binder set** + a **validation plan** (fibril-vs-monomer ELISA/SPR, controls) with a **diagnostic-tracer** framing |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
**Conformational selectivity is VERY hard.** A binder must do more than stick to the fibril — it must
**reject the abundant disordered monomer**, and **most designs will not be selective.** In-silico
binder "hit rates" already vary enormously by target and tool (single-digit to tens of percent passing
the filter), and the **conformational-selectivity** rate on top of that is lower still; the **great
majority of in-silico hits fail experimentally**. A design that passes every filter — even the
in-silico monomer counter-test — is a **hypothesis**, not a tracer: `pae_interaction` low does **not**
mean it binds, the `specificity_gap` is a model proxy (not a measured fold-selectivity), and a
**fibril-vs-monomer assay is mandatory**. **You are graded on rigor, reasoning, and reproducibility —
not on whether the binder works.** A meticulous campaign with a low selective rate and sharp failure
analysis is an excellent capstone. Any example numbers in the notebooks are labeled `EXAMPLE_DATA` /
`SYNTHETIC` and must never be reported as real.

## Responsible research
This project designs **conformation-selective** binders to **pathological amyloid aggregates** (tau /
α-synuclein fibrils) for **neurodegeneration diagnostics** (PET tracers, fibril assays) and
**aggregation modulation** — a defensible, in-scope diagnostic/therapeutic purpose with **low
dual-use** risk (the target is a disease-associated aggregate, and the intent is to detect or modulate
it). It is framed for neurodegeneration diagnostics/therapeutics only. Out of scope: enhancing
pathogen transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause
harm. Real gene-synthesis orders must go through a biosecurity-screening provider (IGSC member);
wet-lab work (including any patient-derived material) requires institutional biosafety/ethics approval.
If your chosen target raises dual-use concern, discuss a defensible diagnostic framing with your
advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(Project 06): the BindCraft/RFdiffusion-binder + AF2-Multimer + shared-filter pattern is shared; the
project-specific addition is the **conformational-specificity** test (`scripts/binder_tools.py:
conformational_specificity` / `specificity_gap`).
