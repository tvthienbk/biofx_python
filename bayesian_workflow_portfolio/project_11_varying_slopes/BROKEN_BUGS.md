# BROKEN_BUGS.md — Project 11 (instructor answer key)

`notebook_broken.ipynb` reproduces this project's pitfall: **ignoring the
intercept-slope correlation** by modeling the random effects as independent
(diagonal covariance, no LKJ) — the headline bug — compounded by the **inferior
centered** parameterization. Each seeded issue with symptom, diagnostic, and fix.

> **Note on Bug 2's severity for this dataset.** Unlike Projects 09–10, the funnel
> here is *mild*: the random-effect SDs are moderate (`sd_a=0.8, sd_b=0.5`) and each
> line has 10 observations, so the per-line effects are well-informed and the
> sampler never enters the small-SD neck. Empirically the centered model samples
> with ~0 divergences and healthy ESS on this DGP. Bug 2 is therefore a *fragility /
> wrong-default* lesson, not a live divergence demo — non-centering is still the
> correct choice, and it is what makes the model robust when the geometry sharpens
> (smaller SDs or fewer observations, as in Projects 09–10). The broken notebook
> says so explicitly rather than pretending divergences occur. **Bug 1 is the real,
> robust seeded error.**

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

## Bug 2 — Centered parameterization (inferior, funnel-prone)

```python
alpha = pm.Normal('alpha', mu_a, sd_a, dims='group')   # centered
beta  = pm.Normal('beta',  mu_b, sd_b, dims='group')   # centered
```

**What is wrong.** Each effect's spread *is* its SD, so the same Neal's-funnel
geometry as Projects 09–10 is latent here — now in two dimensions. It is the wrong
default for a hierarchical scale model.

**Severity here.** For *this* DGP the funnel is mild: with moderate SDs and 10
observations per line the sampler does **not** enter the small-SD neck, so the
centered model samples with ~0 divergences and healthy ESS (`r_hat ≈ 1.00`). Do not
claim divergences that do not occur. The lesson is *fragility*: lower the SDs or the
per-line count (toward the Projects 09–10 regime) and this same centered form
funnels and diverges. At `target_accept` well below the default (e.g. 0.7) even this
mild geometry begins to throw divergences — evidence the neck is there, just not
visited under the default step size.

**Symptom.** None alarming on this dataset (that is the trap — a fragile
parameterization that *looks* fine until the geometry sharpens). Read the energy
plot to confirm BFMI is healthy here.

**Diagnostic.**
- **Divergence count** — ~0 here; would be > 0 with smaller SDs / fewer obs.
- **Energy plot** (`az.plot_energy`): marginal/transition match here (healthy BFMI);
  a mismatch would be the funnel fingerprint.

**Fix.** Non-center regardless: draw standard-normal `z` (shape `2 x G`) and set
`effects = mu + (L @ z).T` where `L` is the Cholesky factor from `LKJCholeskyCov`.
This is the geometry-robust default and keeps divergences at ~0 even when the
centered form would fail.

---

## How the fix is demonstrated

The final cell calls `model.fit(data, correlated=True, ...)` — the LKJ,
non-centered model — and prints `divergences after fix: 0` and a posterior for
`rho` whose interval covers the true 0.6. The headline change is structural: the
broken model had **no `rho`** (correlation assumed away), the fixed model **recovers
`rho ≈ 0.6`**. The parameterization change (centered → non-centered) is the
geometry-robust default; on this mild DGP both forms reach ~0 divergences, but only
the non-centered form stays safe when the SDs shrink or the data thin.

---

## Teaching note — "independent random effects" is a modeling assumption

Adding a varying slope is not enough; the *default* of independent intercept and
slope is itself a strong, often wrong, assumption. Whenever you let two group-level
effects vary, ask whether they plausibly co-vary — and if so, model the correlation
with LKJ rather than assuming it away. The cost is one shape parameter `eta`; the
benefit is correct predictive covariance for new groups.
