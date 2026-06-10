# BROKEN_BUGS.md — Project 11 (instructor answer key)

`notebook_broken.ipynb` reproduces this project's pitfall: **ignoring the
intercept-slope correlation** by modeling the random effects as independent
(diagonal covariance, no LKJ), compounded by a **centered** parameterization that
diverges. Each seeded bug with symptom, diagnostic, and fix.

---

## Bug 1 — Independent intercept and slope (no correlation modeled)

```python
alpha = pm.Normal('alpha', mu_a, sd_a, dims='group')   # independent
beta  = pm.Normal('beta',  mu_b, sd_b, dims='group')   # independent
# (no LKJ, no off-diagonal covariance)
```

**What is wrong.** Giving `alpha_g` and `beta_g` separate, independent priors
hard-codes a **zero** intercept-slope correlation. The data were generated with
`rho = 0.6` (higher-baseline lines respond more steeply), so the model is
structurally unable to represent the truth. Worse, it has **no `rho` parameter at
all** — there is nothing to inspect, and a naive reader might not even notice the
correlation was assumed away.

**Symptom.**
- The model cannot report `rho`; `az.summary` has no correlation entry.
- Population SDs and means are roughly recovered, but the *predictive covariance*
  for a new cell line is wrong: it would generate `(alpha, beta)` pairs with zero
  correlation, mis-predicting the dose response of a new line.
- LOO is typically worse than the LKJ model (the independent model leaves
  structure unexplained).

**Diagnostic.**
- **Compare to the LKJ model with `az.compare`** (LOO): the correlated model wins.
- **Scatter the recovered `(alpha_g, beta_g)`:** the points show a tilt the model
  pretended did not exist. The model's *assumption* (independence), not the data,
  is the error.
- **Prior sensitivity / domain knowledge:** if you expect baseline and sensitivity
  to co-vary, an independence assumption is a red flag by construction.

**Fix.** Model the 2x2 covariance with `pm.LKJCholeskyCov(n=2, eta=2,
sd_dist=HalfNormal)`, which estimates the correlation. Now `rho` is recovered
(posterior covers the true 0.6) and predictions for new lines respect the tilt.

---

## Bug 2 — Centered parameterization (the funnel)

```python
alpha = pm.Normal('alpha', mu_a, sd_a, dims='group')   # centered
beta  = pm.Normal('beta',  mu_b, sd_b, dims='group')   # centered
```

**What is wrong.** Each effect's spread *is* its SD, so the same Neal's-funnel
geometry as Projects 09–10 appears — now in two dimensions. With `target_accept=
0.85` the sampler diverges in the necks.

**Symptom.** Non-zero divergences after tuning; depressed ESS for the SD
parameters; occasional `r_hat > 1.01`.

**Diagnostic.**
- **Divergence count** > 0.
- **Energy plot** (`az.plot_energy`): marginal/transition mismatch (low BFMI).

**Fix.** Non-center: draw standard-normal `z` (shape `2 x G`) and set
`effects = mu + (L @ z).T` where `L` is the Cholesky factor from `LKJCholeskyCov`.
Raise `target_accept` to 0.95. Divergences drop to ~0.

---

## How the fix is demonstrated

The final cell calls `model.fit(data, correlated=True, ...)` — the LKJ,
non-centered model — and prints `divergences after fix: 0` and a posterior for
`rho` whose interval covers the true 0.6. The same data, now with the *correct*
covariance structure and a benign geometry, both fits and samples cleanly.

---

## Teaching note — "independent random effects" is a modeling assumption

Adding a varying slope is not enough; the *default* of independent intercept and
slope is itself a strong, often wrong, assumption. Whenever you let two group-level
effects vary, ask whether they plausibly co-vary — and if so, model the correlation
with LKJ rather than assuming it away. The cost is one shape parameter `eta`; the
benefit is correct predictive covariance for new groups.
