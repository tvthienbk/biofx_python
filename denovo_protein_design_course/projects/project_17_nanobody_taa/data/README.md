# Project 17 — Data

This project's inputs are the **tumor-associated antigen (TAA) structures** you design VHH/nanobodies
against, plus the **related-receptor panel** you use for the specificity counter-screen. Provenance is
graded — every item must carry its source, license, and access date.

## What you need to assemble
| Group | What | Source | Use |
|-------|------|--------|-----|
| Primary TAA + reference complex | HER2 with the trastuzumab footprint | RCSB | defines the epitope (overlapping vs not) |
| Alternative TAA | EGFR (or a mesothelin model) | RCSB / AFDB | second target option + a HER-family off-target |
| Receptor-family panel | EGFR / HER3 / HER4 | RCSB / AFDB | specificity counter-screen |
| VHH framework | a humanized VHH germline framework | IMGT / a published hu-VHH | the fixed scaffold the CDRs sit on |

> **Why the epitope is the hard part:** the design's value hinges on *where* on the TAA it binds. Read
> the epitope residues off the verified antigen surface — and, for the "overlapping" option, off the
> mAb–antigen interface in the reference complex. Do **not** use the EXAMPLE residue lists in the
> notebooks as real epitopes.

## Files in this folder
- `download_data.py` — fetches the TAA structures (RCSB) with SHA-256 + license logging. **You edit
  its `ACCESSIONS` list.** Run: `python data/download_data.py` (or `--dry-run` to preview URLs).
- `provenance.csv` — auto-written by `download_data.py` (accession, URL, sha256, license, date).
- `inputs/` — small seed files only (a cleaned target PDB, the framework FASTA, epitope residue list).
  **Never commit large data** (full PDB dumps, model weights, display libraries) — fetch them.

## Candidate accessions (verify on RCSB in Week 1 — entries get superseded)
- `1N8Z` — **trastuzumab Fab – HER2 (ERBB2) domain IV** complex. Primary TAA; the trastuzumab contact
  residues define the **overlapping** epitope option. **candidate — verify on RCSB.**
- `1IVO` — **EGFR (ERBB1) extracellular region + EGF.** Alternative TAA *and* a HER-family off-target
  for the specificity panel. **candidate — verify on RCSB.**
- **Mesothelin (MSLN, UniProt Q13421)** — there is no single clean experimental TAA-epitope structure
  as teaching-friendly as 1N8Z/1IVO. If you choose mesothelin, use a structural **MODEL** (AlphaFold DB
  via the `alphafold` source) and clearly mark it "**model — verify**"; never treat a model as an
  experimental structure.
- **Receptor-family specificity panel:** the HER/ErbB family — HER2 (target), EGFR/HER1, **HER3
  (ERBB3, P21860)**, **HER4 (ERBB4, Q15303)**. Add their structures or AFDB models when you build the
  counter-screen; verify each. Keep the panel to relatives that share surface with your epitope so the
  test is meaningful.

## Sizes
- Single RCSB structures are small (~0.2–2 MB each); AFDB models are ~0.3 MB. The whole input set is a
  few MB — fine to fetch, never commit. A display screen's NGS/library data (real wet-lab follow-up) is
  large and lives outside the repo.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Any framework/antibody sequence from a paper inherits that paper's terms — log the DOI and check it.

## Responsible research
Therapeutic/diagnostic oncology only (a human tumor antigen). Exclude any target whose primary purpose
is harm; see `MASTER_BLUEPRINT.md §7`. Real gene-synthesis orders go through a biosecurity-screening
provider; wet-lab work requires institutional biosafety/ethics approval.
