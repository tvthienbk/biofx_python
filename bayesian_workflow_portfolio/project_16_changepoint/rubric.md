# Grading rubric — Project 16 (change-point)

Total: **100 points**, across the 8 workflow steps, plus an extension.

| # | Workflow step | Points | What earns them |
|---|---------------|:------:|-----------------|
| 1 | Problem & data story | 8 | States the one-shift Poisson model; **gets the tau index convention right**; flags single/abrupt/constant-rate/Poisson assumptions. |
| 2 | Model & implementations | 18 | Correct `switch(tau > t, ...)`; sensible Exponential/DiscreteUniform priors; **both** a discrete-tau and a marginalized-tau implementation. |
| 3 | Prior predictive | 8 | Checks prior-implied count magnitudes are sane. |
| 4 | Inference | 8 | NUTS+Metropolis settings; ≥4 chains to detect multimodal tau. |
| 5 | Diagnostics & tau posterior | 18 | R-hat/ESS for rates; **summarizes tau by mode + credible set, never the mean**; shows full P(tau\|y). |
| 6 | Posterior predictive | 10 | `plot_ppc` reproduces the two-level structure; checks for over-dispersion. |
| 7 | Criticism & cross-check | 16 | Discrete and marginalized implementations agree; recovery of rates and tau vs truth. |
| 8 | Decision & communication | 8 | Reports tau credible set, rates, and fold-change for a collaborator. |
| — | Reproducibility & hygiene | 6 | Fixed seeds; runs top-to-bottom; shared helpers; tight plots. |

**Deductions.** Reporting `tau` by its mean (−6). Wrong switch direction unnoticed
(−6). Forcing Poisson on visibly over-dispersed counts (−3). Only one
implementation with no cross-check (−3).

---

## Open-ended extension prompt

> **Generalize to an unknown number of change-points.** (a) Extend to *two*
> change-points (`tau1 < tau2`) with three rate regimes, using an ordered pair of
> discrete taus (and/or a marginalized version that sums over ordered pairs).
> Recover both shift times on data simulated with two shifts, and check what the
> two-shift model infers on data with only *one* shift (does the spurious second
> tau become non-identified / diffuse?). (b) Implement a **continuous relaxation**
> of the change-point: replace the hard `switch` with a logistic transition
> `sigmoid((t - tau)/s)` and infer the transition sharpness `s`; discuss when a
> gradual transition is the better model and how `s → 0` recovers the abrupt case.
> (c) For real data where the number of shifts is unknown, sketch how you would
> choose between 0, 1, and 2 change-points (LOO, or a prior over the number of
> segments) and what the multimodal-tau pitfall implies for that comparison.
