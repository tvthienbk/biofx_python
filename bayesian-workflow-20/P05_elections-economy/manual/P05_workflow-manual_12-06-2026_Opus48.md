# Workflow Manual — Project 05: Vote share ~ economic growth (tiny linear regression)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 1 (Foundations) · **Model family:** Normal linear regression (tiny n)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P05 is Hibbs's **"Bread and Peace"** model fit to just **16 elections**;
> its craft skills are reading the **slope in plain units** and building honest **predictive intervals**
> when n is tiny — where parameter uncertainty and residual noise both matter.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `v = 52 + 3.0·g + Normal(0, 3.5)` at realistic growth values; fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a = 52.17, b = 2.87, σ = 3.55 — **all three truths inside their 90% HDI**; R̂ = 1.00,
  ESS-bulk ≈ 2500. (We simulate with extra rows so the intercept is identifiable; the *real* fit below uses all 16.)
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
How many percentage points of the incumbent party's two-party vote share does each extra 1% of economic
growth buy? Target: the slope `b`. Unit: one US presidential election (n = 16, 1952–2012).

## Stage 2 — Data & exploration
hibbs.dat (**whitespace-delimited** → `sep=r"\s+"`), 16 rows. growth range [−0.4, 4.2] %, vote range
[44.6, 61.8] %, **corr(growth, vote) = +0.76** — a strong positive line by eye.

## Stage 3 — Model specification
$$v_i \sim \mathrm{Normal}(\mu_i,\sigma),\quad \mu_i = a + b\,g_i,\quad a\sim\mathrm{Normal}(50,20),\ b\sim\mathrm{Normal}(0,10),\ \sigma\sim\mathrm{HalfNormal}(10).$$
`a ~ Normal(50,20)` centres on a tied election; `b ~ Normal(0,10)` is weakly-informative; `σ ~ HalfNormal(10)`
allows a few points of election-to-election noise.

## Stage 4 — Prior predictive on the VOTE scale
- **Command:** `pm.sample_prior_predictive`; histogram of implied vote%.
- **Observed:** prior-predictive vote mean 51.3%, sd 32.1, 5–95% [−2.2, 104.6] — wide and centred near a
  tie. (The very wide tails reflect deliberately weak priors; the data will tighten them sharply.)
- **Pass criterion:** mass concentrated around plausible electoral values, centred near 50%. **Remedy:** tighten `b`/`σ` if absurd.

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=5)`. ~7 s with the null-model
fit and posterior predictive; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, b, σ; ESS-bulk ≈ 1600; **0 divergences**; BFMI ≈ 0.92–1.03. All pass.

## Stage 7 — Interpretation (vote points per +1% growth)
**Each +1% of economic growth → +3.05 vote points (94% HDI 1.50, 4.45).** At zero growth the incumbent
gets **a = 46.3%** (94% HDI 42.9, 49.7) — i.e. a flat economy slightly favours the challenger.
**P(b > 0) = 0.999** — the economy almost certainly helps the incumbent.

## Stage 8 — Posterior predictive check
- **Discrepancy stats (continuous):** mean p = 0.50, sd p = 0.56, max p = 0.54, **min p = 0.19** — all
  comfortably interior; the straight-line Normal model reproduces the spread of the 16 elections well.

## Stage 9 — Comparison: `vote~growth` vs intercept-only (PSIS-LOO)
- **Observed:** `growth` ranks first (elpd_loo = −46.3); `intercept_only` trails by `elpd_diff` = **5.34
  ± 3.63 SE** (≈ 1.5 SE — favourable but not overwhelming, as expected with n = 16). Stacking weight 0.89
  on the growth model. **Max Pareto-k̂ = 0.62 < threshold 0.70** — LOO is (just) reliable here, but with
  16 points it is inherently fragile; do not over-read the exact elpd.

## Stage 10 — Power-scaling prior sensitivity (slope b)
- **Observed:** E[b] = 3.053 / 3.047 / 3.041 across α ∈ {0.8, 1.0, 1.25} — essentially fixed. The slope
  is data-driven, not prior-driven.

## Stage 11 — Model expansion / iteration
Hibbs's full model adds a **cumulative military-fatalities** ("peace") term; a **StudentT** likelihood
would guard against an outlier election. Natural next steps given the tiny sample.

## Stage 12 — Decision & communication
**Predictions:** at **growth = 2%**, mean vote 52.4% (mean 90% [50.7, 54.1]; full **predictive** 90%
[45.5, 59.4]), **P(win) = 0.74**. At **growth = 4%**, mean vote 58.5% (predictive 90% [51.0, 66.0]),
**P(win) = 0.96**.
**Headline:** *the economy clearly helps the incumbent — each +1% of growth ≈ **+3 points** of vote share
— but with only 16 elections the predictive interval for any single future race spans ≈ ±7 points, so
growth tilts the odds without guaranteeing the outcome.* Note the **predictive** interval is far wider
than the **mean** interval — that gap is the residual election-to-election noise σ ≈ 4.1.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
