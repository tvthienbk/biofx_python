# Lessons — Project 03: Estimating a Rate (Poisson)

The lessons report for the third project. It records what the project teaches, the
surprises and failure modes encountered while building and running it, and how the
Poisson rate model with an exposure offset generalizes.

---

## 1. What this project is really about

Project 03 estimates an event rate from counts — reads per kilobase, mutations per
sample, any "events per opportunity" structure. Two ideas are new. The first is the
**log link**: a rate must be positive, so we model `log_rate` with a Normal prior and
set `lambda = exp(log_rate)`, which keeps the rate positive and makes the prior
symmetric on the multiplicative scale. The second, and the project's headline, is the
**exposure offset**: when samples differ in exposure, the expected count is
`exposure * lambda`, not `lambda`. Forgetting the offset is the single most common — and
most catastrophic — error in count modeling, and this project is built to make that
failure unmistakable.

The eight workflow steps are unchanged from Projects 01 and 02. What changes is a
discrete likelihood (Poisson), a link function (log), and a structural feature
(exposure) that the model must respect.

---

## 2. Takeaways

### 2.1 Ignoring exposure is a structural error, not a tuning issue

This is the project's central lesson. The no-offset model recovers a "rate" of ~7 — the
mean count per sample — when the true rate per unit exposure is ~0.30. That is a 20-fold
error, and it is *confident*: the sampler converges cleanly, R-hat is 1.00, ESS is
healthy. No computational diagnostic catches it, because nothing is computationally
wrong. The model is answering a different question than the one asked. The only defenses
are (a) understanding the data-generating story well enough to know exposure must enter,
(b) plotting count vs exposure (the upward trend screams "offset"), and (c) checking
recovery against a known truth. The transferable lesson: **structural mis-specification
produces confidently wrong answers that diagnostics will not flag — only modeling
understanding and predictive checks will.**

### 2.2 The log link is the natural parameterization for a positive rate

Putting a prior directly on the rate invites two problems: the rate is bounded below by
zero (a skewed, sampler-unfriendly geometry) and a "flat" prior on it is effectively
improper (the same trap as Project 02's scale). Modeling `log_rate` with a Normal prior
solves both: the rate is positive by construction, the geometry is unconstrained and
benign, and a Normal on the log scale is a sensible weakly-informative prior. This log
link is the same one that powers Poisson and logistic GLMs throughout the portfolio.

### 2.3 Count data are information-rich

With 350 total events, the rate is pinned to within a few percent and the prior is
utterly irrelevant (prior sensitivity max difference: 0.0000 to four decimals). Counts
carry a lot of information per observation, which is why the prior matters so little
here. The corollary: at low total counts (few events) the prior *would* matter, and the
log-scale prior's shape would show through.

### 2.4 Report rates, never raw counts, when units differ

The decision lesson. A collaborator who compares raw counts across samples of different
exposures is comparing exposures, not rates. Step 8 and the one-pager insist on the
rate per unit exposure as the comparable quantity, with predicted counts derived as
`rate * exposure`.

---

## 3. Surprises & failures encountered while building

### 3.1 The no-offset model is *spectacularly* wrong, which is perfect

When building the bias demonstration, the no-offset model landed on `log_rate` ~ 1.94,
i.e. a rate of ~7. At first this looked too extreme to be a useful teaching example —
until it became clear that ~7 is exactly the mean count per sample. The model, denied
the exposure, did the only thing it could: it explained every sample with one average
count. That the bias is so large and so interpretable (it equals `log(mean count)`)
makes it an ideal demonstration. The recovery test asserts the no-offset estimate does
*not* cover the truth, encoding the pitfall as an automated check.

### 3.2 The data ran slightly hot

The synthetic draw produced 350 events over 1100.7 units of exposure, an empirical rate
of 0.318 against a true 0.301. The posterior follows the data (0.318), and the truth
sits inside the interval. Same lesson as the earlier projects: inference reports the
data, not the hidden truth.

### 3.3 SBC cost more wall-clock time than expected

Refitting a fresh PyMC model 40-plus times means paying the model-compilation cost on
every iteration, which dominated the runtime. Keeping SBC under ~90s required trimming
to 40 simulations with a 150/150 sampler. The calibration result (p=0.690) is solid;
the lesson is that SBC's cost is per-fit compilation, not per-draw sampling, so the lever
to pull for speed is *fewer simulations with a tiny sampler*, not fewer draws alone.

### 3.4 The prior predictive needed a log scale to be readable

Total counts implied by `Normal(0, 2)` on log_rate span several orders of magnitude, so
a raw histogram is unreadable — the plot uses `log10(total + 1)`. This is a small but
real lesson about count models: their natural display scale is logarithmic, both for
priors and for the data.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| The log link for positive parameters | Every Poisson/Negative-Binomial GLM; rate and intensity models. |
| Exposure offsets | Any rate-from-counts problem; epidemiological incidence; sequencing depth normalization. |
| Structural mis-specification vs computational error | The distinction underlies all model criticism; diagnostics check computation, PPCs check structure. |
| Information-rich likelihoods swamping priors | Generalizes the Projects 01/02 robustness lesson to discrete data. |
| Reporting normalized rates | Any time observation units differ (exposure, time-at-risk, library size). |

The Poisson offset model is the count-data workhorse. Add covariates to `log_rate` and
you have Poisson regression; allow overdispersion and you have the Negative-Binomial
(the natural next project); keep the offset throughout. The exposure lesson learned here
is non-negotiable in all of them.

---

## 5. Concrete next experiments (for the reader)

- Re-run with very low exposures (so only a handful of total events) and watch the
  prior on `log_rate` finally matter in `prior_sensitivity.py`.
- Run SBC on the *no-offset* model and confirm the rank histogram develops a slope
  (bias) — a clean demonstration that SBC catches structural error.
- Make the counts overdispersed (Negative-Binomial DGP) and watch a variance/dispersion
  PPC reveal that the Poisson under-predicts the spread — the `rubric.md` extension.
- Add a binary covariate to `log_rate` (two groups with different rates) and fit a
  two-rate model, comparing with `az.compare`.
