# Build specification for one project (read this fully before writing anything)

You are building one or more **self-contained Bayesian-workflow teaching projects**.
The portfolio lives at `bayesian_workflow_portfolio/`. Shared helpers live in
`bayesian_workflow_portfolio/shared/`. Each project is a directory
`project_NN_slug/` (e.g. `project_01_proportion/`).

## Non-negotiable quality bar
- **Everything must run.** PyMC 5.28 + ArviZ 0.23 + numpy 2.x + scipy are installed.
- **Reproducible:** every random draw goes through a fixed seed. Synthetic data
  must have *known true parameters* that inference recovers within tolerance.
- **Notebooks are authored via `build_notebook.py`** using
  `from shared.nbbuild import NotebookBuilder`. NEVER hand-write `.ipynb` JSON.
  Running `python build_notebook.py` (from the project dir) writes
  `notebook.ipynb` and `notebook_broken.ipynb`.
- **Keep sampling light** so notebooks execute in well under a minute on CPU:
  use `draws=500, tune=500, chains=2` (4 chains only where diagnostics need it),
  small `N`, `progressbar=False`, and an explicit `random_seed`.
- Markdown cells must *teach*: state the assumption, the rationale, and how to
  read the result — not just label the code.

## Required files per project (exact names)
1. `README.md` — the **guideline**. Long-form (aim ~1,200–2,000 lines of real
   teaching content across the 8 workflow steps; this is the "~50pp" deliverable).
   Walk all 8 steps: (1) problem & data-generating story, (2) model spec with
   justified priors, (3) prior predictive checks, (4) inference/NUTS settings,
   (5) computational diagnostics (R-hat, ESS, divergences, energy) + what to do
   when they fail, (6) posterior predictive checks, (7) model criticism/comparison
   (LOO/WAIC where ≥2 models), (8) decision & communication. Flag every modeling
   assumption explicitly. Include a "common pitfalls" subsection tied to the
   project's key pitfall from the brief.
2. `data/generate_data.py` — documented data-generating process, fixed seed,
   writes `data/data.npz` (or `.csv`) and prints the true parameters. Importable:
   expose `def generate(seed=...) -> dict` returning arrays + `truth` dict.
3. `model.py` — standalone model decoupled from the notebook. Expose
   `def build_model(data) -> pm.Model` and `def fit(data, **kw) -> az.InferenceData`.
   Importable by the notebook, the test, SBC, and prior-sensitivity scripts.
4. `build_notebook.py` — emits `notebook.ipynb` (full clean workflow) **and**
   `notebook_broken.ipynb` (the debugging exercise) via `NotebookBuilder`.
   The clean notebook imports from `model.py`/`generate_data.py` where sensible,
   or inlines equivalent code — either way it must run top-to-bottom.
5. `lessons.md` — the **lessons report** (~300–500 lines): takeaways,
   failures/surprises encountered, and how to generalize the technique.
6. `sbc.py` + `SBC_REPORT.md` — Simulation-Based Calibration. `sbc.py` draws
   parameters from the prior, simulates data, refits, computes rank statistics
   (use `shared.bayes_utils.sbc_rank` / `assert_calibrated`), and saves a rank
   histogram + summary. Keep it light (e.g. 60–150 simulations, tiny sampler).
   `SBC_REPORT.md` explains the method, shows results, interprets uniformity.
7. `prior_sensitivity.py` + `PRIOR_SENSITIVITY.md` — refit under 2–3 prior
   choices (e.g. weakly-informative, vague, mildly-informative), compare
   posteriors; markdown interprets robustness.
8. `notebook_broken.ipynb` + `BROKEN_BUGS.md` — the broken notebook contains
   2–4 *seeded* bugs matching the project's pitfall (e.g. label-switching,
   non-identifiability, centered-vs-non-centered, ignored offset, forcing
   Poisson on overdispersed data). `BROKEN_BUGS.md` is the instructor answer key:
   each bug, its symptom, the diagnostic that reveals it, and the fix.
9. `rubric.md` — grading rubric tied to the 8 workflow steps (point allocation)
   **plus** one open-ended extension prompt.
10. `summary_onepager.md` — one-page **non-technical** summary translating the
    posterior into a concrete decision a collaborator can act on.
11. `test_recovery.py` — a minimal pytest: runs `generate_data.generate`, fits
    via `model.fit` with a light sampler, asserts known params recovered within
    tolerance using `shared.bayes_utils.check_recovery`. Must be fast (<60s).

A shared top-level `environment.yml` / `requirements.txt` already exists; do NOT
duplicate per project — reference it from the README.

## Importing shared helpers
Scripts run from the project directory. Add this preamble so `shared` is importable:
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.bayes_utils import check_recovery, rng, sbc_rank, assert_calibrated
```
In notebooks, the builder will inject an equivalent `sys.path` cell — make the
first code cell add the portfolio root to `sys.path`.

## Conventions
- Seeds: use `shared.bayes_utils.DEFAULT_SEED` or a per-project fixed int.
- Plots: ArviZ (`az.plot_trace`, `az.plot_energy`, `az.plot_ppc`, `az.plot_loo_pit`,
  `az.plot_forest`). Always `plt.tight_layout()`; never rely on a display backend
  (use `matplotlib`'s default Agg-safe calls; do not call `plt.show()` is fine).
- Diagnostics: always compute and print `az.summary` (r_hat, ess_bulk, ess_tail)
  and report divergences (`idata.sample_stats.diverging.sum()`).
- Model comparison: use `az.loo` / `az.compare` when the project defines ≥2 models.
- Keep imports at the top of each script; no bare `exec`/`eval`.

## Validation (the build runner will do this, but author defensively)
- Every code cell must be valid Python (the validator AST-compiles each cell).
- `python build_notebook.py` must succeed and write both notebooks.
- `python model.py` and `python data/generate_data.py` should run as `__main__`
  with a short self-test guarded by `if __name__ == "__main__":`.

Write production-quality, teaching-grade content. Prefer correctness and clear
Bayesian reasoning over cleverness.
