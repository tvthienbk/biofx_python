# Project 15 — Data

This project's input is **ONE antibody-antigen complex** that you mature: a structure from **SAbDab**
(the Structural Antibody Database) with a **measured KD reported in the literature**. That complex is
the lead; its KD is the baseline every proposed CDR mutation is measured against. Provenance is graded —
every item must carry its source, license, and access date.

## What you need to assemble
| Group | What | Source | Use |
|-------|------|--------|-----|
| Primary complex | one antibody-antigen complex **with a published KD** | SAbDab → RCSB | the lead you mature; defines CDR contacts + the baseline KD |
| (Optional) off-target antigen | a related paralog / family member | RCSB / AFDB | specificity counter-screen (notebook 05) |
| Antibody numbering | CDR boundaries (IMGT/Kabat/Chothia) | ANARCI on your chain | defines the **mutable CDR positions** (framework is fixed) |

> **The KD is the point of the project.** Affinity maturation is measured *relative to the parent's
> measured affinity*. Pick a complex whose KD is reported in a primary paper (SAbDab links the
> literature), record the **exact value + citation** in your problem statement, and never invent or
> assert a KD anywhere in the code. The notebooks rank candidates; only SPR measures affinity.

## Files in this folder
- `download_data.py` — fetches your chosen complex (RCSB) with SHA-256 + license logging. **You edit
  its `ACCESSIONS` list** (it ships empty on purpose — you pick the complex). Run:
  `python data/download_data.py` (or `--dry-run` to preview URLs).
- `provenance.csv` — auto-written by `download_data.py` (accession, URL, sha256, license, date).
- `inputs/` — small seed files only (the cleaned complex PDB, the parent antibody FASTA, the CDR
  position list from ANARCI). **Never commit large data** — fetch it.

## Choosing your complex (do this in Week 1 — entries get superseded)
- There is **no default accession**: the student picks the antibody-antigen complex. This avoids anyone
  silently inheriting an unverified complex or an unverified KD.
- **How to pick (candidate — verify):** browse SAbDab for a well-characterized **therapeutic Fab-antigen
  complex** with a clean single epitope and a **published KD**; confirm the PDB entry is current on RCSB
  and the interface is well resolved; record the KD + its citation. A therapeutic antibody against a
  **non-pathogen** target keeps you squarely in the responsible-research scope.
- Set `COMPLEX_PDB` in `download_data.py` and notebook 01, then uncomment its `Item`.

## Sizes
- A single RCSB complex is small (~0.2–3 MB); an AFDB off-target model is ~0.3 MB. The whole input set
  is a few MB — fine to fetch, never commit. (SPR/DSF wet-lab data is a real-world follow-up and lives
  outside the repo.)

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- SAbDab: cite Dunbar et al. 2014 (the database) plus the primary paper reporting the KD.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Any antibody/KD value from a paper inherits that paper's terms — log the DOI and check it.

## Responsible research
Therapeutic-antibody lead optimization against a **non-pathogen** target — low dual-use risk (it
improves a therapeutic candidate, it does not create a hazard). Keep the target in the
therapeutic/diagnostic scope; exclude any target whose primary purpose is harm. See
`MASTER_BLUEPRINT.md §7`. Real gene-synthesis orders go through a biosecurity-screening provider; wet-lab
work requires institutional biosafety/ethics approval.
