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
