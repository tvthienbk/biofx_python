# Project 14 — State switching over time (Hidden Markov Model)

> **Workflow focus:** discrete latent *dynamics*. A channel/MD system switches
> between two persistent states; we infer the transition matrix and emission
> parameters by **marginalizing the discrete state path with the forward
> algorithm** (in `pytensor.scan`, inside a `pm.Potential`). The new pitfall is
> the same label symmetry as a mixture, now over a *sequence*.

Part of the 20-project Bayesian-workflow portfolio. Project 13 introduced latent
*membership* (independent points); here the latent state **persists in time**, so
observations are correlated through the hidden Markov chain. The headline new
skill is computing an exact marginal likelihood over an exponential number of
state paths in linear time via the forward recursion.

## Compute requirements

This is one of the heavier projects because each gradient evaluation runs a
length-`T` scan.

| Step | Command | Approx wall-clock (2 cores, no BLAS) |
|------|---------|--------------------------------------|
| data | `python3 data/generate_data.py` | < 1 s |
| fit  | `python3 model.py` (T=250) | ~ 55 s |
| notebooks | `python3 build_notebook.py` | < 1 s |
| validate | `python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb` | < 1 s |
| test | `python3 -m pytest test_recovery.py -q` (T=250, 400 draws) | ~ 45 s |
| SBC | `python3 sbc.py` (12 sims, T=120) | ~ 2–3 min |
| prior sweep | `python3 prior_sensitivity.py` (3 fits) | ~ 2–3 min |

Sampling: `draws=500, tune=1000, chains=2, target_accept=0.9`, fixed seed,
`progressbar=False`. Keep `T` modest (200–300) to stay light. The shared
environment is in the top-level `environment.yml` / `requirements.txt`.

---

## The 8-step workflow

### Step 1 — Problem & data-generating story

An ion channel alternates between **closed** (state 0) and **open** (state 1).
The state is *sticky*: transitions are rare, so the channel dwells in a state for
many time steps. At each step we measure a noisy scalar (a current, or an MD
collective variable) drawn from a state-specific Gaussian. We never see the state.

```
s_1 ~ Categorical([0.5, 0.5])
s_t | s_{t-1} ~ Categorical(P[s_{t-1}, :])     # first-order Markov
y_t | s_t     ~ Normal(mu[s_t], sigma)         # noisy emission
P = [[1-p01, p01],
     [p10, 1-p10]]
```

Truth: `p01 = 0.08` (closed→open), `p10 = 0.15` (open→closed), `mu = (-1.5, 1.5)`,
`sigma = 0.6`, `T = 250`. The mean dwell times are `1/p10 ≈ 7` steps open and
`1/p01 ≈ 12` steps closed.

**Assumptions, made explicit:**

1. **Exactly two states.** As with the mixture, K is a modelling choice; here it
   is justified by the known open/closed physics.
2. **First-order Markov.** The future depends on the past only through the current
   state (no memory of how long it has already dwelt). Real channels sometimes
   show non-exponential dwell times (multiple closed sub-states) — that would need
   more states.
3. **Time-homogeneous transitions.** `P` is constant over the recording (no
   drift, no voltage ramp).
4. **Gaussian emissions with a shared `sigma`.** Per-state noise is a natural
   extension.

### Step 2 — Model: marginalize the states with the forward algorithm

The number of possible state paths is `2^T` — we cannot enumerate them. But the
marginal likelihood factorizes, and the **forward algorithm** computes it in
`O(T·K^2)` time. In log space (for numerical stability):

$$
\alpha_1[j] = \log\pi_j + \log\mathcal N(y_1;\mu_j,\sigma),
$$
$$
\alpha_t[j] = \log\mathcal N(y_t;\mu_j,\sigma) +
  \operatorname*{logsumexp}_i\big(\alpha_{t-1}[i] + \log P_{ij}\big),
$$
$$
\log p(y\mid\theta) = \operatorname*{logsumexp}_j \alpha_T[j].
$$

We implement the recursion with `pytensor.scan` and add the result as a
`pm.Potential`. NUTS then samples only the continuous parameters
`(p01, p10, mu, sigma)`; the discrete states are integrated out exactly.

**Why log-sum-exp, not max?** `logsumexp` *sums* over the previous state — that is
the marginal (total probability of all paths). Replacing it with `max` computes
the **Viterbi** best-single-path probability, a different and wrong objective for
likelihood-based inference. This is a classic, subtle bug (seeded in the broken
notebook): the model still *runs*, but the parameters are biased.

