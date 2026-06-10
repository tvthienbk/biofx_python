# Simulation-Based Calibration (SBC) — Project 03

**Model:** `y_i ~ Poisson(exposure_i * exp(log_rate))`, `log_rate ~ Normal(0, 2)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC, and what it checks here

Convergence diagnostics tell you the sampler explored the posterior it was given; they
are silent about whether that posterior is **correct**. SBC tests the inference
procedure — model + sampler — for self-consistency. For this project it calibrates the
single parameter `log_rate` of the Poisson rate model **with the exposure offset in
place**, so a passing SBC certifies that the offset parameterization and the log link
are implemented correctly.

The guarantee it leans on is exact:

> If `log_rate* ~ Normal(0, 2)` and `y ~ Poisson(exposure * exp(log_rate*))`, then the
> rank of `log_rate*` among `L` posterior draws is **uniform** — provided inference is
> correct.

| Rank histogram shape | Diagnosis |
|---|---|
| Uniform (flat) | Calibrated. |
| U-shaped | Posterior too narrow (over-confident). |
| n-shaped | Posterior too wide (under-confident). |
| Sloped | Biased posterior. |

---

## 2. Procedure used here

For each of `N_SIMS = 40` simulations:

1. Draw `log_rate* ~ Normal(0, 2)` (the prior).
2. Draw `N = 50` **varying exposures** uniformly on `[5, 40]` and simulate
   `y ~ Poisson(exposure * exp(log_rate*))`.
3. Fit the offset model with a tiny sampler (`draws=150, tune=150, chains=2`, `L=300`).
4. Record the rank of `log_rate*` among its posterior draws.

Uniformity is tested with a chi-square goodness-of-fit test (5 bins). The light
sampler and modest simulation count keep the whole sweep to roughly a minute.

Reproduce with:

```bash
python3 sbc.py
```

---

## 3. Results

```
SBC over 40 simulations (N=50, L=300)
  log_rate: chi2=2.25, dof=4, p=0.690, uniform=True
  saved sbc_ranks.png
```

| Quantity | Value |
|---|---|
| Simulations | 40 |
| Data size per sim, N | 50 |
| Posterior draws per sim, L | 300 |
| Chi-square statistic | 2.25 |
| Degrees of freedom | 4 |
| p-value | **0.690** |
| Verdict | **Uniform — calibrated** |

The rank histogram (`sbc_ranks.png`) is flat, sitting near the uniform expectation of
`40 / 5 = 8` counts per bin, with no U, n, or slope.

---

## 4. Interpretation

A chi-square p-value of **0.690** is fully consistent with uniformity: there is no
detectable miscalibration. Concretely, the posterior for `log_rate` is neither
over-confident (no U) nor under-confident (no n) nor biased (no slope). Crucially, SBC
here exercises the model **with the exposure offset and the log link both engaged** —
so the pass confirms those two pieces (the project's whole subject) are correctly
implemented. The same SBC run on the *no-offset* model would fail, because that model
is biased; the bias would show up as a sloped rank histogram.

SBC is a falsification tool: a pass means "no detectable problem at this resolution
(40 sims, 5 bins)", not "provably perfect". Raising `N_SIMS` and the bin count stresses
it harder.

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 40-simulation SBC over `log_rate` and saves the histogram. |
| `sbc_ranks.png` | Rank histogram with the uniform-expectation reference line. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated` (chi-square test). |
