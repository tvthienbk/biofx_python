# Project 03 — RFdiffusion Monomer Design: The Novelty–Foldability Frontier

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Generative backbone design (foundational tooling) · **Compute tier:** Colab T4 (small batches) / A100 or HPC (full campaign)

## The problem (and why it matters now)
Generative backbone models like RFdiffusion can invent protein folds that have no close natural
relative — genuinely *novel* topology. But novelty is not free: the further a backbone strays from
the patterns the predictor was trained on, the less likely a designed sequence actually folds back
to it, and the higher the experimental risk. The live research question is **where the frontier
sits** — *how novel can a monomer backbone be (low TM-score to the PDB) while still self-consistently
folding (scRMSD < 2 Å)?* This project maps that novelty-vs-foldability Pareto frontier across protein
length and secondary-structure topology, and turns it into a usable **"novelty budget"** for the
cohort: how much novelty you can spend before foldability collapses.

## What you will do
By the end you will have run an end-to-end de novo design campaign, triaged it with a
multi-layer in-silico filter, benchmarked your approach, and produced a costed
experimental validation plan — all reproducibly on Google Colab.

Concretely: you generate hundreds of RFdiffusion monomer backbones across lengths {80, 120, 200,
300} and secondary-structure biases (all-α, all-β, mixed), redesign each with ProteinMPNN, fold the
sequences back with AF2/ESMFold to measure self-consistency (scRMSD), score novelty with
Foldseek/TM-align against the PDB, and plot the **novelty-vs-scRMSD frontier** with per-topology and
per-length success rates.

## Learning objectives
1. Run RFdiffusion in unconditional and topology-constrained (secondary-structure-biased) monomer mode.
2. Pair generated backbones with ProteinMPNN sequence design and AF2/ESMFold self-consistency (scRMSD).
3. Quantify structural novelty (Foldseek/TM-score to the PDB) and separate it cleanly from foldability.
4. Map the novelty-vs-foldability Pareto frontier across length and topology, and derive a defensible "novelty budget."

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
RFdiffusion (via the ColabDesign notebook), ProteinMPNN, ColabFold (AlphaFold2) / ESMFold for
self-consistency, Foldseek + TM-align for novelty scoring, Biopython, py3Dmol/PyMOL, pandas/matplotlib.

## Data
**No external data is needed for generation** — RFdiffusion designs monomers from noise. The only
data dependency is the **PDB / Foldseek reference database used for novelty scoring**, which is
**large and fetched by the student, never committed** (see `data/README.md` for sizes and the
download route). `download_data.py` fetches only a handful of small natural reference folds (e.g.,
1UBQ, 1L2Y, 2GB1, 1ENH, 1MJC) for novelty-scoring sanity checks. **Verify every accession on
RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement (measurable novelty/foldability criteria) + reproduced monomer-design tutorial (10 backbones) |
| D1 | P1 (3–6)   | Working minimal pipeline (generate → MPNN → self-consistency → novelty) + first small batch + repo |
| D2 | P2 (7–12)  | Full backbone pool across lengths × SS-bias + design log + `results/backbones.csv` + interim report |
| D3 | P3 (13–18) | Ranked top candidates + novelty-vs-scRMSD frontier + per-topology/length success rates + filtering report |
| D4 | P4 (19–22) | Validation report + costed synthesis/expression plan with paired controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a **"novelty budget" guideline** + a selected **novel-but-foldable design set** with a controlled synthesis plan |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
Self-consistency success (scRMSD < 2 Å) is **high for short, idealized helical folds and drops
steeply as novelty rises and length grows**; **all-β topologies are the hardest** and longest backbones
the least reliable. Do not expect a uniform pass rate — expect a *frontier*: a clear trade-off curve.
Report honest per-topology and per-length pass rates, not a single cherry-picked novel fold.
**You are graded on rigor, reasoning, and reproducibility — not on whether the protein works.** A
meticulous campaign with a low hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is a **methods/tooling project** that generates *novel monomeric proteins* and measures their
foldability and novelty; it designs no binder, toxin, or pathogen component, so its **dual-use
surface is low**. It is framed for building safe generative-design infrastructure and understanding
the novelty–foldability trade-off. Out of scope: enhancing pathogen transmissibility/virulence,
toxins, or any design intended to cause harm. Real gene-synthesis orders must go through a
biosecurity-screening provider; wet-lab work requires institutional biosafety/ethics approval. If a
generated fold is later repurposed toward a functional target, re-evaluate it under
`MASTER_BLUEPRINT.md §7` before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (the Foldseek PDB/AFDB database, weights)
out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
