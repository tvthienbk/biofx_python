# Project 15 — Computational Antibody Affinity Maturation + Developability

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Antibody lead optimization (affinity maturation; NOT de novo design) · **Compute tier:** Colab T4–Pro (scoring is light/CPU-OK; AF2-Multimer pose checks are the heavier part — batch them)

## The problem (and why it matters now)
Therapeutic-antibody **lead optimization** — raising affinity while keeping **developability** (no
aggregation, no chemical-liability hotspots, expressible, stable) — is slow and expensive when done
purely in the lab, where thousands of variants get screened to find a few improvements. **Computational
affinity maturation** flips that: starting from a *known* antibody-antigen complex with a *measured* KD,
it proposes a **small, testable set** of improving CDR mutations so the wet lab tests ~10 variants
instead of thousands. This is directly industrially relevant — it is what antibody-engineering teams do.
The honest catch: most predicted affinity-improving mutations do **not** validate, so the deliverable is
a *ranked* short list plus the experiment that would test it, never a claimed affinity.

## What you will do
By the end you will have taken an existing antibody-antigen complex, scored single CDR mutations with
**ESM-1v** and **AbLang** and run **ProteinMPNN** CDR redesigns (framework FIXED), checked that
survivors keep the **binding pose** with **AF2-Multimer**, screened them for **developability
liabilities** (deamidation/oxidation/glyc/unpaired-Cys), and produced a **SPR-kinetics + DSF validation
plan with controls** — all reproducibly, with a deterministic mock path that runs anywhere and a
clearly-marked real path (light scoring on T4; batched AF2-Multimer).

## Learning objectives
1. Start from a known antibody-antigen complex with a measured KD; identify the CDR contact residues you are allowed to mutate (framework fixed).
2. Propose affinity-improving CDR mutations with ESM-1v / AbLang scoring and ProteinMPNN CDR redesign, and rank them (no fabricated KD/ΔΔG).
3. Verify the binding pose is maintained (AF2-Multimer pae_interaction + scRMSD) and screen for developability liabilities before synthesis.
4. Write an SPR-kinetics / DSF validation plan with mandatory controls (WT baseline + a destabilizing decoy + a specificity panel).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; **you pick + verify the complex** in Week 1).
5. Work through notebooks `01 → 05` following the timeline (everything runs on the `mock` backend with no GPU).

## Tools
ESM-1v (protein-LM mutation scoring), AbLang / AbLang2 (antibody-specific LM), ProteinMPNN (CDR
redesign, framework fixed), AF2-Multimer (ColabFold) for binding-pose maintenance, and developability
filters (TAP / CamSol concepts; a deamidation/oxidation/Cys hotspot scan — used as teaching heuristics
here, swap in the real tools for any claim), plus the shared `shared/filtering_pipeline.py`
(`design_type="antibody"`).

## Data
ONE antibody-antigen complex from **SAbDab** (student-chosen) with a **measured KD in the literature** —
exact accession and license are in `data/README.md`. **You pick the complex; verify the accession on
SAbDab/RCSB in Week 1 and confirm a published KD exists; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement (chosen complex + measured KD + CDR contacts + success criteria) + reproduced mock hello-world |
| D1 | P1 (3–6)   | Working minimal maturation pipeline + first (mock/tiny-real) scored batch + repo |
| D2 | P2 (7–12)  | Candidate mutation set (`campaign.csv`: single mutations + CDR redesigns) + design log + interim report |
| D3 | P3 (13–18) | Antibody-filtered ranked candidates + pose-maintenance/developability/epistasis figures + filtering report |
| D4 | P4 (19–22) | SPR-kinetics + DSF validation plan + controls (WT + destabilizing decoy + specificity panel) + costed plan |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a ranked affinity-improving CDR-mutation set + a developability scan + an SPR-kinetics/DSF validation plan with controls (WT + a destabilizing decoy + a specificity panel) |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
Computational maturation **ranks** candidates; it does **not** measure affinity. **Most predicted
affinity-improving mutations do NOT validate** experimentally — that is the honest, expected result. So
the deliverable is a **small ranked set + the experiment to test it**, not a claimed improvement. Never
fabricate KD/ΔΔG numbers; the notebooks emit dimensionless **ranking** scores, all labelled `SYNTHETIC`
on the mock backend (and `EXAMPLE_DATA` where teaching data appears). pLDDT is not stability; a low
pae_interaction is pose confidence, not affinity. **You are graded on rigor, reasoning, and
reproducibility — not on whether the protein works.** A meticulous campaign that honestly reports a low
validation expectation, with a clean ranked set and a sound SPR/DSF plan, is an excellent capstone.

## Responsible research
This is a **therapeutic-antibody lead-optimization** project: you mature an existing antibody against its
(non-pathogen) target to raise affinity and keep developability. Dual-use risk is **low** — it improves a
therapeutic candidate rather than creating a novel hazard. This project is framed for that legitimate
therapeutic/diagnostic purpose. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or
any design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening
provider; wet-lab work requires institutional biosafety/ethics approval. If your chosen target raises
dual-use concern, discuss a defensible therapeutic/diagnostic framing with your advisor before
proceeding. See `MASTER_BLUEPRINT.md §7`.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **antibody-family template**
(Project 17): light ESM-1v/AbLang + ProteinMPNN scoring → AF2-Multimer pose check → developability →
`design_type="antibody"` filter → a SMALL ranked set + an SPR/DSF validation plan with controls.
