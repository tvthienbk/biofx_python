# Project 09 — Partial Pooling (Hierarchical Means)

> **New skill:** partial pooling / shrinkage of group estimates toward a grand
> mean, with the degree of pooling learned from the data.
> **Key pitfall:** the natural *centered* parameterization creates **Neal's
> funnel** and produces divergences when the between-group SD `tau` is small. The
> fix is the *non-centered* parameterization.

This is the guideline for the project. It walks all eight steps of the Bayesian
workflow on a hierarchical Normal model, flags every modeling assumption, and ends
with a "common pitfalls" section tied to the funnel. Shared dependencies are listed
in the portfolio-root `environment.yml` / `requirements.txt`; this project does not
duplicate them.

Files: `data/generate_data.py`, `model.py`, `build_notebook.py` (writes
`notebook.ipynb` + `notebook_broken.ipynb`), `sbc.py` + `SBC_REPORT.md`,
`prior_sensitivity.py` + `PRIOR_SENSITIVITY.md`, `test_recovery.py`,
`BROKEN_BUGS.md`, `rubric.md`, `summary_onepager.md`, `lessons.md`.

---

## Step 1 — Problem & data-generating story

**Scenario.** A continuous assay readout (say a normalized fluorescence value) is
measured on `J = 12` plates, with only `n = 4` wells per plate. We want two things
at once: a good estimate of *each plate's* mean, and an estimate of *the population
of plates* — how much plates genuinely differ.

**The two naive extremes.**

- **No pooling** estimates each plate independently (its 4-well average). With so
  few wells each estimate is noisy; you will "find" plate differences that are
  pure measurement noise.
- **Complete pooling** collapses everything into one grand average, pretending all
  plates are identical and erasing real plate-to-plate variation.

**Partial pooling** is the principled middle ground: model the plates as
*exchangeable* draws from a common population, and let the data decide how much to
pull each plate toward the grand mean.

**Data-generating model.**

```
theta_j ~ Normal(mu_true, tau_true)      # plate means
y_ij    ~ Normal(theta_j, sigma_true)    # wells within a plate
```

with known truth `mu_true = 5.0`, `tau_true = 0.8`, `sigma_true = 1.0`. We choose
`tau` modest and `n` per group small *on purpose* so that (a) shrinkage is visibly
meaningful and (b) the centered parameterization's funnel can bite. The generator
(`data/generate_data.py`) fixes a seed and prints the recoverable truth.

**Assumptions made explicit.**

