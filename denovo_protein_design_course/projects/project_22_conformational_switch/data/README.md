# Project 22 — Data

This project's data is a small set of **reference switch / two-state structures** (so you know what
a real conformational change looks like) plus a hand-authored **two-state definition** that drives
the whole campaign. **The two backbones you actually design against are GENERATED in notebook 02 —
they are not downloaded.** Provenance is graded: every reference structure must carry its source.

## What you need to assemble
| Group | Count | Source | Purpose |
|-------|-------|--------|---------|
| De novo switch / two-state designs | 1–2 | RCSB (LOCKR family; a designed hinge/two-state protein) | the conceptual reference for "one chain, two states" |
| Natural conformational-change pair | 1 pair | RCSB (e.g. adenylate kinase open + closed) | a textbook two-state hinge — what a real switch looks like |
| LOV photoswitch reference | 1 | RCSB (a LOV-domain structure) | starting point for the light-switch (LOV) **stretch** task |
| Two-state definition | 1 | **you write** `data/inputs/two_state_def.txt` | the two states + trigger + success criteria your campaign is built around |

> **Why the accessions need verifying:** switch designs are deposited under varied names and entries
> are occasionally superseded. **Confirm every accession on RCSB in Week 1 before you rely on it.**

## Files in this folder
- `download_data.py` — fetches the *reference* structures (RCSB) with SHA-256 + license logging.
  **You edit its `ACCESSIONS` list.** Run: `python data/download_data.py` (see `--dry-run`).
- `inputs/two_state_def.txt` — the two-state definition **template you fill in** during Phase 0
  (Week 2): trigger, topology, state A / state B descriptions, the testable hypothesis, measurable
  success criteria, and the mandatory controls. Notebook 02 reads the topology + trigger from here.
- `provenance.csv` — auto-written by `download_data.py` for the fetched structures.

## Candidate accessions (all "candidate — verify on RCSB" before use)
These are starting points carried in `download_data.py`'s `ACCESSIONS`; **confirm each on RCSB and
substitute the current accession if superseded:**
- `6MSP` — **candidate — verify:** LOCKR-family de novo switch (Langan 2019). Confirm the exact
  LOCKR / Co-LOCKR accession on RCSB before use.
- `6X8N` — **candidate — verify:** a designed two-state / hinge-like protein (open vs closed).
- `1AKE` — **candidate — verify:** adenylate kinase **OPEN** state — classic natural two-state hinge.
- `4AKE` — **candidate — verify:** adenylate kinase **CLOSED** state — the partner of `1AKE`; the
  open/closed pair is a textbook two-state example.
- `2LV1` — **candidate — verify:** a LOV-domain / photoswitch reference for the LOV **stretch** task.

The two **designed** backbones (state A and state B) are produced by RFdiffusion in notebook 02 and
written to `results/two_state/state_A.pdb` and `results/two_state/state_B.pdb` — they are outputs,
not inputs, and (like all of `results/`) are kept out of git.

## Licenses (record in your thesis)
- RCSB PDB: public domain; cite each deposition.
- AlphaFold DB (if you fetch any predicted structures): CC-BY-4.0; cite Jumper 2021 + Varadi 2022.
- UniProt: CC-BY-4.0.
- Any switch sequences/coordinates you pull from a paper's supplementary data inherit that paper's
  terms — check and log each DOI.

## Size / git policy
Reference structures are small (a few MB total). **Do not commit** generated backbones, MPNN pools,
AF2 models, or MD trajectories — `download_data.py` fetches references on demand and notebook 02
regenerates the designs. Keep `results/` and large data out of git (see `MASTER_BLUEPRINT.md §6`).
