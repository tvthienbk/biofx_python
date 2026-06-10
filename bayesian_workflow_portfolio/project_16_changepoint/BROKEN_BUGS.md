# BROKEN_BUGS.md — instructor answer key (Project 16)

`notebook_broken.ipynb` seeds the change-point pitfalls. Students run it, read the
diagnostics, fix each. Do not reveal this file until afterward.

---

## Bug 1 — Wrong switch direction (off-by-one / reversed regimes)

**Where.** The model cell:
```python
rate = pm.math.switch(tau < idx, lam0, lam1)   # should be tau > idx
```
**What it does.** With the correct convention `tau` is the first *post*-shift index,
so `switch(tau > t, lam0, lam1)` gives `lam0` before and `lam1` after. The buggy
`tau < t` (and the equivalent of swapping `lam0`/`lam1`) assigns the *pre*-shift
rate to the *post*-shift region — it fits the mirror image of the true change.

**Symptom.** The recovered rates come out **swapped** relative to truth: `lam0 ≈ 11`
and `lam1 ≈ 4` (truth is `lam0 = 4, lam1 = 11`), and/or `tau` lands at a strange
place. The model samples fine — convergence diagnostics look healthy — so only a
**recovery check against known truth** exposes it.

**Diagnostic.** Compare posterior `lam0, lam1` to the true values: they are
transposed. (`switch(tau > idx, ...)` vs `switch(tau < idx, ...)`; also remember
`switch(cond, a, b)` returns `a` where `cond` is true.)

**Fix.** Use `pm.math.switch(tau > idx, lam0, lam1)` (matching the data-generating
convention in `generate_data.py`).

---

## Bug 2 — Too few tuning steps

**Where.** `pm.sample(..., tune=100, ...)`.

**Symptom.** The compound NUTS+Metropolis sampler is poorly adapted: low ESS for
the rates, a jumpy `tau` chain, occasionally a stuck chain.

**Diagnostic.** Low `ess_bulk`/`ess_tail`; `tau` chains that do not agree.

**Fix.** Use `tune=1000` (and `chains=4`) as in the clean notebook.

---

## Bug 3 — Summarizing tau by its mean

**Where.** The final cell:
```python
print('reported tau =', tau_draws.mean())
```
**What it does.** `tau` is discrete and its posterior can be multimodal (several
plausible shift times) or skewed. The **mean** then falls *between* the supported
times — pointing at a bin the data actually argue against.

**Symptom.** The reported `tau` mean sits in a low-probability valley of the
`P(tau | y)` histogram; it may not even be an integer time the model can take.

**Diagnostic.** Plot `P(tau | y)`. If it has multiple bars (or is skewed), the mean
is the wrong summary.

**Fix.** Report the **mode** and a **credible set** (the smallest set of times
covering, e.g., 94% of the posterior mass). Show the full distribution. If `tau` is
genuinely bimodal, report *both* candidate times — the multimodality is information.

---

## Why these bugs together

Bug 1 is silent in convergence diagnostics and only caught by **recovery against
truth** (or SBC on the rates). Bug 3 is a **summary/communication** error, not a
sampling error — the posterior is correct, the reported number is not. Together
they teach that correctness has three layers: the model code (Bug 1), the sampler
(Bug 2), and the summary (Bug 3).

## Checklist for the fixed notebook

- [ ] `switch(tau > idx, lam0, lam1)` (matches the generating convention).
- [ ] `tune >= 1000`, `chains = 4`.
- [ ] Recovered `lam0, lam1` match truth (not swapped).
- [ ] `tau` reported by **mode + credible set**, with the full `P(tau | y)` shown.
