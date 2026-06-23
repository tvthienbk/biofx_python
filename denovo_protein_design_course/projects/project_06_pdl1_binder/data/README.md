# Project 06 — Data

This project's data is a **target definition**: the structure(s) of the PD-1/PD-L1 complex, used to
(a) extract a clean PD-L1 ectodomain to design against and (b) read off the **PD-1-binding hotspot
residues** on PD-L1 (the competitive epitope). Provenance is graded — every input must carry its
source, and every accession is a **candidate to verify on RCSB in Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| PD-1/PD-L1 complex structures | 1–2 | RCSB PDB | define the competitive epitope + hotspots; clean PD-L1 to design against |
| (derived) cleaned PD-L1 ectodomain | 1 | you produce it from the complex | the target PDB for BindCraft/RFdiffusion |
| (optional) known PD-L1 binder | 1 | RCSB / literature | positive control reference for the validation plan |

> **Why the hotspots are the hard part:** generation is easy; steering the binder onto the
> *competitive* (PD-1) face so it can actually **block** is the design decision that matters. Derive
> the hotspots from the PD-1/PD-L1 interface in the complex, not from a generic surface patch.

## Files in this folder
- `download_data.py` — fetches the candidate complex structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned PD-L1 PDB, hotspot list, BindCraft/RFdiffusion
  config). **Never commit large data** (raw PDB dumps, model weights, AF2 outputs) — fetch them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** These define the PD-1/PD-L1
competitive interface; the PD-L1 ectodomain hotspots are read off the PD-1 footprint in the complex:
- `4ZQK` — **candidate** human PD-1/PD-L1 complex (defines the PD-1-binding face of PD-L1). Verify
  chains (which chain is PD-L1), resolution, and that it is the human complex.
- `5O45` — **candidate** PD-1/PD-L1 complex (cross-check the epitope/hotspots against 4ZQK). Verify.

> Identify the PD-L1 chain, isolate its **IgV (membrane-distal) domain**, remove PD-1, waters, and
> heteroatoms, and list the PD-L1 residues within contact distance of PD-1 as your **hotspots**.

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated design pools,
AF2-Multimer outputs, and any model weights are large and **git-ignored** (write them to `results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original PD-1/PD-L1 structure paper).
- AlphaFold DB (if you pull a predicted model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the CD274/PD-L1 sequence): CC-BY-4.0.
- Any binder reference from a paper's supplementary data inherits that paper's terms — log the DOI.

## Responsible-research note
PD-L1 is a human checkpoint protein; this project designs **blocking** binders for **cancer
immunotherapy / diagnostics** (in scope). Do not redistribute restricted data; link + script the
download. See `MASTER_BLUEPRINT.md §7` and the Responsible Research sections of `README.md` / `MANUAL.md`.
