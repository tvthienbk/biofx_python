# Project 03 — Data

This project needs **no external data to *generate*** monomers — RFdiffusion designs backbones from
noise. The data dependencies are (a) a few small **natural reference folds** for novelty-scoring
sanity checks, and (b) the **PDB / Foldseek reference database** used to *score* novelty, which is
**large and fetched by the student, never committed.**

## What you need to assemble
| Group | Count | Source | Role |
|-------|-------|--------|------|
| Natural reference folds | ~5 | RCSB (via `download_data.py`) | sanity-check novelty scoring (a natural fold should score TM ≈ 1 against itself / high vs the PDB) |
| Foldseek PDB database | 1 DB | `foldseek databases PDB ...` | novelty scoring of every generated backbone (TM-score to nearest natural fold) |
| (optional) Foldseek AFDB database | 1 DB | `foldseek databases Alphafold/UniProt50 ...` | broader novelty reference — **very large**, optional |

> **Generation needs nothing external; novelty *scoring* needs the database.** Keep these straight:
> you can run the whole campaign and only need the Foldseek DB at the novelty step (notebook 03/04).

## Files in this folder
- `download_data.py` — fetches the *natural reference* structures (RCSB) with SHA-256 + license
  logging. **You edit its `ACCESSIONS` list.** Run: `python data/download_data.py`. It does **not**
  fetch the Foldseek database (that is large and handled separately — see below).
- `provenance.csv` — auto-written by `download_data.py` for the fetched structures.
- `inputs/` — small seed files only (e.g., reference PDBs). **Never commit large data.**

## Candidate natural references (verify on RCSB in Week 1)
Starting points for novelty-scoring sanity checks — **candidate accessions, verify before use; PDB
entries are occasionally superseded:**
- `1UBQ` — ubiquitin (small robust α/β fold)
- `1L2Y` — Trp-cage (tiny all-α fast-folder)
- `2GB1` — protein G B1 domain (classic α/β)
- `1ENH` — engrailed homeodomain (small all-α)
- `1MJC` — cold-shock protein (β-barrel / all-β reference)

These span the α / β / mixed topologies your campaign generates, so they double as references for
"what does a *natural* fold of this topology score?" when you calibrate the novelty axis.

## The Foldseek novelty database (large — download separately, do NOT commit)
The novelty score (TM-score to the nearest natural fold) requires a structure database. **Do not
commit it; fetch it at the point of use:**
```bash
# PDB-only database (recommended for the course): tens of GB on disk after build.
foldseek databases PDB pdb_db tmp
# (optional, MUCH larger) AlphaFold DB / UniProt50: hundreds of GB+ — HPC scratch only.
# foldseek databases Alphafold/UniProt50 afdb tmp
```
**Approximate sizes (verify at download time; these grow):** the Foldseek PDB database is on the
order of tens of GB once built; the AFDB databases are *hundreds of GB to TB* and are HPC-only. Store
any of these on Google Drive or HPC scratch — **never in the git repo**. `results/` and these
databases are git-ignored.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Foldseek databases: derived from PDB (public domain) / AlphaFold DB (CC-BY-4.0, cite Jumper 2021 +
  Varadi 2022). Cite Foldseek (van Kempen 2024) for the search method.
- RFdiffusion / ProteinMPNN / ColabFold / ESMFold weights: check each repo's license; do **not**
  redistribute weights — script their download.
