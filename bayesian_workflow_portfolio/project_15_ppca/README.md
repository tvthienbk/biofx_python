# Project 15 — Latent dimensions (probabilistic PCA / factor model)

> **Workflow focus:** latent *continuous* structure and the **rotational
> non-identifiability** pitfall. A panel of correlated measurements is driven by a
> few latent factors; we recover the structure but learn to interpret only
> **rotation-invariant** quantities (noise level, reconstructed covariance,
> subspace) rather than raw loadings.

Part of the 20-project Bayesian-workflow portfolio. Projects 13–14 had latent
*discrete* structure (which component / which state). Here the latent variables
are **continuous** factor scores, and the new failure mode is a *continuous*
symmetry: the loadings and scores can be rotated/reflected without changing the
likelihood. The lesson — *interpret invariants, not raw parameters* — is one of
the most important in applied Bayesian modelling.

## Compute requirements

| Step | Command | Approx wall-clock (2 cores, no BLAS) |
|------|---------|--------------------------------------|
| data | `python3 data/generate_data.py` | < 1 s |
| fit  | `python3 model.py` | ~ 32 s |
| notebooks | `python3 build_notebook.py` | < 1 s |
| validate | `python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb` | < 1 s |
| test | `python3 -m pytest test_recovery.py -q` | ~ 34 s |
| SBC | `python3 sbc.py` (12 sims, N=50) | ~ 2–3 min |
| prior sweep | `python3 prior_sensitivity.py` (3 fits) | ~ 2 min |

Sampling: `draws=500, tune=1000, chains=2, target_accept=0.9`, fixed seed,
`progressbar=False`. The shared environment is in the top-level `environment.yml` /
`requirements.txt`.

---

## The 8-step workflow

### Step 1 — Problem & data-generating story

We observe `N = 150` samples, each a vector of `D = 6` correlated measurements
(think: intensities at 6 spectral channels, or 6 omics features). The correlations
arise because a small number `K = 2` of unobserved **latent factors** drive all
six dimensions simultaneously. Probabilistic PCA models this:

```
z_n ~ Normal(0, I_K)                    # K latent factor scores per sample
x_n ~ Normal(W z_n + mu, sigma^2 I_D)   # D observed measurements
```

`W` (D×K) are the **loadings** (how each dimension responds to each factor), `mu`
the per-dimension offset, and `sigma` the isotropic noise. Truth: `sigma = 0.4`.

**Assumptions, made explicit:**

1. **Linear factor structure.** The latent → observed map is linear. Nonlinear
   structure (manifolds) needs a different model (GP-LVM, VAE).
2. **Isotropic Gaussian noise.** One shared `sigma` across dimensions
   (probabilistic PCA). Allowing per-dimension noise gives *factor analysis*.
3. **A fixed number of factors `K`.** Choosing `K` is the central modelling
   decision; **over-specifying `K` is this project's pitfall** (surplus factors
   are non-identified).

### Step 2 — Model specification with priors

Priors: `W ~ Normal(0,1)`, `mu ~ Normal(0,1)`, `sigma ~ HalfNormal(1)`,
`z ~ Normal(0,1)`. Nothing exotic — the action is in the **identifiability**, not
the priors.

**State the non-identifiability up front.** For any orthogonal matrix `R`
(rotation/reflection), `W → WR` and `z → Rᵀz` give the *identical* likelihood,
because `(WR)(Rᵀz) = W z`. So:

- The posterior over **raw `W` and `z` is not unimodal**; their R-hat will be
  large. **This is expected, not a convergence bug.**
- The quantities that *are* identified are **rotation-invariant** functions:
  - the noise **`sigma`**,
  - the **reconstructed covariance** `C = W Wᵀ + sigma² I` (and its trace
    `total_var`, its eigenvalues, the subspace it spans),
  - the **reconstruction** `W z` of any data point.

We will interpret only these. (One could *also* pin a constraint — e.g. force `W`
lower-triangular with positive diagonal — to make `W` itself identified; we prefer
the invariants approach because it generalizes and avoids constraint artifacts.)

