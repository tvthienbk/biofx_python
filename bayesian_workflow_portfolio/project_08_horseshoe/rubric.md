# Grading Rubric — Project 08 (Regularized Horseshoe)

Total: 100 points across the eight workflow steps. The project-specific emphasis
(shrinkage priors, LOO comparison, and avoiding double-dipping) is weighted heavily.

| # | Workflow step | Points | What earns them |
|---|---------------|--------|-----------------|
| 1 | Problem & data story | 8 | States the sparse linear DGP; flags linearity, sparsity, standardized predictors, no severe collinearity. |
| 2 | Model spec & priors | 16 | Ridge and horseshoe; explains global/local/slab scales; uses the **non-centered** parameterization and says why. (Signature skill.) |
| 3 | Prior predictive check | 8 | Shows the horseshoe prior's spike-near-zero + heavy tails. |
| 4 | Inference / NUTS | 8 | `target_accept` raised; fixed seed; sensible draws/tune/chains. |
| 5 | Diagnostics | 14 | $\hat R$, ESS, **divergences**; recognizes a flood of divergences as the centered funnel; reads `az.plot_energy`. |
| 6 | Posterior predictive / recovery | 14 | Coefficient forest (horseshoe sparse vs ridge not); recovers the 3 signals; quantifies noise shrinkage. |
| 7 | Model comparison (LOO) | 14 | `az.compare` with `ic='loo'`; interprets the horseshoe's advantage as **parsimony** (`p_loo`), not necessarily a large `elpd` gap. (Signature skill.) |
| 8 | Decision & communication | 12 | Honest joint-fit reporting; explicitly avoids and explains **double-dipping**. (Signature pitfall.) |
| — | Reproducibility & code quality | 6 | Scripts run clean; notebook executes top-to-bottom; shared helpers reused. |

**Deductions.** Centered horseshoe with unexplained divergences: −12. Double-dipping
(select-then-refit-and-report) without flagging it: −15. Treating a wide-Normal
ridge as feature selection: −6. Cranking `tau0` to zero with no rationale: −4.

---

## Open-ended extension prompt

Our predictors were (nearly) independent, which makes selection comparatively easy.
Real feature sets are **correlated** — several markers may proxy the same biology.
Extend the project:

1. Regenerate $X$ with **correlated columns** (e.g. blocks of features with
   pairwise correlation 0.8) where only one feature per block is truly active.
   Show how the horseshoe distributes the signal across correlated features and how
   that complicates "which predictor" claims.
2. Add an explicit **null-permutation check**: shuffle $y$, run the full pipeline,
   and confirm no predictor is reliably selected from noise — quantifying the
   false-discovery behavior of your reporting rule.
3. Compare the horseshoe to an alternative sparsity prior (e.g. a finite
   spike-and-slab or the R2D2 prior) with `az.compare`, and discuss the
   computational and interpretational trade-offs.
4. For a collaborator, write the honest one-paragraph claim about which features
   matter when features are correlated — and what you cannot claim.
