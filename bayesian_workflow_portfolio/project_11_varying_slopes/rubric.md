# Grading Rubric — Project 11: Varying Slopes (LKJ)

Total: **100 points** across the eight workflow steps plus the correlated-random-
effects skill. An open-ended extension follows.

| # | Workflow step | Criteria | Points |
|---|---|---|---|
| 1 | Problem & data story | States exchangeability; explains why intercept AND slope vary and co-vary; documented DGP, fixed seed, known `rho`. | 10 |
| 2 | Model & priors | Correct `pm.LKJCholeskyCov` 2x2 covariance; **justifies** `eta` and the SD priors; non-centered via the Cholesky factor. | 14 |
| 3 | Prior predictive | Checks implied dose-response lines are on a sensible scale. | 8 |
| 4 | Inference | Non-centered LKJ; sensible NUTS settings (chains ≥ 4, `target_accept` ≥ 0.9, seed). | 10 |
| 5 | Diagnostics | R-hat, ESS, **divergences ≈ 0**, **energy plot**; notes `rho` is the widest interval. | 14 |
| 6 | Posterior predictive | PPC overlay; judges fit. | 8 |
| 7 | Recovering the correlation / criticism | Posterior for `rho` vs truth; per-line effect scatter showing the tilt; explains why independence misfits. | 16 |
| 8 | Decision & communication | Recovers `mu_a`, `mu_b`, SDs, `rho`, `sigma`; one-pager explains the correlation's consequence for predicting new lines. | 10 |
| — | SBC & prior sensitivity | SBC ranks for the population means; prior-sensitivity shows `rho` moves with LKJ `eta` while means are robust. | 10 |

**Deductions.** Modeling intercept and slope as independent without justification
(−10). Using the centered parameterization and shipping divergences (−8).
Over-interpreting a loosely-identified `rho` from few groups as precise (−6).

---

## Open-ended extension prompt

The model has **two** correlated effects. Investigate scaling and identification:

1. **Add a third varying effect** (e.g. a quadratic dose term) so the random-effect
   covariance is 3x3. Does `LKJCholeskyCov(n=3)` still sample cleanly? How does the
   number of correlations you must estimate (now 3) interact with having only 8
   lines — are any correlations unidentified?
2. **Vary the number of groups** (G = 5, 8, 20, 50) and plot the posterior SD of
   `rho` against G. How many groups do you need before the correlation is usefully
   identified? Connect this to the prior-sensitivity result (eta matters most when
   G is small).

Deliver a notebook with the extended model, an SBC check on a population mean, an
`az.compare` (LOO) against the 2-effect model, and a short paragraph on
identification limits with few groups.
