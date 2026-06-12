# Workflow Manual — Project 04: Divorce ~ Marriage + Age (multiple linear regression)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 1 (Foundations) · **Model family:** Normal multiple linear regression

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020), not a one-way pipeline. P04 is the first **multiple** regression; its
> central craft skills are **standardization** (so priors are interpretable and portable) and reading a
> **DAG** to see **confounding** — why an apparent marriage-rate effect dissolves once age at marriage
> is controlled.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `D = 0 + 0.10·M − 0.60·A + Normal(0, 0.7)` on standardized M, A; fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a = −0.024, bM = 0.129, bA = −0.617, σ = 0.703 — **all four truths inside their 90% HDI**; R̂ = 1.00, ESS-bulk > 4000.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before touching real data.

## Stage 1 — Problem & question
Controlling for median age at marriage, is the **marriage rate** itself associated with the **divorce
rate** across the 50 US states? Target: the standardized coefficient `bM`. Unit: one US state.

## Stage 2 — Data & exploration
WaffleDivorce (`;`-delimited), 50 states. **Standardize** D, M, A to mean 0 / sd 1. Pairwise
correlations: corr(M, D) = **+0.37**, corr(A, D) = **−0.60**, and crucially corr(M, A) = **−0.72** —
marriage rate and age at marriage are strongly (negatively) related, which is the seed of the confound.

## Stage 3 — Model specification
$$D_i \sim \mathrm{Normal}(\mu_i,\sigma),\quad \mu_i = a + b_M M_i + b_A A_i,\quad a\sim\mathrm{Normal}(0,0.2),\ b_M,b_A\sim\mathrm{Normal}(0,0.5),\ \sigma\sim\mathrm{Exponential}(1).$$
Standardization makes `a ~ Normal(0,0.2)` (line near origin) and the slope priors comparable across
predictors (effects up to ≈ ±1 sd-per-sd).

## Stage 4 — Prior predictive on the OUTCOME scale
- **Command:** `pm.sample_prior_predictive`; summarize implied standardized divorce.
- **Observed:** prior-predictive D has mean +0.00, sd 1.72, 1–99% band [−5.07, +5.19] — wide but on the
  right order of magnitude (standardized units), no explosion.
- **Pass criterion:** implied outcome stays in a sane standardized band. **Remedy:** tighten slope priors if it explodes.

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=4)`. ~5 s including the two
nested-model fits and posterior predictive; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, bM, bA, σ; ESS-bulk ≈ 2900–3600; **0 divergences**; BFMI ≈ 0.94–1.11. All pass.

## Stage 7 — Interpretation: the confounding revealed
**`bM` collapses once A enters.** In `D~M` alone, `bM = +0.34` (94% HDI +0.10, +0.59) — apparently
predictive. In the full `D~M+A`, **`bM = −0.06` (94% HDI −0.36, +0.24)** — centred on zero. Meanwhile
**`bA = −0.61` (94% HDI −0.91, −0.31)** is the real driver: states where people marry later divorce less.
The forest plot shows `bM`'s interval sliding onto 0 the moment A is added.

## Stage 8 — Posterior predictive check
- **Discrepancy stats (continuous):** mean p = 0.48, sd p = 0.50, max p = 0.58, **min p = 0.22** — all in
  the comfortable interior; no gross misfit of the standardized divorce distribution.

## Stage 9 — Comparison: `D~A` vs `D~M` vs `D~M+A` (PSIS-LOO)
- **Observed:** **`D~A` ranks first** (elpd_loo = −64.0). The full `D~M+A` is statistically tied with it
  (`elpd_diff` = **0.32 ± 0.53 SE** — well under 1 SE, so M adds nothing). `D~M` alone is clearly worse
  (`elpd_diff` = 6.15 ± 4.98). Stacking weight: 0.88 on `D~A`, 0 on the full model.
- **Caveat:** with only n = 50 states, **max Pareto-k̂ = 0.91 > threshold 0.70** — a few high-leverage
  states (e.g. Idaho, Maine) make the LOO estimate somewhat optimistic; `reloo` or moment-matching would
  refine the exact elpd, but the *ranking* (A suffices, M is redundant) is robust.

## Stage 10 — Power-scaling prior sensitivity (`bM`, `bA`)
- **Observed:** across α ∈ {0.8, 1.0, 1.25}, E[bM] = −0.071 / −0.062 / −0.050 and E[bA] = −0.625 /
  −0.611 / −0.595 — both essentially fixed. Conclusions are **data-driven**, not prior-driven.

## Stage 11 — Model expansion / iteration
Natural next steps: add the **South** indicator or model **measurement error** in the rates using the
`Divorce SE` / `Marriage SE` columns (the error-in-variables model is built in full in **P17**).

## Stage 12 — Decision & communication
**Headline:** *across US states, the apparent marriage-rate → divorce association is almost entirely
**confounded by age at marriage**: once A is controlled, bM ≈ 0, while bA remains a clear negative driver.*
Limitation: observational state-level data; the DAG (M ← A → D, M → D) is an assumption, not proof of causation.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
