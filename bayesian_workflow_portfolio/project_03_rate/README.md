# Project 03 — Estimating a Rate (Poisson with exposure offset)

> **Counts per opportunity, done right.** The whole project hinges on one idea: when
> samples differ in *exposure*, you model the *rate*, not the raw count — and the way to
> do that is an **exposure offset**. Forget it and your rate is wrong by an order of
> magnitude, confidently.

This README is the **guideline** for Project 03. It walks all eight workflow steps,
flags every assumption, and ties everything to the project's key pitfall — **ignoring
the exposure/offset** — including a worked demonstration of the bias it causes. Read it
alongside the runnable artifacts:

| Artifact | What it is |
|---|---|
| `data/generate_data.py` | DGP with **varying exposures** and a known `log_rate`. |
| `model.py` | The Poisson offset model (log link), with a `use_offset` switch. |
| `notebook.ipynb` | The clean, runnable, end-to-end workflow. |
| `notebook_broken.ipynb` | The debugging exercise (offset omitted + two more bugs). |
| `sbc.py` / `SBC_REPORT.md` | Calibration of `log_rate`. |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | Robustness across `log_rate` priors. |
| `test_recovery.py` | Recovery test **plus** an asserted offset-bias demonstration. |
| `BROKEN_BUGS.md` | Instructor answer key. |
| `rubric.md` | Grading rubric tied to the eight steps. |
| `lessons.md` | The lessons report. |
| `summary_onepager.md` | The non-technical decision summary. |

---

## Table of contents

