# Project 01 — Estimating a Proportion (Beta–Binomial)

> **The "hello world" of the Bayesian workflow.** A single parameter, a closed-form
> answer, and nowhere for a mistake to hide. We use the simplest possible inference
> problem to walk the *entire* eight-step Bayesian workflow once, end to end, so that
> every later project in the portfolio reuses a process you already trust.

This README is the **guideline** for Project 01. It is long on purpose: it is the
"~50-page" teaching deliverable. It walks all eight workflow steps in detail, flags
every modeling assumption explicitly, ties everything back to the project's key
pitfall ("flat is not uninformative"), and tells you what to do when each step
*fails*. Read it alongside the runnable artifacts:

| Artifact | What it is |
|---|---|
| `data/generate_data.py` | The data-generating process (DGP) with a known truth. |
| `model.py` | The Beta–Bernoulli model, decoupled from the notebook. |
| `notebook.ipynb` | The clean, runnable, end-to-end workflow. |
| `notebook_broken.ipynb` | The debugging exercise (three seeded bugs). |
| `sbc.py` / `SBC_REPORT.md` | Simulation-based calibration of the procedure. |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | Robustness to prior choice. |
| `test_recovery.py` | A fast pytest that inference recovers the known truth. |
| `BROKEN_BUGS.md` | Instructor answer key for the broken notebook. |
| `rubric.md` | Grading rubric tied to the eight steps. |
| `lessons.md` | The lessons report: takeaways, surprises, generalization. |
| `summary_onepager.md` | The non-technical decision summary. |

---

## Table of contents

