# Lessons — Project 01: Estimating a Proportion

This is the lessons report for the first project in the portfolio. It records what
the project *teaches*, the surprises and failure modes encountered while building
and running it, and how the single-parameter Beta–Binomial generalizes to the
harder models that follow.

---

## 1. What this project is really about

On the surface Project 01 estimates one number: the success probability `theta`
of a binary biochemical assay. That is almost trivial — there is even a
closed-form answer. The *point* of the project is not the answer. It is to walk
the **entire Bayesian workflow** once, end to end, on a model so simple that
nothing can hide. Every later project reuses the same eight steps; here we learn
the steps in isolation, where we can check every one against an exact result.

The eight steps, and the artifact in this project that embodies each:

1. **Problem & data story** — `data/generate_data.py` (a documented Bernoulli DGP).
2. **Model spec with justified priors** — `model.py` (`Beta(2,2)`, not `Beta(1,1)`).
3. **Prior predictive checks** — Step 3 cell in `notebook.ipynb`.
4. **Inference (NUTS)** — `model.fit`, even though conjugacy makes it optional.
5. **Computational diagnostics** — R-hat / ESS / divergences in Step 5.
6. **Posterior predictive checks** — `az.plot_ppc` and a Bayesian p-value.
7. **Model criticism** — overlay MCMC posterior on the exact analytic Beta.
8. **Decision & communication** — `summary_onepager.md`.

Plus the three "correctness" artifacts that go beyond a single fit:
SBC (`sbc.py`), prior sensitivity (`prior_sensitivity.py`), and the seeded-bug
debugging exercise (`notebook_broken.ipynb` + `BROKEN_BUGS.md`).

---

## 2. Takeaways

### 2.1 "Flat" is not "uninformative"

The single most transferable lesson. A `Beta(1,1)` prior is uniform on `theta`,
which *feels* like "no opinion". But uniform-on-the-probability is a strong claim:
it says `theta = 0.999` is exactly as plausible a priori as `theta = 0.5`. For an
assay, near-certain success or near-certain failure are extraordinary states; a
prior that treats them as ordinary will, with little data, cheerfully report a
posterior mean near 0 or 1 from a couple of lucky runs.

`Beta(2,2)` is mild, unimodal, centred at 0.5, and pulls gently off the 0/1 edges.
It is *weakly informative* — it encodes the boring-but-true fact that assays
usually do not succeed essentially never or essentially always. With N=80 the
choice barely matters (see §3.1), but the habit it instills matters enormously
later, where flat priors on a variance or a slope genuinely break inference.

### 2.2 You can — and should — check inference, not just convergence

R-hat and ESS tell you the sampler *converged*. They do not tell you the
*posterior is correct*. Simulation-Based Calibration (SBC) does. Draw a parameter
from the prior, simulate data, refit, and record where the true value ranks among
the posterior draws. Over many repetitions those ranks must be uniform. They are
(chi-square p=0.903 over 400 simulations). This is the first time most students
see a check that a Bayesian *procedure* is self-consistent, independent of any
single dataset. It becomes indispensable once models are complex enough that
"the answer looks reasonable" is no longer a reliable check.

### 2.3 Conjugacy is a gift — use it as an oracle

Because `Beta` is conjugate to `Bernoulli/Binomial`, the exact posterior is
`Beta(a+k, b+n-k)`. We do not need MCMC at all. We use NUTS anyway (to learn it),
then **overlay the sampled posterior on the analytic curve** in Step 7. They
coincide. This gives a rare, unambiguous ground truth for "is my sampler doing
the right thing?" — and we exploit it again in `sbc.py`, where using the analytic
posterior makes SBC essentially instantaneous and isolates *modeling* correctness
from sampler noise.

### 2.4 The deliverable is a decision, not a posterior

Step 8 and `summary_onepager.md` exist to make this concrete. A collaborator does
not want a density plot; they want "is the rate above one-half, and how sure are
you?" The posterior answers: mean ≈ 0.585, 94% credible interval ≈ [0.48, 0.69],
and `P(theta > 0.5 | data) ≈ 0.92`. Translating distribution → decision is a
distinct skill, and the portfolio treats it as a first-class step from project 1.

