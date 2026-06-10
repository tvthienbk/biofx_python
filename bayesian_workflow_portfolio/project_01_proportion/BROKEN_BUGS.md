# Broken Notebook — Answer Key (Project 01)

`notebook_broken.ipynb` contains **three seeded bugs**. This is the instructor
answer key: for each bug we give the symptom you should observe, the diagnostic
that reveals it, and the fix. The clean reference is `notebook.ipynb`.

Students should run the broken notebook, read the diagnostics, and try to find all
three before reading this file.

---

## BUG 1 — A "flat" `Beta(1, 1)` prior that over-trusts extreme rates

**Where:** the model block.

```python
theta = pm.Beta('theta', alpha=1.0, beta=1.0)   # BUG 1
```

**The mistake.** `Beta(1, 1)` is uniform on `theta`, which *feels* like "no
assumptions". It is not. Uniform-on-the-probability says `theta = 0.999` is exactly
as plausible a priori as `theta = 0.5`. For a biochemical assay, near-certain
success or failure are extraordinary states, and a prior that treats them as
ordinary will — with little data — happily report a posterior mean near 0 or 1 from
a handful of lucky runs.

**Symptom.** With `n = 80` the symptom is subtle (the data dominate), but the bug
becomes glaring under the recommended stress test of shrinking `n`: with `n = 4`
and 4 successes, `Beta(1,1)` yields a posterior mean of `5/6 ≈ 0.83`, whereas the
weakly-informative `Beta(2,2)` gives `6/8 = 0.75` and the prior predictive spreads
implausible mass at the 0 and 1 edges.

**Diagnostic that reveals it.** The **prior predictive check** (Step 3 of the clean
notebook). Simulate the success count `k` implied by the prior. Under `Beta(1,1)`
the implied `k` is *uniform* over `0…n` — the prior asserts that "all 0 successes"
and "all n successes" are as likely as anything in between, which is clearly wrong
for an assay. Under `Beta(2,2)` the implied `k` concentrates mildly toward the
middle, which is sensible.

**Fix.**

```python
theta = pm.Beta('theta', alpha=2.0, beta=2.0)
```

Use a weakly-informative prior. The teaching point — "flat is not uninformative" —
is the single most transferable lesson in the project.

---

## BUG 2 — `tune=5, chains=1` starves NUTS and breaks the diagnostics

**Where:** the `pm.sample` call.

```python
idata = pm.sample(draws=1000, tune=5, chains=1, random_seed=RNG,
                  progressbar=False)   # BUG 2
```

**The mistake.** Two errors compounded:

1. `tune=5` gives NUTS only five steps to adapt its step size and mass matrix.
   Adaptation never finishes, so the sampler explores with a badly-tuned step size.
2. `chains=1` makes **split-R-hat uncomputable in its usual between-chain form** —
   R-hat compares variance *between* chains to variance *within* them, and with one
   chain there is nothing to compare. ESS is also unreliable from a single short,
   poorly-adapted chain.

**Symptom.** `az.summary` shows either `NaN`/missing `r_hat`, an `r_hat` that
cannot be trusted, and very low `ess_bulk`/`ess_tail`. You may also see tuning
warnings. The posterior *mean* might still look roughly right — which is the trap:
the failure shows up in the **diagnostics**, not necessarily in the point estimate.

**Diagnostic that reveals it.** Read the `az.summary` table (Step 5): look for
`r_hat` that is missing or > 1.01, and `ess_bulk`/`ess_tail` far below ~400. A
trace plot would show a single, poorly-mixed chain rather than the "fuzzy
caterpillar" of multiple overlapping chains.

**Fix.**

```python
idata = pm.sample(draws=1000, tune=1000, chains=4, random_seed=RNG,
                  progressbar=False)
```

Give NUTS adequate tuning and run ≥2 (ideally 4) chains so R-hat is meaningful.

---

## BUG 3 — Posterior predictive summed over the wrong dimension

**Where:** the posterior-predictive reduction.

```python
pp = idata.posterior_predictive['y']
pp_k = pp.sum(dim='draw').values.ravel()   # BUG 3
```

**The mistake.** `posterior_predictive['y']` is an xarray with dimensions
`(chain, draw, observation)`. To get a **predicted success count per replicated
dataset**, you must sum over the `observation` axis (each replicated dataset has
`n = 80` simulated 0/1 outcomes; their sum is the predicted `k`). Summing over
`draw` instead collapses across posterior samples and produces a quantity that is
*not* a predicted `k` at all — but it is a plausible-looking number, so the eye
does not catch it.

**Symptom.** The printed "predicted k mean" is wildly inconsistent with the
observed `k = 47` (e.g. of order hundreds or thousands, since it sums ~1000 draws),
yet there is **no error and no warning**. This is the most insidious of the three
bugs precisely because nothing crashes.

**Diagnostic that reveals it.** Print `pp.dims` and `pp.shape` *before* reducing.
You will see `('chain', 'draw', 'y_dim_2')` (or similar) — making it obvious that
the observation axis is the last one, not `draw`. Then sanity-check the magnitude:
a predicted `k` must lie in `[0, n] = [0, 80]`; anything outside that is impossible
and flags the wrong-axis reduction immediately.

**Fix.**

```python
pp = idata.posterior_predictive['y']
pp_k = pp.sum(dim=pp.dims[-1]).values.ravel()   # sum over the observation axis
```

Reduce over the last (observation) dimension. The defensive habit — *always print
`.dims`/`.shape` before reducing an xarray* — prevents this entire class of silent
error and recurs in every later project.

---

## Summary table

| Bug | Symptom | Diagnostic that reveals it | Fix |
|---|---|---|---|
| 1. `Beta(1,1)` flat prior | Over-trusts extreme rates (visible at small `n`) | Prior predictive check: implied `k` is uniform 0…n | Use `Beta(2,2)` |
| 2. `tune=5, chains=1` | Missing/untrustworthy R-hat, tiny ESS | `az.summary` R-hat & ESS columns; trace plot | `tune=1000, chains=4` |
| 3. Sum over `draw` | Predicted `k` impossibly large; no error | Print `pp.dims`/`.shape`; predicted `k` must be in [0, n] | Sum over `pp.dims[-1]` |
