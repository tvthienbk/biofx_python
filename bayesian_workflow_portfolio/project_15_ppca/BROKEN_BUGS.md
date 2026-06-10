# BROKEN_BUGS.md — instructor answer key (Project 15)

`notebook_broken.ipynb` seeds the PPCA pitfalls around rotational
non-identifiability. Students run it, read the diagnostics, fix each. Do not
reveal this file until afterward.

---

## Bug 1 — Over-specifying the number of factors (K=5 when truth is K=2)

**Where.** `K_WRONG = 5` in the model cell.

**Symptom.** The three surplus factors are non-identified. R-hat for `W` is large
and ESS tiny; the sampler may also slow down and occasionally diverge. Crucially,
the extra factors do **not** improve the fit — the reconstructed covariance is no
better than with K=2.

**Diagnostic that reveals it.**
- Reconstruction error vs K plateaus at K=2: K=5 buys nothing.
- `W`'s already-large R-hat gets worse; more parameters chase the same
  rotational/permutation freedom.
- LOO (`az.compare`) across K=1,2,3,5 does not prefer K=5 (often penalizes it).

**Fix.** Use `K=2` (the true latent dimension). In practice, choose K by
reconstruction-vs-K and LOO, preferring the smallest K that captures the
covariance.

---

## Bug 2 — Too few tuning steps for a poorly-identified geometry

**Where.** `pm.sample(..., tune=200, ...)`.

**Symptom.** On top of the rotation symmetry, 200 tuning steps leave NUTS poorly
adapted: extra divergences, even worse ESS, occasionally a stuck chain.

**Diagnostic.** Low `ess_bulk`/`ess_tail`; non-zero `diverging` count.

**Fix.** Use `tune=1000` (and `target_accept=0.9`) as in the clean notebook. (Note:
more tuning helps the *sampler*, but it does **not** fix the non-identifiability —
that is Bug 3's lesson.)

---

## Bug 3 — Interpreting a raw loading entry as if it were identified

**Where.** The final cell reports `W[0,0]`:
```python
w00 = idata.posterior['W'].values.reshape(-1, D, K_WRONG)[:,0,0]
print('reported W[0,0] =', w00.mean(), '+/-', w00.std())
```
**Symptom.** `W[0,0]` has a **multimodal** marginal and an enormous R-hat; its
posterior mean is a meaningless average over rotations/reflections. Reporting it
as "the loading of channel 0 on factor 0" is wrong — that number changes under any
rotation of the latent space.

**Diagnostic.** The histogram of `W[0,0]` is multimodal/symmetric about 0; the
`az.summary` R-hat for `W` entries is far from 1.0 even after fixing Bug 2.

**Fix.** Two parts:
1. Stop interpreting raw `W`. Report **rotation-invariant** quantities: the
   reconstructed covariance `W Wᵀ + sigma² I` (stable across draws), the subspace
   `W` spans, the eigen-spectrum, the noise `sigma`, and reconstructions `W z`.
2. If you *must* report loadings, first impose an identifying constraint (e.g.
   lower-triangular `W` with positive diagonal, or post-hoc Procrustes alignment to
   a reference) — and state the constraint explicitly.

**Teaching point.** A large R-hat does not always mean "sample more." Here it means
"this parameter is not identified — interpret an invariant instead." Knowing
*which* parameters are estimable is part of model criticism.

---

## Checklist for the fixed notebook

- [ ] `K = 2` (chosen via reconstruction-vs-K / LOO).
- [ ] `tune >= 1000`, `target_accept = 0.9`; 0 divergences.
- [ ] R-hat checked for **sigma / reconstruction**, not raw W.
- [ ] Conclusions reported as reconstructed covariance / sigma / dimensionality,
      never raw loading entries.
