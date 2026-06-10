# Project 17 — Nonparametric Curves with a Gaussian Process

> **Workflow focus:** flexible function estimation without committing to a
> parametric form. **New skill:** kernels, hyperpriors, controlling flexibility.
> **Key pitfall:** the length-scale ↔ marginal-variance (and noise) trade-off,
> which a vague length-scale prior turns into outright non-identifiability.

---

## 0. Compute requirements (read first)

This is one of the four "heavy" projects in the portfolio (#17–20).

- A Gaussian process with `pm.gp.Marginal` forms an `N × N` covariance matrix and
  Cholesky-factorises it **at every leapfrog step**. Cost grows like `O(N^3)`, so
  we keep `N ≈ 40` for the main fit and `N ≈ 15` for the SBC simulations.
- **BLAS is not linked in this environment**, so dense linear algebra is slow and,
  critically, PyMC's *multiprocess* sampler can hang. We therefore sample with
  `cores=1` (serial chains). This is set inside `model.fit`; do not remove it.
- Expected wall-clock on a CPU core, serial (CPU-bound; slower under contention):
  - `python3 model.py` (self-test, 250 draws): ~60–150 s
  - `python3 -m pytest test_recovery.py -q` (250 draws + curve predict): ~90–150 s
  - `python3 sbc.py` (200 sims, **analytic** importance sampling — no MCMC): ~60 s
  - `python3 prior_sensitivity.py` (3 priors, **analytic** importance sampling): ~5 s
- The notebook uses `draws=400, tune=600` for the showcase fit. It is
  **validated statically** (AST compile), not executed, by the build runner.

If you need it faster, lower `draws`/`tune` or `N` — correctness of the recovered
`sigma` and the fitted curve does not depend on large samples here.

---

## 1. Problem & data-generating story (Step 1)

We measure a smooth response `y` at inputs `x` — think a **thermal-melt** curve
(fluorescence vs temperature) or a **dose–response** curve (effect vs log-dose).
The true relationship is some smooth nonlinear function `f(x)` whose parametric
form we either don't know or don't want to assume. Forcing a logistic or a
polynomial bakes in a shape; if the real curve has a shoulder, a secondary bump,
or asymmetry, a mis-specified parametric model will confidently mislead.

A **Gaussian process** sidesteps this. Instead of parameters of a curve, we put a
prior *directly over functions* and let the data pick the curve, with honest
uncertainty bands that widen where data are sparse.

**Data-generating process** (`data/generate_data.py`):

```
f_true(x) = 2 * sigmoid(x - 4) + 0.35 * exp(-0.5 * ((x - 7)/0.9)^2)
y_i       = f_true(x_i) + N(0, sigma^2),  sigma = 0.18,  N = 40, x in [0, 10]
```

The latent curve is a sigmoidal rise with a deliberate secondary bump — exactly
the kind of feature a single logistic would smear away. **Recoverable truths:**
(i) the latent function values `f_true(x)` at the inputs (the GP mean should track
them), and (ii) the scalar noise `sigma` (the one cleanly identifiable parameter).

**Assumptions, made explicit:**
1. `f` is smooth — the squared-exponential (ExpQuad) kernel encodes infinitely
   differentiable sample paths. If the true process had kinks, a Matérn-½/-3/2
   kernel would be more honest.
2. Noise is homoscedastic Gaussian (constant `sigma`).
3. Inputs `x` are observed without error (no errors-in-variables here).
4. The mean function is zero (we centre the data implicitly via the kernel-only
   model; a non-zero `pm.gp.mean` could be added).

---

## 2. Model specification with justified priors (Step 2)

```
f(x)  ~ GP(0, k),      k(x, x') = eta^2 * exp(-(x - x')^2 / (2 * ell^2))
y     ~ Normal(f(x), sigma)

ell   ~ InverseGamma(alpha=6, beta=12)   # INFORMATIVE length-scale prior
eta   ~ HalfNormal(2.0)                   # marginal signal sd
sigma ~ HalfNormal(0.5)                   # observation noise (recoverable)
```

We use `pm.gp.Marginal`, which **integrates the latent `f` out analytically**
(the marginal likelihood of a GP-with-Gaussian-noise is itself multivariate
normal). This is what keeps inference tractable: NUTS only explores the three
hyperparameters `(ell, eta, sigma)`, not the 40 latent function values.

### Why the length-scale prior is everything

The squared-exponential kernel has a fundamental ambiguity. The data constrain
the **overall wiggliness and amplitude** of `f`, but many `(ell, eta)` pairs
produce nearly identical fits:

- A short length-scale with small amplitude, **or**
- a long length-scale with large amplitude,

can explain the same data. Worse, both can trade against the observation noise
`sigma`: a GP can "explain" noise either as genuine short-scale signal (small
`ell`) or as observation noise (large `sigma`). Left unconstrained, this produces
a **ridge** in the posterior — a curving valley of equally-good solutions — which
manifests as high `R-hat`, low ESS, and divergences.

The fix is an **informative length-scale prior**. `InverseGamma(6, 12)` has:

- mean ≈ `beta/(alpha-1)` = 12/5 = **2.4**, mode ≈ `beta/(alpha+1)` = **1.7**,
- almost no mass below `ell ≈ 1` (it forbids the model from chasing each point),
- a light right tail that discourages `ell` larger than the input range.

In words: "the curve varies on a scale of roughly one-fifth of the input range —
not pointwise, not globally flat." The inverse-gamma is the standard recommended
length-scale prior precisely because it is *zero-avoiding at both ends*: it pushes
mass away from the degenerate tiny- and huge-length-scale regimes that cause the
pathology. (`HalfNormal`/`LogNormal` are alternatives; the key property is that it
be informative, not vague.)

`eta ~ HalfNormal(2)` allows amplitudes up to a few units (the data span ~2.4).
`sigma ~ HalfNormal(0.5)` expects small noise but does not forbid larger.

---

## 3. Prior predictive checks (Step 3)

We draw functions from the GP prior (sample `ell, eta`, build the kernel, draw a
multivariate normal). We want the prior to imply **plausible curves**: smooth, but
varying on the scale of the data — not flat lines, not white noise. With the
InverseGamma length-scale prior the draws have one to a few gentle turns across
the domain, exactly the regime we expect a melt/dose curve to inhabit. If instead
the draws were near-flat (length-scale too large) or jagged (too small), we'd
revise the prior *before* looking at the data.

---

## 4. Inference / NUTS settings (Step 4)

```
draws=500, tune=1000, chains=2, target_accept=0.95, cores=1, random_seed=101
```

- `target_accept=0.95`: GP hyperposteriors have mild curvature; a smaller step
  size keeps divergences at zero.
- `tune=1000`: lets NUTS adapt step size and the (3-dim) mass matrix.
- `chains=2`: enough for `R-hat`; we keep it at two for speed. `cores=1` because
  multiprocessing hangs without a linked BLAS (see §0).
- The test and SBC use lighter settings (`draws=300`/`120`).

---

## 5. Computational diagnostics (Step 5)

Report `R-hat` (≈1.00), `ess_bulk`/`ess_tail` (want ≳ 100 given the light draws),
and **divergences** (should be 0). The decisive plot is the **`(ell, eta)` pair
plot**: with the informative prior it is a compact blob. A diagonal ridge is the
signature of the trade-off pathology — see `notebook_broken.ipynb`, where a
`HalfFlat` length-scale prior reproduces it.

**If diagnostics fail:** (a) divergences → raise `target_accept`, then suspect the
length-scale prior; (b) a ridge in `(ell, eta)` → tighten the length-scale prior
(the cure is modelling, not sampler tuning); (c) low ESS with otherwise healthy
geometry → more draws.

---

## 6. Posterior predictive checks (Step 6)

We reconstruct the latent function on a dense grid using `gp.predict` averaged
over a thinned set of posterior hyperparameter draws, giving a posterior mean and
a 94% credible band. The fit is good when the band hugs the data, **contains the
true curve**, and widens in data-sparse regions. We report the mean absolute error
of the GP mean against `f_true` at the training inputs (`< 0.25` passes).

---

## 7. Model criticism & comparison (Step 7)

Criticism here is (a) recovering `sigma` (the residual sd of the fit should match
the inferred `sigma` and the true `0.18`), and (b) checking residuals look like
white noise. A GP is deliberately a single, flexible model; you *could* compare it
to a parametric logistic via LOO, but the GP's selling point is avoiding that
commitment. (LOO-based GP comparison appears conceptually in the capstone.)

---

## 8. Decision & communication (Step 8)

We translate the curve into a decision-relevant quantity: the input `x` at which
the response crosses a threshold (a melt midpoint / EC50-like value), reported
**with** the band width there. The headline for a collaborator: the response rises
smoothly with a clear transition; the GP recovers it within tolerance; and the
length-scale prior, not the kernel choice, made the fit stable.

---

## Common pitfalls (tied to this project's key pitfall)

- **Vague length-scale prior.** The #1 GP mistake. Produces `ell ↔ eta` ridges,
  divergences, multimodality. *Always* use an informative, zero-avoiding prior.
- **Reading a point estimate of the curve without the band.** The band is the
  product; a GP without its uncertainty is just an overconfident spline.
- **Forgetting the noise term.** Without `sigma`, the GP interpolates every point
  and the length-scale collapses.
- **Extrapolation.** A zero-mean GP reverts to the prior mean far from data;
  bands explode. Communicate this; don't quote extrapolated values.

---

## File index

| File | Role |
|---|---|
| `data/generate_data.py` | DGP; known `f_true`, `sigma`; writes `data/data.npz` |
| `model.py` | `build_model`, `fit`, `predict_curve` (marginal GP) |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow |
| `notebook_broken.ipynb` | seeded length-scale non-identifiability bugs |
| `test_recovery.py` | recovers `sigma` + curve MAE |
| `sbc.py` / `SBC_REPORT.md` | light SBC on `sigma` |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | length-scale prior sweep |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension |
| `lessons.md` | takeaways |
| `summary_onepager.md` | non-technical decision summary |

Environment: see the portfolio-level `requirements.txt` / `environment.yml`
(PyMC 5.28, ArviZ 0.23, numpy, scipy). Do not duplicate per project.
