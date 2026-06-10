# BROKEN_BUGS.md — Project 12 (instructor answer key)

`notebook_broken.ipynb` reproduces this project's pitfall: **attenuation bias** from
ignoring predictor noise, plus a **latent-variable indexing bug** in a botched
errors-in-variables fix. Each seeded bug with symptom, diagnostic, and fix.

---

## Bug 1 — Naive regression on the noisy predictor (attenuation bias)

```python
pm.Normal('y', mu=alpha + beta * x_obs, sigma=sigma_y, observed=y)
```

**What is wrong.** Regressing `y` on the *observed* predictor `x_obs` ignores that
`x_obs = x* + noise`. Classical measurement error in a predictor **attenuates** the
slope: the estimate is multiplied by the reliability ratio
`lambda = var(x*) / (var(x*) + var(noise)) ≈ 0.74` here, pulling `beta` from the true
2.0 down to ~1.5. Crucially this is a **bias**, not noise — more data shrinks the
interval around the *wrong* value, making you more confident in a slope that is 25%
too small.

**Symptom.** The posterior slope sits near `beta_true * 0.74 ≈ 1.47`, far from the
known truth 2.0, with a tight, confident interval that *excludes* the truth.

**Diagnostic.**
- **Compare to known truth** (this is a simulation): the slope is systematically low.
- **The attenuation factor** `var(x*)/(var(x*)+tau_x^2)` predicts the bias exactly —
  printed by `data/generate_data.py`.
- **Prior sensitivity** (`prior_sensitivity.py`): the `tau_x = 0` row *is* the naive
  fit; increasing the assumed `tau_x` walks the slope back up toward 2.0.
- A good posterior-predictive fit to `y` does **not** clear the naive model — the
  bias is in the coefficient, not the fit to `y`.

**Fix.** Use the errors-in-variables model: introduce a latent `x_true` with a
population prior, add the measurement model `x_obs ~ Normal(x_true, tau_x)` (with
`tau_x` known from calibration), and write the structural model `y ~ Normal(alpha +
beta * x_true, sigma_y)`. The slope de-attenuates to ~2.0.

---

## Bug 2 — Latent-variable indexing bug in the EIV attempt

```python
x_true = pm.Normal('x_true', mu_x, sd_x, dims='obs')
pm.Normal('x_obs', mu=x_true,      sigma=tau_x, observed=x_obs)   # OK
pm.Normal('y', mu=alpha + beta * x_true[::-1], sigma=sigma_y, observed=y)  # BUG
```

**What is wrong.** The latent `x_true` must line up **row-for-row** with both `x_obs`
(the measurement model) and `y` (the structural model): `x_true[i]` is the true
predictor for observation `i`. Reversing it (`x_true[::-1]`) pairs each `y_i` with the
*wrong* unit's latent predictor, destroying the relationship. The model still runs
(shapes match), so there is no error — just a silently broken fit.

**Symptom.** The slope `beta` collapses toward 0 (the shuffled pairing has no linear
relationship), and the fit is poor. No exception is raised — this is the insidious
kind of bug.

**Diagnostic.**
- **Slope near 0** despite a correctly-specified-looking EIV model — a red flag that
  the latent and the data are misaligned.
- **Sanity-check the alignment:** the same index must drive `x_obs`, `y`, and
  `x_true`. Print shapes and, in a controllable test, check that `x_true`'s posterior
  mean tracks `x_obs` (it should, since the measurement model ties them).

**Fix.** Use `x_true` in natural order in the structural model:
`mu=alpha + beta * x_true` (no `[::-1]`). The measurement and structural models then
share the same indexing, and the slope is recovered.

---

## How the fix is demonstrated

The final cell calls `model.fit(data, model='eiv', ...)` — the correctly-aligned EIV
model — and prints a slope posterior near 2.0, covering the truth. Side by side with
Bug 1's ~1.5 and Bug 2's ~0, it shows that *both* a correct model structure (latent
predictor) *and* correct indexing are needed.

---

## Teaching note — measurement error is a modeling problem, not a data problem

The instinct on seeing a noisy predictor is "collect more data". That does not help:
attenuation is a bias that persists at any sample size. The cure is a *model* that
represents the noise — a latent true variable plus a measurement model — together
with a calibrated noise SD. And once you introduce latent variables indexed per
observation, alignment bugs become a new hazard class: always verify the latent
vector shares the observations' indexing.
