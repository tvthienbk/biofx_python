# Grading Rubric — Project 04: Simple Linear Regression

Total: **100 points**, allocated across the eight workflow steps, plus a correctness
tier (SBC, prior sensitivity, debugging) and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, seeded, exposes a `truth` dict; predictor lives **far from zero**
  (so standardization matters).
- (3) Assumptions stated: (a) linearity, (b) Gaussian homoscedastic noise, (c) predictor
  measured without error.

### Step 2 — Model specification & standardization (14 pts)
- (3) Likelihood `y_i ~ Normal(alpha + beta*x, sigma)` correct.
- (6) **Standardizes the predictor** and justifies why: interpretable intercept (response
  at mean dose), O(1) slope (per 1 SD), and decorrelated `alpha`-`beta` geometry. Using
  raw `x` with no discussion caps this at 2/6.
- (3) O(1) priors on the standardized coefficients, justified as weakly-informative.
- (2) Proper scale prior on `sigma` (carried from Project 02).

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates dose-response **lines** from the prior; inspects their spread.
- (4) Interprets: the implied lines are wide but plausible; would catch an absurd prior
  (e.g. a raw-scale width sweeping enormous response ranges).

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit, reproducible settings (≥2 chains, adequate `tune`, seed).
- (3) Notes that standardizing decorrelates the coefficients and improves mixing.

### Step 5 — Computational diagnostics (12 pts)
- (4) Reports R-hat, ESS bulk/tail, divergences for `alpha`, `beta`, `sigma`.
- (4) Inspects the `alpha`-`beta` correlation / pair plot and connects high correlation
  (on raw x) to low ESS.
- (4) States remedies; identifies standardization as the geometric fix.

### Step 6 — Posterior predictive checks (10 pts)
- (4) PPC (`az.plot_ppc`) and/or a fitted-line-with-uncertainty overlay.
- (3) Data and line plotted on the **same scale** (no scale-mismatch bug).
- (3) Comments on residual structure / homoscedasticity.

### Step 7 — Model criticism & comparison (8 pts)
- (4) Confirms the posterior brackets the known standardized truth.
- (4) **Maps coefficients back to the natural scale** and checks they match the true
  `alpha=2.0`, `beta=0.015`; notes LOO is available for comparing models.

### Step 8 — Decision & communication (6 pts)
- (3) Reports the dose effect on the **natural scale** with a credible interval.
- (3) Predicts the response at a dose of interest, with uncertainty.

---

## Correctness tier (20 points)

### Simulation-Based Calibration (8 pts)
- (4) `sbc.py` runs SBC over `alpha`, `beta`, `sigma` on the standardized design.
- (4) `SBC_REPORT.md` reports all three uniformity tests and reads the histograms.

### Prior sensitivity (6 pts)
- (3) Refits under ≥3 prior widths and compares.
- (3) Concludes robustness AND explains that standardizing is what makes a common O(1)
  prior width meaningful; un-scaled x would make priors un-settable.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes all three seeded bugs: raw un-scaled predictor,
  prior-width copied across scales, fitted line plotted on the wrong x scale.

---

## Extension prompt (10 points, open-ended)

> **Break linearity and detect it.** Modify the DGP so the true dose-response is mildly
> **curved** (e.g. add a quadratic term, `y = alpha + beta*x + gamma*x^2 + noise`, with a
> small `gamma`). Fit the *linear* model from this project and show, via a posterior
> predictive check on the **residuals vs dose** (a structured U- or arch-shaped residual
> pattern) where it breaks. Then fit a quadratic model (still standardizing) and compare
> the two with `az.compare` (LOO).

Grade on: (4) a correct curved DGP, (3) a residual-based PPC that **detects** the
nonlinearity, (3) a quadratic remedy with a LOO comparison that prefers it. This previews
nonlinear and polynomial regression.
