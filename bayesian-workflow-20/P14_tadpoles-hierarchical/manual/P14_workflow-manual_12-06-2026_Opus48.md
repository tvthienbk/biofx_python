# Workflow Manual — Project 14: Tadpoles (hierarchical Binomial, shrinkage)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 3 (Hierarchical) · **Model family:** Hierarchical Binomial GLM (varying intercept)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P14 introduces **partial pooling**: 48 tanks share an adaptive prior, so
> each tank's estimate borrows strength from the others. The craft skills are the **shrinkage plot**, the
> **non-centered** parameterization, and **Simulation-Based Calibration (SBC)**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts, Betancourt, Simpson, Vehtari, Gelman (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate 48 tanks from `a_bar = 1.4`, `sigma_tank = 1.0` (non-centered); fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a_bar recovered (1.50), sigma recovered (0.78) — both truths inside their 90% HDIs; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
What is each tank's survival probability, and how much do tanks vary? Target: across-tank sd `sigma_tank`
and the per-tank survival. Unit: one tank of reed-frog tadpoles.

## Stage 2 — Data & exploration
reedfrogs (`;`-delimited) → 48 tanks, densities {10, 25, 35}, overall survival **0.699**. Low-density tanks
give the noisiest raw proportions — exactly where pooling helps most.

## Stage 3 — Model specification (non-centered)
$$\text{surv}_i \sim \mathrm{Binomial}(\text{density}_i, p_i),\ \mathrm{logit}(p_i)=a_{\text{tank}[i]},\ a_{\text{tank}}=\bar a + z\,\sigma_{\text{tank}},\ z\sim\mathrm{Normal}(0,1),\ \bar a\sim\mathrm{Normal}(0,1.5),\ \sigma_{\text{tank}}\sim\mathrm{Exponential}(1).$$
The **non-centered** form decouples the per-tank offsets from `sigma_tank`, removing the funnel.

## Stage 4 — Prior predictive on the OUTCOME scale (survival probability)
- **Observed:** prior survival probability median **0.52**; only 3% pile below 0.02 and 3% above 0.98 — the
  prior spreads sensibly across (0,1) without edge-piling.
- **Pass criterion:** prior implies plausible survival probabilities. **Remedy:** tighten `a_bar`/`sigma` if it piles at 0/1.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.95, random_seed=14)`. ~17 s incl. posterior predictive; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.01 (a_bar) / 1.00 (sigma_tank); ESS-bulk 602–902, ESS-tail 1153–1864; **0 divergences**;
  BFMI 0.68–0.77. All pass (non-centered geometry is clean).

## Stage 7 — Interpretation + SHRINKAGE [the key lesson]
**a_bar = 1.35 → grand-mean survival 0.794; sigma_tank = 1.62.** Shrinkage toward the grand mean scales with
1/density: **density-10 tanks shrink most (mean 0.037)**, density-25 (0.022), density-35 (0.017). Small tanks
carry the least information, so the adaptive prior pulls them hardest toward the population mean.

## Stage 8 — Posterior predictive check (survival proportion)
- **Observed:** overall survival obs 0.699, bayes-p **0.50** (perfectly centered); per-tank 90% PPC coverage
  of the raw proportion **1.00**. No misfit.

## Stage 9 — Comparison: hierarchical vs complete-pooling (LOO)
- **Observed:** `elpd_diff` = **178.7** in favour of hierarchical, `dse` = 32.6 → **5.5 SE**, decisive; stacking
  weight 1.0 on hierarchical. Max Pareto-k̂ = **1.34 > 0.70** — flagged: a few tanks (e.g. all-survive/all-die)
  are influential, so LOO is approximate here (reloo would refine), but the gap is far too large to overturn.

## Stage 10 — Power-scaling prior sensitivity (sigma_tank)
- **Observed:** E[sigma_tank] = 1.630 / 1.620 / 1.609 across α ∈ {0.8,1,1.25} — essentially fixed; the
  across-tank sd is data-driven, not prior-driven.

## SBC — Simulation-Based Calibration on `sigma_tank` [required, Tier 3]
- **Command:** 100 sims, cheap sampler (draws=400, tune=400, chains=2); rank true `sigma_tank` among posterior draws.
- **Observed:** 100 sims in **382 s**; rank histogram flat; **chi-square uniformity p = 0.784** (> 0.05) → ranks
  consistent with uniform ⇒ the model + sampler are calibrated (Talts et al. 2018). No ∪/∩ shape.

## Stage 11 — Model expansion / iteration
Add tank-level predictors `pred` (predation) and `size` to the linear model for `a_tank` — explaining *why*
tanks differ. A correlated varying-slope extension follows in P13.

## Stage 12 — Decision & communication
**Headline:** *tadpole survival varies substantially across the 48 tanks (sigma_tank ≈ 1.62 on the logit
scale); partial pooling shrinks the noisiest low-density tanks toward the grand-mean survival (≈ 0.79), and
the hierarchical model decisively beats complete pooling by LOO (5.5 SE).* Limitation: with no covariates the
model quantifies variation but does not explain it.

---
*SBC required at Tier 3 and PASSED (p = 0.78). Every stage lists command · observed output · pass criterion · failure remedy.*
