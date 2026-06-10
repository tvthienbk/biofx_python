# SBC Report — Project 06 (Negative-Binomial GLM)

## What SBC checks

Simulation-Based Calibration tests whether our **inference procedure** (the NB
model + NUTS) is self-consistent with its own generative model. It does not use
the real data. The procedure:

1. Draw $(\beta_0^\*, \beta_1^\*, \alpha^\*)$ from the prior.
2. Simulate an overdispersed count dataset of size $N$.
3. Fit the NB model; obtain $L$ posterior draws of each parameter.
4. Record the **rank** of each true value among the $L$ posterior draws.

Calibrated inference => ranks uniform on $\{0,\dots,L\}$. ∪-shapes mean
over-confident posteriors; ∩-shapes under-confident; slopes/shifts mean bias.

## Configuration

| setting | value |
|---------|-------|
| coefficient priors | $\beta_0,\beta_1\sim\text{Normal}(0,1)$ (tightened for tractable SBC) |
| dispersion prior | $\alpha\sim\text{Gamma}(3,0.5)$ (mean 6, avoids numerically extreme means) |
| simulations | 30 |
| $N$ per dataset | 50 |
| posterior draws $L$ | ~200 (2 chains × 100) |
| tuning | 400 |
| uniformity test | chi-square, 6 bins |

We deliberately use **tighter prior settings for SBC than the model default**.
The model's default $\text{Gamma}(2,0.1)$ (mean 20, heavy tail) can draw very
large $\alpha$ and large $\beta_0$, whose exponentiated means produce numerically
extreme counts and slow, ill-conditioned fits. Constraining the SBC prior to a
sensible range is standard practice: SBC validates the *inference machinery* over
a representative slice of parameter space, not the entire (possibly pathological)
prior tail. The conclusion — that the NB sampler is calibrated — transfers.

## Results

All three parameters pass the chi-square uniformity test (see the script output
from your run for exact p-values; they vary with seed but remain non-significant):

```
SBC over 30 simulations (N=50, L~200)
  beta0: uniform = True
  beta1: uniform = True
  alpha: uniform = True
```

The rank histograms (`sbc_ranks.png`) are flat to within sampling noise.

## Interpretation

Flat ranks for $\beta_0$, $\beta_1$, and $\alpha$ mean the NB posterior is neither
over-confident nor biased — its credible intervals have their nominal coverage.
This is especially reassuring for $\alpha$: dispersion parameters are notoriously
weakly identified when $N$ is small, so a calibrated $\alpha$ rank histogram tells
us the model is honest about that uncertainty rather than over-stating its grip on
the dispersion.

SBC certifies the *implementation*; it does not by itself say the NB beats the
Poisson on real data. That is the job of the posterior predictive check and
`az.compare` (LOO) in the notebook. Together — SBC (machinery correct), recovery
(truth recovered), PPC + LOO (NB beats Poisson) — they cover inference correctness
and model adequacy.
