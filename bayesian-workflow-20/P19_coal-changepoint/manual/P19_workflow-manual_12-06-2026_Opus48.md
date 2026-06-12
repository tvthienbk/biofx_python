# Workflow Manual — Project 19: Coal-Mining Disasters (Poisson changepoint)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 4 (Advanced) · **Model family:** Poisson changepoint with a **discrete switchpoint** (+ marginalized NUTS twin)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of models*
> (Gelman et al. 2020). P19 is the project where **diagnostics become model-aware**: a discrete latent
> variable forces compound sampling, so the "0 divergences" NUTS rule does **not** apply (§6, §9, §7.8).

## Master references
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2). · Vehtari, Gelman, Gabry (2017). *LOO-CV/WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *SBC.* arXiv:1804.06788; Säilynoja et al. (2022).

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate a series with a known switch at 1900, early rate 3.2, late rate 0.9; fit the discrete model.
- **Observed:** switchpoint posterior median **1902** (truth 1900); early **3.12**, late **0.86** → recovery passes.
- **Pass criterion:** switchpoint within a few years of truth; rates recovered. **Remedy:** widen rate priors / more draws.

## Stage 1–2 — Question & data
When did the annual rate of British coal-mining disasters drop, and by how much? Data: **hardcoded** Jarrett (1979)
series, 1851–1961 (n = 111, 191 total disasters). Tiny and canonical, so hardcoded (§7.4) with a cache copy written.

## Stage 3 — Model A: discrete switchpoint (compound sampling)
$$s\sim\mathrm{DiscreteUniform}(0,n{-}1),\ e,\ell\sim\mathrm{Exponential}(1),\ \text{rate}_i = e\ \text{if}\ i<s\ \text{else}\ \ell,\ y_i\sim\mathrm{Poisson}(\text{rate}_i).$$
Because `s` is **discrete**, PyMC cannot use NUTS for it; it assigns a **CompoundStep** (Metropolis on `s`, NUTS on `e`, `ℓ`).

## Stage 4 — Prior predictive (outcome = counts)
- **Observed:** simulated annual counts sit in a plausible 0–~10 band with a sensible zero fraction; no absurdities.

## Stage 5 — Fit (compound step)
`pm.sample(3000, tune=2000, chains=4)`. **The sampler PyMC selects is a CompoundStep** (printed/confirmed in stderr).

## Stage 6 — Diagnostics (MODEL-AWARE)
- **The divergence-count criterion is WAIVED** for the compound/discrete-latent model (documented in the cell).
- **What we check instead:** per-block R̂/ESS and that the **switchpoint mixes**. Observed: e R̂ = 1.00 (ESS ≈ 7600),
  ℓ R̂ = 1.00 (ESS ≈ 9200), **s R̂ = 1.00 (ESS ≈ 1740)** — the discrete variable is exploring, not stuck.
- **Switchpoint posterior:** median year **1891**, 94% HDI **[1887, 1897]**.

## Stage 7 — Interpretation
**Before ~1891: ≈ 3.06 disasters/year. After: ≈ 0.94/year — a 69% drop** (plausibly tied to the 1880s–90s mining
safety legislation and unionization).

## Stage 8 — Posterior predictive check (count discrepancy stats)
- proportion of zero-years: obs 0.29, **bayes-p = 0.38**; max annual count: obs 6, bayes-p = 0.97; total: obs 191,
  bayes-p = 0.46. The two-rate model reproduces the count distribution well.

## Stage 9 — Comparison: changepoint vs constant-rate Poisson (LOO)
- **Observed:** the changepoint beats a single constant rate by **elpd_diff = 32.0 with dse = 8.0 → 4.0 SE**, stacking
  weight 0.97. The rate change is strongly supported.

## Model B: marginalized switchpoint (restores full NUTS)
Summing the likelihood over all switch positions analytically (a `pm.Potential` with a `logsumexp` over cumulative
Poisson log-likelihoods) removes the discrete variable. **Result: 0 divergences with pure NUTS**, and the rate
estimates (e ≈ 3.06, ℓ ≈ 0.94) match Model A. *Now* the 0-divergence criterion legitimately applies.

## SBC — Simulation-Based Calibration (Tier 4), marginalized model
- **Observed:** 100 sims, rank histogram for the early rate consistent with uniform, **chi-square p = 0.74** → calibrated.

## Stage 10 — Power-scaling prior sensitivity (rates)
- **Observed:** E[early] = 3.079 / 3.063 / 3.042 and E[late] ≈ 0.936 across α ∈ {0.8,1,1.25} — flat; data-driven.

## Stage 11 — Model expansion / iteration
Allow a **gradual** logistic transition instead of a hard step, or **multiple** changepoints / a hidden-Markov rate
(state-space). The marginalization machinery generalizes directly.

## Stage 12 — Decision & communication
**Headline:** *British coal-mining disasters fell abruptly around 1891, from ~3 per year to ~1 per year; the
discrete-switchpoint model — judged by R̂/ESS and switchpoint mixing rather than divergence count — and its
full-NUTS marginalized twin agree, and SBC confirms calibration.* Limitation: a single hard switch is a simplification
of a likely gradual safety improvement.

---
*Model-aware acceptance (§9): for the compound-step model the divergence criterion is waived and documented; the
marginalized model restores and passes the 0-divergence NUTS criterion. SBC present (Tier 4).*
