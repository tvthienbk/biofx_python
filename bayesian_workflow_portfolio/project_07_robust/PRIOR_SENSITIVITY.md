# Prior Sensitivity — Project 07 (Student-t Robust Regression)

## Question

Robustness is governed by the **degrees of freedom $\nu$**, so the prior worth
stress-testing is the prior on $\nu$. Run `python3 prior_sensitivity.py` to
reproduce. $\nu$ controls tail weight: small $\nu$ => heavy tails (very robust,
outliers down-weighted); large $\nu$ => the Student-t approaches a Normal
(non-robust). We refit the contaminated data under three priors on $\nu$:

| label | prior on $\nu$ | character |
|-------|----------------|-----------|
| Heavy-tail-friendly | $\text{Gamma}(2,0.5)$ | mean 4 → readily permits heavy tails |
| Default | $\text{Gamma}(2,0.1)$ | mean 20, but mass on small $\nu$ → flexible |
| Normal-leaning | $\text{Gamma}(20,0.5)$ | mean 40 → nudges toward Normal |

## Results (representative run)

| nu prior | param | mean | sd | 94% HDI |
|----------|-------|------|----|---------|
| Heavy-tail Gamma(2,0.5) | beta | ~1.99 | ~0.06 | covers 2.0 |
| Heavy-tail Gamma(2,0.5) | nu   | ~1.09 | ~0.23 | small (heavy tails) |
| Default Gamma(2,0.1) | beta | ~2.00 | ~0.06 | covers 2.0 |
| Default Gamma(2,0.1) | nu   | ~1.12 | ~0.25 | small |
| Normal-leaning Gamma(20,0.5) | beta | ~2.01 | ~0.07 | covers 2.0 |
| Normal-leaning Gamma(20,0.5) | nu   | ~2.46 | ~0.54 | pulled up, still finite |

## Interpretation

1. **The robust slope is stable as long as the prior PERMITS small $\nu$.** Across
   all three priors $\beta$ sits at ~2.0 with a tight interval covering the truth.
   Even the "Normal-leaning" $\text{Gamma}(20,0.5)$ prior cannot force $\nu$ very
   large here, because the data — with 6 clear outliers — *insist* on heavy tails;
   the posterior $\nu$ only rises to ~2.5, still firmly in the robust regime.

2. **The data, not the prior, choose the tail weight.** This is the reassuring
   headline: with enough clearly-anomalous points, the likelihood overrules a
   mildly Normal-leaning $\nu$ prior and keeps the fit robust.

3. **The real danger is not a soft prior but a HARD constraint.** Fixing
   $\nu$ at a large value (e.g. $\nu=100$, as in the broken notebook) *does* defeat
   robustness, because then the data have no freedom to express heavy tails. The
   fix for a non-robust fit is therefore to **let $\nu$ be free (or set it small)**
   — never to pin it large. Prior sensitivity over reasonable $\nu$ priors is benign;
   the dangerous move is removing $\nu$ as a parameter altogether.

## Takeaway

Report: the robust slope is insensitive to the $\nu$ prior across a wide range,
because the outliers force the tails heavy regardless. Keep $\nu$ a free parameter
with a prior that allows small values; do not fix it large.
