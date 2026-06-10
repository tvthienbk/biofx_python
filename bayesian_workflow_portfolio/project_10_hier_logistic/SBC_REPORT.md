# Simulation-Based Calibration (SBC) — Project 10

**Model:** hierarchical logistic, **non-centered**
`y_i ~ Bernoulli(logit^{-1}(alpha_{g[i]} + beta*x_i))`, `alpha_g = mu + tau*z_g`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC here

R-hat/ESS/divergences certify the sampler explored its posterior; they do not
certify that posterior is correct. A hierarchical GLM can go wrong in quiet ways —
a centered/non-centered slip, a mis-scaled prior on the log-odds, an indexing bug
on `group`. SBC tests the whole procedure for self-consistency: if parameters are
drawn from the prior and data simulated from them, the rank of each true value
among the posterior draws must be uniform.

We target the **population-level** parameters `mu`, `tau`, and the global slope
`beta` — exactly what a hierarchical GLM reports.

---

## 2. Procedure

For each of `N_SIMS = 40` simulations: draw `mu* ~ Normal(0,1.5)`,
`tau* ~ HalfNormal(1)`, `beta* ~ Normal(0,1.5)`; draw `alpha_g ~ Normal(mu*,tau*)`;
simulate Bernoulli `y` for G=10 families x 12 obs; refit the non-centered model
(1 chain, 400 tune, L≈200 draws, `target_accept=0.95`); record ranks. Uniformity
tested with chi-square (`assert_calibrated`, 10 bins). Light by design —
hierarchical SBC is expensive. Reproduce: `python3 sbc.py`.

---

## 3. Results

```
SBC over 40 simulations (G=10, n_per=12, L~200)
  mu:   chi2=14.50, dof=9, p=0.106, uniform=True
  tau:  chi2=3.00,  dof=9, p=0.964, uniform=True
  beta: chi2=15.00, dof=9, p=0.091, uniform=True
```

| Parameter | chi2 | dof | p-value | Verdict |
|---|---|---|---|---|
| `mu`   | 14.50 | 9 | 0.106 | Uniform |
| `tau`  | 3.00  | 9 | 0.964 | Uniform |
| `beta` | 15.00 | 9 | 0.091 | Uniform |

All three histograms are consistent with uniformity at alpha=0.01: no `U` (over-
confidence), no inverted-`U` (under-confidence), no slope (bias).

---

## 4. Interpretation

The non-centered hierarchical logistic is **calibrated** for all three population
parameters. `tau`'s near-perfect uniformity (p=0.964) is the reassuring result: the
parameter most exposed to the funnel shows no calibration defect once non-centered.
`mu` and `beta` sit lower (0.106, 0.091) but comfortably above the 0.01 gate; with
40 sims and 10 bins the test has limited power and such fluctuations are expected.

SBC falsifies, it does not certify — "no detectable miscalibration at this
resolution" is the honest reading. To stress it, raise `N_SIMS`, or deliberately
refit with the centered parameterization and an over-tight `tau` prior and watch
the ranks for `tau` skew (the over-pooling bias made visible).

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 40-simulation hierarchical-logistic SBC and saves histograms. |
| `sbc_ranks.png` | Rank histograms for `mu`, `tau`, `beta`. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated`. |
