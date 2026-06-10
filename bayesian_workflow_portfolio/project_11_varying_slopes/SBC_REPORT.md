# Simulation-Based Calibration (SBC) — Project 11

**Model:** varying slopes with correlated random effects (LKJ), **non-centered**
`[alpha_g, beta_g] ~ MVNormal(mu, Sigma)`, `Sigma` via `LKJCholeskyCov(eta=2)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC here, and what we target

A varying-slopes model with an LKJ covariance has many ways to go subtly wrong: the
Cholesky-factor reconstruction, the `(chol, corr, sds)` unpacking, the non-centered
algebra. SBC tests the whole procedure for self-consistency — if parameters are
drawn from the prior and data simulated from them, each true value's rank among the
posterior draws must be uniform.

We target the **population means** `mu_a` (mean intercept) and `mu_b` (mean slope)
— what a varying-slopes analysis ultimately reports. We deliberately do **not** SBC
the correlation `rho`: with only G=8 lines it is loosely identified, and calibrating
it well would need far more (and more expensive) simulations. The LKJ model is the
slowest in the portfolio (no BLAS in this environment), so SBC is kept very light.

---

## 2. Procedure

For each of `N_SIMS = 10` simulations: draw `mu_a*, mu_b* ~ Normal(0,5)`,
random-effect SDs `~ HalfNormal(1)`, and a correlation from the LKJ(eta=2) prior
(`rho ~ 2*Beta(eta,eta)-1` for n=2); build the 2x2 covariance; draw
`[alpha_g, beta_g] ~ MVNormal`; simulate `y` for G=8 lines x 10 obs; refit the
correlated non-centered model with a small sampler (1 chain, 200 tune, L≈100
draws). Ranks are tested for uniformity with chi-square (`assert_calibrated`,
5 bins). Reproduce: `python3 sbc.py`.

---

## 3. Results

```
SBC over 10 simulations (G=8, n_per=10, L~100)
  mu_a: chi2=2.00, dof=4, p=0.736, uniform=True
  mu_b: chi2=2.00, dof=4, p=0.736, uniform=True
  saved sbc_ranks.png
```

| Parameter | chi2 | dof | p-value | Verdict |
|---|---|---|---|---|
| `mu_a` | 2.00 | 4 | 0.736 | Uniform |
| `mu_b` | 2.00 | 4 | 0.736 | Uniform |

Both rank histograms are consistent with uniformity.

---

## 4. Interpretation

The non-centered LKJ model is **calibrated** for the two population means at this
(deliberately coarse) resolution. With only 10 simulations and 5 bins this is a weak
test — it can catch a gross calibration failure (a strong slope or `U`/`∩` shape) but
not a subtle one. The honest reading is "no detectable miscalibration in the
population means", and that is the realistic ceiling for SBC on a model this
expensive to refit.

This is a deliberate teaching point: **SBC is not free**, and for costly
multivariate hierarchical models you trade resolution for feasibility. The recovery
test (`test_recovery.py`) provides the complementary check on a single known-truth
dataset — including that `rho`'s interval covers the truth — while SBC checks the
*procedure* on the parameters it can afford to.

To stress it further (offline), raise `N_SIMS`, add `rho` as a target, or refit with
the **centered** parameterization and confirm the ranks distort.

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the light LKJ SBC and saves the histograms. |
| `sbc_ranks.png` | Rank histograms for `mu_a`, `mu_b`. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated`. |
