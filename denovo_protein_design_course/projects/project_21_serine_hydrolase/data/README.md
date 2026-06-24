# Project 21 — Data

This project designs an enzyme from scratch, so most of its "data" is something you **construct**,
not download: the **theozyme** (the Ser-His-Asp triad + oxyanion hole + ester transition-state
geometry) and the **chromogenic-ester substrate** definition. The only fetched files are a couple of
**reference serine hydrolases** used as structural references, triad-geometry sanity checks, and
positive controls. Provenance is graded — record the source of every item.

## What you assemble vs. what you fetch
| Item | How | Source | Status |
|------|-----|--------|--------|
| Theozyme (Ser-His-Asp triad + oxyanion hole + ester-TS geometry) | **You build it** | Literature + QM TS model | `data/inputs/theozyme_def.txt` (TEMPLATE to fill) |
| Chromogenic-ester substrate + tetrahedral-intermediate TS | **You build it** | Serine-hydrolase mechanism; QM | encoded in the theozyme; NOT fabricated data |
| Acyl-chain series (pNP C2/C4/C6/C8) for substrate scope | **You define it** | pNP-ester chemistry | `substrate_scope_scan` in `scripts/enzyme_tools.py` |
| Reference serine hydrolases (cutinase / lipase) | `download_data.py` | RCSB | **candidates — verify on RCSB** |
| Designed/natural-enzyme sequences w/ reported kinetics | **You curate** | Paper supplementary tables | log DOI/table/license each |

> **The theozyme is a teaching template, not data.** The placeholder distances/angles in
> `data/inputs/theozyme_def.txt` are clearly labelled `<...>`/PLACEHOLDER. You replace them with
> real values from the literature and/or a QM transition-state calculation, and you cite where each
> number came from. Nothing here is a measured experimental result, and no kcat/KM/ee is fabricated.

## Files in this folder
- `download_data.py` — fetches the candidate reference structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py` (or
  `--dry-run`). It writes `provenance.csv`.
- `inputs/theozyme_def.txt` — the theozyme TEMPLATE you fill in (triad + oxyanion-hole + ester TS).
- `provenance.csv` — auto-written by `download_data.py` for fetched structures.

## Candidate reference accessions (VERIFY on RCSB in Week 1 — do not trust blindly)
These are **candidate** IDs flagged "look up + verify"; serine-hydrolase structures are numerous
(wild-type, mutants, complexes, and the new de novo designs) and entries get superseded. Confirm the
exact entry/chain/variant on RCSB before use; if you cannot confirm one, comment it out and rely on
the constructed theozyme only.
- `1CEX` — **candidate — verify on RCSB:** a *Fusarium solani* **cutinase** entry — a compact
  alpha/beta-hydrolase with the classic Ser-His-Asp triad + oxyanion hole; a clean triad-geometry
  reference for a small esterase. Confirm the exact ID/chain.
- `3TGL` — **candidate — verify on RCSB:** a *Rhizomucor miehei* **lipase** entry — a well-studied
  serine-hydrolase triad with a lid and a larger acyl pocket; a useful *longer-acyl* substrate-scope
  reference. Confirm the exact ID/variant; many lipase entries exist.
- Also worth looking up + verifying: a **Lauko 2025 (Science) de novo serine-hydrolase** design entry
  (the frontier result this project reproduces) **if** a coordinate file has been deposited/released —
  look it up on RCSB; do not assume an ID. A thermophilic esterase is another candidate comparator.
  Treat every ID as a candidate.

## Where to find labeled designed/natural-enzyme data (for controls/benchmarks)
Look in the supplementary materials of the foundational papers (Lauko 2025 de novo serine hydrolases,
*Science*; Schnettler 2025 Riff-Diff, *Nature*; Dauparas 2024 LigandMPNN; plus a classic
alpha/beta-hydrolase mechanism reference). Many report catalytic residues, kcat/KM, and sequences.
**Record the DOI, the exact table/figure, and the license/terms** for each item. Use reported
kinetics only as *context/positive controls* — never copy a reported kcat/KM into your own results
as if you measured it.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Paper supplementary data: inherits that paper's terms — check and log each one (DOI + table).
- Any QM/literature geometry you encode: cite the source paper(s).

## Compute / size note
No large data here — a few small PDBs. Never commit fetched structures, model weights, or MD
trajectories; `results/` and large files stay out of git (see `MASTER_BLUEPRINT.md §6`).
