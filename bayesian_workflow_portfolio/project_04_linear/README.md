# Project 04 — Simple Linear Regression (dose-response)

> **The atom of regression — and a one-line fix that makes or breaks it.** Project 04
> adds a *predictor*: the response is driven by dose, and we estimate a slope and an
> intercept. The pitfall is using the predictor on its raw scale when it lives far from
> zero. The fix — **standardize** — repairs interpretability, priors, and sampler
> geometry all at once.

This README is the **guideline** for Project 04. It walks all eight workflow steps, flags
every assumption, and ties everything to the project's key pitfall — **un-scaled
predictors**. Read it alongside the runnable artifacts:

| Artifact | What it is |
|---|---|
| `data/generate_data.py` | DGP with a predictor **far from zero** and known coefficients. |
| `model.py` | Linear regression on the standardized predictor, with a `to_natural` mapper. |
| `notebook.ipynb` | The clean, runnable, end-to-end workflow. |
| `notebook_broken.ipynb` | The debugging exercise (raw x + two more bugs). |
| `sbc.py` / `SBC_REPORT.md` | Calibration over `alpha`, `beta`, `sigma`. |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | Robustness across coefficient priors. |
| `test_recovery.py` | A fast pytest that recovers the standardized coefficients. |
| `BROKEN_BUGS.md` | Instructor answer key. |
| `rubric.md` | Grading rubric tied to the eight steps. |
| `lessons.md` | The lessons report. |
| `summary_onepager.md` | The non-technical decision summary. |

---

## Table of contents

