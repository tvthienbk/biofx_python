# Workflow Manual — Project 16: Trolley (ordered-categorical / OrderedLogistic)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 4 (Advanced) · **Model family:** Ordered logistic regression (cutpoints)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P16 introduces the **ordered-categorical likelihood**: a 1–7 rating is not
> a count and not continuous — it is ordinal. The craft skills are **cutpoints on a latent logistic scale**,
> mapping responses `1..7 → 0..6`, and a **category-frequency posterior predictive check**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate 1500 ordinal responses (7 levels) from known cutpoints and `bA = −0.7`; fit; check recovery.
- **Observed:** bA recovered (**−0.719**, 90% HDI [−0.87, −0.58]); R̂ = 1.00. Truth inside HDI.
- **Pass criterion:** bA inside 90% HDI. **Remedy:** fix the cutpoint prior / ordered transform if it misses.
- **Note:** the ordered cutpoints need an ordered starting point — passed via `pm.sample(initvals={"cut": linspace})`,
  **not** as a variable `initval` (the latter breaks `sample_prior_predictive` in PyMC 5.28).

## Stage 1 — Problem & question
How do **action**, **intention**, and **physical contact** change the rated permissibility (1=low, 7=high)
of an act in a moral dilemma? Target: `bA, bI, bC` (expected negative). Unit: one rating by one participant.

## Stage 2 — Data & exploration
Trolley (`;`-delimited) → **9930 rows**, response 1–7, mean **4.20**. Observed level frequencies:
1:0.128, 2:0.092, 3:0.108, 4:**0.234** (mode), 5:0.147, 6:0.146, 7:0.146. We pass `response − 1` (0–6).

## Stage 3 — Model specification (OrderedLogistic)
$$\text{resp}_i-1 \sim \mathrm{OrderedLogistic}(\eta_i, \kappa),\ \eta_i = b_A A_i + b_I I_i + b_C C_i,\ \kappa\sim\mathrm{Normal}(0,1.5)\,\text{(ordered)},\ b_\bullet\sim\mathrm{Normal}(0,0.5).$$
The 6 ordered **cutpoints** slice the latent logistic scale into 7 categories; larger `eta` shifts mass up.

## Stage 4 — Prior predictive on the OUTCOME scale (category frequencies)
- **Observed:** prior predictive frequencies span all 7 levels (e.g. [0.30, 0.07, 0.08, 0.09, 0.06, 0.08, 0.33]) —
  a sensible, if U-shaped, spread, not all mass in one level.
- **Pass criterion:** the prior implies a usable spread over the 7 categories. **Remedy:** widen/narrow the cutpoint prior.

## Stage 5 — Fit (FULL model, all 9930 rows)
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=16, initvals={"cut": linspace})`.
**~249 s on the full n = 9930 — no subsampling needed**; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for all coefficients and cutpoints; ESS-bulk 3080–5346; **0 divergences**; BFMI 1.03–1.20. All pass.

## Stage 7 — Interpretation (log-odds / odds ratios)
- **bA = −0.697** (94% HDI [−0.771, −0.619]), odds multiplier **0.50**;
- **bI = −0.713** (HDI [−0.784, −0.649]), multiplier **0.49**;
- **bC = −0.945** (HDI [−1.031, −0.849]), multiplier **0.39** — contact has the strongest (most negative) effect.
All three lower the odds of a higher-or-equal permissibility rating; all tightly estimated and clearly negative.

## Stage 8 — Category-frequency PPC [the key check]
- **Observed:** predicted vs observed frequency of each of the 7 levels match almost exactly — per-level
  bayes-p between 0.31 and 0.71, and **max absolute frequency discrepancy = 0.003**. The ordinal model
  reproduces the full response distribution, including the mode at 4.

## Stage 9 — Comparison: full vs cutpoints-only (LOO)
- **Observed:** **full wins decisively.** `elpd_diff` = **382.3** with `dse` = 27.6 → **13.8 SE**; stacking weight
  0.99 on full. Max Pareto-k̂ = **0.06** < 0.70 → LOO reliable. Action+intention+contact add real predictive power.

## Stage 10 — Power-scaling prior sensitivity (bA)
- **Observed:** E[bA] = −0.698 / −0.697 / −0.696 across α ∈ {0.8,1,1.25} — essentially fixed; data-driven.

## SBC — Simulation-Based Calibration on `bA` [Tier 4, recommended — done]
- **Command:** 100 sims on a 1000-row simulated set (action only), cheap sampler; rank true `bA`.
- **Observed:** 100 sims in **398 s**; **chi-square uniformity p = 0.305** (> 0.05) → ranks uniform ⇒ calibrated.

## Stage 11 — Model expansion / iteration
Add the **action×intention** and **contact×intention** interactions (the canonical Trolley analysis) and
varying intercepts per participant `id`. The ordinal machinery is unchanged; only `eta` grows.

## Stage 12 — Decision & communication
**Headline:** *action, intention, and physical contact each clearly lower the rated permissibility of an act
(odds multipliers 0.50, 0.49, 0.39), they decisively out-predict a bare ordered-intercept model (13.8 SE by
LOO), and the category-frequency PPC tracks all 7 levels to within 0.003.* Limitation: no participant-level
clustering yet — ratings are correlated within person.

---
*SBC recommended at Tier 4 and done — PASSED (p = 0.31). Full model fit on all 9930 rows (~249 s), within the
Tier-4 budget; no subsampling required. Every stage lists command · observed output · pass criterion · failure remedy.*
