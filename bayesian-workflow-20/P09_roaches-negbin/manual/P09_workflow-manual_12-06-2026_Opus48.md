# Workflow Manual — Project 09: Roaches (Poisson + offset → NegativeBinomial)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 2 (Generalised linear models) · **Model family:** Poisson / NegativeBinomial GLM with offset

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P09 is the canonical **diagnose-then-cure**: a PPC reveals that a
> Poisson cannot reproduce the observed zeros, and the cure is to **expand to a NegativeBinomial**
> (Gelman & Hill 2007, Ch. 15).

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate an **overdispersed** count from a NegativeBinomial with a known offset and (a=2.0, b1=0.8, b2=-0.5); fit the NegBin; `az.summary(hdi_prob=0.9)`.
- **Observed:** a (2.02), b1 (0.730), b2 (-0.618) — all three truths inside their 90% HDIs; R̂ = 1.00. The offset machinery and dispersion are exercised before real data.
- **Pass criterion:** truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
Did the pest-management treatment reduce roach counts, after adjusting for pre-treatment infestation, senior-only buildings, and **exposure** (trap-days)? Target: the treatment rate ratio. Unit: one apartment (n = 262).

## Stage 2 — Data & exploration
roaches.csv (comma, **unnamed index col** → `index_col=0`), n = 262. **Observed proportion of zero-roach apartments = 0.359**; max count **357**; mean **25.6** but variance **2576** — variance ≫ mean, the signature of **overdispersion**. `log(exposure2)` is used as an offset.

## Stage 3 — Model specification (Poisson, then NegativeBinomial)
$$y_i \sim \mathrm{Poisson}(\mu_i),\quad \log\mu_i = \log(\text{exposure}_i) + a + b_1 \text{roach}_z + b_2 \text{treatment} + b_3 \text{senior}.$$
Model B replaces Poisson with **NegativeBinomial(μ, α)**, `α ~ Exponential(1)`. The `log(exposure)` is an **offset** (coefficient fixed at 1), not a free parameter. Priors: a ~ Normal(0,5), b ~ Normal(0,1).

## Stage 4 — Prior predictive on the COUNT scale
- **Observed:** a ~ Normal(0,5) is wide on the log scale, but the **offset anchors the rate**; the posterior tightens it sharply once the data arrive.
- **Pass criterion:** prior counts are not degenerate. **Remedy:** narrow `a` if the prior count explodes.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=9)` for both, with `idata_kwargs={"log_likelihood": True}` for LOO.

## Stage 6 — Diagnostics
- **Poisson:** R̂ = 1.00, ESS-bulk ≥ 2500, **0 divergences** — note the SDs are *implausibly tiny* (b2 sd = 0.025), a hallmark of an overdispersed model that is over-confident.
- **NegBin:** R̂ = 1.00, ESS-bulk ≥ 2766, **0 divergences**; dispersion **α = 0.27** (small α ⇒ strong overdispersion). All pass.

## Stage 7 — Interpretation (rate ratios)
- **Poisson:** b_treatment = **-0.517** (94% HDI -0.564..-0.469) → rate ratio **0.60** (40% fewer roaches) — but the interval is **falsely narrow**.
- **NegBin:** b_treatment = **-0.738** (94% HDI -1.191..-0.305) → rate ratio **0.48** (**52% fewer roaches**), with an honestly wider interval. The treatment works.
- **α = 0.27**: the Poisson is the α→∞ limit; this small α quantifies how far the data depart from Poisson.

## Stage 8 — Posterior predictive check: PROPORTION OF ZEROS & MAX [the payoff]
- **Poisson:** predicted proportion-zeros 5–95% = **[0.000, 0.004]** vs observed **0.359** → **bayes-p = 0.000**: the Poisson essentially **never** produces a zero-roach apartment, a catastrophic misfit.
- **NegBin:** predicted proportion-zeros 5–95% = **[0.271, 0.405]**, covering the observed 0.359 → **bayes-p = 0.296**: the misfit is cured. (Both models cover the maximum count of 357.)

## Stage 9 — Comparison: Poisson vs NegativeBinomial (PSIS-LOO)
- **Observed:** `elpd_diff = 5342.7 ± 705.7` (≈ **7.6 SE**) in favour of NegBin; stacking weight **0.98**. NegBin is decisively better. Max Pareto-k̂ = **0.74**, just above the 0.70 threshold (a handful of high-leverage apartments) — LOO is mildly approximate, but the gap is so enormous the conclusion is unambiguous.

## Stage 10 — Power-scaling prior sensitivity (b_treatment)
- **Observed:** E[b_treatment] = **-0.747 / -0.738 / -0.728** across α ∈ {0.8, 1, 1.25} — essentially fixed. The treatment effect is data-driven.

## Stage 11 — Model expansion / iteration
Even the NegBin may leave a residual spike at exactly zero (structurally roach-free apartments) — the next step is a **zero-inflated NegativeBinomial (ZINB)** or a **hurdle** model, mixing a structural-zero process with the count process.

## Stage 12 — Decision & communication
**Headline:** *the treatment reduces roach counts (rate ratio ≈ 0.48, ~52% fewer), but a plain Poisson
is unusable — it predicts essentially **zero** zero-roach apartments when **36%** were observed.
Switching to a NegativeBinomial fixes the overdispersion and is favoured by LOO by ~7.6 SE.* Limitation:
a ZINB may still be needed if structural zeros remain.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
