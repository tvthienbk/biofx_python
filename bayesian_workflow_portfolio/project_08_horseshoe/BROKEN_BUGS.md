# Broken Notebook — Answer Key (Project 08)

`notebook_broken.ipynb` contains two seeded bugs matching this project's pitfalls:
a **centered horseshoe** (divergences) and **double-dipping** (selection bias).
This is the instructor key.

---

## Bug 1 — Centered horseshoe parameterization (the funnel)

**Code.**
```python
tau = pm.HalfCauchy('tau', beta=0.1)
lam = pm.HalfCauchy('lam', beta=1.0, shape=p)
beta = pm.Normal('beta', 0.0, tau * lam, shape=p)   # centered: beta tied to its scale
```

**Symptom.** A **flood of divergences** (often dozens to hundreds), high $\hat R$
on `tau` and the small coefficients, low ESS, and a mismatched `az.plot_energy`
diagnostic. The estimates are unreliable; the sampler is stuck.

**Why.** Sampling `beta` *directly* through its own scale `tau*lam` creates a
**pinched funnel**: when `tau` is small, the feasible region for `beta` collapses
to a needle that NUTS, with a single global step size, cannot traverse. It either
steps too far (diverges) or too short (gets stuck). This is the canonical
hierarchical-funnel pathology, here induced by the shrinkage scales.

**Diagnostic.**
- `int(idata.sample_stats['diverging'].sum())` is large.
- `az.plot_energy` shows the marginal-energy and energy-transition distributions
  disagree (poor exploration).
- The divergences cluster at small `tau` (visible in a `tau`-vs-`beta` scatter).

**Fix.** Use the **non-centered** parameterization (as `model.py` does by default):
```python
z = pm.Normal('z', 0.0, 1.0, shape=p)
beta = pm.Deterministic('beta', z * tau * lam_tilde)   # decoupled geometry
```
The standardized `z` is sampled in a fixed-scale space; the scale is applied
afterward, so NUTS sees benign geometry. Divergences drop to ~0.

---

## Bug 2 — Double-dipping / selection bias

**Code.**
```python
j_star = int(np.argmax(np.abs(bmean)))      # pick the biggest coefficient...
# ...then refit a SIMPLE regression on ONLY predictor j_star and report its
# narrow interval / 'p-value' as significance.
```

**Symptom.** The re-fit single-predictor slope has a deceptively **narrow credible
interval** that excludes zero, presented as strong evidence. It overstates
confidence.

**Why.** The predictor was **selected because it looked large in this sample**, and
then **tested on the same sample**. Using the data twice — once to choose, once to
test — is circular. Even pure-noise predictors will, by chance, produce one
"largest" coefficient that looks significant when re-tested in isolation. This is
selection bias / the winner's curse / double-dipping.

**Diagnostic.** Ask: *was the hypothesis (which predictor to test) chosen using the
same data used to test it?* If yes, the reported uncertainty is invalid. A
permutation/null check (shuffle `y`, repeat the select-then-test procedure, and
watch "significant" selected predictors appear from noise) makes the bias visible.

**Fix.** Do **not** select-then-refit. Let the **shrinkage prior perform selection
within one joint fit**, and report the full posterior over *all* coefficients,
including the posterior probability that each $|\beta_j|$ exceeds a threshold. The
joint fit already accounts for the multiplicity and the uncertainty about which
predictors are active. (If out-of-sample testing is needed, use a *held-out* set
that played no role in selection.)

---

## Meta-lesson

The two bugs are the two ways high-dimensional Bayesian regression goes wrong:
**computationally** (the shrinkage funnel demands non-centered sampling) and
**inferentially** (selecting and testing on the same data fakes significance). The
horseshoe addresses both: its non-centered form is samplable, and its joint
shrinkage replaces the dangerous select-then-test ritual with honest, simultaneous
selection-with-uncertainty.