1. [Why this project exists](#why-this-project-exists)
2. [The eight-step workflow at a glance](#the-eight-step-workflow-at-a-glance)
3. [Mathematical background: the Poisson rate model with an offset](#mathematical-background)
4. [Step 1 — Problem & data-generating story](#step-1--problem--data-generating-story)
5. [Step 2 — Model specification with justified priors](#step-2--model-specification)
6. [Step 3 — Prior predictive checks](#step-3--prior-predictive-checks)
7. [Step 4 — Inference (NUTS)](#step-4--inference-nuts)
8. [Step 5 — Computational diagnostics](#step-5--computational-diagnostics)
9. [Step 6 — Posterior predictive checks](#step-6--posterior-predictive-checks)
10. [Step 7 — Model criticism: the offset matters](#step-7--model-criticism-the-offset-matters)
11. [Step 8 — Decision & communication](#step-8--decision--communication)
12. [Beyond a single fit](#beyond-a-single-fit)
13. [Common pitfalls](#common-pitfalls)
14. [How to run everything](#how-to-run-everything)
15. [Glossary](#glossary)

---

## Why this project exists

Counts are everywhere in genomics: reads per kilobase, variants per sample, events per
unit of time-at-risk. The naive instinct — average the counts and call it a rate — is
wrong whenever the samples differ in how much *opportunity* they had to accumulate
events. A sample sequenced to twice the depth will show twice the reads at the same
underlying rate; averaging the raw counts confounds the rate with the depth.

The fix is an **exposure offset**: model the expected count as `exposure * rate`, so
that the rate is the comparable, exposure-free quantity. This is the single most
important idea in count modeling, and it is also the most commonly botched. Project 03
makes the failure unmistakable by giving the data *widely varying exposures* and then,
in the broken notebook, omitting the offset — producing a rate that is wrong by a factor
of ~20, with no diagnostic complaining.

The project's second new idea is the **log link**. A rate must be positive, so we model
`log_rate` with a Normal prior and exponentiate. This keeps the rate positive, gives the
sampler a benign unconstrained geometry, and makes the prior sensible on the
multiplicative scale.

### The scenario

We have `N = 50` genomics samples. Each sample `i` has an exposure `e_i` (e.g.
sequencing depth in kb) drawn over a wide band `[5, 40]`, and an observed integer count
`y_i` of events. Events occur at a common rate `lambda` per unit exposure, so
`y_i ~ Poisson(e_i * lambda)`. We want the posterior for `lambda` (via `log_rate`), so
we can compare samples on a rate basis and predict counts for new samples.

### What is *new* in this project

- **Priors for a positive rate via a log link** (`log_rate ~ Normal`, `lambda = exp`).
- **The exposure offset** and a concrete demonstration of the bias from omitting it.
- A `test_recovery.py` that asserts both correct recovery *and* the offset-omission
  bias, encoding the pitfall as an automated check.

---

## The eight-step workflow at a glance

| # | Step | Question it answers | Project 03 artifact |
|---|---|---|---|
| 1 | **Problem & data story** | What generated the counts, and what do I assume? | `data/generate_data.py` |
| 2 | **Model spec + priors** | Likelihood? Log link? Exposure offset? | `model.py` |
| 3 | **Prior predictive checks** | Does my prior imply sane total counts? | Notebook Step 3 |
| 4 | **Inference** | How do I compute the posterior for `log_rate`? | `model.fit` (NUTS) |
| 5 | **Computational diagnostics** | Did the sampler work? | R-hat / ESS / divergences |
| 6 | **Posterior predictive checks** | Does the model reproduce counts across exposures? | `az.plot_ppc` |
| 7 | **Model criticism / comparison** | Does omitting the offset bias the rate? | offset vs no-offset |
| 8 | **Decision & communication** | What rate, and what count for a new sample? | `summary_onepager.md` |

The cross-cutting principles continue: **flag every assumption** and **check before you
trust**. This project sharpens a third: **a clean diagnostic report does not certify a
correct model** — the offset bug passes every computational check and is still wrong.

---

<a name="mathematical-background"></a>
## Mathematical background: the Poisson rate model with an offset

### The likelihood

Each count is Poisson with a mean equal to the sample's exposure times the common rate:

```
y_i ~ Poisson(mu_i),    mu_i = e_i * lambda,    i = 1, ..., N.
```

The Poisson is the canonical distribution for counts of independent events: its single
parameter is its mean (which also equals its variance — a property we will lean on when
discussing overdispersion). The exposure `e_i` enters multiplicatively because, for a
process at rate `lambda` per unit, twice the exposure means twice the expected events.

### The log link and the offset

A rate must be positive, so we parameterize it as `lambda = exp(log_rate)` and put the
prior on `log_rate`. Taking logs of the mean:

```
log(mu_i) = log(e_i) + log_rate.
```

The term `log(e_i)` is a **fixed offset** — a known quantity added to the linear
predictor, with no coefficient to estimate. This is the standard way exposure enters a
Poisson GLM. In PyMC we can write it either as `mu = exposure * exp(log_rate)` (as
`model.py` does) or as `mu = exp(log(exposure) + log_rate)`; the two are identical.

### The prior

```
log_rate ~ Normal(0, 2).
```

Centred at 0 (so `lambda ~ 1` a priori) and broad: two prior SDs span `log_rate` in
`[-4, 4]`, i.e. rates from `~0.018` to `~55`. This is weakly-informative on the
multiplicative scale — it rules out the absurd (rates of millions) without dictating the
answer. A flat prior placed *directly on the rate* would be the wrong move (it is
effectively improper and gives the sampler a skewed, bounded geometry); the log link
plus a Normal prior is the right parameterization.

### Why the offset is not optional

Suppose you omit it and fit `y_i ~ Poisson(lambda)`. The model must explain samples with
exposures from 7 to 40 — and hence expected counts differing ~6-fold — with a *single*
mean. The best it can do is set `lambda` to the average count per sample (~7 here),
which has nothing to do with the rate per unit exposure (~0.30). The result is a
confident estimate that is wrong by a factor of ~20. No prior fixes this; it is a
structural error.

---

## Step 1 — Problem & data-generating story

> **Goal of this step:** encode how the counts arose — crucially, with *varying
> exposures* — and name every assumption.

`data/generate_data.py`:

```python
LOG_RATE_TRUE = -1.2   # lambda_true = exp(-1.2) ~ 0.301 events/unit
N_SAMPLES     = 50
EXPOSURE_LOW, EXPOSURE_HIGH = 5.0, 40.0
SEED = 20240603

def generate(seed=SEED, n=N_SAMPLES, log_rate=LOG_RATE_TRUE) -> dict:
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(EXPOSURE_LOW, EXPOSURE_HIGH, size=n)  # VARYING exposures
    lam = np.exp(log_rate)
    y = rng.poisson(exposure * lam).astype(int)                 # mean = exposure * rate
    return {"y": y, "exposure": exposure, "n": int(n),
            "truth": {"log_rate": float(log_rate)}}
```

Running it prints:

```
Synthesized 50 samples with exposures in [6.7, 39.9].
  total events = 350, total exposure = 1100.7
  naive mean count per sample (IGNORES exposure) = 7.000
  exposure-adjusted rate (events/exposure)       = 0.318
  true rate lambda = exp(-1.2) = 0.301  -> the adjusted rate should match this
  true log_rate = -1.200  (saved to data/data.npz)
```

The script deliberately prints **two** summaries: the naive mean count per sample (7.0)
and the exposure-adjusted rate (0.318). They differ by a factor of ~22, and the adjusted
rate is the one that matches the true 0.301. That single contrast is the entire
motivation for the offset, surfaced before any modeling.

### Why exposures must vary

The whole pitfall only bites when exposures differ. We draw them uniformly over `[5,
40]` — an ~8-fold range — so that omitting the offset produces a large, obvious bias. If
all exposures were equal, the offset would be a constant that folds harmlessly into the
intercept, and you could get away with ignoring it. Real data rarely have equal
exposures, which is why the offset is the default, not an optional refinement.

### The assumptions, stated explicitly

- **(A1) Independence.** Events are independent (the Poisson assumption). *Violated if*
  events cluster (e.g. PCR duplicates inflating read counts).
- **(A2) A single common rate; no overdispersion.** Every sample shares one `lambda`,
  and the only variability is Poisson counting noise (variance = mean). *Violated if*
  samples are intrinsically more/less active than each other (overdispersion), which the
  Poisson cannot represent.
- **(A3) Exposures known exactly.** `e_i` is a known constant, not itself estimated or
  noisy. *Violated if* sequencing depth is measured with error.

We revisit (A2) in the `rubric.md` extension, which injects overdispersion to make the
Poisson fail a variance-based PPC — the motivation for the Negative-Binomial.

### What can go wrong at Step 1

- **Not recording exposures.** Then you cannot build the offset model at all. The DGP
  must return `exposure`.
- **Equal exposures by accident.** Hides the pitfall; the offset's importance becomes
  invisible. Vary them deliberately.
- **No recoverable `log_rate`.** Then you cannot test recovery or the bias demonstration.

---

## Step 2 — Model specification with justified priors

> **Goal of this step:** state the likelihood, the log link, and the offset — and
> justify each.

`model.py`:

```python
def build_model(data, prior_mean=0.0, prior_sd=2.0, use_offset=True):
    y = np.asarray(data["y"]); exposure = np.asarray(data["exposure"])
    with pm.Model() as model:
        log_rate = pm.Normal("log_rate", mu=prior_mean, sigma=prior_sd)
        rate = pm.math.exp(log_rate)
        mu = exposure * rate if use_offset else rate    # offset = correct
        pm.Poisson("y", mu=mu, observed=y)
    return model
```

The `use_offset` switch exists so the notebook and tests can fit the *wrong* model
on demand and exhibit the bias. The default and only correct setting is `True`.

### Justifying the log link

Modeling `log_rate` rather than `lambda` directly buys three things: (1) `lambda =
exp(log_rate)` is positive for any real `log_rate`, so the constraint is automatic; (2)
the posterior lives on an unconstrained, roughly-symmetric scale that NUTS samples
efficiently; (3) a Normal prior on `log_rate` is multiplicative on the rate, which is
the natural way to be uncertain about a rate (a factor of 2 up or down, not an additive
amount).

### Justifying the prior

`Normal(0, 2)` on `log_rate` is weakly-informative: centred at `lambda = 1`, broad
enough to cover rates from ~0.02 to ~55. It rules out the absurd while letting the data
decide. The prior predictive check (Step 3) confirms the implied total counts are wide
but finite.

### Justifying the offset

Covered in the background section: varying exposures force `mu_i = e_i * lambda`. This is
the structural heart of the model. Omitting it (BUG 1) is the project's key pitfall.

### What can go wrong at Step 2

- **Omitting the offset** (BUG 1). The key pitfall — a ~20x bias. Cure: `mu = exposure *
  rate`; verify with a count-vs-exposure plot and recovery.
- **A flat prior directly on the rate** (BUG 2). Abandons the log link and is effectively
  improper. Cure: Normal on `log_rate`, then `exp`.
- **A too-tight `log_rate` prior.** Fights the data at low counts. Keep it broad unless
  you have real prior rate information.

---

## Step 3 — Prior predictive checks

> **Goal of this step:** simulate counts from the prior (with the real exposures) and
> confirm the implied totals are sane.

```python
with model:
    prior = pm.sample_prior_predictive(draws=500, random_seed=RNG)
prior_tot = prior.prior_predictive['y'].sum(dim=<observation axis>)
# plotted on a log10 scale because counts span orders of magnitude
```

Under `Normal(0, 2)` on `log_rate`, the implied total counts span several orders of
magnitude — which is why the plot uses `log10(total + 1)`. The distribution should be
wide (reflecting genuine prior uncertainty about the rate) but **finite and not absurd**
(no implied totals of billions). If you had used the flat-on-the-rate prior of BUG 2,
the implied totals would balloon to absurd magnitudes — the visual tell of a bad rate
prior.

Count models almost always need a **log display scale** for both priors and data; a raw
histogram of count totals spanning `[1, 100000]` is unreadable. Internalizing that is a
small but recurring lesson.

### What can go wrong at Step 3

- **Skipping it.** A bad rate prior is then only caught when the posterior misbehaves.
- **Plotting on a linear scale.** Counts spanning orders of magnitude are unreadable
  linearly; use `log10`.
- **Wrong reduction axis.** Sum over observations, not `draw`. Print `.dims`.

---

## Step 4 — Inference (NUTS)

> **Goal of this step:** compute the posterior for `log_rate`.

```python
idata = fit(data, draws=1000, tune=1000, chains=4, seed=303)
```

Standard settings: four chains for reliable split-R-hat, generous tuning, fixed seed,
`log_likelihood=True` for later LOO, prior + posterior predictive attached.

### A benign geometry, thanks to the log link

Because `log_rate` is a single unconstrained parameter, the posterior is smooth and
roughly symmetric, and NUTS mixes easily — expect R-hat = 1.00 and ESS in the hundreds
to low thousands with no divergences. Contrast this with a prior placed directly on the
bounded, skewed rate (BUG 2), which gives the sampler a harder time. The log link is as
much a *computational* convenience as a modeling one.

### What can go wrong at Step 4

- **A flat-on-the-rate prior degrading geometry** (BUG 2): poorer mixing on the bounded
  rate scale.
- **Too little tuning / one chain:** unreliable diagnostics, as in every project.
- **Trusting a clean fit of the wrong (no-offset) model.** The sampler converges
  beautifully on the biased model — convergence is not correctness. Proceed to Steps 6
  and 7.

---

## Step 5 — Computational diagnostics

> **Goal of this step:** confirm the sampler worked. For this model it will — which is
> exactly why diagnostics alone cannot catch the offset bug.

```python
print(az.summary(idata, var_names=['log_rate']))
print('divergences:', int(idata.sample_stats['diverging'].sum()))
az.plot_trace(idata, var_names=['log_rate'])
```

Expect R-hat = 1.00, ESS in the hundreds to thousands, and 0 divergences. The trace
should be a clean, well-mixed caterpillar. The standalone `python3 model.py` self-test
prints exactly this for the correct model.

### The critical caveat: diagnostics do not see the offset bug

Run the *same diagnostics* on the no-offset model and they look just as clean — R-hat =
1.00, healthy ESS, 0 divergences — while the estimate is wrong by ~20x. This is the most
important lesson of the project, sharper than in any earlier one: **computational
diagnostics certify that the sampler explored the posterior correctly; they say nothing
about whether the model is the right one.** A confidently-converged wrong model is the
most dangerous outcome in applied Bayes, and the only defenses are predictive checks
(Step 6) and explicit model criticism (Step 7).

### What to do when diagnostics fail

| Symptom | Likely cause | First remedy |
|---|---|---|
| High R-hat | Chains not converged | More draws; inspect trace |
| Low ESS | Autocorrelation (often a bounded-rate prior) | Use the log link; more draws |
| Divergences | Hard geometry (rare with the log link) | Raise `target_accept` |
| Clean diagnostics, absurd rate | **Structural error (omitted offset)** | Not a sampler fix — check the model (Steps 6-7) |

That last row is the one to remember: a clean report plus an implausible estimate points
at the *model*, not the sampler.

---

## Step 6 — Posterior predictive checks

> **Goal of this step:** confirm the model reproduces the counts — and specifically that
> it reproduces them *across the exposure range*, which is where the offset earns its
> keep.

```python
az.plot_ppc(idata, num_pp_samples=100)
```

then a numerical check on the total count:

```python
pp = idata.posterior_predictive['y']
obs_dim = [d for d in pp.dims if d not in ('chain', 'draw')][0]
pp_tot = pp.sum(dim=obs_dim).values.ravel()
p_value = float(np.mean(pp_tot >= y.sum()))      # near 0.5 = good fit
```

For the correct (offset) model, the observed total (350) sits squarely inside the
posterior-predictive distribution of totals, giving a Bayesian p-value near 0.5. More
importantly, because the model multiplies the rate by each exposure, its replicates
reproduce the *exposure-count relationship*: high-exposure samples get high predicted
counts, low-exposure samples get low ones.

### How a PPC exposes the offset bug

The no-offset model predicts the **same** count distribution for every sample regardless
of exposure. So its replicates badly miss both ends: it over-predicts low-exposure
samples and under-predicts high-exposure ones. A PPC *stratified by exposure* (predicted
vs observed count, plotted against exposure) makes this glaring — the no-offset model's
predictions are flat across exposure while the data trend upward. This is the predictive
counterpart to the recovery failure, and it is the kind of check that catches structural
errors diagnostics miss.

### What a PPC catches and misses here

A total-count PPC catches gross mis-fit. It does **not** catch **overdispersion** —
extra sample-to-sample variance the Poisson cannot represent — because the total can
match even when the per-sample spread is too large. To catch overdispersion you need a
PPC on the count *variance* or a dispersion statistic, which is exactly the `rubric.md`
extension. Match the statistic to the failure mode you care about.

### What can go wrong at Step 6

- **Checking only the total.** A matching total can hide both the exposure trend and
  overdispersion. Stratify by exposure; check a dispersion statistic.
- **Wrong reduction axis** (BUG 3). Sum over observations, not `draw`. Print `.dims`.
- **Declaring victory from a clean overall PPC.** Always check the exposure-stratified
  behaviour, which is the whole point of the offset.

---

## Step 7 — Model criticism: the offset matters

> **Goal of this step:** the criticism *is* the lesson here. We fit the wrong (no-offset)
> model and compare it to the correct one, quantifying the bias.

```python
idata_no_offset = fit(data, use_offset=False, ...)
# correct  log_rate mean ~ -1.14   (rate ~ 0.32, true ~ 0.30)
# no-offset log_rate mean ~  1.94   (rate ~ 7.0  = mean count per sample)
# true     log_rate       = -1.20
```

The contrast is stark and interpretable:

- The **correct** model recovers `log_rate ~ -1.14`, a rate of ~0.32, close to the true
  0.30 (the data ran slightly hot; the posterior follows the data, and the 94% interval
  covers the truth).
- The **no-offset** model lands on `log_rate ~ 1.94`, a rate of ~7.0 — which is exactly
  `log(mean count per sample)`. Denied the exposure, the model collapses the rate onto
  the average count, an error of more than an order of magnitude.

`test_recovery.py` encodes both facts as automated assertions: the offset model's 94%
interval **covers** the truth, and the no-offset model's interval **does not**. The
pitfall is thus a tested invariant, not just a narrative.

### Why no LOO is needed to see this

The bias is so large that LOO is overkill — the recovery check alone settles it. But for
completeness, both fits store `log_likelihood`, so `az.compare({"offset": idata,
"no_offset": idata_no_offset})` would rank the offset model far ahead. LOO becomes the
*necessary* tool when models differ subtly (e.g. Poisson vs Negative-Binomial), where
eyeballing the estimate is not enough. That is the natural next comparison and the
extension's subject.

### What can go wrong at Step 7

- **Skipping the comparison.** Without fitting the wrong model you never *see* the bias;
  the offset's importance stays abstract.
- **Confusing the no-offset rate (~7) for a plausible answer.** It looks like a rate but
  is a mean count. Sanity-check against the exposure-adjusted estimate (~0.30).
- **Reaching for LOO when recovery already answers the question.** Use the simplest check
  that settles the matter.

---

## Step 8 — Decision & communication

> **Goal of this step:** report the rate per unit exposure, with an interval, and
> translate it into a predicted count for a stated exposure.

```python
rate_post = np.exp(idata.posterior['log_rate'].values.ravel())
lo, hi = np.percentile(rate_post, [3, 97])
exp_count = rate_post.mean() * 20.0      # expected count at exposure 20
```

For the fixed dataset:

- **Rate** `lambda ~ 0.30` events per unit exposure, 94% CI ~ `[0.27, 0.36]`.
- **Predicted count at exposure 20** ~ 6 events.

### The communication that matters: rate, not raw count

The key message to a collaborator is that **raw counts are not comparable across samples
of different exposure** — they mostly reflect exposure. Always report and compare the
*rate per unit exposure*, and derive predicted counts as `rate * exposure`. The one-pager
(`summary_onepager.md`) leads with this, and notes that a naive count-average would have
reported ~7 (meaningless) instead of 0.30.

### What can go wrong at Step 8

- **Reporting or comparing raw counts.** They confound rate with exposure. Report the
  rate.
- **Forgetting to multiply by exposure when predicting.** A new sample's expected count
  is `rate * its exposure`, not the rate itself.
- **Ignoring the assumptions.** If overdispersion is present (A2 violated), the stated
  interval is too narrow. Flag it.

---

<a name="beyond-a-single-fit"></a>
## Beyond a single fit: SBC, prior sensitivity, and the broken notebook

### Simulation-Based Calibration

`sbc.py` runs SBC on `log_rate` *with the offset and varying exposures engaged*: draw
`log_rate*` from the prior, simulate counts with varying exposures, refit the offset
model, and rank the truth among the posterior draws. Over 40 simulations the ranks are
uniform (chi-square p = 0.690), confirming the offset+log-link parameterization is
correctly implemented. Tellingly, the *no-offset* model would **fail** SBC — its bias
shows up as a sloped rank histogram — so SBC is itself a check on the structural choice.
Detail in `SBC_REPORT.md`.

### Prior sensitivity

`prior_sensitivity.py` refits under `Normal(0,5)`, `Normal(0,2)`, and `Normal(-1,1)` on
`log_rate`. The posterior mean is identical to four decimals (max difference 0.0000):
with 350 total events the data swamp the prior. The lesson, and the warning: prior
robustness says nothing about *model* correctness — the offset is the danger, not the
prior. Detail in `PRIOR_SENSITIVITY.md`.

### The broken notebook

`notebook_broken.ipynb` seeds three bugs; `BROKEN_BUGS.md` is the answer key:

- **BUG 1 (headline)** — the **exposure offset is omitted**, biasing the rate ~20x.
  *Revealed by* the count-vs-exposure trend, an exposure-stratified PPC, and the recovery
  check.
- **BUG 2** — a flat prior placed directly on the rate (`Uniform(0, 1e4)`), abandoning
  the log link. *Revealed by* a prior predictive check with absurd implied totals.
- **BUG 3** — the total count summed over the `draw` axis instead of the observation
  axis. *Revealed by* printing `.dims` and checking the total against the observed 350.

---

<a name="common-pitfalls"></a>
## Common pitfalls (tied to this project's key pitfall)

### 1. Ignoring the exposure offset (THE key pitfall)
With varying exposures, omitting `mu_i = e_i * lambda` collapses the rate onto the mean
count — a ~20x structural error that diagnostics will not flag. **Cure:** always include
the offset; verify with a count-vs-exposure plot and recovery against a known truth.

### 2. Putting a prior directly on the rate (no log link)
A flat prior on a positive rate is effectively improper and gives a skewed, bounded
geometry. **Cure:** model `log_rate` with a Normal prior and exponentiate.

### 3. Trusting clean diagnostics as proof of correctness
The no-offset model converges perfectly and is still wrong. **Cure:** posterior
predictive checks and explicit model criticism, not R-hat/ESS alone.

### 4. Comparing or reporting raw counts across unequal exposures
Raw counts reflect exposure as much as rate. **Cure:** report the rate per unit exposure;
derive counts as `rate * exposure`.

### 5. Reducing xarray over the wrong axis
Sum over the observation axis, not `draw`. **Cure:** print `.dims`; a per-dataset total
should be near the observed total.

### 6. Forcing the Poisson on overdispersed data
The Poisson assumes variance = mean. Real counts are often overdispersed. **Cure:** a
variance/dispersion PPC to detect it; a Negative-Binomial to fix it (the extension).

### 7. Assuming prior robustness implies model correctness
A robust prior on a mis-specified model still gives a confidently wrong answer. **Cure:**
keep model criticism (Steps 6-7) separate from prior sensitivity.

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

- **Poisson distribution** — the canonical distribution for counts of independent events;
  its mean equals its variance.
- **Rate (`lambda`)** — the expected number of events per unit exposure.
- **Exposure (`e_i`)** — the amount of opportunity a sample had to accumulate events
  (sequencing depth, time-at-risk, library size).
- **Offset** — a known quantity added to the linear predictor with no fitted coefficient;
  here `log(exposure)`, encoding that expected count scales with exposure.
- **Log link** — modeling `log(mean)` linearly so the mean is positive; here
  `lambda = exp(log_rate)`.
- **Overdispersion** — count variance exceeding the mean, which the Poisson cannot
  represent; the motivation for the Negative-Binomial.
- **Structural mis-specification** — using the wrong model form (e.g. omitting the
  offset); produces confidently wrong answers that convergence diagnostics do not catch.
- **NUTS, R-hat, ESS, divergence** — see Project 01's glossary; identical meanings here.
- **SBC** — simulation-based calibration; here run on `log_rate` with the offset engaged.
- **LOO** — leave-one-out cross-validation for model comparison; the tool for subtle
  comparisons like Poisson vs Negative-Binomial.
- **Bayesian p-value** — posterior-predictive probability of a discrepancy statistic as
  extreme as observed; near 0.5 indicates good fit.

---

*Project 03 of the 20-project Bayesian-workflow teaching portfolio. The Poisson offset
model is the count-data workhorse: add covariates to `log_rate` for Poisson regression,
allow overdispersion for the Negative-Binomial — and keep the exposure offset throughout.
The lesson that structural errors produce confidently wrong, diagnostically-clean answers
is the sharpest in the portfolio so far.*
