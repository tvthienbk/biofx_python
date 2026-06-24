# Project 05 — Data

This project's "data" is a **design pool**: candidate sequences each annotated with in-silico
metrics (scRMSD, pLDDT, pAE, solubility, interface energy, MD drift). The engine *scores* the pool;
it does not generate designs. There are two kinds of pool, and you should be clear about which you
are using.

## What you need (two pools)
| Pool | Count | Source | Use |
|------|-------|--------|-----|
| **Production pool** | ~100–500 designs *with predictions* | Projects 01/03 outputs, or public design sets (e.g., supplementary data of de novo design papers) | the real thing the engine triages |
| **`EXAMPLE_DATA` teaching pool** | ~200 designs (you generate) | `scripts/make_example_pool.py` (deterministic seed) | develop + unit-test the layers with **no GPU**; every row clearly synthetic |
| Natural positive references | a few | RCSB / UniProt (`download_data.py`) | sanity-check the geometry helper; positive controls for downstream projects |

> **Why there is no single accession to fetch:** a design pool is *produced by a campaign*, not
> downloaded from one database. The production pool comes from Projects 01/03 (or public design-paper
> supplementary tables), each item carrying its own provenance. `download_data.py` here fetches only
> a handful of **natural reference structures** so you can exercise the Cα-RMSD helper and have
> positive controls — it is intentionally minimal.

## The teaching pool (`EXAMPLE_DATA`)
`scripts/make_example_pool.py` writes `results/pool.csv` with ~200 rows. **Every row is clearly
synthetic** — `design_id` is prefixed `EXAMPLE_DATA_`, and a hidden `truth` column (`good`/`bad`)
records the *planted* label so notebook 04 can measure enrichment. The pool is **mixed**
(monomer/binder/enzyme/antibody/oligomer) and contains deliberately planted cases:
- **known-GOOD** designs that pass every layer (low scRMSD, high pLDDT, orthogonal agreement, soluble, good interface, stable MD);
- **known-BAD** designs that fail a *specific* layer (e.g., good static metrics but the orthogonal predictor disagrees → fails L2; self-consistent but aggregation-prone → fails L3; folds-but-melts → fails L4);
- **ambiguous** designs near the cutoffs, so enrichment is imperfect and the discrimination problem is visible.

**Never present these numbers as real results.** They exist to develop and test the engine and to
*illustrate* the discrimination problem, not to report a hit rate.

## Files in this folder
- `download_data.py` — fetches a few *natural reference* structures (RCSB) with SHA-256 + license
  logging. **You edit its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `provenance.csv` — auto-written by `download_data.py` for the fetched structures.
- (the design pool itself lives in `results/pool.csv`, written by `scripts/make_example_pool.py`, and is git-ignored.)

## Candidate natural references (verify on RCSB in Week 1)
Starting points for positive controls / geometry sanity checks — **candidate accessions, verify
before use; PDB entries are occasionally superseded:**
- `1UBQ` — ubiquitin (small, robust α/β fold)
- `1L2Y` — Trp-cage (tiny fast-folder)
- `1ENH` — engrailed homeodomain (small all-α)

## Where a real production pool comes from
- **Project 01** (validation harness): designs with parsed AF2/ESMFold/Boltz confidence.
- **Project 03** (and other design projects): generated pools with their metrics.
- **Public design sets:** supplementary tables of de novo design papers (RFdiffusion, ProteinMPNN,
  BindCraft, etc.) that report per-design metrics. **Record the DOI, the exact table, and the
  license** for each item. Exclude anything whose primary function is harmful (`MASTER_BLUEPRINT.md §7`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Paper supplementary data (production pool): inherits that paper's terms — check and log each one.
- The `EXAMPLE_DATA` pool is synthetic and generated locally; it carries no external license but is **not real data**.
