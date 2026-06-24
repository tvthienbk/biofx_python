# Project 14 — Data

This project's inputs are (1) a **conserved-epitope reference complex** (to define the neutralizing
epitope on the viral antigen), (2) a **humanized VHH framework**, and (3) a **strain panel** for the
breadth analysis. Provenance is graded — record the source of every input.

## What you need to assemble
| Input | Source | Note |
|-------|--------|------|
| Antigen + neutralizing-Ab complex | RCSB (candidate **4FQI** HA stem; or **5UDE** RSV F prefusion) | defines the conserved neutralizing epitope |
| Humanized VHH framework | literature / IMGT | the fixed scaffold; the CDRs are the design variables |
| Strain panel | RCSB + UniProt (HA / RSV F sequences across subtypes/strains) | for the breadth analysis |
| Conservation alignment | built in-notebook | scores epitope conservation; the conserved-epitope justification |

> **Why the panel matters:** breadth is the point of a *conserved* epitope. One antigen structure is
> not enough — you need the strain panel to test whether a VHH generalizes.

## Files in this folder
- `download_data.py` — fetches the reference complex (RCSB) with SHA-256 + license logging. **You edit
  its `ACCESSIONS` list** to add the strain sequences/complexes you choose. Run: `python data/download_data.py`.
- `inputs/` — small seed files only (epitope/framework definitions, the strain list). Never commit large structures.

## Candidate accessions (verify on RCSB/UniProt in Week 1)
- `4FQI` — influenza HA with a broadly-neutralizing antibody (the conserved **HA-stem** epitope). **Candidate — verify.**
- `5UDE` / DS-Cav1 — RSV F prefusion (alternative conserved neutralizing target). **Candidate — verify.**
- Strain panel: HA (or RSV F) sequences across subtypes/strains — **the student assembles + verifies** (record DOI/source per item).

## Responsible-research note on data
Use only published structures/sequences for a **neutralizing/diagnostic** purpose. Do not assemble
data to support enhancing viral fitness or escape. See `MASTER_BLUEPRINT.md §7`.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- UniProt: CC-BY-4.0; OAS for antibody repertoires. Any sequence from a paper inherits that paper's terms — log the DOI.
