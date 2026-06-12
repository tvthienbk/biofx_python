# Workflow Manual — Project 12: Radon (varying-intercept multilevel) + group predictor + LOGO-CV

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 3 (Multilevel) · **Model family:** Varying-intercept Gaussian regression with group predictor

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P12 is the canonical multilevel regression: a **county-varying intercept**
> with a **county-level predictor** (soil uranium). Its central craft skills are the **pooling spectrum**
> (shrinkage of small counties) and the honest cross-validation for grouped data — **leave-one-GROUP-out
> CV (LOGO)**. Tier 3 adds **SBC**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.
- Säilynoja et al. (2022). *Graphical Test for Discrete Uniformity.* Stat. Comput. 32.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate from `g0=1.4, g_u=0.7, b_floor=−0.65, sigma_a=0.35, sigma=0.75`; fit the non-centered model; `az.summary(hdi_prob=0.9)`.
- **Observed:** all five recovered (g0 1.45, g_u 0.76, b_floor −0.61, sigma_a 0.30, sigma 0.75) inside their 90% HDIs; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
How much lower is radon on the first floor than the basement, once each county has its own baseline and we
account for county soil uranium? Targets: `b_floor` (floor effect) and `g_u` (uranium slope). Unit: one home.

## Stage 2 — Data & exploration
Minnesota radon (`,`-delimited), **919 homes in 85 counties**; median **5 homes/county**, 11 counties with
≤2 homes. The county-level predictor `log_uranium = log(Uppm)` is constant within county. Most counties have
few homes — borrowing strength matters.

## Stage 3 — Model specification (non-centered)
$$y_i \sim \mathrm{Normal}(a_{c[i]} + b_{\mathrm{floor}}\,\mathrm{floor}_i,\ \sigma),\quad a_c = \gamma_0 + \gamma_u u_c + \sigma_a z_c,\ z_c\sim\mathrm{Normal}(0,1).$$
Priors `g0,g_u~Normal(0,2)`, `b_floor~Normal(0,1)`, `sigma_a~HalfNormal(1)`, `sigma~Exponential(1)`.
`u_c` is standardized county log-uranium. The **non-centered** `a_c = … + sigma_a·z_c` avoids the funnel.

## Stage 4 — Prior predictive on the OUTCOME scale (log_radon)
- **Observed:** prior-predictive `log_radon` mean 0.02, sd 3.47, 1–99% [−9.1, 8.8] — wide but covers the observed range [−2.3, 3.9] without absurd values.
- **Pass criterion:** implied outcomes plausible. **Remedy:** tighten `sigma_a`/`g` priors if they explode.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.95, seed=12)`. ~20 s; **0 divergences** (non-centering works).

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 (max 1.000); ESS-bulk ≥ **1169** (sigma_a) to ~4300; **0 divergences**; BFMI 0.70–0.76. All pass.

## Stage 7 — Interpretation (original units) + the pooling spectrum
- **b_floor = −0.636** (94% HDI −0.764 to −0.515) log units → **×0.53** on the radon scale: first-floor homes have about half the radon of basements.
- **g_u = 0.267** (94% HDI 0.204 to 0.333) per +1 SD county log-uranium — higher-uranium counties have higher baselines.
- **Shrinkage:** the 3 single-home counties move from their raw means (2.50, 1.39, 2.24) toward the grand mean **1.26** (to 1.81, 1.59, 1.69) — partial pooling tempers noisy small-n counties.

## Stage 8 — Posterior predictive check
- **Discrepancy stats:** mean p = 0.49, sd p = 0.51, max p = 0.42 — good fit; min p = 0.99 (the lower tail is slightly heavier than the Normal allows, a minor note).

## Stage 9 — naive LOO vs Leave-One-GROUP-Out CV (LOGO) [the key skill]
- **Naive LOO:** elpd = −1027.5 ± 28.9; max Pareto-k̂ = 0.57 < 0.70 (reliable). But naive LOO holds out one *home* while keeping other homes of the **same county**, so it has effectively seen the county.
- **LOGO** (refit dropping a whole county, predict its homes from `g0 + g_u·u_c` and the population SD) on **5 held-out counties** (codes 1, 18, 25, 69, 79; 382 homes): LOGO per-home elpd **−1.075** vs naive LOO **−1.060** on the same homes — LOGO is **worse by 5.8 elpd**. Naive LOO is optimistic for a genuinely **new** county; LOGO is the honest estimate.

## Stage 10 — Power-scaling prior sensitivity (b_floor, g_u)
- **Observed:** E[b_floor] = −0.6369 / −0.6363 / −0.6355 and E[g_u] = 0.2673 across α ∈ {0.8, 1, 1.25} — both essentially fixed; conclusions are data-driven, not prior-driven.

## Stage 11 — SBC on `b_floor` [Tier-3 required]
- **Command:** 100 sims; each draws all parameters from the priors, simulates `log_radon`, refits with a cheap sampler (draws=300, tune=300, chains=2); record rank of the prior `b_floor` among 600 posterior draws.
- **Budget note:** with 85 counties each fit is costly; we use the guide's minimum 100 sims with a trimmed 300/300 sampler. Runtime **349 s** — within the Tier-3 < 8 min budget.
- **Observed:** rank histogram flat; **chi-square = 13.6, df = 19, p = 0.806 → uniform (calibrated)**.

## Stage 12 — Decision & communication
**Headline:** *first-floor homes have roughly half the radon of basements (`b_floor` ≈ −0.64 log units,
×0.53), and high-uranium counties have higher baselines (`g_u` ≈ 0.27 per SD). Partial pooling shrinks
small counties toward the uranium-informed line; naive LOO is optimistic for predicting a* **new** *county,
so LOGO (−1.075 vs −1.060 per home) is the honest measure.* Limitation: single-home counties carry almost
no within-county information — their estimates lean heavily on the uranium model.

---
*SBC at Tier 3 used 100 sims / trimmed sampler to fit the budget (documented in Stage 11). Every stage lists command · expected output · pass criterion · failure remedy.*
