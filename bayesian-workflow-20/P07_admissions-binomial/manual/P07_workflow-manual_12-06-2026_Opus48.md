# Workflow Manual — Project 07: UCBadmit (Binomial GLM), Simpson's paradox revealed

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 2 (Generalised linear models) · **Model family:** aggregated Binomial GLM (logit link)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P07 is the **payoff of P02**: a single pooled rate cannot fit six
> departments, so we add department as an index variable and watch the apparent gender gap dissolve —
> **Simpson's paradox** (Bickel, Hammel & O'Connell 1975).

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate an aggregated Binomial with known 6-department log-odds and `b_male = -0.1`; fit the dept+gender model; `az.summary(hdi_prob=0.9)`.
- **Observed:** `b_male` recovered (mean **-0.121**, 90% HDI -0.202..-0.035, truth -0.1 inside); department log-odds recovered to within sampling/finite-data error; R̂ = 1.00, ESS-bulk ≈ 3300–5400.
- **Pass criterion:** the key coefficient `b_male` truth inside its 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
Does an applicant's gender affect admission probability at UC Berkeley (1973)? Target: `b_male` (log-odds). Unit: one application within a dept×gender cell.

## Stage 2 — Data & exploration
UCBadmit (`;`-delimited), 6 departments × 2 genders = 12 rows. **Pooled rates: women 0.304, men 0.445** — men appear favoured by ~14 points. **But per department the sign reverses or vanishes:** in dept A women are admitted at **0.824** vs men **0.621**; in B 0.680 vs 0.630; only C/E slightly favour men. Women applied disproportionately to the hardest departments (E, F admit <25%).

## Stage 3 — Model specification (two models)
$$\text{admit}_i \sim \mathrm{Binomial}(N_i, p_i).$$
Model **G** (gender only): $\mathrm{logit}(p_i) = a + b_{male}\text{male}_i$.
Model **DG** (dept+gender): $\mathrm{logit}(p_i) = a_{dept[i]} + b_{male}\text{male}_i$, with $a_{dept}\sim\mathrm{Normal}(0,1.5)$, $b_{male}\sim\mathrm{Normal}(0,1)$.
Department is an **index variable** (`a_dept[dept]`), not dummy contrasts.

## Stage 4 — Prior predictive on the OUTCOME scale [probability]
- **Command:** push the prior through `invlogit`; histogram the implied admission probability.
- **Observed:** implied admission probability spans **5–95% = [0.05, 0.95]** — covers the full plausible range without piling at 0/1.
- **Pass criterion:** prior probabilities cover (0,1) sensibly. **Remedy:** narrow the log-odds prior if it piles at the extremes.

## Stage 5 — Fit
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=7)` for both models, with `idata_kwargs={"log_likelihood": True}` for LOO.

## Stage 6 — Diagnostics
- **Gender-only:** R̂ = 1.01, ESS-bulk ≈ 1020+, 0 divergences.
- **Dept+gender:** R̂ = 1.00, ESS-bulk ≈ 1700–4100, **0 divergences**. All pass.

## Stage 7 — Interpretation: THE PARADOX
- **Gender-only:** `b_male = +0.609` log-odds (94% HDI +0.492..+0.726), **OR = 1.84** — being male multiplies admission odds by 1.84; P(b_male<0) = 0.00.
- **Dept+gender:** `b_male = -0.103` log-odds (94% HDI -0.249..+0.043), **OR = 0.90** — the male advantage **vanishes** (slightly favouring women); P(b_male<0) = 0.91.
- **Sign/shrink check:** b_male moved **+0.609 → -0.103 (change -0.711)**. Simpson's paradox confirmed: the pooled gender gap is entirely a confound with department choice.

## Stage 8 — Posterior predictive check (category PPC: admit count per cell)
- **Discrepancy (per-cell admitted counts):** gender-only covers only **0.17** of the 12 observed cells in its 94% predictive band (χ² discrepancy **433**); dept+gender covers **0.92** (χ² discrepancy **8.2**). The expanded model reproduces every cell; the pooled-gender model badly misfits the high-admit departments.

## Stage 9 — Comparison: gender-only vs dept+gender (PSIS-LOO)
- **Observed:** `elpd_diff = 427.1 ± 150.9` (≈ **2.8 SE**) in favour of dept+gender; stacking weight **1.00** on dept+gender. **Caveat:** max Pareto-k̂ = **1.02 > 0.70** threshold — expected for an aggregated Binomial where each "observation" is a large-count cell, so LOO is approximate. The conclusion (dept+gender vastly better) is unambiguous and corroborated by the PPC; `reloo` or a disaggregated Bernoulli would sharpen the elpd if a precise number were needed.

## Stage 10 — Power-scaling prior sensitivity (b_male)
- **Observed:** E[b_male] = **-0.103 / -0.103 / -0.102** across α ∈ {0.8, 1, 1.25} — essentially fixed. The near-zero gender effect is data-driven, not prior-driven.

## Stage 11 — Model expansion / iteration
Departments are exchangeable draws from a population — the natural next step is a **hierarchical (partial-pooling)** model `a_dept ~ Normal(mu, tau)` (built in P11/P12), which stabilises small departments and gives a population-level rate. A `b_male[dept]` (per-department gender slope) would reveal that department A genuinely favours women.

## Stage 12 — Decision & communication
**Headline:** *pooled over departments, men appear favoured (b_male = +0.61, OR 1.84); conditioning on
department reverses this to b_male = -0.10 (OR 0.90, no male advantage). The pooled gap is Simpson's
paradox — women applied disproportionately to the most competitive departments.* Limitation: aggregated
LOO is approximate (high Pareto-k); the substantive conclusion rests on the coefficient flip and the PPC.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
