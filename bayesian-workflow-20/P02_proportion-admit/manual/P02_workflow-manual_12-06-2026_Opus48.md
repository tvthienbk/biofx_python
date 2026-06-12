# Workflow Manual — Project 02: A Single Proportion (pooled admission rate)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 1 (Foundations) · **Model family:** Beta-Binomial (single proportion p)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020), not a one-way pipeline. P02 builds the smallest GLM-adjacent model —
> one proportion — and ends by *naming the model that fixes it* (P07). The numbering is a reference
> order for a single pass.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Rank-normalization … improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *Practical Bayesian model evaluation using LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** `y_sim = rng.binomial(1000, 0.38)`; fit `Binomial(1000, p)`, `p ~ Beta(2,2)`; `az.summary(hdi_prob=0.9)`.
- **Observed:** p̂ = 0.384 (90% HDI 0.357–0.408); **0.38 inside** → recovery passes; R̂ = 1.00, ESS ≈ 2900/4300.
- **Pass criterion:** truth inside 90% HDI, no pathologies. **Remedy if failed:** fix prior/likelihood code before real data.

## Stage 1 — Problem & question
What is the **overall admission probability** at UC Berkeley (1973), pooling all six departments? Target: a single p. Unit: one application. A good answer is a tight interval for p — *plus* the recognition that the pooled number is the wrong object for comparing groups.

## Stage 2 — Data & exploration
`UCBadmit.csv` (rethinking, **`;`-delimited**). 12 rows (6 departments × 2 genders) with `admit`, `reject`, `applications`. **Pooled:** 1755 / 4526 = **0.388** admitted. **Pooled by gender:** female **0.304**, male **0.445** — a 14-point apparent gap that motivates the whole project (and dissolves in P07).

## Stage 3 — Model specification
$$y \sim \mathrm{Binomial}(N, p), \qquad p \sim \mathrm{Beta}(2, 2).$$
`y` = total admitted, `N` = total applications. `Beta(2,2)` is weakly-informative — gentle mass toward mid-range p, away from the 0/1 extremes. The conjugate posterior is `Beta(2 + y, 2 + N − y)`, which we use as an exact check.

## Stage 4 — Prior predictive (OUTCOME scale)
- **Command:** `pm.sample_prior_predictive`; histogram of `y / N` (admitted *proportion*).
- **Observed:** central 5–95% spans roughly the whole unit interval — `Beta(2,2)` admits any plausible rate; no absurd mass.
- **Pass criterion:** plausible proportions, no spike at 0 or 1. **Remedy:** use a more concentrated Beta if domain knowledge is strong.

## Stage 5 — Fit
`pm.sample(draws=2000, tune=1000, chains=4, target_accept=0.9, random_seed=2)`. Sub-second; no warnings.

## Stage 6 — Diagnostics
- **Observed:** p = 0.388, R̂ = 1.00, ESS-bulk ≈ 3100, ESS-tail ≈ 4600, **0 divergences**, BFMI ≈ 1.1–1.3. All pass.

## Grid vs MCMC (the new skill)
Evaluate the one-parameter posterior on a 2000-point grid and overlay the MCMC histogram and the
exact `Beta` posterior. **Posterior means agree to four decimals:** MCMC 0.3877, grid 0.3879, exact
0.3879. The lesson: for one parameter all three methods coincide — MCMC's value is that it *keeps
working* when the parameter count grows and the grid becomes infeasible.

## Stage 7 — Interpretation
**Overall admission probability p = 0.388 (94% HDI 0.375–0.403)** — about 39 of every 100
applications admitted, pooling all departments.

## Stage 8 — Posterior predictive check (department level)
The pooled model reproduces the *total* by construction, so the informative check is per department.
**Observed department rates range from 0.06 to 0.64** — wildly outside the pooled 94% HDI (0.375–0.403).
A single p cannot fit six departments: the systematic misfit *is* the result.

## Stage 9 — Model comparison
Formal LOO comparison is deferred to P07 (where a department + gender GLM is the meaningful expanded
model). At Tier 1 the rubric permits dropping comparison; the Stage-8 department plot already shows
the pooled model is inadequate.

## Stage 10 — Power-scaling prior sensitivity
Reweight by `prior^(α−1)` for α ∈ {0.5, 1, 2}: E[p] = 0.3876 / 0.3877 / 0.3877 — unchanged. With
N > 4500 applications the prior is irrelevant; the data fix p.

## Stage 11 — Model expansion / iteration
**Next model: P07 — `admit ~ department + gender` (Binomial GLM).** Conditioning on department
dissolves the 0.304-vs-0.445 gender gap (women applied disproportionately to harder departments):
**Simpson's paradox.**

## Stage 12 — Decision & communication
**Headline:** *the pooled Berkeley admission probability is ≈ 0.39 (94% HDI 0.375–0.403), but this
single number is misleading — admission rates span 0.06–0.64 across departments, so a pooled rate must
never be used to compare applicant groups.* Limitation: pooling discards the only variable
(department) that explains the gender pattern.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
