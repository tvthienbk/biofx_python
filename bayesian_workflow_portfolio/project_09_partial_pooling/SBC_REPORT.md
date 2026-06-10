# Simulation-Based Calibration (SBC) — Project 09

**Model:** hierarchical Normal, **non-centered**
`y_ij ~ Normal(theta_j, sigma)`, `theta_j = mu + tau*z_j`, `z_j ~ Normal(0,1)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC here

Convergence diagnostics (R-hat, ESS, divergences) only tell us the sampler
explored the posterior it was handed. For a hierarchical model the more dangerous
question is whether that posterior is the *correct* one — a centered/non-centered
mistake, a mis-specified scale prior, or an indexing bug can converge cleanly to
the wrong distribution. SBC tests the whole inference procedure for
self-consistency.

> If `theta* ~ prior` and `y ~ likelihood(theta*)`, the rank of `theta*` among `L`
> posterior draws is **uniform** when inference is correct.

We target the **population-level** parameters `mu` (grand mean) and `tau`
(between-group SD), because those are what a partial-pooling analysis reports, and
because `tau` is precisely the parameter the funnel attacks — the one most worth
calibration-checking.

---

## 2. Procedure

For each of `N_SIMS = 40` simulations:

1. Draw `mu* ~ Normal(5,5)`, `tau* ~ HalfNormal(2)`, `sigma* ~ HalfNormal(2)`.
2. Draw `theta_j ~ Normal(mu*, tau*)` and simulate `y_ij ~ Normal(theta_j, sigma*)`
   for J=12 groups x 4 obs.
3. Refit the **non-centered** model with a tiny sampler (1 chain, 400 tune,
   `L≈200` draws, `target_accept=0.95`).
4. Record the rank of `mu*` and `tau*` among the posterior draws.

Uniformity is tested with a chi-square goodness-of-fit (`assert_calibrated`, 10
bins). The run is kept light deliberately — hierarchical SBC is expensive, and the
goal is to demonstrate the procedure and read the histogram, not certify to three
decimals. Reproduce with `python3 sbc.py`.

---

## 3. Results

```
SBC over 40 simulations (J=12, n_per=4, L~200)
  mu:  chi2=16.00, dof=9, p=0.067, uniform=True
  tau: chi2=8.00,  dof=9, p=0.534, uniform=True
  saved sbc_ranks.png
```

| Parameter | chi2 | dof | p-value | Verdict |
|---|---|---|---|---|
| `mu`  | 16.00 | 9 | 0.067 | Uniform (no rejection at alpha=0.01) |
| `tau` | 8.00  | 9 | 0.534 | Uniform |

Both rank histograms (`sbc_ranks.png`) are consistent with uniformity: no `U`
shape (would mean over-confident posteriors), no inverted-`U` (under-confident),
no slope (bias).

---

## 4. Interpretation

The non-centered model is **calibrated** for both population parameters at this
resolution. `tau` — the parameter most threatened by the funnel — is cleanly
uniform (p=0.534), which is the reassuring result: the non-centering has removed
the geometry problem rather than merely hiding it.

`mu`'s p-value (0.067) is lower but still well above the 0.01 threshold; with only
40 simulations and 10 bins the test has limited power and modest fluctuations are
expected. The honest reading is "no detectable miscalibration", not "proven
perfect" — SBC falsifies, it does not certify. To stress it harder, raise
`N_SIMS`, or deliberately refit with the **centered** parameterization at low
`target_accept` and watch `tau`'s ranks skew (the funnel's bias made visible).

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 40-simulation hierarchical SBC and saves the histograms. |
| `sbc_ranks.png` | Rank histograms for `mu` and `tau` with uniform reference lines. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated` (chi-square test). |
