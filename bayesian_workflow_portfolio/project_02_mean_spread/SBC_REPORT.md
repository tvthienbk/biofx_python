# Simulation-Based Calibration (SBC) — Project 02

**Model:** `y_i ~ Normal(mu, sigma)`, `mu ~ Normal(5, 10)`, `sigma ~ HalfNormal(5)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC, and what it checks here

Convergence diagnostics (R-hat, ESS, divergences) tell you the sampler explored the
posterior it was given. They are silent about whether that posterior is the **correct**
one. SBC tests the inference *procedure* — model + sampler together — for
self-consistency, and in this project it does so for **two** parameters at once: the
location `mu` and the scale `sigma`.

The guarantee it leans on is exact:

> If `(mu*, sigma*) ~ prior` and `y ~ Normal(mu*, sigma*)`, then the rank of each true
> value among `L` posterior draws is **uniform** — provided inference is correct.

Any systematic departure from uniformity is a fingerprint:

| Rank histogram shape | Diagnosis |
|---|---|
| Uniform (flat) | Calibrated — what we want. |
| U-shaped | Posterior **too narrow** (over-confident). |
| n-shaped | Posterior **too wide** (under-confident). |
| Sloped | **Biased** posterior. |

Scale parameters are precisely where calibration most often fails (a too-permissive
prior over-widens the posterior; an improper one breaks it). Running SBC on `sigma`,
not just `mu`, is therefore the point of this report.

---

## 2. Procedure used here

For each of `N_SIMS = 35` simulations:

1. Draw `mu* ~ Normal(5, 10)` and `sigma* ~ HalfNormal(5)` (the model's priors).
2. Simulate `y ~ Normal(mu*, sigma*)` with `N = 30` observations.
3. Fit the model with a tiny sampler (`draws=120, tune=120, chains=2`, so `L = 240`).
4. Record the rank of `mu*` and of `sigma*` among their posterior draws
   (`shared.bayes_utils.sbc_rank`).

Uniformity is tested with a chi-square goodness-of-fit test
(`shared.bayes_utils.assert_calibrated`, 5 bins). The light sampler keeps the whole
sweep to about a minute. (SBC's cost is dominated by per-fit model compilation, so the
lever for speed is *fewer simulations*, not fewer draws.)

Reproduce with:

```bash
python3 sbc.py
```

---

## 3. Results

```
SBC over 35 simulations (N=30, L=240)
  mu   : chi2=2.00, dof=4, p=0.736, uniform=True
  sigma: chi2=3.14, dof=4, p=0.534, uniform=True
  saved sbc_ranks.png
```

| Parameter | Chi-square | dof | p-value | Verdict |
|---|---|---|---|---|
| `mu` | 2.00 | 4 | 0.736 | Uniform — calibrated |
| `sigma` | 3.14 | 4 | 0.534 | Uniform — calibrated |

Both rank histograms (`sbc_ranks.png`) are flat, sitting near the uniform expectation
of `35 / 5 = 7` counts per bin, with no U, n, or slope for either parameter.

---

## 4. Interpretation

Both p-values are comfortably large, so there is no evidence of miscalibration for
either parameter. Concretely:

- **`mu` is calibrated** — no surprise; locations are easy and the broad Normal prior
  is benign.
- **`sigma` is calibrated** — the more important result. The proper `HalfNormal(5)`
  prior yields a posterior for the scale that is neither too narrow (no U) nor too wide
  (no n), with correct interval coverage. This is exactly the calibration that an
  *improper* flat prior on `sigma` would destroy — which is why the broken notebook
  seeds that bug, and why we use a proper prior by default.

The modest `N_SIMS = 35` is chosen to keep the script fast; the test is a falsification
tool, so "uniform at this resolution" means "no detectable problem", not "provably
perfect". Raising `N_SIMS` and the bin count stresses it harder.

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 35-simulation SBC over `(mu, sigma)` and saves the histograms. |
| `sbc_ranks.png` | Side-by-side rank histograms for `mu` and `sigma`. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated` (chi-square test). |
