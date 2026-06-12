# Workflow Manual — Project 06: Switching wells ~ arsenic + distance (logistic regression)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 2 (GLMs) · **Model family:** Bernoulli / logit GLM (logistic regression)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P06 is the first **GLM**; its craft skills are the **logit link** and
> **odds-ratio** interpretation, the **prior predictive on the probability scale**, and a **binary PPC**
> via a calibration plot.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `y ~ Bernoulli(invlogit(0.3 + 0.9·ars − 0.6·dist))` on standardized predictors; fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a = 0.379, b_ars = 0.932, b_dist = −0.703 — **all three truths inside their 90% HDI**;
  R̂ = 1.00, ESS-bulk > 3100.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
What makes a Bangladeshi household **switch** away from an arsenic-contaminated well — the water's danger
(arsenic) and/or the distance to the nearest safe well? Target: the odds ratios. Unit: one household.

## Stage 2 — Data & exploration
wells.csv (**comma-delimited**), **3020 households**, overall **switch rate = 0.575**. arsenic mean 1.66
(range 0.51–9.65); distance mean 48.3 m (range 0.4–339.5). We **standardize** `arsenic` and `dist` to
mean 0 / sd 1 so coefficients are comparable and priors interpretable.

## Stage 3 — Model specification
$$\mathrm{switch}_i \sim \mathrm{Bernoulli}(p_i),\quad \mathrm{logit}(p_i)=a+b_{ars}\,\mathrm{ars\_z}_i+b_{dist}\,\mathrm{dist\_z}_i,$$
$$a\sim\mathrm{Normal}(0,1.5),\quad b_{ars},b_{dist}\sim\mathrm{Normal}(0,1).$$
On standardized predictors, `Normal(0,1)` on a logit slope keeps the odds ratio `exp(b)` in a plausible
band (≈ 1/7 to 7 per sd).

## Stage 4 — Prior predictive on the PROBABILITY scale [the GLM lesson]
- **Command:** push prior draws through `invlogit`; histogram the implied P(switch).
- **Observed:** prior-predictive p has mean 0.48, with only **7% below 0.05 and 7% above 0.95** — mass
  spread across (0, 1), **no piling at the extremes**. This is the signature of a sane logit prior.
- **Pass criterion:** probabilities cover (0,1) without piling at 0/1. **Remedy:** shrink the slope priors if they do.

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=6)`. ~17 s including the
distance-only model and posterior predictive; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, b_ars, b_dist; ESS-bulk ≈ 3000–3400; **0 divergences**; BFMI ≈ 0.98–1.17. All pass.

## Stage 7 — Interpretation: odds ratios
- **arsenic:** coef **+0.510** (94% HDI +0.427, +0.600) → **OR 1.67 per +1 sd** (94% HDI 1.53, 1.82) —
  more contaminated water sharply raises the odds of switching.
- **distance:** coef **−0.346** (94% HDI −0.421, −0.265) → **OR 0.71 per +1 sd** (94% HDI 0.66, 0.77) —
  a farther safe well modestly lowers the odds of switching.
Arsenic is the stronger driver.

## Stage 8 — PPC for binary data: switch rate + calibration
- **Discrepancy stat (overall proportion switched):** observed 0.575 vs posterior-predictive mean 0.575,
  **bayes-p = 0.51** — perfectly centred.
- **Calibration:** across predicted-probability deciles, the max |observed − predicted| is just **0.039** —
  the model is well calibrated; deciles fall on the 45° line.

## Stage 9 — Comparison: `switch~dist` vs `switch~dist+arsenic` (PSIS-LOO)
- **Observed:** adding arsenic is **decisive** — `elpd_diff` = **71.73 ± 12.13 SE** (≈ 6 SE) in favour of
  `dist+arsenic`; stacking weight 0.94. **Max Pareto-k̂ = 0.16 < threshold 0.70** → LOO fully reliable.

## Stage 10 — Power-scaling prior sensitivity (b_ars, b_dist)
- **Observed:** E[b_ars] = 0.510 / 0.510 / 0.509 and E[b_dist] = −0.346 throughout α ∈ {0.8, 1.0, 1.25} —
  completely flat. With n = 3020 the likelihood dominates; conclusions are data-driven.

## Stage 11 — Model expansion / iteration
The ROS analysis adds an **arsenic × distance interaction**, an **education** term, and a **non-linear**
(log-arsenic / spline) effect. The interaction is the natural immediate expansion.

## Stage 12 — Decision & communication
**Headline:** *households switch wells mainly because of **how contaminated their water is** — each +1 sd
of arsenic multiplies the odds of switching by ≈ **1.67** — and are modestly deterred by **distance**
(OR ≈ 0.71 per sd); arsenic dominates, and a model without it predicts switching far worse
(elpd_diff 72 ± 12).* Limitation: observational; standardized arsenic is right-skewed, so a log/spline
term may fit the low-arsenic tail better.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
