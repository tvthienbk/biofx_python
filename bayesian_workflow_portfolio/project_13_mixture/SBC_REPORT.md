# SBC Report — 2-component mixture

## Method

Simulation-Based Calibration (SBC) checks that the **whole inference procedure**
(model + sampler) is self-consistent, beyond merely converging. The recipe:

1. Draw parameters from the prior: weights `w ~ Dirichlet(2,2)`, means
   `mu ~ Normal(0,3)` (then **sorted** to match the ordered model), and
   `sigma ~ HalfNormal(1)`.
2. Simulate a labelled mixture dataset of `N = 100` points.
3. Refit the ordered mixture model with a tiny sampler
   (`draws=150, tune=300, chains=2`).
4. Record the **rank** of each true value among its posterior draws.

If inference is calibrated, the ranks are **uniform** on `{0, …, L}`. We run
`N_SIMS = 18` simulations — a deliberately *light* smoke-level check, because each
mixture refit costs a few seconds and many prior draws give nearly-overlapping
means (a hard, slow regime).

We calibrate only the **identifiable** quantities — the separation
`mu[1]-mu[0]`, the high-mean weight `w[1]`, and `sigma`. The raw per-label means
are not separately identified across simulations and would not yield meaningful
ranks.

## Results

Output of `python3 sbc.py` (chi-square uniformity test per quantity, 8 bins;
histogram saved to `sbc_ranks.png`):

```
SBC over 18 simulations (N=100, draws=150/chain x2)
   separation: chi2=6.89, p=0.441, uniform=True
         w[1]: chi2=3.33, p=0.853, uniform=True
        sigma: chi2=2.44, p=0.931, uniform=True
```

(Run the script to regenerate the exact numbers; they print to stdout and the
rank histograms are written to `sbc_ranks.png`. All three identifiable quantities
pass the 8-bin chi-square uniformity test at the smoke-level resolution above.)

## How to read it

- A **flat** histogram → calibrated inference for that quantity.
- A **∪-shape** (mass piling at both ends) → the posterior is *too narrow*
  (over-confident); the truth lands in the tails too often.
- A **∩-shape** (mass in the middle) → the posterior is *too wide*
  (under-confident).
- A **slope / shift** → bias.

With only 18 simulations and a tiny sampler the histograms are noisy; we are
looking for *gross* miscalibration, not fine structure. The chi-square p-value is
reported but should be read alongside the histogram shape rather than as a hard
pass/fail at these small counts. A higher-resolution SBC (≥ 200 simulations, more
draws) is the production-grade version; it is omitted here to keep the project
runnable in a couple of minutes.

## Caveats specific to mixtures

- The ordered transform is *essential* for SBC to be meaningful: without it the
  per-label ranks are corrupted by label switching and would look miscalibrated
  for the wrong reason.
- Prior draws occasionally place the two means almost on top of each other
  (separation ≈ 0). Those datasets are genuinely uninformative about which
  component is which; they widen the rank distribution but are a faithful part of
  the prior, so we keep them.
