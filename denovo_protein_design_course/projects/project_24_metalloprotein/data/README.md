# Project 24 — Data

This project designs a **cofactor-binding metalloprotein** from scratch, so most of its "data" is
something you **construct**, not download: the **cofactor-site spec** (the cofactor + its coordinating
ligands + the geometry they must hold). The only fetched files are a few **reference cofactor-binding
proteins** used to *read off* the target coordination geometry and as positive controls / sanity
checks. Provenance is graded — record the source of every item. **There are no spectra here**: this
project never ships a measured Soret wavelength, EPR g-value, or redox potential.

## What you assemble vs. what you fetch
| Item | How | Source | Status |
|------|-----|--------|--------|
| Cofactor-site spec (cofactor + coordinating ligands + geometry) | **You build it** | A verified reference structure + literature | `data/inputs/cofactor_site_def.txt` (TEMPLATE to fill) |
| Cofactor definition (heme / [4Fe-4S] / Zn) + coordination scheme | **You build it** | Literature + the reference structure | encoded in the spec; NOT fabricated data |
| Reference heme / Fe-S / Zn proteins | `download_data.py` | RCSB | **candidates — verify on RCSB** |
| Designed-metalloprotein sequences (maquettes, de novo heme) | **You curate** | Paper supplementary tables | log DOI/table/license each |

> **The cofactor-site spec is a teaching template, not data.** The placeholder distances/angles in
> `data/inputs/cofactor_site_def.txt` are clearly labelled `<...>`/PLACEHOLDER. You replace them with
> real values read off a **verified** reference structure (and/or a QM model of the metal centre), and
> you cite where each number came from. Nothing here is a measured experimental result, and **no
> spectrum is ever fabricated** — predicted spectroscopic signatures are stated qualitatively only.

## Files in this folder
- `download_data.py` — fetches the candidate reference structures (RCSB) with SHA-256 + license
  logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py` (or
  `--dry-run`). It writes `provenance.csv`.
- `inputs/cofactor_site_def.txt` — the cofactor-site TEMPLATE you fill in (cofactor + coordinating
  ligands + coordination geometry; default = bis-His heme).
- `provenance.csv` — auto-written by `download_data.py` for fetched structures.

## Candidate reference accessions (VERIFY on RCSB in Week 1 — do not trust blindly)
These are **candidate** IDs flagged "look up + verify"; cofactor-binding proteins have many deposited
variants and entries get superseded. Confirm the exact entry/chain/cofactor on RCSB before use; if
you cannot confirm one, comment it out and rely on the constructed cofactor-site spec only.
- `1MBN` — **candidate — verify on RCSB:** sperm-whale **myoglobin**, the classic heme protein
  (proximal His F8 coordinates the Fe; the distal pocket binds O₂). Read off the Fe–N geometry; use
  for the **proximal-His O₂-binding** scheme.
- `3MK7` — **candidate — verify on RCSB:** a **b-type cytochrome / bis-His heme** electron-transfer
  reference (axial His/His). Confirm it really is a bis-His b-type heme before relying on it; if not,
  substitute another verified b-type cytochrome (e.g. a **cytochrome b562** entry) — the **default
  bis-His heme** scheme reads its geometry from a b-type cytochrome.
- `1FXD` — **candidate — verify on RCSB:** a **ferredoxin** carrying an Fe–S cluster (electron-transfer
  reference for the **[4Fe-4S]-4Cys** scheme). Confirm the cluster type (some ferredoxins are
  [2Fe-2S]) and the Cys motif before use.
- Also worth looking up + verifying: a **cytochrome b562** entry (a small natural bis-His heme
  4-helix bundle — an excellent design comparison), and a **designed/maquette heme protein** entry if
  one is deposited. Treat every ID as a candidate.

## Where to find labeled designed-metalloprotein data (for controls/benchmarks)
Look in the supplementary materials of the designed-metalloprotein papers (DeGrado-lab maquettes /
de novo metalloproteins; Baker-lab de novo cofactor-binders; Dauparas 2024 LigandMPNN examples).
Many report coordinating residues, cofactor, and the coordination scheme; some report spectroscopy.
**Record the DOI, the exact table/figure, and the license/terms** for each item. Use any reported
spectroscopy only as *context/positive controls* — never copy a reported Soret/EPR value into your
own results as if you measured it.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- Paper supplementary data: inherits that paper's terms — check and log each one (DOI + table).
- Any QM/literature geometry you encode: cite the source paper(s).

## Compute / size note
No large data here — a few small PDBs. Never commit fetched structures, model weights, or MD
trajectories; `results/` and large files stay out of git (see `MASTER_BLUEPRINT.md §6`).
