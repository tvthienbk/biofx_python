# Broken Notebook — Answer Key (Project 03)

`notebook_broken.ipynb` contains **three seeded bugs**. The headline bug is the one
this whole project is about: an **omitted exposure offset**. This is the instructor
answer key: for each bug we give the symptom, the diagnostic that reveals it, and the
fix. The clean reference is `notebook.ipynb`.

---

## BUG 1 (headline) — The exposure offset is omitted

**Where:** the model's expected count.

```python
mu = rate                # BUG 1: no multiplication by exposure
pm.Poisson('y', mu=mu, observed=y)
```

**The mistake.** The data have **varying exposures** on `[5, 40]`. The correct model is
`y_i ~ Poisson(exposure_i * lambda)`: a sample with twice the exposure racks up twice
the expected count at the *same* underlying rate. Omitting the offset and fitting
`y_i ~ Poisson(lambda)` directly forces a single mean count to explain samples whose
exposures (and hence expected counts) differ tenfold. The fitted "rate" collapses onto
the **mean count per sample** (~7), which is nothing like the true rate per unit
exposure (~0.30). The estimate is biased by more than an order of magnitude.

**Symptom.** The recovered rate is ~7 (or `log_rate` ~ 1.94) instead of ~0.30
(`log_rate` ~ -1.2). The posterior is confidently, badly wrong — and confident, because
the sampler converges fine; the error is *structural*, not computational. R-hat and ESS
look healthy.

**Diagnostic that reveals it.** Two complementary checks:
1. **Plot count vs exposure** (Step 1 of the clean notebook). The clear upward trend —
   more exposure, more counts — is the visual signature that exposure must enter the
   model. A model that ignores it cannot reproduce that trend.
2. **A posterior predictive check stratified by exposure.** The no-offset model
   predicts the same count distribution for every sample regardless of exposure, so its
   replicates badly miss the high-exposure (high-count) and low-exposure (low-count)
   samples. The overall PPC also fails. A recovery check against the known
   `log_rate = -1.2` flags it immediately.

**Fix.**

```python
mu = exposure * rate     # scale the rate by each sample's exposure
```

Equivalently, on the log scale, add `log(exposure)` as a fixed offset:
`log(mu_i) = log(exposure_i) + log_rate`.

---

## BUG 2 — A flat prior placed directly on the positive rate (wrong scale)

**Where:** the prior.

```python
rate = pm.Uniform('rate', lower=0.0, upper=1e4)   # BUG 2
```

**The mistake.** Two problems in one line. First, it abandons the **log link**: instead
of a Normal prior on `log_rate` (which makes the rate positive and the prior symmetric
on the multiplicative scale), it puts a prior directly on the rate. Second, that prior
is a near-flat `Uniform(0, 1e4)`, which is effectively improper on a rate — it places
almost all of its mass on absurdly large rates (the plausible region below ~1 is one
ten-thousandth of the range). It is the same "flat is not uninformative" trap as the
earlier projects, now on a rate.

**Symptom.** Poorer sampling geometry (the rate scale is skewed and bounded, which NUTS
handles less gracefully than the unconstrained `log_rate`), and a prior that fights
small rates. Combined with BUG 1 the estimate is doubly off.

**Diagnostic that reveals it.** A **prior predictive check**: simulated total counts
under `Uniform(0, 1e4)` span absurd magnitudes (millions of events), flagging the
implausible prior. Comparing the parameterization to the clean model shows the missing
log link.

**Fix.**

```python
log_rate = pm.Normal('log_rate', mu=0.0, sigma=2.0)
rate = pm.math.exp(log_rate)
```

Put a Normal prior on the **log** rate and exponentiate. The rate is then positive by
construction and the prior is sensible and weakly-informative.

---

## BUG 3 — Total count summed over the wrong axis

**Where:** the posterior-predictive reduction.

```python
pp = idata.posterior_predictive['y']
pp_tot = pp.sum(dim='draw').values.ravel()   # BUG 3
```

**The mistake.** `posterior_predictive['y']` has dims `(chain, draw, observation)`. To
get the **total count per replicated dataset** you sum over the **observation** axis.
Summing over `draw` collapses across posterior samples instead, producing a meaningless
quantity that looks like a count but is not the per-dataset total.

**Symptom.** The printed "predicted total mean" is inconsistent with the observed total
(350) and raises no error — the silent class of bug.

**Diagnostic that reveals it.** Print `pp.dims`/`pp.shape` before reducing; the
observation axis is the non-`(chain, draw)` one. Sanity-check the magnitude against the
observed total of 350.

**Fix.**

```python
pp = idata.posterior_predictive['y']
obs_dim = [d for d in pp.dims if d not in ('chain', 'draw')][0]
pp_tot = pp.sum(dim=obs_dim).values.ravel()   # sum over the OBSERVATION axis
```

---

## Summary table

| Bug | Symptom | Diagnostic that reveals it | Fix |
|---|---|---|---|
| 1. Omitted exposure offset | Rate ~ mean count (~7), not ~0.30; biased ~10x | Count-vs-exposure trend; exposure-stratified PPC; recovery | `mu = exposure * rate` |
| 2. Flat prior on the rate (no log link) | Skewed geometry; prior fights small rates | Prior predictive spans absurd totals | `Normal` prior on `log_rate`, then `exp` |
| 3. Sum over `draw` | Predicted total unrelated to observed 350; no error | Print `pp.dims`; total should be ~350 | Sum over the observation axis |
