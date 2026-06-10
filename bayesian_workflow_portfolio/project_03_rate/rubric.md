# Grading Rubric — Project 03: Estimating a Rate (Poisson)

Total: **100 points**, allocated across the eight workflow steps, plus a correctness
tier (SBC, prior sensitivity, debugging) and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (8 pts)
- (3) DGP documented, seeded, exposes a `truth` dict (`log_rate`) AND **varying
  exposures**.
- (3) Assumptions stated: (a) events independent (Poisson), (b) single common rate (no
  overdispersion/covariates), (c) exposures known exactly.
- (2) Demonstrates that the naive mean count and the exposure-adjusted rate disagree
  (motivating the offset).

### Step 2 — Model specification with justified priors (12 pts)
- (3) Likelihood `y_i ~ Poisson(exposure_i * lambda)` correct.
- (4) **Uses the exposure offset** (`mu = exposure * exp(log_rate)`), and explains why
  varying exposure requires it. Omitting it caps the score at 2/4.
- (5) **Log link justified**: a Normal prior on `log_rate` makes the rate positive and
  the prior multiplicative; weakly-informative breadth explained.

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates counts from the prior (with real exposures); inspects implied totals.
- (4) Interprets: the implied range is wide but finite; would catch a flat-on-the-rate
  prior by its absurd implied totals.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit, reproducible settings (≥2 chains, adequate `tune`, seed).
- (3) Notes the log link gives an unconstrained, benign geometry.

### Step 5 — Computational diagnostics (10 pts)
- (4) Reports R-hat, ESS bulk/tail, divergences.
- (3) Trace read (well-mixed caterpillar).
- (3) States remedies for failure.

### Step 6 — Posterior predictive checks (10 pts)
- (4) PPC overlaying replicates on observed counts.
- (3) A discrepancy statistic (e.g. total count) with a Bayesian p-value near 0.5.
- (3) Correct reduction axis (observation, not draw).

### Step 7 — Model criticism & comparison (10 pts)
- (6) **Fits the no-offset model and compares**, showing the order-of-magnitude bias —
  the central criticism of this project.
- (4) Confirms the correct (offset) model recovers the known `log_rate`; notes LOO is
  available (`log_likelihood=True`) for formal comparison.

### Step 8 — Decision & communication (6 pts)
- (3) Reports the rate per unit exposure with a credible interval.
- (3) Translates to an expected count for a stated exposure (the actionable quantity).

---

## Correctness tier (20 points)

### Simulation-Based Calibration (8 pts)
- (4) `sbc.py` runs SBC on `log_rate` with varying exposures and the offset engaged.
- (4) `SBC_REPORT.md` reports the uniformity test and reads the histogram; notes the
  no-offset model would fail SBC (sloped ranks).

### Prior sensitivity (6 pts)
- (3) Refits under ≥3 priors on `log_rate` and compares.
- (3) Concludes robustness AND notes that the far larger danger is the *structural*
  offset error, which no prior choice fixes.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes all three seeded bugs: omitted offset, flat prior on the
  rate (no log link), wrong PPC reduction axis.

---

## Extension prompt (10 points, open-ended)

> **Add overdispersion and watch the Poisson fail.** Real count data are often
> *overdispersed*: the variance exceeds the mean (extra sample-to-sample variability the
> Poisson cannot accommodate). Modify the DGP so counts are drawn from a
> Negative-Binomial (e.g. `mu = exposure * lambda`, with a dispersion parameter), still
> with the exposure offset. Fit the Poisson offset model from this project and show, via
> a posterior predictive check on the count *variance* (or a dispersion statistic), where
> it breaks — the observed variance will exceed the Poisson's predicted variance. Then
> fit a Negative-Binomial offset model and compare with `az.compare` (LOO).

Grade on: (4) a correct overdispersed DGP retaining the offset, (3) a PPC/dispersion
statistic that **detects** the misfit, (3) a coherent Negative-Binomial remedy with a
LOO comparison. This previews the over-dispersion / Negative-Binomial project.
