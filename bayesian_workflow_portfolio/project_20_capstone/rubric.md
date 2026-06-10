# Grading Rubric — Project 20: Capstone (Decision Under Uncertainty)

Total: **100 points** across the eight workflow steps, a correctness tier (SBC,
prior sensitivity, debugging), and an open-ended extension. As the capstone, the
decision step (Step 8) carries the most weight.

---

## Workflow steps (70 points)

### Step 1 — Problem & data-generating story (6 pts)
- (3) DGP documented, reproducible, exposes truths (`mu`, `tau`, `theta_j`,
  true-best) and **unequal replication** that creates the winner's curse.
- (3) States the four assumptions: exchangeability, shared `sigma`, conditional
  independence, utility increasing in effect.

### Step 2 — Model specification with justified priors (10 pts)
- (4) Correct hierarchical model, **non-centred**, with the funnel justification.
- (4) **Partial pooling justified** as the cure for the winner's curse (vs complete
  / no pooling). A model with no discussion of pooling <= 2/4.
- (2) `mu`, `tau`, `sigma` priors stated.

### Step 3 — Prior predictive checks (6 pts)
- (3) Simulates compound screens from the priors.
- (3) Interprets: plausible effect spread, not degenerate or extreme.

### Step 4 — Inference / NUTS settings (6 pts)
- (3) NUTS with explicit settings, non-centred, `cores=1` noted.
- (3) Justifies the settings (hierarchical geometry; multiprocess hang).

### Step 5 — Computational diagnostics (10 pts)
- (4) Reports R-hat, ESS, divergences (0).
- (6) Produces and reads the **shrinkage plot** (posterior vs raw means, by
  replicate count); explains that low-`n` compounds are shrunk most.

### Step 6 — Posterior predictive checks (6 pts)
- (3) PPC over the replicate data.
- (3) Reads it; notes what a miss (per-compound `sigma`) would imply.

### Step 7 — Model comparison via LOO (8 pts)
- (5) Fits the complete-pooling comparator and compares via LOO (`az.compare`).
- (3) Interprets: hierarchical wins when compounds differ; LOO would flag the
  reverse if `tau ~ 0`.

### Step 8 — DECISION under uncertainty (18 pts) — capstone core
- (6) Defines an explicit **utility/loss** (e.g. `U_j = theta_j - cost`).
- (6) Computes **expected utility**, **probability-of-being-best**, and **expected
  regret** per compound; recommends the **min-expected-regret** compound.
- (3) Shows the decision can differ from the argmax of the posterior mean AND
  overturns the raw-mean winner's curse.
- (3) Communicates the recommendation **with** `P(best)` and the runner-up (advance
  one vs two).

---

## Correctness tier (20 points)

### SBC (7 pts)
- (4) `sbc.py` runs the prior->simulate->refit->rank loop on `tau`, light, non-centred.
- (3) `SBC_REPORT.md` reports the uniformity test, interprets it, and ties `tau`
  calibration to trust in the decision.

### Prior sensitivity (7 pts)
- (4) Refits under >=3 `tau` priors and compares — including whether the
  **recommended compound** changes (decision robustness, not just `tau`).
- (3) Concludes correctly: robust to reasonable priors, over-tight `tau` over-pools.

### Debugging exercise (6 pts)
- (2 each) Identifies and fixes the three seeded bugs: raw-mean ranking
  (winner's curse), stopping at the posterior (no loss function), centred hierarchy
  (funnel).

---

## Extension prompt (10 points, open-ended)

> **Value of information: which compound should you replicate next?** Extend the
> decision layer to compute, for each compound, the **expected reduction in regret**
> from collecting one more batch of replicates (a one-step expected-value-of-sample-
> information calculation): simulate plausible new data from the posterior
> predictive, refit (or approximate), and measure how much the expected regret of
> the final decision drops. Recommend not just which compound to advance, but which
> to **measure more**. Discuss when it is worth paying for more data versus deciding
> now.

Grade on: (4) a correct posterior-predictive-based EVSI-style calculation; (3) a
recommendation of which compound to replicate that is justified by the numbers;
(3) a coherent discussion of the measure-more-vs-decide-now trade-off.
