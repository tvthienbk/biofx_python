# Grading Rubric — Project 05 (Logistic GLM)

Total: 100 points, allocated across the eight workflow steps. The project-specific
emphasis (link functions, priors on the probability scale) is weighted heavily.

| # | Workflow step | Points | What earns them |
|---|---------------|--------|-----------------|
| 1 | Problem & data story | 8 | States the Bernoulli/logistic DGP; flags independence, log-odds linearity, no measurement error, no confounding; standardizes $x$ and explains why. |
| 2 | Model spec & priors | 16 | Correct likelihood + **logit link**; justifies $\text{Normal}(0,1.5)$ over $\text{Normal}(0,10)$ *with reference to the probability scale*. |
| 3 | Prior predictive check | 16 | Performs the check **on the probability scale**; shows Normal(0,10) piles $p$ at 0/1 while Normal(0,1.5) spreads it. (This is the signature skill.) |
| 4 | Inference / NUTS | 8 | Sensible draws/tune/chains; fixed seed; explains the role of standardization in geometry. |
| 5 | Diagnostics | 12 | Reports $\hat R$, ESS, divergences; trace plots; names remedies (separation → weak prior; correlation → centering). |
| 6 | Posterior predictive | 12 | `plot_ppc` **and** a calibration curve; interprets departures. |
| 7 | Criticism / sensitivity | 14 | Recovery vs known truth; prior-width sensitivity; distinguishes "robust given data" from "defensible a priori". |
| 8 | Decision & communication | 8 | $P(\beta>0)$, the $p=0.5$ crossover with interval; non-technical summary. |
| — | Reproducibility & code quality | 6 | Scripts run clean; notebook executes top-to-bottom; shared helpers reused. |

**Deductions.** Modeling $p$ directly without a link: −15. Justifying priors only
on the log-odds scale: −8. Prior predictive check done on the log-odds scale: −8.
Un-standardized $x$ with no rationale: −4.

---

## Open-ended extension prompt

The current model assumes the log-odds is **linear** in $x$. Real dose–response
curves are often non-monotone or have a threshold. Extend the model with a
**non-linear predictor** — e.g. add a quadratic term $\beta_2 x^2$, or replace the
linear predictor with a small spline / Gaussian-process term on $x$ — and:

1. Justify priors for the new terms **on the probability scale** (the same
   discipline as the linear case).
2. Compare the linear and non-linear models with `az.loo` / `az.compare`. Does
   the extra flexibility earn its keep, or does LOO penalize it?
3. Re-examine the calibration curve. Did the non-linearity remove a systematic
   S-shaped miscalibration, or introduce overfitting in sparse regions of $x$?
4. Discuss the bias–variance and identifiability trade-offs you observe, and what
   you would tell an experimentalist about the half-maximal concentration now
   that the curve is non-linear.
