# Project 12 — Data

This project's data is a **target definition** plus **reference designs**: (a) the structure of a
chosen **biomarker / analyte** (STUDENT CHOICE) to design a binder against and read off an epitope, and
(b) **split-reporter / LOCKR-style switch reference designs** to adapt for the transduction element.
Provenance is graded — every input must carry its source, and every accession is a **candidate to
verify on RCSB in Week 1**.

## The analyte is YOUR choice
The catalog deliberately leaves the analyte open. **You pick the biomarker** — e.g. a **cytokine**
(inflammation/infection) or a **cardiac marker** (e.g. a troponin subunit) — and verify its structure
on RCSB. Choose one with:
- a verified, reasonably high-resolution **RCSB structure** (or a confident AlphaFold model);
- a clear **point-of-care / diagnostic** motivation (low dual-use);
- a surface **epitope** you can target without disrupting whatever makes it a useful marker.

> Generation is easy; the design decisions that matter are **which epitope** the binder engages (so
> binding couples to the switch) and **which switch architecture** transduces it. Derive the epitope
> from the analyte structure, not from a generic surface patch.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| analyte/biomarker structure | 1 | RCSB PDB (or AlphaFold DB) | clean target to design the binder against; read off the epitope |
| (derived) cleaned analyte target | 1 | you produce it | the target PDB for BindCraft/RFdiffusion |
| split-reporter / LOCKR reference design | 1+ | literature supplementary (Langan 2019, Quijano-Rubio 2021, NanoBiT) | the switch scaffold to adapt for transduction |
| (optional) off-target analyte | 1 | RCSB | specificity control (the sensor must NOT switch for it) |

## Files in this folder
- `download_data.py` — fetches the candidate analyte structure (RCSB) with SHA-256 + license logging.
  **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned analyte PDB, epitope list, switch reference,
  BindCraft/RFdiffusion config). **Never commit large data** (raw PDB dumps, model weights, AF2/two-state
  outputs) — fetch/generate them into `results/`.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accession (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded, and the analyte is YOUR
choice — this is only an example to get the plumbing running.**
- `1J1E` — **candidate** human **cardiac troponin** (core domain) — an EXAMPLE cardiac biomarker so the
  download/plumbing has something to fetch. **Verify** the entry, chains, resolution, and that the
  chain/domain you target is the right one — **or replace it entirely** with your chosen analyte
  (e.g. a cytokine such as IL-6, TNF-α, etc.). Mark whatever you choose "candidate — verify on RCSB."

> Identify the analyte chain, clean it (remove waters/heteroatoms/irrelevant partners), and list the
> surface residues you will target as your **epitope** (the binder hotspots).

## Split-reporter / switch references (no single download — literature + reuse)
The switch module is **literature-driven**, not a package download:
- **LOCKR** cage+latch designs — Langan et al. 2019 (Nature) supplementary structures/sequences.
- **De novo biosensors** (LOCKR-coupled binders) — Quijano-Rubio et al. 2021 (Nature).
- **Split-luciferase / NanoBiT** — Dixon et al. 2016 (the LgBiT/SmBiT split).
Record the DOI + any structure accession you adapt; switch reference designs inherit their paper's terms.

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated design pools,
AF2-Multimer / two-state outputs, and any model weights are large and **git-ignored** (write them to
`results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original analyte structure paper).
- AlphaFold DB (if you pull a predicted model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the analyte sequence): CC-BY-4.0.
- Any switch/split-reporter reference from a paper's supplementary data inherits that paper's terms —
  log the DOI.

## Responsible-research note
This project designs a **diagnostic / point-of-care biosensor** for a disease biomarker — an in-scope
diagnostic purpose with **low dual-use** concern. Do not redistribute restricted data; link + script
the download. See `MASTER_BLUEPRINT.md §7` and the Responsible Research sections of `README.md` /
`MANUAL.md`.
