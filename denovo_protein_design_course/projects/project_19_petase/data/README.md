# Project 19 — Data

This project designs an enzyme from scratch (or grafts a known triad), so most of its "data" is
something you **construct**, not download: the **theozyme** (the Ser-His-Asp triad + oxyanion hole +
ester transition-state geometry) and the **PET-mimic ester substrate** definition. The only fetched
files are a couple of **reference PET hydrolases / cutinases** used as structural references,
positive controls, and **thermostability comparators**. Provenance is graded — record the source of
every item.

## What you assemble vs. what you fetch
| Item | How | Source | Status |
|------|-----|--------|--------|
| Theozyme (Ser-His-Asp triad + oxyanion hole + ester-TS geometry) | **You build it** | Literature + QM TS model | `data/inputs/theozyme_def.txt` (TEMPLATE to fill) |
| PET-mimic ester substrate + tetrahedral-intermediate TS | **You build it** | Serine-hydrolase mechanism; QM | encoded in the theozyme; NOT fabricated data |
| Reference PET hydrolases / cutinases | `download_data.py` | RCSB | **candidates — verify on RCSB** |
| Designed/engineered-enzyme sequences w/ reported kinetics & Tm | **You curate** | Paper supplementary tables | log DOI/table/license each |

> **The theozyme is a teaching template, not data.** The placeholder distances/angles in
> `data/inputs/theozyme_def.txt` are clearly labelled `<...>`/PLACEHOLDER. You replace them with
> real values from the literature and/or a QM transition-state calculation, and you cite where each
> number came from. Nothing here is a measured experimental result, and no kcat or Tm is fabricated.

## Files in this folder
- `download_data.py` — fetches the candidate reference structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py` (or
  `--dry-run`). It writes `provenance.csv`.
- `inputs/theozyme_def.txt` — the theozyme TEMPLATE you fill in (triad + oxyanion-hole + ester TS).
- `provenance.csv` — auto-written by `download_data.py` for fetched structures.

## Candidate reference accessions (VERIFY on RCSB in Week 1 — do not trust blindly)
These are **candidate** IDs flagged "look up + verify"; PET-hydrolase / cutinase structures are
numerous (wild-type, mutants, complexes) and entries get superseded. Confirm the exact entry/chain/
variant on RCSB before use; if you cannot confirm one, comment it out and rely on the constructed
theozyme only.
- `6EQE` — **candidate — verify on RCSB:** an *Ideonella sakaiensis* **IsPETase** entry — the
  canonical PET hydrolase, and the thermostability comparator (wild-type IsPETase is fragile near
  PET's glass transition). Confirm the exact ID/variant; many IsPETase entries exist.
- `5XJH` — **candidate — verify on RCSB:** a **cutinase / PET-active hydrolase** entry — a
  serine-hydrolase fold with the Ser-His-Asp triad + oxyanion hole, useful as the **engineered-natural**
  scaffold track and a triad-geometry reference.
- Also worth looking up + verifying: an **engineered thermostable** variant (e.g. the LCC ICCG /
  DuraPETase lineage) as a *designed-then-stabilised* comparator for your thermostability ranking;
  and a thermophilic cutinase. Treat every ID as a candidate.

## Where to find labeled designed/engineered-enzyme data (for controls/benchmarks)
Look in the supplementary materials of the foundational PET-hydrolase and de novo enzyme papers
(Austin 2018 IsPETase; Tournier 2020 engineered LCC, *Nature*; Lauko 2025 de novo serine hydrolases,
*Science*; Schnettler 2025 Riff-Diff; Dauparas 2024 LigandMPNN). Many report catalytic residues,
kcat/KM, **Tm**, and sequences. **Record the DOI, the exact table/figure, and the license/terms** for
each item. Use reported kinetics/Tm only as *context/positive controls* — never copy a reported kcat
or Tm into your own results as if you measured it.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Paper supplementary data: inherits that paper's terms — check and log each one (DOI + table).
- Any QM/literature geometry you encode: cite the source paper(s).

## Compute / size note
No large data here — a few small PDBs. Never commit fetched structures, model weights, or MD
trajectories (thermostability MD trajectories can be large); `results/` and large files stay out of
git (see `MASTER_BLUEPRINT.md §6`).
