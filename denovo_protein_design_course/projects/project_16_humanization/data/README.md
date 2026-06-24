# Project 16 — Data

This project's inputs are unusual: the primary input is a **sequence**, not a structure. You supply a
**non-human (murine / chimeric) therapeutic antibody** (VH + VL) and a **human germline framework
database** (IMGT / OAS). Provenance is graded — every item must carry its source, license, and access
date.

## What you need to assemble
| Group | What | Source | Use |
|-------|------|--------|-----|
| Non-human antibody (PRIMARY) | A published murine/chimeric therapeutic antibody VH + VL sequence | the publication (UniProt / patent / SAbDab) | the thing you humanize; the parental/ΔΔG/humanness baseline |
| Human germline frameworks | The human IGHV/IGKV/IGLV germline FRs you graft onto | **IMGT** / **OAS** | the human scaffold for CDR grafting (pick the closest germlines) |
| (Optional) reference structure | An Fab/Fv structure of your antibody, if one exists | RCSB / SAbDab | sanity-check the Fv model; read Vernier positions |

> **Why the antibody choice is the hard part:** humanization quality hinges on choosing a human germline
> **close** to your parental antibody (by V/J gene) so the graft changes as few framework residues as
> possible. Number your antibody (ANARCI; Kabat/Chothia/IMGT scheme) and read the Vernier-zone positions
> off the *verified* sequence. Do **not** use the EXAMPLE placeholder sequences in `humanization_tools.py`
> as a real antibody.

## Files in this folder
- `download_data.py` — a **provenance scaffold** (copied from `templates/download_data.py`). Its
  `ACCESSIONS` list is **mostly commented**, because the primary input is a student-supplied **sequence**
  and the germline DB is fetched separately (below). Use it to record any structures you do pull (e.g., a
  reference Fab) with SHA-256 + license logging. Run: `python data/download_data.py` (or `--dry-run`).
- `provenance.csv` — auto-written by `download_data.py` (accession, URL, sha256, license, date).
- `inputs/` — small seed files only (your antibody VH/VL FASTA, the chosen human germline FRs, the Vernier
  position list). **Never commit large data** — see below.

## The antibody sequence (student-supplied — VERIFY)
- Choose a **published** non-human therapeutic antibody whose humanization is a legitimate, defensible aim
  (immunogenicity reduction). Record the **paper / DOI**, the exact **VH and VL** sequences, and the
  CDR-definition scheme. **Mark it "candidate — verify"** until you confirm the sequence against the
  primary source. (Examples of historically humanized murine antibodies exist in the literature/SAbDab —
  pick one with a clear publication and CDR annotation; verify it.)
- Place the FASTA in `inputs/`. It is tiny (a few hundred residues) — safe to commit.

## The human germline framework database (downloaded separately — NOT committed)
- **IMGT** germline reference directory (IMGT/GENE-DB, IMGT/V-QUEST) — the canonical human IGHV/IGKV/IGLV
  germline sequences. License: IMGT terms (academic use; **read and record them** — IMGT data are not
  public-domain; cite Lefranc et al.).
- **OAS** (Observed Antibody Space) — large repertoire data for humanness scoring (OASis uses it). License:
  CC-BY-style per the OAS terms; **verify the current terms**.
- **Sizes:** a curated set of human germline FRs is tiny (a few KB). The **full OAS / IMGT databases are
  large** (OAS is many GB of repertoire data) — **download separately, never commit**, and document the
  size + access date in your report. For grafting you only need the **germline FR sequences** (small); the
  large repertoire DB is only needed if you run OASis humanness locally (BioPhi bundles what it needs).

## Candidate structures to pull (optional — verify on RCSB/SAbDab)
- If your antibody has a deposited **Fab/Fv structure**, fetch it for an Fv-model sanity check and to read
  Vernier positions. Add it to `ACCESSIONS` in `download_data.py` (uncomment the example) and verify the
  PDB ID. **candidate — verify.**

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- UniProt: CC-BY-4.0.
- IMGT: academic-use terms (NOT public domain); cite Lefranc et al. and record the terms.
- OAS: per the OAS data terms; cite Olsen et al.; verify the current license.
- Any antibody sequence from a paper/patent inherits that source's terms — log the DOI and check it.

## Responsible research
Therapeutic-antibody immunogenicity reduction only (humanizing a non-human therapeutic). Exclude any
target whose primary purpose is harm; see `MASTER_BLUEPRINT.md §7`. Real gene-synthesis orders go through a
biosecurity-screening provider; wet-lab work requires institutional biosafety/ethics approval.
