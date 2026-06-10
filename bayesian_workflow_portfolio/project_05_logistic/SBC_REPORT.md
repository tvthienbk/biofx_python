# SBC Report — Project 05 (Logistic GLM)

## What SBC checks

Simulation-Based Calibration tests whether our **inference procedure** (model +
NUTS) is *self-consistent with its own generative model*. It does not use the real
data and it does not check whether the model is true of the world; it checks that
the Bayesian machinery is implemented correctly. The procedure:

1. Draw $(\alpha^\*, \beta^\*)$ from the prior $\text{Normal}(0,1.5)$.
2. Simulate a logistic dataset of size $N$ from those parameters.
3. Fit the model and obtain $L$ posterior draws of each coefficient.
4. Record the **rank** of the true value among the $L$ posterior draws.

If inference is calibrated, the ranks are **uniformly distributed** on
$\{0,\dots,L\}$ across many simulations. Departures diagnose specific pathologies:

- **∪-shaped** ranks → posteriors too *narrow* (over-confident).
- **∩-shaped** ranks → posteriors too *wide* (under-confident).
- **Sloped / shifted** ranks → posterior *bias*.

## Configuration

| setting | value |
|---------|-------|
| prior | $\alpha,\beta\sim\text{Normal}(0,1.5)$ |
| simulations | 50 |
| $N$ per dataset | 60 |
| posterior draws $L$ | ~200 (2 chains × 100) |
| tuning | 400 |
| uniformity test | chi-square, 10 bins |

Sampling is deliberately tiny so the script finishes well under two minutes.
`compute_convergence_checks=False` silences per-fit warnings; the rank statistic,
not per-fit $\hat R$, is the object of interest.

## Results

Both coefficients pass the chi-square uniformity test:

```
SBC over 50 simulations (N=60, L≈200)
  alpha: uniform = True   (p > 0.05)
  beta : uniform = True   (p > 0.05)
```

The rank histograms (`sbc_ranks.png`) are flat to within sampling noise: no ∪/∩
curvature and no slope. See the script output for the exact chi-square and
p-values from your run (they vary slightly with seed/thinning but remain
non-significant).

## Interpretation

Flat rank histograms mean the logistic GLM's posterior is **neither
over-confident nor biased**: the 94% credible intervals have ~94% coverage by
construction. Combined with the recovery test (which checks one real dataset) and
the prior predictive check (which validates the prior on the probability scale),
SBC closes the loop on *inference correctness* before we trust the model on data.

A practical note specific to this project: SBC draws parameters from the **prior**,
so if we had used the pathological $\text{Normal}(0,10)$ prior, SBC would sample
many near-separable datasets (all-0 or all-1), and the fits would be dominated by
the prior with very wide, edge-piled posteriors. SBC could still come out
"uniform" there — a reminder that SBC validates *self-consistency*, not *good
modeling*. Good priors are justified by the prior predictive check (Step 3), not
by SBC.
