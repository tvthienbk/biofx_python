# Project 04 — Symmetric Protein Nanocage / Oligomer Design

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Symmetric backbone design + multimer validation · **Compute tier:** A100 recommended

## The problem (and why it matters now)
Self-assembling protein nanocages are a leading platform for **multivalent vaccine antigen display**
and for delivery — arraying many copies of an antigen on a symmetric particle boosts immune
responses, and the same scaffolds carry cargo. The hard, high-impact part is designing **subunits
that reliably form the *target* symmetry and not the wrong oligomer**: a sequence intended to close
into a C3 trimer may instead prefer a dimer, a tetramer, or an off-target tangle. This project
designs symmetric assemblies (cyclic C3/C4 and dihedral D2), validates the subunit *and* the
interface with AF2-Multimer, and — crucially — teaches you to reason honestly about
**oligomeric-state error**, the failure mode that wastes the most wet-lab effort in this field.

## What you will do
By the end you will have run an end-to-end de novo design campaign, triaged it with a
multi-layer in-silico filter, benchmarked your approach, and produced a costed
experimental validation plan — all reproducibly on Google Colab. Concretely: generate C3/C4/D2
backbones with RFdiffusion symmetric mode, sequence-design them with **tied** ProteinMPNN (so all
symmetry-related subunits share one sequence), predict each assembly with AF2-Multimer, filter on
subunit scRMSD / interface pAE / symmetry RMSD, and write a ranked candidate set with an
nsEM/SEC-MALS validation plan.

## Learning objectives
1. Design symmetric assemblies (Cn/Dn) with RFdiffusion symmetric mode and symmetric contigs.
2. Sequence-design with **tied positions** so symmetry-related subunits share one sequence.
3. Validate the subunit *and* the interface with AF2-Multimer (subunit scRMSD, interface pAE, symmetry RMSD).
4. Reason rigorously about **oligomeric-state error** — why designs form the wrong oligomer, and how to catch it in silico.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4 — which only runs the *small C3 demo*; a full campaign needs an A100).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; **the accessions list is empty until you verify Cn/Dn IDs in Week 1**).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the deterministic **mock** backend with no GPU, so you can build the plumbing first.

## Tools
RFdiffusion (symmetric mode), ProteinMPNN (tied positions), AF2-Multimer / ColabFold (multimer mode),
SymDesign concepts (symmetry definitions + docking), py3Dmol, Biopython, pandas/matplotlib. The
shared filter is `shared/filtering_pipeline.py` (run with `design_type="oligomer"`).

## Data
Light by design — the campaign *generates* backbones. You assemble a small set of **reference
homo-oligomers** (a natural Cn and a Dn, verified on RCSB) and a teaching scaffold of symmetry
definitions; the designed **I3-01 / I53-50 nanocage family** is named for context — exact accessions
and licenses are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; nanocage
and oligomer entries are easy to mis-remember and get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced small-C3 "hello-world" output |
| D1 | P1 (3–6)   | Working minimal pipeline + first small design batch + repo |
| D2 | P2 (7–12)  | Full C3/C4/D2 design pool (tied MPNN) + design log + interim report |
| D3 | P3 (13–18) | Ranked top assemblies + benchmark figures (symmetry order, tied vs untied) + filtering report |
| D4 | P4 (19–22) | Validation report + nsEM/SEC-MALS experimental plan (+ optional wet-lab data) |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** an assembly design report + a ranked C3/C4/D2 candidate set with an nsEM/SEC-MALS validation plan (and an epitope-graft antigen-display extension) |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
**Correct-symmetry assembly is hard, and wrong-oligomer outcomes are common.** AF2-Multimer interface
pAE is a *necessary-not-sufficient* filter: passing it does not prove the cage assembles, and only
negative-stain EM (nsEM) and SEC-MALS / native-MS confirm the actual oligomeric state. Report honest
assembly success rates and **never claim a cage "will assemble."** Any example distributions in the
notebooks come from the deterministic mock backend and are labelled `EXAMPLE_DATA` — never present
them as real results. **You are graded on rigor, reasoning, and reproducibility — not on whether the
protein works.** A meticulous campaign with a low success rate and sharp wrong-oligomer forensics is
an excellent capstone.

## Responsible research
Designed nanocages are **dual-use**. This project is framed for **vaccine antigen-display and
delivery scaffolds** (therapeutic / diagnostic / vaccine): an antigen-display extension means
grafting a **neutralizing or otherwise benign antigen** onto the cage surface to raise a protective
immune response (the RSV-F / SARS-CoV-2-RBD nanoparticle-vaccine paradigm). Out of scope, and to be
refused: displaying anything intended to **enhance pathogen fitness, transmissibility, or
virulence**, toxin display/delivery, or any assembly whose primary purpose is to cause harm. Real
gene-synthesis orders must go through a biosecurity-screening provider (IGSC member); wet-lab work
requires institutional biosafety/ethics approval. If your chosen antigen raises dual-use concern,
agree a defensible neutralizing/vaccine framing with your advisor before proceeding. See
`MASTER_BLUEPRINT.md §7`.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report.