1. [Why this project exists](#why-this-project-exists)
2. [The eight-step workflow at a glance](#the-eight-step-workflow-at-a-glance)
3. [Mathematical background: linear regression and standardization](#mathematical-background)
4. [Step 1 — Problem & data-generating story](#step-1--problem--data-generating-story)
5. [Step 2 — Model specification & the standardization fix](#step-2--model-specification)
6. [Step 3 — Prior predictive checks](#step-3--prior-predictive-checks)
7. [Step 4 — Inference (NUTS)](#step-4--inference-nuts)
8. [Step 5 — Computational diagnostics](#step-5--computational-diagnostics)
9. [Step 6 — Posterior predictive checks](#step-6--posterior-predictive-checks)
10. [Step 7 — Model criticism & comparison](#step-7--model-criticism--comparison)
11. [Step 8 — Decision & communication](#step-8--decision--communication)
12. [Beyond a single fit](#beyond-a-single-fit)
13. [Common pitfalls](#common-pitfalls)
14. [How to run everything](#how-to-run-everything)
15. [Glossary](#glossary)

---

## Why this project exists

Regression — predicting a response from one or more predictors — is the workhorse of
applied statistics. Project 04 introduces it in its simplest form: one continuous
predictor, a straight-line relationship, Gaussian noise. The new skill is putting priors
on a **slope** and an **intercept**, and the new danger is the scale of the predictor.

When a predictor lives far from zero — doses on `[100, 600]`, ages in years, gene
expression counts — fitting on the raw scale quietly sabotages three things at once:

1. **Interpretability.** The intercept is the response at `x = 0`, which for doses
   starting at 100 is an extrapolation to a value no experiment ever observed.
2. **Priors.** The slope lives on a tiny scale (~0.015 here), so there is no obvious
   sensible prior width, and any width you pick means something different for the slope
   than for the intercept.
3. **Geometry.** Because `x` is far from zero, shifting the intercept can be compensated
   by shifting the slope, so the two become strongly correlated. The posterior is a thin,
   tilted banana that NUTS explores inefficiently — collapsed ESS, sometimes divergences.

The fix is to **standardize** the predictor: replace `x` with `x_std = (x - mean) / sd`.
This one transformation makes the intercept the response at the *mean* predictor (in-data,
interpretable), makes the slope an O(1) "per 1 SD" effect (easy to prior), and
decorrelates the coefficients (clean geometry). It is exact and invertible, so you fit on
the standardized scale and report on the natural scale. Project 04 is, fundamentally, a
sustained demonstration of why this one line matters.

### The scenario

A dose-response experiment: `N = 40` measurements, each pairing a dose `x` (on `[100,
600]`) with a continuous response `y`. The truth is linear: `y = alpha + beta*x + noise`,
with natural-scale `alpha = 2.0`, `beta = 0.015`, `sigma = 0.8`. We want the slope (the
dose effect) and predictions, with uncertainty.

### What is *new* in this project

- **Predictors**, with priors on a **slope** and an **intercept**.
- **Standardization** as the fix for un-scaled predictors, and the exact mapping back to
  the natural scale.
- Calibration (SBC) over three parameters at once (`alpha`, `beta`, `sigma`).

The scale prior on `sigma` is inherited unchanged from Project 02; what is new is the
predictor and its scaling.

---

## The eight-step workflow at a glance

| # | Step | Question it answers | Project 04 artifact |
|---|---|---|---|
| 1 | **Problem & data story** | What generated the data, and what do I assume? | `data/generate_data.py` |
| 2 | **Model spec + priors** | Likelihood? Standardize? Priors on slope/intercept? | `model.py` |
| 3 | **Prior predictive checks** | Do my priors imply sane dose-response lines? | Notebook Step 3 |
| 4 | **Inference** | How do I compute the posterior? | `model.fit` (NUTS) |
| 5 | **Computational diagnostics** | Did the sampler work? Are coefficients decorrelated? | R-hat / ESS / pair plot |
| 6 | **Posterior predictive checks** | Does the line fit across the dose range? | `az.plot_ppc` + overlay |
| 7 | **Model criticism / comparison** | Do the coefficients map back to truth? | `to_natural` |
| 8 | **Decision & communication** | What dose effect do I report (natural scale)? | `summary_onepager.md` |

The cross-cutting principles continue: **flag every assumption** and **check before you
trust**. This project adds a regression-specific one: **mind the scale of your
predictors** — at every stage, from priors to geometry to plotting.

---

<a name="mathematical-background"></a>
## Mathematical background: linear regression and standardization

### The likelihood

```
y_i ~ Normal(mu_i, sigma),    mu_i = alpha + beta * x_i,    i = 1, ..., N.
```

A straight line (`alpha + beta*x`) plus constant-variance Gaussian noise. The intercept
`alpha` is the response when `x = 0`; the slope `beta` is the change in response per unit
of `x`; `sigma` is the noise SD around the line.

### The standardization transform

Define `x_std = (x - x_mean) / x_sd`, where `x_mean` and `x_sd` are the predictor's mean
and SD. Substituting `x = x_mean + x_sd * x_std`:

```
mu = alpha + beta*x = (alpha + beta*x_mean) + (beta*x_sd)*x_std
                    = alpha_std + beta_std * x_std,
```

so the standardized coefficients are

```
alpha_std = alpha + beta * x_mean      (response at the MEAN dose)
beta_std  = beta * x_sd                (change per 1 SD of dose)
```

and the inverse mapping (for reporting) is

```
beta  = beta_std / x_sd
alpha = alpha_std - beta_std * x_mean / x_sd.
```

This is an **exact, invertible reparameterization** — no information is lost. `model.py`
fits `(alpha_std, beta_std, sigma)` and `model.to_natural` maps back to `(alpha, beta)`.

### The priors

On the standardized scale, the coefficients are O(1)-to-O(10), so common weakly-
informative priors are sensible:

```
alpha ~ Normal(0, 5)     # intercept at mean dose, per the standardized scale
beta  ~ Normal(0, 5)     # slope per 1 SD of dose
sigma ~ HalfNormal(2)    # proper scale prior (from Project 02)
```

On the **raw** scale these same widths would be nonsensical (a `Normal(0, 5)` prior on a
slope whose truth is ~0.015 allows slopes 330x too large), which is the whole point:
standardizing is what makes a common, thinkable prior width possible.

### Why the geometry improves

With raw `x` far from zero, the design matrix columns (a constant and `x`) are nearly
collinear after the implicit centering the likelihood performs, so `alpha` and `beta`
are strongly correlated in the posterior — a thin diagonal ridge. Centering `x` (the
"minus mean" half of standardizing) makes the constant and `x_std` orthogonal in
expectation, which **decorrelates** `alpha` and `beta`. Scaling to unit SD (the "divide
by sd" half) puts them on comparable footing. The result is a round, well-conditioned
posterior that NUTS samples with high ESS.

---

## Step 1 — Problem & data-generating story

> **Goal of this step:** encode the linear dose-response with a predictor *far from
> zero*, with known coefficients, and name every assumption.

`data/generate_data.py`:

```python
ALPHA_TRUE, BETA_TRUE, SIGMA_TRUE = 2.0, 0.015, 0.8   # natural scale
N_OBS = 40
DOSE_LOW, DOSE_HIGH = 100.0, 600.0                    # doses far from zero
SEED = 20240604

def generate(...):
    x = rng.uniform(DOSE_LOW, DOSE_HIGH, size=n)
    y = alpha + beta*x + rng.normal(0, sigma, size=n)
    x_std = (x - x.mean()) / x.std()
    # truth reported on the STANDARDIZED scale (what the model fits),
    # plus truth_natural for interpretation.
```

Running it prints:

```
Synthesized 40 dose-response points; doses in [127, 570] (far from zero).
  standardization: x_mean=333.24, x_sd=125.47
  Truth on the STANDARDIZED scale (what the model fits):
    alpha_std=6.999, beta_std=1.882, sigma=0.800
  Truth on the NATURAL scale (for interpretation):
    alpha=2.000, beta=0.0150, sigma=0.800
```

The DGP deliberately reports the truth on **both** scales. The model fits the
standardized coefficients (`alpha_std ~ 7.0`, `beta_std ~ 1.9`); the natural-scale truth
(`alpha = 2.0`, `beta = 0.015`) is what a collaborator cares about, recovered by mapping
back. Note how different the two slopes look (1.88 vs 0.015) — that gulf is exactly why a
prior width sensible for one is absurd for the other.

### Why the predictor must be far from zero

If doses started at zero and ran to a few units, the raw intercept would already be
interpretable and the `alpha`-`beta` correlation modest — the pitfall would barely bite.
Putting doses on `[100, 600]` ensures the raw intercept is a genuine extrapolation and the
coefficients genuinely correlate, so standardizing has a visible payoff. Most real
predictors (concentrations, ages, depths) live far from zero, which is why standardizing
is the default, not a niche trick.

### The assumptions, stated explicitly

- **(A1) Linearity.** The response is a straight-line function of dose. *Violated if* the
  effect saturates or curves (the extension injects curvature).
- **(A2) Gaussian, homoscedastic noise.** Errors are Normal with constant variance across
  the dose range. *Violated if* the response gets noisier at high dose.
- **(A3) Predictor measured without error.** Doses are exact. *Violated if* the delivered
  dose is itself uncertain (errors-in-variables).

We revisit (A1) at Step 6 and in the `rubric.md` extension.

### What can go wrong at Step 1

- **Predictor accidentally near zero.** Hides the standardization lesson. Put it far from
  zero deliberately.
- **No natural-scale truth recorded.** Then you cannot check that the back-mapping is
  correct. Record both scales.

---

## Step 2 — Model specification & the standardization fix

> **Goal of this step:** specify the regression on the *standardized* predictor and
> justify standardizing — the heart of the project.

`model.py`:

```python
def build_model(data, alpha_sd=5.0, beta_sd=5.0, sigma_scale=2.0, standardize=True):
    y = np.asarray(data["y"])
    x = np.asarray(data["x_std"] if standardize else data["x"])
    with pm.Model() as model:
        alpha = pm.Normal("alpha", 0.0, alpha_sd)
        beta  = pm.Normal("beta",  0.0, beta_sd)
        sigma = pm.HalfNormal("sigma", sigma_scale)
        pm.Normal("y", mu=alpha + beta*x, sigma=sigma, observed=y)
    return model
```

The `standardize` switch lets the notebook and demos fit the raw-x version to *exhibit*
the pitfall. The default and recommended setting is `True`.

### Justifying standardization (the three payoffs)

1. **Interpretable intercept.** On `x_std`, `alpha` is the response at `x_std = 0`, i.e.
   at the *mean* dose — a value the experiment actually covers, not an extrapolation.
2. **Settable priors.** On `x_std`, the slope is the change per 1 SD of dose, an O(1)
   quantity. `Normal(0, 5)` is a sensible weakly-informative width for both coefficients
   because both now live on the same scale.
3. **Clean geometry.** Centering decorrelates `alpha` and `beta`; the posterior is round,
   not a banana, so NUTS achieves high ESS. This is a *computational* payoff you can
   measure (compare ESS with `standardize=False`).

### Justifying the priors

`Normal(0, 5)` on each standardized coefficient is weakly-informative — broad enough that
the data dominate, tight enough to rule out absurd lines (checked at Step 3). The
`HalfNormal(2)` on `sigma` is the proper scale prior from Project 02. Crucially, these
widths are only meaningful *because* of standardization; on raw `x` there is no single
sensible width.

### What can go wrong at Step 2

- **Fitting on raw `x`** (BUG 1). Meaningless intercept, unsettable priors, banana
  geometry. Cure: standardize; map back for reporting.
- **Copying a prior width across scales** (BUG 2). A width sensible on one scale is
  nonsensical on another. Cure: standardize first, then use O(1) priors.
- **An improper scale prior on `sigma`.** The Project 02 lesson still applies — keep it
  proper.

---

## Step 3 — Prior predictive checks

> **Goal of this step:** simulate dose-response *lines* from the prior and confirm they
> are plausible.

```python
with model:
    prior = pm.sample_prior_predictive(draws=80, random_seed=RNG)
# draw the implied lines: alpha_i + beta_i * x_std
```

We plot the lines implied by the prior over the standardized predictor range. Under
`Normal(0, 5)` priors the lines fan out widely — many slopes, many intercepts — but stay
within a plausible response range. That wide-but-bounded fan is what a weakly-informative
prior should produce: it does not commit to a slope sign or magnitude, but it does not
predict responses of a million either.

This check is also how you would catch BUG 2. If you used the raw-scale priors over raw
`x ~ [100, 600]`, the implied lines would sweep across an enormous response range
(because `beta * 600` is large even for modest `beta`), revealing that the prior is not
saying what you intended. The prior predictive translates an abstract prior on
coefficients into concrete, checkable predictions about lines.

### What can go wrong at Step 3

- **Skipping it.** A mis-scaled prior is then only caught when the fit misbehaves.
- **Checking coefficients instead of lines.** The pathology is clearest in the *implied
  lines*, which combine slope and intercept. Plot the lines.
- **Forgetting to use the same scale as the model.** Simulate on the standardized scale if
  that is what you fit.

---

## Step 4 — Inference (NUTS)

> **Goal of this step:** compute the joint posterior for `(alpha, beta, sigma)`.

```python
idata = fit(data, draws=1000, tune=1000, chains=4, seed=404)
```

Standard settings: four chains, generous tuning, fixed seed, `log_likelihood=True`, prior
+ posterior predictive attached.

### The geometric payoff is measurable here

Because we standardized, `alpha` and `beta` are decorrelated, the posterior is
well-conditioned, and NUTS mixes efficiently — expect ESS in the thousands and 0
divergences. Refit with `standardize=False` and you can *watch* the cost of not
standardizing: the `alpha`-`beta` correlation climbs toward 1, ESS collapses, and the
sampler labors. Standardization is as much an inference-engineering decision as a modeling
one.

### What can go wrong at Step 4

- **Raw-x geometry** (BUG 1): collapsed ESS, slow mixing, sometimes divergences.
- **Too little tuning / one chain:** unreliable diagnostics, as always.
- **Trusting roughly-right estimates from a badly-mixed raw-x fit.** The means may look
  fine while the ESS says you cannot trust them. Read Step 5.

---

## Step 5 — Computational diagnostics

> **Goal of this step:** confirm the sampler worked, and specifically that the
> coefficients are *decorrelated* — the payoff of standardization.

```python
print(az.summary(idata, var_names=['alpha', 'beta', 'sigma']))
print('divergences:', int(idata.sample_stats['diverging'].sum()))
az.plot_trace(idata, var_names=['alpha', 'beta', 'sigma'])
```

Read the usual three things for all three parameters: R-hat ≈ 1.00, ESS ≳ 400, 0
divergences. With standardized `x` the `alpha`-`beta` correlation is near zero, so ESS is
high (thousands). The standalone `python3 model.py` self-test prints exactly this for the
fixed dataset.

### The regression-specific diagnostic: coefficient correlation

```python
az.plot_pair(idata, var_names=['alpha', 'beta'])
```

On standardized `x`, the `alpha`-`beta` scatter is a round blob — the coefficients are
independent. On raw `x`, it is a thin diagonal line (correlation near 1) — the banana that
wrecks ESS. The pair plot is the fastest way to *see* whether standardization did its job.
If you ever find collapsed ESS on regression coefficients, the pair plot tells you
immediately whether collinear/un-centered predictors are the cause.

### What to do when diagnostics fail

| Symptom | Likely cause | First remedy |
|---|---|---|
| Low ESS on `alpha`/`beta`; high pair correlation | Un-centered/raw predictor | Standardize (center + scale) |
| High R-hat | Chains not converged | More draws; inspect trace |
| Divergences | Hard geometry (often raw-x banana) | Standardize; raise `target_accept` |
| Clean R-hat but low ESS | Strong posterior correlation | Decorrelate via standardization/centering |

The first row is the project's signature failure, and its remedy is the project's central
lesson.

---

## Step 6 — Posterior predictive checks

> **Goal of this step:** confirm the line fits the data *across the dose range*, with no
> systematic structure left in the residuals.

```python
az.plot_ppc(idata, num_pp_samples=100)
```

then overlay the fitted line with its uncertainty band:

```python
xs = np.linspace(x_std.min(), x_std.max(), 50)
lines = alpha[:, None] + beta[:, None] * xs[None, :]
lo, mid, hi = np.percentile(lines, [3, 50, 97], axis=0)
# scatter data on x_std, plot mid line and fill 94% band
```

A well-fit linear model has the data scattered evenly around the line across the whole
dose range, with the 94% band capturing the bulk of the points. The key check is for
**residual structure**: plot residuals (`y - fitted`) against dose and look for a pattern.
A flat, patternless cloud means linearity holds; a U-shape or arch means the relationship
curves and a straight line is mis-specified (the extension's subject).

**Plot on a consistent scale.** Whether you overlay on standardized or raw `x`, the data
and the line must be on the *same* scale — mixing them is BUG 3, which makes a good fit
look terrible. Print the x-ranges of both before plotting.

### What a PPC catches and misses here

A residuals-vs-dose check catches **nonlinearity** and **heteroscedasticity** (if the
residual spread grows with dose). A plain `plot_ppc` of the marginal `y` distribution
catches gross misfit but can miss structure that is only visible against the predictor.
Match the check to the assumption: to test linearity, look at residuals *vs dose*.

### What can go wrong at Step 6

- **Scale-mismatch in the overlay** (BUG 3). Plot data and line on the same scale.
- **Only checking the marginal `y`.** Structure shows up against the predictor; plot
  residuals vs dose.
- **Ignoring fanning residuals.** Growing spread signals heteroscedasticity (A2
  violated).

---

## Step 7 — Model criticism & comparison

> **Goal of this step:** confirm the fit recovers the truth — *on the natural scale the
> collaborator uses* — and note when a competing model is warranted.

### Criticism via the back-mapping

```python
nat = to_natural(idata, data)
# recovered: alpha ~ 1.97, beta ~ 0.0155
# true:      alpha = 2.0,  beta = 0.015
```

The standardized fit (`alpha_std ~ 7.13`, `beta_std ~ 1.94`) maps back to natural-scale
`alpha ~ 1.97`, `beta ~ 0.0155`, matching the true `2.0` and `0.015`. This confirms two
things: the model recovers the truth, and the standardization reparameterization is exact
(the back-mapping is not an approximation). `test_recovery.py` asserts the standardized
coefficients' 94% intervals cover the standardized truth.

### When to compare models

The natural competitor is a **quadratic** model, `mu = alpha + beta*x_std + gamma*x_std^2`,
which the extension introduces. With `log_likelihood=True` stored, comparing is one call:

```python
az.compare({"linear": idata_linear, "quadratic": idata_quadratic})
```

On the truly-linear data here, LOO should find the quadratic term unnecessary (its
coefficient overlaps zero and LOO does not prefer it) — correctly reporting that the
simpler model suffices. On curved data (the extension's DGP), LOO would prefer the
quadratic. That contrast — comparison that knows when *not* to add complexity — is the
lesson.

### What can go wrong at Step 7

- **Reporting standardized coefficients to a collaborator.** Map back to the natural
  scale; `beta_std ~ 1.9` is meaningless to someone thinking in dose units.
- **Forgetting `log_likelihood=True`.** Then LOO needs a refit.
- **Adding a quadratic term and over-reading a tiny LOO gain.** Read the LOO difference's
  standard error; a gain within ~2 SE is not decisive.

---

## Step 8 — Decision & communication

> **Goal of this step:** report the dose effect on the natural scale, with uncertainty,
> and predict a response at a dose of interest.

```python
beta_nat = idata.posterior['beta'].values.ravel() / data['x_sd']
# dose effect ~ 0.015 / unit, 94% CI ~ [0.011, 0.019]
# predicted response at dose 400 ~ 8
```

For the fixed dataset:

- **Dose effect** ~ 0.015 response units per unit dose, 94% CI ~ `[0.011, 0.019]` —
  clearly positive.
- **Predicted response at dose 400** ~ 8, with its own credible interval.

### The communication that matters: report on the natural scale

We standardized internally for stable estimation, but every reported number is mapped back
to natural dose units. The collaborator never sees the standardized scale. The one-pager
(`summary_onepager.md`) leads with "each unit of dose raises the response by ~0.015" and
explains that standardization was a purely internal device that does not change the
science.

### What can go wrong at Step 8

- **Reporting the standardized slope.** Map back; report per natural unit.
- **Predicting without back-transforming the query dose.** To predict at dose 400, convert
  it to `x_std = (400 - x_mean) / x_sd` before plugging into the standardized line.
- **Ignoring the linearity caveat.** If the relationship curves, the line mis-predicts at
  the extremes. Flag it.

---

<a name="beyond-a-single-fit"></a>
## Beyond a single fit: SBC, prior sensitivity, and the broken notebook

### Simulation-Based Calibration

`sbc.py` runs SBC over all three parameters on a standardized design: draw
`(alpha, beta, sigma)` from the priors, simulate, refit, rank each truth. Over 30
simulations the ranks are uniform for all three (`alpha` p = 0.797, `beta` p = 0.675,
`sigma` p = 0.797), confirming the model and sampler are calibrated. Standardization is
part of why the geometry is clean enough to calibrate easily. Detail in `SBC_REPORT.md`.

### Prior sensitivity

`prior_sensitivity.py` refits under `Normal(0, 20)`, `Normal(0, 5)`, and `Normal(0, 1)` on
the coefficients. The vague and weakly-informative priors agree exactly; even a tight
prior (SD smaller than the true intercept) shifts the slope by under 0.03 (standardized).
The lesson: standardizing is what makes a common O(1) prior width meaningful; un-scaled `x`
would make priors un-settable. Detail in `PRIOR_SENSITIVITY.md`.

### The broken notebook

`notebook_broken.ipynb` seeds three bugs; `BROKEN_BUGS.md` is the answer key:

- **BUG 1 (headline)** — regressing on the **raw, un-scaled predictor**. *Revealed by*
  collapsed ESS and an `alpha`-`beta` pair plot showing near-perfect correlation (banana).
- **BUG 2** — a **prior width copied across scales** without thinking. *Revealed by* a
  prior predictive check whose implied lines sweep an absurd response range on raw `x`.
- **BUG 3** — the fitted line **plotted on the wrong x scale** (standardized line over
  raw-x data). *Revealed by* comparing the data's x-range to the line's x-range.

---

<a name="common-pitfalls"></a>
## Common pitfalls (tied to this project's key pitfall)

### 1. Un-scaled predictors far from zero (THE key pitfall)
Raw `x` on `[100, 600]` gives a meaningless intercept, unsettable priors, and a
banana-shaped posterior with collapsed ESS. **Cure:** standardize (center + scale); map
coefficients back to the natural scale for reporting.

### 2. Copying prior widths across scales
A width sensible on the standardized scale is nonsensical on the raw scale, and vice versa.
**Cure:** standardize first, then use O(1) priors; check with a prior predictive.

### 3. Reading the means but not the ESS/correlation
Raw-x fits can have roughly-right means but collapsed ESS. **Cure:** read ESS and the
`alpha`-`beta` pair plot, not just the point estimates.

### 4. Mixing scales in a plot
Overlaying a standardized line on raw-x data (or vice versa) makes a good fit look bad.
**Cure:** plot data and line on the same scale; print both x-ranges first.

### 5. Reporting standardized coefficients
`beta_std ~ 1.9` is meaningless to a collaborator. **Cure:** map back to per-natural-unit
effects.

### 6. Assuming linearity without checking
A straight line can hide curvature. **Cure:** a residuals-vs-dose PPC; a quadratic model
+ LOO if structure appears.

### 7. Forgetting the scale prior lesson
`sigma` still needs a proper prior (Project 02). **Cure:** `HalfNormal`/`Exponential`/
`HalfCauchy`, never improper.

---

## How to run everything

All commands run **from the project directory** with `python3` (the only interpreter with
numpy/pymc here — never bare `python` or `pytest`).

```bash
python3 data/generate_data.py
python3 model.py
python3 build_notebook.py
python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb
python3 -m pytest test_recovery.py -q
python3 sbc.py
python3 prior_sensitivity.py
```

Then open `notebook.ipynb` and run it top to bottom. Dependencies are pinned by the shared
top-level `requirements.txt` / `environment.yml`.

---

## Glossary

- **Predictor (covariate)** — an input variable used to explain the response; here the
  dose `x`.
- **Intercept (`alpha`)** — the response when the predictor is zero (or, standardized, at
  the mean predictor value).
- **Slope (`beta`)** — the change in response per unit of the predictor (or, standardized,
  per 1 SD of the predictor).
- **Standardization** — replacing `x` with `(x - mean) / sd`; centers and scales the
  predictor.
- **Centering** — subtracting the mean (decorrelates intercept and slope).
- **Scaling** — dividing by the SD (puts coefficients on a common O(1) footing).
- **Collinearity / correlation of coefficients** — when coefficients trade off in the
  posterior, producing a ridge that the sampler explores inefficiently.
- **Homoscedasticity** — constant noise variance across the predictor range (assumption
  A2).
- **NUTS, R-hat, ESS, divergence** — see Project 01's glossary; identical meanings here.
- **SBC** — simulation-based calibration; here over `alpha`, `beta`, `sigma`.
- **LOO** — leave-one-out cross-validation for model comparison (e.g. linear vs quadratic).
- **Bayesian p-value** — posterior-predictive probability of a discrepancy statistic as
  extreme as observed; near 0.5 indicates good fit.

---

*Project 04 of the 20-project Bayesian-workflow teaching portfolio. Simple linear
regression is the atom of supervised modeling: add predictors for multiple regression,
swap the likelihood and link for logistic regression, add a quadratic term for polynomial
regression. The lesson to standardize predictors that live far from zero — for
interpretable intercepts, settable priors, and clean geometry — is non-negotiable in all
of them.*
