# Project 13 — Data

This project's data is a **target definition**: the structure of the **IL-2 / IL-2R quaternary
complex**, used to (a) extract the individual **receptor subunits** (IL-2Rα/CD25, IL-2Rβ/CD122,
γc/CD132) to design against and model selectivity, and (b) read off the **IL-2 contact residues on each
subunit** as your per-subunit hotspots. Provenance is graded — every input must carry its source, and
every accession is a **candidate to verify on RCSB in Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| IL-2 / IL-2R quaternary complex | 1 | RCSB PDB | read off the per-subunit IL-2 contacts; separate the three receptor chains |
| (derived) IL-2Rα / IL-2Rβ / γc individual subunits | 3 | you produce them from the complex | the per-subunit targets for design + AF2-Multimer selectivity modeling |
| (derived) IL-2Rβ + γc signaling-pair surface | 1 | you produce it from the complex | the surface you steer the agonist onto (must bridge β and γc to dimerize) |
| (optional) Neo-2/15 reference design | 1 | PDB / literature (Silva 2019) | a reference de novo βγ-biased agonist + a positive control for the validation plan |

> **Why selectivity is the hard part:** generation is easy; steering the agonist onto the **signaling
> pair (β + γc)** so it dimerizes them, *while sparing the capture chain (α/CD25)*, is the design
> decision that matters — and it must be **proven by modeling against each subunit separately**, not
> assumed. Derive the hotspots from the IL-2/IL-2R interface in the complex, not from a generic patch.

## Files in this folder
- `download_data.py` — fetches the candidate complex structure (RCSB) with SHA-256 + license logging.
  **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your separated subunit PDBs, per-subunit hotspot lists,
  RFdiffusion/BindCraft config). **Never commit large data** (raw PDB dumps, model weights, AF2 outputs)
  — fetch/generate them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** This defines the IL-2/IL-2R
interfaces; the per-subunit hotspots are read off the IL-2 footprint on each chain in the complex:
- `2B5I` — **candidate** human IL-2 in complex with its trimeric receptor (IL-2Rα/IL-2Rβ/γc). Verify the
  chains (which chain is IL-2 vs α vs β vs γc), resolution, and that it is the human quaternary complex.
  *(If 2B5I is superseded or partial, cross-check against other IL-2–receptor complexes on RCSB and
  record what you used.)*
- *(optional)* the **Neo-2/15** de novo design coordinates (from Silva 2019 supplementary / PDB if
  deposited) as a reference βγ-biased agonist. Verify availability/terms.

> Identify the receptor chains, **split** IL-2Rα, IL-2Rβ, and γc into three separate target PDBs (remove
> IL-2, waters, heteroatoms), and list the IL-2-contacting residues on **each** chain as your per-subunit
> hotspots. The agonist target is the **IL-2Rβ + γc** surface; α is the chain you model selectivity
> *against* (you want to **spare** it).

## Sizes
The PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated design pools,
AF2-Multimer outputs (×3 subunits), and any model weights are large and **git-ignored** (write them to
`results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original IL-2/IL-2R structure paper).
- AlphaFold DB (if you pull a predicted subunit model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the IL2 / IL2RA / IL2RB / IL2RG sequences): CC-BY-4.0.
- The Neo-2/15 design / any reference from a paper's supplementary data inherits that paper's terms —
  log the DOI (Silva et al. 2019, *Nature*).

## Responsible-research note
IL-2 and its receptor are human immune-signaling proteins; this project designs a **receptor-selective
agonist mini-protein** whose explicit goal is to **reduce the toxicity** of the natural cytokine (a
βγ-biased mimetic spares CD25-high Tregs and vascular-leak toxicity) — an in-scope therapeutic purpose
with **low dual-use risk**. Do not redistribute restricted data; link + script the download. See
`MASTER_BLUEPRINT.md §7` and the Responsible Research sections of `README.md` / `MANUAL.md`.
