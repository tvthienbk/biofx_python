# Project 25 — Data

This capstone needs **two** kinds of data: (1) the **structure/sequence of your chosen,
advisor-approved target** (to design against), and (2) the **aggregated design→outcome feature table**
assembled across Projects 01–24 in the cohort (to train the success predictor). Provenance is graded —
every input must carry its source, and every accession is a **candidate to verify on RCSB/UniProt in
Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| Your target structure / sequence | 1–few | RCSB PDB / AlphaFold DB / UniProt | the structure(s) you design against (your `design_type`) |
| (derived) cleaned target | 1 | you produce it from the structure | the input PDB / motif / theozyme for generation |
| **Cohort design→outcome table** | many rows | **Projects 01–24 outputs** | the `features → success` table the ML predictor trains on |
| (optional) experimental labels | as available | your cohort's wet-lab results | real `success` labels (`label_origin="experimental"`) — never fabricated |

> **The cohort table is the project's distinctive input.** One row per design with the in-silico
> features (`scrmsd`, `plddt`, `pae_interaction`, `solubility`, `rosetta_dG`, `shape_complementarity`,
> `tm_to_pdb`) and a `success` label. Assemble it from each prior project's filtered design table
> (`results/ranked.csv` etc.), normalizing columns to the feature schema, tagging `design_type`/`target`,
> and attaching any experimental outcome. Write it to `data/cohort_design_outcomes.csv` so
> `ml_predictor.build_cohort_table(csv_path=...)` LOADS it instead of synthesizing.

## `EXAMPLE_DATA` (teaching fallback — no real cohort yet)
With no real cohort assembled, `scripts/ml_predictor.py:build_cohort_table()` **generates a
deterministic `EXAMPLE_DATA` synthetic cohort** (fixed seed) with a planted, *imperfect* feature→outcome
structure, so notebook 04 runs anywhere. **Every synthetic row's `source` is `EXAMPLE_DATA` and its
`label_origin` is `EXAMPLE_DATA_SYNTHETIC`.** These are *teaching numbers only* — never present them as
real outcomes, and never report a hit rate, K_D, or kcat derived from them as real.

## Files in this folder
- `download_data.py` — fetches your **target** structure/sequence (RCSB/UniProt) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list** for your chosen target. Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned target PDB, configs, a small `cohort_design_outcomes.csv`
  if it fits). **Never commit large data** (design pools, model weights, AF2 outputs) — fetch/regenerate them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).
- `cohort_design_outcomes.csv` — *you create this* by assembling Projects 01–24 outputs (the real table).

## Candidate accessions (verify on RCSB/UniProt in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** The `download_data.py`
shipped here uses neutral, in-scope example structures as placeholders — **replace them with your
advisor-approved target**:
- `1UBQ` — ubiquitin (a small natural reference / placeholder; replace with your target).
- Replace with your target's accession(s) and confirm chains, resolution, and that the framing is
  in-scope under `MASTER_BLUEPRINT.md §7` (advisor-approved before P2).

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. The cohort feature table is a
CSV (small). Generated design pools, model weights, and AF2 outputs are large and **git-ignored** (write
them to `results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Any design→outcome rows pulled from a paper's supplementary data inherit that paper's terms — log the
  DOI and check it.

## Responsible-research note
Your target is **student-chosen and must be advisor-approved against `MASTER_BLUEPRINT.md §7` before the
design campaign (P2)**. Default any ambiguous target to a neutralizing/diagnostic/inhibitory/industrial
framing; no out-of-scope targets. Do not redistribute restricted data; link + script the download. See
the Responsible Research sections of `README.md` / `MANUAL.md §8`.
