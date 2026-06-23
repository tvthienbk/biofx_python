<!-- README_TEMPLATE.md — Claude Code fills {{TOKENS}} from the PROJECT_CATALOG.md entry. -->
# Project {{NN}} — {{PROJECT_TITLE}}

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** {{PARADIGM}} · **Compute tier:** {{COMPUTE_TIER}}

## The problem (and why it matters now)
{{REAL_WORLD_PROBLEM_2_4_SENTENCES}}

## What you will do
By the end you will have run an end-to-end de novo design campaign, triaged it with a
multi-layer in-silico filter, benchmarked your approach, and produced a costed
experimental validation plan — all reproducibly on Google Colab.

## Learning objectives
{{OBJECTIVE_1}}
{{OBJECTIVE_2}}
{{OBJECTIVE_3}}
{{OBJECTIVE_4}}

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following the timeline.

## Tools
{{TOOLS_LIST}}

## Data
{{DATA_SUMMARY}} — exact accessions and licenses are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + benchmark figures + filtering report |
| D4 | P4 (19–22) | Validation report + costed experimental plan {{+OPTIONAL_WETLAB}} |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** {{PROJECT_SPECIFIC_DELIVERABLE}} |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
{{REALISTIC_HIT_RATE_NOTE}} **You are graded on rigor, reasoning, and reproducibility — not on whether the protein works.** A meticulous campaign with a low hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
{{RESPONSIBLE_RESEARCH_PARAGRAPH}} This project is framed for {{LEGITIMATE_PURPOSE}}. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening provider; wet-lab work requires institutional biosafety/ethics approval. If your chosen target raises dual-use concern, discuss a defensible neutralizing/diagnostic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