---

## 3. Surprises & failures encountered while building

### 3.1 The priors agreed to three decimal places

Running `prior_sensitivity.py`, the posterior means under Jeffreys `Beta(0.5,0.5)`,
Uniform `Beta(1,1)`, and Weak-info `Beta(2,2)` were 0.586, 0.585, 0.583 — a
maximum spread of **0.003**. That is the lesson, not a bug: with N=80 the
likelihood dominates and prior choice is nearly irrelevant. The corollary is the
real warning — *this robustness is a property of the sample size, not of the
priors*. Re-run with N=5 and the same three priors visibly diverge. Robustness
must be demonstrated at the N you actually have, never assumed.

### 3.2 The PPC reduction axis is a silent trap

The most insidious seeded bug (BUG 3) is summing the posterior-predictive array
over the wrong dimension. `posterior_predictive['y']` has dims
`(chain, draw, observation)`. To get a predicted success count per replicated
dataset you must sum over the **observation** axis. Summing over `draw` produces a
number that is not nonsense-looking enough to catch by eye — it just quietly
gives a wrong "predicted k". There is no error, no warning, no failed diagnostic.
The only defenses are (a) knowing your array dimensions and (b) sanity-checking
the magnitude against the observed `k`. This taught me to always print
`.dims` and `.shape` before reducing an xarray.

### 3.3 Starving the sampler degrades diagnostics, not just estimates

BUG 2 sets `tune=5, chains=1`. With only 5 tuning steps NUTS never adapts its
step size or mass matrix, and with a single chain **split-R-hat cannot be
computed meaningfully** (it needs ≥2 chains to compare). The surprise for a
newcomer is that the posterior mean might still look roughly right — the failure
shows up in the *diagnostics*, not necessarily in the point estimate. The lesson:
always run ≥2 (ideally 4) chains and give NUTS enough tuning, then *read* R-hat
and ESS rather than trusting the mean.

### 3.4 `sample_prior_predictive` dimension names vary

A small but real friction: the auto-generated last-dimension name for the
observed variable (e.g. `y_dim_2`) is not stable across PyMC versions, so the
notebook reduces over `dims[-1]` defensively rather than hard-coding a name. Worth
internalizing early because the same array-shape awareness prevents BUG 3.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Weakly-informative vs flat priors | Every project; critical for variances (P02), slopes (P04), and hierarchical scales (P09+). |
| Prior predictive checks | The only guard against absurd priors once models are too complex to reason about by hand. |
| SBC for procedure correctness | The portfolio's standard correctness gate; indispensable for hierarchical and latent-variable models. |
| Reading R-hat/ESS/divergences | Becomes load-bearing the moment geometry gets hard (funnels in P09, multimodality in P13). |
| Posterior predictive p-values | Generalize to LOO-PIT and discrepancy statistics for model criticism. |
| Posterior → decision | The capstone (P20) is *entirely* about this step. |

The Beta–Binomial is the "hello world" that contains, in miniature, every move
the hard projects make. Master the workflow here where an exact answer keeps you
honest, and the later models become a matter of new likelihoods and new geometry
rather than new *process*.

---

## 5. Concrete next experiments (for the reader)

- Re-run `prior_sensitivity.py` with `N=5` and `N=500`. Watch the prior matter,
  then stop mattering.
- Break SBC on purpose: use `Beta(a+k, b+n-k+5)` (an over-wide posterior) and
  confirm the rank histogram turns ∩-shaped (under-confident).
- Add a second model (e.g. a logistic reparameterization `theta = sigmoid(eta)`,
  `eta ~ Normal`) and compare with `az.loo` — a preview of Step 7 with two models.
- Replace the i.i.d. assumption with batch effects (some runs share a sub-rate)
  and watch the simple model's PPC start to fail — motivation for hierarchy (P09).
