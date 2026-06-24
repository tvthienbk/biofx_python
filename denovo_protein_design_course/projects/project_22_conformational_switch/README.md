# Project 22 — Conformational-Switch / Multi-State Protein Design

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Multi-state generative design (frontier) · **Compute tier:** A100 recommended (two-backbone generation + multi-state MPNN + AF2 ×2 + MD); free Colab T4 = small fallback only

## The problem (and why it matters now)
Most designed proteins are built to hold *one* shape. The interesting biology — and a genuine
frontier of the field — is proteins that **change conformation, and therefore function, on a
stimulus**: pH, a ligand, light, temperature. These conformational switches underpin **smart
biomaterials, allosteric biosensors, and protein logic gates**. Designing one means solving a
much harder problem than single-state design: you must find **one amino-acid sequence that is
compatible with TWO different backbones** (state A and state B) and that can interconvert between
them when the trigger fires. de novo switches like the Baker lab's **LOCKR** system showed this is
possible, but it remains rare and hard: a sequence that folds well to one state usually folds badly
to the other, and even our best structure predictors may only ever show you *one* of the two states.

## What you will do
By the end you will have run an end-to-end de novo design campaign, triaged it with a
multi-layer in-silico filter, benchmarked your approach, and produced a costed
experimental validation plan — all reproducibly on Google Colab.

Concretely: you **define two target states + a trigger**, generate the two backbones with
RFdiffusion, run **multi-state ProteinMPNN** (residue identities *tied* across both backbones) to
search for a shared sequence, predict **both states from that one sequence** with AF2, reason about
the **energy gap** between the states (close enough to switch, distinct enough to define OFF/ON),
apply the shared monomer filter to **each state**, and plan a **state-change read-out** (FRET /
protease accessibility / SAXS) with paired controls.

## Learning objectives
1. Define a two-state design problem: two backbones + an explicit, physically plausible trigger, with measurable success criteria.
2. Run multi-state ProteinMPNN (tied/ensemble across both states) to search for one sequence compatible with both backbones.
3. Validate a switch in silico: predict BOTH states from one sequence, apply the foldability filter to each, and reason about the state energy gap — and its limits.
4. Design a state-change read-out (FRET / protease accessibility / SAXS) with the controls that actually prove a switch.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`.

## Tools
RFdiffusion (via the ColabDesign notebook — **two backbones**), **ProteinMPNN in multi-state /
tied mode** (ensemble across both states), ColabFold (AlphaFold2) to predict **both states**,
ESMFold for fast triage, OpenMM for a short transition-plausibility MD, Foldseek/TM-align and
Biopython for geometry, py3Dmol, pandas/matplotlib. LOCKR is the conceptual reference.

## Data
Reference switch / two-state designs (LOCKR, hinge open/closed pairs, a LOV photoswitch) as
starting points, plus a hand-authored **two-state definition** (`data/inputs/two_state_def.txt`:
state A / state B + trigger) — exact accessions and licenses are in `data/README.md`. **Every PDB
accession is flagged "candidate — verify on RCSB"; switch designs are deposited under varied names,
so confirm each before use.** The two state backbones you actually design against are **generated**
in notebook 02, not downloaded.

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement: two states + trigger + measurable success criteria + reproduced mock hello-world (one sequence, two states) |
| D1 | P1 (3–6)   | Working minimal pipeline (two states → multi-state MPNN → per-state prediction) + first small batch + repo |
| D2 | P2 (7–12)  | Two state backbones + multi-state MPNN shared-sequence pool (`results/multistate_designs.csv`) + design log + interim report |
| D3 | P3 (13–18) | Per-state filter (monomer cutoffs on BOTH states) + AF2-predicts-both-states + energy-gap analysis + filtering report |
| D4 | P4 (19–22) | Validation report + state-change read-out plan (FRET/protease/SAXS) with paired controls + (extension) transition MD |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a **multi-state sequence + two-state validation** (AF2 predicts both states from one sequence) + a **state-change read-out plan with controls**; light-switch (LOV) integration [stretch] |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
**Multi-state design is VERY hard.** One sequence that folds self-consistently to two *defined*
states is rare; a sequence that fits state A well usually fits state B poorly, and AF2 may only ever
return one of the two states, so confirming the switch in silico is genuinely difficult. Expect a
**low success rate**, expect the **energy-gap caveat** to bite (the gap proxy is teaching-grade, not
a real ΔΔG), and report it honestly. The deliverable is a *rigorously characterized switch
hypothesis with a real validation plan*, not a guaranteed working switch. **You are graded on rigor,
reasoning, and reproducibility — not on whether the protein works.** A meticulous campaign with a low
hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This project designs **conformational switches for smart biomaterials, allosteric sensors, and
protein logic gates** — basic-science and biomaterials framing with a **low dual-use surface**: the
designs have no targeted binding/toxic function, they change their own shape on a stimulus. It is
framed for building safe switchable-protein infrastructure and understanding multi-state
designability. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design
intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening provider;
wet-lab work requires institutional biosafety/ethics approval. If a switch is later coupled to a
functional payload (a binder, an enzyme, a delivery module), re-evaluate it under
`MASTER_BLUEPRINT.md §7` before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (RFdiffusion/MPNN/AF2 weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
