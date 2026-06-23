# Project 05 — Automated Multi-Layer Design-Triage Pipeline (Shared Engine)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Infrastructure & tooling (the cohort's filter engine) · **Compute tier:** Free Colab T4

## The problem (and why it matters now)
A real design campaign does not produce *a* protein — it produces **thousands** of candidate
sequences, each with a pile of in-silico metrics (scRMSD, pLDDT, pAE, solubility, interface energy,
MD drift). Picking the dozen worth synthesizing is, in most labs, a spreadsheet and a gut feeling:
irreproducible, undocumented, and impossible to defend. This project builds the missing
infrastructure — an **automated, documented, tested 4-layer filter** that scores, ranks, and
reports on a design pool the same way every time. Your deliverable *is* `shared/filtering_pipeline.py`,
the engine Projects 01 and 03 feed and Projects 06–25 depend on. The central, honest message you
must internalize and write up: **no in-silico metric perfectly separates true hits from false ones —
filters enrich, they do not guarantee.**

## What you will do
You will implement and unit-test the four filter layers (self-consistency → orthogonal agreement →
physics → optional short MD) as clean Python functions behind tidy boundaries, justify each cutoff
per design type, run the engine on a mixed design pool, and emit ranked tables plus a survival
figure. Then you will write the project's defining artifact: an **honest discrimination-problem
analysis** — enrichment at each layer on a *labeled* pool, a cutoff-sensitivity sweep, and a clear
statement of where the filter fails. All of it is pure-Python scoring, so it runs end-to-end on a
free T4 (or even CPU) with a clearly-labeled `EXAMPLE_DATA` pool when no GPU pool is at hand.

## Learning objectives
1. Implement the 4-layer filter (`self_consistency` → `orthogonal_check` → `physics_filter` → `dynamics_filter`) as clean, **unit-tested** functions with heavy tools kept behind function boundaries.
2. Define and **justify cutoffs per design type** (monomer/binder/enzyme/antibody/oligomer), and reason about their sensitivity.
3. Emit ranked tables + a survival-at-each-layer figure via `rank_designs()`, `run_pipeline()`, and `report()`.
4. Document the **discrimination problem** honestly: enrichment per layer, cutoff sensitivity, and the false-positive/false-negative reality.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU (a T4 is plenty; this filter is CPU-fine).
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Build the labeled teaching pool: `python scripts/make_example_pool.py` → `results/pool.csv` (clearly synthetic `EXAMPLE_DATA`).
5. Run the tests against the shared engine: `python scripts/test_filtering.py` (no pytest, no GPU needed).
6. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
Python (pandas, numpy, matplotlib), Biopython (Cα-RMSD). The metrics the filter *scores* come from
upstream tools — ColabFold/AF2 + ESMFold (self-consistency & orthogonal layers), Boltz-2 (a third
opinion + affinity), optional PyRosetta / FreeBindCraft relax and CamSol-style solubility (physics
layer), short OpenMM MD (dynamics layer) — all kept **behind clean function boundaries** so the
engine itself needs no GPU. scikit-learn is used only for the enrichment/ROC bookkeeping in the
analysis.

## Data
A pre-computed pool of **~100–500 designs with predictions** — in production these come from
Projects 01/03 or public design sets, *not* a single-accession fetch. For teaching, you generate a
**labeled, clearly-synthetic `EXAMPLE_DATA` pool** (`scripts/make_example_pool.py`, fixed seed) with
*planted* known-good and known-bad designs so the layers can be developed and unit-tested with **no
GPU**. `data/download_data.py` fetches only a few natural reference structures — exact accessions
and licenses are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | API spec write-up (`Design` + layer signatures) + Layer 1 implemented & asserted on planted designs |
| D1 | P1 (3–6)   | Working minimal engine (Layer 1 + ranking + report) + labeled `EXAMPLE_DATA` pool + repo |
| D2 | P2 (7–12)  | Layers 2 + 3 implemented + unit tests (known-good passes / known-bad fails) + design log |
| D3 | P3 (13–18) | Ranked CSV + survival figure from the **shared** engine + enrichment-per-layer + discrimination analysis |
| D4 | P4 (19–22) | Cutoff-sensitivity study + optional Layer 4 (short MD) hook + cohort-adoption (PR) guide |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** the tested, documented `filtering_pipeline.py` contribution (ranked CSV + survival figure + `report()`), packaged for cohort adoption, **plus the discrimination-problem analysis** |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
This is an **infrastructure** project, so "success" is a clean, tested, documented filter plus an
*honest* discrimination-problem writeup — **not** a perfect classifier. Expect that no single metric
(and no single layer) cleanly separates real hits from decoys; the interesting, gradeable result is
the **enrichment** each layer buys, *where* it fails, and how sensitive the ranking is to your
cutoffs. Every example number you show is `EXAMPLE_DATA` and must be labeled as such — never present
synthetic enrichment as a real result. **You are graded on rigor, reasoning, and reproducibility — not on whether the protein works.** A meticulous campaign with a low hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This project builds *infrastructure* — it scores and ranks designs others produce; it designs no new
functional protein itself, so its dual-use surface is low. It is framed for building **safe,
reproducible triage infrastructure** for the cohort, scoring pools whose default framing is
neutralizing/diagnostic/industrial. Out of scope: enhancing pathogen transmissibility/virulence,
toxins, or any design intended to cause harm — **the filter must not be used to optimize designs
whose purpose is harmful.** Real gene-synthesis orders (by downstream projects) must go through a
biosecurity-screening provider; wet-lab work requires institutional biosafety/ethics approval. If a
pool you are asked to score raises dual-use concern, decline it and discuss a defensible
neutralizing/diagnostic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. **Your `filtering_pipeline.py` improvements feed back
into `shared/` for Projects 01–25 — coordinate via pull request; do not silently overwrite the
shared file.**
