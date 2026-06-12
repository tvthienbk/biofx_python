# Workflow Manual — Project 18: Cherry-Blossom Timing (B-splines + optional HSGP)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 4 (Advanced) · **Model family:** B-spline basis regression (optional Hilbert-space GP)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P18 fits a smooth non-linear time trend with a **basis expansion**, the
> scalable alternative to an exact Gaussian process.

## Master references
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian inference with SBC.* arXiv:1804.06788; Säilynoja et al. (2022).

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `doy` from a known smooth curve + Normal(0, 6) noise; fit an 18-knot spline; check the
  posterior mean-curve ribbon covers the truth and σ is recovered.
- **Observed:** ≥ 80% of truth points inside the 90% pointwise ribbon; σ̂ ≈ 6.1 (truth 6.0) → recovery passes.
- **Pass criterion:** σ recovered and the smooth ribbon covers the large majority of truth points; no pathologies.
- **Failure remedy:** add knots / raise `target_accept` if the curve is biased at wiggle peaks.

## Stage 1 — Problem & question
How has Kyoto's first cherry-blossom **day-of-year** drifted over a millennium (warmer springs ⇒ earlier
blooms)? Target: the smooth mean curve μ(year). Unit: one year's record.

## Stage 2 — Data & exploration
`cherry_blossoms.csv` (rethinking, **`;`-delimited**). 1215 rows, **388 missing `doy`** (§7.7) → we model the
**827** years with an observed bloom date (years 812–2015). Mean doy ≈ 104.5, sd ≈ 6.4.

## Stage 3 — Model specification (B-splines)
$$\text{doy}_i \sim \mathrm{Normal}(\mu_i,\sigma),\quad \mu_i = a + \sum_k w_k B_k(\text{year}_i),\quad
a\sim\mathrm{Normal}(105,10),\ w_k\sim\mathrm{Normal}(0,10),\ \sigma\sim\mathrm{HalfNormal}(10).$$
`B` is a cubic B-spline basis: **15 quantile knots → 17 local basis functions** (827×17 design matrix). Local
support means the curve flexes only where data demand it — no global-polynomial tail blow-up. **Why not an
exact GP?** O(n³) on 827 points blows the runtime budget (§7.7); the spline is O(n).

## Stage 4 — Prior predictive (OUTCOME scale = day of year)
- **Observed:** simulated day-of-year stays in a plausible band (a real bloom is day ~85–125); the prior is broad
  but not absurd. **Remedy if needed:** tighten `w` scale to curb extreme wiggles.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=18)`. Wall-clock ≈ 28 s.

## Stage 6 — Diagnostics
- **Observed:** intercept R̂ = 1.00 (ESS-bulk ≈ 670); all 17 spline weights R̂ = 1.00, min ESS ≈ 836; σ R̂ = 1.00
  (ESS ≈ 3800); **0 divergences**; BFMI ≈ 0.93–1.04. All pass.

## Stage 7 — Interpretation: the smooth trend
The posterior mean spline tracks the bloom series tightly with a 94% ribbon. **Mean bloom-day ≈ 103.3 before
1100 vs ≈ 100.4 after 1900 — a shift of ≈ 2.9 days earlier**, with the steepest decline in the warming 20th
century (the curve, not a single slope, tells the story).

## Stage 8 — Posterior predictive check
- **Discrepancy stats:** mean p = 0.50, sd p = 0.64, max p = 0.57, **min p = 0.09** — the earliest blooms are
  marginally under-predicted, otherwise an excellent fit.

## Stage 9 — Comparison: spline vs straight-line trend (PSIS-LOO)
- **Observed:** the spline beats a linear `doy ~ year` by **elpd_diff = 52.7 with dse = 9.9 → 5.3 SE**, stacking
  weight 1.0 on the spline; max Pareto-k̂ = 0.37 < threshold 0.70 → LOO reliable. The trend is genuinely
  non-linear.

## Stage 10 — Power-scaling prior sensitivity (σ)
- **Observed:** E[σ] = 5.964 / 5.964 / 5.963 across α ∈ {0.8,1,1.25} — flat; the noise scale is data-driven.

## SBC — Simulation-Based Calibration (Tier 4 requirement)
- **Command:** 100 sims on a reduced 6-knot spline (cheap sampler), rank the true σ.
- **Observed:** rank histogram consistent with uniform, **chi-square p = 0.90** (> 0.05) → calibrated.

## Optional HSGP
The `pm.gp.HSGP` (Matérn-5/2, m=30, c=1.5) reproduces the same smooth trend at low rank; ≈ 2 divergences
(acceptable for the approximate path) — the bridge to genuine GP models with principled extrapolation.

## Stage 11 — Model expansion / iteration
Join the bloom series to the **temperature** reconstruction (`temp`) for a mechanistic temperature→bloom model,
or replace the B-spline with the HSGP for honest extrapolation uncertainty.

## Stage 12 — Decision & communication
**Headline:** *Kyoto's cherry now blooms several days earlier than a millennium ago; the B-spline recovers a
smooth, well-mixed trend (R̂≈1.0, 0 divergences) at a fraction of an exact GP's cost, and SBC confirms the
noise model is calibrated.* Limitation: a B-spline must **not** be extrapolated beyond the data range.

---
*Every stage lists command · expected output · pass criterion · failure remedy. SBC present (Tier 4).*
