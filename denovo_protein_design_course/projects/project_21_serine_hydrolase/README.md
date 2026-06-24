# Project 21 — De Novo Serine Hydrolase / Esterase (Green Chemistry)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo enzyme design (theozyme → scaffold → sequence → catalytic geometry) · **Compute tier:** A100 recommended for scaffolding; free-tier demo possible

## The problem (and why it matters now)
**Serine hydrolases** — esterases, lipases, proteases — are the **industrial workhorses** of
biocatalysis: ester synthesis and hydrolysis, kinetic resolution of chiral building blocks, and the
enzymes in laundry detergents all run on the same **Ser-His-Asp triad + oxyanion hole**. For decades
you could only *borrow and tweak* a natural hydrolase. That changed with the **2025 Science de novo
serine-hydrolase work (Lauko et al.)**, which **designed efficient hydrolases from scratch** — a
tractable, validated frontier result. This project reproduces that workflow on a general esterase:
it is **green-chemistry / industrial** in flavour, with **low dual-use** risk.

## What you will do
By the end you will have run an end-to-end de novo enzyme-design campaign — **construct a theozyme**
(the Ser-His-Asp triad + the oxyanion hole around the ester tetrahedral intermediate), **scaffold** it
into many backbones, **sequence-design with LigandMPNN while fixing the catalytic triad**, triage with
a multi-layer filter centred on **catalytic-geometry RMSD vs the theozyme** plus **pocket
accessibility** and **substrate-scope** (acyl-chain length), and produce a costed **pNP-ester
steady-state kinetics + DSF plan** whose perfect negative is a **catalytic-Ser→Ala "dead" mutant** —
all reproducibly, with a no-GPU mock path so the plumbing runs anywhere.

## Learning objectives
1. Construct a serine-hydrolase **theozyme**: the **Ser-His-Asp catalytic triad** + an **oxyanion hole** placed around the ester **tetrahedral intermediate**.
2. Scaffold the motif (RFdiffusion2 / Riff-Diff / RFdiffusion motif scaffolding) and sequence-design with **LigandMPNN preserving the catalytic triad + oxyanion-hole donors**.
3. Validate **catalytic-residue geometry** (catalytic-geometry RMSD < 0.5 Å vs the theozyme), **pocket accessibility** (substrate docking), active-site MD stability, and **substrate scope** (acyl-chain length).
4. Plan a **pNP-ester steady-state kinetic assay** + DSF with the right controls — a **catalytic-Ser→Ala "dead" mutant** (the perfect negative), a natural reference, and empty vector.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the **mock**
   backend with no GPU; switch to the real backends on Colab/HPC where noted.

## Tools
Theozyme construction (**Ser-His-Asp triad + oxyanion hole** for the ester tetrahedral intermediate),
**RFdiffusion2 / Riff-Diff / RFdiffusion** motif scaffolding, **LigandMPNN** (sequence design, catalytic
triad + oxyanion-hole donors fixed), **AF2** (catalytic-residue geometry + active-site pLDDT),
**AutoDock Vina** (pocket accessibility + acyl-chain substrate-scope scan), **OpenMM** (active-site
stability MD), `shared/filtering_pipeline.py` with `design_type="enzyme"`.

## Data
Mostly **constructed, not downloaded**: you build the **theozyme** (triad + oxyanion hole) and the
ester transition-state geometry from literature/QM (`data/inputs/theozyme_def.txt` is a template to
fill — *not* fabricated data). `download_data.py` fetches a couple of **candidate reference serine
hydrolases** (a cutinase + a lipase) as triad-geometry references and positive controls — exact
accessions and licenses are in `data/README.md`. **Verify every accession on RCSB in Week 1; serine-
hydrolase entries are numerous and get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output (mock theozyme hello-world) |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (scaffolds + LigandMPNN sequences, catalytic triad fixed) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + catalytic-geometry, pocket-accessibility & scaffolding-method benchmark figures + filtering report |
| D4 | P4 (19–22) | Validation report (geometry + docking + MD + substrate scope) + costed pNP-ester kinetic-assay + DSF plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** triad theozyme → scaffold → sequence + a catalytic-geometry-filtered **<96-design** set + a **pNP-ester steady-state kinetics + DSF plan** with controls (catalytic-Ser→Ala dead mutant, natural reference, empty vector) + an **enantioselectivity** concept `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo enzyme **hit rates are low**: often **<5% active without directed evolution**, and even the
recent methods that improved this substantially **still require screening**. Crucially, **preserving
the catalytic geometry in silico does NOT guarantee activity** — a design can hold a perfect triad
geometry and still be catalytically dead (dynamics, desolvation, His pKa, oxyanion-hole subtleties,
second-shell effects all matter); only a **kinetic assay** decides, and the **catalytic-Ser→Ala dead
mutant** is what proves any measured rate is real. Any example numbers in the notebooks are labelled
`EXAMPLE_DATA`/`SYNTHETIC`; no kcat/KM/ee is fabricated. **You are graded on rigor, reasoning, and
reproducibility — not on whether the enzyme works.** A meticulous campaign with a low hit rate and
sharp failure analysis is an excellent capstone.

## Responsible research
This is an **industrial / green-chemistry / basic-science** enzyme with **low dual-use** risk:
esterases for synthesis, kinetic resolution, and detergents have no toxin/pathogen connection, and the
project is framed for building and benchmarking de novo enzyme-design methodology. Out of scope:
enhancing pathogen transmissibility/virulence, toxins, or any design intended to cause harm. Real
gene-synthesis orders must go through a biosecurity-screening provider (IGSC member); wet-lab work
requires institutional biosafety/ethics approval. If you adapt this template to a different reaction
(e.g. a protease or a toxin-relevant substrate), re-check the target against `MASTER_BLUEPRINT.md §7`
with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (PDB dumps, model weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
This project follows the **enzyme-family template** established by Project 18 (Kemp eliminase) and
shared with Projects 19/20/24 — theozyme → scaffold → LigandMPNN (catalytic residues fixed) →
catalytic-geometry filter — with this project's reaction (ester hydrolysis) and emphasis (geometry →
pocket → substrate scope → kinetics).
