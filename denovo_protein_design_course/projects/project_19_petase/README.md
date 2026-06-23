# Project 19 — Plastic-Degrading Active-Site Design (PETase-like)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo enzyme design (theozyme → scaffold → sequence → catalytic geometry), emphasis on **thermostability** · **Compute tier:** A100 recommended for scaffolding + thermostability MD; free-tier demo possible

## The problem (and why it matters now)
PET (polyethylene terephthalate) is one of the most-produced plastics, and most of it is never
recycled. **PET hydrolases** — enzymes like *Ideonella sakaiensis* **IsPETase** and the engineered
leaf-branch compost cutinase **LCC** — depolymerise PET back to its monomers, enabling true
**circular chemistry** instead of downcycling. The catch is not the chemistry: PET hydrolysis uses
the same **Ser-His-Asp catalytic triad + oxyanion hole** found in every serine hydrolase. The catch
is **stability**. Industrial PET digestion runs hot (near PET's ~65–70 °C glass transition, where the
polymer becomes accessible), and wild-type IsPETase falls apart there. **Thermostability — not
catalytic novelty — is the real bottleneck**, which makes this a clean teaching project: graft a
known triad into a *stable* fold and let the campaign be decided by an MD-based stability ranking.

## What you will do
By the end you will have run an end-to-end de novo enzyme-design campaign — **define the serine-
hydrolase theozyme** (Ser-His-Asp triad + oxyanion hole around an ester transition state),
**scaffold** it into thermostable folds, **sequence-design with LigandMPNN while fixing the catalytic
triad**, triage with a multi-layer filter centred on **catalytic-geometry RMSD vs the theozyme**,
then **rank candidates by an MD-based thermostability proxy (RMSF + a melting-proxy)** and check
**substrate-pocket accessibility** by docking a PET-mimic ester — and produce a costed **activity +
thermostability assay plan** — all reproducibly, with a no-GPU mock path so the plumbing runs anywhere.

## Learning objectives
1. Define a serine-hydrolase **theozyme**: the **Ser-His-Asp catalytic triad** plus the **oxyanion hole** (two backbone-NH H-bond donors) placed around the **ester (tetrahedral-intermediate) transition state**.
2. Scaffold the motif into a **thermostable** fold (RFdiffusion2 / Riff-Diff) and sequence-design with **LigandMPNN preserving the catalytic triad**.
3. Validate **catalytic-geometry RMSD** (< 0.5 Å vs the theozyme) and then **rank by an MD-based thermostability proxy** (RMSF / melting-proxy) plus **PET-mimic substrate-pocket accessibility** (docking).
4. Plan an **activity assay** (pNP-ester colorimetric or PET-film/HPLC) + a **DSF thermostability** assay with the right controls (incl. a catalytic-Ser→Ala "dead" mutant).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the **mock**
   backend with no GPU; switch to the real backends on Colab/HPC where noted.

## Tools
Theozyme construction (Ser-His-Asp triad + oxyanion hole for the ester TS), **RFdiffusion2 /
Riff-Diff / RFdiffusion** motif scaffolding, **LigandMPNN** (sequence design, catalytic triad fixed),
**AF2** (catalytic-residue geometry + active-site pLDDT), **AutoDock Vina** (PET-mimic ester fit),
**OpenMM** (thermostability MD — RMSF + melting-proxy, the project's emphasis),
`shared/filtering_pipeline.py` with `design_type="enzyme"`.

## Data
Mostly **constructed, not downloaded**: you build the **theozyme** (Ser-His-Asp triad + oxyanion-hole
geometry) and the **PET-mimic ester** transition-state model from literature/QM
(`data/inputs/theozyme_def.txt` is a template to fill — *not* fabricated data). `download_data.py`
fetches a couple of **candidate reference PET hydrolases / cutinases** (IsPETase, cutinase) as
structural references and thermostability comparators — exact accessions and licenses are in
`data/README.md`. **Verify every accession on RCSB in Week 1; PET-hydrolase entries are numerous and
get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output (mock triad/oxyanion-hole hello-world) |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (scaffolds + LigandMPNN sequences, catalytic triad fixed) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + catalytic-geometry & **thermostability** benchmark figures + filtering report |
| D4 | P4 (19–22) | Validation report (geometry + MD-thermostability + docking) + costed activity + DSF assay plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** Ser-His-Asp triad + oxyanion-hole **theozyme → scaffold → sequence**, an **MD-thermostability-ranked** catalytic-geometry-filtered **<96-design** set, and an **activity-assay plan** (pNP-ester colorimetric or PET-film/HPLC; DSF thermostability; controls: natural reference, heat-killed, empty vector, catalytic-Ser→Ala "dead" mutant) + surface-residue redesign for solubility `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo enzyme **hit rates are low**: often **<5% active without directed evolution**, and even
recent methods that improved this substantially **still require screening**. For PET hydrolases the
twist is the **thermostability ↔ activity trade-off**: a fold stable enough to work at 65–70 °C can
be catalytically sluggish, and a rigid active site can lose the dynamics catalysis needs — so a
design that holds the triad geometry *and* survives the thermostability MD can still be inactive.
Crucially, **preserving the catalytic geometry in silico does NOT guarantee activity** — only an
**activity assay** decides, and only a **DSF/thermal-shift** measurement decides stability. Any
example numbers in the notebooks are labelled `EXAMPLE_DATA`/`SYNTHETIC` (no fabricated kcat). **You
are graded on rigor, reasoning, and reproducibility — not on whether the enzyme works.** A meticulous
campaign with a low hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is an **industrial / green-chemistry / pollution-remediation** enzyme with **low dual-use**
risk: PET hydrolysis breaks down a synthetic polymer into recyclable monomers — there is no
toxin/pathogen connection. The project is framed for building and benchmarking de novo enzyme-design
methodology for plastic degradation and circular chemistry. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, or any design intended to cause harm. Real gene-synthesis orders
must go through a biosecurity-screening provider (IGSC member); wet-lab work requires institutional
biosafety/ethics approval. If you adapt this template to a different reaction or substrate, re-check
the target against `MASTER_BLUEPRINT.md §7` with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (PDB dumps, model weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
This project follows the **enzyme-family template** (Project 18 — Kemp eliminase); its reaction
(ester hydrolysis) and emphasis (**thermostability MD**) differ.
