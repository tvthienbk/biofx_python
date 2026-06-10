# Grading Rubric — Project 01: Estimating a Proportion

Total: **100 points**, allocated across the eight workflow steps, plus a
correctness tier (SBC, prior sensitivity, debugging) and an open-ended extension.
Use this rubric to grade a student's reproduction or extension of the project.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) Data-generating process is documented, reproducible (fixed seed), and exposes
  a `truth` dict for later recovery checks.
- (3) The three modeling assumptions are stated explicitly: (a) runs independent,
  (b) `theta` constant across runs, (c) outcomes truly binary.

### Step 2 — Model specification with justified priors (10 pts)
- (4) Likelihood correctly specified: `y_i ~ Bernoulli(theta)` (or
  `k ~ Binomial(n, theta)`).
- (6) Prior is **justified, not just stated**. Full credit requires explaining why
  `Beta(2,2)` is preferred over `Beta(1,1)` ("flat is not uninformative"). A bare
  `Beta(1,1)` with no discussion earns at most 2/6.

### Step 3 — Prior predictive checks (8 pts)
- (4) Simulates datasets from the prior and inspects the implied success count `k`.
- (4) Interprets the result: the spread is sensible (mild central concentration),
  no pathological mass piled at the 0/1 edges.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) Uses NUTS with explicit, reproducible settings (`draws`, `tune`, `chains`,
  `random_seed`).
- (3) Justifies ≥2 (ideally 4) chains and adequate tuning, and explains why (R-hat
  needs multiple chains; tuning lets NUTS adapt).

### Step 5 — Computational diagnostics (12 pts)
- (4) Reports R-hat (≈1.00), ESS bulk/tail (≳400), and divergence count (0).
- (4) Produces and reads a trace plot ("fuzzy caterpillars", well-mixed chains).
- (4) States the remedies for failures: raise `target_accept` for divergences,
  increase `tune`/`draws` for low ESS, suspect multimodality/non-identifiability if
  R-hat stays high.

### Step 6 — Posterior predictive checks (10 pts)
- (4) Produces a PPC (`az.plot_ppc`) comparing observed to posterior-predictive
  replicates.
- (3) Computes a Bayesian p-value and reads it (near 0.5 = good fit).
- (3) Reduces the posterior-predictive array over the **correct (observation)**
  axis — explicitly demonstrating awareness of the dimension trap.

### Step 7 — Model criticism & comparison (8 pts)
- (5) Overlays the MCMC posterior on the **exact conjugate** `Beta(2+k, 2+n-k)` and
  confirms they coincide (using the analytic answer as an oracle).
- (3) Notes that with one model there is no LOO/WAIC comparison yet, and explains
  when comparison becomes relevant (≥2 models).

### Step 8 — Decision & communication (10 pts)
- (4) Reports a point estimate **with** a 94% credible interval.
- (3) Computes a decision-relevant probability, e.g. `P(theta > 0.5 | data)`.
- (3) Translates the posterior into a sentence a non-technical collaborator can act
  on (see `summary_onepager.md`).

---

## Correctness tier (20 points)

### Simulation-Based Calibration (8 pts)
- (4) `sbc.py` draws from the prior, simulates, refits, and records rank statistics.
- (4) `SBC_REPORT.md` reports the uniformity test (chi-square p-value) and reads the
  rank histogram correctly (∪ = over-confident, ∩ = under-confident, slope = biased).

### Prior sensitivity (6 pts)
- (3) Refits under ≥3 priors and compares posteriors.
- (3) Correctly concludes robustness **and** notes that robustness is a property of
  the sample size, not the prior (would break at small `n`).

### Debugging exercise (6 pts)
- (2 each) Correctly identifies and fixes all three seeded bugs in
  `notebook_broken.ipynb`: flat prior, starved sampler, wrong PPC reduction axis.

---

## Extension prompt (10 points, open-ended)

> **Introduce batch effects and watch the simple model fail.** Modify
> `data/generate_data.py` so that the `n` assay runs are split across several
> *batches*, each with its own success sub-rate drawn around the global `theta`
> (e.g. `theta_batch ~ Beta` centred on `theta`, with extra-binomial dispersion).
> Refit the i.i.d. `Beta(theta)` model from this project and show, via the
> posterior predictive check, where it *breaks*: the observed dispersion of
> per-batch success counts should fall outside the model's posterior-predictive
> spread. Then sketch (in words or code) the hierarchical model that would fix it.

Grade on: (4) a correct over-dispersed DGP, (3) a PPC or discrepancy statistic that
**detects** the misfit rather than merely asserting it, (3) a coherent description
of the hierarchical remedy. This previews the hierarchical projects later in the
portfolio.
