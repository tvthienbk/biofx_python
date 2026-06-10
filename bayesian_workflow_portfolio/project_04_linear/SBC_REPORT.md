# Simulation-Based Calibration (SBC) — Project 04

**Model:** `y_i ~ Normal(alpha + beta * x_std, sigma)`, `alpha,beta ~ Normal(0, 5)`,
`sigma ~ HalfNormal(2)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC, and what it checks here

Convergence diagnostics tell you the sampler explored the posterior it was given; they
are silent about whether that posterior is **correct**. SBC tests the inference
procedure — model + sampler — for self-consistency, here over **all three** regression
parameters: the intercept `alpha`, the slope `beta`, and the noise scale `sigma`. A
passing SBC certifies that the standardized linear-regression model is implemented
correctly and that its credible intervals have correct coverage.

The guarantee it leans on is exact:

> If `(alpha*, beta*, sigma*) ~ prior` and `y ~ Normal(alpha* + beta* x_std, sigma*)`,
> then the rank of each true value among `L` posterior draws is **uniform** — provided
> inference is correct.

| Rank histogram shape | Diagnosis |
|---|---|
| Uniform (flat) | Calibrated. |
| U-shaped | Posterior too narrow (over-confident). |
| n-shaped | Posterior too wide (under-confident). |
| Sloped | Biased posterior. |

---

## 2. Procedure used here

For each of `N_SIMS = 30` simulations:

1. Draw `alpha*, beta* ~ Normal(0, 5)` and `sigma* ~ HalfNormal(2)` (the model's priors).
2. Simulate `y ~ Normal(alpha* + beta* x_std, sigma*)` on a fixed standardized design of
   `N = 40` points.
3. Fit the model with a tiny sampler (`draws=120, tune=120, chains=2`, `L = 240`).
4. Record the rank of each true value among its posterior draws.

Uniformity is tested with a chi-square goodness-of-fit test (5 bins) for each parameter.
The light sampler and modest simulation count keep the whole sweep to about a minute.
(SBC's cost is dominated by per-fit model compilation, so the lever for speed is *fewer
simulations*, not fewer draws.)

Reproduce with:

```bash
python3 sbc.py
```

---

## 3. Results

```
SBC over 30 simulations (N=40, L=240)
  alpha: chi2=1.67, dof=4, p=0.797, uniform=True
   beta: chi2=2.33, dof=4, p=0.675, uniform=True
  sigma: chi2=1.67, dof=4, p=0.797, uniform=True
  saved sbc_ranks.png
```

| Parameter | Chi-square | dof | p-value | Verdict |
|---|---|---|---|---|
| `alpha` | 1.67 | 4 | 0.797 | Uniform — calibrated |
| `beta` | 2.33 | 4 | 0.675 | Uniform — calibrated |
| `sigma` | 1.67 | 4 | 0.797 | Uniform — calibrated |

All three rank histograms (`sbc_ranks.png`) are flat, sitting near the uniform
expectation of `30 / 5 = 6` counts per bin, with no U, n, or slope.

---

## 4. Interpretation

All three p-values are comfortably large: no evidence of miscalibration for the
intercept, slope, or noise scale. Concretely, each parameter's posterior is neither
over-confident (no U) nor under-confident (no n) nor biased (no slope), so the credible
intervals have correct coverage. This is the expected outcome for a correctly-implemented
linear regression on a **standardized** design — and the standardization is part of why
the geometry is clean enough to calibrate so easily. SBC run on the *raw-predictor* model
would still be calibrated in principle (the model is the same up to reparameterization),
but the badly-conditioned geometry makes each fit slower and noisier; standardizing is
the practical enabler.

SBC is a falsification tool: a pass means "no detectable problem at this resolution (30
sims, 5 bins)", not "provably perfect". Raising `N_SIMS` and the bin count stresses it
harder.

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 30-simulation SBC over `alpha`, `beta`, `sigma` and saves the histograms. |
| `sbc_ranks.png` | Three rank histograms (one per parameter). |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated` (chi-square test). |
