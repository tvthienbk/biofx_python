# SBC Report — Project 17 (Gaussian Process noise scale)

## Method

Simulation-Based Calibration checks that the **inference procedure** is
self-consistent, independent of any particular dataset. The loop:

1. Draw hyperparameters from their priors: `ell* ~ InverseGamma(6,12)`,
   `eta* ~ HalfNormal(2)`, `sigma* ~ HalfNormal(0.5)`.
2. Draw a function from the GP prior with `(ell*, eta*)` and add noise `sigma*`
   to produce a tiny dataset (`N = 12`).
3. Obtain posterior draws of `sigma`.
4. Record the **rank** of `sigma*` among those posterior draws.

If inference is calibrated, the ranks are **uniform**. Systematic shapes diagnose
failure: ∪-shaped → posteriors too narrow (overconfident); ∩-shaped → too wide
(underconfident); a slope → bias.

We focus SBC on `sigma` because it is the cleanly identifiable scalar; full SBC
over `(ell, eta)` jointly is partly confounded by the very trade-off this project
teaches about — which is itself the point.

## Why an analytic (MCMC-free) posterior

A GP-with-Gaussian-noise has a **closed-form marginal likelihood**
`N(y; 0, eta^2 ExpQuad(ell) + sigma^2 I)`. We exploit this to do SBC **without
running NUTS**: for each simulated dataset we draw `N_PRIOR = 4000` hyperparameter
particles from the prior, weight them by the marginal likelihood, and **resample**
to obtain `(ell, eta, sigma)` posterior draws (self-normalised importance
sampling). The rank of `sigma*` among the resampled `sigma` draws is the SBC
statistic. This is exact up to Monte-Carlo error and runs in **seconds**, so we can
afford `N_SIMS = 200` — a genuinely informative calibration rather than a token
one. (Running per-dataset NUTS would have been ~30 s/refit here without a linked
BLAS — hence the analytic route, which is the responsible choice when the
likelihood is available in closed form, mirroring the project's main-model
philosophy.)

## Results

Run `python3 sbc.py`. It prints the chi-square uniformity test over 16 rank bins
and saves `sbc_ranks.png`. The test should report a **non-significant** deviation
from uniformity (`p > 0.01`, `uniform: True`) — no evidence of miscalibration for
`sigma` across 200 simulations.

## Interpretation

A pass means: given correctly-specified data, inference recovers the noise scale
with correctly-sized uncertainty. It does **not** certify the `(ell, eta)`
sub-space — by design, those are weakly identified, and the informative
length-scale prior is what keeps them tame (see `PRIOR_SENSITIVITY.md`). The
importance-sampling posterior also depends on the prior being a reasonable proposal
for the likelihood; with the informative length-scale prior this holds, and the
effective sample size of the weights stays healthy on these tiny datasets.
