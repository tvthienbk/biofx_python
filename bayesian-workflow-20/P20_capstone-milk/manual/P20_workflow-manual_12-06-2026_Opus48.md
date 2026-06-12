# Workflow Manual — Project 20 (CAPSTONE): Primate Milk Energy

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 4 (Capstone) · **Model family:** multivariate Normal regression + Bayesian missing-data imputation

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of models*
> (Gelman et al. 2020). The capstone exercises **every** stage at once: Stage 0 recovery, outcome-scale prior
> predictive, model-aware diagnostics, PPC, **LOO model selection**, power-scaling sensitivity, and **SBC**.

## Master references
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2). · Vehtari, Gelman, Gabry (2017). *LOO-CV/WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *SBC.* arXiv:1804.06788; Säilynoja et al. (2022).

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate complete `K = a + bN·N + bM·M + Normal(0,0.4)` with known coefficients; fit complete-case.
- **Observed:** all four recovered (bN 0.713, bM −0.675, a −0.041, σ 0.478 — truths inside 90% HDI).
- **Pass criterion:** all truths inside 90% HDI before imputation is added on real data.

## Stage 1–2 — Question & data
Does milk energy density (`kcal.per.g`) rise with relative brain size (`neocortex.perc`) once body mass is
accounted for? n = 29 primate species; **12 of 29 neocortex values are missing** — the modelling challenge.
Standardize K, log(mass)→M, neocortex→N. **Each predictor alone looks weak** (the Stage-2 scatterplots).

## Stage 3 — Full model with missing-data imputation
$$K_i\sim\mathrm{Normal}(a+b_N N_i+b_M M_i,\sigma),\quad N_i\sim\mathrm{Normal}(\nu,\sigma_N),$$
priors `a,bN,bM~Normal(0,0.5)`, `σ,σ_N~Exponential(1)`, `ν~Normal(0,1)`. Missing N entries become **latent
parameters with a prior** (Bayesian imputation): PyMC auto-imputes when `observed` is a masked array, splitting
N into observed and unobserved nodes. All 29 species inform the fit — no rows dropped, no mean-filling.

## Stage 4 — Prior predictive (outcome = standardized kcal)
- **Observed:** simulated K spans roughly the data's [−2, 2] standardized range; no absurd mass.

## Stage 5 — Fit
`pm.sample(1500, tune=1500, chains=4, target_accept=0.95, random_seed=20)`. ~12 s.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for all (a, bN, bM, σ, ν, σ_N); ESS-bulk ≈ 2000–7000; **0 divergences**; BFMI ≈ 0.66–0.80
  (> 0.3). All pass.

## Stage 7 — Interpretation: the masked (suppression) effect
- **bN (neocortex) = +0.48 (94% HDI +0.01, +0.89)** → bigger relative neocortex, **more** energetic milk.
- **bM (log mass) = −0.54 (94% HDI −0.93, −0.16)** → bigger body, **less** energetic milk.
Each is hard to see alone because mass and neocortex are positively correlated and push K in opposite directions —
a textbook **masking / statistical-suppression** effect. Only the joint model reveals either.

## Stage 8 — Posterior predictive check
- mean p = 0.47, sd p = 0.73, max p = 0.63, **min p = 0.01** — one unusually low-energy species sits in the tail
  (a documented, localized misfit, not a systematic one).

## Stage 9 — Model selection with PSIS-LOO (mass-only vs neocortex-only vs both)
- **Observed:** **both** ranks first (stacking weight 1.0); it beats mass-only by elpd_diff 2.47 ± 1.12 and
  neocortex-only by 3.82 ± 1.98. Max Pareto-k̂ = **0.79 > 0.70** (n = 29 is small) — flagged honestly; moment-matching
  / `reloo` would refine the estimate, but the ranking is clear.

## Stage 10 — Power-scaling prior sensitivity (bN, bM)
- **Observed:** E[bN] = 0.516 / 0.480 / 0.442 and E[bM] = −0.568 / −0.537 / −0.503 across α ∈ {0.8,1,1.25} — the
  signs and rough magnitudes are stable; some movement is expected with only 29 species (reported, not hidden).

## SBC — Simulation-Based Calibration (capstone requirement)
- **Observed:** 100 sims, rank histogram for bN consistent with uniform, **chi-square p = 0.98** → calibrated.

## Stage 11 — Model expansion / iteration
Model the imputation with mass (`N_i ~ Normal(αN + βN·M_i, σN)`) so imputed neocortex borrows strength from body
size; or add `clade` as a varying intercept (ties back to Tier 3).

## Stage 12 — Decision & communication
**Headline:** *across primates, milk grows more energy-dense as relative neocortex size rises and less dense as
body mass rises — but only a model with **both** predictors reveals either, because the two effects mask each
other. Bayesian imputation let all 29 species inform the fit despite 12 missing neocortex values; LOO favours the
two-predictor model and SBC confirms calibration.* Limitation: n = 29 and one Pareto-k̂ > 0.7 — treat effect sizes
as indicative, not precise.

---
*This capstone exercised every workflow stage: Stage-0 recovery, outcome-scale prior predictive, diagnostics, PPC,
LOO selection, power-scaling sensitivity, and SBC.*
