# Project 11 — Data

This project's data is a **two-conformation target definition**: the cryo-EM structure(s) of the
amyloid **fibril** (tau PHF or α-synuclein fibril), used to (a) extract a clean protofilament surface
to design against and (b) read off the exposed **fibril-surface epitope residues** — plus a **monomer
model** of the same protein for the conformational-specificity **counter-test**. Provenance is graded —
every input must carry its source, and every accession is a **candidate to verify on RCSB/UniProt in
Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| Amyloid **fibril** cryo-EM structures | 1–2 | RCSB PDB | the design target surface; read the exposed fibril epitope; clean a protofilament |
| (derived) cleaned **protofilament** surface | 1 | you produce it from the fibril | the target PDB for BindCraft/RFdiffusion |
| **Monomer** model (same protein) | 1 | AlphaFold DB / disordered-ensemble model | the conformational-specificity **counter-test** (the binder must reject it) |
| (cross-amyloid) the **other** amyloid fibril | 1 | RCSB PDB | tau-vs-α-syn off-target for the discrimination extension |
| (optional) conformational anti-fibril antibody/tracer | 1 | RCSB / literature | positive control reference for the validation plan |

> **Why the conformation is the hard part:** generation against the fibril surface is the easy half.
> The design decision that matters is choosing a **fibril-specific** surface — one that is exposed on
> the ordered cross-β core but **buried or simply absent in the disordered monomer** — so the binder
> can be **selective**. Derive the epitope from the fibril structure, not a generic surface patch, and
> always run the **monomer counter-test**.

## Files in this folder
- `download_data.py` — fetches the candidate fibril structures (RCSB) and the monomer model (AFDB) with
  SHA-256 + license logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned protofilament PDB, the monomer model, fibril-surface
  hotspot list, BindCraft/RFdiffusion config). **Never commit large data** (raw cryo-EM maps, model
  weights, AF2 outputs) — fetch them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** These define the fibril
conformation; the fibril-surface hotspots are read off the exposed cross-β core:
- `5O3L` — **candidate** tau paired-helical filament (PHF) cryo-EM fibril (Fitzpatrick 2017). Verify
  chains, the ordered-core residue range, and the protofilament you isolate.
- `5O3T` — **candidate** tau straight filament (SF) — cross-check the fibril surface against 5O3L. Verify.
- `6CU7` — **candidate** α-synuclein fibril cryo-EM. Verify; also the tau↔α-syn cross-amyloid off-target.
- `6H6B` — **candidate** α-synuclein fibril polymorph — cross-check against 6CU7. Verify.
- (monomer) `P10636` (tau / MAPT) and `P37840` (α-synuclein / SNCA) **AFDB monomer models** —
  **candidate, verify on UniProt**; the monomer is **intrinsically disordered**, so a single model is a
  modeling caveat (prefer an ensemble) — note this in your report.

> Isolate a **protofilament**, keep the **ordered cross-β core**, remove waters/heteroatoms, and list
> the **solvent-exposed surface residues** as your **fibril-surface hotspots** (the epitope). For the
> counter-test, pull the **monomer** model of the same protein and score against it (`pae_monomer`).

## Sizes
Each fibril PDB/mmCIF is modest (≈0.5–5 MB; fibrils have many chains in the asymmetric unit) and the
AFDB monomer model is small (≈0.2 MB) — fine to fetch, **not** to commit. Raw cryo-EM maps, generated
design pools, AF2-Multimer outputs, and any model weights are large and **git-ignored** (write them to
`results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original fibril cryo-EM papers — Fitzpatrick
  2017 for tau PHF; the α-synuclein fibril paper for 6CU7/6H6B).
- AlphaFold DB (the monomer model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the MAPT / SNCA sequence): CC-BY-4.0.
- Any binder/antibody reference from a paper's supplementary data inherits that paper's terms — log the DOI.

## Responsible-research note
Tau and α-synuclein fibrils are **disease-associated aggregates**; this project designs
**conformation-selective** binders for **neurodegeneration diagnostics** (PET tracers, fibril assays)
and **aggregation modulation** — in scope, **low dual-use**. Do not redistribute restricted data; link
+ script the download. Any **patient-derived material** in the validation plan requires institutional
biosafety/ethics approval. See `MASTER_BLUEPRINT.md §7` and the Responsible Research sections of
`README.md` / `MANUAL.md`.
