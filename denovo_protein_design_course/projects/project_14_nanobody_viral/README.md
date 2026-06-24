# Project 14 — De Novo Neutralizing Nanobody (VHH) vs a Conserved Viral Antigen

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Defensive de novo nanobody design (RFantibody / BoltzGen) · **Compute tier:** A100 recommended (free-tier T4 = tiny demo only)

## The problem (and why it matters now)
Nanobodies (VHHs, ~15 kDa, stable, cheap, deep-tissue) are an ideal pandemic-ready platform. De novo
VHH design against **conserved neutralizing** viral epitopes — the influenza HA **stem** or the RSV F
**prefusion** site — is newly feasible with RFantibody. This is a **defensive / neutralizing** project:
every design is steered to a conserved epitope to **block** the virus, never to enhance it.

## What you will do
You will choose a conserved neutralizing epitope, design VHH CDRs with RFantibody (and, as an
extension, BoltzGen nanobody mode), filter with antibody-aware metrics + developability, assess
predicted **breadth** across a strain panel, and plan a **yeast-display** screen — all with a
neutralizing/diagnostic framing.

## Learning objectives
1. Understand VHH/CDR structure and choose a conserved neutralizing epitope + a humanized framework.
2. Run RFantibody (RFdiffusion-Ab + ProteinMPNN) CDR design and score with AF2-Multimer/IgFold.
3. Filter with the shared antibody cutoffs + developability/humanness, and assess cross-strain breadth.
4. Plan a yeast-display screen (pool → FACS vs labeled antigen → sequence → express → SPR/neutralization).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (GPU check + installs; degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (week-by-week) and `MANUAL.md` (technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
RFantibody (RFdiffusion-Ab + ProteinMPNN), BoltzGen nanobody protocol, AF2-Multimer / IgFold
(ImmuneBuilder), humanness + developability heuristics, and the shared `filtering_pipeline.py`
(design_type="antibody").

## Data
A conserved-epitope reference complex — influenza HA + a broadly-neutralizing antibody (candidate:
**4FQI**, HA stem) or RSV F prefusion (candidate: **5UDE / DS-Cav1**) — plus a humanized VHH framework
and a **strain panel** for breadth. Exact accessions and licenses are in `data/README.md`. **Verify
every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Conserved-epitope + framework choice + problem statement + reproduced mini-run |
| D1 | P1 (3–6)   | Working minimal VHH pipeline + first design batch + repo |
| D2 | P2 (7–12)  | VHH CDR design pool (500+) + design log + interim report |
| D3 | P3 (13–18) | Ranked + developability-filtered candidates + cross-strain breadth + filtering report |
| D4 | P4 (19–22) | Yeast-display screen plan + neutralization/breadth plan + controls + cost |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a conserved-epitope VHH set (developability-filtered) + a yeast-display screen plan with a predicted-breadth profile |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo antibody/nanobody design hit rates are **LOW** (RFantibody reports low-single-digit %
experimental success at best; many designs fail folding/binding). Treat every surviving design as a
**screening input** for yeast display, not a finished binder, and report breadth as the **worst-case**
strain. **You are graded on rigor, reasoning, and reproducibility — not on whether the nanobody works.**

## Responsible research
This is a **defensive / neutralizing** project. In scope: designing a VHH that **blocks** the virus by
binding a conserved neutralizing epitope (the basis of antivirals and diagnostics). **Explicitly out
of scope** (do not design, refuse proposals for): anything intended to enhance viral
**transmissibility, virulence, affinity, immune escape, or fitness**; any pathogen gain-of-function.
Targeting a pathogen protein to *neutralize* it is fine; engineering the pathogen to be *more
dangerous* is not (`MASTER_BLUEPRINT.md §7`). Wet-lab work (including any neutralization assay)
requires institutional biosafety/IBC approval at the appropriate containment level; gene synthesis
must go through a biosecurity-screening provider. If your epitope/construct raises dual-use concern,
stop and consult your advisor.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report.
