# Project 09 — Macrocycle / Peptide Binder vs MDM2–p53

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Peptide / macrocycle binder design · **Compute tier:** Colab **T4–Pro** (peptides are small; Boltz-2 affinity on small inputs runs on a free T4; a full macrocycle campaign prefers Pro)

## The problem (and why it matters now)
Macrocyclic and constrained peptides sit in the "beyond-rule-of-5" sweet spot **between small
molecules and biologics** — large enough to cover a protein–protein interface, yet potentially **oral
or cell-penetrant** in a way antibodies never are. The **MDM2–p53** interaction is the canonical
proving ground: in many tumors MDM2 over-engages and silences the p53 tumor suppressor, so a peptide
that **mimics the p53 helix** (its Phe19/Trp23/Leu26 anchors), occupies the MDM2 cleft, and
**displaces p53** could restore p53 signalling. MDM2–p53 has decades of known peptide/stapled-peptide
chemistry, which makes it the right target to learn de novo peptide *and* macrocycle design on. **This
is a human-oncology PPI-restoration project; framing is therapeutic only.**

## What you will do
By the end you will have run an end-to-end de novo **peptide and macrocycle** campaign against the
MDM2 p53-binding cleft, triaged it with the shared multi-layer in-silico filter
(`design_type="binder"`), compared **linear vs cyclic** and **peptide vs mini-protein** modalities
head-to-head, used Boltz-2 only for **relative ranking** (never a fabricated K_D), and produced a
**synthesis/validation plan appropriate to peptides** (SPPS, protease-stability, permeability) with
proper controls — all reproducibly, running end-to-end on a deterministic `mock` backend with no GPU.

## Learning objectives
1. Prepare the MDM2 target and define the **p53-binding cleft** (the Phe19/Trp23/Leu26 sub-pockets) as the design site.
2. Design **linear and macrocyclic** peptide binders (BoltzGen peptide/macrocycle protocols, EvoBind2) and a mini-protein **foil** for the modality comparison.
3. Apply the shared 4-layer filter (`pae_interaction` is the key interface metric) and report an honest hit rate; use Boltz-2 affinity for **ranking only**.
4. Compare **linear-vs-cyclic** and **peptide-vs-protein** modalities, and write a **peptide-specific** synthesis/validation plan (SPPS + protease stability + permeability), not just an E. coli plan.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; peptides are small, so a free T4 is often enough — a macrocycle campaign prefers Pro).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab.

## Tools
**BoltzGen** (peptide-anything / macrocycle-anything protocols — *verify the current public release*)
and **EvoBind2** (MSA-free cyclic/linear peptide binder design) for generation; **AF2 / Boltz-2**
(ColabFold) for interface confidence (`pae_interaction`) and **Boltz-2 affinity** for *relative*
ranking; **RFpeptides** concepts for cyclic-peptide design; the shared `filtering_pipeline.py`
(`design_type="binder"`); Biopython, py3Dmol. The **mini-protein foil** for the modality comparison
reuses the Project-06 binder workflow (BindCraft / RFdiffusion-binder + ProteinMPNN, A100).

## Data
The **MDM2–p53 peptide complex** to define the p53-binding cleft and the cleft residues — candidate
accession **1YCR** (**candidate — verify on RCSB**). The peptide targets the MDM2 N-terminal domain's
hydrophobic cleft. **IL-17A** is a documented alternative target. Exact accessions, sizes, and licenses
are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + MDM2 cleft prep + reproduced peptide-design mini-run (mock) |
| D1 | P1 (3–6)   | Working minimal peptide pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Linear + macrocyclic peptide pools + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + linear-vs-cyclic + peptide-vs-protein figures + filtering report |
| D4 | P4 (19–22) | Validation report + costed SPPS / protease-stability / permeability plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** peptide/macrocycle design report + **linear-vs-cyclic and peptide-vs-protein modality comparison** + top candidates with an **SPPS + protease-stability + permeability** validation plan (positive known-p53-peptide control, scrambled-sequence negative, unrelated negative) |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo **peptide and macrocycle** hit rates are **modest and chemistry-dependent**, and predicted
affinity for short peptides is **unreliable** — **rank, don't trust absolute numbers**. A peptide that
passes every filter is a **hypothesis**, not a drug: low `pae_interaction` does **not** mean it binds,
the Boltz-2 affinity score is a **relative rank scaffold and not a K_D**, and a linear peptide that
binds in silico may be **degraded by proteases or unable to enter cells**. Cyclization, D-amino acids,
N-methylation, and stapling are what buy stability/permeability — and they add synthesis complexity.
**You are graded on rigor, reasoning, and reproducibility — not on whether the peptide works.** Any
example numbers in the notebooks are labeled `EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as
real, and **no K_D is ever fabricated.**

## Responsible research
This project designs **competitive p53-mimetic** peptides/macrocycles to a human oncology PPI target
(MDM2) for the **therapeutic purpose of restoring p53 tumor-suppressor function** — a defensible,
in-scope therapeutic purpose. It is framed for oncology only. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause harm. Real
peptide synthesis / gene-synthesis orders must go through a biosecurity-screening provider (IGSC
member); wet-lab work requires institutional biosafety/ethics approval. If your chosen target raises
dual-use concern, discuss a defensible therapeutic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(Project 06): the BoltzGen/EvoBind2 + AF2/Boltz-2 + shared-filter (`design_type="binder"`) pattern
mirrors the mini-binder workflow, with peptide/macrocycle chemistry and SPPS validation swapped in.
