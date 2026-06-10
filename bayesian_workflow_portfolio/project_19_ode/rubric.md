# Grading Rubric — Project 19: Mechanistic Model (Bayesian PK / ODE)

Total: **100 points** across the eight workflow steps, a correctness tier (SBC,
prior sensitivity, debugging), and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, reproducible, exposes `truth` (`k`, `V`, `sigma`) and the
  closed form; design includes early + late timepoints.
- (3) States the four assumptions: one compartment, first-order elimination,
  instantaneous bolus, additive Gaussian noise.

### Step 2 — Model specification with justified priors (12 pts)
- (4) Correct mechanism (`C(t)=(D/V)exp(-kt)`), log-scale positivity, likelihood.
- (5) Priors justified as **domain knowledge** (physiological ranges), and the
  identifiability story explained (early pins `V`, slope pins `k`; the `Vmax/Km`
  analogy). Bare priors with no discussion <= 2/5.
- (3) Explains why the closed form is used and when a numerical solver is needed.

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates concentration curves from the priors.
- (4) Interprets: plausible `C0` and half-lives, nothing absurd.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit settings, log parameterisation, `cores=1` noted.
- (3) Justifies the settings (clean geometry; multiprocess hang).

### Step 5 — Computational diagnostics & identifiability (12 pts)
- (4) Reports R-hat, ESS, divergences.
- (5) Produces and reads the **`(k, V)` pair plot**; reports `corr(k,V)` and the
  better-identified `CL = k*V`.
- (3) States remedies: fix the design / tighten priors for a ridge; tighten solver
  tolerance for stiff genuine ODEs.

### Step 6 — Posterior predictive checks (8 pts)
- (4) PPC overlay of predictive curves on the data.
- (4) Reads it; notes what a systematic miss (curvature) would imply (two-compartment).

### Step 7 — Model criticism & the ODE solver (10 pts)
- (6) Fits the same model with `pymc.ode.DifferentialEquation` (tiny settings) and
  shows it agrees with the analytic fit.
- (4) Makes the **compute cost** explicit and argues the closed-form choice.

### Step 8 — Decision & communication (8 pts)
- (4) Reports half-life and clearance with credible intervals.
- (4) Communicates these as dosing-relevant quantities for a pharmacologist.

---

## Correctness tier (20 points)

### SBC (8 pts)
- (4) `sbc.py` runs the prior->simulate->refit->rank loop on `k` (analytic), light.
- (4) `SBC_REPORT.md` reports the uniformity test, interprets it, and explains the
  analytic-model compute trade-off and the calibration-vs-identifiability distinction.

### Prior sensitivity (6 pts)
- (3) Refits under >=3 priors; compares posteriors and `corr(k,V)`.
- (3) Concludes correctly: robust under a good design, but the prior is load-bearing
  for identifiability (corr grows as prior loosens).

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes the three seeded bugs: late-only design,
  vague priors, and reporting the factors instead of the identified combination.

---

## Extension prompt (10 points, open-ended)

> **Break the closed form: saturable (Michaelis-Menten) elimination.** Replace
> first-order elimination with `dC/dt = -Vmax*C/(Km + C)`, which has **no** closed
> form, and regenerate data in a regime that is mostly linear (`C << Km`). Fit it
> with `pymc.ode.DifferentialEquation` and show that `Vmax` and `Km` are
> practically non-identifiable from linear-regime data alone (the classic
> `Vmax/Km` ridge). Then add data from the saturated regime (`C >> Km`) and show
> identifiability is restored. Discuss solver tolerance and sampling cost.

Grade on: (4) a correct Michaelis-Menten ODE model that samples; (3) a pair plot /
diagnostic that **detects** the `Vmax/Km` ridge in the linear regime; (3) a coherent
discussion of design (regime coverage), solver tolerance, and compute cost.
