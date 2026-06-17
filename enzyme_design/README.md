# `enzyme_design` — computational toolkit for the *de novo* enzyme-design protocol

This directory operationalizes the **computational half (Stages 1–6)** of the
*Nature Protocols*-style document
*“Deep-learning–based de novo design of enzymes.”*

The heavy GPU models named in the protocol — **RFdiffusion(AA/2/3)**,
**LigandMPNN**, **AlphaFold/ColabFold**, **PLACER/ChemNet** — cannot run without
their weights, containers, and a ≥24 GB GPU. What *can* be made reproducible,
testable, and correct is the **glue around them**: building their inputs,
emitting their exact commands, and processing their outputs into a ranked,
diversity-aware experimental panel. That is what this package is.

> Scope note: this is an engineering scaffold + filtering/ranking logic, **not**
> a replacement for the generative models. Where a step requires a model, the
> toolkit builds and *validates* the command/input instead of executing it.

## What maps to which protocol stage

| Protocol stage | Module | What it does |
|---|---|---|
| 1 — Theozyme | `theozyme.py` | Build / serialise / parse Rosetta `enzdes` `.cst` catalytic constraints |
| 2 — Inputs (contig) | `contig.py` | Parse/build/**validate** RFdiffusion contigs (bare-integer & length guards) |
| 3 — Backbone gen | `pipeline.py` → `RFdiffusionAAJob` | Validated RFdiffusionAA command line |
| 4 — Sequence design | `pipeline.py` → `LigandMPNNJob` | Validated LigandMPNN command; enforces *catalytic residues fixed* |
| 5a — Self-consistency | `metrics.py`, `geometry.py` | AF2/AF3 metric thresholds; Kabsch motif Cα-/ligand-RMSD |
| 5b — Preorganization | `preorg.py` | Whole-reaction-coordinate scoring, **ranked by worst step** |
| 5c/14 — Rank & diversify | `selection.py` | Combined ranking + greedy per-cluster diverse panel |
| 6 — Order genes | `registry.py` | Construct registry, pre-synthesis checks, CSV archive |

## Layout

```
enzyme_design/
  enzyme_design/        the package (8 modules, pure-Python + numpy)
  tests/                pytest suite (68 tests)
  examples/             tiny synthetic inputs (active-site PDB, theozyme.cst, metrics, ensembles)
  notebooks/            5 runnable .ipynb demos/tests (+ generator script)
  environment.yml       full-protocol conda template (pin commit hashes!)
  requirements.txt      toolkit runtime + dev deps
  PROTOCOL_REVIEW.md    correctness review of the source protocol
```

## Quick start

```bash
pip install -r requirements.txt
pytest -q                       # 68 tests
cd notebooks
python _build_notebooks.py      # (re)generate the notebooks from source
jupyter lab                     # open 00_end_to_end_overview.ipynb
```

## The one idea worth keeping

The protocol’s central, experimentally-supported claim is that catalytic success
tracks **active-site preorganization across the *entire* reaction coordinate**,
not a single transition state. `preorg.py` encodes this literally: a design is
ranked by its **worst mechanistic step** (`PreorgProfile.worst_score`), so a
candidate that is excellent on average but collapses at one intermediate is
correctly demoted — see `design_0004` in the example data and notebook 03.
