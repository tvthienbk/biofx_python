# Grading Rubric — Project 09: Partial Pooling

Total: **100 points**, allocated across the eight workflow steps plus the
project-specific parameterization skill. An open-ended extension follows.

| # | Workflow step | Criteria | Points |
|---|---|---|---|
| 1 | Problem & data story | States the exchangeability assumption; explains why few-obs-per-group makes pooling matter; documented DGP with fixed seed and known truth. | 10 |
| 2 | Model & priors | Correct hierarchical Normal; **justifies** hyperpriors on `mu`, `tau`, `sigma`; explains centered vs non-centered. | 12 |
| 3 | Prior predictive | Simulates from the prior; confirms implied data cover the real scale without absurd extremes. | 8 |
| 4 | Inference | Non-centered model; sensible NUTS settings (chains ≥ 4, `target_accept` ≥ 0.9, seed). | 10 |
| 5 | Diagnostics | Reports R-hat, ESS, **divergences = 0**; includes **energy plot** and a funnel pairs plot; interprets them. | 16 |
| 6 | Posterior predictive | PPC overlay; judges adequacy of the fit to the observed spread. | 8 |
| 7 | Shrinkage / criticism | Shows the shrinkage plot (no-pool vs partial-pool); explains the bias–variance trade and that small groups shrink more. | 14 |
| 8 | Decision & communication | Recovers population params within tolerance; one-pager translates `mu`, `tau` into an actionable per-plate recommendation. | 10 |
| — | SBC & prior sensitivity | SBC ranks for `mu`/`tau` read correctly; prior-sensitivity shows `tau` (and shrinkage) is prior-sensitive with few groups. | 12 |

**Deductions.** Using the centered parameterization in the clean notebook without
addressing divergences (−10). Ignoring a non-zero divergence count (−8). Reporting
raw per-group means as the deliverable instead of the shrunken estimates (−6).

---

## Open-ended extension prompt

The current model assumes a **common** within-group noise `sigma` and a **Normal**
population of group means. Pick one and investigate:

1. **Heteroscedastic groups.** Let each group have its own `sigma_j` with a
   hierarchical prior (`sigma_j ~ HalfNormal(s)`, `s` itself estimated). Does this
   change the shrinkage pattern? Does it introduce a *second* funnel (now on `s`)?
2. **Heavy-tailed population.** Replace `theta_j ~ Normal(mu, tau)` with a Student-t
   population. Re-simulate data with one outlying group and compare how the Normal
   and t hierarchies shrink that outlier. Which is more robust, and what does the
   energy/divergence picture look like for each?

Deliver a short notebook with the new model, an SBC sanity check on the added
parameter, and a paragraph on whether the extra flexibility was warranted by the
data (use `az.compare` with LOO).
