# Grading Rubric — Project 02: Estimating a Mean & Spread

Total: **100 points**, allocated across the eight workflow steps, plus a correctness
tier (SBC, prior sensitivity, debugging) and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, seeded, exposes a `truth` dict with **both** `mu` and `sigma`.
- (3) Assumptions stated: (a) measurements independent, (b) `mu`/`sigma` constant
  (homoscedastic, no drift), (c) Gaussian/symmetric noise (no heavy tails).

### Step 2 — Model specification with justified priors (12 pts)
- (3) Likelihood `y_i ~ Normal(mu, sigma)` correct.
- (3) Location prior justified as broad/weakly-informative on the data's scale.
- (6) **Scale prior justified as proper.** Full credit requires explaining why a flat
  improper prior on `sigma` is dangerous and choosing a proper alternative
  (`HalfNormal`/`Exponential`/`HalfCauchy`). A bare improper prior earns at most 1/6.

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates datasets from the prior; inspects implied means **and** spreads.
- (4) Interprets the result; would catch an improper scale prior by its
  many-orders-of-magnitude implied spread.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit, reproducible settings (≥2 chains, adequate `tune`, seed).
- (3) Justifies the settings; notes scale parameters can be harder to sample.

### Step 5 — Computational diagnostics (12 pts)
- (4) Reports R-hat, ESS bulk/tail, divergences for **both** parameters.
- (4) Trace plot read for both `mu` and `sigma` (well-mixed caterpillars).
- (4) States remedies for failure, explicitly linking poor `sigma` mixing to a bad
  scale prior.

### Step 6 — Posterior predictive checks (10 pts)
- (4) PPC overlaying replicates on observed data (`az.plot_ppc`).
- (3) A discrepancy statistic on the **spread** (e.g. predicted SD vs observed SD).
- (3) Correct reduction axis (observation, not draw).

### Step 7 — Model criticism & comparison (8 pts)
- (4) Confirms the joint posterior brackets the known `(mu, sigma)`.
- (4) Inspects the joint `(mu, sigma)` posterior (e.g. `az.plot_pair`) and comments on
  any mu-sigma dependence; notes that comparison (LOO) needs a second model.

### Step 8 — Decision & communication (8 pts)
- (4) Reports `mu` with a credible interval.
- (4) Reports `sigma` with a credible interval and explains why reporting the spread
  matters (reproducibility of a future measurement).

---

## Correctness tier (20 points)

### Simulation-Based Calibration (8 pts)
- (4) `sbc.py` runs SBC over **both** `mu` and `sigma`.
- (4) `SBC_REPORT.md` reports both uniformity tests and reads the histograms; explains
  why calibrating the *scale* is the point.

### Prior sensitivity (6 pts)
- (3) Refits under ≥3 **proper** scale priors and compares.
- (3) Concludes robustness among proper priors **and** distinguishes proper vs improper
  as the decisive choice; notes robustness is sample-size-dependent.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes all three seeded bugs: improper flat `sigma` prior,
  variance-vs-SD confusion, wrong PPC reduction axis.

---

## Extension prompt (10 points, open-ended)

> **Break homoscedasticity and watch the model fail.** Modify the DGP so the noise SD
> grows with the measurement index (e.g. `sigma_i = 0.5 + 0.05 * i`), violating
> assumption (b). Fit the constant-`sigma` model from this project and show, via a
> posterior predictive check on a *residual-spread* statistic (e.g. the SD of the
> first half vs the second half of the data), where it breaks. Then sketch the model
> that would fix it (e.g. `sigma_i = exp(a + b * x_i)`, a log-linear variance model).

Grade on: (4) a correct heteroscedastic DGP, (3) a PPC/discrepancy statistic that
**detects** the misfit, (3) a coherent description of the variance-model remedy.
