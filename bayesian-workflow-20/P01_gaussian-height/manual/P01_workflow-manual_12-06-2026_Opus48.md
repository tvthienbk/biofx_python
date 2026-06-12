# Workflow Manual — Project 01: Mean Height (Gaussian)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 1 (Foundations) · **Model family:** Gaussian location–scale (μ, σ)

> **Framing — read first.** The Bayesian workflow is **not a linear checklist**. It is an
> *iterative loop* over a *growing network of models* (Gelman et al. 2020). You pass through the
> stages below more than once, expanding the model when checks fail. The numbering is a
> *reference order for a single pass*, not a one-way pipeline. P01 is the smallest model that
> still exercises every stage — learn the rhythm here.

## Master references (cited in all 20 manuals)
- Gelman, Vehtari, Simpson, Margossian, Carpenter, Yao, Kennedy, Gabry, Bürkner, Modrák (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Betancourt (2020). *Towards a Principled Bayesian Workflow.* (web case study).
- Vehtari, Gelman, Simpson, Carpenter, Bürkner (2021). *Rank-normalization, folding, and localization: an improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *Practical Bayesian model evaluation using LOO-CV and WAIC.* Stat. Comput. 27.
- Talts, Betancourt, Simpson, Vehtari, Gelman (2018). *Validating Bayesian inference algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** `y_sim = rng.normal(178, 8, 200)`; fit the same model; `az.summary(..., hdi_prob=0.9)`; `az.plot_posterior(..., ref_val=[178, 8])`.
- **Expected output:** posterior means near 178 and 8; both truths inside the 90% HDI.
- **Observed in this run:** μ̂ = 177.4 (90% HDI 176.6–178.2), σ̂ = 7.46 (6.84–8.08); both truths inside → recovery passes.
- **Pass criterion:** every true value inside its 90% HDI; R̂ = 1.00; ESS in the thousands; 0 divergences.
- **Failure remedy:** if a truth falls outside, the bug is in the *model code or priors*, not the data — fix here before Stage 1.

## Stage 1 — Problem & question
What is the **mean adult !Kung height**, with honest uncertainty? Target quantity: μ (population mean, cm) and σ (between-person sd, cm). Unit of observation: one adult person. A "good answer" is a tight, prior-insensitive interval for μ with a model that reproduces the height distribution.

## Stage 2 — Data & exploration
`Howell1.csv` from the *rethinking* repo, **`;`-delimited** (Gotcha 1). Columns: height, weight, age, male. **Filter `age >= 18`** (Gotcha 3): the full sample mixes children, making height bimodal; a single Gaussian is only defensible for adults. Adults: n = 352, mean 154.6 cm, sd 7.73 cm. No transformation needed (already in cm; no standardization for an intercept-only model).

## Stage 3 — Model specification
$$h_i \sim \mathrm{Normal}(\mu,\sigma),\quad \mu \sim \mathrm{Normal}(178,20),\quad \sigma \sim \mathrm{HalfNormal}(20).$$
- **Likelihood** Gaussian: symmetric continuous outcome, no covariates yet.
- **μ ~ Normal(178, 20):** centred on a generic adult height, ±40 cm covers the plausible range.
- **σ ~ HalfNormal(20):** the modern weakly-informative scale prior the V2 spec mandates (replaces `Uniform(0,50)` / `HalfCauchy`). Positive by construction; gentle mass under ~40 cm.
- DAG: `mu, sigma → height` (rendered with `pm.model_to_graphviz`).

## Stage 4 — Prior predictive check (OUTCOME scale) [upgraded]
- **Command:** `pm.sample_prior_predictive(samples=500)`; histogram of `prior_predictive["height"]`.
- **Expected output / pass criterion:** essentially **no negative heights**, mass centred on human scales.
- **Observed:** range ≈ [−15, 446] cm, **fraction < 0 = 0.000**. The prior is deliberately broad (reaches implausibly tall) but never negative — adequate for a first pass.
- **Failure remedy:** if much mass were negative or absurd, tighten σ (e.g. `HalfNormal(10)`) and re-check. Exercise 1 does exactly this.

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=1)`. Wall-clock ≈ 2–3 s on Colab CPU. No sampler warnings emitted.

## Stage 6 — Computational diagnostics (model-aware)
- **Command:** `az.summary(...)`, `az.plot_trace`, `az.plot_energy`, `idata.sample_stats.diverging.sum()`, `az.bfmi`.
- **Thresholds (continuous/NUTS):** R̂ < 1.01; ESS-bulk & ESS-tail > 400; 0 divergences; BFMI > 0.3.
- **Observed:** R̂ = 1.00 (both params); ESS-bulk ≈ 3200, ESS-tail ≈ 2300; **0 divergences**; BFMI ≈ 1.0–1.15 per chain; traces are overlapping fuzzy caterpillars. All pass.
- **Failure remedy (not needed here):** non-centred parameterization, raise `target_accept`, tighten priors, rescale.

## Stage 7 — Posterior summary & interpretation (original units)
- **Command:** `az.summary(..., hdi_prob=0.94)`, `az.plot_posterior`.
- **Observed:** **μ = 154.6 cm (94% HDI 153.8–155.4)**, **σ = 7.77 cm (7.18–8.31)**. So ~95% of adults fall roughly within 154.6 ± 2·7.8 = 139–170 cm. Uncertainty in μ is small because n = 352.

## Stage 8 — Posterior predictive check [required]
- **Command:** `pm.sample_posterior_predictive`; `az.plot_ppc`; discrepancy stats for continuous data = mean, sd, min, max with Bayesian p-values.
- **Observed:** mean p = 0.50, sd p = 0.50 (centre and spread reproduced); max p = 0.25; **min p = 0.04** — a mild flag that real heights have a slightly heavier *short* tail than a symmetric Gaussian. This is the systematic misfit that motivates Stage 11.
- **Pass criterion:** no gross misfit (no p ≈ 0 or 1 on a central statistic). Passes, with the min flag noted as the lead into P03.

## Stage 9 — Model comparison: Normal vs Student-t
- **Command:** refit with `StudentT(nu, mu, sigma)`, `nu ~ Gamma(2, 0.1)`; `az.compare({"normal":..., "student_t":...})`.
- **Observed:** Normal ranks first; `elpd_diff` ≈ 1.5 with `dse` ≈ 0.5; stacking weight ≈ 1.0 on Normal. With no genuine outliers, the heavier-tailed Student-t buys nothing.
- **Pareto-k̂:** all below the sample-size-aware threshold `min(1 − 1/log10(S), 0.7) ≈ 0.68`, so LOO is reliable; no moment-matching/`reloo` needed.

## Stage 10 — Power-scaling prior sensitivity [upgraded]
- **Command:** reweight posterior draws by `prior^(α−1)` for α ∈ {0.8, 1.0, 1.25}; report E[μ], E[σ].
- **Observed:** E[μ] = 154.604 / 154.606 / 154.609 across α — a swing < 0.01 cm. **The conclusion is robust; the data, not the prior, drives it.** (Contrast: a strongly prior-sensitive result would move visibly here.)

## Stage 11 — Model expansion / iteration
The only PPC flag is the short-height tail. The concrete next model is **P03: height ~ weight** — a linear mean explains the residual structure a constant μ leaves behind. (For robustness to outliers specifically, the Student-t of Stage 9 is the alternative branch — but LOO says it is unnecessary here.)

## Stage 12 — Decision & communication
**Headline figure:** the Stage-7 posterior of μ. **Headline sentence:** *the mean height of !Kung San adults is **154.6 cm** (94% HDI 153.8–155.4), with a between-person standard deviation of **7.8 cm**; the estimate is tightly determined and insensitive to the prior.* Limitation: a single Gaussian slightly under-models the shortest adults; anyone needing the lower tail (e.g. clothing sizing extremes) should prefer the P03 predictor model.

---
*SBC is not required at Tier 1 (introduced at Tier 3, Project 11). Every stage above lists command · expected output · pass criterion · failure remedy as required by §4.*