### Step 3 — Prior predictive checks

We simulate datasets from the prior and check the implied **total variance**
(trace of the covariance) is comparable to or larger than what we observe — i.e.
the prior can generate data of the right scale. A prior that implied negligible or
explosive variance would be revised.

### Step 4 — Inference (NUTS settings)

`draws=500, tune=1000, chains=2, target_accept=0.9`. With `N×K` latent scores this
is a few-hundred-parameter model; it samples in ~30 s. Expect **clean** sampling
for `sigma` and the reconstruction, and **poor** mixing for raw `W`/`z` — by
design.

### Step 5 — Diagnostics: read the *right* R-hat

The headline diagnostic lesson: **check R-hat for what is identified.**

- `sigma`, `total_var`, reconstructed covariance entries → R-hat ≈ 1.0–1.05,
  healthy ESS. These are your real results.
- Raw `W` entries → R-hat often large. **Do not panic and do not "fix" it** — it
  reflects the rotation symmetry, which no amount of tuning removes. The only
  "fixes" are to interpret invariants (recommended) or impose an identifying
  constraint.
- Divergences should be 0; raise `target_accept` if not.

### Step 6 — Posterior predictive checks

Compare the **observed covariance** to posterior-predictive / reconstructed
covariances. Even though `W` wanders, `WWᵀ + sigma²I` is rotation-invariant and
stable; it should match the empirical covariance closely. The notebook shows the
three matrices (empirical, reconstructed, true) side by side and reports the
relative Frobenius error.

### Step 7 — Model criticism: how many factors?

**Over-specifying `K`** (the pitfall) makes surplus factors non-identified: they
absorb rotational freedom, hurt mixing, and do not improve fit. Robust checks:

- **Reconstruction error** as a function of `K` (it plateaus once `K` ≥ true).
- **LOO** across `K` (we compute the pointwise log-likelihood, so `az.compare` is
  available).
- The **identifiable recovery test**: `sigma` and `total_var` against truth.

`test_recovery.py` targets `sigma`, `total_var`, and the reconstructed-covariance
relative error — never raw `W`.

### Step 8 — Decision & communication

For a collaborator: *"Two latent factors explain the bulk of the cross-channel
variance; per-channel noise is ≈ 0.4. The factor directions are defined only up to
rotation, so interpret the reconstruction and the dimensionality — not individual
loading numbers."* See `summary_onepager.md`.

---

## Common pitfalls (tied to this project's key pitfall)

1. **Interpreting raw loadings (THE pitfall).** `W[i,j]` is not identified; any
   rotation changes it. Symptom: large `W` R-hat, multimodal `W` marginals. Fix:
   report rotation-invariant quantities (reconstruction, subspace, sigma).
2. **Over-specifying `K`.** Surplus factors are non-identified → poor mixing, no
   fit gain. Choose the smallest `K` that reconstructs the covariance; check with
   LOO / reconstruction-vs-K.
3. **Panicking at `W`'s R-hat.** It is *supposed* to be large; checking the wrong
   parameter wastes effort. Know which quantities are identified before reading
   diagnostics.
4. **Forgetting sign flips.** Even `K=1` has a sign symmetry (`W → -W, z → -z`).
   Always invariant-ize.

## Files in this project

```
README.md                this guideline
data/generate_data.py    synthetic factor-structured data, identifiable truth
model.py                 probabilistic PCA (build_model / fit) + invariants
build_notebook.py        emits notebook.ipynb + notebook_broken.ipynb
notebook.ipynb           clean end-to-end workflow
notebook_broken.ipynb    over-specification + raw-loadings debugging exercise
test_recovery.py         recovers sigma, total_var, reconstructed covariance
sbc.py / SBC_REPORT.md   simulation-based calibration on sigma
prior_sensitivity.py / PRIOR_SENSITIVITY.md   loading-scale robustness
BROKEN_BUGS.md           instructor answer key
rubric.md                grading rubric + extension prompt
lessons.md               narrative takeaways
summary_onepager.md      non-technical decision summary
```
