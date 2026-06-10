# Grading Rubric — Project 06 (Negative-Binomial GLM)

Total: 100 points across the eight workflow steps. The project-specific emphasis
(detecting overdispersion; choosing the count family with LOO) is weighted heavily.

| # | Workflow step | Points | What earns them |
|---|---------------|--------|-----------------|
| 1 | Problem & data story | 8 | States the log-linear NB DGP; flags independence, log-linearity, constant dispersion, no zero-inflation, sequencing-depth offset; reports var/mean. |
| 2 | Model spec & priors | 12 | Both Poisson and NB with a log link; weakly-informative priors; notes NB nests Poisson as $\alpha\to\infty$. |
| 3 | Prior predictive check | 8 | Simulates NB-implied counts; confirms heavy-tailed but plausible; guards against exponentiated-mean blow-up. |
| 4 | Inference / NUTS | 8 | Sensible draws/tune/chains for both models; fixed seed; notes Poisson converges fine. |
| 5 | Diagnostics | 10 | $\hat R$, ESS, divergences for both; recognizes convergence ≠ adequacy. |
| 6 | Posterior predictive | 18 | `plot_ppc` for both; **quantifies** that Poisson predicted variance << observed; identifies forced equidispersion. (Signature skill.) |
| 7 | Model comparison (LOO) | 20 | `az.compare` with `ic='loo'`; NB rank 0; interprets `elpd_diff`/`dse`; checks Pareto-$k$; notes inflated `p_loo` for Poisson. (Signature skill.) |
| 8 | Decision & communication | 10 | Fold-change $e^{\beta_1}$ with interval; $P(\beta_1>0)$; warns that Poisson would mislead on variance. |
| — | Reproducibility & code quality | 6 | Scripts run clean; notebook executes top-to-bottom; shared helpers reused. |

**Deductions.** Fitting only Poisson with no NB/LOO comparison: −15. Concluding
adequacy from $\hat R$ alone with no PPC: −12. Wide $\beta_0$ prior that explodes
after exponentiation, unflagged: −4. Ignoring sequencing-depth offset without
mention: −3.

---

## Open-ended extension prompt

The model assumes **constant dispersion** — one $\alpha$ for all samples. Real
sequencing data show **mean–variance trends**: dispersion typically *decreases*
with expression level (the empirical-Bayes shrinkage at the heart of edgeR/DESeq2).
Extend the model so dispersion depends on the mean, e.g. let
$\log\alpha_i = \gamma_0 + \gamma_1\log\mu_i$, and:

1. Set and justify priors for $\gamma_0,\gamma_1$; run a prior predictive check on
   the implied var/mean relationship.
2. Compare the constant-dispersion and mean-dependent-dispersion NB models with
   `az.compare`. Does the extra flexibility earn its keep?
3. Add a per-sample sequencing-depth **offset** $\log(\text{depth}_i)$ to the
   linear predictor and discuss how omitting it would have biased $\beta_0$.
4. Reflect on the connection to empirical-Bayes count tools: what does a fully
   Bayesian hierarchical dispersion model buy you over their point-estimate
   shrinkage, and what does it cost?
