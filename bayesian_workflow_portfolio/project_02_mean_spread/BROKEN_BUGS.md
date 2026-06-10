# Broken Notebook — Answer Key (Project 02)

`notebook_broken.ipynb` contains **three seeded bugs**, all centred on this project's
pitfall: priors and parameterization of a *scale*. This is the instructor answer key:
for each bug we give the symptom, the diagnostic that reveals it, and the fix. The
clean reference is `notebook.ipynb`.

---

## BUG 1 — An improper "flat" prior on `sigma`

**Where:** the model block.

```python
sigma = pm.Uniform('sigma', lower=0.0, upper=1e6)   # BUG 1
```

**The mistake.** A `Uniform(0, 1e6)` is a stand-in for the "flat/improper" scale prior
that beginners reach for thinking it is uninformative. It is the opposite: it places
essentially all of its prior mass on enormous values of `sigma` (the interval
`[0, 10]` is one part in 100,000 of the total range). It asserts, a priori, that a
measurement noise of 500,000 mg/mL is overwhelmingly more plausible than 1 mg/mL —
absurd for any real assay.

**Symptom.** The posterior for `sigma` can be pulled high and develop a heavy right
tail; ESS for `sigma` drops and you may see warnings or divergences. Crucially, the
**prior predictive check** would show simulated datasets with astronomically large
spread — the visual tell of an improper scale prior. (In this particular dataset the
30 informative points partly rescue the fit, which is itself the lesson: do not rely
on the data to bail out a broken prior — at small `N` it will not.)

**Diagnostic that reveals it.** (1) A **prior predictive check**: simulate datasets
from the prior and look at their spread — it will span many orders of magnitude. (2)
The `az.summary` ESS column for `sigma`, which degrades relative to a proper prior.

**Fix.**

```python
sigma = pm.HalfNormal('sigma', sigma=5.0)
```

Use a **proper** scale prior. `HalfNormal`, `Exponential`, and `HalfCauchy` are all
defensible (see `PRIOR_SENSITIVITY.md`); an unbounded uniform is not.

---

## BUG 2 — Passing a **variance** where a **standard deviation** is expected

**Where:** the likelihood.

```python
variance = sigma ** 2
pm.Normal('y', mu=mu, sigma=variance, observed=y)   # BUG 2: variance, not sd
```

**The mistake.** PyMC's `pm.Normal` takes `sigma` = the **standard deviation**, not the
variance. Passing `sigma**2` silently changes the scale of the likelihood. If the true
SD is ~1.2, the code tells the model the SD is ~1.44 (and the relationship is
nonlinear, so the error grows for larger `sigma`). This is one of the most common
distribution-parameterization bugs in all of applied Bayes.

**Symptom.** The recovered `sigma` is biased — it settles at a value that, when you
remember it is being squared into the likelihood, is inconsistent with the observed
spread. The recovery test would fail: the posterior for `sigma` no longer brackets the
known truth of 1.2. Posterior predictive spread will not match the data.

**Diagnostic that reveals it.** A **posterior predictive check** on the spread: the
replicated datasets' SD will systematically mismatch the observed SD. A **recovery
check** against the known `sigma_true = 1.2` flags it immediately. Reading the
docstring / signature of `pm.Normal` (sigma = SD) is the root-cause fix.

**Fix.**

```python
pm.Normal('y', mu=mu, sigma=sigma, observed=y)   # pass the SD directly
```

Pass `sigma` (the SD) directly. If you genuinely want to parameterize by variance, use
`pm.Normal('y', mu=mu, sigma=pm.math.sqrt(variance), ...)` — but know which one the API
expects.

---

## BUG 3 — Posterior predictive spread reduced over the wrong axis

**Where:** the posterior-predictive reduction.

```python
pp = idata.posterior_predictive['y']
pp_sd = pp.std(dim='draw').values.ravel()   # BUG 3
```

**The mistake.** `posterior_predictive['y']` has dims `(chain, draw, observation)`. To
get the spread of each *replicated dataset* you must take the standard deviation over
the **observation** axis. Taking `std` over `draw` instead computes the variability of
each observation slot *across posterior samples* — a completely different, meaningless
quantity for a per-dataset spread.

**Symptom.** The printed "predicted sd mean" is inconsistent with the observed SD
(~1.39) and does not behave like a dataset spread, yet there is **no error and no
warning**. The silent class of bug.

**Diagnostic that reveals it.** Print `pp.dims` and `pp.shape` *before* reducing; the
observation axis is the non-`(chain, draw)` one. Sanity-check the magnitude against the
observed SD — a per-dataset predicted SD should hover near 1.39, not somewhere
unrelated.

**Fix.**

```python
pp = idata.posterior_predictive['y']
obs_dim = [d for d in pp.dims if d not in ('chain', 'draw')][0]
pp_sd = pp.std(dim=obs_dim).values.ravel()   # std over the OBSERVATION axis
```

Reduce over the observation axis. As always: print `.dims`/`.shape` before reducing an
xarray.

---

## Summary table

| Bug | Symptom | Diagnostic that reveals it | Fix |
|---|---|---|---|
| 1. Improper flat `sigma` prior | Heavy-tailed/biased `sigma`, low ESS | Prior predictive spread spans orders of magnitude; ESS | Proper prior (`HalfNormal`) |
| 2. Variance passed as SD | `sigma` biased; recovery fails | PPC on spread mismatches; recovery vs known `sigma=1.2` | Pass `sigma` (the SD) directly |
| 3. `std` over `draw` | Predicted SD unrelated to observed; no error | Print `pp.dims`; predicted SD should be ~1.39 | Reduce over the observation axis |
