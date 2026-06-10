# Grading Rubric — Project 18: Dynamics & Drift (State-Space)

Total: **100 points** across the eight workflow steps, a correctness tier (SBC,
prior sensitivity, debugging), and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, reproducible, exposes `truth` (both variances) and the true
  latent level.
- (3) States the four assumptions: random-walk level (no mean reversion),
  Gaussian homoscedastic noises, conditional independence, single latent level.

### Step 2 — Model specification with justified priors (12 pts)
- (4) Correct local-level structure (random walk + observation noise), implemented
  **non-centred**, with a justification of why non-centred (funnel avoidance).
- (5) Variance priors justified relative to the **confounding**: explains that
  vague priors let `sigma_level`/`sigma_obs` trade off, and why the chosen priors
  break the symmetry. Vague priors with no discussion <= 2/5.
- (3) `level0` prior stated.

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates series from the priors.
- (4) Interprets: plausible drift magnitude, not explosive or flat.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit settings, raised `target_accept`, `cores=1` noted.
- (3) Justifies the settings (random-walk geometry; multiprocess hang).

### Step 5 — Computational diagnostics (12 pts)
- (4) Reports R-hat, ESS, divergences.
- (4) Produces and reads the **`(sigma_level, sigma_obs)` pair plot**; identifies
  the negative correlation as the confounding signature.
- (4) States remedies: non-centred form + `target_accept` for divergences,
  informative priors / more data for the variance ridge.

### Step 6 — Posterior predictive checks & latent trajectory (10 pts)
- (5) Overlays inferred level (mean + band) on truth and data.
- (5) Confirms the level tracks the truth inside a band tighter than the obs
  scatter; reports level-recovery MAE.

### Step 7 — Model criticism & comparison (8 pts)
- (5) Fits the AR(1) comparator and compares via LOO (`az.compare`).
- (3) Interprets the comparison **and** notes the caveat that the two models score
  slightly different targets.

### Step 8 — Decision & communication (8 pts)
- (4) Reports the current level with a credible interval and a trend probability.
- (4) Communicates for a collaborator: report the level and trend, not raw readings.

---

## Correctness tier (20 points)

### SBC (8 pts)
- (4) `sbc.py` runs the prior->simulate->refit->rank loop on `sigma_obs`, kept light.
- (4) `SBC_REPORT.md` reports the uniformity test and interprets the histogram,
  acknowledging the light-sim compute trade-off.

### Prior sensitivity (6 pts)
- (3) Refits under >=3 variance-prior regimes and compares.
- (3) Concludes correctly: the prior shifts the process/obs split; robustness comes
  from informative priors + longer series.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes the three seeded bugs: vague variance priors,
  centred random walk (funnel), and reading marginals instead of the joint +
  level-vs-data overlay.

---

## Extension prompt (10 points, open-ended)

> **Add a drifting slope (local-linear trend).** Extend the model with a second
> latent state -- a *slope* that itself follows a random walk -- so the level can
> trend, not just wander. Regenerate data with a genuine trend, fit both the
> local-level and the local-linear-trend models, and compare via LOO. Show where
> the level-only model systematically lags a trending series (its one-step
> forecasts are biased) and how the trend model fixes it. Discuss the **new**
> identifiability tension: now THREE variances (level, slope, observation) compete
> to explain the data.

Grade on: (4) a correct trend DGP and a level-only PPC/forecast that **detects**
the lag; (3) a working local-linear-trend model; (3) a coherent discussion of the
three-way variance identifiability.