1. **Exchangeability** — no plate is special a priori; their means are i.i.d.
   draws from one population. (If plate 7 used a different reagent lot, this is
   violated and you'd add a covariate.)
2. **Normal population of group means** — `theta_j ~ Normal`. Heavy-tailed group
   variation would call for Student-t (see the rubric extension).
3. **Common within-group noise** `sigma` — every plate has the same measurement
   noise. Heteroscedastic plates would need `sigma_j`.
4. **Independence** of wells given the plate mean.

---

## Step 2 — Model specification with justified priors

```
mu    ~ Normal(5, 5)       # grand mean
tau   ~ HalfNormal(2)      # between-group SD
sigma ~ HalfNormal(2)      # within-group noise
theta_j = mu + tau * z_j,   z_j ~ Normal(0, 1)      # NON-CENTERED
y_ij  ~ Normal(theta_j, sigma)
```

**Why these priors.**

- `mu ~ Normal(5, 5)` is weakly informative: centred at the plausible scale of the
  readout with an SD wide enough to be dominated by 48 observations, but not so
  wide as to be silly.
- `tau ~ HalfNormal(2)` is a positive, weakly-informative scale prior. It places
  most mass on small-to-moderate between-plate spreads while allowing larger ones,
  and crucially it does **not** pile mass at `tau = 0` the way an improper prior or
  an over-tight one would (which would force complete pooling). `tau` is the
  parameter the prior-sensitivity analysis scrutinizes — with few groups it is
  weakly identified, so its prior has teeth.
- `sigma ~ HalfNormal(2)` — same logic for within-plate noise.

**Centered vs non-centered — the crux of this project.**

The *centered* form writes the model exactly as the data story reads it:

```
theta_j ~ Normal(mu, tau)     # centered
```

This couples each `theta_j` to `tau`: the conditional spread of `theta_j` *is*
`tau`. When `tau` is small the joint density of `(log tau, theta_j)` collapses into
a narrow neck (Neal's funnel), which a single-step-size sampler cannot traverse.

The *non-centered* form factors the dependence out:

```
z_j ~ Normal(0, 1)
theta_j = mu + tau * z_j      # non-centered (Deterministic)
```

Now the *sampled* quantities `z_j` always have unit-Normal geometry, independent of
`tau`. The model is mathematically identical — same prior, same likelihood, same
posterior on `theta_j` — but the sampler sees a benign, roughly isotropic space.
**We fit non-centered in the clean notebook and demonstrate the centered failure in
the broken one.** `model.build_model(data, parameterization=...)` exposes both;
`fit` defaults to `"noncentered"`.

---

## Step 3 — Prior predictive checks

Before looking at the data we simulate datasets implied by the prior
(`pm.sample_prior_predictive`) and check the implied observations cover the real
data's scale without absurd extremes. A `HalfNormal(2)` on `tau` admits everything
from near-complete-pooling (`tau ≈ 0`, all plates alike) to substantial spread —
the flexibility we want the data to resolve, not a pre-baked answer. If the prior
predictive put almost all mass outside the physically plausible readout range, we
would revise the priors *now*, before inference.

---

## Step 4 — Inference (NUTS, non-centered)

Settings: `draws=800, tune=1000, chains=4, target_accept=0.9`, fixed
`random_seed`. Rationale:

- **4 chains** make split-R-hat reliable and surface multimodality / chain
  disagreement.
- **1000 tuning steps** let NUTS adapt step size and mass matrix.
- **`target_accept=0.9`** is a mild safeguard: a slightly smaller step size than
  the 0.8 default, cheap insurance for hierarchical geometry. With non-centering it
  is more than enough to reach 0 divergences.

`model.fit` also attaches prior and posterior predictive samples and
`idata_kwargs={"log_likelihood": True}` so LOO is available downstream.

---

## Step 5 — Computational diagnostics (and what to do when they fail)

Compute and read, in order:

1. **R-hat** — must be ≈ 1.00; > 1.01 means chains disagree.
2. **ESS** (bulk and tail) — want comfortably in the hundreds for the parameters
   you report. `tau`'s tail ESS is the one to watch in hierarchical models.
3. **Divergences** — `idata.sample_stats['diverging'].sum()` must be ~0. For the
   non-centered model it is 0.
4. **Energy plot** (`az.plot_energy`) — overlays the marginal-energy and
   energy-transition distributions. A close match (high BFMI) means NUTS moves
   freely; a large mismatch is the **funnel fingerprint**, and is the first thing
   to look at in a hierarchical model even when R-hat looks fine.
5. **Funnel pairs plot** — `az.plot_pair(idata, var_names=['tau','z'],
   coords={'group':[0]}, divergences=True)`. In the non-centered space this is a
   clean round cloud; in the centered space (broken notebook) the same `(tau,
   theta_0)` pair forms the divergent neck.

**When diagnostics fail.** The hierarchical playbook, in order:

- Divergences → **reparameterize** (centered → non-centered). This is the cure.
- Still some divergences → raise `target_accept` to 0.95–0.99 (a band-aid that
  shrinks the step size).
- Low ESS on `tau` → more tuning/draws, and check the `tau` prior isn't fighting
  the data.
- High R-hat that persists → suspect multimodality or non-identifiability (later
  projects).

---

## Step 6 — Posterior predictive checks

We draw replicated datasets from the posterior (`pm.sample_posterior_predictive`)
and overlay them on the observed data with `az.plot_ppc`. A good fit envelopes the
observed spread without systematic gaps. For a hierarchical model also worth
checking: does the *between-group* spread of replicated group means match the
observed spread? Systematic under-dispersion there would flag an over-tight `tau`.

---

## Step 7 — Model criticism: shrinkage, the heart of partial pooling

The central diagnostic plot compares each plate's **no-pooling** empirical mean to
its **partial-pooling** posterior mean, with a line connecting them and the grand
mean `mu_hat` drawn as a reference. You should see:

- Every plate pulled **toward** `mu_hat` (shrinkage).
- Plates with extreme empirical means pulled **more** (they are the least
  trustworthy, so the model leans harder on the population).

This is the bias–variance trade made explicit: a little bias toward the population
buys a large reduction in variance, which is exactly why partial pooling beats both
naive extremes when groups have few observations. The amount of shrinkage is set by
`tau` relative to `sigma/sqrt(n)` — small `tau` ⇒ strong pooling.

(With a single model there is no LOO/WAIC comparison here; later projects with
competing models use `az.compare`. The recovery check against known truth plays the
role of criticism in this single-model project.)

---

## Step 8 — Decision & communication

We report the population parameters with uncertainty and verify recovery of the
known truth with `shared.bayes_utils.check_recovery`:

- `mu` ≈ 5.0 (tight interval) — the overall mean readout.
- `tau` ≈ 0.8 — plates differ from one another with a between-plate SD of ~0.8:
  real but modest variation.
- `sigma` ≈ 1.0 — within-plate measurement noise.

For a collaborator the actionable message is in `summary_onepager.md`: **report the
shrunken per-plate estimates, not the raw 4-well averages**, and budget for the
real ~0.8 plate-to-plate spread. If sharper per-plate numbers are needed, add wells
(more obs per plate), not plates.

---

## Common pitfalls (tied to this project's key hazard)

1. **Using the centered parameterization and shipping the divergences.** This is
   *the* pitfall. Divergences cluster in the small-`tau` neck, bias `tau` upward,
   and understate shrinkage. Always non-center a hierarchical scale model; see
   `notebook_broken.ipynb` and `BROKEN_BUGS.md`.
2. **Dismissing a "small" divergence count.** Three divergences can still mark a
   biased `tau`. Judge by *where* they land (the energy/pairs plots), not the raw
   number.
3. **A too-tight prior on `tau`.** `HalfNormal(0.5)` manufactures pooling: it pulls
   `tau` toward 0 and makes the plates look more alike than they are. The
   prior-sensitivity analysis shows `tau`'s posterior mean swinging by ~0.17 across
   priors while `mu` is rock-solid.
4. **Reporting raw group means as the deliverable.** The whole point of partial
   pooling is that the shrunken estimates are better, especially for small/noisy
   groups.
5. **Assuming prior robustness from another project.** Project 01's "priors don't
   matter at N=80" does **not** transfer: with 12 groups, the scale prior on `tau`
   genuinely matters.

---

## How to run

```bash
python3 data/generate_data.py        # synthesize data, print truth
python3 model.py                     # self-test: non-centered vs centered
python3 build_notebook.py            # write notebook.ipynb + notebook_broken.ipynb
python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb
python3 -m pytest test_recovery.py -q
python3 sbc.py                       # SBC ranks for mu, tau -> sbc_ranks.png
python3 prior_sensitivity.py         # tau prior sensitivity
```

All steps are light (each well under a couple of minutes on CPU).
