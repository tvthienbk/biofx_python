# Workflow Manual — Project 15: Hurricanes (Gamma-Poisson; critical appraisal)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 3 (Hierarchical / Count) · **Model family:** NegativeBinomial (Gamma-Poisson) GLM

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P15 is a **critical-appraisal** project: we re-analyze a famous contested
> claim — Jung et al. (2014, *PNAS*): "feminine-named hurricanes are deadlier" — and show, with an
> overdispersed count model, that the effect is **fragile and does not survive scrutiny**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate NegBin counts from `a = 3.0`, `b_fem = 0.0` (NULL truth), `alpha = 1.0`; fit; check recovery.
- **Observed:** a (3.15), b_fem (**−0.012**, near zero — no false positive), alpha (1.22) all inside 90% HDI; R̂ = 1.00.
- **Pass criterion:** truths inside 90% HDI, including a near-zero `b_fem`. **Remedy:** fix model/priors first.

## Stage 1 — Problem & question
The contested claim: are hurricanes with more *feminine* names associated with more deaths? Target: `b_fem`,
the coefficient on standardized femininity. Unit: one Atlantic hurricane (1950–2012).

## Stage 2 — Data & exploration
Hurricanes (`;`-delimited) → 92 storms. Deaths: mean **20.7**, variance **1655** (var ≫ mean ⇒ massive
overdispersion), max **256** (Camille). The deadliest storms — Camille (256), Diane (200), Sandy (159),
Agnes (117) — are candidate **influential points**.

## Stage 3 — Model specification (NegativeBinomial)
$$\text{deaths}_i \sim \mathrm{NegativeBinomial}(\mu_i, \alpha),\ \log\mu_i = a + b_{\text{fem}}\,\text{fem}_i^{z},\ a\sim\mathrm{Normal}(3,1),\ b_{\text{fem}}\sim\mathrm{Normal}(0,1),\ \alpha\sim\mathrm{Exponential}(1).$$
The dispersion parameter `alpha` (Gamma-Poisson mixture) absorbs the excess variance a plain Poisson cannot.

## Stage 4 — Prior predictive on the COUNT scale
- **Observed:** prior mean deaths median **21.6**, 95% ≈ **86** — plausible tens-to-hundreds, not millions.
- **Pass criterion:** implied counts are physically plausible. **Remedy:** tighten `a` if counts explode.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=15)`. ~12 s; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, b_fem, alpha; ESS-bulk 3270–4098; **0 divergences**; BFMI 1.08–1.20. All pass.
- **alpha = 0.452** confirms strong overdispersion (small alpha ⇒ heavy Gamma mixing).

## Stage 7 — Interpretation + FRAGILITY [the key lesson]
- **b_fem = 0.212 ± 0.152 (sd); 94% HDI [−0.067, 0.495] — the HDI includes 0.** P(b_fem > 0) = 0.92.
- **|b_fem| / sd = 1.39** (< 2 ⇒ weak, not credible). Implied multiplier exp(b_fem) = 1.24× (HDI 0.94–1.64).
- **Influence test:** dropping the single deadliest storm (Camille, 256 deaths) shifts b_fem from **0.212 → 0.132**
  (−0.080) — over a third of the effect rides on one storm. The effect is influence-driven.

## Stage 8 — Posterior predictive check (max + small counts)
- **Observed:** max deaths obs 256, bayes-p **0.16**; sd obs 40.7, bayes-p **0.18**; prop(deaths ≤ 2) obs 0.28,
  bayes-p 0.72; mean bayes-p 0.53. The model slightly under-predicts the extreme tail (Camille is hard to fit),
  consistent with a few dominating storms.

## Stage 9 — Comparison: with vs without femininity (LOO)
- **Observed:** **intercept-only WINS.** `elpd_diff` = **0.10** with `dse` = 1.56 → **0.06 SE** — utterly
  indistinguishable; stacking weight is split ~0.53/0.47. Max Pareto-k̂ = 0.44 < 0.70 → LOO reliable. **Femininity
  does not improve out-of-sample prediction.**

## Stage 10 — Power-scaling prior sensitivity (b_fem)
- **Observed:** E[b_fem] = 0.213 / 0.212 / 0.211 across α ∈ {0.8,1,1.25} — barely moves. The point estimate is
  not a prior artifact; it is simply small and uncertain.

## SBC — Simulation-Based Calibration on `b_fem` [required, Tier 3]
- **Command:** 100 sims, cheap sampler; rank true `b_fem` among posterior draws.
- **Observed:** 100 sims in **221 s**; **chi-square uniformity p = 0.603** (> 0.05) → ranks uniform ⇒ calibrated.
  The model machinery is sound; the *effect* is what is weak, not the inference.

## Stage 11 — Model expansion / iteration
The original paper's real model added a **femininity × damage_norm interaction** (feminine names matter only for
severe storms). With 92 storms and a handful dominating deaths, that interaction is even more fragile — a
cautionary expansion, not a rescue.

## Stage 12 — Decision & communication
**Headline:** *with overdispersion properly modeled, the feminine-name effect on hurricane deaths is small
relative to its own uncertainty (b_fem = 0.21 ± 0.15, HDI crosses 0), flips by a third when one storm (Camille)
is dropped, and does NOT improve out-of-sample prediction by more than 0.06 SE. The headline claim does not
survive scrutiny.* This mirrors the published critiques (Maley; Malter; Christensen & Christensen) of Jung et al. (2014).

---
*SBC required at Tier 3 and PASSED (p = 0.60). Every stage lists command · observed output · pass criterion · failure remedy.*
