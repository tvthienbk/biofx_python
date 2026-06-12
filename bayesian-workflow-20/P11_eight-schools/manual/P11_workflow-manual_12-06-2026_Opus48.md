# Workflow Manual — Project 11: Eight Schools (centered vs non-centered + the funnel)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 3 (Multilevel) · **Model family:** Hierarchical normal (partial pooling)

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020). P11 is the **first multilevel model** and a **deliberate-failure
> project**: the textbook *centered* parameterization breaks the sampler in the *funnel*; the
> *non-centered* form fixes the geometry without changing the model. Tier 3 adds **Simulation-Based
> Calibration (SBC)** to certify the fixed sampler.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.
- Talts et al. (2018). *Validating Bayesian Inference Algorithms with SBC.* arXiv:1804.06788.
- Säilynoja, Bürkner, Vehtari (2022). *Graphical Test for Discrete Uniformity.* Stat. Comput. 32.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate from `mu = 6, tau = 5`; draw `theta_j`, then `y_j`; fit the **non-centered** model; `az.summary(hdi_prob=0.9)`.
- **Observed:** mu recovered (6.04, 90% HDI −0.61 to 13.27), tau recovered (4.94, HDI 0.00 to 10.27); R̂ = 1.00.
- **Pass criterion:** both truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
Is there a real coaching effect across 8 schools, and how much should each noisy estimate be **shrunk**
toward the common mean `mu`? The key hyperparameter is `tau`, the between-school SD (`tau→0` = complete
pooling; large `tau` = no pooling). Unit: one school.

## Stage 2 — Data & exploration
Rubin (1981) eight schools, **hardcoded**: `y = [28, 8, −3, 7, −1, 1, 18, 12]`,
`sigma = [15, 10, 16, 11, 9, 11, 10, 18]`. Precision-weighted pooled mean **7.69**. Every school's
interval overlaps every other's — much of the spread could be sampling noise.

## Stage 3 — Model specification
$$y_j \sim \mathrm{Normal}(\theta_j, \sigma_j),\quad \theta_j \sim \mathrm{Normal}(\mu, \tau),\quad \mu\sim\mathrm{Normal}(0,10),\ \tau\sim\mathrm{HalfNormal}(10).$$
The **centered** form samples `theta_j` directly. When `tau` is small, `(theta_j, tau)` forms a sharp
*funnel* HMC cannot traverse with one step size → divergences.

## Stage 4 — Prior predictive on the OUTCOME scale
- **Observed:** prior-predictive school effects have mean 0.2, sd 18.8, 1–99% range [−46, 47] points — plausible (tens of points, not thousands).
- **Pass criterion:** implied effects are physically sensible. **Remedy:** tighten `mu`/`tau` priors if effects explode.

## Stage 5 — Fit the CENTERED model [the deliberate failure]
`pm.sample(1000, tune=1000, chains=4, target_accept=0.9, seed=11)`. ~12 s.

## Stage 6 — Diagnostics of the CENTERED model: the failure
- **Observed:** **129 divergences**; tau ESS-bulk only **215** (ess-tail 140); R̂(tau) = **1.02** (> 0.01 target). Textbook funnel pathology.
- **Stage 6b — the funnel visualized:** `plot_pair(theta[0], tau, divergences=True)` shows divergent draws clustered in the neck — median `log(tau) = 0.22` for divergent draws vs **1.55** for non-divergent.

## Stage 5-fix / 6-fix — the NON-CENTERED reparameterization [the fix]
Write `theta_j = mu + tau·z_j`, `z_j ~ Normal(0,1)`, so `z` and `tau` are *a priori independent*.
- **Observed:** **0 divergences** (was 129); tau ESS-bulk **2008** (was 215); R̂ = 1.00; BFMI ≈ 0.88–0.98. Same posterior, friendlier geometry.
- **Stage 6c:** the identical `theta[0]` vs `tau` plot now reaches the neck cleanly with no divergences.

## Stage 7 — Interpretation (non-centered) + shrinkage
- **mu = 6.40** (94% HDI −1.28 to 14.35); **tau = 4.90** (94% HDI 0.01 to 11.75 — poorly identified from only 8 schools).
- **Shrinkage:** school A's raw +28 is pulled to **9.06**; C's −3 rises to **5.23**; G's +18 to **8.83**. Small-information schools shrink hard toward `mu`.

## Stage 8 — Posterior predictive check
- **Discrepancy stats:** mean p = 0.36, sd p = 0.74, min p = 0.15, max p = 0.41 — no gross misfit; the hierarchical model reproduces the observed spread of estimates.

## Stage 9 — Comparison: partial vs complete pooling (LOO)
The centered/non-centered choice is *computation*, so the genuine model comparison is **partial pooling**
vs **complete pooling** (`tau→0`).
- **Observed:** `elpd_diff` = **0.30 ± 0.18** (1.7 SE) — the two are statistically indistinguishable with J = 8; max Pareto-k̂ = 0.55 < 0.70 (LOO reliable). With so few schools and weak evidence for `tau > 0`, complete pooling is nearly as good — exactly the right humility.

## Stage 10 — Power-scaling prior sensitivity (tau)
- **Observed:** E[tau] = 5.12 / 4.90 / 4.66 across α ∈ {0.8, 1, 1.25}; E[mu] = 6.62 / 6.40 / 6.15. Mild movement in `tau` (expected — it is weakly identified), `mu` essentially stable.

## Stage 11 — SBC (Simulation-Based Calibration) [Tier-3 required]
- **Command:** 150 sims; each draws `(mu_t, tau_t)` from the priors, simulates `y`, refits the non-centered model with a cheap sampler (draws=400, tune=400, chains=2); record rank of `mu_t` among 800 posterior draws.
- **Observed:** rank histogram flat; **chi-square = 16.7, df = 19, p = 0.612 → uniform (calibrated)**. Runtime 347 s (within the Tier-3 < 8 min budget). No ∪/∩ shape → no systematic bias in `mu`.

## Stage 12 — Decision & communication
**Headline:** *the coaching effect is small and uncertain (`mu` ≈ 6 points, 94% HDI crossing 0), with
`tau` barely identified from 8 schools. The* **centered** *parameterization fails with 129 divergences in
the funnel; the* **non-centered** *form fixes it (0 divergences, ESS ×9), and SBC (p = 0.61) confirms the
fixed sampler is calibrated.* Limitation: with J = 8, `tau` and any "best school" ranking remain highly
uncertain — do not over-interpret school A's raw +28.

---
*SBC is introduced here at Tier 3. Every stage lists command · expected output · pass criterion · failure remedy. This is a model-aware acceptance: the centered failure is shown, explained, then fixed.*
