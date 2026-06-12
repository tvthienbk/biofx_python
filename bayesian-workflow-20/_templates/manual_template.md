# Workflow Manual — Project &lt;NN&gt;: &lt;Title&gt;

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** &lt;dd-mm-yyyy&gt; · **Model tag:** Opus48
**Tier:** &lt;1–4&gt; · **Model family:** &lt;e.g. Gaussian / Logistic / Hierarchical normal&gt;

> **Framing — read first.** The Bayesian workflow is **not a linear checklist**. It is an
> *iterative loop* over a *growing network of models* (Gelman et al. 2020). You will pass
> through the stages below more than once, expanding the model when checks fail or questions
> sharpen. The numbering is a *reference order for a single pass*, not a one-way pipeline.

## Master references (cited in all 20 manuals)
- Gelman, Vehtari, Simpson, Margossian, Carpenter, Yao, Kennedy, Gabry, Bürkner, Modrák (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Betancourt (2020). *Towards a Principled Bayesian Workflow.* (web case study).
- Vehtari, Gelman, Simpson, Carpenter, Bürkner (2021). *Rank-normalization, folding, and localization: an improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *Practical Bayesian model evaluation using LOO-CV and WAIC.* Stat. Comput. 27.
- Talts, Betancourt, Simpson, Vehtari, Gelman (2018). *Validating Bayesian inference algorithms with SBC.* arXiv:1804.06788.

---

## Stage 0 — Fake-data parameter recovery (computational faithfulness) [required]
- **Command:** simulate from the model with known θ; `pm.sample(...)`; overlay truth on posterior.
- **Expected output:** posteriors concentrate near the known values.
- **Pass criterion:** every true value inside its 90% HDI; no divergences/pathologies.
- **Failure remedy:** fix model code / priors / parameterization before touching real data.

## Stage 1 — Problem & question
Domain framing, the decision/scientific question, the target quantity, unit of observation, what a "good answer" looks like.

## Stage 2 — Data & exploration (EDA)
Load, describe, missingness, units/scales, plots. Decide transformations (center/standardize); **record the back-transformation** for later interpretation.

## Stage 3 — Model specification
Generative model written explicitly: likelihood, link, parameters, a small DAG. Priors weakly-informative by default: **scale params → `HalfNormal`/`Exponential`** (not `HalfCauchy`); **correlations → `LKJCholeskyCov(eta=2)`**; coefficients → `Normal(0, scale)` on standardized predictors. Math first, then PyMC, then `pm.model_to_graphviz`.

## Stage 4 — Prior predictive check (OUTCOME scale) [upgraded]
`pm.sample_prior_predictive`; plot simulated **outcomes** (push GLMs through the link). Confirm the prior implies *plausible* data. Show before/after when a prior is tightened.
- **Command · expected output · pass criterion · failure remedy** (fill in per model).

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=SEED)`. Record wall-clock; quote sampler warnings verbatim.

## Stage 6 — Computational diagnostics (model-aware)
Default (continuous, NUTS): R̂ < 1.01; ESS-bulk & ESS-tail > 400; 0 divergences; BFMI > 0.3; fuzzy-caterpillar traces. **Remedies:** non-centered parameterization, raise `target_accept`, tighten priors, rescale. **Compound/discrete models:** judge per-block R̂/ESS and discrete mixing; divergence-count criterion waived (document it).

## Stage 7 — Posterior summary & interpretation
`az.summary` (mean, sd, 94% HDI, R̂, ESS-bulk, ESS-tail). Forest/posterior plots. Translate to domain language **in original units** (undo standardization). State uncertainty honestly.

## Stage 8 — Posterior predictive check [required, always]
`pm.sample_posterior_predictive` → `az.plot_ppc` + a **discrepancy statistic suited to the data type** (proportion of zeros for counts; category frequencies for ordinal; min/max/sd for continuous). Identify *systematic* misfit.

## Stage 9 — Model comparison & evaluation [when meaningful]
Compare a **meaningful nested/expanded pair** with PSIS-LOO (`az.compare`, `az.loo`). Check Pareto-k̂ vs `min(1 − 1/log10(S), 0.7)`; moment-matching/`reloo` for bad k. Judge `elpd_diff` against its **SE**. `az.compare` returns **stacking** weights by default. **Hierarchical → leave-one-group-out CV.**

## Stage 10 — Sensitivity analysis [upgraded]
**Power-scaling** prior/likelihood sensitivity (`priorsense`, or power-scale the log-prior/log-lik by hand and re-weight). Report which conclusions are robust and which move.

## Stage 11 — Model expansion / iteration
State the *next* model and why (every Tier ≥ 2 project names a concrete expansion; Tier 3–4 implements ≥ 1).

## Stage 12 — Decision & communication
Answer the Stage-1 question in plain language with calibrated uncertainty; state limitations and who should/shouldn't act. **One headline figure + one headline sentence.**

### Advanced module (Tier 3–4 + capstone) — Simulation-Based Calibration (SBC)
Repeatedly: draw θ̃ from the prior → simulate data → fit → record the **rank** of θ̃ among posterior draws. Ranks must be **uniform** over many replicates; ∪/∩ shapes reveal miscalibration. Use ≥ 100 simulations; plot rank ECDF-difference bands (Säilynoja et al. 2022).

> Every filled-in stage must show **command · expected output · pass criterion · failure remedy.**