1. [Why this project exists](#why-this-project-exists)
2. [The eight-step workflow at a glance](#the-eight-step-workflow-at-a-glance)
3. [Mathematical background: the Beta–Binomial model](#mathematical-background-the-betabinomial-model)
4. [Step 1 — Problem & data-generating story](#step-1--problem--data-generating-story)
5. [Step 2 — Model specification with justified priors](#step-2--model-specification-with-justified-priors)
6. [Step 3 — Prior predictive checks](#step-3--prior-predictive-checks)
7. [Step 4 — Inference (NUTS)](#step-4--inference-nuts)
8. [Step 5 — Computational diagnostics](#step-5--computational-diagnostics)
9. [Step 6 — Posterior predictive checks](#step-6--posterior-predictive-checks)
10. [Step 7 — Model criticism & comparison](#step-7--model-criticism--comparison)
11. [Step 8 — Decision & communication](#step-8--decision--communication)
12. [Beyond a single fit: SBC, prior sensitivity, and the broken notebook](#beyond-a-single-fit)
13. [Common pitfalls (tied to this project's key pitfall)](#common-pitfalls)
14. [How to run everything](#how-to-run-everything)
15. [Glossary](#glossary)

---

## Why this project exists

Most people meet Bayesian inference as a *formula* — Bayes' theorem — and then a
*tool* — a sampler like Stan or PyMC. Neither teaches the thing that actually
matters in practice: the **workflow**. Real Bayesian modeling is a loop of
specifying a model, checking that it is sane *before* seeing data, fitting it,
checking that the fit *computed* correctly, checking that the model *describes* the
data, criticizing and possibly revising it, and finally turning the posterior into
a decision someone can act on.

That loop is identical whether you are estimating a single proportion or a
forty-parameter hierarchical model. The trouble is that on a hard model you cannot
tell whether a surprising result is a bug, a bad prior, a sampler failure, or a
genuine finding — too many things can go wrong at once. So we learn the loop here,
on the **easiest possible problem**, where:

- there is exactly **one** parameter, so plots are trivial to read;
- the posterior has a **closed form**, so we always have an exact oracle to check
  the sampler against;
- the data are **synthetic with a known true value**, so "did we recover the
  truth?" is a question with a definite answer.

Once you have run the eight steps where nothing can hide, the later projects become
a matter of *new likelihoods and new geometry* rather than *new process*. That is
the entire pedagogical bet of this portfolio, and Project 01 is where the bet is
placed.

### The scenario

A biochemical binary assay is run many times. Each run independently "succeeds"
(a substrate is cleaved, a well turns positive, a binding event is detected) with
an unknown true probability `theta`. We observe a sequence of 0/1 outcomes and want
the **full posterior distribution** for `theta` — not merely a point estimate, but
a quantified statement of how uncertain we are, so that downstream decisions
("is the rate above one-half?") carry their uncertainty with them.

### What is *new* in this project

Every project in the portfolio introduces one new skill. Here the new skill is
**the workflow itself** — there is no prior project to build on. The specific
modeling idea introduced is the **conjugate Beta–Binomial pair** and, with it, the
distinction between a *flat* prior and an *uninformative* one. That distinction is
the project's key pitfall, and it recurs (in more dangerous forms) in every later
project.

---

## The eight-step workflow at a glance

The portfolio standardizes on eight steps. Memorize them; they are the spine of
every project.

| # | Step | Question it answers | Project 01 artifact |
|---|---|---|---|
| 1 | **Problem & data story** | What generated the data, and what do I assume? | `data/generate_data.py` |
| 2 | **Model spec + priors** | What is my likelihood, and what priors are justified? | `model.py` |
| 3 | **Prior predictive checks** | Does my prior imply sane *data*, before I look? | Notebook Step 3 |
| 4 | **Inference** | How do I actually compute the posterior? | `model.fit` (NUTS) |
| 5 | **Computational diagnostics** | Did the *sampler* work? | R-hat / ESS / divergences |
| 6 | **Posterior predictive checks** | Does the fitted model *describe* the data? | `az.plot_ppc` |
| 7 | **Model criticism / comparison** | Is there a better model? Is this one wrong? | Analytic overlay |
| 8 | **Decision & communication** | What do I tell a collaborator to *do*? | `summary_onepager.md` |

Two principles cut across all eight:

- **Flag every assumption explicitly.** A model is a set of assumptions. The only
  way to know which one broke when something goes wrong is to have written them down.
- **Check before you trust.** Each step has its own failure mode and its own check.
  A posterior you have not checked is a number you should not report.

Beyond the eight steps, three *meta-checks* test the procedure rather than any
single fit: **simulation-based calibration** (is the inference procedure correct?),
**prior sensitivity** (does the answer depend on the prior?), and the **broken
notebook** (can you diagnose seeded failures?). They are covered after the eight
steps.

---

## Mathematical background: the Beta–Binomial model

### The likelihood

Each of `n` assay runs is an independent Bernoulli trial with success probability
`theta`:

```
y_i ~ Bernoulli(theta),   i = 1, ..., n,   y_i in {0, 1}.
```

Because the runs are independent and identically distributed, the total number of
successes `k = sum_i y_i` is a sufficient statistic and follows a Binomial:

```
k ~ Binomial(n, theta).
```

We can model either the individual `y_i` (as `model.py` does, for pedagogy) or the
aggregate `k`; the posterior for `theta` is identical because `k` carries all the
information about `theta` that the individual outcomes do.

### The prior

We place a Beta prior on `theta`:

```
theta ~ Beta(a, b),   a > 0, b > 0,   theta in (0, 1).
```

The Beta distribution lives on the unit interval — exactly the support of a
probability — which is why it is the natural prior for a proportion. Its mean is
`a / (a + b)` and its "concentration" is `a + b`: larger `a + b` means a tighter
prior. The shape parameters have an intuitive reading as *pseudo-counts*: `Beta(a, b)`
behaves like having already seen `a - 1` prior successes and `b - 1` prior failures.

### Conjugacy: the exact posterior

The Beta is the **conjugate prior** for the Bernoulli/Binomial likelihood, meaning
the posterior is again a Beta:

```
theta | k, n  ~  Beta(a + k, b + n - k).
```

This is one of the rare cases where Bayes' theorem has a closed-form answer. It is a
gift, and we exploit it relentlessly:

- as an **oracle** to confirm the MCMC sampler is producing the right posterior
  (Step 7);
- to make **SBC essentially free** — no MCMC needed, so calibration is tested in
  seconds (`sbc.py`);
- to make **prior sensitivity exact** — we read posterior means and intervals
  straight off the Beta quantile function with zero sampling noise
  (`prior_sensitivity.py`).

The conjugate posterior mean is a precision-weighted average of the prior mean and
the data:

```
E[theta | k, n] = (a + k) / (a + b + n).
```

As `n` grows, the `k/n` term dominates and the prior is outvoted — which is exactly
why prior choice barely matters at `n = 80` but matters a great deal at `n = 4`.

---

## Step 1 — Problem & data-generating story

> **Goal of this step:** write down, in code, exactly how you believe the data came
> to be — and make every assumption explicit so you can later check each one.

### The data-generating process

`data/generate_data.py` encodes the DGP. The relevant lines:

```python
THETA_TRUE = 0.62   # the known success probability we will try to recover
N_TRIALS   = 80     # number of independent assay runs
SEED       = 20240601

def generate(seed=SEED, n=N_TRIALS, theta=THETA_TRUE) -> dict:
    rng = np.random.default_rng(seed)
    y = rng.binomial(1, theta, size=n).astype(int)
    return {"y": y, "k": int(y.sum()), "n": int(n),
            "truth": {"theta": float(theta)}}
```

Three design choices deserve comment:

1. **A known truth.** We *choose* `theta_true = 0.62` and simulate from it. This is
   the single most valuable feature of a teaching project: because we know the
   answer, "did inference recover it?" is a question with a definite yes/no. Real
   data never offer this. `test_recovery.py` turns this into an automated assertion.

2. **A fixed seed.** Every random draw flows through `np.random.default_rng(seed)`.
   Re-running the script reproduces the *exact* same dataset (`k = 47` successes of
   `n = 80`). Reproducibility is non-negotiable in this portfolio: a result you
   cannot reproduce is a result you cannot debug.

3. **An importable function returning a `truth` dict.** Every consumer — the
   notebook, the test, SBC, prior sensitivity — imports `generate()` and reads
   `data["truth"]`. There is exactly one source of truth for the truth.

Running the script prints:

```
Synthesized 80 assay runs; observed 47 successes (empirical rate 0.588).
True theta = 0.620  (saved to data/data.npz)
```

Note already that the *empirical* rate (0.588) is not the true rate (0.620): with
80 runs, sampling noise alone moves the observed proportion by a few points. A
point estimate of 0.588 would be "right" in some loose sense, but it hides the
uncertainty. The whole reason we go Bayesian is to quantify exactly how far from
0.588 the truth could plausibly be.

### The assumptions, stated explicitly

A model is only as trustworthy as its assumptions are visible. This DGP — and the
model we will fit to match it — makes three:

- **(A1) Independence.** Each run's outcome is independent of the others. *Violated
  if*, e.g., a contaminated reagent makes a whole batch of runs fail together.
- **(A2) Constant `theta`.** The success probability is the same for every run — no
  drift over time, no operator effect, no batch-to-batch variation. *Violated if*
  the assay degrades as a plate ages.
- **(A3) Truly binary outcomes.** Each run is unambiguously a success or a failure —
  no partial successes, no missing/uncertain reads. *Violated if* borderline wells
  are scored inconsistently.

We will return to (A1)–(A3) at Step 6 (posterior predictive checks) and again in the
`rubric.md` extension prompt, which deliberately breaks (A2) with batch effects to
show how the simple model fails. For now, flagging them is enough — you cannot check
an assumption you have not named.

### What can go wrong at Step 1

- **Silent non-reproducibility.** Using a global RNG (`np.random.seed`) or no seed at
  all makes the dataset drift between runs, so a bug looks intermittent. *Fix:* one
  explicit `Generator` seeded once.
- **No recoverable truth.** If the DGP does not record the parameters it used, you
  cannot write a recovery test, and you lose the project's main safety net. *Fix:*
  always return a `truth` dict.
- **Mismatched DGP and model.** If you simulate from a process your model cannot
  represent, recovery will fail for a *good* reason — but it is easy to mistake that
  for a sampler bug. Keep DGP and model in deliberate correspondence here; mismatch
  is a tool we introduce later, on purpose.

---

## Step 2 — Model specification with justified priors

> **Goal of this step:** state the likelihood and the prior, and *justify* the prior
> rather than reaching for a default. This is where the project's key pitfall lives.

`model.py` builds the model:

```python
def build_model(data, a=2.0, b=2.0) -> pm.Model:
    y = np.asarray(data["y"])
    with pm.Model() as model:
        theta = pm.Beta("theta", alpha=a, beta=b)
        pm.Bernoulli("y", p=theta, observed=y)
    return model
```

The likelihood (`Bernoulli`) is dictated by the data story: binary outcomes, common
success probability. There is no real choice there. The *prior* is where judgment
enters — and where beginners most often go wrong.

### Why `Beta(2, 2)` and not `Beta(1, 1)`?

The instinct is to choose a "flat" prior, `Beta(1, 1)`, which is uniform on `theta`,
on the grounds that it represents "no opinion". **This instinct is wrong, and
unlearning it is the single most transferable lesson in the project.**

Uniform-on-the-probability is not the absence of an assumption; it is a *strong*
assumption. It says that `theta = 0.999` is *exactly as plausible a priori* as
`theta = 0.5`. For a biochemical assay, an almost-never-succeeds or
almost-always-succeeds rate is an extraordinary state of the world. A prior that
treats those edge rates as ordinary will, when data are scarce, cheerfully report a
posterior mean near 0 or 1 from a couple of lucky runs.

`Beta(2, 2)` is the weakly-informative alternative:

- it is **unimodal and centred at 0.5**;
- it pulls **gently away from the 0/1 edges** (its density is zero at both ends);
- it encodes the boring-but-true fact that assay rates are usually somewhere in the
  middle, without committing to any particular value.

It is *weakly* informative: it nudges, it does not dictate. With `n = 80` the data
swamp it entirely (the prior sensitivity analysis shows the choice changes the
posterior mean by 0.003). So why insist on it? Because **the habit costs nothing
when data are plentiful and saves you when they are scarce** — and because the same
distinction, applied to a variance (Project 02), a slope (Project 04), or a
hierarchical scale (the hierarchical projects), is the difference between inference
that works and inference that diverges.

### The pseudo-count intuition

`Beta(a, b)` acts like `a - 1` prior successes and `b - 1` prior failures:

- `Beta(1, 1)` = 0 prior successes, 0 prior failures = "flat" = uniform.
- `Beta(2, 2)` = 1 prior success, 1 prior failure = "I have seen one of each, so I
  lean mildly toward the middle and away from 0/1."
- `Beta(0.5, 0.5)` (Jeffreys) = *negative* pseudo-counts = U-shaped, piling mass at
  the edges (a reference prior with desirable invariance properties, but visually
  the opposite of "centrist").

Reading priors as pseudo-counts makes their strength concrete: a `Beta(2, 2)` prior
carries 2 pseudo-observations against the data's 80 — a ~40-to-1 disadvantage, which
is why it barely moves the posterior here.

### Decoupling the model from the notebook

Notice that the model lives in `model.py`, not inside the notebook. This is a
deliberate convention across the portfolio: the model is the single source of truth,
imported by the notebook, the recovery test, the SBC script, and the prior
sensitivity script alike. If the model were inlined in the notebook, every consumer
would re-implement it, and they would drift out of sync. One model, four consumers,
zero drift.

### What can go wrong at Step 2

- **Flat-as-uninformative (the key pitfall).** Covered above. The cure is a prior
  predictive check (Step 3), which makes the pathology *visible*.
- **A prior that excludes the truth.** If you put `Beta(20, 2)` (mean 0.91) on an
  assay whose true rate is 0.62, the prior fights the data. With enough data the data
  win, but the posterior is biased at small `n`. Always sanity-check that the prior's
  bulk covers values you would not be astonished by.
- **Improper priors on bounded parameters.** Not an issue for a proportion (the Beta
  is always proper), but a foreshadowing of Project 02, where an improper *flat*
  prior on a scale parameter genuinely breaks things.

---

## Step 3 — Prior predictive checks

> **Goal of this step:** before looking at the data, simulate *datasets* from the
> prior and ask whether they are plausible. A prior predictive check turns an
> abstract prior on a parameter into concrete, checkable predictions about data.

A prior on `theta` is hard to evaluate by staring at it. A prior on *the data it
implies* is easy. The prior predictive distribution is:

```
p(y_new) = integral  p(y_new | theta) p(theta) d theta,
```

i.e. "what datasets does my model expect before it has seen anything?" We sample it:

```python
with model:
    prior = pm.sample_prior_predictive(draws=1000, random_seed=RNG)
# implied number of successes per simulated dataset:
prior_k = prior.prior_predictive['y'].sum(dim=<observation axis>).values.ravel()
```

and histogram `prior_k`, the implied success count across 1000 prior-simulated
datasets.

### How to read it

Under `Beta(2, 2)`, the implied success count `k` spreads across the whole `0…n`
range with a **mild concentration toward the middle**. That is sensible: we are not
asserting any particular rate, but we are gently saying "all-successes and
all-failures are less expected than something in between".

Contrast with `Beta(1, 1)`: the implied `k` is **uniform** over `0…n`. The prior
asserts that "0 of 80 succeed" is exactly as expected as "40 of 80 succeed". For an
assay that is an implausible thing to believe, and the prior predictive check makes
the implausibility *visible* — which is precisely how you would catch the flat-prior
pitfall in practice. (This is BUG 1 of the broken notebook; the prior predictive
check is the diagnostic that reveals it.)

### Why this step matters more as models get harder

For a one-parameter model you could almost reason about the prior directly. The
power of prior predictive checks shows up when a model has many parameters whose
*joint* prior implies something absurd that no single marginal reveals — e.g. a
regression whose innocuous-looking priors on intercept and slope jointly predict
dose-responses that span 40 orders of magnitude (a real failure mode we meet in
Project 04). The discipline of "always simulate data from the prior first" is the
only practical guard once you can no longer reason about the prior in your head.

### What can go wrong at Step 3

- **Skipping it.** The most common error is to never do a prior predictive check.
  Then a bad prior is only discovered (if at all) when the posterior looks strange,
  by which point you cannot tell prior from likelihood from bug.
- **Reducing over the wrong axis.** `prior_predictive['y']` has a `(chain, draw,
  observation)` shape; to get a per-dataset `k` you sum over the **observation** axis.
  Summing over the wrong axis gives a meaningless histogram — the same class of error
  as BUG 3. The defensive habit: print `.dims` and `.shape` before reducing.
- **Over-tight implied predictions.** If the prior predictive `k` is concentrated in
  a narrow band, your prior is informative — fine if intended, a problem if you meant
  it to be weak. Check that the *spread* matches your actual prior knowledge.

---

## Step 4 — Inference (NUTS)

> **Goal of this step:** actually compute the posterior. Here we use Markov-chain
> Monte Carlo (specifically NUTS) even though a closed form exists, because learning
> the sampler on an easy problem pays off on the hard ones.

`model.fit` wraps the sampler:

```python
def fit(data, a=2.0, b=2.0, draws=1000, tune=1000, chains=4, seed=101, **kw):
    with build_model(data, a=a, b=b):
        idata = pm.sample(draws=draws, tune=tune, chains=chains,
                          random_seed=seed, progressbar=False,
                          idata_kwargs={"log_likelihood": True})
        idata.extend(pm.sample_prior_predictive(draws=500, random_seed=seed))
        idata.extend(pm.sample_posterior_predictive(idata, random_seed=seed))
    return idata
```

### Why MCMC at all, when we have the exact answer?

Pure pedagogy. The conjugate posterior `Beta(2 + k, 2 + n - k)` is exact and free.
But almost every interesting model is *not* conjugate, so the portfolio's standard
tool is MCMC. Project 01 is the ideal place to learn it because we can lay the
sampled posterior directly on top of the analytic one (Step 7) and *see* that the
sampler is right. You build trust in the tool where you can check it, then use the
tool where you cannot.

### What NUTS is, briefly

The No-U-Turn Sampler is an adaptive form of Hamiltonian Monte Carlo. It simulates
the trajectory of a particle on the (negative log) posterior surface, using
gradients to take long, informed steps that explore the distribution far more
efficiently than random-walk methods. "No-U-Turn" refers to its rule for
automatically choosing trajectory length: it keeps going until the path starts to
double back on itself. The two settings that matter most:

- **`tune`** — the number of warm-up iterations during which NUTS *adapts* its step
  size and mass matrix. These draws are discarded. Too few, and the sampler never
  learns the geometry (this is BUG 2 of the broken notebook).
- **`target_accept`** — the target acceptance probability (default 0.8). Raising it
  (e.g. 0.9–0.99) forces smaller steps, which clears divergences at the cost of
  speed. We do not need it here, but it is the first lever to reach for when
  divergences appear in later projects.

### Our settings, and why

```
draws=1000, tune=1000, chains=4, random_seed=101
```

- **`chains=4`.** Four independent chains, started from different points, let us
  compute split-R-hat reliably (it compares between-chain to within-chain variance,
  so it needs ≥2 chains; 4 is the comfortable default). Running one chain — as the
  broken notebook does — makes R-hat unreliable.
- **`tune=1000`.** Generous adaptation; NUTS converges its step size and mass matrix
  well within this budget for so simple a posterior.
- **`draws=1000`.** Plenty of post-warmup samples for a one-dimensional posterior;
  ESS will be in the thousands.
- **`random_seed=101`.** Reproducibility, again. The exact posterior summary is the
  same every run.
- **`log_likelihood=True`.** Stores pointwise log-likelihoods so that LOO/WAIC model
  comparison is available later. We do not compare models here (there is only one),
  but the portfolio always stores it so the option exists.

We also attach **prior and posterior predictive** samples to the same `InferenceData`
object, so a single `idata` carries everything Steps 3, 5, 6, and 7 need.

### Lightness as a constraint

Throughout the portfolio, sampling is kept light (`draws=500–1000`, `chains=2–4`) so
notebooks and tests finish in seconds. The recovery test, SBC, and prior-sensitivity
scripts use even lighter settings (or the analytic posterior) where they can. This
is a deliberate engineering constraint: a workflow you cannot re-run quickly is a
workflow you will not re-run, and the whole point is to iterate.

### What can go wrong at Step 4

- **Too few tuning steps** (BUG 2). NUTS never adapts; you get a poorly-mixed chain
  and meaningless diagnostics. *Fix:* `tune` of several hundred to a few thousand.
- **One chain** (BUG 2). R-hat cannot do its between-chain comparison. *Fix:* ≥2
  chains, ideally 4.
- **No seed.** Non-reproducible posteriors; a flaky test. *Fix:* always set
  `random_seed`.
- **Trusting the mean before reading diagnostics.** A starved sampler can still
  produce a roughly-right point estimate, which lulls you into skipping Step 5. Never
  report a posterior you have not diagnosed.

---

## Step 5 — Computational diagnostics

> **Goal of this step:** answer the question "did the *sampler* work?" — entirely
> separate from "is the *model* right?" (that is Step 6). Diagnostics are about the
> machinery, not the science.

This is the step beginners most often skip and experts never do. A posterior summary
is worthless if the chains that produced it did not converge. We compute and read
three things.

### R-hat (potential scale reduction factor)

`R-hat` compares the variance *between* chains to the variance *within* each chain.
If the chains have converged to the same distribution, these match and `R-hat ≈ 1.00`.

- **`R-hat ≈ 1.00`** — chains agree; good.
- **`R-hat > 1.01`** — chains disagree; the sampler has *not* converged. Do not trust
  the posterior. Common causes: too few draws, a multimodal posterior, or a
  non-identified model.

For this model you should see `R-hat = 1.0` to two decimals. If you ever see it
above 1.01, the first moves are: run longer, run more chains, and inspect the trace
for one chain stuck in a different region.

### ESS (effective sample size)

MCMC draws are autocorrelated, so 1000 draws are worth fewer than 1000 *independent*
draws. ESS estimates how many independent draws you effectively have. ArviZ reports
two flavours:

- **`ess_bulk`** — effective samples for estimating the *center* of the distribution
  (means, medians). Want ≳ 400.
- **`ess_tail`** — effective samples in the *tails*, which govern the reliability of
  credible-interval endpoints. Want ≳ 400.

For a one-dimensional, well-behaved posterior like this, ESS will be in the thousands.
Low ESS (a few dozen) signals heavy autocorrelation — raise `draws`, or fix whatever
geometry is slowing the sampler.

### Divergences

A *divergence* is NUTS reporting that its numerical trajectory blew up — usually
because the posterior has a region of high curvature the sampler could not navigate
at its current step size. Even a handful of divergences can mean a whole region of
the posterior is being under-sampled, biasing your estimates.

```python
n_div = int(idata.sample_stats['diverging'].sum())
```

- **0 divergences** — what we expect here; the Beta posterior is smooth and benign.
- **> 0 divergences** — investigate. The standard remedies, in order: raise
  `target_accept` (0.9, 0.95, 0.99) to shrink the step size; reparameterize the model
  (the famous "non-centered" trick for hierarchical models, which we meet later); or
  recognize that the divergences are pointing at a genuinely pathological geometry
  (a funnel) that needs a structural fix.

### The trace plot

```python
az.plot_trace(idata, var_names=['theta'])
```

Read the right-hand panels: each chain's draws over iterations should look like a
**fuzzy caterpillar** — a stationary, well-mixed band with no trends, no chains
parked in separate regions, no slow drift. The left-hand panels overlay each chain's
marginal density; for converged chains they should sit on top of one another. A
"healthy caterpillar" is the single fastest visual check that sampling went well.

### The summary table

```python
print(az.summary(idata, var_names=['theta']))
```

This one table contains `mean`, `sd`, the HDI bounds, `r_hat`, `ess_bulk`, and
`ess_tail`. Reading it is a reflex you should build now: glance at `r_hat` (≈1.00?),
glance at the two ESS columns (≳400?), then read the estimate. Always in that order —
diagnostics first, estimate second.

### What to do when diagnostics fail

A compact field guide (we will need every row of it in later projects):

| Symptom | Likely cause | First remedy |
|---|---|---|
| `R-hat > 1.01` | Chains not converged / multimodal | More draws; inspect trace; suspect identifiability |
| Low `ess_bulk` | High autocorrelation | More draws; reparameterize |
| Low `ess_tail` | Poorly-sampled tails | More draws; raise `target_accept` |
| Divergences > 0 | High-curvature geometry | Raise `target_accept`; non-centered parameterization |
| One chain offset in trace | Multimodality / bad init | More chains; better inits; rethink the model |

For Project 01 you will hit none of these — which is the point. You learn to read a
*clean* diagnostic report against a known-good case, so that when a later project's
report is *dirty*, you recognize it instantly.

---

## Step 6 — Posterior predictive checks

> **Goal of this step:** now that the sampler has worked, ask whether the *model*
> describes the data. A posterior predictive check (PPC) simulates new data from the
> fitted posterior and compares it to what we actually observed.

Diagnostics (Step 5) asked "did we compute the posterior correctly?" PPCs ask the
different, scientific question "is this posterior's *model* an adequate description
of reality?" A model can be sampled perfectly and still be wrong.

The posterior predictive distribution is:

```
p(y_new | y) = integral  p(y_new | theta) p(theta | y) d theta,
```

"what datasets does the fitted model expect?" If the model is adequate, the data we
actually saw should look like a typical draw from it.

### The graphical check

```python
az.plot_ppc(idata, num_pp_samples=200)
```

ArviZ overlays the distribution of the observed data with many posterior-predictive
replicates. For binary data the natural summary is the success count; the observed
`k = 47` should sit comfortably inside the cloud of replicated counts. If the
observed value were out in the tail of the predictive cloud, the model would be
failing to reproduce a feature of the data.

### The numerical check: a Bayesian p-value

```python
pp = idata.posterior_predictive['y']
pp_k = pp.sum(dim=pp.dims[-1]).values.ravel()      # sum over OBSERVATION axis
p_value = float(np.mean(pp_k >= data['k']))
```

This computes the fraction of posterior-predictive datasets whose success count
meets or exceeds the observed `k`. A value **near 0.5** means the observed data are
typical of the model — a good fit. Values near 0 or 1 mean the observed data are
extreme relative to the model, signalling misfit.

**Note the reduction axis.** `pp` has dims `(chain, draw, observation)`; to get a
predicted `k` per replicated dataset you sum over the **observation** axis
(`pp.dims[-1]`). Summing over `draw` instead is BUG 3 of the broken notebook — it
produces a number that is *not* a predicted `k`, looks plausible, and raises no error.
A predicted `k` must lie in `[0, n] = [0, 80]`; that is the sanity check that catches
the wrong-axis reduction.

### What a PPC can and cannot catch

A PPC will catch a model that fails to reproduce a *feature you chose to look at*.
Choosing the success count `k` catches the wrong central tendency but is blind to,
say, *over-dispersion* — extra batch-to-batch variability that violates assumption
(A2). The extension prompt in `rubric.md` deliberately injects batch effects; a PPC
on the *dispersion* of per-batch counts (rather than the total `k`) is what detects
that misfit. The lesson: **a PPC is only as good as the discrepancy statistic you
check.** Pick statistics that would reveal the failure modes you care about.

### What can go wrong at Step 6

- **Checking the wrong statistic.** A PPC on `k` cannot see over-dispersion. Match
  the statistic to the assumption you want to test.
- **Wrong reduction axis** (BUG 3). Sum over observations, not draws. Print `.dims`.
- **Over-reading a single p-value.** A Bayesian p-value near 0.5 is reassuring but not
  proof of correctness; it is one check among several. Use it alongside the graphical
  PPC and, in multi-model settings, LOO.

---

## Step 7 — Model criticism & comparison

> **Goal of this step:** stress the model. Is there a better one? Is this one subtly
> wrong? In Project 01 we have a luxury no other project has: an *exact* answer to
> check against.

### Criticism via the analytic oracle

Because the model is conjugate, the exact posterior is `Beta(2 + k, 2 + n - k)`. We
overlay the MCMC posterior on this analytic curve:

```python
a_post, b_post = analytic_posterior(data)          # (2 + k, 2 + n - k)
az.plot_dist(idata.posterior['theta'].values.ravel(), label='MCMC posterior')
plt.plot(grid, beta_dist.pdf(grid, a_post, b_post), 'k--', label='analytic Beta')
plt.axvline(data['truth']['theta'], color='red', label='true theta')
```

They coincide. This is the most unambiguous model check in the entire portfolio:
the sampled posterior lies exactly on the curve we can compute by hand, and the true
`theta = 0.62` sits within the posterior's bulk. There is no clearer way to confirm
that the inference machinery is doing the right thing.

This trick — using a known result as an oracle — generalizes. Whenever any part of a
complex model has a tractable special case, fit that case and confirm you recover the
analytic answer before trusting the full model. It is the modeling equivalent of a
unit test against a known output.

### Why there is no LOO/WAIC here

Model *comparison* (LOO, WAIC, `az.compare`) requires **at least two models** to
compare. Project 01 has exactly one. We store the pointwise log-likelihood
(`log_likelihood=True`) so the option exists, but there is nothing to compare it
against yet. Comparison enters the portfolio the moment a project defines competing
models — for example, Poisson vs. Negative-Binomial for over-dispersed counts, or a
linear vs. a quadratic dose-response.

When you *do* have two models, the workflow is:

```python
loo_a = az.loo(idata_a)
loo_b = az.loo(idata_b)
az.compare({"model_a": idata_a, "model_b": idata_b})
```

LOO (leave-one-out cross-validation, approximated via Pareto-smoothed importance
sampling) estimates out-of-sample predictive accuracy. `az.compare` ranks models and
reports the difference with a standard error, so you can see whether one model is
*reliably* better or just nominally ahead. We flag this here as foreshadowing; the
mechanics arrive when there is a second model to fit.

### A preview exercise

`lessons.md` suggests adding a second, non-conjugate model — a logistic
reparameterization `theta = sigmoid(eta)`, `eta ~ Normal(0, 1.5)` — and comparing it
to the Beta model with `az.loo`. The two are nearly equivalent here, so LOO should
find them indistinguishable, which is itself an instructive result: model comparison
that (correctly) reports "no meaningful difference" is a success, not a failure.

### What can go wrong at Step 7

- **Forgetting `log_likelihood=True`.** Then LOO/WAIC cannot be computed and you must
  refit. Store it by default.
- **Over-interpreting LOO differences.** A LOO difference smaller than ~2× its
  standard error is not decisive. Read the SE, not just the point.
- **Confusing criticism with comparison.** Criticism (does this model fit?) and
  comparison (which model fits better?) are distinct. A model can win a comparison and
  still fit badly in absolute terms — always do PPCs *and* comparison.

---

## Step 8 — Decision & communication

> **Goal of this step:** the deliverable is a *decision*, not a posterior. Translate
> the distribution into something a collaborator can act on, with its uncertainty
> attached.

A density plot is not an answer to "should we advance this assay?" Step 8 closes the
loop by turning the posterior into a decision-relevant statement.

```python
post = idata.posterior['theta'].values.ravel()
mean = post.mean()
lo, hi = np.percentile(post, [3, 97])         # central 94% interval
p_above = float(np.mean(post > 0.5))          # decision-relevant probability
```

For this dataset:

- **Posterior mean** `theta ≈ 0.585` — the best single estimate of the success rate.
- **94% credible interval** `[0.49, 0.69]` — we are 94% sure the true rate lies here.
  (Note this is a *credible* interval, with the direct probabilistic interpretation a
  frequentist confidence interval lacks: there genuinely is a 94% posterior
  probability that `theta` is in this range.)
- **`P(theta > 0.5 | data) ≈ 0.92`** — the probability the assay succeeds more often
  than not. This is the number a decision-maker actually wants.

### Translating to a recommendation

`summary_onepager.md` does this in full, but the shape of the communication is:

> "The assay's success rate is most plausibly about 59%, with a 94% credible interval
> of roughly 49%–69%. We are about 92% confident it exceeds one-half. If your bar is
> 'succeeds more often than not', the evidence is fairly strong but not conclusive
> (~1-in-12 chance the rate is actually ≤ 50%). If your bar is higher (say 65%), the
> data do not yet support that. To halve the uncertainty, collect ~4× more runs."

Notice what this communication does: it leads with the decision-relevant number,
states the uncertainty honestly, names the threshold the decision hinges on, and says
what *more data* would buy. It never shows the collaborator a density plot.

### The 94% convention

The portfolio uses **94%** intervals (ArviZ's default), not 95%, as a deliberate
nudge: there is nothing magical about 95%, and the odd number discourages reflexively
collapsing a Bayesian credible interval into a frequentist significance ritual. The
exact percentage is a choice you should make to suit the decision, not a law.

### What can go wrong at Step 8

- **Reporting a point estimate with no interval.** `theta ≈ 0.585` alone hides all
  uncertainty and invites overconfident decisions. Always pair it with an interval.
- **Reporting the posterior instead of the decision.** A collaborator cannot act on a
  density. Give them the probability of the thing they care about.
- **Ignoring the assumptions.** The whole chain of inference rests on (A1)–(A3). If
  the runs were actually batched, the stated interval is too narrow. The one-pager
  flags this caveat explicitly — the honest thing to do.

---

<a name="beyond-a-single-fit"></a>
## Beyond a single fit: SBC, prior sensitivity, and the broken notebook

The eight steps validate *one* fit of *one* model to *one* dataset. Three further
checks validate the *procedure itself*. They are what separate a workflow you have
merely executed from one you can *trust*.

### Simulation-Based Calibration (SBC) — is the procedure correct?

Diagnostics tell you a chain converged. They do *not* tell you the posterior it
converged to is the *correct* one — a model with a coding error can converge
beautifully to the wrong distribution. SBC closes that gap. Its logic:

1. Draw `theta*` from the prior.
2. Simulate a dataset from `theta*`.
3. Fit the model; obtain `L` posterior draws.
4. Record the **rank** of `theta*` among those draws.

If inference is correct, those ranks are **uniform**. Systematic departures are
fingerprints: a ∪-shape means the posterior is too narrow (over-confident), a ∩-shape
means too wide (under-confident), a slope means biased. Our SBC over 400 simulations
gives a chi-square uniformity p-value of **0.903** — emphatically uniform, exactly
what a correct conjugate model should produce. Full detail in `SBC_REPORT.md`; the
runner is `sbc.py`, which uses the analytic posterior so the whole thing finishes in
seconds.

SBC is the portfolio's standard correctness gate. It becomes *indispensable* once
models are complex enough that "the answer looks reasonable" is no longer a reliable
check — which is to say, almost immediately after this project.

### Prior sensitivity — does the answer depend on the prior?

`prior_sensitivity.py` refits the same data under Jeffreys `Beta(0.5,0.5)`, Uniform
`Beta(1,1)`, and Weak-info `Beta(2,2)`. The posterior means come out 0.586, 0.585,
0.583 — a maximum spread of **0.003**, negligible against the ±0.05 posterior SD. The
conclusion is robust *at this sample size*. The crucial caveat, spelled out in
`PRIOR_SENSITIVITY.md`: robustness is a property of `n`, not of the priors. Re-run at
`n = 5` and the three posteriors visibly separate. Always demonstrate robustness at
the sample size you actually have.

### The broken notebook — can you diagnose seeded failures?

`notebook_broken.ipynb` contains three deliberately seeded bugs, each tied to this
project's pitfalls; `BROKEN_BUGS.md` is the answer key. In brief:

- **BUG 1** — a flat `Beta(1,1)` prior that over-trusts extreme rates. *Revealed by*
  the prior predictive check.
- **BUG 2** — `tune=5, chains=1` starving NUTS so R-hat/ESS become meaningless.
  *Revealed by* the `az.summary` diagnostics.
- **BUG 3** — the posterior predictive summed over the `draw` axis instead of the
  observation axis, producing a silently-wrong predicted `k`. *Revealed by* printing
  `.dims` and sanity-checking that a predicted `k` must lie in `[0, n]`.

The exercise teaches the most valuable skill of all: not writing correct code, but
*recognizing incorrect code from its symptoms*.

---

<a name="common-pitfalls"></a>
## Common pitfalls (tied to this project's key pitfall)

The project's headline pitfall is **"flat is not uninformative"**, but it sits inside
a family of related traps. Collected here for quick reference:

### 1. Mistaking a flat prior for no assumptions (THE key pitfall)

`Beta(1,1)` is uniform on `theta`, which *feels* neutral but asserts that
near-certain success/failure is as plausible as a middling rate. With scarce data it
produces wild posteriors. **Cure:** weakly-informative priors (`Beta(2,2)` here) plus
a prior predictive check to make the pathology visible. This is the same disease that,
on a *scale* parameter, becomes an improper prior that breaks inference outright
(Project 02) — so the habit you build here is load-bearing later.

### 2. Confusing convergence with correctness

R-hat ≈ 1.00 means the *sampler* worked. It says nothing about whether the *model* is
right or even whether the posterior is the correct one for the model. **Cure:**
posterior predictive checks (model correctness) and SBC (procedure correctness) on
top of diagnostics.

### 3. Starving the sampler and trusting the mean anyway

Too little tuning or a single chain corrupts the diagnostics while sometimes leaving
the point estimate looking fine. **Cure:** adequate `tune`, ≥2 chains, and the
discipline to *read* R-hat/ESS before reading the estimate.

### 4. Reducing xarray over the wrong axis

PPC and prior-predictive arrays are `(chain, draw, observation)`. Summing over the
wrong axis gives a plausible-looking, silently-wrong number with no error. **Cure:**
print `.dims`/`.shape` before reducing; sanity-check magnitudes (a predicted `k` must
be in `[0, n]`).

### 5. Reporting a posterior instead of a decision

A density plot is not an answer. **Cure:** Step 8 — point estimate *with* interval,
plus the probability of the decision-relevant event, plus a plain-language sentence.

### 6. Assuming robustness instead of demonstrating it

"The prior doesn't matter" is true here only because `n = 80`. **Cure:** run the prior
sensitivity analysis at your actual sample size; never extrapolate robustness from a
larger `n` to a smaller one.

### 7. Forgetting the modeling assumptions

(A1) independence, (A2) constant `theta`, (A3) binary outcomes underlie everything.
Forgetting them means the stated uncertainty can be badly wrong (e.g. too narrow if
data are batched). **Cure:** write the assumptions down at Step 1 and re-examine them
at Step 6 and Step 8.

---

## How to run everything

All commands run **from the project directory** with `python3` (the only interpreter
with numpy/pymc in this environment — never bare `python` or `pytest`).

```bash
# 1. Generate the synthetic data (writes data/data.npz, prints the truth)
python3 data/generate_data.py

# 2. Smoke-test the model standalone (fits and prints a summary)
python3 model.py

# 3. Build both notebooks (notebook.ipynb and notebook_broken.ipynb)
python3 build_notebook.py

# 4. Statically validate the notebooks (schema + per-cell syntax)
python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb

# 5. Fast recovery test (fits with a light sampler, asserts truth recovered)
python3 -m pytest test_recovery.py -q

# 6. Simulation-based calibration (writes sbc_ranks.png, prints the chi-square test)
python3 sbc.py

# 7. Prior sensitivity (prints the three-prior comparison table)
python3 prior_sensitivity.py
```

Then open `notebook.ipynb` and run it top to bottom (it executes in well under a
minute on CPU). The environment is pinned by the shared top-level
`requirements.txt` / `environment.yml`; do not duplicate dependencies per project.

---

## Glossary

- **Bernoulli trial** — a single binary (0/1) experiment with success probability
  `theta`.
- **Binomial** — the distribution of the number of successes in `n` independent
  Bernoulli trials.
- **Beta distribution** — a distribution on `(0, 1)`, the natural prior for a
  probability; conjugate to the Bernoulli/Binomial.
- **Conjugate prior** — a prior that yields a posterior in the same family; here
  `Beta` prior → `Beta` posterior.
- **Prior predictive distribution** — the distribution of data implied by the model
  *before* seeing any data; used to sanity-check priors.
- **Posterior predictive distribution** — the distribution of new data implied by the
  *fitted* model; used to check fit.
- **NUTS** — the No-U-Turn Sampler, an adaptive Hamiltonian Monte Carlo MCMC method.
- **R-hat** — a convergence diagnostic comparing between- and within-chain variance;
  ≈1.00 is healthy.
- **ESS** — effective sample size; the number of effectively-independent draws,
  accounting for autocorrelation.
- **Divergence** — a NUTS trajectory failure flagging high-curvature geometry the
  sampler could not navigate.
- **Credible interval** — a posterior interval; "94% credible" means 94% posterior
  probability that the parameter lies inside.
- **HDI** — highest-density interval; the narrowest credible interval at a given
  probability.
- **SBC** — simulation-based calibration; checks that the *inference procedure* is
  self-consistent by testing rank uniformity.
- **LOO / WAIC** — leave-one-out / widely-applicable information criteria;
  estimate out-of-sample predictive accuracy for model comparison.
- **Bayesian p-value** — the posterior-predictive probability of a discrepancy
  statistic as extreme as observed; near 0.5 indicates good fit.

---

*Project 01 of the 20-project Bayesian-workflow teaching portfolio. The
single-parameter Beta–Binomial is the "hello world" that contains, in miniature,
every move the hard projects make. Master the workflow here — where an exact answer
keeps you honest — and the later models become a matter of new likelihoods and new
geometry, not new process.*

---

## Appendix A — A fully worked numerical walkthrough

It is worth grinding through the arithmetic once, by hand, so the machinery stops
being a black box. We use the exact dataset the DGP produces: `n = 80`, `k = 47`.

### A.1 The prior as pseudo-counts

We chose `theta ~ Beta(2, 2)`. In pseudo-count language this is "1 prior success and
1 prior failure" (recall `Beta(a, b)` ≈ `a - 1` successes and `b - 1` failures). The
prior mean is `a / (a + b) = 2 / 4 = 0.5`, and the prior concentration is `a + b = 4`
— equivalent in weight to having seen 4 - 2 = 2 prior observations. Against 80 real
observations, that is a 2-vs-80 contest. The data will win overwhelmingly.

### A.2 The likelihood

The likelihood as a function of `theta` is proportional to
`theta^k (1 - theta)^(n - k) = theta^47 (1 - theta)^33`. Its maximum (the maximum-
likelihood estimate) sits at `k / n = 47 / 80 = 0.5875`. This is the "data-only"
answer that ignores the prior — the value a frequentist point estimate would report.

### A.3 The posterior

Conjugacy gives the posterior in closed form:

```
theta | k, n  ~  Beta(a + k, b + n - k) = Beta(2 + 47, 2 + 80 - 47) = Beta(49, 35).
```

From the Beta distribution's formulas:

- **Posterior mean** = `49 / (49 + 35) = 49 / 84 = 0.5833`.
- **Posterior variance** = `(49 * 35) / ((84^2)(85)) = 1715 / 599760 = 0.002860`, so
  the **posterior SD** = `sqrt(0.002860) = 0.0535`.
- **94% central interval** = `[Beta.ppf(0.03, 49, 35), Beta.ppf(0.97, 49, 35)]`
  ≈ `[0.481, 0.682]`.

### A.4 Reading the result

Three observations connect the arithmetic to the workflow:

1. **The posterior mean (0.583) sits between the prior mean (0.5) and the MLE
   (0.5875), much closer to the MLE.** The precision-weighted average formula
   `(a + k) / (a + b + n) = 49 / 84` makes this exact: the data's weight (80) swamps
   the prior's weight (4), pulling the compromise almost all the way to the data.

2. **The true value (0.62) lies inside the 94% interval `[0.481, 0.682]`.** Inference
   recovered the truth — which is exactly what `test_recovery.py` asserts
   automatically. Note the truth is *not* at the center: with only 80 runs, sampling
   noise left the data slightly low (observed rate 0.5875 vs true 0.62), and the
   posterior faithfully reflects the data it was given.

3. **The posterior SD (0.0535) quantifies the uncertainty.** This is the number that
   makes the Bayesian answer more useful than the bare MLE of 0.5875: we are not
   merely guessing 0.58, we are saying "0.58, give or take about 0.05, and here is
   the full distribution."

### A.5 Why the MCMC matches

When you run `model.fit` and overlay the sampled posterior on `Beta(49, 35)` (Step
7), they coincide to within Monte Carlo error. The sampler does not "know" the
analytic answer — it explores the posterior using only gradients of the log-density —
yet it reproduces `Beta(49, 35)` precisely. That agreement is your proof that NUTS is
implemented and configured correctly, and it is the trust you carry into the
non-conjugate models where no such check exists.

---

## Appendix B — Frequently asked questions

**Q: Why use MCMC when the answer is a closed-form Beta?**
A: Pedagogy and transferability. The closed form exists *only* because of conjugacy,
which almost no real model enjoys. We learn the general-purpose tool (NUTS) on the one
problem where we can check it against an exact oracle, then deploy it where we cannot.

**Q: Is `Beta(2, 2)` always the right prior for a proportion?**
A: No. It is a reasonable *weakly-informative default* when you genuinely have little
prior knowledge but want to avoid the flat-prior pathology. If you have real prior
information — say, similar assays historically succeed ~70% of the time — encode it
(e.g. `Beta(7, 3)`), then check it with a prior predictive check and a sensitivity
analysis.

**Q: Credible interval vs confidence interval — what's the difference?**
A: A 94% *credible* interval is a direct probability statement: given the data and
model, there is 94% posterior probability the parameter lies inside. A frequentist
94% *confidence* interval has a more contorted interpretation (94% of such intervals,
over hypothetical repeated experiments, would contain the fixed true value). The
Bayesian statement is the one collaborators actually want, and it is the one Step 8
reports.

**Q: My R-hat is 1.00 and ESS is huge — am I done?**
A: You have passed Step 5 (the sampler worked). You still owe Step 6 (does the model
fit the data?) and, for the procedure as a whole, SBC. Convergence is necessary, not
sufficient.

**Q: The posterior mean (0.583) isn't the true value (0.62). Is something wrong?**
A: No. The *data* came out slightly low (47/80 = 0.5875) due to sampling noise, and
the posterior correctly reflects the data it saw. The truth lies well inside the 94%
interval, which is the right notion of "recovered". A posterior that nailed 0.62
exactly from low data would actually be suspicious.

**Q: How many runs would I need to halve the uncertainty?**
A: Posterior SD shrinks like `1 / sqrt(n)`, so halving it requires roughly **4× the
data** — about 320 runs instead of 80. The one-pager states this so a collaborator can
weigh the cost of more experiments against the value of tighter certainty.

**Q: What if my outcomes aren't really binary (borderline wells)?**
A: Then assumption (A3) is violated and this model is mis-specified. Options: define a
crisp scoring rule to make outcomes binary, or move to a model with a graded outcome
(e.g. ordinal or continuous). Do not force binary structure onto graded data and hope.

**Q: Where does this go next?**
A: Project 02 adds a second parameter (a scale) and shows how a flat prior on it — the
same pitfall as here, but on a variance — genuinely breaks inference rather than merely
nudging it. The workflow stays identical; only the likelihood and the geometry change.

---

## Appendix C — Checklist (print this)

Use this as a per-fit checklist. It is the eight steps plus the three meta-checks,
condensed to one line each.

- [ ] **Step 1** — DGP documented, seeded, exposes a `truth` dict; assumptions
  (A1)–(A3) written down.
- [ ] **Step 2** — Likelihood matches the data story; prior justified
  (weakly-informative, not flat).
- [ ] **Step 3** — Prior predictive check run; implied data are sane.
- [ ] **Step 4** — NUTS with ≥2 chains, adequate `tune`, fixed `random_seed`,
  `log_likelihood=True`.
- [ ] **Step 5** — R-hat ≈ 1.00, ESS ≳ 400, 0 divergences, trace is a fuzzy
  caterpillar.
- [ ] **Step 6** — Posterior predictive check + Bayesian p-value near 0.5; correct
  reduction axis.
- [ ] **Step 7** — Criticized against the analytic oracle (or LOO if ≥2 models).
- [ ] **Step 8** — Point estimate *with* interval + decision-relevant probability +
  plain-language sentence.
- [ ] **SBC** — rank histogram uniform (chi-square p not tiny).
- [ ] **Prior sensitivity** — robust at *this* `n`; caveat stated.
- [ ] **Assumptions** — re-examined; caveats flagged in the one-pager.

If every box is ticked, you have not just produced a number — you have produced a
*defensible* number, with its uncertainty, its assumptions, and its decision all
attached. That is the whole point of the Bayesian workflow, and it is the standard
every project in this portfolio holds itself to.

---

## Appendix D — The data-generating story in depth

It is tempting to treat Step 1 as a formality — "we simulate some coin flips" — and
rush to the modeling. Resisting that temptation is itself a lesson, because the data
story is where every downstream assumption is born.

### D.1 Why a *biochemical assay*, concretely

Picture a 96-well plate. Into each well you pipette substrate and enzyme; after
incubation a well either turns positive (the reaction fired) or stays negative. You
run the plate 80 times under nominally identical conditions. The question your PI
asks is deceptively simple: "what fraction of the time does this thing actually
work?" The naive answer — count the positives and divide — throws away the single
most important piece of information: *how sure are you?* If 47 of 80 fired, is the
true rate 0.59? Could it be 0.50? Could it be 0.70? The Bayesian posterior answers
all three at once.

This scenario is the binary skeleton under a huge range of real biology: a CRISPR
edit either took or it did not; a cell either expressed a marker or it did not; a PCR
either amplified or it did not; a patient either responded or did not. Whenever the
unit of observation is a yes/no event with a stable underlying rate, you are in the
Beta–Binomial world of Project 01.

### D.2 Each assumption, made physical

The three assumptions are not abstractions; each corresponds to a way a real plate
could betray you.

- **(A1) Independence — "no shared cause of failure."** Suppose one corner of the
  plate dried out, so those wells failed together. Their outcomes are now correlated:
  knowing one corner well failed tells you the others likely did too. The Binomial
  likelihood, which assumes 80 independent coin flips, will *understate* the
  uncertainty, because correlated data carry less information than the same number of
  independent data. Your 94% interval will be too narrow — overconfident.

- **(A2) Constant `theta` — "no drift, no batch effect."** Suppose the enzyme
  degrades over the afternoon, so early runs succeed at 0.70 and late runs at 0.50.
  There is no single `theta`; there is a *distribution* of rates. Fitting one `theta`
  averages them (~0.60) but mis-states the spread: the per-run variability is larger
  than a single-rate Binomial predicts. This is *over-dispersion*, and it is exactly
  what the `rubric.md` extension prompt injects to make the simple model fail a PPC.

- **(A3) Binary outcomes — "no borderline wells."** Suppose some wells are faintly
  positive and a human scores them inconsistently. Now the "data" are partly noise in
  the *scoring*, not the *biology*. No amount of clever modeling of `theta` fixes a
  measurement that is itself ambiguous; you must fix the assay or model the grading.

### D.3 Why synthetic data are a feature, not a cheat

A common objection: "isn't it circular to test a model on data you simulated from a
model you control?" No — it is the *only* way to validate inference, because it is the
only setting where you know the answer. If a method cannot recover a truth you *put
in*, it certainly will not recover a truth you do not know. Synthetic-data recovery is
a *necessary* condition for trusting a method on real data, and `test_recovery.py`
encodes exactly that condition as an automated gate. The portfolio uses synthetic data
everywhere for this reason: known truth is the bedrock that makes every other check
meaningful.

### D.4 The bridge to SBC

Recovery (`test_recovery.py`) checks inference on *one* truth. SBC (`sbc.py`)
generalizes it to *many* truths drawn from the prior, and checks not just "is the
truth inside the interval?" but "are the intervals the right *size*, on average?"
Recovery is a single spot-check; SBC is the full calibration sweep. Both rest on the
same foundation laid in Step 1: a data-generating story with a known truth. Get the
data story right, and every validation downstream has something solid to stand on.

### D.5 A note on sample size and the shape of the answer

With `n = 80`, the empirical rate (0.5875) already pins `theta` to within about ±0.05.
Had we drawn `n = 8`, the same true rate could have produced anywhere from 3 to 7
successes, and the posterior would be visibly wider and visibly more prior-dependent.
Had we drawn `n = 800`, the interval would shrink to about ±0.017 and the prior would
be utterly irrelevant. The *shape* of your final answer — how wide, how prior-sensitive
— is determined at Step 1 by how much data you chose to collect. Modeling cannot
manufacture certainty the data do not contain; it can only report, honestly, how much
certainty is there. That honesty is the product the Bayesian workflow ships.
