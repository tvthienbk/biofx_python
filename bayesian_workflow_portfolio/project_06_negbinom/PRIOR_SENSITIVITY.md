# Prior Sensitivity — Project 06 (Negative-Binomial GLM)

## Question

The parameter that defines this project is the **dispersion** $\alpha$, so the
prior worth stress-testing is the prior on $\alpha$. Run
`python3 prior_sensitivity.py` to reproduce.

$\alpha$ controls overdispersion: $\operatorname{Var}(y)=\mu+\mu^2/\alpha$. A
prior that pushes $\alpha$ large drags the NB toward Poisson (under-dispersed); a
prior that allows small $\alpha$ lets the data express their true overdispersion.
We refit under three Gamma priors:

| label | prior on $\alpha$ | character |
|-------|-------------------|-----------|
| Tight-large | $\text{Gamma}(20,1)$ | mean 20, narrow → nudges toward Poisson |
| Default | $\text{Gamma}(2,0.1)$ | mean 20, heavy-tailed → flexible |
| Loose-small | $\text{Gamma}(1,1)$ | mean 1 → favors strong overdispersion |

## Results (representative run)

| alpha prior | param | mean | sd | 94% HDI |
|-------------|-------|------|----|---------|
| Tight-large Gamma(20,1) | beta1 | ~0.70 | ~0.07 | covers 0.8 |
| Tight-large Gamma(20,1) | alpha | ~2.57 | ~0.37 | pulled **up** from 2.0 |
| Default Gamma(2,0.1) | beta1 | ~0.71 | ~0.08 | covers 0.8 |
| Default Gamma(2,0.1) | alpha | ~1.86 | ~0.29 | covers 2.0 |
| Loose-small Gamma(1,1) | beta1 | ~0.71 | ~0.08 | covers 0.8 |
| Loose-small Gamma(1,1) | alpha | ~1.75 | ~0.26 | covers 2.0 |

## Interpretation

1. **The mean effect $\beta_1$ is robust.** Across all three priors $\beta_1$
   sits at ~0.70 with a 94% interval covering the truth 0.8. The log link
   *separates the mean from the variance*: the dispersion prior barely touches the
   regression coefficients. This is the reassuring headline — conclusions about
   the effect of $x$ do not hinge on the dispersion prior.

2. **The dispersion posterior shifts as expected.** The aggressive
   $\text{Gamma}(20,1)$ — which insists $\alpha$ is near 20 — pulls the posterior
   $\alpha$ up to ~2.6, away from the truth 2.0, because it is fighting the data
   toward Poisson-like behavior. The flexible and loose priors recover ~1.8–1.9,
   comfortably covering 2.0.

3. **Lesson.** With $N=150$ the data are informative enough to overrule all but
   the most stubborn dispersion prior. But the partial failure of
   $\text{Gamma}(20,1)$ is a useful warning: an overly confident prior that
   *assumes equidispersion* can quietly reintroduce the very Poisson pathology the
   NB was meant to fix. Prefer a weakly-informative, heavy-tailed prior on
   $\alpha$ so the data, not the prior, decide how overdispersed the counts are.

## Takeaway

Report: the effect of $x$ is robust to the dispersion prior; the dispersion
estimate itself is robust except under a prior that essentially asserts Poisson.
Default to a flexible $\text{Gamma}$ that lets the data speak.
