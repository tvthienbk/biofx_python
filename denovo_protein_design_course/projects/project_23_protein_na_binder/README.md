# Project 23 — Protein–Nucleic-Acid Binder (DNA/RNA-Binding Mini-Protein)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Nucleic-acid-targeted binder design (RFdiffusion + **LigandMPNN**) · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
Proteins that bind a *specific* DNA or RNA sequence are the basis of **gene-editing modulators**,
**RNA-targeting therapeutics**, and **synthetic transcription factors** — programmable tools for
turning genes on/off, tuning CRISPR systems, and reading or blocking RNA elements. Designing them de
novo was largely out of reach until **LigandMPNN** added the ability to design protein sequences
**conditioned on nucleic-acid context** (it sees the DNA/RNA atoms; ProteinMPNN does not). That makes
designing a small **NA-binding mini-protein** newly tractable — and this project does exactly that,
then confronts the field's central difficulty head-on: **sequence specificity**. This is a
therapeutic / basic-science project with low dual-use risk; framing is neutralizing/therapeutic.

## What you will do
By the end you will have run an end-to-end de novo campaign for a protein that binds a **chosen DNA/RNA
motif** — scaffolding backbones near the nucleic acid (RFdiffusion), designing sequences around it with
the **NA-aware LigandMPNN** (and a **NA-blind ProteinMPNN** baseline for comparison), modeling the
protein–NA complex, triaging with the shared multi-layer filter (`design_type="binder"`) plus a
**specificity gate**, benchmarking LigandMPNN vs ProteinMPNN at the interface, and producing a costed
**EMSA / fluorescence-anisotropy** validation plan with **scrambled-NA controls** — all reproducibly,
degrading gracefully when only a free T4 is available.

## Learning objectives
1. Choose and justify a **DNA/RNA target motif** and understand how proteins read nucleic acids (base readout vs generic backbone contacts).
2. Run **RFdiffusion** near the nucleic acid and **LigandMPNN** (NA-aware) to design a binding mini-protein, with a **ProteinMPNN** NA-blind baseline.
3. Apply the shared 4-layer filter with binder cutoffs **plus a specificity gate** (intended motif vs scrambled), and report an honest hit rate — separating *confidence* from *specificity*.
4. Benchmark LigandMPNN vs ProteinMPNN at the interface and design a controlled **EMSA / fluorescence-anisotropy** validation plan with a **scrambled-NA** control.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
**RFdiffusion** to scaffold a protein backbone near the nucleic acid; **LigandMPNN** (nucleic-acid-aware)
to design sequences around the NA — the central tool; **ProteinMPNN** as the NA-blind baseline for the
benchmark; **Boltz-2** (or an AF3-style server / AF2) for protein–NA complex modeling
(`pae_interaction`); the shared `filtering_pipeline.py` (`design_type="binder"`); Biopython, py3Dmol.
LigandMPNN/ProteinMPNN are CPU-cheap; RFdiffusion-near-NA and complex modeling are the heavy steps.

## Data
A protein–DNA/RNA complex as a starting template (a **candidate accession — verify on RCSB**; protein–
DNA *and* protein–RNA complexes exist — pick one matching your goal) plus a **DNA/RNA target motif that
you choose**. Exact accessions, sizes, and licenses are in `data/README.md`. **Verify every accession on
RCSB in Week 1; entries get superseded.** The course does **not** assert a specific complex as required —
you pick and justify both the complex and the motif.

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + chosen DNA/RNA motif + reproduced mock mini-run |
| D1 | P1 (3–6)   | Working minimal NA-binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Scaffold-near-NA + LigandMPNN design pool (+ ProteinMPNN baseline) + design log + interim report |
| D3 | P3 (13–18) | Ranked confident+specific candidates + LigandMPNN-vs-ProteinMPNN benchmark + specificity figures + filtering report |
| D4 | P4 (19–22) | Validation report + costed **EMSA / fluorescence-anisotropy** plan with **scrambled-NA** controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** an NA-binding mini-protein design + a **sequence-specificity analysis** (vs a scrambled motif) + an **EMSA / fluorescence-anisotropy** binding plan with **scrambled-NA controls** |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
**Protein–NA design is newer and harder than protein–protein binder design.** A protein can grip the
generic, negatively-charged phosphate backbone of *any* DNA/RNA without reading your intended
bases — so **sequence specificity is the main failure mode**, and many in-silico hits will bind
non-specifically or not at all. A passing design is a **hypothesis**: a low `pae_interaction` is
*confidence*, not affinity; a positive computational specificity score is a *proxy*, not a measured
ΔΔG; **EMSA / fluorescence-anisotropy with a scrambled-NA control is mandatory**. There is **no
fabricated K_D** anywhere in this project. **You are graded on rigor, reasoning, and reproducibility —
not on whether the binder works.** A meticulous campaign that honestly reports a low specificity rate
with sharp failure forensics is an excellent capstone. Any example numbers in the notebooks are labeled
`EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as real.

## Responsible research
This project designs **nucleic-acid-binding proteins** for **gene-editing modulation, RNA-targeting
therapeutics, and synthetic transcription factors** — defensible therapeutic / basic-science purposes
with **low dual-use risk**; the default framing is neutralizing/therapeutic (e.g., an anti-CRISPR-like
modulator that makes editing *safer/more controllable*, an RNA element you *block*). Out of scope:
enhancing pathogen transmissibility/virulence, toxins, evasion of biosecurity screening, or any design
intended to cause harm — including using a CRISPR modulator to defeat safety safeguards. Real
gene-synthesis orders (protein genes and NA oligos) must go through a biosecurity-screening provider
(IGSC member); wet-lab work requires institutional biosafety/ethics approval. If your chosen target
raises dual-use concern, discuss a defensible neutralizing/therapeutic framing with your advisor before
proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(`projects/project_06_pdl1_binder/`): the key difference is the target is a **nucleic acid** and the
central sequence designer is **LigandMPNN** (NA-aware), with a **specificity gate** on top of the shared
filter.
