# Project 23 — Data

This project designs a **protein that binds a chosen DNA/RNA target motif**. The two inputs are
(1) a **target motif** (the NA sequence/structure you want to recognize) and (2) a **protein-NA
complex template** to scaffold near. Provenance is graded — record the source of every input.

## What you need to assemble
| Input | Source | Note |
|-------|--------|------|
| DNA/RNA target motif | your choice (a TF box, an RNA hairpin, a Cas-adjacent site) | justify it biologically; define the exact sequence |
| Protein-NA complex template | RCSB (a protein-DNA/RNA complex) | scaffold backbones near the NA; **candidate, verify** |
| Scrambled-motif control | generated in code (`na_binder_tools.py`) | the specificity counter-test — not fetched |

## Files in this folder
- `download_data.py` — fetches the candidate complex (RCSB) with SHA-256 + license logging. **You edit
  its `ACCESSIONS` list** to your chosen template. Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your motif definition, configs). Never commit large structures.

## Candidate template (verify on RCSB in Week 1)
- `1MEY` — designed zinc-finger-DNA complex (a classic protein-DNA recognition reference). **Candidate —
  verify; entries get superseded.** Replace with the complex matching your motif if more appropriate.

## Specificity is the whole point
A binder that hits your motif **and** a scrambled motif is not specific. The `motif_specificity()`
helper scores intended-vs-scrambled; report the gap, not just the intended-motif score.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- UniProt: CC-BY-4.0. Any motif taken from a paper inherits that paper's terms — log the DOI.
