# Grading Rubric — Project 07 (Student-t Robust Regression)

Total: 100 points across the eight workflow steps. The project-specific emphasis
(heavy tails; $\nu$ as a parameter; outlier robustness) is weighted heavily.

| # | Workflow step | Points | What earns them |
|---|---------------|--------|-----------------|
| 1 | Problem & data story | 8 | States the contaminated-linear DGP; flags linearity, vertical low-leverage outliers, known $x$; notes the clean line is the truth. |
| 2 | Model spec & priors | 14 | Both Normal and Student-t; $\nu$ as a free parameter with a prior that permits small $\nu$; notes t nests Normal as $\nu\to\infty$. |
| 3 | Prior predictive check | 8 | Simulates Student-t-implied responses; confirms heavy-tailed but plausible. |
| 4 | Inference / NUTS | 8 | Sensible draws/tune/chains; fixed seed; notes both converge. |
| 5 | Diagnostics | 10 | $\hat R$, ESS, divergences; recognizes convergence ≠ adequacy; reads inflated Normal $\sigma$ and small Student-t $\nu$ as tells. |
| 6 | Posterior predictive | 14 | Overlaid fitted lines (Normal over-uncertain / inflated band vs t robust); `plot_ppc` for the t. (Signature skill.) |
| 7 | Model comparison (LOO) | 20 | `az.compare` with `ic='loo'`; t rank 0; interprets `elpd_diff`/`dse`; notes outliers as high Pareto-$k$ under Normal; recovers clean $(\alpha,\beta)$; correctly does NOT compare $\sigma$ to the Normal SD. (Signature skill.) |
| 8 | Decision & communication | 12 | Robust slope/intercept with intervals; $\nu$ as outlier indicator; warns least-squares would mislead. |
| — | Reproducibility & code quality | 6 | Scripts run clean; notebook executes top-to-bottom; shared helpers reused. |

**Deductions.** Fitting only a Normal with no robust comparison: −15. Using a
Student-t but fixing $\nu$ large: −12. Asserting recovery of $\sigma$ against the
Normal SD when $\nu$ is small: −5. Treating high-leverage $x$ outliers as if a
robust likelihood alone would fix them: −4.

---

## Open-ended extension prompt

Our outliers were **vertical and low-leverage** by construction, which a robust
*likelihood* handles cleanly. Real corruptions are often **high-leverage** — bad
points at extreme $x$ that pull the slope hard — and a Student-t likelihood alone
may not save you. Extend the project:

1. Regenerate data with outliers placed at **extreme $x$** (high leverage) and
   show that the Student-t likelihood is *less* effective there. Explain why
   (leverage acts through the design, not the residual distribution).
2. Implement an explicit **mixture / contamination model**: each point is clean
   with probability $w$ or an outlier (broad component) with probability $1-w$,
   and infer $w$ and per-point outlier probabilities. Compare to the Student-t via
   `az.compare`.
3. Discuss the relationship between the Student-t and the mixture model (the t is
   a continuous scale-mixture of Normals) and when each is the better tool.
4. Report, for a collaborator, which points your model flags as outliers and how
   confident it is — and whether you would re-run those wells.
