# Lessons — Project 04: Simple Linear Regression

The lessons report for the fourth project. It records what the project teaches, the
surprises and failure modes encountered while building and running it, and how simple
linear regression generalizes to the broader world of predictors.

---

## 1. What this project is really about

Project 04 introduces **predictors**: the response is now driven by an external variable
(dose), and we estimate a **slope** and an **intercept** with priors on each. This is the
gateway to all of regression. The new skill is setting priors on regression coefficients;
the headline pitfall is **un-scaled predictors**.

When a predictor lives far from zero — doses on `[100, 600]` here — three things go wrong
simultaneously: the intercept becomes a meaningless extrapolation to `x = 0`, the slope
lives on a scale (~0.015) where priors are hard to guess, and the intercept and slope
become so strongly correlated that the posterior is a thin, tilted banana the sampler
struggles to explore. The fix is one line — **standardize the predictor** — and it
repairs all three problems at once. Project 04 is, at heart, a sustained argument for
that one line.

The model is the Normal location-scale model of Project 02 with a predictor added to the
mean: `mu = alpha + beta * x_std`. The scale-prior lesson from Project 02 carries over
unchanged (`sigma ~ HalfNormal`); what is new is the predictor and its scaling.

---

## 2. Takeaways

### 2.1 Standardize predictors that are far from zero

The central lesson. Standardizing `x` to `(x - mean) / sd`:

- makes the **intercept** the response at the *mean* predictor value — an interpretable,
  in-data quantity rather than an extrapolation;
- makes the **slope** the change per 1 SD of the predictor — an O(1) quantity for which
  a common prior width like `Normal(0, 5)` is meaningful;
- **decorrelates** the intercept and slope, turning a banana-shaped posterior into a
  round, well-conditioned one that NUTS samples efficiently.

It is exact and invertible: fit on the standardized scale, then map coefficients back to
the natural scale for reporting. There is essentially no reason *not* to standardize a
continuous predictor that is far from zero.

### 2.2 Prior widths are not portable across scales

A subtle corollary. A `Normal(0, 5)` prior regularizes sensibly on the standardized scale
but is wildly diffuse on a raw slope of ~0.015 (it allows slopes 300x the truth) and
nonsensical on a raw intercept. There is no single sensible width on the raw scale because
the slope and intercept live on different magnitudes. Standardizing puts them on a common
O(1) footing — which is the only thing that makes "use `Normal(0, 5)` for both" a
defensible default. Copying a prior width from one scale to another without thinking is
BUG 2.

### 2.3 Bad geometry shows up as collapsed ESS, not wrong estimates

A diagnostic lesson. On raw `x`, the point estimates can still be roughly right, but the
`alpha`-`beta` correlation approaches 1 and the effective sample size for both collapses
— sometimes to a few dozen out of thousands of draws. The failure is in *efficiency and
trustworthiness*, not (necessarily) in the point estimate. Reading the pair plot and the
ESS columns, not just the means, is what catches it.

### 2.4 Report on the scale the collaborator uses

The communication lesson. We standardize internally for stable computation, but the
collaborator thinks in natural dose units. Step 8 and the one-pager map everything back:
the dose effect is reported as ~0.015 response per unit dose, not as a standardized
coefficient of ~1.9. The internal device stays internal.

---

## 3. Surprises & failures encountered while building

### 3.1 The back-mapping is exact, and that is reassuring

The standardized fit recovered `alpha_std ~ 7.13`, `beta_std ~ 1.94`, which mapped back
to natural-scale `alpha ~ 1.97`, `beta ~ 0.0155` against the true `2.0` and `0.015`. The
algebra (`beta_nat = beta_std / x_sd`, `alpha_nat = alpha_std - beta_std * x_mean / x_sd`)
is exact, so standardizing genuinely costs nothing in interpretation — a relief, since the
whole pitch is "standardize for free". Seeing the natural-scale numbers land on the truth
confirms the reparameterization is sound.

### 3.2 A tight prior on the standardized scale barely bit

In `prior_sensitivity.py`, even a deliberately tight `Normal(0, 1)` prior — whose SD is
smaller than the true intercept of ~7 — only pulled the intercept to 7.028 and the slope
to 1.917 (from 7.130 / 1.945). With 40 informative points the data overwhelmed even a
prior tighter than the truth. The lesson is double-edged: standardizing makes priors *easy
to set*, and informative data make the fit *robust to getting them slightly wrong* — but
that robustness is a property of N, not a license to be careless at small N.

### 3.3 SBC on three parameters was slow, and vague priors made it slower

SBC here draws `alpha, beta ~ Normal(0, 5)` and refits 30 times. Occasionally a draw of
large coefficients produces a dataset that the tiny sampler handles less gracefully
(transient overflow warnings during tuning), which lengthened individual fits. Trimming to
30 simulations with a 120/120 sampler kept the sweep under ~70s while still giving clean
calibration (all p > 0.6). The recurring SBC lesson: cost is per-fit compilation, so
reduce *simulations*, and keep the sampler tiny.

### 3.4 The scale-mismatch plotting bug is easy to commit

Building the broken notebook, it was striking how natural it is to evaluate a fitted line
on a standardized grid while scattering the data on the raw scale (BUG 3). Nothing errors;
the line just visibly misses the data, tempting you to blame the model. The defense —
check that the data x-range and the line x-range are the same scale — is trivial but easy
to forget.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Standardizing predictors | Every regression with continuous predictors; essential in multiple regression and GLMs. |
| Priors on slopes/intercepts | All regression models; the basis for regularizing/shrinkage priors later. |
| Decorrelating geometry by centering | The same idea powers centered-vs-non-centered tricks in hierarchical models. |
| ESS/correlation diagnostics for coefficients | Load-bearing whenever predictors are collinear. |
| Reporting on the natural scale | Every model fit on a transformed scale (log, logit, standardized). |

Simple linear regression is the atom of supervised modeling. Add more predictors and you
have multiple regression (where standardization and collinearity diagnostics become
essential); swap the Normal likelihood for a Bernoulli with a logit link and you have
logistic regression; add a quadratic term and you have polynomial regression (the
extension). The standardization lesson is non-negotiable in all of them.

---

## 5. Concrete next experiments (for the reader)

- Fit the **raw-x** model (`standardize=False`) and compare the `alpha`-`beta` pair plot
  and ESS to the standardized fit — watch the banana and the ESS collapse.
- Re-run `prior_sensitivity.py` at `N = 6` and watch the tight prior finally bite.
- Add a small quadratic term to the DGP and watch a residuals-vs-dose PPC reveal the
  nonlinearity; fit a quadratic model and compare with `az.compare` — the `rubric.md`
  extension.
- Add a second, collinear predictor and watch the coefficients' ESS drop and their
  posterior correlation rise — a preview of multicollinearity.
