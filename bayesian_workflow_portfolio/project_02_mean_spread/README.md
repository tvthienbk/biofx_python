# Project 02 — Estimating a Mean & Spread (Normal location-scale)

> **Two parameters, one of them a scale.** Project 01 estimated a single proportion.
> Here we estimate a location `mu` *and* a spread `sigma` jointly — and we meet the
> first genuinely dangerous prior in the portfolio: a flat/improper prior on a scale
> parameter. The workflow is unchanged; the wrinkle is the scale.

This README is the **guideline** for Project 02. It walks all eight workflow steps in
detail, flags every modeling assumption, ties everything to the project's key pitfall
(**improper/uninformative scale priors**), and says what to do when each step fails.
Read it alongside the runnable artifacts:

| Artifact | What it is |
|---|---|
| `data/generate_data.py` | The data-generating process with known `mu`, `sigma`. |
| `model.py` | The `Normal(mu, sigma)` model, decoupled from the notebook. |
| `notebook.ipynb` | The clean, runnable, end-to-end workflow. |
| `notebook_broken.ipynb` | The debugging exercise (three seeded bugs). |
| `sbc.py` / `SBC_REPORT.md` | Calibration over **both** `mu` and `sigma`. |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | Robustness across scale priors. |
| `test_recovery.py` | A fast pytest that inference recovers `mu` and `sigma`. |
| `BROKEN_BUGS.md` | Instructor answer key for the broken notebook. |
| `rubric.md` | Grading rubric tied to the eight steps. |
| `lessons.md` | The lessons report. |
| `summary_onepager.md` | The non-technical decision summary. |

---

## Table of contents