**Priors.** `p01, p10 ~ Beta(2, 8)` encodes the prior belief that switches are
rare (mean ≈ 0.2, mass concentrated below 0.4), giving sensible dwell times.
`mu ~ Normal(0, 3)` with an **ordered transform** (`mu[0] < mu[1]`) breaks the
state-label symmetry — exactly the mixture trick from Project 13, now protecting a
*sequence* model. `sigma ~ HalfNormal(1)`.

### Step 3 — Prior predictive (on parameters)

Because the likelihood is a `pm.Potential`, there is no observed RV for standard
data-space prior predictive. We instead sanity-check the *parameter* prior: the
Beta(2,8) implies dwell times of a few to tens of steps — physically reasonable.
(The notebook plots the Beta prior; one could also simulate trajectories from
prior draws and check the emission histograms look bimodal.)

### Step 4 — Inference (NUTS settings)

`draws=500, tune=1000, chains=2, target_accept=0.9`. Each leapfrog step now costs
a length-`T` scan, so sampling is ~1 min at T=250 — the price of an exact
marginal likelihood. Two chains suffice to compute R-hat; bump to 4 if you suspect
label issues. The ordered transform keeps mixing clean.

### Step 5 — Computational diagnostics

- **R-hat** ≈ 1.00 for all parameters; high `mu` R-hat ⇒ label switching (fix:
  ordering).
- **ESS** bulk/tail ≳ 400.
- **Divergences** should be 0; raise `target_accept` if not.
- **Recovered transition matrix.** Reassemble `P_hat` from posterior means of
  `p01, p10` and compare to the true `P`. The notebook prints both.

### Step 6 — Posterior predictive checks

With a Potential likelihood we roll our own PPC: simulate trajectories from
posterior-draw parameters and compare summary statistics (emission histogram,
fraction of time in the high state, dwell-time distribution) to the observed data.
Systematic misfit — e.g. observed dwell times far longer than the geometric
distribution the 2-state model implies — would point to missing states.

### Step 7 — Model criticism & identifiability

State labels are identified only via the ordered means. Report:

- **separation** `mu[1] - mu[0]` and **sigma** (label-invariant),
- **direction-aware transition probabilities** (`p01` = rate *into* the higher
  state), which are meaningful once the means are ordered.

`test_recovery.py` checks `p01, p10, mu_low, mu_high, separation, sigma` against
truth.

### Step 8 — Decision & communication

Translate to occupancy and dwell times: *"The channel is open ~37% of the time; it
opens rarely but stays open ~7 steps on average."* These are the quantities an
electrophysiologist acts on. See `summary_onepager.md`.

---

## Common pitfalls (tied to this project's key pitfall)

1. **State-label non-identifiability (THE pitfall).** Same permutation symmetry as
   a mixture. Symptom: high `mu` R-hat, chains disagree on which state is "open".
   Fix: ordered transform on the emission means.
2. **Wrong forward recursion (max vs log-sum-exp).** The model runs but optimizes
   the Viterbi path probability, not the marginal likelihood → biased parameters.
   Diagnose by checking recovery on synthetic data with known truth.
3. **Forgetting log space.** A linear-space forward recursion underflows for even
   modest `T`. Always work in logs with `logsumexp`.
4. **Sampling the discrete states.** Possible (e.g. FFBS / `pm.Categorical`) but
   mixes poorly and loses gradients. Marginalize.
5. **Too few states.** Non-exponential dwell times signal hidden sub-states; the
   posterior predictive dwell-time check is the guard.

## Fallback note

The brief permits a known-states fallback if the marginalized HMM proves fragile.
It does **not**: the marginalized forward-algorithm model samples cleanly
(R-hat ≈ 1.00, 0 divergences, ~1 min) and recovers the transition matrix and
emission means. We therefore ship the marginalized version as the primary model.

## Files in this project

```
README.md                this guideline
data/generate_data.py    synthetic HMM trajectory, known truth
model.py                 forward-algorithm marginalized HMM (build_model / fit)
build_notebook.py        emits notebook.ipynb + notebook_broken.ipynb
notebook.ipynb           clean end-to-end workflow
notebook_broken.ipynb    label + wrong-recursion debugging exercise
test_recovery.py         recovers transition probs, means, sigma
sbc.py / SBC_REPORT.md   simulation-based calibration (light)
prior_sensitivity.py / PRIOR_SENSITIVITY.md   transition-prior robustness
BROKEN_BUGS.md           instructor answer key
rubric.md                grading rubric + extension prompt
lessons.md               narrative takeaways
summary_onepager.md      non-technical decision summary
```
