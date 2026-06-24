# Project 20 — Data

This project designs a **metalloenzyme** from scratch, so most of its "data" is something you
**construct**, not download: the **metal-site theozyme** (the Zn-His3-OH catalytic centre + geometry)
and the **substrate/readout** definition. The only fetched files are a couple of **reference carbonic
anhydrase II structures** — used to read off the real Zn-His3 geometry and as a natural-CA positive
control. Provenance is graded — record the source of every item.

## What you assemble vs. what you fetch
| Item | How | Source | Status |
|------|-----|--------|--------|
| Metal site (Zn + His3 ligands + Zn-hydroxide + geometry) | **You build it** | A verified CA structure + literature/QM | `data/inputs/metal_site_def.txt` (TEMPLATE to fill) |
| CO2 substrate + Zn-OH TS; pNPA esterase proxy | **You build it** | CA mechanism literature; QM | encoded in the theozyme; NOT fabricated data |
| Reference carbonic anhydrase II structures | `download_data.py` | RCSB | **candidates — verify on RCSB** |
| GRACE de-novo-CA designs + reported activity | **You curate** | Hu 2024 supplementary | log DOI/table/license each |

> **The metal site is a teaching template, not data.** The placeholder distances/angles in
> `data/inputs/metal_site_def.txt` are clearly labelled `<...>`/PLACEHOLDER. You replace them with
> real values read from a verified carbonic-anhydrase structure and/or a QM transition-state model,
> and you cite where each number came from. Nothing here is a measured experimental result.

## Files in this folder
- `download_data.py` — fetches the candidate reference CA structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py` (or
  `--dry-run`). It writes `provenance.csv`.
- `inputs/metal_site_def.txt` — the metal-site TEMPLATE you fill in (Zn ion + His3 ligands +
  Zn-hydroxide + TS geometry).
- `provenance.csv` — auto-written by `download_data.py` for fetched structures.

## Candidate reference accessions (VERIFY on RCSB in Week 1 — do not trust blindly)
These are **candidate** IDs flagged "look up + verify"; PDB entries get superseded and carbonic
anhydrase has many deposited structures/variants. Confirm the exact entry/chain on RCSB before use;
if you cannot confirm one, comment it out and rely on the other (or the constructed template only).
- `2CAB` — **candidate — verify on RCSB:** a human carbonic anhydrase II structure with the
  catalytic **Zn-His3** site. Read off the real **Zn-N(His) distances (~2.0–2.2 Å)** and the
  **N-Zn-N angles** to replace the placeholders in `metal_site_def.txt`.
- `3KS3` — **candidate — verify on RCSB:** a second human carbonic anhydrase II candidate — cross-
  check the Zn-His3 geometry and use as the **natural-CA positive control** for the assay logic.
- Also worth looking up + verifying: other human CA II entries (and CA isozymes), and any deposited
  **Co(II)-substituted** CA for the alternative-metal stretch. Treat every ID as a candidate.

## Where to find labeled de-novo-metalloenzyme data (for controls/benchmarks)
The **GRACE** work (Hu et al. 2024) reports de novo carbonic-anhydrase-style designs, the pool size
(~10k), and activity data — read its **supplementary materials** for design definitions and reported
metrics. **Record the DOI, the exact table/figure, and the license/terms** for each item. Use any
reported activity only as *context / positive control* — never copy a reported Wilbur-Anderson unit
or kcat into your own results as if you measured it.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Paper supplementary data (GRACE etc.): inherits that paper's terms — check and log each one (DOI +
  table).
- Any QM/literature geometry you encode: cite the source paper(s).

## Compute / size note
No large data here — a few small PDBs. Never commit fetched structures, model weights, or MD
trajectories; `results/` and large files stay out of git (see `MASTER_BLUEPRINT.md §6`).
