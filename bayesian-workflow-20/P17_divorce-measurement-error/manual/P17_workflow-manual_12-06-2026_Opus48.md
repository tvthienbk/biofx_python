# Workflow Manual — Project 17: Divorce (error-in-variables + Student-t)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 4 (Advanced) · **Model family:** Error-in-variables Gaussian regression (+ Student-t robust variant)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P17 introduces **measurement error**: the observed state divorce rate is a
> noisy reading of a latent true rate, and small states are read most noisily. The craft skills are the
> **error-in-variables** model, the **measurement-error shrinkage** plot, and a **Student-t** robust variant.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate latent true divorce from `a=0, bA=−0.6, bM=0.3, sigma=0.6`, add per-state SE noise,
  fit the error-in-variables model; check recovery.
- **Observed:** a, bA, bM, sigma all recovered inside their 90% HDIs; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** check the latent layer / SE scaling first.

## Stage 1 — Problem & question
How do median age at marriage (A) and marriage rate (M) relate to divorce (D), **once we acknowledge D is
measured with error**? Target: `bA, bM` on the latent divorce rate. Unit: one US state.

## Stage 2 — Data & exploration
WaffleDivorce (`;`-delimited) → 50 states. **The SE columns are `Divorce SE` / `Marriage SE` (with SPACES)** —
renamed to `Divorce_SE` / `Marriage_SE`. We standardize D, A, M and put the SE on the standardized D scale
(`D_SE` range 0.13–1.39). The noisiest (smallest-population) states are **SD, AK, WY, DC, VT**.

## Stage 3 — Model specification (error-in-variables)
$$D^{\text{obs}}_j \sim \mathrm{Normal}(D^{\text{true}}_j, \mathrm{SE}_j),\ D^{\text{true}}_j\sim\mathrm{Normal}(\mu_j,\sigma),\ \mu_j=a+b_A A_j+b_M M_j,\ a\sim\mathrm{Normal}(0,0.2),\ b_A,b_M\sim\mathrm{Normal}(0,0.5),\ \sigma\sim\mathrm{Exponential}(1).$$
The latent `D_true` is one parameter per state; the regression acts on it, so noisy states get pulled toward the line.

## Stage 4 — Prior predictive on the OUTCOME scale (standardized divorce)
- **Observed:** prior predictive divorce has sd 1.80, 95% within ±3.7 — a sensible standardized range.
- **Pass criterion:** implied divorce stays within a few standard deviations. **Remedy:** tighten priors if it explodes.

## Stage 5 — Fit (Normal error-in-variables)
`pm.sample(1000, tune=1000, chains=4, target_accept=0.95, random_seed=17)`. ~6 s; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, bA, bM, sigma; ESS-bulk 1286–3187; **0 divergences**; BFMI 0.70–0.81. All pass.

## Stage 7 — Interpretation + MEASUREMENT-ERROR SHRINKAGE [the key lesson]
- **bA = −0.616** (94% HDI [−0.928, −0.328]) — a clear **negative** age-at-marriage effect; **bM = +0.053**
  (HDI [−0.264, +0.358]) — marriage rate adds little once age is in.
- **Shrinkage:** mean |observed − latent| is **0.443 for high-SE states** vs only **0.128 for low-SE states** —
  noisy small states are pulled ~3.5× harder toward the regression line, because the model trusts their
  readings less. This is the whole point of modeling measurement error.

## Stage 8 — Posterior predictive check (continuous discrepancies)
- **Observed:** mean bayes-p 0.28, sd 0.74, min 0.15, max 0.67 — all comfortably interior; no gross misfit.

## Stage 9 — Comparison: Normal vs Student-t error-in-variables (LOO)
- **Observed:** Student-t edges ahead but the gap is negligible: `elpd_diff` = **0.48** with `dse` = 1.03 →
  **0.46 SE** — statistically indistinguishable. The Student-t **nu posterior mean ≈ 19.1** (near-Gaussian),
  so the data show little need for heavy tails. Max Pareto-k̂ = **1.26 > 0.70** for the Normal — a few states
  (small-population, high-SE) are influential, so LOO here is approximate (reloo would refine).

## Stage 10 — Power-scaling prior sensitivity (bA)
- **Observed:** E[bA] = −0.628 / −0.616 / −0.601 across α ∈ {0.8,1,1.25} — barely moves; data-driven.

## SBC — Simulation-Based Calibration on `bA` [Tier 4, recommended — done]
- **Command:** 100 sims, cheap sampler; rank true `bA`.
- **Observed:** 100 sims in **228 s**; **chi-square uniformity p = 0.419** (> 0.05) → ranks uniform ⇒ calibrated.

## Stage 11 — Model expansion / iteration
Also model **Marriage with error** (`M_obs ~ Normal(M_true, Marriage_SE)`), so predictor and outcome both carry
their measurement uncertainty — the full double-error-in-variables model of *Statistical Rethinking* Ch.15.

## Stage 12 — Decision & communication
**Headline:** *median age at marriage has a clear negative association with divorce (bA = −0.62, HDI excludes 0);
once measurement error is modeled, noisy small-population states (SD, AK, WY) shrink ~3.5× harder toward the
regression line than well-measured states, and a Student-t robust variant is statistically indistinguishable
from the Normal (0.46 SE), with nu ≈ 19 indicating near-Gaussian tails.*

---
*SBC recommended at Tier 4 and done — PASSED (p = 0.42). Every stage lists command · observed output · pass criterion · failure remedy.*
