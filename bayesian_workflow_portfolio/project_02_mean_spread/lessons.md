# Lessons — Project 02: Estimating a Mean & Spread

The lessons report for the second project in the portfolio. It records what the
project teaches, the surprises and failure modes encountered while building and
running it, and how the Normal location-scale model generalizes.

---

## 1. What this project is really about

Project 01 estimated one number. Project 02 estimates **two** — a location `mu` and a
scale `sigma` — and the jump from one parameter to two is where the real lessons of
joint inference begin. The headline new skill is **inferring a scale parameter
jointly with a location**, with priors on both. The headline pitfall is the **scale
prior**: the same "flat is not uninformative" trap from Project 01, but now with
teeth, because on a scale parameter a flat/improper prior is not merely a mild nudge —
it is improper, it puts unbounded mass on huge variances, and it can break inference
outright.

The scenario — replicate measurements of a concentration — is the everyday structure
of any lab measurement: a true value plus instrument/pipetting noise. We want both the
value and the noise, because the noise is what tells a collaborator how much to trust
a single future reading.

The eight workflow steps are identical to Project 01; only the likelihood and the
geometry change. That is the whole pedagogical point of the portfolio: reuse the
process, learn the new wrinkle.

---

## 2. Takeaways

### 2.1 A scale parameter must have a proper prior

This is the project's central lesson and the dangerous sibling of Project 01's "flat
is not uninformative". On a *probability* (Project 01), a flat `Beta(1,1)` is still a
proper prior — it merely over-trusts the edges. On a *scale*, a flat prior is
`Uniform(0, inf)`, which is **improper**: it does not integrate to a finite value, it
asserts that `sigma = 500,000` is overwhelmingly more plausible than `sigma = 1`, and
in the worst case (small `N`) it yields an *improper posterior*. We default to a
proper `HalfNormal(5)` and offer `Exponential` / `HalfCauchy` alternatives. The habit:
**never put a flat/unbounded prior on a positive scale.**

### 2.2 The location is known far better than any single measurement

A subtle but important point for communication. After 30 replicates, the posterior for
`mu` is tight (SD ~0.27) because averaging cancels noise. But `sigma` (~1.45) describes
the scatter of a *single* measurement, which is much larger. Conflating "uncertainty
in the average" with "spread of one measurement" is a classic reporting error; this
project forces the distinction into Step 8 and the one-pager.

### 2.3 Calibrate the scale, not just the location

SBC in Project 01 had one parameter. Here it must run over `(mu, sigma)` *separately*,
because the failure modes differ: locations are forgiving, scales are where
over/under-confidence hides. Our SBC found both calibrated (mu p=0.736, sigma p=0.534),
but the fact that we *checked sigma at all* is the transferable habit — every later
project with a variance, a hierarchical scale, or a dispersion parameter owes it the
same separate calibration check.

### 2.4 Parameterization bugs are silent and common

The variance-vs-SD confusion (BUG 2) — passing `sigma**2` where PyMC wants the SD — is
among the most common errors in applied Bayes, and it raises no error. The only
defenses are knowing the API's convention (`pm.Normal` takes the SD) and checking
recovery against a known truth. This is why every project ships a `test_recovery.py`
against synthetic data with a known `sigma`.

---

## 3. Surprises & failures encountered while building

### 3.1 The data came out noisier than the truth

The synthetic draw (seed 20240602) produced an empirical SD of **1.389** against a true
`sigma` of 1.2 — the sample happened to be ~16% more scattered than the generating
process. The posterior for `sigma` (mean ~1.45) faithfully follows the *data*, not the
hidden truth, and the truth still sits inside the 94% interval. This is the same lesson
as Project 01's "mean isn't the truth": inference reports what the data say, and a
posterior that tracked the hidden truth more closely than the data warrant would be
*wrong*, not better.

### 3.2 Proper scale priors agreed to three decimals

Running `prior_sensitivity.py`, `HalfNormal`, `Exponential`, and `HalfCauchy` gave
`sigma` posterior means of 1.450, 1.454, 1.454 — a spread of **0.004**. With 30
informative points the likelihood for the scale is sharp and the priors' differing
tails are irrelevant. The lesson is *not* "the prior never matters" — it is that the
choice *among proper priors* is minor while the choice *between proper and improper*
(the seeded bug) is decisive. Robustness here is a property of `N = 30`.

### 3.3 The improper prior did not always crash

A genuine surprise: with this particular 30-point dataset, the `Uniform(0, 1e6)` prior
on `sigma` (BUG 1) did not produce an obviously broken posterior — the informative data
partly rescued it. That is exactly the trap. An improper prior that "works" on a lucky
dataset lulls you into using it on the next dataset, where small `N` exposes the
improper posterior. The defense is the *prior predictive check* (which shows the
absurd implied spreads regardless of the data) plus the principled rule "never improper
on a scale".

### 3.4 Scale parameters cost the sampler more

The `sigma` ESS (~700) consistently ran below the `mu` ESS in the standalone fit. Scale
parameters live on a skewed, positively-constrained geometry that NUTS finds slightly
harder than a symmetric location. Nothing pathological here, but it foreshadows the
hierarchical "funnel" geometries where the scale genuinely fights the sampler.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Proper priors on scale parameters | Every model with a variance, dispersion, or hierarchical SD (P03, P06, the hierarchical projects). |
| Joint inference of location + scale | The foundation of regression (P04 adds predictors to exactly this structure). |
| Separate SBC per parameter | Standard once models have several parameters of different character. |
| Distribution-parameterization care (SD vs variance) | A recurring silent-bug class across every PyMC model. |
| Reporting spread vs uncertainty-in-the-mean | Generalizes to every predictive vs parametric uncertainty distinction. |

The Normal location-scale model is the bridge between Project 01's single proportion
and the regression models that follow: add a predictor to `mu` and you have linear
regression (Project 04); let `sigma` vary and you have heteroscedasticity; swap the
Normal for a Student-t and you have robust regression. The scale prior lesson learned
here is load-bearing in all of them.

---

## 5. Concrete next experiments (for the reader)

- Re-run `prior_sensitivity.py` with `N=3`. Watch the heavy-tailed `HalfCauchy` and the
  light-tailed `HalfNormal` finally disagree.
- Replace `HalfNormal` with `Uniform(0, 1e6)` and re-run SBC at small `N`; confirm the
  `sigma` rank histogram develops a shape (miscalibration) or the fit fails to settle.
- Deliberately pass `sigma**2` to the likelihood and watch `test_recovery.py` fail on
  `sigma` while `mu` stays fine — a clean demonstration of the variance/SD bug.
- Make the noise heteroscedastic (SD growing across replicates) and watch a PPC on a
  half-vs-half spread statistic detect the misfit — the `rubric.md` extension.
