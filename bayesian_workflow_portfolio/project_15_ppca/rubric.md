# Grading rubric — Project 15 (probabilistic PCA)

Total: **100 points**, across the 8 workflow steps, plus an extension.

| # | Workflow step | Points | What earns them |
|---|---------------|:------:|-----------------|
| 1 | Problem & data story | 8 | States the factor-model generative process; flags linearity, isotropic noise, fixed K as assumptions. |
| 2 | Model & identifiability | 18 | Correct PPCA model; **states the rotational/sign non-identifiability up front**; commits to interpreting invariants (or a stated constraint). |
| 3 | Prior predictive | 8 | Checks prior-implied total variance is sensible. |
| 4 | Inference | 8 | NUTS settings; anticipates clean sigma / poor raw-W mixing. |
| 5 | Diagnostics (right R-hat) | 18 | Checks R-hat for **identified** quantities (sigma, total_var, reconstruction); correctly explains that large raw-W R-hat is the symmetry, not a bug. |
| 6 | Posterior predictive | 12 | Compares observed vs reconstructed covariance; reports relative Frobenius error. |
| 7 | Criticism: choosing K | 16 | Reconstruction-vs-K and/or LOO; recovery on identifiable quantities; discusses over-specification harm. |
| 8 | Decision & communication | 8 | Communicates dimensionality + noise; warns against interpreting raw loadings. |
| — | Reproducibility & hygiene | 4 | Fixed seeds; runs top-to-bottom; shared helpers; tight plots. |

**Deductions.** Reporting raw loading entries as identified results (−8).
"Fixing" raw-W R-hat by sampling more without recognizing the symmetry (−4).
Over-specifying K without a model-selection check (−4).

---

## Open-ended extension prompt

> **Make the loadings identifiable and select K honestly.** (a) Impose an
> identifying constraint on `W` (e.g. lower-triangular with positive diagonal, or
> an ordered/positive first row) and verify that `W`'s R-hat drops to ≈ 1.0 — then
> discuss what the constraint *costs* (it privileges arbitrary directions and can
> distort uncertainty). (b) Implement **automatic relevance determination (ARD)**:
> put a per-column scale `tau_k ~ HalfNormal` on `W[:,k]` so the model can switch
> off unneeded factors, fit with K set generously (say 5), and show the posterior
> `tau_k` pruning the surplus factors toward zero. (c) Compare K=1..5 by LOO
> (`az.compare`) and by reconstruction error, and reconcile the two signals. Which
> would you trust to pick K for a real spectral/omics dataset, and why? When does
> ARD beat hard K-selection, and when does it just hide the problem?
