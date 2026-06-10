# One-Page Summary — Gene Expression vs a Covariate (Count Data)

**Audience:** a bench collaborator who needs a decision, not a posterior.

## The question

Does our gene's expression change with the covariate $x$ (a standardized
treatment dose / condition score), and by how much? We measured read counts in 150
samples and fit a count regression.

## The key modeling decision (and why it matters to you)

Read counts are **overdispersed**: their spread is much larger than a simple
"Poisson" count model allows (here the variance is ~14× the mean). We fit **two**
models — a Poisson and a Negative-Binomial — and the Negative-Binomial won
decisively on a held-out predictive score (LOO). **We report the
Negative-Binomial results.** Had we used the Poisson, we would have handed you a
falsely precise effect and a severe underestimate of how variable the counts are —
which would mislead any power calculation for the next experiment.

## What we found

- **Expression rises with $x$.** Each one standard-deviation increase in $x$
  multiplies expression by about **2.2-fold** (94% credible range roughly
  1.9–2.6).
- **The effect is essentially certain:** $P(\text{effect} > 0)\approx 1.00$.
- **The counts are genuinely noisy** (strong overdispersion), and our uncertainty
  reflects that honestly.

## What this means for the bench

- Treat the ~2.2-fold-per-SD effect as **real and robust** — it does not depend on
  our variance-modeling choices.
- When sizing the **next experiment**, use the Negative-Binomial variance, not the
  Poisson's: the true count-to-count variability is much larger, so you need more
  replicates than a Poisson would suggest to detect a given fold-change.
- If samples differ in **sequencing depth**, fold that in as an offset before
  comparing — otherwise depth differences masquerade as expression differences.

## Caveats (one line each)

- We assumed a single overdispersion level for all samples; strongly heterogeneous
  samples could need a mean-dependent dispersion model.
- We assumed log-linearity in $x$ and independent samples.

## Bottom line

Expression increases ~2.2-fold per SD of $x$, certainly and robustly. The headline
caution is methodological: **use a Negative-Binomial, not a Poisson**, or you will
understate the noise and over-trust the precision.
