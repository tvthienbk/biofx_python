# Project 16 — Detecting a shift (single change-point)

> **Workflow focus:** discrete *structural* change. A count time series undergoes
> a regime shift at an unknown time; we locate the shift and quantify the
> before/after rates. The new pitfall is a **multimodal posterior over the
> change-point** — which makes the posterior *mean* of tau a trap.

Part of the 20-project Bayesian-workflow portfolio. This project ties together
threads from the earlier latent-structure projects: like the HMM it has a discrete
latent (here a single change time), and we again show that **marginalizing the
discrete latent** is the robust path. We implement tau two ways and cross-check
them.

## Compute requirements

The lightest of the four advanced projects — both models sample in seconds.

| Step | Command | Approx wall-clock (2 cores, no BLAS) |
|------|---------|--------------------------------------|
| data | `python3 data/generate_data.py` | < 1 s |
| fit  | `python3 model.py` (both models) | ~ 10 s |
| notebooks | `python3 build_notebook.py` | < 1 s |
| validate | `python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb` | < 1 s |
| test | `python3 -m pytest test_recovery.py -q` | ~ 10 s |
| SBC | `python3 sbc.py` (45 sims) | ~ 2–3 min |
| prior sweep | `python3 prior_sensitivity.py` (3 fits) | ~ 30 s |

Sampling: discrete model `draws=1000, tune=1000, chains=4` (NUTS for rates +
Metropolis for tau); marginal model same with pure NUTS. Fixed seed,
`progressbar=False`. Shared environment in the top-level
`environment.yml` / `requirements.txt`.

---

## The 8-step workflow

### Step 1 — Problem & data-generating story

A reaction-kinetics assay counts events per time bin. At an unknown time `tau` a
catalyst is added (or a pathway switches on) and the underlying Poisson **rate**
jumps from `lam0` to `lam1`. We observe the noisy counts and want to (a) locate the
shift and (b) quantify the two rates.

```
rate_t = lam0   if t <  tau
         lam1   if t >= tau
y_t ~ Poisson(rate_t)
```

**Index convention (important).** `tau` is the index of the **first post-shift**
observation: indices `0..tau-1` are drawn at `lam0`, `tau..T-1` at `lam1`. This
matches the model's `switch(tau > t, lam0, lam1)`. Getting this convention
backwards is the seeded off-by-one bug. Truth: `tau = 70, lam0 = 4, lam1 = 11,
T = 120`.

**Assumptions, made explicit:**

1. **Exactly one change-point.** Multiple shifts need multiple taus (or a
   non-parametric prior on the number of segments).
2. **Abrupt change.** The rate jumps; a gradual ramp would need a different model
   (e.g. logistic transition).
3. **Constant rate within each regime.** No trend inside a segment.
4. **Poisson counts** (mean = variance). Over-dispersed counts would call for
   Negative-Binomial (cf. Project 06).

### Step 2 — Model specification with priors

**(a) Discrete tau (the classic switch model).**

$$
\tau \sim \text{DiscreteUniform}(1, T-1),\quad
\lambda_0, \lambda_1 \sim \text{Exponential}(1/5),\quad
\text{rate}_t = \text{switch}(\tau > t,\ \lambda_0,\ \lambda_1).
$$

PyMC samples the continuous rates with NUTS and the integer `tau` with a
Metropolis step (a `CompoundStep`). This gives an **explicit posterior over
`tau`** — which may be multimodal if several times look like plausible shifts.

**(b) Marginalized tau (the robust alternative).** `tau` has only `T-1` possible
values, so we can **sum the likelihood over all of them analytically**:

$$
p(y\mid\lambda_0,\lambda_1) =
  \sum_{\tau=1}^{T-1} p(\tau)\,
  \prod_{t<\tau}\text{Pois}(y_t;\lambda_0)\,
  \prod_{t\ge\tau}\text{Pois}(y_t;\lambda_1).
$$

We compute cumulative Poisson log-probabilities and `logsumexp` over tau, adding
the result as a `pm.Potential`. Now **only `lam0, lam1` are sampled (pure NUTS,
no discrete step)**, and we reconstruct the full `P(tau | y)` afterwards from the
per-tau weights. The two implementations should agree — a strong cross-check, and
the marginal one avoids the discrete-sampler mixing issues entirely.

