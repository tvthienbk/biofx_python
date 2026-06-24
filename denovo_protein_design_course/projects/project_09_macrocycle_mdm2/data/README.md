# Project 09 — Data

This project's data is a **target definition**: the structure of the **MDM2–p53 peptide complex**,
used to (a) extract a clean MDM2 N-terminal domain to design against and (b) read off the **MDM2
cleft residues** — the hydrophobic pocket that buries the p53 transactivation helix
(p53 **Phe19 / Trp23 / Leu26**). Those cleft residues are the analog of binder "hotspots": steering a
peptide/macrocycle there is what makes it a **p53-mimetic competitor** that can displace p53 from MDM2
and, in principle, restore p53 tumor-suppressor signalling. Provenance is graded — every input must
carry its source, and every accession is a **candidate to verify on RCSB in Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| MDM2–p53 peptide complex | 1 | RCSB PDB | define the p53-binding cleft + cleft residues; clean MDM2 to design against |
| (derived) cleaned MDM2 N-terminal domain | 1 | you produce it from the complex | the target PDB for BoltzGen / EvoBind2 |
| (optional) known p53-peptide / stapled-peptide | 1 | RCSB / literature | positive-control reference for the validation plan |
| (optional, alternative) IL-17A structure | 1 | RCSB | only if you switch the target from MDM2 to IL-17A (catalog alternative) |

> **Why the cleft is the hard part:** generation is easy; steering the peptide onto the actual
> **p53-mimetic cleft** (the Phe19/Trp23/Leu26 sub-pockets) so it can *compete with p53* is the design
> decision that matters. Derive the cleft residues from the MDM2–p53 interface in the complex, not from
> a generic surface patch.

## Files in this folder
- `download_data.py` — fetches the candidate complex structure (RCSB) with SHA-256 + license logging.
  **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned MDM2 PDB, cleft-residue list, BoltzGen/EvoBind2
  config). **Never commit large data** (raw PDB dumps, model weights, AF2/Boltz outputs) — fetch them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** This defines the MDM2–p53
competitive interface; the MDM2 cleft residues are read off the p53-peptide footprint in the complex:
- `1YCR` — **candidate** human MDM2 (N-terminal domain) bound to the **p53 transactivation peptide**
  (Kussie et al. 1996). It defines the hydrophobic p53-binding cleft and the three sub-pockets that
  bury p53 Phe19/Trp23/Leu26. **Verify on RCSB:** which chain is MDM2, the resolution, and that the
  p53 peptide is resolved. This is the canonical structure for MDM2–p53 peptide chemistry.
- *(alternative target)* `4HSA` — **candidate** IL-17A structure, only if you take the catalog's
  **IL-17A** alternative instead of MDM2. **Verify the correct accession/assembly** for the IL-17A
  binding cleft on RCSB before use (IL-17A is a different PPI with its own cleft definition).

> Identify the MDM2 chain, isolate its **N-terminal p53-binding domain**, remove the p53 peptide,
> waters, and heteroatoms, and list the MDM2 residues within contact distance of the p53 peptide as
> your **cleft residues** (the competitive epitope). Numbering depends on the PDB you verify.

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated peptide pools,
AF2/Boltz outputs, and any model weights are large and **git-ignored** (write them to `results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (Kussie et al. 1996 for 1YCR / the MDM2–p53 structure).
- AlphaFold DB (if you pull a predicted model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the MDM2 sequence, Q00987): CC-BY-4.0.
- Any peptide reference from a paper's supplementary data inherits that paper's terms — log the DOI.

## Responsible-research note
MDM2 is a human oncology **protein–protein-interaction** target; this project designs **competitive
p53-mimetic** peptides/macrocycles to **restore p53 tumor-suppressor function** (an in-scope
therapeutic purpose). Do not redistribute restricted data; link + script the download. See
`MASTER_BLUEPRINT.md §7` and the Responsible Research sections of `README.md` / `MANUAL.md`.
