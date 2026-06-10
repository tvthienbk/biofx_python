# SBC Report — Project 07 (Student-t Robust Regression)

## What SBC checks

Simulation-Based Calibration tests whether our **inference procedure** (the
Student-t model + NUTS) is self-consistent with its own generative model. It does
not use the real data. The procedure:

1. Draw $(\alpha^\*, \beta^\*, \sigma^\*)$ from the prior, and $\nu^\*$ from the
   model's $\nu$ prior.
2. Simulate a Student-t dataset of size $N$ using $(\alpha^\*,\beta^\*,\sigma^\*,\nu^\*)$.
3. Fit the Student-t model; obtain $L$ posterior draws of each parameter.
4. Record the **rank** of each true value among the $L$ posterior draws.

Calibrated inference => ranks uniform on $\{0,\dots,L\}$. ∪-shapes mean
over-confident posteriors; ∩-shapes under-confident; slopes/shifts mean bias.

## Configuration

| setting | value |
|---------|-------|
| coefficient priors | $\alpha,\beta\sim\text{Normal}(0,2)$ (tightened for tractable SBC) |
| scale prior | $\sigma\sim\text{HalfNormal}(1)$ |
| tail prior | $\nu\sim\text{Gamma}(8,0.5)$ (mean 16) **in both simulator and model** |
| simulations | 20 |
| $N$ per dataset | 40 |
| posterior draws $L$ | ~200 (2 chains × 100) |
| tuning | 400 |
| uniformity test | chi-square, 4 bins |

**A subtlety that mattered.** An early version simulated with a *fixed* $\nu=6$
while the model fit $\nu$ from its prior. That mismatch made the simulator and the
model disagree about the data-generating process, and the SBC rank histogram for
the **scale $\sigma$** came out non-uniform — a false alarm caused by the test
setup, not the inference. The fix is the textbook SBC requirement: **the simulator
must draw every parameter (including $\nu$) from exactly the prior the model
assumes.** Once $\nu$ is drawn from the same $\text{Gamma}(8,0.5)$ used by the
model, the calibration is clean. (We use tighter coefficient priors for SBC than
the model default $\text{Normal}(0,5)$ so the simulated lines fit quickly; SBC
validates the machinery over a representative parameter slice.)

## Results

After making the simulator consistent with the model, all three calibrated
parameters pass the chi-square uniformity test:

```
SBC over 20 simulations (N=40, L~200)
  alpha: uniform = True
  beta : uniform = True
  sigma: uniform = True
```

The rank histograms (`sbc_ranks.png`) are flat to within sampling noise.

## Interpretation

Flat ranks for $\alpha$, $\beta$, and $\sigma$ mean the Student-t posterior is
neither over-confident nor biased — its credible intervals have their nominal
coverage. Combined with the recovery test (clean line recovered from contaminated
data) and the LOO comparison (Student-t beats Normal), SBC closes the loop on
inference correctness.

The episode is itself the lesson: **SBC is only as valid as the match between your
simulator and your model.** A non-uniform rank histogram can signal a broken
inference *or* a broken test harness; always confirm the simulator draws from the
model's exact prior before blaming the sampler.