Priors: `Exponential(1/5)` (mean 5) is a weakly-informative positive-rate prior;
`DiscreteUniform` over interior times encodes no prior knowledge of *when* the
shift occurred.

### Step 3 — Prior predictive checks

Prior-predictive count series should span plausible levels (rates of a few to
~tens, not thousands) and arbitrary shift locations. We check the implied count
magnitudes are sane; an Exponential(1/5) on the rates keeps them reasonable.

### Step 4 — Inference (NUTS + Metropolis)

Discrete model: `draws=1000, tune=1000, chains=4`. Four chains let us confirm all
chains agree on the same `tau` mode (chains favouring *different* peaks is the
multimodality signature). The marginal model uses pure NUTS and mixes even more
cleanly.

### Step 5 — Computational diagnostics & the tau posterior

- **R-hat / ESS** for the rates → ≈ 1.0 / healthy.
- **Do NOT summarize `tau` by its mean.** Inspect the full discrete posterior
  `P(tau | y)`. Report the **mode** and a **credible set** (smallest set of times
  covering, say, 94% of the posterior mass). Here the shift is sharp so `tau`
  concentrates on one value, but the discipline matters: with a weak shift the
  posterior spreads or splits, and the mean lands at a time the data do not
  support.
- For the discrete `tau`, Metropolis ESS can be lower than NUTS ESS; the marginal
  model sidesteps this.

### Step 6 — Posterior predictive checks

Compare observed counts to posterior-predictive counts (`az.plot_ppc`). The
two-level structure (low before, high after) should be reproduced. Systematic
over-dispersion in the residuals would suggest Poisson is too rigid
(→ Negative-Binomial).

### Step 7 — Model criticism & cross-check

The two implementations (discrete and marginalized) should give the **same** rates
and the **same** `P(tau | y)`. Agreement is strong evidence both are coded
correctly; disagreement points to an index/normalization bug. `test_recovery.py`
checks the rates' HDIs cover truth and the `tau` mode is within ±2 of the truth.

### Step 8 — Decision & communication

For a collaborator: *"The event rate jumps from ~4 to ~11 per bin at about bin 70
(credible set [68, 71]); a ~2.7-fold increase."* Report the `tau` **mode/credible
set**, the two rates, and the **fold-change** `lam1/lam0`. See
`summary_onepager.md`.

---

## Common pitfalls (tied to this project's key pitfall)

1. **Summarizing a multimodal tau by its mean (THE pitfall).** The mean falls
   between peaks and points at an unsupported time. Symptom: a `tau` mean that sits
   in a low-probability valley. Fix: report the mode and a credible *set*; show the
   full `P(tau | y)`.
2. **Wrong switch direction / off-by-one.** `switch(tau < t, ...)` (or swapped
   rates) fits a mirror-image change. Symptom: `lam0`/`lam1` come out swapped vs
   truth. Diagnose by recovery against known truth.
3. **Treating multimodality as a sampler failure.** A genuinely bimodal `tau`
   posterior (two plausible shifts) is *information*, not a bug — report both.
4. **Forcing Poisson on over-dispersed counts.** If variance ≫ mean within a
   regime, use Negative-Binomial.

## Two implementations, on purpose

`model.py` ships **both** the discrete-tau switch model (`build_model` / `fit`) and
the marginalized-tau model (`build_marginal_model` / `fit_marginal` +
`tau_posterior_from_marginal`). The notebook runs both and shows they agree. The
marginalized version is the recommended default — it removes the discrete sampler
and gives a clean `P(tau | y)`.

## Files in this project

```
README.md                this guideline
data/generate_data.py    synthetic Poisson count series with one shift
model.py                 discrete-tau AND marginalized-tau models
build_notebook.py        emits notebook.ipynb + notebook_broken.ipynb
notebook.ipynb           clean end-to-end workflow (both implementations)
notebook_broken.ipynb    wrong-switch + tau-by-mean debugging exercise
test_recovery.py         recovers rates (HDI) and tau (mode)
sbc.py / SBC_REPORT.md   simulation-based calibration on the rates
prior_sensitivity.py / PRIOR_SENSITIVITY.md   tau-prior robustness
BROKEN_BUGS.md           instructor answer key
rubric.md                grading rubric + extension prompt
lessons.md               narrative takeaways
summary_onepager.md      non-technical decision summary
```
