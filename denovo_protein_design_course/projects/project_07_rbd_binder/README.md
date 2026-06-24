# Project 07 — De Novo Neutralizing Binder vs SARS-CoV-2 / Pan-Sarbecovirus Spike RBD

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Defensive neutralizing-binder design (BindCraft + RFdiffusion) · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback only)

## The problem (and why it matters now)
Pandemic preparedness needs fast, broadly cross-reactive countermeasures. The SARS-CoV-2 spike
receptor-binding domain (RBD) engages the host receptor ACE2; antibodies that block this interaction
neutralize the virus, but the variable receptor-binding motif (RBM) mutates rapidly and escapes them.
Designing small **neutralizing** binders to a **conserved** RBD epitope (rather than the variable RBM)
is a live research direction for **variant-resistant antivirals and diagnostics**. This is a
**defensive** project: every design is steered to *block* the virus by occluding the host-receptor
(ACE2) face — never to enhance it.

## What you will do
You will choose and justify a conserved vs variable RBD epitope, run two de novo binder paradigms
(BindCraft and RFdiffusion binder mode) against it, triage the pool with the shared 4-layer filter,
assess predicted **breadth** across a panel of variant RBDs, and produce a costed validation +
breadth-testing plan with proper controls — all reproducibly, with a neutralizing/diagnostic framing.

## Learning objectives
1. Map conserved vs variable RBD epitopes (sarbecovirus conservation) and justify a target face.
2. Run BindCraft and RFdiffusion-binder + ProteinMPNN against a structural target, and score with AF2-Multimer.
3. Apply the shared binder filter and quantify predicted breadth across variant RBDs (worst-case, not best).
4. Write a controlled validation + breadth plan (ACE2-competition, pseudovirus neutralization) with biosafety oversight.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (GPU check + installs; degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (week-by-week) and `MANUAL.md` (technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
BindCraft (or FreeBindCraft), RFdiffusion binder mode + ProteinMPNN, AF2-Multimer (ColabFold),
sequence-conservation analysis, and the shared `filtering_pipeline.py` (design_type="binder").

## Data
The RBD–ACE2 complex (candidate: **6M0J**) defines the ACE2-binding face; plus a panel of **variant
RBD** sequences/structures (Wuhan/Delta/Omicron sublineages + other sarbecoviruses) for the breadth
analysis — exact accessions and licenses are in `data/README.md`. **Verify every accession on
RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Conserved-epitope map + problem statement (success criteria + controls) + reproduced mini-run |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (BindCraft + RFdiffusion) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + cross-variant breadth analysis + filtering report |
| D4 | P4 (19–22) | Validation + breadth-testing plan (ACE2-competition, pseudovirus neutralization), controls, cost |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a pandemic-preparedness report — a conserved-epitope neutralizing-binder set with a predicted-breadth analysis across variants |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo binder campaigns have variable, often low in-silico→experimental hit rates (single-digit to
tens of % pass the filter; far fewer validate), and **breadth is harder than affinity** — a binder
that holds across all variants is rare. The deliverable is an honest, controlled campaign + breadth
analysis, not a guaranteed antiviral. **You are graded on rigor, reasoning, and reproducibility — not
on whether the protein works.** Never present any predicted number as a measured result.

## Responsible research
This is a **defensive / neutralizing** project. In scope: designing a binder that **blocks** the
virus by occluding the host-receptor (ACE2)-binding face of a conserved RBD epitope — the basis of
antivirals and diagnostics. **Explicitly out of scope** (do not design, and refuse proposals for):
anything intended to enhance viral **transmissibility, virulence, receptor affinity, immune escape,
or fitness**; any gain-of-function on the pathogen. Targeting a pathogen protein to *neutralize* it is
fine; engineering the pathogen to be *more dangerous* is not (`MASTER_BLUEPRINT.md §7`). Wet-lab work
(including pseudovirus neutralization) requires institutional biosafety/IBC approval at the
appropriate containment level; any gene-synthesis order must go through a biosecurity-screening
provider. If your chosen epitope or construct raises dual-use concern, stop and consult your advisor.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report.
