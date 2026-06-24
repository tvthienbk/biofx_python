# Project 01 — AF2 / ESMFold / Boltz Validation Harness & Confidence Calibration

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Validation & tooling (foundational) · **Compute tier:** Free Colab T4

## The problem (and why it matters now)
Every de novo design pipeline lives or dies by its *in-silico filter* — yet the confidence
metrics it rests on (pLDDT, PAE, self-consistency RMSD) are routinely misread. pLDDT is
reported as "stability," PAE is ignored, and self-consistency thresholds are copied between
papers without checking they transfer. Before a lab designs a single new protein, it needs a
**calibrated, reproducible validation harness** and an evidence-based answer to: *which metric
actually predicts experimental success, and at what cutoff?* This project builds that harness —
and it becomes shared infrastructure the rest of the cohort depends on.

## What you will do
You will run and interpret three structure predictors (AlphaFold2 via ColabFold, ESMFold,
Boltz-2), compute the standard confidence/quality metrics, and **calibrate them against known
experimental outcomes** drawn from published de novo design datasets. You deliver a reusable,
documented validation module plus a "Validation SOP" card with calibrated cutoffs by design
type — all reproducibly on Google Colab.

## Learning objectives
1. Run AF2/ColabFold, ESMFold, and Boltz-2, and correctly parse pLDDT, PAE, and pTM.
2. Compute self-consistency scRMSD, TM-score/novelty, and per-residue confidence.
3. Calibrate each metric against real experimental outcomes (ROC/PR), and find the best single + composite predictor.
4. Deliver a reusable validation module + SOP that the whole cohort adopts.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
ColabFold (AlphaFold2), ESMFold (via HuggingFace transformers), Boltz-2, TM-align / Foldseek
(novelty + structure comparison), Biopython, py3Dmol, scikit-learn (ROC/PR), pandas/matplotlib.

## Data
A curated set of **designed proteins with known experimental outcomes** (sequence + folded?/bound?)
assembled from published de novo design papers' supplementary data, plus 5–10 natural proteins as
positive references — exact accessions and licenses are in `data/README.md`. **Verify every
accession on RCSB/UniProt in Week 1; entries get superseded, and you must log each item's source DOI and license.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Metric-definitions write-up + reproduced single-sequence prediction |
| D1 | P1 (3–6)   | Working prediction wrapper (AF2/ESMFold/Boltz → parsed confidence) + repo |
| D2 | P2 (7–12)  | Curated labeled dataset (≥40 designs + ≥10 natural refs) + all predictions |
| D3 | P3 (13–18) | Calibration study: ROC/PR per metric + best single/composite predictor |
| D4 | P4 (19–22) | Validation SOP (calibrated cutoffs by design type) + hardened module |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a validated, documented **validation module** + an SOP card with calibrated cutoffs, adopted as cohort infrastructure |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
This is a *tooling/benchmarking* project, so "success" is a well-calibrated, honestly-reported
harness — not a high hit rate. Expect that no single metric perfectly separates outcomes; the
interesting result is usually a **composite** predictor and a clear statement of where it fails.
**You are graded on rigor, reasoning, and reproducibility — not on whether any protein works.**

## Responsible research
This project analyses *existing, published* sequences and predicts their structures; it designs
no new functional proteins, so its dual-use surface is low. It is framed for building **safe,
calibrated validation infrastructure** for the cohort. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, or any design intended to cause harm. If you later extend the
dataset, exclude sequences whose function is primarily harmful, and record the provenance/license
of every item. Wet-lab follow-up by other projects must go through institutional biosafety/ethics
approval and a gene-synthesis screening provider.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. **Your `filtering_pipeline.py` improvements feed
back into `shared/` for Projects 02–25 — coordinate via pull request.**
