# Broken Notebook — Answer Key (Project 04)

`notebook_broken.ipynb` contains **three seeded bugs**, all centred on this project's
pitfall: un-scaled predictors and the priors and plots they break. This is the
instructor answer key: for each bug we give the symptom, the diagnostic that reveals it,
and the fix. The clean reference is `notebook.ipynb`.

---

## BUG 1 (headline) — Regressing on the raw, un-scaled predictor

**Where:** the model's linear predictor.

```python
mu = alpha + beta * x      # BUG 1: raw dose x (~100..600), not standardized
```

**The mistake.** The doses live on `[100, 600]`, far from zero. Regressing on raw `x`
causes three problems at once:

1. **A meaningless intercept.** `alpha` is now the response at `x = 0` — a wild
   extrapolation far outside the observed dose range. It no longer corresponds to
   anything in the data, and its prior is hard to reason about.
2. **A tiny, hard-to-prior slope.** The true raw slope is ~0.015. A prior width that is
   sensible for a slope of order 1 is absurd for a slope of order 0.01, and vice versa.
3. **A pathological posterior geometry.** Because `x` is far from zero, `alpha` and
   `beta` become **strongly correlated** (the line pivots around the data, so shifting
   the intercept must be compensated by shifting the slope). The posterior is a thin,
   tilted "banana" that NUTS samples inefficiently.

**Symptom.** The `alpha`-`beta` posterior correlation approaches 1; ESS for `alpha` and
`beta` collapses (often to a few dozen despite thousands of draws); you may see
divergences or step-size warnings. The point estimates can still be roughly right, but
the *efficiency* and *interpretability* are wrecked.

**Diagnostic that reveals it.** (1) `az.summary` ESS columns for `alpha`/`beta`, which
are far below the `sigma` ESS. (2) `az.plot_pair(idata, var_names=['alpha','beta'])`,
which shows the tight diagonal banana — the visual signature of correlated coefficients
from an un-centered predictor.

**Fix.**

```python
x_std = (x - x.mean()) / x.std()
mu = alpha + beta * x_std        # standardized predictor
```

Standardize the predictor (center and scale). The intercept becomes the response at the
*mean* dose (interpretable), the slope becomes the change per 1 SD of dose (O(1)), and
the `alpha`-`beta` correlation drops to near zero, fixing the geometry. Map the
coefficients back to the natural scale for reporting (see `model.to_natural`).

---

## BUG 2 — A prior width copied across scales without thinking

**Where:** the slope/intercept priors.

```python
alpha = pm.Normal('alpha', mu=0.0, sigma=0.5)   # BUG 2
beta  = pm.Normal('beta',  mu=0.0, sigma=0.5)
```

**The mistake.** A `Normal(0, 0.5)` prior is reasonable on a *standardized* scale (where
coefficients are O(1)) but is being applied here to the *raw* scale. On the raw scale the
true intercept is ~2 and lies near the edge of what `Normal(0, 0.5)` allows, while the
true slope is ~0.015 and is barely constrained — the same width means completely
different things on the two scales. The deeper lesson: **prior widths are not portable
across predictor scalings.** A width that regularizes gently on one scale can be
crushingly tight or uselessly loose on another.

**Symptom.** Combined with BUG 1, the intercept is pulled toward zero (fighting the
true ~2) and/or the slope is essentially unconstrained, biasing the natural-scale
estimates. On the raw scale the effect is entangled with BUG 1's geometry problem.

**Diagnostic that reveals it.** A **prior predictive check** on the raw scale: the lines
implied by `Normal(0, 0.5)` priors over raw `x ~ [100, 600]` sweep across an enormous
response range (because `beta * 600` is huge even for modest `beta`), revealing the
prior is not saying what you think. Comparing the implied response range to the observed
`y` range flags the mismatch.

**Fix.** Standardize first (BUG 1's fix), *then* use O(1) priors like `Normal(0, 5)`,
which are meaningful on the standardized scale. The fix for BUG 2 is inseparable from the
fix for BUG 1: standardize, then prior.

---

## BUG 3 — Overlaying the fitted line on the wrong x scale

**Where:** the posterior-predictive overlay plot.

```python
xs = np.linspace(data['x_std'].min(), data['x_std'].max(), 50)   # standardized grid
ax.scatter(x, y, ...)                                            # raw-x data
ax.plot(xs, a.mean() + b.mean()*xs, ...)                         # BUG 3: scale mismatch
```

**The mistake.** The data are plotted against **raw** `x`, but the fitted line is
evaluated on a **standardized** grid `xs`. The line and the data live on different
horizontal scales, so the line will not pass through the data cloud even when the fit is
correct. (And in the broken notebook the fit itself used raw `x`, compounding the
confusion.) This is the regression-specific cousin of the "wrong reduction axis" bug:
mixing scales in a plot.

**Symptom.** The fitted line visibly misses the data — it looks like a terrible fit — yet
the parameter estimates may be fine. The mismatch is in the *plot*, not (necessarily) the
*model*.

**Diagnostic that reveals it.** Check that the x-values of the data and of the line are
on the **same scale** before plotting. Print `x.min(), x.max()` and `xs.min(), xs.max()`
— if one is `[100, 600]` and the other is `[-2, 2]`, the scales are mismatched.

**Fix.** Plot both on the same scale. Either overlay on the standardized scale
(`ax.scatter(data['x_std'], y)` with the standardized line), or map the line back to raw
`x` before plotting:

```python
xs_raw = np.linspace(x.min(), x.max(), 50)
xs_std = (xs_raw - data['x_mean']) / data['x_sd']
ax.scatter(x, y)
ax.plot(xs_raw, a.mean() + b.mean() * xs_std)   # line evaluated at the matching std x
```

---

## Summary table

| Bug | Symptom | Diagnostic that reveals it | Fix |
|---|---|---|---|
| 1. Raw un-scaled predictor | `alpha`-`beta` corr ~ 1; ESS collapse; banana posterior | ESS columns; `plot_pair(alpha, beta)` | Standardize `x`; map back for reporting |
| 2. Prior width copied across scales | Intercept/slope mis-constrained; biased natural-scale fit | Prior predictive on raw scale sweeps absurd response range | Standardize, then O(1) priors |
| 3. Line plotted on the wrong x scale | Fitted line misses the data cloud despite a fine fit | Compare `x` range vs `xs` range | Plot data and line on the same scale |
