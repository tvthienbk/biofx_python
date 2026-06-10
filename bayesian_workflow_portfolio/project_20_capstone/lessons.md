# Lessons — Project 20 (Capstone: Decision Under Uncertainty)

## Headline takeaways

1. **The workflow exists to support a decision.** Every earlier project ended at a
   posterior or a comparison. The capstone insists on the last step the others
   skip: specify a loss, compute expected utility, and **recommend an action**. A
   posterior without a decision rule is an unfinished analysis.

2. **Partial pooling beats the winner's curse.** With unequal replication, the
   highest *raw* mean is usually a low-`n` fluke. Hierarchical shrinkage pulls
   noisy estimates toward the population mean by an amount set by their precision,
   so the surviving "winner" is one with genuine support. In our seed, the raw
   winner (#10, `n=2`) is wrong; the pooled decision recovers the true best (#9).

3. **The decision can differ from the argmax of the posterior mean.** Ranking by
   posterior mean is better than raw means but still ignores the spread. Expected
   regret and probability-of-best use the *whole* distribution and can reorder the
   recommendation — and, crucially, they communicate *how sure* we are.

4. **`P(best)` is honest about ambiguity.** It typically spreads probability across
   several compounds. That is the signal to advance two candidates, or to run more
   replicates, rather than over-committing to a single noisy winner.

5. **Non-centred parameterisation is still the price of admission.** Even at the
   capstone, the hierarchical funnel is the thing that breaks sampling; non-centring
   is what makes the whole pipeline run cleanly.

## Failures and surprises encountered while building this

- **Multiprocess sampling hung** without a linked BLAS; `cores=1` fixed it.
- **The winner's curse had to be *engineered*** via unequal replication. With equal
  replication the raw maximum is usually fine; it is the *heterogeneous precision*
  that creates the trap. This is itself the lesson: the danger lives in the design.
- **The decision was robust to the prior — but the model wasn't free.** The
  recommendation held across reasonable `tau` priors, yet an over-tight `tau` prior
  over-pooled and erased the signal. Robustness of the *action* is the right thing
  to check, and it is not automatic.
- **LOO favoured the hierarchical model**, confirming the structure earns its keep —
  a satisfying convergence of model criticism and the modelling choice.

## How to generalise the technique

- **Richer utilities.** Real decisions weigh cost, toxicity risk, manufacturability,
  and portfolio effects. The same machinery (expected utility over the posterior)
  handles any utility you can write down.
- **Sequential / adaptive design.** Use expected regret or expected value of
  information to decide *which compound to replicate next*, not just which to
  advance — Bayesian optimal experimental design.
- **Top-k decisions.** Generalise "pick the best" to "advance the best `k`" by
  computing the probability each compound is in the true top-`k`.
- **Per-compound noise / covariates.** Add `sigma_j` or compound-level predictors;
  the decision layer is unchanged.
- **Connecting the portfolio.** The hierarchical backbone is from Projects 10-12;
  the LOO comparison from the mixture/change-point projects; SBC and prior
  sensitivity are the portfolio-wide correctness tier. The capstone is where they
  combine into an action — which was the point of learning the workflow at all.
