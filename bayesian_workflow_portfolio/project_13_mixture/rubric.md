# Grading rubric — Project 13 (finite mixture)

Total: **100 points**, allocated across the 8 workflow steps, plus an extension.

| # | Workflow step | Points | What earns them |
|---|---------------|:------:|-----------------|
| 1 | Problem & data story | 8 | States the latent-membership generative model; flags K=2, shared sigma, independence, hard membership as assumptions. |
| 2 | Model & priors | 16 | Marginalizes labels via `NormalMixture`; **justifies the ordered transform** as the cure for label switching; sensible Dirichlet/HalfNormal/Normal priors. |
| 3 | Prior predictive | 10 | Simulates prior datasets; confirms plausible bimodality; would revise priors if pathological. |
| 4 | Inference | 8 | NUTS settings stated (draws/tune/chains/target_accept); ≥4 chains to enable R-hat detection of switching. |
| 5 | Diagnostics | 18 | R-hat, ESS, divergences reported; correctly identifies that high `mu` R-hat = label switching and that the fix is the constraint, not more tuning. |
| 6 | Posterior predictive | 10 | `plot_ppc` reproduces bimodal shape, weights, widths; discusses what misfit would imply about K. |
| 7 | Criticism & identifiability | 16 | Reports **label-invariant** quantities (separation, sigma, weight); checks recovery against truth; discusses over-specifying K. |
| 8 | Decision & communication | 8 | Translates posterior into a collaborator-facing statement (fraction in high state, resolution of states). |
| — | Reproducibility & hygiene | 6 | Fixed seeds; runs top-to-bottom; uses shared helpers; tight plots. |

**Deductions.** Reporting raw per-label means without checking identification
(−6). Sampling discrete `z` directly with poor mixing (−4). Claiming robustness
without running the prior sweep (−3).

---

## Open-ended extension prompt

> **Extend the model to an unknown number of components.** Replace the fixed K=2
> with (a) K=3 and (b) K=4 fits, each with an ordered-mean constraint, and
> compare them to K=2 using LOO (`az.compare`) **and** posterior predictive
> checks. Then implement an **over-fitted / sparse mixture**: set K=5 with a
> Dirichlet prior whose concentration is *small* (e.g. `a = 0.5` per component)
> so the prior prunes empty components, and inspect the posterior weights. Discuss:
> Does LOO prefer the true K? What do the "extra" components do — do they go empty,
> split a real component, or chase outliers? How does the ordered constraint
> interact with empty components (hint: an empty component's mean is non-identified
> and the ordering can pin it to an arbitrary gap)? Write up which model-selection
> signal you would trust for a real experiment and why.
