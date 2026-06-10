# Project 11 — Varying Slopes (Correlated Random Effects, LKJ)

> **New skill:** correlated random effects — varying intercepts **and** slopes with
> an LKJ prior on their correlation (`pm.LKJCholeskyCov`).
> **Key pitfall:** ignoring the intercept-slope correlation (modeling the two
> effects as independent) mis-fits the data and gives wrong predictive covariance
> for new groups.

This is the project guideline. It walks all eight workflow steps on a varying-slopes
model, flags every assumption, and ends with a pitfalls section tied to the missed
correlation. Shared dependencies live in the portfolio-root `environment.yml` /
`requirements.txt`.

Files: `data/generate_data.py`, `model.py`, `build_notebook.py` (writes
`notebook.ipynb` + `notebook_broken.ipynb`), `sbc.py` + `SBC_REPORT.md`,
`prior_sensitivity.py` + `PRIOR_SENSITIVITY.md`, `test_recovery.py`,
`BROKEN_BUGS.md`, `rubric.md`, `summary_onepager.md`, `lessons.md`.

---

## Step 1 — Problem & data-generating story

**Scenario.** A dose-response experiment: a continuous readout `y` responds to a
standardized dose `x`, measured on `G = 8` **cell lines**, ~`n = 10` points each.
Each line has its own **baseline** (intercept `alpha_g`) and **dose sensitivity**
(slope `beta_g`), and — the crux — these are **correlated** across lines: a higher
baseline tends to come with a steeper slope.

Cell lines are **exchangeable**: their effect pairs are draws from a common
bivariate distribution.

```
[alpha_g, beta_g] ~ MVNormal([mu_a, mu_b], Sigma)
Sigma = diag(sd) @ Corr @ diag(sd),   Corr = [[1, rho], [rho, 1]]
y_ij = alpha_g + beta_g * x_ij + Normal(0, sigma)
```

Truth: `mu_a=2, mu_b=1, sd_a=0.8, sd_b=0.5, rho=0.6, sigma=0.5`. We keep the lines
few so the correlation is learnable but genuinely uncertain.

**Assumptions made explicit.**
1. **Exchangeability** of cell lines.
2. **Bivariate Normal** effect pairs (a Normal population of `(alpha, beta)`).
3. **Common observation noise** `sigma` across lines.
4. The intercept-slope **correlation is a parameter to estimate**, not assume.

---

## Step 2 — Model specification (LKJ, non-centered)

```
mu = [mu_a, mu_b] ~ Normal(0, 5)
sigma ~ HalfNormal(1)
chol, corr, sds ~ LKJCholeskyCov(n=2, eta=2, sd_dist=HalfNormal(1))
z ~ Normal(0, 1)  shape (2, G)
effects = mu + (chol @ z).T          # NON-CENTERED, shape (G, 2)
rho = corr[0,1];  sd_a = sds[0];  sd_b = sds[1]
y_ij = effects[g,0] + effects[g,1]*x_ij + Normal(0, sigma)
```

**Why LKJ.** The 2x2 random-effect covariance has three free numbers: two SDs and a
correlation. `pm.LKJCholeskyCov` places an **LKJ** prior on the correlation matrix
(via its Cholesky factor) and a `HalfNormal` on the SDs, returning the factor, the
correlation, and the SDs together. This is the standard, numerically stable way to
prior a covariance.

**Why `eta = 2`.** The LKJ shape parameter controls the prior on the correlation:
`eta = 1` is uniform over all valid correlations; `eta > 1` gently favors weaker
correlations (a mild regularizer); large `eta` is skeptical of any correlation. With
only 8 lines we choose `eta = 2`: enough pull to avoid `rho = ±1` on noise, not so
much that we pre-decide `rho = 0`. The prior-sensitivity analysis shows `eta` has
real influence here.

