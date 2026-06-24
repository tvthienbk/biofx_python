# Project 04 — Data

This project's data is **light by design**. The campaign *generates* symmetric backbones de novo
(notebook 02), so you do not need a large input set. What you assemble is (a) a small set of
**reference homo-oligomers** to anchor your symmetry intuition and comparison, (b) the named
**designed-nanocage family** for context, and (c) a tiny teaching scaffold of **symmetry
definitions**. The notebooks run end-to-end on a deterministic *mock* backend with **no downloaded
data at all**, so you can build the plumbing before fetching anything.

> **Accession honesty.** Symmetric / nanocage PDB IDs are easy to mis-remember and entries get
> superseded. **Treat every accession in this project as "candidate — verify on RCSB in Week 1."**
> `download_data.py` ships with an *empty, commented* `ACCESSIONS` list on purpose: you must fill it
> with **verified** IDs whose biological-assembly symmetry you have confirmed on the RCSB
> "Symmetry / Assembly" tab. Do not paste an unverified ID into your thesis.

## What you need to assemble
| Group | Count | Source | Why |
|-------|-------|--------|-----|
| Natural Cn homo-oligomer reference | 1–2 | RCSB (verify symmetry) | a real cyclic ring (C3/C4) to compare your designs against |
| Natural Dn homo-oligomer reference | 1 | RCSB (verify symmetry) | a real D2 homotetramer (dihedral) reference |
| Designed nanocage family (named) | — | RCSB (look up IDs) | I3-01 / I53-50 two-component nanocages — context, not required input |
| Symmetry definitions | 1 file | `inputs/symmetry_defs.txt` (shipped) | example C3/C4/D2 symmetric-contig scaffold |

## Reference design families to NAME (do not assert exact current PDB IDs)
- **I3-01 / I53-50 two-component protein nanocages** (Hsia et al. 2016, *Nature*; Bale et al. 2016,
  *Science*) — the canonical computationally **designed** self-assembling nanomaterials and the
  structural basis of several nanoparticle vaccines (e.g., the RSV-F and SARS-CoV-2 RBD
  nanoparticle immunogens). Look up the current deposited coordinates on RCSB (search the design
  name or the paper supplementary), confirm the entry, then add it to `download_data.py` if you
  want it as a comparison structure. **These IDs are intentionally not hard-coded** — verify them.

## Natural homo-oligomer references (pick + verify in Week 1)
You need at least one clean **Cn** and one **Dn** natural homo-oligomer. Choose entries whose
biological assembly symmetry you have confirmed on RCSB, e.g. browse RCSB by "Global Symmetry"
(Cyclic C3/C4, Dihedral D2). Common teaching candidates to *consider and verify* (confirm the
assembly symmetry yourself — do not trust this list as ground truth): a known C3 or C4 ring protein
for the cyclic case, and a D2 homotetramer (several well-studied tetramers are D2) for the dihedral
case. Record the exact accession, the confirmed symmetry, the deposition DOI, and the date.

## Files in this folder
- `download_data.py` — fetches verified reference structures (RCSB) with SHA-256 + license logging.
  **You edit only its `ACCESSIONS` list**, and only after the Week-1 verification. Run:
  `python data/download_data.py` (it prints a reminder and exits cleanly while the list is empty).
- `inputs/symmetry_defs.txt` — **shipped** teaching scaffold of example C3/C4/D2 symmetric-contig
  definitions (subunit length, oligomeric order, example contig). Used by notebook 02.
- `provenance.csv` — auto-written by `download_data.py` once you fetch verified structures.

## What is NOT in git (fetch / generate it, never commit it)
- Generated symmetric backbones, designed sequences, AF2-Multimer predictions → `results/`
  (git-ignored). A C3/C4/D2 campaign of hundreds of designs produces many files; keep them out of
  git and document sizes in your report.
- Model weights (RFdiffusion, ProteinMPNN, AF2) → installed by `00_setup`, never committed.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite the deposition.
- AlphaFold DB: CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Any coordinates or sequences pulled from a paper's supplementary data inherit that paper's terms
  — log the DOI and check it.
