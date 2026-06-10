# BROKEN_BUGS.md — instructor answer key (Project 14)

`notebook_broken.ipynb` seeds the two HMM-specific pitfalls. Students run it, read
the diagnostics, and fix each. Do not reveal this file until afterward.

---

## Bug 1 — Wrong forward recursion: `max` instead of `logsumexp`

**Where.** Inside `forward_BUGGY`:
```python
return logem_t + pt.max(m, axis=0)     # should be pt.logsumexp(m, axis=0)
...
return pt.max(seq[-1])                  # should be pt.logsumexp(seq[-1])
```
**What it does.** Summing over the previous state with `logsumexp` gives the
**marginal likelihood** (total probability of all paths). Using `max` gives the
**Viterbi** best-single-path probability — a *different* objective. The model still
compiles and samples, which is what makes this bug insidious.

**Symptom.** The posterior parameters are **biased**: typically the transition
probabilities and/or sigma are off, because the sampler is fitting the wrong
likelihood. On synthetic data with known truth, recovery fails — the recovered
`p01, p10` do not bracket the true values, even though R-hat looks fine.

**Diagnostic that reveals it.** This bug does **not** show up in convergence
diagnostics (R-hat/ESS can be perfectly healthy). It shows up in **recovery
against known truth** (`test_recovery.py`) and in a **posterior predictive
check**: trajectories simulated from the biased parameters do not match the
observed dwell-time / occupancy statistics. *Lesson: convergence ≠ correctness;
SBC and recovery tests catch wrong-objective bugs that R-hat cannot.*

**Fix.** Restore `pt.logsumexp` in both the recursion step and the final
reduction (the correct version is in `model._forward_logp`).

---

## Bug 2 — Unordered emission means: state-label non-identifiability

**Where.** The model cell:
```python
mu = pm.Normal('mu', 0.0, 3.0, shape=2)   # no ordered transform
```
**Symptom.** Large **R-hat for `mu`** and a bimodal per-state `mu` marginal: across
the 4 chains, some label state 0 as the low-emission state and others as the high.
The transition probabilities `p01`/`p10` may also become confused because their
*meaning* (into/out of the higher state) flips with the labels.

**Diagnostic.** `az.summary(var_names=['mu'])` → R-hat ≫ 1.01; `az.plot_trace` shows
chains in different label assignments.

**Fix.** Add the ordered transform with a sorted init:
```python
import pymc.distributions.transforms as tr
mu = pm.Normal('mu', 0.0, 3.0, shape=2,
               transform=tr.ordered, initval=np.array([-1.0, 1.0]))
```
This pins state 0 to the lower emission mean, breaking the symmetry. As with the
mixture, the cure is the *constraint*, not more tuning.

---

## Why two bugs together is instructive

Bug 1 (wrong objective) and Bug 2 (label switching) fail in **different**
diagnostics: Bug 2 is loud in R-hat, Bug 1 is silent there and only caught by
recovery/PPC. Fixing Bug 2 alone makes the chains agree — on the *wrong* answer.
Students must use the full toolkit (convergence **and** calibration **and**
predictive checks) to be confident the HMM is right.

## Checklist for the fixed notebook

- [ ] Forward recursion uses `pt.logsumexp` in the step **and** the final reduction.
- [ ] `mu` has an ordered transform with a sorted `initval`.
- [ ] R-hat ≈ 1.00, 0 divergences.
- [ ] Recovered `p01, p10, mu, sigma` bracket the known truth.
- [ ] Posterior-predictive trajectories match observed occupancy/dwell stats.
