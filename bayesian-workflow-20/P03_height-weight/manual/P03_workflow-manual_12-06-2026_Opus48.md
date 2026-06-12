# Workflow Manual — Project 03: Height ~ Weight (Normal linear regression)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Date:** 12-06-2026 · **Model tag:** Opus48
**Tier:** 1 (Foundations) · **Model family:** Normal linear regression

> **Framing — read first.** The Bayesian workflow is an *iterative loop* over a *growing network of
> models* (Gelman et al. 2020), not a one-way pipeline. P03 adds one predictor to P01; its central
> craft skill is the **prior predictive check on the slope**.

## Master references (cited in all 20 manuals)
- Gelman et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Vehtari et al. (2021). *Improved R̂.* Bayesian Analysis 16(2).
- Vehtari, Gelman, Gabry (2017). *LOO-CV and WAIC.* Stat. Comput. 27.

---

## Stage 0 — Fake-data parameter recovery [required]
- **Command:** simulate `h = 155 + 0.9·(w−w̄) + Normal(0,5)`; fit; `az.summary(hdi_prob=0.9)`.
- **Observed:** a recovered (155.1), b recovered (0.93), σ recovered (4.98) — all truths inside 90% HDI; R̂ = 1.00.
- **Pass criterion:** all truths inside 90% HDI. **Remedy:** fix model/priors before real data.

## Stage 1 — Problem & question
How much taller, on average, is a heavier !Kung adult? Target: the slope b (cm per kg). Unit: one adult.

## Stage 2 — Data & exploration
Howell1 (`;`-delimited), `age >= 18` → 352 adults. weight-height correlation **0.75**. **Centering:**
`wc = weight − 45.0 kg`, so the intercept a becomes the mean height *at average weight* (interpretable),
and the sampler explores a and b nearly independently (higher ESS).

## Stage 3 — Model specification
$$h_i \sim \mathrm{Normal}(\mu_i,\sigma),\quad \mu_i = a + b(w_i-\bar w),\quad a\sim\mathrm{Normal}(178,20),\ b\sim\mathrm{LogNormal}(0,1),\ \sigma\sim\mathrm{HalfNormal}(20).$$
`b ~ LogNormal(0,1)` enforces a **positive** slope (heavier ⇒ taller) with median 1 cm/kg — defended next.

## Stage 4 — Prior predictive on the SLOPE [the key lesson]
- **Command:** draw (a,b) from two priors; plot implied height-vs-weight lines over the real weight range.
- **Observed:** `b ~ Normal(0,10)` produces many *downward* and superhuman lines (heights > 272 cm or < 0);
  `b ~ LogNormal(0,1)` keeps every line positive and humane.
- **Pass criterion:** the prior-implied *lines* are physically plausible (checked on the outcome, not just b).
- **Remedy:** if lines are absurd, constrain the slope's sign/scale — exactly the move from Normal(0,10) to LogNormal(0,1).

## Stage 5 — Fit
`pm.sample(draws=1000, tune=1000, chains=4, target_accept=0.9, random_seed=3)`. ~3 s; no warnings.

## Stage 6 — Diagnostics
- **Observed:** R̂ = 1.00 for a, b, σ; ESS-bulk ≈ 3000–4200; **0 divergences**; BFMI ≈ 1.1–1.2. All pass.

## Stage 7 — Interpretation (original units)
**Each +1 kg of weight ↔ +0.90 cm height (94% HDI 0.83–0.99).** Intercept a = 154.6 cm = mean height at
45 kg. Note **σ falls from 7.8 cm (P01) to 5.1 cm** — weight explains a large share of height variation.
The fitted line + 94% HDI ribbon overlays the scatter tightly.

## Stage 8 — Posterior predictive check
- **Discrepancy stats (continuous):** mean p = 0.50, sd p = 0.50, max p = 0.20, **min p = 0.08** — a faint
  residue of the short-tail asymmetry from P01, now much reduced. No gross misfit.

## Stage 9 — Comparison: linear vs intercept-only (P01)
- **Observed:** `elpd_diff` = **147.3** in favour of the linear model with `dse` = 14.5 → **10.1 SE**, decisive;
  stacking weight 0.98 on linear. Max Pareto-k̂ = 0.15 < threshold 0.70 → LOO reliable. Adding weight is
  unambiguously worth it.

## Stage 10 — Power-scaling prior sensitivity (slope b)
- **Observed:** E[b] = 0.9037 / 0.9034 / 0.9029 across α ∈ {0.8,1,1.25} — essentially fixed; the slope is
  data-driven, not prior-driven, despite the informative LogNormal.

## Stage 11 — Model expansion / iteration
The straight line is adequate for adults; once children enter, the relationship curves. The natural next
step is a **polynomial or spline in weight** — built in full in **P18** (B-splines).

## Stage 12 — Decision & communication
**Headline:** *among !Kung adults, each additional kilogram is associated with about **0.90 cm** more
height (94% HDI 0.83–0.99); the relationship is strong, positive, and tightly estimated.* Limitation:
linear only over the adult weight range — do not extrapolate to children or to weights outside ~30–63 kg.

---
*SBC is introduced at Tier 3 (P11); not required here. Every stage lists command · expected output · pass criterion · failure remedy.*
