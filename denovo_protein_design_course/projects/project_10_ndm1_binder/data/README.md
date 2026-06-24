# Project 10 — Data

This project's data is a **target definition**: the structure(s) of **NDM-1** (New Delhi
metallo-β-lactamase) with its **di-zinc active site**, used to (a) extract a clean target to design
against — **preserving both catalytic Zn²⁺ ions** — and (b) read off the **active-site-rim hotspot
residues** that wall the substrate-access channel (the occluding epitope). Provenance is graded —
every input must carry its source, and every accession is a **candidate to verify on RCSB in Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| NDM-1 di-zinc structures | 1–2 | RCSB PDB | define the di-zinc active site + active-site-rim hotspots; clean target to design against |
| (derived) cleaned NDM-1 target | 1 | you produce it from the structure | the target PDB for BindCraft/RFdiffusion — **both Zn²⁺ kept as heteroatoms** |
| (optional) NDM-1 sequence | 1 | UniProt | residue-numbering reference for the rim hotspots |
| (optional) human metalloenzyme refs | 1–2 | RCSB | off-target SPECIFICITY counter-test (e.g. carbonic anhydrase II 1CA2) — verify |

> **Why the di-zinc site is the hard part:** generation is easy; the two catalytic **Zn²⁺ ions are
> part of the epitope**. If you strip them in prep, every downstream design is wrong. Keep both metals
> as heteroatoms, do **not** design over the Zn-coordinating His/Cys/Asp residues, and steer the binder
> onto the **rim** that walls the substrate channel — that is what makes it an *occluder/inhibitor*.

## Files in this folder
- `download_data.py` — fetches the candidate NDM-1 structures (RCSB) with SHA-256 + license logging.
  **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned NDM-1 PDB **with Zn**, rim-hotspot list,
  BindCraft/RFdiffusion config). **Never commit large data** (raw PDB dumps, model weights, AF2
  outputs) — fetch them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** These define the NDM-1
di-zinc active site; confirm **both Zn²⁺ ions are present** and read the active-site-rim hotspots off
the substrate-access channel:
- `3SPU` — **candidate** NDM-1 with the di-zinc active site (primary target prep). Verify the chain,
  resolution, and that **both Zn²⁺** are modeled; read off the active-site-rim hotspots here.
- `4EYL` — **candidate** NDM-1 (often with a hydrolyzed β-lactam product bound). Cross-check the
  di-zinc geometry and the substrate-channel rim against 3SPU; remove the hydrolyzed-substrate ligand
  but **keep the metals**.

> Identify the NDM-1 chain, remove waters/buffer and any hydrolyzed-substrate ligand, **retain both
> Zn²⁺ ions as heteroatoms**, and list the rim residues within contact distance of the substrate-access
> channel as your **hotspots**. (EXAMPLE placeholders in the notebooks: `A120,A220,A228` — replace
> with the rim residues you derive from the verified structure.)

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated design pools,
AF2-Multimer outputs, and any model weights are large and **git-ignored** (write them to `results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original NDM-1 structure paper).
- AlphaFold DB (if you pull a predicted model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the blaNDM-1 sequence): CC-BY-4.0.
- Any inhibitor/binder reference from a paper's supplementary data inherits that paper's terms — log the DOI.

## Responsible-research note
This is a **defensive anti-AMR** target: the goal is to **inhibit** NDM-1 (restore carbapenem
efficacy), in scope under `MASTER_BLUEPRINT.md §7` ("AMR enzymes (to *inhibit*)"). It is out of scope
to enhance resistance, pathogen fitness, or to stabilize/protect the enzyme. Do not redistribute
restricted data; link + script the download. See the Responsible Research sections of `README.md` /
`MANUAL.md`.
