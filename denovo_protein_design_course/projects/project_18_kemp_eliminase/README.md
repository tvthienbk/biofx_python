# Project 18 — De Novo Kemp Eliminase (the Field Benchmark)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo enzyme design (theozyme → scaffold → sequence → catalytic geometry) · **Compute tier:** A100 recommended for scaffolding; free-tier demo possible

## The problem (and why it matters now)
The **Kemp elimination** — base-catalysed ring opening of a benzisoxazole — is the model reaction
for de novo enzyme design: it has **no natural counterpart** (so any activity is genuinely designed,
not borrowed) and a **simple UV readout** (the product absorbs, giving easy kinetics). For fifteen
years computational Kemp eliminases were weak and only became efficient after directed evolution.
That changed recently: methods like **Riff-Diff** and **RFdiffusion2** reach near-natural rates
*without* directed evolution. That makes this both a near-perfect **teaching benchmark** and a
**genuine methods test** — and it is industrial / green-chemistry / basic-science in flavour, with
low dual-use risk.

## What you will do
By the end you will have run an end-to-end de novo enzyme-design campaign — **construct a theozyme**
(the catalytic functional groups around the transition state), **scaffold** it into thousands of
backbones, **sequence-design with LigandMPNN while fixing the catalytic residues**, triage with a
multi-layer filter centred on **catalytic-geometry RMSD vs the theozyme**, benchmark the scaffolding
methods, and produce a costed **kinetic-assay + directed-evolution plan** — all reproducibly, with a
no-GPU mock path so the plumbing runs anywhere.

## Learning objectives
1. Construct a Kemp-eliminase **theozyme**: a catalytic base + an aromatic π-stack + an H-bond donor placed around the 5-nitrobenzisoxazole transition state.
2. Scaffold the motif (RFdiffusion2 / Riff-Diff / RFdiffusion motif scaffolding) and sequence-design with **LigandMPNN preserving the catalytic residues**.
3. Validate **catalytic-residue geometry** (catalytic-geometry RMSD < 0.5 Å vs the theozyme), plus substrate docking and short active-site MD.
4. Plan a kinetic assay with the right controls (incl. a catalytic-residue→Ala "dead" mutant) and a directed-evolution path for hits.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the **mock**
   backend with no GPU; switch to the real backends on Colab/HPC where noted.

## Tools
Theozyme construction (catalytic base Asp/Glu + π-stack Trp/Tyr + H-bond donor for the
5-nitrobenzisoxazole TS), **RFdiffusion2 / Riff-Diff / RFdiffusion** motif scaffolding,
**LigandMPNN** (sequence design, catalytic residues fixed), **AF2** (catalytic-residue geometry +
active-site pLDDT), **AutoDock Vina** (substrate fit), **OpenMM** (active-site stability MD),
`shared/filtering_pipeline.py` with `design_type="enzyme"`.

## Data
Mostly **constructed, not downloaded**: you build the **theozyme** and the 5-nitrobenzisoxazole
transition-state geometry from literature/QM (`data/inputs/theozyme_def.txt` is a template to fill —
*not* fabricated data). `download_data.py` fetches a couple of **candidate reference designed Kemp
eliminases** as positive controls — exact accessions and licenses are in `data/README.md`. **Verify
every accession on RCSB in Week 1; the designed-Kemp lineage has many variants and entries get
superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output (mock theozyme hello-world) |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (scaffolds + LigandMPNN sequences, catalytic residues fixed) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + catalytic-geometry & scaffolding-method benchmark figures + filtering report |
| D4 | P4 (19–22) | Validation report (docking + MD) + costed kinetic-assay plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** Kemp theozyme → scaffold → sequence + a catalytic-geometry-filtered **<96-design** set + a **kinetic-assay plan** (UV product readout; kcat/KM; controls: natural reference, heat-killed, empty vector, catalytic-residue→Ala "dead" mutant) + a directed-evolution plan for hits `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo enzyme **hit rates are low**: often **<1% active without directed evolution**, and even
recent methods that improved this substantially **still require screening**. Crucially, **preserving
the catalytic geometry in silico does NOT guarantee activity** — a design can hold a perfect
active-site geometry and still be catalytically dead; only a **kinetic assay** decides. Any example
numbers in the notebooks are labelled `EXAMPLE_DATA`/`SYNTHETIC`. **You are graded on rigor,
reasoning, and reproducibility — not on whether the enzyme works.** A meticulous campaign with a low
hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is an **industrial / green-chemistry / basic-science** enzyme with **low dual-use** risk: the
Kemp elimination has no natural counterpart and no toxin/pathogen connection. The project is framed
for building and benchmarking de novo enzyme-design methodology. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, or any design intended to cause harm. Real gene-synthesis orders
must go through a biosecurity-screening provider (IGSC member); wet-lab work requires institutional
biosafety/ethics approval. If you adapt this template to a different reaction, re-check the target
against `MASTER_BLUEPRINT.md §7` with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (PDB dumps, model weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
This project is the **enzyme-family template** (Projects 19–21, 24 follow its structure).
