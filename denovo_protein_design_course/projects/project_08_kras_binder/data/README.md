# Project 08 — Data

This project's data is a **target definition**: the structure(s) of **KRAS** (in the right allele and
the right **nucleotide state**), used to (a) extract a clean KRAS G-domain to design against and (b)
read off the **epitope hotspots** (switch I, switch II, or an allele-specific pocket), **plus** HRAS
and NRAS structures so you can model and later test **isoform selectivity**. Provenance is graded —
every input must carry its source, and every accession is a **candidate to verify on RCSB in Week 1**.

## What you need to assemble
| Group | Count | Source | Use |
|-------|-------|--------|-----|
| KRAS structure(s) — chosen allele + nucleotide state | 1–2 | RCSB PDB | clean the KRAS G-domain to design against; read off switch I/II (or allele-pocket) hotspots |
| HRAS + NRAS structures | 2 | RCSB PDB | the **isoform-specificity panel** — model the binder against off-target isoforms |
| (derived) cleaned KRAS target | 1 | you produce it | the target PDB for BindCraft/RFdiffusion (correct nucleotide state, Mg²⁺ kept if relevant) |
| (optional) known KRAS-binder reference | 1 | RCSB / literature | positive-control reference for the validation plan (e.g. a G12C-inhibitor complex, a DARPin/binder) |

> **Why this is the hard part:** generation is easy; the design *decisions* that matter are
> **(a) the epitope** (KRAS has a small, charged, relatively featureless surface — the druggable
> handholds are switch I/II or an allele pocket), **(b) the nucleotide state** (GDP "off" vs GTP/GppNHp
> "on" change the switch conformations), and **(c) selectivity vs HRAS/NRAS** (the isoforms are nearly
> identical across the switches). Derive the hotspots from the actual structure + state, not a generic
> surface patch.

## Files in this folder
- `download_data.py` — fetches the candidate KRAS / HRAS / NRAS structures (RCSB) with SHA-256 +
  license logging. **You edit only its `ACCESSIONS` list.** Run: `python data/download_data.py`.
- `inputs/` — small seed files only (your cleaned KRAS PDB, the hotspot list, the BindCraft/RFdiffusion
  config, the KRAS/HRAS/NRAS alignment). **Never commit large data** (raw PDB dumps, model weights,
  AF2 outputs) — fetch them.
- `provenance.csv` — auto-written by `download_data.py` (URL, checksum, license, fetch date).

## Candidate accessions (verify on RCSB in Week 1)
**Candidate — verify before use; PDB entries are occasionally superseded.** Confirm the allele,
**nucleotide state**, chain, and resolution for each before you trust the numbering:
- `4OBE` — **candidate** WT KRAS. Verify it is WT human KRAS and **record its nucleotide state**
  (GDP vs GTP/analog); the switch I/II hotspots are read off this structure.
- `6OIM` — **candidate** KRAS **G12C**. Verify the allele/state; this defines the **G12C
  allele-specific surface** used in allele-selectivity reasoning. *(Some G12C structures are covalent
  inhibitor complexes — note whether a covalent warhead occupies the switch-II pocket.)*
- **HRAS / NRAS (isoform-specificity panel)** — add **verified** HRAS and NRAS accessions (placeholders
  are commented in `download_data.py`, e.g. a classic HRAS G-domain and an NRAS structure). These are
  the **off-targets**: you model the binder against them to estimate selectivity.

> Isolate the KRAS chain, keep the **bound nucleotide + Mg²⁺** when the switch conformation depends on
> them, remove waters/extra heteroatoms, and list the KRAS residues of your chosen epitope (switch I
> ~30–38, switch II ~60–76, or the allele pocket) as your **hotspots**. Record the **state** alongside.

## Nucleotide-state note (read before you clean anything)
KRAS cycles between a **GDP-bound "off"** state and a **GTP-bound "on"** state; effectors (RAF, etc.)
engage the GTP state. The **switch I and switch II** loops change conformation between states, so the
binder surface you are targeting **only exists in one state**. Decide which state you are designing
against, pick a structure in that state (GppNHp / GMPPCP are common non-hydrolyzable GTP analogs), and
**record the state in every design row** (`binder_tools.BinderDesign.nucleotide_state`). A
**nucleotide-state-dependence test** is a `[stretch]` deliverable (notebook 05).

## Sizes
Each PDB/mmCIF is small (≈0.2–1 MB) — fine to fetch, **not** to commit. Generated design pools,
AF2-Multimer outputs, isoform-panel predictions, and any model weights are large and **git-ignored**
(write them to `results/`).

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition (and the original KRAS / HRAS / NRAS structure papers).
- AlphaFold DB (if you pull a predicted model): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt (if you pull the KRAS/HRAS/NRAS sequences, e.g. P01116/P01112/P01111): CC-BY-4.0.
- Any binder/inhibitor reference from a paper's supplementary data inherits that paper's terms — log the DOI.

## Responsible-research note
KRAS is a human **oncotarget**; this project designs **inhibitory/blocking** binders to it for
**cancer therapeutics / diagnostics** (in scope). Do not redistribute restricted data; link + script
the download. See `MASTER_BLUEPRINT.md §7` and the Responsible Research sections of `README.md` /
`MANUAL.md`.
