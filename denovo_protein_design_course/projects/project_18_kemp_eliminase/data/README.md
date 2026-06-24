# Project 18 — Data

This project designs an enzyme from scratch, so most of its "data" is something you **construct**,
not download: the **theozyme** (catalytic functional groups + transition-state geometry) and the
**substrate** definition. The only fetched files are a couple of **reference designed Kemp
eliminases** used as positive controls and geometry sanity checks. Provenance is graded — record
the source of every item.

## What you assemble vs. what you fetch
| Item | How | Source | Status |
|------|-----|--------|--------|
| Theozyme (base + π-stack + H-bond donor + TS geometry) | **You build it** | Literature + QM TS model | `data/inputs/theozyme_def.txt` (TEMPLATE to fill) |
| 5-nitrobenzisoxazole substrate + TS | **You build it** | Röthlisberger 2008; QM | encoded in the theozyme; NOT fabricated data |
| Reference designed Kemp eliminases | `download_data.py` | RCSB | **candidates — verify on RCSB** |
| Designed-enzyme sequences w/ reported kinetics | **You curate** | Paper supplementary tables | log DOI/table/license each |

> **The theozyme is a teaching template, not data.** The placeholder distances/angles in
> `data/inputs/theozyme_def.txt` are clearly labelled `<...>`/PLACEHOLDER. You replace them with
> real values from the literature and/or a QM transition-state calculation, and you cite where each
> number came from. Nothing here is a measured experimental result.

## Files in this folder
- `download_data.py` — fetches the candidate reference structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py` (or
  `--dry-run`). It writes `provenance.csv`.
- `inputs/theozyme_def.txt` — the theozyme TEMPLATE you fill in (functional groups + TS geometry).
- `provenance.csv` — auto-written by `download_data.py` for fetched structures.

## Candidate reference accessions (VERIFY on RCSB in Week 1 — do not trust blindly)
These are **candidate** IDs flagged "look up + verify"; the designed-Kemp-eliminase lineage has
many variants and entries get superseded. Confirm the exact entry/chain/variant on RCSB before use;
if you cannot confirm one, comment it out and rely on the constructed theozyme only.
- `3IIP` — **candidate — verify on RCSB:** a Röthlisberger-2008 Kemp-eliminase (KE07 lineage) entry.
- `5D38` — **candidate — verify on RCSB:** an HG3/HG3.17 evolved Kemp-eliminase (directed-evolution
  endpoint) entry — useful to compare a *designed-then-evolved* active site to your *de novo* one.
- Also worth looking up + verifying: KE70 and other KE-series / HG-series entries, and the
  retro-aldolase RA95 series as a second de-novo-enzyme reference. Treat every ID as a candidate.

## Where to find labeled designed-enzyme data (for controls/benchmarks)
Look in the supplementary materials of the foundational de novo enzyme papers (Röthlisberger 2008;
the HG3/HG3.17 directed-evolution work; Schnettler 2025 Riff-Diff; Dauparas 2025 RFdiffusion2).
Many report catalytic residues, kcat/KM, and sequences. **Record the DOI, the exact table/figure,
and the license/terms** for each item. Use designed-enzyme kinetics only as *context/positive
controls* — never copy a reported kcat into your own results as if you measured it.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Paper supplementary data: inherits that paper's terms — check and log each one (DOI + table).
- Any QM/literature geometry you encode: cite the source paper(s).

## Compute / size note
No large data here — a few small PDBs. Never commit fetched structures, model weights, or MD
trajectories; `results/` and large files stay out of git (see `MASTER_BLUEPRINT.md §6`).
