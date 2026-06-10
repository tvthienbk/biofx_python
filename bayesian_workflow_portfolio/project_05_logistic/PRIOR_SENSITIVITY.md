# Prior Sensitivity — Project 05 (Logistic GLM)

## Question

The signature pitfall of this project is the **width of the coefficient priors**.
Prior sensitivity asks: how much does the posterior actually move as we change
that width? Run `python3 prior_sensitivity.py` to reproduce.

We refit the same $N=120$ dataset under three coefficient priors:

| label | prior | character |
|-------|-------|-----------|
| Tight | $\text{Normal}(0,0.5)$ | strongly informative; will fight the data |
| Weak-info | $\text{Normal}(0,1.5)$ | our default; sensible on the probability scale |
| Vague | $\text{Normal}(0,10)$ | the "non-informative" mistake; edge-seeking a priori |

## Results (representative run)

| prior | param | post mean | post sd | 94% HDI |
|-------|-------|-----------|---------|---------|
| Tight Normal(0,0.5) | alpha | ~0.34 | ~0.18 | covers 0.3 |
| Tight Normal(0,0.5) | beta  | ~1.18 | ~0.22 | **shrunk toward 0** |
| Weak-info Normal(0,1.5) | alpha | ~0.39 | ~0.22 | covers 0.3 |
| Weak-info Normal(0,1.5) | beta  | ~1.62 | ~0.32 | covers 1.4 |
| Vague Normal(0,10) | alpha | ~0.43 | ~0.23 | covers 0.3 |
| Vague Normal(0,10) | beta  | ~1.68 | ~0.34 | covers 1.4 |

(Exact numbers vary slightly with seed; the pattern is stable.)

## Interpretation

1. **Weak vs vague: nearly identical posteriors.** With 120 informative
   observations the likelihood dominates, so $\text{Normal}(0,1.5)$ and
   $\text{Normal}(0,10)$ give almost the same posterior for $\beta$ (~1.6, both
   covering the truth 1.4). On *this* dataset the choice barely matters.

2. **Tight prior shrinks the slope.** $\text{Normal}(0,0.5)$ pulls $\beta$ from
   ~1.6 down toward ~1.2 — the informative prior is fighting the data. Whether
   that is desirable depends on genuine prior knowledge; absent it, the default
   weak-info prior is the honest choice.

3. **The crucial caveat.** "Weak and vague agree" is a statement about the
   *posterior given these data*. It is **not** a license to use the vague prior.
   On the **probability scale, before data**, $\text{Normal}(0,10)$ is
   pathological: it asserts binding is near-deterministic (U-shaped implied $p$).
   See the notebook Step 3 prior predictive check. A prior can be simultaneously
   "harmless once you have plenty of data" and "absurd as a statement of prior
   belief." With *scarce* data — or under separation — that absurdity leaks
   straight into the posterior, which is why we default to $\text{Normal}(0,1.5)$.

## Takeaway

Report robustness honestly: the slope conclusion is robust across reasonable
prior widths here, *and* we still prefer the weakly-informative prior because it
is the only one that is defensible a priori on the probability scale.
