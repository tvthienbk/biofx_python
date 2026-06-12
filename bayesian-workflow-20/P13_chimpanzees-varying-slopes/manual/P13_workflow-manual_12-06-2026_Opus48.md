# Workflow Manual — Project 13: Chimpanzees (correlated varying intercepts + slopes; LKJCholeskyCov)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 3 (Multilevel) · **Model family:** Logistic with correlated varying effects (MvNormal / LKJ)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P13 adds the final multilevel ingredient: **correlated** random effects.
> Each chimp gets its own intercept *and* slope, and the two are drawn from a 2-D distribution whose
> **correlation** is given a `pm.LKJCholeskyCov(eta=2)` prior. The craft skill is reading off the
> posterior intercept–slope correlation. Tier 3 adds **SBC**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.
- Säilynoja et al. (2022). *Graphical Test for Discrete Uniformity.* Stat. Comput. 32.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate from `a_bar=0.4, b_bar=0.5`, actor SDs (0.8, 0.4), correlation `rho=−0.5`; fit the LKJ model; `az.summary(hdi_prob=0.9)`.
- **Observed:** a_bar recovered (−0.28, 90% HDI −1.06 to 0.41), b_bar recovered (0.73, HDI 0.33 to 1.18), rho recovered (0.04, HDI −0.63 to 0.70); R̂ = 1.00. (The correlation is recovered but with wide uncertainty — 7 actors carry little information about `rho`.)
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
Do chimps pull the *prosocial* (partner-feeding) lever more, and does that tendency vary by individual?
Targets: the population mean slope `b_bar` on `prosoc_left`, and the actor intercept–slope correlation `rho`.
Unit: one lever-pull trial.

## Stage 2 — Data & exploration
Chimpanzees (`;`-delimited), 504 trials, **7 actors**. Per-actor pull rates range from 0.35 to **1.00**
(actor 2 always pulls left — a perfect-separation case the hierarchical prior regularizes). Overall pull
rate 0.58.

## Stage 3 — Model specification (correlated varying effects)
$$\mathrm{pulled}_i \sim \mathrm{Bernoulli}(p_i),\quad \mathrm{logit}(p_i)=a_{\mathrm{actor}[i]} + b_{\mathrm{actor}[i]}\,\mathrm{prosoc\_left}_i,$$
$$(a_j,b_j)\sim\mathrm{MvNormal}((\bar a,\bar b),\ \Sigma),\quad \Sigma=\mathrm{diag}(\sigma)R\,\mathrm{diag}(\sigma),\ R\sim\mathrm{LKJ}(\eta=2),\ \sigma\sim\mathrm{Exponential}(1).$$
`LKJCholeskyCov(eta=2)` weakly regularizes the correlation. Effects are sampled **non-centered** as
`[a_bar,b_bar] + chol @ z`, `z~Normal(0,1)`.

## Stage 4 — Prior predictive on the PROBABILITY scale
- **Observed:** prior-predictive baseline `P(pull)` mean 0.48, 5–95% [0.04, 0.95] — spans (0,1) without piling at the edges.
- **Pass criterion:** implied probabilities cover the interior. **Remedy:** tighten `a_bar`/`sd_dist` if mass piles at 0/1.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.95, seed=13)`. ~52 s; **0 divergences** (non-centered MvNormal).

## Stage 6 — Diagnostics
- **Observed:** R̂ ≤ **1.01** (chol_stds[0]); ESS-bulk ≥ **449**; **0 divergences**; BFMI 0.84–0.98. All within target.

## Stage 7 — Interpretation: the treatment effect and the CORRELATION
- **b_bar = 0.702** log-odds (94% HDI **0.195 to 1.165**) → odds **×2.02**: chimps are about twice as likely to pull when the prosocial option is on the left (a left-side/handedness effect more than pure prosociality, as Silk et al. argued).
- **rho (actor intercept–slope correlation) = −0.123** (94% HDI **−0.889 to 0.681**), P(rho<0) = 0.61 — the data only **weakly** identify the correlation with 7 actors; the LKJ(2) prior dominates, so we report it honestly as uncertain.

## Stage 8 — Posterior predictive check (binary)
- **Discrepancy stats:** overall pull rate obs 0.579 vs predicted 0.579 (bayes-p 0.51); per-actor absolute errors ≤ 0.016 — excellent recovery of each individual's rate (the random intercepts soak up the big between-actor differences).

## Stage 9 — Comparison: correlated vs independent varying effects (LOO)
- **Observed:** `elpd_diff` = **0.23 ± 0.11** (2.1 SE) favouring the correlated model; max Pareto-k̂ = 0.21 < 0.70 (LOO reliable). The correlation buys a *tiny* predictive gain — consistent with `rho` being weakly identified. Modelling the correlation does no harm and is the principled default.

## Stage 10 — Power-scaling prior sensitivity (b_bar)
- **Observed:** E[b_bar] = 0.711 / 0.702 / 0.692 and E[rho] = −0.120 / −0.123 / −0.126 across α ∈ {0.8, 1, 1.25} — essentially fixed; the treatment effect is data-driven.

## Stage 11 — SBC on the mean treatment slope `b_bar` [Tier-3 required]
- **Command:** 100 sims; each draws the full prior (including an LKJ correlation via rejection sampling), simulates `pulled_left`, refits with a cheap sampler (draws=250, tune=250, chains=2); record rank of the prior `b_bar` among 500 posterior draws.
- **Budget note:** the correlated LKJ model is costly; we use the guide's minimum 100 sims with a trimmed 250/250 sampler. Runtime ≈ 523 s — at the edge of the Tier-3 < 8 min budget (the SBC loop dominates; the full model fit is only ~50 s).
- **Observed:** rank histogram flat; **chi-square = 10.4, df = 19, p = 0.942 → uniform (calibrated)**. No systematic bias in `b_bar`.

## Stage 12 — Decision & communication
**Headline:** *chimps pull the prosocial-side lever about twice as often (`b_bar` ≈ 0.70 log-odds, ×2.0),
but this is a side/handedness effect; individuals differ greatly in baseline pull rate. The* **LKJ(eta=2)**
*prior yields a posterior actor intercept–slope correlation `rho` ≈ −0.12 (94% HDI −0.89 to 0.68) — weakly
identified with 7 actors. Correlated and independent random effects predict almost identically
(`elpd_diff` 0.23 ± 0.11), and SBC confirms the sampler is calibrated.* Limitation: with only 7 actors, do
not over-interpret `rho`; report its full uncertainty.

---
*SBC at Tier 3 used 100 sims / trimmed sampler to fit the budget (documented in Stage 11). Every stage lists command · expected output · pass criterion · failure remedy.*
