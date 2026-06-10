# BROKEN_BUGS.md — Project 18 (instructor answer key)

`notebook_broken.ipynb` seeds the canonical state-space failure mode: **process
vs observation noise confounding**, aggravated by a centred random walk. Don't
reveal this file until students have attempted the debug.

---

## Bug 1 — Vague variance priors let the two noises trade off

```python
sigma_level = pm.HalfNormal('sigma_level', sigma=10.0)   # BROKEN
sigma_obs   = pm.HalfNormal('sigma_obs',   sigma=10.0)   # BROKEN
```

- **Symptom.** Both variance posteriors are wide and **anti-correlated**; the
  inferred latent level either **chases every observation** (overfit: it absorbed
  the obs noise into the level) or **flattens** (oversmooth: it dumped real drift
  into obs noise). Recovered variances miss their truths.
- **Diagnostic.** The `(sigma_level, sigma_obs)` **pair plot** shows a strong
  negative-correlation banana — the model cannot decide drift vs noise.
- **Fix.** Informative priors: `HalfNormal(0.5)` for `sigma_level`,
  `HalfNormal(1.0)` for `sigma_obs` (as in `model.build_model`).

---

## Bug 2 — Centred random walk -> funnel and divergences

```python
level = pm.GaussianRandomWalk('level', sigma=sigma_level, shape=T, ...)   # BROKEN
```

- **Symptom.** Non-zero (often many) **divergences**, especially when
  `sigma_level` is small; poor ESS for `level` and `sigma_level`.
- **Diagnostic.** Divergence count > 0; a funnel in the joint of `sigma_level` and
  the level innovations (small `sigma_level` -> pinched neck).
- **Fix.** Use the **non-centred** parameterisation: standardised innovations
  `z ~ N(0,1)` scaled by `sigma_level` and cumulatively summed (as in `model.py`).

---

## Bug 3 — Stopping at the marginals / mis-reading the fit

A student may look at the marginal summaries (which can look plausible) and miss
that the *joint* posterior is a ridge, or accept an over/under-smoothed level
without comparing to the data scatter.

- **Symptom.** "Looks converged" from marginals while the level visibly overfits
  or oversmooths the data.
- **Diagnostic.** Plot the inferred level over the data: an overfit level passes
  through nearly every point; an oversmoothed one ignores genuine excursions.
  Combine with the `(sigma_level, sigma_obs)` pair plot.
- **Fix.** Always inspect the joint variance geometry **and** the level-vs-data
  overlay before trusting a state-space fit.

---

## Summary table

| Bug | Symptom | Diagnostic | Fix |
|---|---|---|---|
| 1. Vague variance priors | wide, anti-correlated variances; over/under-smooth | `(sigma_level,sigma_obs)` pair-plot banana | informative HalfNormal priors |
| 2. Centred random walk | divergences, funnel | divergence count, funnel geometry | non-centred RW |
| 3. Reading marginals only | "looks fine" but misfit | level-vs-data overlay + joint pair plot | inspect joint + trajectory |

Meta-lesson: in a state-space model, **identifiability of the two variances lives
in the priors and the data length**, and **the parameterisation (non-centred)
determines whether NUTS can sample it at all**.
