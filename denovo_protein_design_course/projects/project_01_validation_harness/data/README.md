# Project 01 — Data

This project's data is a **labeled benchmark**: protein sequences whose *experimental outcome is
known*, used to calibrate confidence metrics. Provenance is graded — every item must carry its
source.

## What you need to assemble
| Group | Count | Source | Label |
|-------|-------|--------|-------|
| De novo designs with known outcomes | ≥ 40 | Supplementary data of published de novo design papers | folded? / expressed? / bound? (as reported) |
| Natural positive references | ≥ 10 | RCSB / UniProt | known-good fold (positive control) |
| (optional) Known *failed* designs | a few | Papers that report negatives | negative control |

> **Why labels are the hard part:** prediction is easy; trustworthy labels are not. Use only items
> where the paper states a clear experimental result, and record exactly which table/figure it came
> from. A smaller, cleaner labeled set beats a large, dubious one.

## Files in this folder
- `download_data.py` — fetches the *natural reference* structures/sequences (RCSB/UniProt) with
  SHA-256 + license logging. **You edit its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `dataset.csv` — *you create this* during P2. One row per labeled item. Suggested columns:
  `id, sequence, design_type, source_doi, source_table, license, outcome, outcome_detail, notes`.
- `provenance.csv` — auto-written by `download_data.py` for the fetched structures.

## Candidate natural references (verify on RCSB in Week 1)
These are starting points for positive controls — **candidate accessions, verify before use; PDB
entries are occasionally superseded:**
- `1UBQ` — ubiquitin (small, robust α/β fold)
- `1L2Y` — Trp-cage (tiny fast-folder)
- `1ENH` — engrailed homeodomain (small all-α)
- `2GB1` — protein G B1 domain (classic α/β)
- `1MJC` — cold-shock protein (β-barrel)
- plus 5+ more spanning fold classes you expect downstream projects to design.

## Where to find labeled de novo designs
Look in the supplementary materials of foundational de novo design papers (e.g., RFdiffusion,
ProteinMPNN, Baker-lab binder/minibinder papers, BindCraft). Many report which designs expressed,
folded, or bound, with sequences in supplementary tables. **Record the DOI, the exact table, and
the license/terms** for each item you pull. Exclude anything whose primary function is harmful
(see `MASTER_BLUEPRINT.md §7`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Paper supplementary data: inherits that paper's terms — check and log each one.
