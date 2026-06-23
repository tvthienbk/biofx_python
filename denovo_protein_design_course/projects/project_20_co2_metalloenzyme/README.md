# Project 20 — CO₂-Fixing Metalloenzyme (Carbonic-Anhydrase-Style)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo **metalloenzyme** design (Zn metal-site theozyme → scaffold → metal-aware sequence → metal-site geometry) · **Compute tier:** A100 recommended for the large scaffolding pool; free-tier demo possible

## The problem (and why it matters now)
**Carbon capture** needs robust, fast catalysts for **CO₂ hydration** (CO₂ + H₂O ⇌ HCO₃⁻ + H⁺), and
nature's champion is **carbonic anhydrase (CA)** — a tiny **Zn-metalloenzyme** that runs near the
diffusion limit. Designing a CA-style active site **de novo** is a genuine test of **metal-aware**
protein design: you must place a catalytic metal, hold three histidines in a clean tetrahedral cage
around it, and poise a Zn-bound hydroxide to attack CO₂. The **GRACE** paradigm (Hu 2024) showed this
is now tractable — it produced functional carbonic-anhydrase-style designs by generating a **large
pool (~10k)** and screening. This project reproduces that end-to-end. It is **industrial /
carbon-capture / basic-science** in flavour, with **low dual-use** risk.

## What you will do
By the end you will have run an end-to-end de novo **metalloenzyme**-design campaign — **construct a
metal-site theozyme** (a **Zn-His₃-OH** centre around the CO₂-hydration transition state), **scaffold**
it into a large pool of backbones, **sequence-design with metal-aware LigandMPNN while fixing the three
His ligands and passing the Zn as context**, triage with a multi-layer filter centred on **metal-ligand
geometry** (the Zn-N distances + N-Zn-N angles vs the target), add a **CLEAN-style functional
classification** and solubility check, benchmark **LigandMPNN vs ProteinMPNN at the metal site** and
**pool-size vs hit-rate**, and produce a costed **activity + metal-incorporation assay plan** — all
reproducibly, with a no-GPU mock path so the plumbing runs anywhere.

## Learning objectives
1. Define a **Zn-coordinating active site** (a 3-His cage + a Zn-bound hydroxide) as a metal-site theozyme around the CO₂-hydration transition state.
2. Scaffold the metal motif (RFdiffusion2 / Riff-Diff / RFdiffusion) and sequence-design with **metal-aware LigandMPNN preserving the three His ligands** (vanilla ProteinMPNN is metal-blind).
3. Validate **metal-site geometry** (metal-ligand RMSD < 0.5 Å; clean Zn-N distances + N-Zn-N angles), plus a CLEAN-style functional classification and a (caveated) short metal-site MD.
4. Plan an **activity + metal-incorporation assay** with the right controls (esterase-proxy pNPA and/or CO₂-hydration Wilbur-Anderson units; ICP/PAR metal check; apo enzyme, natural CA).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the **mock**
   backend with no GPU; switch to the real backends on Colab/HPC where noted.

## Tools
Metal-site theozyme construction (a **Zn-His₃-OH** centre around the CO₂-hydration TS),
**RFdiffusion2 / Riff-Diff / RFdiffusion** motif scaffolding, **metal-aware LigandMPNN** (the central
tool — fixes the three His ligands, passes the Zn as atom context), **ProteinMPNN** (metal-blind
baseline for the benchmark), **AF2** (active-site pLDDT + His₃ geometry; note AF2 does **not** place
the metal), a **CLEAN-style** functional classifier + solubility (GRACE-style triage), **AutoDock
Vina** (substrate fit toward the Zn-OH), **OpenMM** (short metal-site MD — **classical-metal-FF
caveat**), `shared/filtering_pipeline.py` with `design_type="enzyme"`.

## Data
Mostly **constructed, not downloaded**: you build the **metal-site theozyme** and the Zn-OH + CO₂
transition-state geometry from a verified CA structure / literature / QM (`data/inputs/metal_site_def.txt`
is a template to fill — *not* fabricated data). `download_data.py` fetches a couple of **candidate
reference carbonic anhydrase II structures** (read off the Zn-His₃ geometry; natural-CA positive
control) — exact accessions and licenses are in `data/README.md`. **Verify every accession on RCSB in
Week 1; CA has many deposited variants and entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output (mock metal-site theozyme hello-world) |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (scaffolds + metal-aware LigandMPNN sequences, His₃ ligands fixed) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + metal-geometry & LigandMPNN-vs-ProteinMPNN & pool-size-vs-hit-rate figures + filtering report |
| D4 | P4 (19–22) | Validation report (geometry + CLEAN + MD) + costed activity + metal-incorporation assay plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** Zn-His₃-OH metal-site design + a **metal-geometry-filtered <96-design set** + an **activity + metal-incorporation assay plan** (esterase-proxy pNPA and/or CO₂-hydration Wilbur-Anderson units; ICP/PAR metal-incorporation check; controls: **apo enzyme**, **natural CA**) + an **alternative-metal Co(II) substitution** test `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo **metalloenzyme** design is **hard** and hit rates are **low**: GRACE reached functional
CA-style designs only by generating a **large pool (~10k)** and screening. Three honest caveats stack
here: **(1)** preserving the metal geometry in silico does **not** guarantee activity; **(2)** **metal
incorporation is uncertain** — a perfect geometry on paper does not mean Zn actually binds the
expressed protein (you must check by ICP/PAR); and **(3)** **classical MD cannot model the metal site
well** (fixed charges, no charge transfer/polarisation), so MD here is a weak, caveated proxy. Any
example numbers in the notebooks are labelled `EXAMPLE_DATA`/`SYNTHETIC`. **You are graded on rigor,
reasoning, and reproducibility — not on whether the enzyme works.** A meticulous campaign with a low
hit rate and sharp failure analysis is an excellent capstone.

## Responsible research
This is an **industrial / carbon-capture / basic-science** enzyme with **low dual-use** risk:
CO₂ hydration is a green-chemistry/carbon-capture reaction with no toxin/pathogen connection. The
project is framed for building and benchmarking de novo **metal-aware** enzyme-design methodology.
Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended to cause
harm. Real gene-synthesis orders must go through a biosecurity-screening provider (IGSC member);
wet-lab work requires institutional biosafety/ethics approval. If you adapt this template to a
different metal or reaction, re-check the target against `MASTER_BLUEPRINT.md §7` with your advisor
before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (PDB dumps, model weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
This project follows the **enzyme-family template** (Project 18, Kemp eliminase), specialised to a
**metal active site**.
