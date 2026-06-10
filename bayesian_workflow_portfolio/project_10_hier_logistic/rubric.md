# Grading Rubric — Project 10: Varying Intercepts (Hierarchical Logistic)

Total: **100 points** across the eight workflow steps plus the group-structure
skill. An open-ended extension follows.

| # | Workflow step | Criteria | Points |
|---|---|---|---|
| 1 | Problem & data story | States exchangeability of families; explains log-odds intercept + global covariate; documented DGP, fixed seed, known truth. | 10 |
| 2 | Model & priors | Correct hierarchical logistic; **justifies** priors on the **log-odds** scale; explains why an over-tight `tau` prior over-pools; non-centered. | 12 |
| 3 | Prior predictive | Checks implied binding rates spread across [0,1] rather than piling at 0/1. | 8 |
| 4 | Inference | Non-centered; sensible NUTS settings (chains ≥ 4, `target_accept` ≥ 0.9, seed). | 10 |
| 5 | Diagnostics | R-hat, ESS, **divergences = 0**, **energy plot**; interprets them. | 14 |
| 6 | Posterior predictive | PPC overlay; judges fit to the spread of family rates. | 8 |
| 7 | Varying intercepts / criticism | Shrinkage plot of intercepts; explains pooling and the over-pooling pitfall. | 16 |
| 8 | Decision & communication | Recovers `mu`, `tau`, `beta`; one-pager separates the robust slope from the prior-sensitive family spread. | 10 |
| — | SBC & prior sensitivity | SBC ranks for `mu`/`tau`/`beta`; prior-sensitivity demonstrates over-pooling under a tight `tau` prior. | 12 |

**Deductions.** Putting wide priors on log-odds parameters without checking the
implied probability scale (−6). Using a tight `tau` prior to "regularize" without
recognizing it over-pools (−8). Reporting raw per-family rates as the deliverable
(−6). Ignoring divergences (−8).

---

## Open-ended extension prompt

The model uses a **single global slope** `beta` shared by all families. Investigate
**varying slopes**: let each family have its own `beta_g` with a hierarchical prior,
and (the right way) model the **correlation** between a family's intercept and its
slope using `pm.LKJCholeskyCov` — exactly the structure of Project 11.

1. Does allowing family-specific slopes improve LOO over the varying-intercepts-only
   model (`az.compare`)? Or does the data not support the extra parameters?
2. Is there a real intercept–slope correlation, and does ignoring it (diagonal
   covariance) bias the population slope?

Deliver a short notebook with the extended model, an SBC check on the added
population slope mean, and a paragraph on whether the added flexibility paid off.
