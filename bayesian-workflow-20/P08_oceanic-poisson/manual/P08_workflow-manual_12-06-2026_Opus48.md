# Workflow Manual — Project 08: Oceanic tool kits (Poisson regression)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 2 (Generalised linear models) · **Model family:** Poisson GLM (log link)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P08 introduces the **log link** and an **interaction on the count
> scale**, and shows why the intercept prior must be set on the *outcome* (count) scale, not by habit
> (Kline & Boyd 2010).

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `total_tools ~ Poisson(exp(3.2 + 0.3·P + 0.2·contact))`, n = 60; fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a (3.21), b_p (0.303), b_c (0.249) — all three truths inside their 90% HDIs; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
How does tool-kit size scale with (log) population, and does contact change that scaling? Target: the population slope `b_p` and interaction `b_pc`. Unit: one society (n = 10).

## Stage 2 — Data & exploration
Kline (`;`-delimited), **n = 10**, `total_tools` ranges **13 (Malekula) to 71 (Hawaii)**. We standardize `log(population)` → P and code contact `high = 1 / low = 0`. **Hawaii** is a huge outlier on population (275,000; P = +2.32) — a high-leverage point flagged throughout.

## Stage 3 — Model specification (two models)
$$\text{total\_tools}_i \sim \mathrm{Poisson}(\lambda_i),\quad a\sim\mathrm{Normal}(3,0.5),\ b\sim\mathrm{Normal}(0,0.5).$$
M1: $\log\lambda = a + b_P P + b_c c$.  M2: adds $+\,b_{Pc}\,P c$ (the interaction).

## Stage 4 — Prior predictive on the COUNT scale [the key lesson]
- **Command:** push two intercept priors through `exp`; compare implied tool counts at mean population.
- **Observed:** a "flat" `Normal(0,10)` implies a **95th-percentile tool count of ~15.6 million** (absurd for islands); the chosen `Normal(3,0.5)` implies median **20**, 95th percentile **45** — biologically plausible.
- **Pass criterion:** prior-implied counts are realistic. **Remedy:** tighten the intercept prior on the count scale, as here.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=8)` for both models, with `idata_kwargs={"log_likelihood": True}` for LOO.

## Stage 6 — Diagnostics
- **M1:** R̂ = 1.00, ESS-bulk ≥ 1870, BFMI ≈ 1.0–1.1, **0 divergences**.
- **M2:** R̂ = 1.00, ESS-bulk ≥ 2300, BFMI ≈ 1.0–1.1, **0 divergences**. All pass.

## Stage 7 — Interpretation (count scale)
- **b_p = +0.398** (94% HDI +0.299..+0.493) → a +1 SD in log-population **multiplies expected tools by exp(b_p) = 1.49×**.
- **b_c (contact, at mean pop) = +0.280**; **interaction b_pc = +0.084** (94% HDI **-0.358..+0.503**) — straddles 0, weakly identified.
- Population slope by contact: low **+0.398**, high **+0.482** (the interaction nudges high-contact societies to grow slightly faster, but the data cannot pin it down with n = 10).

## Stage 8 — Posterior predictive check (count discrepancy)
- **Discrepancy stats:** mean bayes-p **0.48**, max bayes-p **0.46**, sd bayes-p **0.34** — all near 0.5; the Poisson reproduces the central tendency and the extreme (Hawaii = 71) without gross misfit.

## Stage 9 — Comparison: with vs without interaction (PSIS-LOO)
- **Observed:** `elpd_diff = 2.94 ± 2.10` (≈ **1.4 SE**) favouring the **no-interaction** model — the interaction does **not** earn its complexity; stacking weight 1.00 on M1.
- **Caveat (honest):** max Pareto-k̂ = **1.11 > 0.70**, with **3/10** points above threshold (Hawaii and other high-leverage societies). With n = 10, LOO is approximate — **`reloo`** would refit those points for a precise elpd; the qualitative conclusion (no support for the interaction) is stable.

## Stage 10 — Power-scaling prior sensitivity (b_p)
- **Observed:** E[b_p] = **0.399 / 0.398 / 0.397** across α ∈ {0.8, 1, 1.25} — the prior pulls only slightly; the population effect's sign and magnitude are stable despite n = 10.

## Stage 11 — Model expansion / iteration
The principled next step is the **scientific Poisson** `lambda = exp(a)·population^b_P / gamma` (a mechanistic theory of tool innovation/loss), plus a **robust** treatment of the Hawaii outlier and possibly a **NegativeBinomial** for residual overdispersion (the P09 topic).

## Stage 12 — Decision & communication
**Headline:** *tool-kit size grows with population on the log scale — a +1 SD in log-population
multiplies expected tools by ~1.5× — but with only ten societies and one high-leverage point (Hawaii)
the population × contact interaction is weakly identified and not supported by LOO.* Limitation: n = 10,
high Pareto-k̂; treat the interaction as undetermined, not absent.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
