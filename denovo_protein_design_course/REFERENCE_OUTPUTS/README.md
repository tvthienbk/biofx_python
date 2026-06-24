# REFERENCE OUTPUTS — run these to check yourself

This folder holds **reference outputs** for all 25 projects, so you can confirm your environment
reproduces the expected results. For each project you get:

- `project_NN_slug/ALL_IN_ONE.executed.ipynb` — the project's combined notebook **executed**, with every
  cell's output and figure rendered inline. Open it and scroll.
- `project_NN_slug/results/` — the artifacts the notebooks emit (ranked CSVs, survival/breadth figures,
  validation plans, etc.).

## ⚠️ Read this first — what these outputs ARE and ARE NOT

These were produced on the **deterministic `mock` / `EXAMPLE_DATA` backend** that every project ships
with — **no GPU, no real tools** (BindCraft, RFdiffusion, RFantibody, AF2-Multimer, LigandMPNN, OpenMM,
Boltz, …). Therefore:

- ✅ **They ARE** a reference for the *plumbing*: the pipeline runs end-to-end, the shared filter is
  called correctly, the tables/figures are produced, and the numbers are **deterministic** (seeded).
- ✅ **They ARE** a reproducibility check: run the same notebooks on the mock backend and you should get
  the **same** numbers and figures. If yours differ, your environment, package versions, or the mock
  backend changed — investigate before trusting anything.
- ❌ **They are NOT real scientific results.** Every number here is **`EXAMPLE_DATA` / `SYNTHETIC`** by
  construction — no real pLDDT, pae_interaction, scRMSD, K_D, kcat, IC50, breadth, or hit rate. The
  *real* campaign runs the GPU tools on an A100 (see each project's `MANUAL.md §2`) and produces
  different, real data, which you then filter with the same shared pipeline.

This separation is deliberate and matches the course honesty policy (`MASTER_BLUEPRINT.md §9`):
*a computational design is a hypothesis, not a result; synthetic teaching data is always labeled and
never presented as a finding.*

## How to use these as a student
1. Run `00_setup.ipynb`, then `01 → 05` (or `ALL_IN_ONE.ipynb`) on the **mock backend** (the default).
2. Compare your notebook outputs and `results/` files against the matching folder here. They should match.
3. Once the plumbing is verified, switch the backends to the real tools on an A100 and run your *actual*
   campaign — those results will be new and are what your thesis reports (with full hit-rate accounting).

## How these were generated
`ALL_IN_ONE.ipynb` for each project was executed with `nbclient` (fresh kernel, mock backend, no GPU).
The canonical project notebooks in `projects/` remain **unexecuted** (empty outputs) — these executed
copies live only here. Regenerate with the course's reference-output script if tools/seeds change.
