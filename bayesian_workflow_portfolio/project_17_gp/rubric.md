# Grading Rubric — Project 17: Nonparametric Curves (Gaussian Process)

Total: **100 points** across the eight workflow steps, a correctness tier (SBC,
prior sensitivity, debugging), and an open-ended extension.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, reproducible (fixed seed), exposes `truth` (`sigma`) and the
  latent `f_true` for recovery checks.
- (3) States the four assumptions: smooth `f` (ExpQuad), homoscedastic Gaussian
  noise, noise-free inputs, zero mean function.

### Step 2 — Model specification with justified hyperpriors (12 pts)
- (3) Correct marginal GP: ExpQuad kernel, Normal likelihood, `pm.gp.Marginal`.
- (6) **Length-scale prior justified, not just stated.** Full credit requires
  explaining that `InverseGamma` is informative and zero-avoiding and *why* that
  prevents the `ell ↔ eta` trade-off. A vague prior with no discussion ≤ 2/6.
- (3) `eta` and `sigma` priors stated with rationale.

### Step 3 — Prior predictive checks (8 pts)
- (4) Draws functions from the GP prior.
- (4) Interprets: curves are smooth but non-trivially varying — not flat, not
  jagged — i.e. the length-scale prior implies plausible curves.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit reproducible settings, `target_accept` raised, `cores=1`
  noted for this environment.
- (3) Justifies the settings (curvature → higher `target_accept`; compute → small N).

### Step 5 — Computational diagnostics (12 pts)
- (4) Reports R-hat, ESS, divergences.
- (4) Produces and reads the **`(ell, eta)` pair plot**; identifies a compact blob
  as healthy vs a ridge as pathological.
- (4) States remedies: tighten length-scale prior (modelling), raise
  `target_accept` (sampler), more draws for ESS.

### Step 6 — Posterior predictive checks (10 pts)
- (5) Reconstructs the curve with posterior mean + 94% band.
- (5) Confirms the band contains the **true** curve and reports curve MAE/RMSE.

### Step 7 — Model criticism & comparison (8 pts)
- (5) Recovers `sigma`; checks residual sd matches inferred/true noise.
- (3) Discusses GP-vs-parametric comparison and why the GP avoids the shape
  commitment.

### Step 8 — Decision & communication (8 pts)
- (4) Derives a decision-relevant quantity from the curve (crossing point / midpoint)
  **with** uncertainty.
- (4) Communicates it for a collaborator, including the extrapolation caveat.

---

## Correctness tier (20 points)

### SBC (8 pts)
- (4) `sbc.py` runs the prior→simulate→refit→rank loop on `sigma`, kept light.
- (4) `SBC_REPORT.md` reports the uniformity test and interprets the histogram
  (∪ overconfident, ∩ underconfident, slope biased), acknowledging the light-sim
  compute trade-off.

### Prior sensitivity (6 pts)
- (3) Refits under ≥3 length-scale priors and compares posteriors + divergences.
- (3) Concludes correctly: robustness is purchased by the length-scale prior;
  the vague `IG(1,1)` re-opens the ridge.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes the three seeded bugs: vague `HalfFlat`
  length-scale prior, low `target_accept`, and reading marginals instead of the
  joint pair plot.

---

## Extension prompt (10 points, open-ended)

> **Make the noise depend on the input.** Modify `data/generate_data.py` so the
> noise scale grows with `x` (e.g. `sigma(x) = 0.1 + 0.05*x`). Refit the
> homoscedastic GP from this project and show, via the residuals and the PPC,
> where it breaks (bands too wide at low `x`, too narrow at high `x`). Then build a
> **heteroscedastic** GP — put a second GP prior on `log sigma(x)` — and show it
> fixes the residual structure. Discuss the new identifiability concerns (the
> signal GP and the noise GP can now trade off).

Grade on: (4) a correct heteroscedastic DGP and a homoscedastic-model PPC that
**detects** the misfit; (3) a working heteroscedastic GP; (3) a coherent discussion
of the added signal-vs-noise identifiability tension.
