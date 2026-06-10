# BROKEN_BUGS.md — instructor answer key (Project 13)

`notebook_broken.ipynb` reproduces the mixture's signature pathology,
**label switching**, plus two supporting mistakes. Students run the notebook,
read the diagnostics, and fix each bug. Do not show this file until after the
exercise.

---

## Bug 1 — No ordering constraint on the means (THE pitfall)

**Where.** The model cell:
```python
mu = pm.Normal('mu', 0.0, 3.0, shape=2)   # unordered
```
**Symptom.** `az.summary` shows a large **R-hat for `mu`** (often > 1.3, sometimes
> 1.5) and possibly for `w`. The trace/marginal of `mu[0]` is **bimodal**: it has
mass near both -2 and +1.5, because different chains (or different parts of one
chain) disagree about which label is the low state.

**Diagnostic that reveals it.**
- `az.summary(var_names=['mu','w'])` → R-hat ≫ 1.01.
- The histogram cell at the end shows `mu[0]` and `mu[1]` each with **two** peaks
  — the classic label-switching fingerprint.
- `az.plot_trace` (add it) shows chains parked in different label assignments.

**Fix.** Impose the ordered transform and a sorted init:
```python
import pymc.distributions.transforms as tr
mu = pm.Normal('mu', 0.0, 3.0, shape=2,
               transform=tr.ordered, initval=np.array([-1.0, 1.0]))
```
This forces `mu[0] < mu[1]`, removing the permutation symmetry. R-hat returns to
≈ 1.00 and each `mu` marginal becomes unimodal.

**Teaching point.** Label switching is a *model-symmetry* problem, not a
*sampler* problem. More tuning, more draws, or higher `target_accept` will **not**
fix it — only breaking the symmetry will.

---

## Bug 2 — Too few tuning steps

**Where.** `pm.sample(..., tune=150, ...)`.

**Symptom.** Even after fixing Bug 1, 150 tuning steps may leave a poorly adapted
step size: occasional divergences and lower ESS. Compounded with Bug 1 it makes
the mess worse.

**Diagnostic.** Low `ess_bulk`/`ess_tail`; non-zero `diverging` count
(`idata.sample_stats['diverging'].sum()`).

**Fix.** Use `tune=1000` (and `target_accept=0.9`) as in the clean notebook. NUTS
needs enough warmup to adapt its mass matrix to the mixture geometry.

---

## Bug 3 — Reporting the per-label posterior mean as if it were identified

**Where.** The final cell:
```python
print('reported mu[0] =', mu_post[:,0].mean(), 'mu[1] =', mu_post[:,1].mean())
```
**Symptom.** With Bug 1 present, `mu[0].mean()` and `mu[1].mean()` both drift
toward the **overall** signal mean (~0.36) — a confidently reported number that
corresponds to *neither* true state. The bimodal histogram in the same cell shows
why the mean is meaningless.

**Diagnostic.** Compare the reported means to the visibly bimodal marginals: the
mean sits in the empty valley between the two modes.

**Fix.** Two parts:
1. Fix Bug 1 (ordering) so the labels are identified, **and**
2. Report **label-invariant** quantities — the separation `mu[1]-mu[0]`, the
   shared `sigma`, and the high-mean weight `w[1]` — rather than raw labels.
   `model.add_separation` attaches these as named scalars.

**Teaching point.** Never summarize a mixture by per-label point estimates
without first confirming (R-hat, unimodal marginals) that the labels are
identified, and prefer permutation-invariant summaries regardless.

---

## Checklist for the fixed notebook

- [ ] `mu` has an ordered transform with a sorted `initval`.
- [ ] `tune >= 1000`, `chains = 4`, `target_accept = 0.9`.
- [ ] R-hat ≈ 1.00 for `mu`, `w`, `sigma`; 0 divergences.
- [ ] Each `mu` marginal is unimodal.
- [ ] Conclusions reported as separation / sigma / weight, not raw labels.
