# Project 02 — Data

This project's data is **backbones to redesign**: de novo monomer backbones (the real subjects of
the MPNN sweep) plus a handful of natural monomers as folding/recovery baselines. Provenance is
graded — every backbone must carry its source.

## What you need to assemble
| Group | Count | Source | Role |
|-------|-------|--------|------|
| De novo monomer backbones | 20–30 | **Project 03 outputs** or a public de novo design set | the subjects of the sweep |
| Natural reference monomers | 5–10 | RCSB / UniProt | recovery + recapitulation baselines (do MPNN sequences recover natives? do they recapitulate?) |
| (optional) A known-bad/aggregation-prone design | a few | papers reporting failures | negative control for the solubility proxies |

> **Why the de novo backbones are the hard part:** they do **not** come from a single-accession
> fetch. Assemble them from Project 03's generated/filtered backbones (preferred — keeps the cohort
> pipeline connected) or a published de novo design set, and record exactly where each one came from
> (project run ID, or paper DOI + supplementary file). A smaller, cleanly-sourced backbone set beats
> a large set of unknown provenance.

## Files in this folder
- `download_data.py` — fetches the **natural reference** structures (RCSB) with SHA-256 + license
  logging. **You edit its `ACCESSIONS` list.** Run: `python data/download_data.py`. It does **not**
  fetch the de novo backbones — those you assemble and drop into `data/inputs/`.
- `inputs/` — small seed files only (a few example backbone PDBs / configs). **Never commit the full
  backbone set or large data** — keep `results/` and bulk data out of git.
- `provenance.csv` — auto-written by `download_data.py` for the fetched natural references.

## Candidate natural references (verify on RCSB in Week 1)
Starting points for the recovery/recapitulation baselines — **candidate accessions, verify before
use; PDB entries are occasionally superseded:**
- `1UBQ` — ubiquitin (small, robust α/β fold)
- `1L2Y` — Trp-cage (tiny fast-folder)
- `1ENH` — engrailed homeodomain (small all-α)
- `2GB1` — protein G B1 domain (classic α/β)
- `1MJC` — cold-shock protein (β-barrel)
- plus a few more spanning the fold classes your de novo backbones cover.

## Where to find de novo backbones
- **Project 03** (RFdiffusion monomer design) — the intended cohort source; use its filtered
  novel-but-foldable backbones and cite the run.
- **Public design sets** — supplementary structures from foundational de novo design papers
  (RFdiffusion, ProteinMPNN benchmarking). Record the DOI, the exact supplementary file, and the
  license for every backbone you pull. Exclude anything whose primary function is harmful
  (see `MASTER_BLUEPRINT.md §7`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Project 03 outputs: cite the run + the generating tool (RFdiffusion) license.
- Paper supplementary structures: inherit that paper's terms — check and log each one.
- ProteinMPNN / LigandMPNN weights and code: check the upstream repo license (MIT-style for
  ProteinMPNN at time of writing — verify) and cite Dauparas 2022 / 2024.
