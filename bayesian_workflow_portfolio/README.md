# A 20-Project Portfolio for Mastering the Bayesian Workflow

A self-contained teaching portfolio that takes a student from beginner to
confident practitioner of the **full Bayesian workflow**, using **Python +
PyMC + ArviZ**. Projects are sequenced simplest → hardest; each later project
assumes the skills of the earlier ones.

## The workflow every project walks through

1. **Problem & data-generating story** — the scientific question and assumed mechanism.
2. **Model specification** — likelihood + *justified* priors (never defaults-by-habit).
3. **Prior predictive checks** — confirm priors imply sensible data *before* seeing data.
4. **Inference** — NUTS sampling with settings explained.
5. **Computational diagnostics** — R-hat, ESS, divergences, trace/energy; and the fixes.
6. **Posterior predictive checks** — does the fit reproduce key data features?
7. **Model criticism & comparison** — LOO/WAIC, sensitivity, alternatives.
8. **Decision & communication** — turn the posterior into an actionable conclusion.

## Master index

| #  | Directory | Title | Model family | Difficulty |
|----|-----------|-------|--------------|------------|
| 1  | `project_01_proportion`        | Estimating a proportion        | Beta–Binomial            | ★ |
| 2  | `project_02_mean_spread`       | Estimating a mean & spread     | Normal (μ, σ)            | ★ |
| 3  | `project_03_rate`              | Estimating a rate              | Poisson                  | ★ |
| 4  | `project_04_linear`            | Simple linear regression       | Linear                   | ★ |
| 5  | `project_05_logistic`          | Binary outcomes                | Logistic GLM             | ★★ |
| 6  | `project_06_negbinom`          | Overdispersed counts           | Neg-Binomial GLM         | ★★ |
| 7  | `project_07_robust`            | Robust regression              | Student-t                | ★★ |
| 8  | `project_08_horseshoe`         | Many predictors                | Regularized GLM          | ★★ |
| 9  | `project_09_partial_pooling`   | Partial pooling                | Hierarchical means       | ★★★ |
| 10 | `project_10_hier_logistic`     | Varying intercepts             | Hierarchical logistic    | ★★★ |
| 11 | `project_11_varying_slopes`    | Varying slopes                 | Hierarchical + LKJ       | ★★★ |
| 12 | `project_12_errors_in_vars`    | Errors-in-variables            | Measurement-error        | ★★★ |
| 13 | `project_13_mixture`           | Subpopulations                 | Finite mixture           | ★★★★ |
| 14 | `project_14_hmm`               | State switching over time      | Hidden Markov            | ★★★★ |
| 15 | `project_15_ppca`              | Latent dimensions              | Probabilistic PCA        | ★★★★ |
| 16 | `project_16_changepoint`       | Detecting a shift              | Change-point             | ★★★★ |
| 17 | `project_17_gp`                | Nonparametric curves           | Gaussian process         | ★★★★★ |
| 18 | `project_18_state_space`       | Dynamics & drift               | State-space / AR         | ★★★★★ |
| 19 | `project_19_ode`               | Mechanistic model              | Bayesian ODE             | ★★★★★ |
| 20 | `project_20_capstone`          | Decision under uncertainty     | Hierarchical + decision  | ★★★★★ |

## Deliverables in every project

Each `project_NN_*/` directory contains:

- `README.md` — full **guideline** across all 8 workflow steps (the long-form deliverable).
- `data/generate_data.py` — documented, seeded data-generating process (true params recoverable).
- `model.py` — standalone model (`build_model`, `fit`) decoupled from the notebook.
- `build_notebook.py` → `notebook.ipynb` — the end-to-end runnable notebook.
- `notebook_broken.ipynb` + `BROKEN_BUGS.md` — seeded-bug **debugging exercise** + answer key.
- `lessons.md` — **lessons report** (takeaways, surprises, generalization).
- `sbc.py` + `SBC_REPORT.md` — **Simulation-Based Calibration** (correctness, not just convergence).
- `prior_sensitivity.py` + `PRIOR_SENSITIVITY.md` — posteriors across 2–3 prior choices.
- `rubric.md` — grading rubric tied to the workflow + an extension prompt.
- `summary_onepager.md` — one-page **non-technical** decision summary.
- `test_recovery.py` — minimal test that data + inference recover known parameters.

## Quick start

```bash
# 1. Environment (pick one)
pip install -r requirements.txt
# conda env create -f environment.yml && conda activate bayes-workflow

# 2. Build all notebooks from their generator scripts and validate them
python build_all.py

# 3. Run a single project end-to-end
cd project_01_proportion
python data/generate_data.py     # synthesize data, print true params
python build_notebook.py         # emit notebook.ipynb + notebook_broken.ipynb
pytest test_recovery.py -q       # confirm inference recovers known params
jupyter lab notebook.ipynb       # work through the workflow

# 4. Validate notebooks only (CI gate: schema + per-cell syntax)
python shared/validate_notebooks.py
```

## Design choices

- **Notebooks are generated, not hand-written.** Each project ships a
  `build_notebook.py` that emits its `.ipynb` via `nbformat`. This guarantees
  valid notebook JSON and lets `python build_all.py` rebuild the entire
  portfolio reproducibly.
- **Synthetic data with known truth.** Where real data is unavailable, data is
  synthesized from a stated generative process with a fixed seed, so inference
  can be checked against the true parameters.
- **Correctness over convergence.** Every project includes Simulation-Based
  Calibration in addition to R-hat/ESS/divergence diagnostics.
- **Light sampling.** Defaults are small (`draws=500, tune=500, chains=2`) so the
  whole portfolio runs on a laptop CPU. Compute-heavier projects (#17–#20) note
  their requirements in their READMEs.

## Shared tooling (`shared/`)

- `nbbuild.py` — `NotebookBuilder` for authoring notebooks programmatically.
- `bayes_utils.py` — seeds, recovery checks, SBC rank statistics, calibration tests.
- `validate_notebooks.py` — schema + per-cell syntax validator (used by `build_all.py`).
- `AGENT_SPEC.md` — the build specification each project conforms to.
