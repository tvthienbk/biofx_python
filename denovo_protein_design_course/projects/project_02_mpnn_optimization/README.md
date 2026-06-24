# Project 02 — ProteinMPNN Optimization & Expression-Success Prediction

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Sequence design & tooling (foundational) · **Compute tier:** Free Colab T4

## The problem (and why it matters now)
ProteinMPNN sits in nearly every modern design pipeline — it is *the* step that turns a backbone
into a sequence — yet its three most-used knobs (**sampling temperature**, **backbone noise**, and
**sequences-per-backbone**) are usually copied between papers without checking they transfer. Those
settings strongly affect whether a design folds self-consistently *and* whether it expresses solubly
in *E. coli*; labs routinely waste synthesis budget on sequences chosen at poorly understood
settings. This project asks the practical question every wet lab faces before ordering genes: *which
MPNN settings maximize foldability **and** expressibility, and what do you trade away to get them?*
The answer is not a single "best" number — it is a Pareto map and a settings cheat-sheet, and it
becomes shared know-how the rest of the cohort reuses.

## What you will do
You will master the ProteinMPNN/LigandMPNN parameter space, run a **systematic sweep** over
temperature × backbone-noise × sequences-per-backbone across 20–30 backbones, and connect each
setting to four families of metric — sequence recovery, AF2/ESMFold recapitulation (foldability),
diversity (per-position entropy), and solubility proxies (net charge, hydrophobic-patch fraction,
a clearly-labeled CamSol-style heuristic). You deliver an honest **Pareto map** of the trade-offs
plus an **MPNN settings cheat-sheet** and a small settings-recommendation tool — all reproducibly
on a free Colab T4.

## Learning objectives
1. Master ProteinMPNN/LigandMPNN parameters and what each one does to a designed sequence.
2. Quantify the diversity ↔ recovery ↔ foldability ↔ expressibility trade-off across a real sweep.
3. Connect in-silico sequence properties (CamSol/SAP-style, net charge, hydrophobic patches) to *predicted* expression — and state honestly what these proxies do and do **not** tell you.
4. Produce a settings-recommendation tool and a cheat-sheet the cohort can actually use.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
ProteinMPNN and LigandMPNN (sequence design), ColabFold (AlphaFold2) / ESMFold (recapitulation →
scRMSD), solubility proxies (a CamSol-style heuristic / SAP, net charge at pH 7.4,
hydrophobic-patch fraction), Biopython, pandas/numpy/matplotlib. A deterministic **mock** MPNN
backend lets every notebook run end-to-end with no GPU.

## Data
20–30 **de novo backbones** (from Project 03 outputs or public design sets) plus **natural reference
monomers** as folding/recovery baselines — exact accessions and licenses are in `data/README.md`.
**Verify every accession on RCSB/UniProt in Week 1; entries get superseded.** The de novo backbones
do not come from single-accession fetches — assemble them from Project 03 or a public design set and
log their provenance.

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement (trade-off + metrics table) + reproduced ProteinMPNN + recapitulation hello-world |
| D1 | P1 (3–6)   | Working minimal pipeline (backbone → MPNN → recapitulation → recovery) + first design batch + repo |
| D2 | P2 (7–12)  | Full sweep over the grid → `results/sequences.csv` (hundreds of sequences) + design log + interim report |
| D3 | P3 (13–18) | Ranked survivors via the shared filter + per-setting metric tables + Pareto-optimal settings + filtering report |
| D4 | P4 (19–22) | Settings-recommendation heuristic + codon/tag strategy + costed experimental validation plan |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** an **MPNN settings cheat-sheet** + a settings-recommendation tool/heuristic, adopted as cohort know-how |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
Typical ProteinMPNN **sequence recovery is ~40–50%** vs the native sequence — and recovery is *not*
the goal, just a sanity check. Recapitulation success (scRMSD < 2 Å) and predicted solubility both
vary strongly with settings, and **no single setting is universally best**: lower temperature buys
recovery and foldability but kills diversity; higher temperature and noise buy diversity at the cost
of foldability. The deliverable is an honest **Pareto map** and a **settings cheat-sheet**, not a
record number. Recapitulation never proves a protein folds, and the solubility proxies are
*heuristics* — they do not measure expression. **You are graded on rigor, reasoning, and
reproducibility — not on whether the protein works.** A meticulous sweep with a low recapitulation
rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is a **methods/tooling project** for foldable, soluble *monomers*: it optimizes a sequence-design
step and predicts expression, designing no binder, antibody, toxin, or pathogen-targeting protein, so
its dual-use surface is low. It is framed for building **safe, well-characterized sequence-design
know-how** for the cohort. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any
design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening
provider (IGSC member); wet-lab work requires institutional biosafety/ethics approval. If you later
apply these settings to a functional target, switch to that project's responsible-research framing and
discuss it with your advisor first.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. Your settings cheat-sheet feeds back into the cohort:
later projects (binders, enzymes, antibodies) all run MPNN and should adopt your recommended
defaults.
