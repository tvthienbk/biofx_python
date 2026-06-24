# Project 07 — Data

This project's inputs are (1) the **RBD–ACE2 complex** (to define the ACE2-binding face and the
conserved epitope) and (2) a **panel of variant RBDs** (for the breadth analysis). Provenance is
graded — record the source of every input.

## What you need to assemble
| Input | Source | Note |
|-------|--------|------|
| RBD–ACE2 complex | RCSB (candidate **6M0J**) | defines the ACE2-binding (neutralizing) face + hotspots |
| Variant RBD panel | RCSB + UniProt (spike S sequences) | Wuhan/Delta/Omicron sublineages + sarbecoviruses for breadth |
| Conservation alignment | built in-notebook (align the panel) | scores epitope conservation; the conserved-epitope justification |

> **Why the panel matters:** breadth is the whole point of targeting a *conserved* epitope. A single
> RBD structure is not enough — you need the variant panel to test whether a binder generalizes.

## Files in this folder
- `download_data.py` — fetches the RBD–ACE2 complex (RCSB) with SHA-256 + license logging. **You edit
  its `ACCESSIONS` list** to add the variant complexes/sequences you choose. Run: `python data/download_data.py`.
- `inputs/` — small seed files only (epitope/hotspot definitions, the variant list). Never commit large structures.

## Candidate accessions (verify on RCSB/UniProt in Week 1)
- `6M0J` — SARS-CoV-2 RBD–ACE2 complex (defines the ACE2-binding face). **Candidate — verify; may be superseded.**
- Variant RBD structures/sequences (e.g. Omicron RBD–ACE2 complexes; SARS-CoV-2 spike UniProt `P0DTC2`
  to slice RBD variants) — **the student assembles + verifies the panel.** Record DOI/source per item.

## Responsible-research note on data
Use only published structures/sequences for a **neutralizing/diagnostic** purpose. Do not assemble
data to support enhancing viral fitness or escape. See `MASTER_BLUEPRINT.md §7`.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- UniProt: CC-BY-4.0. Any sequence from a paper inherits that paper's terms — log the DOI.
