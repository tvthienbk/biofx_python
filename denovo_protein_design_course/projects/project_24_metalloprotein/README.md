# Project 24 — Metalloprotein / Cofactor-Binding De Novo Protein (Heme / FeS / Zn)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** De novo **metalloprotein** design (cofactor-site spec → scaffold pocket → cofactor-aware sequence → coordination geometry) · **Compute tier:** A100 recommended for the scaffolding pool; free-tier demo possible

## The problem (and why it matters now)
De novo **metalloproteins and cofactor-binders** are the basis of **artificial electron-transfer
proteins, synthetic O₂ carriers, and artificial metalloenzymes** — a long-standing grand challenge,
because building a clean coordination pocket for a redox/O₂ cofactor (a **heme**, a **[4Fe-4S]**
cluster, or a **Zn**) from scratch is hard. The field went from hand-built four-helix-bundle
**"maquettes"** (DeGrado) to **ML-designed** cofactor-binders (Baker lab), and the arrival of a
**cofactor-aware sequence designer — LigandMPNN** — that can "see" a bound heme/metal makes this now
tractable as a capstone. It is **basic-science / industrial** in flavour (electron transfer, carbon-
neutral catalysis, O₂ transport), with **low dual-use** risk.

## What you will do
By the end you will have run an end-to-end de novo **cofactor-binding-protein** campaign — **construct
a cofactor-site spec** (the default is a **bis-His heme** electron-transfer site: heme b held by two
axial histidines), **scaffold** it into many backbones that present the coordination motif,
**sequence-design with cofactor-aware LigandMPNN while fixing the coordinating residues and passing
the cofactor as context**, triage with a multi-layer filter centred on **coordination-geometry RMSD**
(plus cofactor docking, site pLDDT, and solubility), reason about **redox tuning**, and produce a
costed **spectroscopic assay plan** (UV-vis Soret for heme / EPR for Fe-S; a cofactor titration with
apo + ligand→Ala controls) — all reproducibly, with a no-GPU mock path so the plumbing runs anywhere.

## Learning objectives
1. Choose a **cofactor** (heme, [4Fe-4S], or Zn) and a **coordination scheme** (e.g. bis-His heme) and encode it as a cofactor-site spec around the bound cofactor.
2. Scaffold the coordination motif (RFdiffusion2 / Riff-Diff / RFdiffusion) and sequence-design with **cofactor-aware LigandMPNN preserving the coordinating residues** (vanilla ProteinMPNN is cofactor-blind).
3. Validate **coordination geometry** (coordination-RMSD < 0.5 Å; clean metal-ligand distances + ligand-metal-ligand angles), plus cofactor docking, site pLDDT, solubility, and a (caveated) short MD; reason about **redox tuning** `[extension]`.
4. Plan a **spectroscopic assay** with the right controls (UV-vis Soret band for heme **or** EPR for Fe-S; a metal/cofactor **titration**; controls: **apo protein**, a **coordinating-residue→Ala** mutant).

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs on the **mock**
   backend with no GPU; switch to the real backends on Colab/HPC where noted.

## Tools
Cofactor-site spec construction (default: a **bis-His heme** electron-transfer site; alternatives:
His/Met heme, proximal-His O₂-binding heme, [4Fe-4S]-4Cys ferredoxin, Cys2His2 structural Zn),
**RFdiffusion2 / Riff-Diff / RFdiffusion** motif scaffolding, **cofactor-aware LigandMPNN** (the
**central** tool — fixes the coordinating residues, passes the cofactor as atom context),
**AF2** (site pLDDT + coordinating-residue geometry; note AF2 does **not** place the cofactor),
**AutoDock Vina** (cofactor fit — heme macrocycle / cluster), **OpenMM** (short pocket MD —
**classical-metal-FF caveat**), `shared/filtering_pipeline.py` with `design_type="enzyme"`
(here `cat_geom` = **coordination**-geometry RMSD, `plddt_cat` = **site** confidence).

## Data
Mostly **constructed, not downloaded**: you build the **cofactor-site spec** and the coordination
geometry from a **verified** reference structure / literature (`data/inputs/cofactor_site_def.txt` is
a template to fill — *not* fabricated data; **there are no spectra in this project**). `download_data.py`
fetches a few **candidate reference cofactor proteins** — **1MBN** (myoglobin), a **b-type cytochrome**
(bis-His heme), and a **ferredoxin** (Fe-S) — to read off the target geometry and as positive controls.
Exact accessions and licenses are in `data/README.md`. **Verify every accession on RCSB in Week 1;
cofactor proteins have many deposited variants and entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + reproduced tutorial output (mock cofactor-site hello-world) |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design pool (scaffolds + cofactor-aware LigandMPNN sequences, coordinating residues fixed) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + coordination-geometry & cofactor/scheme-comparison figures + filtering report |
| D4 | P4 (19–22) | Validation report (geometry + docking + site pLDDT + caveated MD) + costed spectroscopic assay plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a **cofactor-pocket design** (e.g. bis-His heme) + a **coordination-geometry-filtered <96-design set** + a **spectroscopic assay plan** (UV-vis **Soret band** for heme **or** **EPR** for Fe-S; a metal/cofactor **titration**) with controls (**apo protein**, a **coordinating-residue→Ala** mutant) + **redox-tuning** reasoning `[extension]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo **cofactor-binding / metalloprotein** design is **hard** and hit rates are **low**. Three
honest caveats stack here: **coordination geometry ≠ cofactor incorporation ≠ function** — a perfect
bis-His geometry on paper does **not** mean heme actually loads into the expressed protein, and loading
does **not** mean the designed redox/O₂ behaviour; **AF2 does not place the cofactor** (it predicts the
apo backbone, so you dock/model the cofactor separately); and **classical MD models the metal site
poorly**, so MD here is a weak, caveated proxy. Only **spectroscopy** (UV-vis Soret / EPR + a cofactor
titration) confirms incorporation and coordination. Any example numbers in the notebooks are labelled
`EXAMPLE_DATA`/`SYNTHETIC`; **no spectra are fabricated.** **You are graded on rigor, reasoning, and
reproducibility — not on whether the protein works.** A meticulous campaign with a low hit rate and
sharp failure analysis is an excellent capstone.

## Responsible research
This is a **basic-science / industrial** metalloprotein with **low dual-use** risk: artificial
electron-transfer proteins, synthetic O₂ carriers, and artificial metalloenzymes have no toxin/pathogen
connection, and the project is framed for building and benchmarking de novo **cofactor-aware**
metalloprotein-design methodology. Out of scope: enhancing pathogen transmissibility/virulence,
toxins, or any design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-
screening provider (IGSC member); wet-lab work requires institutional biosafety/ethics approval. If you
adapt this template to a different cofactor or function, re-check the target against
`MASTER_BLUEPRINT.md §7` with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (PDB dumps, model weights, MD
trajectories) out of git; pin `env/requirements.txt`; tag a `v1.0` release with your final report.
This project follows the **enzyme-family template** (Project 18, Kemp eliminase), specialised to a
**cofactor-coordination site** validated by spectroscopy.