1. [Why this project exists](#why-this-project-exists)
2. [The eight-step workflow at a glance](#the-eight-step-workflow-at-a-glance)
3. [Mathematical background: the Normal location-scale model](#mathematical-background)
4. [Step 1 — Problem & data-generating story](#step-1--problem--data-generating-story)
5. [Step 2 — Model specification with justified priors](#step-2--model-specification)
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

Almost every measurement in a lab is a true value contaminated by noise. You pipette
the same sample 30 times and get 30 slightly different numbers. Two questions follow
immediately: *what is the true value?* (the location `mu`) and *how noisy is the
measurement?* (the scale `sigma`). Project 02 estimates both at once and, in doing so,
teaches the first multi-parameter inference in the portfolio.

The reason this is more than "Project 01 with an extra parameter" is the **scale**.
A scale parameter is constrained to be positive and lives on a skewed geometry, and —
crucially — the naive "uninformative" prior for it is not innocent the way a flat prior
on a probability merely is. A flat prior on a probability (`Beta(1,1)`) is still a
proper distribution; a flat prior on a scale (`Uniform(0, inf)`) is **improper** — it
does not integrate to a finite number, it concentrates essentially all its mass on
enormous values, and it can produce an improper posterior that does not exist as a
probability distribution at all. Learning to put a *proper, weakly-informative* prior
on a scale is the single most important habit this project instills, and it recurs in
every later model that has a variance, a dispersion, or a hierarchical standard
deviation.

### The scenario

A concentration — say protein concentration in mg/mL — is measured `N = 30` times on
the same sample. Each replicate is the true concentration `mu` plus independent
Gaussian noise of unknown SD `sigma` (instrument and pipetting error). We want the
**joint posterior** for `(mu, sigma)`, so we can report both the concentration and how
reproducible a single future measurement will be.

### What is *new* in this project

- **Joint inference of a location and a scale**, with priors on both.
- **The scale-prior pitfall**: why a flat/improper prior on `sigma` is dangerous, and
  what proper alternatives (`HalfNormal`, `Exponential`, `HalfCauchy`) to use instead.
- **Per-parameter calibration**: running SBC separately on `mu` and `sigma`, because
  their failure modes differ.

Everything else — the eight steps, the prior predictive check, the diagnostics, the
decision framing — is the same machinery you learned in Project 01, now applied to a
two-parameter model.

---

## The eight-step workflow at a glance

| # | Step | Question it answers | Project 02 artifact |
|---|---|---|---|
| 1 | **Problem & data story** | What generated the data, and what do I assume? | `data/generate_data.py` |
| 2 | **Model spec + priors** | Likelihood? Priors on location *and* scale? | `model.py` |
| 3 | **Prior predictive checks** | Does my prior imply sane data spreads? | Notebook Step 3 |
| 4 | **Inference** | How do I compute the joint posterior? | `model.fit` (NUTS) |
| 5 | **Computational diagnostics** | Did the sampler work for *both* parameters? | R-hat / ESS / divergences |
| 6 | **Posterior predictive checks** | Does the model reproduce the spread? | `az.plot_ppc` + SD statistic |
| 7 | **Model criticism / comparison** | Is the joint posterior sane? Better model? | `az.plot_pair` |
| 8 | **Decision & communication** | What concentration *and* noise do I report? | `summary_onepager.md` |

The two cross-cutting principles from Project 01 still hold: **flag every assumption**
and **check before you trust**. To them this project adds a third: **treat scale
parameters with extra care** — their priors, their diagnostics, and their calibration
all deserve separate attention.

---

<a name="mathematical-background"></a>
## Mathematical background: the Normal location-scale model

### The likelihood

Each of `N` replicate measurements is Normally distributed around a common true value
with a common noise SD:

```
y_i ~ Normal(mu, sigma),   i = 1, ..., N.
```

The sufficient statistics are the sample mean (which informs `mu`) and the sample
standard deviation (which informs `sigma`). Two numbers in the data; two parameters in
the model.

### The priors

```
mu    ~ Normal(prior_mean, prior_sd)      # weakly-informative location
sigma ~ HalfNormal(sigma_scale)           # proper, positive scale prior
```

- **`mu ~ Normal(5, 10)`** — centred at a rough guess (5 mg/mL) but *broad*: two prior
  SDs span roughly `-15` to `25`, far wider than any plausible concentration. This is
  weakly-informative: it rules out the absurd without dictating the answer.
- **`sigma ~ HalfNormal(5)`** — the `HalfNormal` is a Normal folded at zero, so it lives
  on `(0, inf)` as a scale must, and it is **proper** (integrates to one). Its scale of
  5 concentrates mass on plausible noise levels (mostly below ~10) while still allowing
  larger values if the data demand them.

### Why not a flat prior on `sigma`?

Because a flat prior on a scale is improper. `Uniform(0, inf)` (or its finite stand-in
`Uniform(0, 1e6)`) places essentially all of its mass on enormous values — the interval
`[0, 10]` is one part in 100,000 of `[0, 1e6]`. It asserts a priori that a measurement
noise of half a million mg/mL is overwhelmingly more likely than 1 mg/mL. With ample
informative data the likelihood can sometimes rescue the fit; with scarce data it
cannot, and the posterior may fail to be a proper distribution at all. The portfolio's
rule, learned here: **always put a proper prior on a positive scale parameter.**

### No conjugacy shortcut (and why that's fine)

Unlike Project 01's Beta-Binomial, the joint `Normal(mu, sigma)` model with these
priors has no simple closed form, so we rely on NUTS. (There is a conjugate
Normal-Inverse-Gamma analysis, but it forces a specific prior we do not want.) This is
the realistic case — most models are not conjugate — and it is why the portfolio
standardizes on MCMC.

---

## Step 1 — Problem & data-generating story

> **Goal of this step:** encode how the measurements arose, with a known truth, and
> name every assumption.

`data/generate_data.py` encodes the DGP:

```python
MU_TRUE    = 5.0    # true concentration, mg/mL
SIGMA_TRUE = 1.2    # true measurement noise SD, mg/mL
N_OBS      = 30
SEED       = 20240602

def generate(seed=SEED, n=N_OBS, mu=MU_TRUE, sigma=SIGMA_TRUE) -> dict:
    rng = np.random.default_rng(seed)
    y = rng.normal(mu, sigma, size=n)
    return {"y": y, "n": int(n),
            "truth": {"mu": float(mu), "sigma": float(sigma)}}
```

Running it prints:

```
Synthesized 30 replicate measurements.
  empirical mean = 4.839, empirical sd = 1.389
  True mu = 5.000, true sigma = 1.200  (saved to data/data.npz)
```

Note the data are noisier than the truth: the empirical SD (1.389) overshoots the true
`sigma` (1.2) by ~16%, just from the luck of 30 draws. The posterior will track the
*data*, and the true value will sit inside its interval — that is correct behaviour,
not a bug. A method that recovered 1.2 exactly from data whose SD is 1.389 would be
ignoring the evidence it was given.

### The assumptions, stated explicitly

- **(A1) Independence.** Each measurement is independent of the others. *Violated if*
  consecutive readings share a slow drift or a common disturbance.
- **(A2) Homoscedasticity (constant `sigma`).** The noise SD is the same for every
  replicate — no growing variance, no changing precision. *Violated if* the instrument
  warms up and its noise shrinks over the run.
- **(A3) Gaussian, symmetric noise.** Errors are Normal — symmetric, light-tailed, no
  outliers. *Violated if* one pipetting blunder produces a gross outlier (which a
  Normal model will let drag both `mu` and `sigma`).

We revisit (A2) and (A3) at Step 6 and in the `rubric.md` extension (which breaks
homoscedasticity on purpose). Heavy-tailed violations of (A3) are the motivation for
the robust-regression projects later in the portfolio.

### What can go wrong at Step 1

- **No recoverable scale.** If the DGP does not record `sigma`, you cannot test scale
  recovery — and the scale is exactly the parameter this project is about. Always
  expose both `mu` and `sigma` in `truth`.
- **Confusing SD and variance in the DGP itself.** `np.random.normal` takes the SD; if
  you pass a variance you simulate the wrong data. Keep the SD/variance convention
  straight from the very first line (it returns as BUG 2 in the model).

---

## Step 2 — Model specification with justified priors

> **Goal of this step:** state the likelihood and *justify both priors* — and this is
> where the scale-prior pitfall lives.

`model.py`:

```python
def build_model(data, prior_mean=5.0, prior_sd=10.0, sigma_scale=5.0,
                sigma_prior="halfnormal"):
    y = np.asarray(data["y"])
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=prior_mean, sigma=prior_sd)
        sigma = pm.HalfNormal("sigma", sigma=sigma_scale)   # proper scale prior
        pm.Normal("y", mu=mu, sigma=sigma, observed=y)
    return model
```

(The `sigma_prior` switch selects `HalfNormal`/`Exponential`/`HalfCauchy` for the
prior-sensitivity study; the default is `HalfNormal`.)

### Justifying the location prior

`mu ~ Normal(5, 10)` is weakly-informative: centred at a plausible concentration but so
broad that the data dominate. We could centre it elsewhere; what matters is that it is
broad enough not to fight the likelihood and not so broad as to be improper. (A truly
flat prior on a *location* is improper too, but it is far more forgiving than a flat
prior on a scale, because the location likelihood is symmetric and well-behaved.)

### Justifying the scale prior — the heart of the project

`sigma ~ HalfNormal(5)` is **proper** and weakly-informative. Three things recommend it:

1. **Correct support.** `HalfNormal` lives on `(0, inf)`, exactly the domain of a scale.
2. **Properness.** It integrates to one, guaranteeing a proper posterior regardless of
   how little data we have.
3. **Sane concentration.** Its mass sits on plausible noise levels (mostly < 10) while
   still permitting larger `sigma` if the data insist.

Contrast the **flat/improper** alternative `Uniform(0, inf)`: improper, mass piled on
absurd values, no guarantee of a proper posterior. This is the seeded BUG 1 in the
broken notebook, and the prior predictive check (Step 3) makes its pathology visible.

`PRIOR_SENSITIVITY.md` shows that the *proper* alternatives (`HalfNormal`,
`Exponential`, `HalfCauchy`) all give nearly identical answers at `N = 30` — the choice
among them is minor. The choice that matters is **proper vs improper**.

### What can go wrong at Step 2

- **Improper scale prior** (BUG 1). The key pitfall. Cure: a proper prior + a prior
  predictive check.
- **Variance/SD confusion** (BUG 2). Passing `sigma**2` where `pm.Normal` wants the SD
  silently mis-scales the likelihood. Cure: know the API convention; check recovery.
- **A location prior that fights the data.** A tight, mis-centred `mu` prior biases the
  estimate at small `N`. Keep it broad unless you have real prior information.

---

## Step 3 — Prior predictive checks

> **Goal of this step:** simulate datasets from the prior and confirm their *spreads*
> are sane — the spread is where a bad scale prior betrays itself.

```python
with model:
    prior = pm.sample_prior_predictive(draws=500, random_seed=RNG)
# implied per-dataset means and spreads:
pp_means = prior.prior_predictive['y'].mean(dim=<observation axis>)
pp_sds   = prior.prior_predictive['y'].std(dim=<observation axis>)
```

We histogram the implied per-dataset means *and* SDs. Under `mu ~ N(5,10)` and
`sigma ~ HalfNormal(5)`:

- the implied **means** spread broadly around 5 (reflecting the broad location prior);
- the implied **SDs** sit mostly below ~10 (reflecting the proper scale prior).

This is the diagnostic that catches BUG 1. Swap in the improper `Uniform(0, 1e6)` scale
prior and the implied SDs span *many orders of magnitude* — datasets with spreads of
hundreds of thousands of mg/mL. No real assay produces that, so the prior predictive
check flags the improper prior immediately, *regardless of the observed data*. That
last point matters: the check works even when the data would otherwise rescue the fit,
which is precisely when the bug is most likely to slip through unnoticed.

### What can go wrong at Step 3

- **Skipping it.** Then an improper scale prior is only caught (if ever) when the
  posterior misbehaves — by which point prior, likelihood, and bug are entangled.
- **Only checking the mean.** The mean would look fine even with a broken scale prior;
  you must check the *spread*. Match the prior-predictive statistic to the parameter
  you are worried about.
- **Wrong reduction axis.** Same trap as everywhere: reduce over the observation axis,
  not `draw`. Print `.dims`.

---

## Step 4 — Inference (NUTS)

> **Goal of this step:** compute the joint posterior for `(mu, sigma)`.

```python
idata = fit(data, draws=1000, tune=1000, chains=4, seed=202)
```

The settings mirror Project 01: four chains for reliable split-R-hat, generous tuning,
a fixed seed, `log_likelihood=True` so LOO is available later, and prior + posterior
predictive attached to the same `InferenceData`.

### What is different now: a two-dimensional geometry

With two parameters the posterior is a surface, not a curve, and NUTS must explore both
dimensions together. The location dimension (`mu`) is easy — symmetric and Gaussian.
The scale dimension (`sigma`) is harder — positively constrained and right-skewed —
so NUTS typically achieves slightly lower ESS on `sigma` than on `mu`. That is normal
and benign here; it foreshadows the genuinely hard scale geometries (funnels) in the
hierarchical projects, where the scale and the sampler actively fight.

### What can go wrong at Step 4

- **An improper scale prior degrading mixing.** BUG 1 often shows up here as poor
  `sigma` ESS or a posterior tail that never settles.
- **Too little tuning / one chain.** Same failures as Project 01: unreliable
  diagnostics. Keep ≥2 chains and adequate `tune`.
- **Trusting the fit before reading diagnostics.** Especially tempting when `mu` looks
  right but `sigma` is quietly mis-mixed. Read Step 5 first.

---

## Step 5 — Computational diagnostics

> **Goal of this step:** confirm the sampler worked — for *both* parameters. Scale
> parameters are where diagnostics most often reveal trouble.

```python
print(az.summary(idata, var_names=['mu', 'sigma']))
n_div = int(idata.sample_stats['diverging'].sum())
az.plot_trace(idata, var_names=['mu', 'sigma'])
```

Read the same three things as Project 01, but now for two parameters:

- **R-hat** for both `mu` and `sigma` should be ≈ 1.00. A scale parameter with R-hat
  above 1.01 while the location is fine points straight at the scale prior or the scale
  geometry.
- **ESS (bulk and tail)** for both should be ≳ 400. Expect `sigma`'s ESS to run a bit
  below `mu`'s — that is the skewed scale geometry, not a bug, unless it falls far below
  400.
- **Divergences** should be 0. Divergences concentrated near small `sigma` are the
  classic signature of a scale that the sampler cannot navigate (a preview of the
  hierarchical funnel).

The standalone `python3 model.py` self-test prints, for the fixed dataset, R-hat ≈
1.00 for `mu` and ~1.00–1.01 for `sigma`, ESS in the hundreds-to-thousands, and 0
divergences — a clean report you can use as the known-good baseline.

### The trace plot, read for two parameters

Both `mu` and `sigma` panels should show well-mixed "fuzzy caterpillars" with the
chains overlapping. A common scale-specific pathology to watch for: one chain parked at
a systematically larger `sigma` than the others, which inflates R-hat and signals the
sampler is struggling with the scale's tail.

### What to do when diagnostics fail

| Symptom | Likely cause | First remedy |
|---|---|---|
| High R-hat on `sigma` only | Bad scale prior / hard scale geometry | Use a proper prior; raise `target_accept`; more tuning |
| Low `sigma` ESS | Skewed scale geometry | More draws; raise `target_accept` |
| Divergences near small `sigma` | High curvature at the scale boundary | Raise `target_accept`; reparameterize (non-centered, later projects) |
| Heavy, unsettled `sigma` tail | Improper/too-permissive scale prior | Switch to a proper, lighter-tailed prior |

For this project, a clean fit should hit none of these — the value of seeing a clean
report is that you will recognize a dirty one instantly in later projects.

---

## Step 6 — Posterior predictive checks

> **Goal of this step:** confirm the *model* reproduces the data — and for this project
> that specifically means reproducing the **spread**, not just the mean.

```python
az.plot_ppc(idata, num_pp_samples=100)
```

Then a numerical check tailored to the scale:

```python
pp = idata.posterior_predictive['y']
obs_dim = [d for d in pp.dims if d not in ('chain', 'draw')][0]
pp_sd = pp.std(dim=obs_dim).values.ravel()      # spread of each replicated dataset
obs_sd = y.std(ddof=1)
p_value = float(np.mean(pp_sd >= obs_sd))        # near 0.5 = good fit
```

The discrepancy statistic is the **dataset standard deviation**. We ask: across many
datasets simulated from the posterior, how often is the replicated SD at least as large
as the observed SD (1.389)? A Bayesian p-value near 0.5 means the model reproduces the
observed spread — the scale is well-fit. A value near 0 or 1 means the model
systematically under- or over-states the spread.

**Choosing the right statistic is the lesson.** A PPC on the *mean* would pass even if
the scale were badly modeled; only a PPC on the *spread* tests the scale. And note the
reduction axis: SD over the **observation** axis, not `draw` (that is BUG 3). A
predicted dataset SD should land near 1.4; anything wildly off flags the wrong axis.

### What a spread-PPC catches and misses

A spread-PPC catches a mis-fit scale. It does *not* catch **heteroscedasticity** (a SD
that changes across the run) or **outliers/heavy tails**, because a single global SD
statistic averages over them. To catch those you need a more targeted statistic — e.g.
the SD of the first half vs the second half (for heteroscedasticity), or the maximum
absolute residual (for outliers). The `rubric.md` extension uses exactly the
half-vs-half statistic to detect injected heteroscedasticity.

### What can go wrong at Step 6

- **Checking the mean instead of the spread.** Match the statistic to the parameter
  under suspicion. For a scale model, check the spread.
- **Wrong reduction axis** (BUG 3). Reduce over observations. Print `.dims`.
- **Concluding "Normal is fine" from one passing PPC.** A passing SD-PPC does not rule
  out heavy tails; check a tail-sensitive statistic if outliers are a concern.

---

## Step 7 — Model criticism & comparison

> **Goal of this step:** stress the joint model and ask whether a different model is
> warranted.

### Criticizing the joint posterior

We confirm the joint posterior for `(mu, sigma)` brackets the known truth `(5.0, 1.2)`
and inspect the joint distribution for structure:

```python
az.plot_pair(idata, var_names=['mu', 'sigma'], kind='kde', marginals=True)
```

For replicate measurements with a modest `N`, the `mu`-`sigma` posterior is close to
independent (the sample mean and sample SD are independent for a Normal). A strong
correlation would signal something off in the model or the data. Seeing approximate
independence here is itself a check: the model is behaving as the theory predicts.

### Why no LOO/WAIC yet

Model *comparison* needs ≥2 models, and this project has one. We store the pointwise
log-likelihood (`log_likelihood=True`) so the option exists. The natural second model —
introduced as the extension and built out in the robust-regression project — replaces
the Normal likelihood with a **Student-t**, which tolerates outliers. Then:

```python
az.compare({"normal": idata_normal, "student_t": idata_t})
```

would tell you, via LOO, whether the heavier-tailed model predicts held-out data
better. On clean Gaussian data (as here) LOO should find them indistinguishable —
correctly reporting "no evidence the extra robustness is needed".

### What can go wrong at Step 7

- **Forgetting `log_likelihood=True`.** Then LOO requires a refit.
- **Mistaking a clean PPC for proof of correctness.** Criticism (does it fit?) and
  comparison (is there a better model?) are distinct; do both when you have alternatives.
- **Over-reading mild `mu`-`sigma` correlation at small `N`.** Some dependence appears
  as `N` shrinks; it is not necessarily a defect.

---

## Step 8 — Decision & communication

> **Goal of this step:** report the concentration *and* the noise, each with its
> uncertainty, and explain why both matter.

```python
mu_post = idata.posterior['mu'].values.ravel()
sigma_post = idata.posterior['sigma'].values.ravel()
mu_lo, mu_hi = np.percentile(mu_post, [3, 97])
sig_lo, sig_hi = np.percentile(sigma_post, [3, 97])
```

For the fixed dataset this yields, approximately:

- **Concentration** `mu ≈ 4.85 mg/mL`, 94% CI ≈ `[4.4, 5.4]`.
- **Measurement noise** `sigma ≈ 1.45 mg/mL`, 94% CI ≈ `[1.1, 1.9]`.

### The communication that matters: average vs single measurement

The most important point to convey is the difference between two uncertainties:

- The **uncertainty in the average** (`mu`'s SD ≈ 0.27) is small, because 30 replicates
  average away most of the noise. Report the *concentration* with this.
- The **spread of a single measurement** (`sigma` ≈ 1.45) is much larger. A collaborator
  predicting one future reading should expect `4.85 ± 1.45`, not `4.85 ± 0.27`.

Conflating these is a classic error. The one-pager (`summary_onepager.md`) states both
explicitly and tells the collaborator which to use for which purpose.

### What can go wrong at Step 8

- **Reporting only `mu`.** The noise is half the answer; omitting `sigma` hides how
  reproducible the measurement is.
- **Using the average's uncertainty to predict a single measurement.** Use `sigma` for
  one-shot predictions, `mu`'s SD for the average.
- **Ignoring the assumptions.** If the noise was not constant (A2) or had outliers (A3),
  the reported `sigma` is an average that may mislead. Flag the caveat.

---

<a name="beyond-a-single-fit"></a>
## Beyond a single fit: SBC, prior sensitivity, and the broken notebook

### Simulation-Based Calibration — calibrate *both* parameters

`sbc.py` runs SBC over `(mu, sigma)`: draw both from their priors, simulate data, refit
with a tiny sampler, and record the rank of each true value among its posterior draws.
Over 35 simulations the ranks are uniform for both (`mu` chi-square p = 0.736, `sigma`
p = 0.534), so the procedure is calibrated. The point of running it on `sigma`
*separately* is that scale parameters are exactly where over- or under-confidence hides;
an improper or too-permissive scale prior would show up as a U- or n-shaped `sigma`
rank histogram even when `mu` looks perfect. Full detail in `SBC_REPORT.md`.

### Prior sensitivity — across proper scale priors

`prior_sensitivity.py` refits under `HalfNormal(5)`, `Exponential(1/5)`, and
`HalfCauchy(5)`. The `sigma` posterior mean moves by 0.004 and `mu` by 0.031 — the three
*proper* priors agree. The deliberate omission is the improper flat prior: it is not a
legitimate option to compare but the seeded *bug*. The lesson: the choice among proper
priors is minor; the choice between proper and improper is decisive. Detail in
`PRIOR_SENSITIVITY.md`.

### The broken notebook — three scale-flavoured bugs

`notebook_broken.ipynb` seeds three bugs; `BROKEN_BUGS.md` is the answer key:

- **BUG 1** — an improper flat `sigma` prior (`Uniform(0, 1e6)`). *Revealed by* the
  prior predictive check (implied spreads span orders of magnitude) and degraded `sigma`
  ESS.
- **BUG 2** — a **variance passed where a standard deviation is expected**
  (`pm.Normal(..., sigma=sigma**2)`). *Revealed by* a recovery check against the known
  `sigma = 1.2` and a spread-PPC mismatch.
- **BUG 3** — the posterior-predictive SD taken over the `draw` axis instead of the
  observation axis. *Revealed by* printing `.dims` and sanity-checking the predicted SD
  against the observed 1.39.

---

<a name="common-pitfalls"></a>
## Common pitfalls (tied to this project's key pitfall)

### 1. An improper/flat prior on a scale parameter (THE key pitfall)
`Uniform(0, inf)` on `sigma` is improper: unbounded mass on huge variances, no
guaranteed proper posterior. **Cure:** a proper prior (`HalfNormal`/`Exponential`/
`HalfCauchy`) plus a prior predictive check on the implied spread.

### 2. Confusing standard deviation with variance
`pm.Normal` takes the SD. Passing the variance (`sigma**2`) silently mis-scales the
likelihood and biases `sigma`. **Cure:** know the API convention; check recovery against
a known truth.

### 3. Checking the mean when you should check the spread
A mean-based prior- or posterior-predictive check passes even with a broken scale.
**Cure:** match the discrepancy statistic to the parameter — check the SD to test the
scale.

### 4. Reducing xarray over the wrong axis
PPC and prior-predictive arrays are `(chain, draw, observation)`. Reduce over the
observation axis. **Cure:** print `.dims`/`.shape`; a per-dataset SD should land near
the observed SD.

### 5. Reporting the average's uncertainty as if it were a single measurement's spread
`mu`'s SD (~0.27) and `sigma` (~1.45) answer different questions. **Cure:** report both;
use `sigma` for one-shot predictions, `mu`'s SD for the average.

### 6. Assuming robustness instead of demonstrating it
The proper scale priors agree only because `N = 30`. **Cure:** run prior sensitivity at
your actual `N`; at small `N` the heavy-tailed prior diverges from the light-tailed one.

### 7. Forgetting the assumptions
Homoscedasticity (A2) and Gaussianity (A3) underlie the single global `sigma`. Outliers
or changing noise make the reported `sigma` a misleading average. **Cure:** name the
assumptions at Step 1; test them with targeted PPCs at Step 6.

---

## How to run everything

All commands run **from the project directory** with `python3` (the only interpreter
with numpy/pymc here — never bare `python` or `pytest`).

```bash
python3 data/generate_data.py
python3 model.py
python3 build_notebook.py
python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb
python3 -m pytest test_recovery.py -q
python3 sbc.py
python3 prior_sensitivity.py
```

Then open `notebook.ipynb` and run it top to bottom. Dependencies are pinned by the
shared top-level `requirements.txt` / `environment.yml`.

---

## Glossary

- **Location parameter** — a parameter that shifts a distribution along its axis; here
  `mu`, the true concentration.
- **Scale parameter** — a positive parameter that controls spread; here `sigma`, the
  measurement noise SD.
- **Standard deviation vs variance** — the SD is the square root of the variance;
  `pm.Normal` is parameterized by the SD. Confusing the two is a common silent bug.
- **Proper vs improper prior** — a proper prior integrates to one; an improper one (e.g.
  `Uniform(0, inf)`) does not and can yield an improper posterior.
- **HalfNormal / Exponential / HalfCauchy** — proper distributions on `(0, inf)`, used
  as scale priors; they differ mainly in tail weight.
- **Homoscedasticity** — constant noise variance across observations (assumption A2).
- **Heteroscedasticity** — variance that changes across observations; the violation the
  extension injects.
- **Prior / posterior predictive distribution** — distributions of data implied by the
  prior / fitted posterior; used to check priors and fit.
- **NUTS, R-hat, ESS, divergence** — see Project 01's glossary; identical meanings here.
- **SBC** — simulation-based calibration; run here separately on `mu` and `sigma`.
- **Bayesian p-value** — posterior-predictive probability of a discrepancy statistic as
  extreme as observed; near 0.5 indicates good fit.

---

*Project 02 of the 20-project Bayesian-workflow teaching portfolio. The Normal
location-scale model is the bridge from a single proportion to regression: add a
predictor to `mu` and you have Project 04. The lesson that a scale parameter needs a
proper prior is load-bearing in every model with a variance, a dispersion, or a
hierarchical standard deviation that follows.*