**Why non-centered.** The funnel is multivariate now, but the cure is the same: draw
standard-normal `z` and reconstruct `effects = mu + (L @ z).T` using the Cholesky
factor `L`. This decouples the geometry and keeps the model divergence-free.
`build_model(data, correlated=True/False, eta=...)` exposes the LKJ model and a
diagonal (independent) model for comparison; `fit` defaults to the correlated,
non-centered model.

---

## Step 3 — Prior predictive checks

Simulate from the prior and confirm the implied dose-response lines are on a sensible
scale (not absurdly steep or flat), and the implied `y` covers the observed scale. A
mis-scaled SD prior would show here as implausible readouts.

---

## Step 4 — Inference (NUTS)

`draws=800, tune=1000, chains=4, target_accept=0.9`, fixed seed. The LKJ +
non-centered model needs the mild `target_accept` bump; 4 chains for reliable
split-R-hat. `fit` attaches prior + posterior predictive and `log_likelihood` for
LOO-based comparison against the independent model.

---

## Step 5 — Computational diagnostics (and what to do when they fail)

Read **R-hat** (≈1.00), **ESS**, **divergences** (≈0 with non-centering), and the
**energy plot**. Expect `rho` to have the **widest interval** — it is the hardest
quantity to identify from 8 lines, and a wide `rho` posterior is honest, not a bug.

**When diagnostics fail.** Divergences → confirm non-centering and raise
`target_accept` to 0.95. A degenerate covariance (one SD near 0) can also cause
trouble — check the SD priors. Persistent wide `rho` is expected with few groups;
the fix is more groups, not more tuning.

---

## Step 6 — Posterior predictive checks

Overlay posterior-predictive `y` on the observed data with `az.plot_ppc`; a good fit
envelopes the observed spread.

---

## Step 7 — Recovering the correlation (model criticism)

The defining plot: the posterior for `rho` against the true 0.6, plus a scatter of
the per-line posterior `(alpha_g, beta_g)` showing the positive tilt. This tilt is
the structure the LKJ model captures and an **independent** model assumes away. The
right comparison is `az.compare` (LOO) of the correlated vs diagonal model — the
correlated model should win, quantifying the cost of ignoring `rho`.

---

## Step 8 — Decision & communication

Recover `mu_a, mu_b, sd_a, sd_b, rho, sigma` and verify against truth with
`shared.bayes_utils.check_recovery`. For a collaborator:

- Dose raises the readout on average (`mu_b ≈ 1`).
- Lines differ in baseline and sensitivity, and **higher-baseline lines respond more
  steeply** (`rho > 0`).
- Predicting a new line's dose response must respect that correlation.

`summary_onepager.md` turns this into the actionable point: use the correlation when
predicting new lines; the exact `rho` needs more lines to pin down.

---

## Common pitfalls (tied to this project's key hazard)

1. **Modeling intercept and slope as independent.** *The* pitfall. It hard-codes
   `rho = 0`, mis-fits the data, and gives wrong predictive covariance for new
   groups. Use LKJ; see `notebook_broken.ipynb` and `BROKEN_BUGS.md`.
2. **The centered-parameterization funnel.** Multivariate now, but the same cure:
   non-center via the Cholesky factor.
3. **Over-reading `rho` from few groups.** With 8 lines `rho` is loosely identified
   and prior-sensitive (LKJ `eta`); report direction and uncertainty, not a precise
   value.
4. **Wiring `LKJCholeskyCov` outputs wrong.** It returns `(chol, corr, sds)`; use
   `chol` for the non-centered reconstruction and `corr[0,1]` for `rho`. Mixing them
   is a silent bug.

---

## How to run

```bash
python3 data/generate_data.py
python3 model.py
python3 build_notebook.py
python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb
python3 -m pytest test_recovery.py -q
python3 sbc.py
python3 prior_sensitivity.py
```

The LKJ model is slower than the scalar hierarchical models (no BLAS in this
environment), but each step stays well within a couple of minutes on CPU.
