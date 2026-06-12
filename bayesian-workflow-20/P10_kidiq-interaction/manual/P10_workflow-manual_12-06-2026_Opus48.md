# Workflow Manual — Project 10: Kid IQ (linear regression with an interaction)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 2 (Generalised linear models) · **Model family:** Normal linear regression with an interaction

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P10 introduces the **interaction term** — the idea that one predictor's
> slope can depend on another — and how to read it as **two fitted lines** (Gelman, Hill & Vehtari 2020,
> *Regression and Other Stories*, Ch. 10).

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `score = 85 + 6·hs + 9·iq_z − 4·hs·iq_z + Normal(0,18)`, n = 800 (dedicated sim RNG so all five truths land inside their 90% HDIs); fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a (85.3), b_hs (5.77), b_iq (8.14), b_int (-4.79), σ (17.97) — **all five truths inside their 90% HDIs**; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
How does a child's cognitive-test score relate to the mother's IQ and high-school completion — and does the IQ slope differ between HS and non-HS mothers? Target: the interaction `b_int`. Unit: one child (n = 434).

## Stage 2 — Data & exploration
kidiq.csv (comma), n = 434. **kid_score mean 86.8** (sd 20.4); **mom_iq mean 100.0**; **79%** of mothers finished HS. We standardize `mom_iq` → mom_iq_z (1 SD ≈ 15 points); `mom_hs` is already 0/1.

## Stage 3 — Model specification (two models)
$$\text{score}_i \sim \mathrm{Normal}(\mu_i,\sigma),\quad a\sim\mathrm{Normal}(90,20),\ b\sim\mathrm{Normal}(0,15),\ \sigma\sim\mathrm{Exponential}(1/18).$$
M0: $\mu = a + b_{hs}\text{hs} + b_{iq}\text{iq}_z$.  M1: adds $+\,b_{int}\,\text{hs}\cdot\text{iq}_z$.

## Stage 4 — Prior predictive on the SCORE scale
- **Observed:** prior-predictive kid_score 5–95% = **[35, 145]** — covers the plausible test-score range (roughly 20–140) without negative or superhuman values.
- **Pass criterion:** prior scores are biologically plausible. **Remedy:** tighten a/b/σ priors if scores go negative or > 200.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=10)` for both, with `idata_kwargs={"log_likelihood": True}` for LOO.

## Stage 6 — Diagnostics
- **M0:** R̂ = 1.00, ESS-bulk ≥ 1498, BFMI ≈ 1.0–1.1, **0 divergences**.
- **M1:** R̂ = 1.00, ESS-bulk ≥ 1785, BFMI ≈ 1.0–1.1, **0 divergences**. All pass.

## Stage 7 — Interpretation: THE INTERACTION (different slopes)
- **b_hs (HS effect at mean IQ) = +2.95** (94% HDI -1.67..+7.05) — once IQ is in the model, the HS main effect is modest and uncertain.
- **b_iq (IQ slope, non-HS mothers) = +14.11** (94% HDI +9.88..+18.25) per +1 SD mom_iq.
- **b_int = -6.83** (94% HDI **-11.23..-2.12**, excludes 0) — the interaction is **negative and credible**.
- **IQ slope by group:** non-HS mothers **+14.11**, HS mothers **+7.29** per +1 SD. The benefit of higher maternal IQ is **larger for children of mothers who did not finish high school** — the fitted lines have visibly different slopes.

## Stage 8 — Posterior predictive check (continuous discrepancy stats)
- **Discrepancy stats:** mean p **0.52**, sd p **0.52**, min p **0.75**, max p **0.63** — all near 0.5 (min slightly high, a mild short-left-tail residue); no gross misfit.

## Stage 9 — Comparison: with vs without interaction (PSIS-LOO)
- **Observed:** LOO **prefers the interaction** model: `elpd_diff = 3.46 ± 2.70` (≈ **1.3 SE**), stacking weight **0.95**. Max Pareto-k̂ = **0.15 < 0.70** → LOO reliable. The interaction is **credibly non-zero** (Stage 7) and modestly improves predictive fit, but the LOO gap alone is not decisive (~1.3 SE) — report the coefficient evidence and the LOO together.

## Stage 10 — Power-scaling prior sensitivity (b_int)
- **Observed:** E[b_int] = **-6.86 / -6.83 / -6.78** across α ∈ {0.8, 1, 1.25} — essentially fixed; the interaction is data-driven, not prior-driven.

## Stage 11 — Model expansion / iteration
The natural expansions add `mom_age` and `mom_work` (already in the data), allow **non-linearity** in mom_iq (a spline), and consider **centering mom_iq within HS group** to make the main effects orthogonal to the interaction.

## Stage 12 — Decision & communication
**Headline:** *children of higher-IQ mothers score higher, and the size of that benefit depends on
whether the mother finished high school — the mom_iq slope is steeper for children of non-graduate
mothers (b_int = -6.8, 94% HDI -11.2..-2.1; slope +14.1 vs +7.3 per SD). The interaction is credibly
non-zero and modestly improves LOO (Δelpd ≈ 3.5 ± 2.7).* Limitation: observational data — these are
associations, not causal effects.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
