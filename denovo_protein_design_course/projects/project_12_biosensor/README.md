# Project 12 — De Novo Binder → Biosensor (Binder + Split-Reporter Switch)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed binder + conformational-switch / split-reporter coupling · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
Rapid, cheap diagnostics — at the bedside, in the field, at home — need **analyte-responsive
sensors** that turn the presence of a biomarker directly into a readable signal. Coupling a **de novo
binder** (the recognition element) to a **conformational switch or split-reporter** (the transduction
element) does exactly that: a LOCKR-style cage whose latch is displaced on binding, or a
split-luciferase / split-fluorophore that reconstitutes when the binder engages its analyte, converts
**binding → luminescence/FRET**. This is a real point-of-care platform (Quijano-Rubio 2021), and it is
**diagnostic** in purpose — low dual-use. This project designs such a sensor computationally:
a binder to a chosen biomarker, integrated with a switch, with a planned functional readout.

## What you will do
By the end you will have run an end-to-end de novo **binder** campaign against a chosen biomarker
(the Project-06 two-paradigm workflow), designed or borrowed a **switch** module (an RFdiffusion
scaffold or a LOCKR-style cage with a split-reporter), triaged the binders with the shared multi-layer
in-silico filter (`design_type="binder"`), **integrated** the binder and switch and reasoned about the
**ON/OFF (two-state)** behaviour, and produced a costed **functional-readout** plan (luminescence/FRET
dose-response + LOD estimate) with no-analyte and off-target controls — all reproducibly, degrading
gracefully when only a free T4 is available.

## Learning objectives
1. Compare the two **biosensor architectures** (allosteric/LOCKR-style conformational switches vs split-reporter systems) and choose an **analyte + readout** on purpose.
2. Design a de novo binder to the chosen biomarker epitope (BindCraft / RFdiffusion-binder + ProteinMPNN) and design/borrow a switch (RFdiffusion scaffold / LOCKR cage).
3. Apply the shared 4-layer filter with binder cutoffs, then **integrate** binder + switch and reason about ON/OFF states and the **affinity-vs-dynamic-range trade-off**.
4. Plan a controlled functional readout (luminescence/FRET dose-response, LOD estimate) with **no-analyte** and **off-target** controls; sketch a **multiplexing** concept.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
BindCraft (or FreeBindCraft) and RFdiffusion **binder mode** + ProteinMPNN for the binder module;
RFdiffusion (scaffold/switch generation) or a borrowed **LOCKR**-style cage for the switch module;
AF2-Multimer (ColabFold) for interface confidence (`pae_interaction`) and **two-state** modeling of
the switch; the shared `filtering_pipeline.py` (`design_type="binder"`); Biopython, py3Dmol. The
switch / split-reporter design draws on the LOCKR and de-novo-biosensor literature (Langan 2019,
Quijano-Rubio 2021) and split-luciferase references (NanoBiT, Dixon 2016).

## Data
A **biomarker target structure** — **STUDENT CHOICE** (e.g. a cytokine or a cardiac marker such as a
troponin subunit) — plus split-reporter reference designs. The analyte is yours to pick; pick one with
a verified RCSB structure and a clear point-of-care motivation. Exact accessions, sizes, and licenses
are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded,
and the candidate accession is flagged "candidate — verify."**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + analyte/readout choice + reproduced mock hello-world (binder → switch → ON/OFF) |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Binder design pool (BindCraft + RFdiffusion) + switch module + design log + interim report |
| D3 | P3 (13–18) | Filtered/ranked binders + integrated constructs + switch-architecture benchmark + ON/OFF figures |
| D4 | P4 (19–22) | Validation report + costed luminescence/FRET dose-response + LOD plan with no-analyte/off-target controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** an **integrated binder + switch construct** + a **functional-readout plan** (luminescence/FRET dose-response, LOD estimate) with controls (no-analyte, off-target) + a multiplexing concept `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
Coupling binding to a **clean ON/OFF signal is hard.** In-silico binder hit rates vary **enormously**
by target and tool, and the **majority of in-silico hits fail experimentally**. On top of that, the
sensor adds a second hard problem: **dynamic range vs binder affinity is a real trade-off** (a too-tight
binder can lock the switch ON regardless of analyte; too weak and the ON state never forms), and **most
integrated constructs need iteration** (linker length/rigidity, latch redesign, reporter placement).
A passing binder is a **hypothesis**, and a modeled dynamic range is **not** a measured signal —
`pae_interaction` is not affinity, and there is **no LOD** until a real dose-response is fit. **You are
graded on rigor, reasoning, and reproducibility — not on whether the sensor works.** A meticulous
campaign with a low hit rate and sharp failure analysis is an excellent capstone. Any example numbers
in the notebooks are labeled `EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as real.

## Responsible research
This project designs a **diagnostic / point-of-care biosensor** for a disease biomarker — a defensible,
in-scope diagnostic purpose with **low dual-use** concern. It is framed for diagnostic sensing only.
Out of scope: enhancing pathogen transmissibility/virulence, toxins, immune-evasion tools, or any
design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening
provider (IGSC member); wet-lab work requires institutional biosafety/ethics approval. If your chosen
analyte raises any dual-use concern, discuss a defensible diagnostic framing with your advisor before
proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(Project 06): it reuses the BindCraft/RFdiffusion-binder + AF2-Multimer + shared-filter workflow and
adds the switch / split-reporter module on top.
