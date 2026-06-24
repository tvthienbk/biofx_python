# Project 16 — Antibody Humanization Pipeline with Humanness Scoring

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Antibody engineering / humanization · **Compute tier:** Free Colab **T4** (genuinely free-tier-friendly)

## The problem (and why it matters now)
A non-human therapeutic antibody — murine, or a murine/human **chimera** — triggers an **anti-drug-antibody
(ADA)** response: the patient's immune system recognizes the foreign sequence, clears the drug, and can
cause adverse reactions. **Humanization** rewrites the antibody so it resembles a **human germline**
antibody (low ADA risk) while keeping the original **CDRs** that confer binding. It is a **regulatory
necessity** for non-human candidates. The catch is a real, unavoidable **trade-off**: humanizing the
framework usually **costs affinity and stability**, so a sound pipeline must *predict that cost* and plan
the **back-mutations** that rescue it. A reproducible computational **humanization + humanness-scoring**
pipeline that quantifies the stability cost is a clean, high-value capstone.

## What you will do
By the end you will have run an end-to-end **humanization campaign**: graft a non-human antibody's CDRs
onto **candidate human germline frameworks**, score **humanness** (OASis / Hu-mAb / T20 / AbLang),
predict the **ΔΔG stability cost** (FoldX / Rosetta on an IgFold model), identify the **Vernier-zone
back-mutations** needed, compare **CDR grafting vs resurfacing**, and produce a costed **ELISA/SPR/DSF
validation plan** with controls — all reproducibly, with a deterministic mock path that runs anywhere and
a clearly-marked real (T4) path.

## Learning objectives
1. Choose and justify a non-human therapeutic antibody + human germline framework(s), with measurable success criteria (target humanness band + acceptable stability/binding cost).
2. Graft CDRs onto candidate human frameworks and generate variants (grafting, resurfacing, germline-content), with the parental + an over-humanized decoy as controls.
3. Score humanness, predict ΔΔG stability, and identify Vernier-zone back-mutations; quantify the humanness↔stability trade-off with the `design_type="antibody"` filter.
4. Plan an ELISA/SPR (retained binding) + DSF (stability) validation with mandatory controls and an immunogenicity-risk summary.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4 — and a T4 is all this project needs).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch/assemble inputs: edit + run `python data/download_data.py` (records provenance; the antibody sequence + germline DB are mostly student-supplied — verify in Week 1).
5. Work through notebooks `01 → 05` following the timeline (everything runs on the `mock` backend with no GPU).

## Tools
AbLang (antibody language model — humanness + residue restoration), **OASis / Hu-mAb / T20** humanness
scoring (verify current public release), **ProteinMPNN** (framework-position optimization `[extension]`),
**AF2 / IgFold / ImmuneBuilder** (Fv structure for ΔΔG modelling), **FoldX / Rosetta** ΔΔG (stability
proxy), and the shared `shared/filtering_pipeline.py` (`design_type="antibody"`). The humanness + ΔΔG
functions in `scripts/humanization_tools.py` are **teaching heuristics** — swap in the real tools for any
reportable claim.

## Data
A **non-human therapeutic antibody sequence** (the student supplies a published murine/chimeric
therapeutic antibody — mark "verify") + the **human germline framework database** (IMGT / OAS, downloaded
separately, not committed) — exact accessions and licenses are in `data/README.md`. **Verify your antibody
and germline choices in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement (antibody + germline + strategy + success criteria) + reproduced mock humanization hello-world |
| D1 | P1 (3–6)   | Working minimal humanization pipeline + first (mock/real) variant batch + repo |
| D2 | P2 (7–12)  | Full variant pool (`campaign.csv`: grafts, back-mutated, resurfaced + controls) + design log + interim report |
| D3 | P3 (13–18) | Antibody-filtered ranked variants + humanness↔stability trade-off / back-mutation / grafting-vs-resurfacing figures + filtering report |
| D4 | P4 (19–22) | ELISA/SPR/DSF validation plan + immunogenicity-risk summary + controls (parental + over-humanized decoy) + costed plan |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** humanized variants + a humanness/stability **trade-off analysis** + an **immunogenicity-risk summary** + an **ELISA/SPR/DSF validation plan** with controls (parental + an over-humanized decoy) |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
Humanization is a **trade-off, not a free lunch**: grafting often loses affinity/stability and needs
**back-mutations** to recover. The deliverable is **variants + the trade-off analysis + the experiment**,
not "a humanized antibody". A humanness score is a **hypothesis**, not a guaranteed low-ADA outcome; pLDDT
is not stability; a ΔΔG proxy is not a measured Tm. **NEVER fabricate ΔΔG or humanness numbers** — any
synthetic teaching value in the notebooks is labelled `SYNTHETIC` / `EXAMPLE_DATA` and must never be
reported as real. **You are graded on rigor, reasoning, and reproducibility — not on whether the protein
works.** A meticulous campaign that honestly reports the trade-off is an excellent capstone.

## Responsible research
This is a **therapeutic antibody** project: **reducing the immunogenicity (ADA risk)** of a non-human
therapeutic antibody so it is safer and more effective in patients. It is a defensive, **low-dual-use**
aim. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended to cause
harm. Real gene-synthesis orders must go through a biosecurity-screening provider; wet-lab work requires
institutional biosafety/ethics approval. Do not overstate a humanness score as a proven low-ADA outcome —
only a clinical immunogenicity assessment is definitive. See `MASTER_BLUEPRINT.md §7`.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data (the IMGT/OAS germline DB) out of git; pin
`env/requirements.txt`; tag a `v1.0` release with your final report. This project follows the
**antibody-family pattern** set by Project 17 (`design_type="antibody"` filter hand-off, deterministic
mock, controlled validation plan).
