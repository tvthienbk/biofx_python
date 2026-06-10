# Project 08 — Many Predictors, Sparse Truth (Regularized Horseshoe)

> **The guideline.** Long-form teaching document for Project 08. It walks the full
> eight-step Bayesian workflow on a high-dimensional regression with a sparse
> truth, with the project's signature skills — **shrinkage priors** and **LOO/WAIC
> comparison** — and its signature pitfall, **double-dipping / selection bias**.
> Read it with `notebook.ipynb`, `notebook_broken.ipynb`, and the per-artifact
> reports (`SBC_REPORT.md`, `PRIOR_SENSITIVITY.md`, `BROKEN_BUGS.md`).

---

## 0. Where this project sits in the portfolio

Earlier projects had a handful of parameters. Project 08 confronts the
**many-predictors** regime: ~20 candidate features, only ~3 truly relevant. Two new
ideas arrive together. First, **shrinkage priors** — specifically the regularized
horseshoe — which perform feature selection *inside a single Bayesian fit* by
crushing irrelevant coefficients toward zero while letting real ones escape.
Second, the **selection-bias / double-dipping** pitfall: the seductively wrong
habit of using the same data to *choose* a predictor and then to *test* it, which
manufactures false confidence. This project also leans hard on the
non-centered-vs-centered parameterization lesson, because the horseshoe's funnel
geometry is the canonical place divergences appear.

Environment (PyMC 5.28, ArviZ 0.23, numpy 2.x, scipy) is shared; see the
top-level `environment.yml` / `requirements.txt`.

---

## 1. Step 1 — Problem & the data-generating story

### 1.1 Scenario

$P=20$ candidate predictors, $N=120$ samples. The response is linear in the
predictors, but the coefficient vector is **sparse**: only 3 entries (indices 2,
7, 13, with values 2.5, -1.8, 1.4) are nonzero; the other 17 are exactly 0.

### 1.2 Generative model

$$
y_i=\beta_0+\sum_{j=1}^{P} X_{ij}\beta_j+\varepsilon_i,\qquad
\varepsilon_i\sim N(0,\sigma),\qquad \#\{j:\beta_j\neq 0\}=K\ll P .
$$

Predictor columns are standardized so coefficient magnitudes are comparable. The
known truth is the full $\beta$ vector (mostly zeros). A good sparse model recovers
the nonzero entries and shrinks the rest to ~0.

### 1.3 Assumptions, stated out loud

1. **Linearity** in the predictors.
2. **Sparsity** — most coefficients are truly zero. This is the prior belief the
   horseshoe encodes; if the truth were dense, a ridge would be more appropriate.
3. **Standardized predictors** — required for the shrinkage scale to apply
   uniformly.
4. **Normal, homoscedastic errors.**
5. **Predictors not perfectly collinear** — severe collinearity makes selection
   among correlated features ill-posed for any method.

---

## 2. Step 2 — Two priors: wide-Normal ridge vs regularized horseshoe

Both models share $y=\beta_0+X\beta+N(0,\sigma)$; only the prior on $\beta$ differs.

### 2.1 Ridge (wide Normal)

$\beta_j\sim N(0,5)$ for every $j$. Every coefficient is equally free; there is no
mechanism to prefer sparsity. Small spurious correlations in finite data get
non-trivial coefficients.

### 2.2 Regularized horseshoe

Each coefficient's scale factorizes into a **global** scale $\tau$ and a **local**
scale $\lambda_j$:

$$
\beta_j = z_j\,\tau\,\tilde\lambda_j,\quad z_j\sim N(0,1),\quad
\lambda_j\sim\text{HalfCauchy}(1),\quad \tau\sim\text{HalfCauchy}(\tau_0),
$$
with the **regularized** local scale
$\tilde\lambda_j=\lambda_j\sqrt{c^2/(c^2+\tau^2\lambda_j^2)}$ (Piironen & Vehtari
2017), where the slab scale $c$ caps how large an escaping coefficient can grow.

- The **global** $\tau$ sets *how many* coefficients survive.
- The **local** $\lambda_j$ has heavy half-Cauchy tails, so each coefficient is
  either crushed toward 0 (most) or allowed to escape (the few real ones).
- The **slab** $c$ stabilizes the escapees, preventing the unregularized
  horseshoe's occasional runaway coefficients.

### 2.3 The non-centered parameterization is mandatory

We sample standardized $z_j\sim N(0,1)$ and *then* multiply by the scale. The
*centered* alternative — $\beta_j\sim N(0,\tau\lambda_j)$ directly — couples each
coefficient to its own scale in a pinched **funnel** that NUTS cannot traverse,
producing a flood of divergences. The non-centered form decouples the geometry
NUTS sees from the scales. This is exactly the seeded bug in the broken notebook,
and it is the single most important practical lesson of the project.

`model.py` exposes `build_model(data, model="horseshoe" | "ridge", centered=...)`
and a matching `fit(...)` with `target_accept=0.95` by default.

---

## 3. Step 3 — Prior predictive checks

We draw $\beta$ from the horseshoe prior and confirm its shape: a sharp **spike**
of mass near zero with **heavy tails** — the "spike and slab"-like structure that
encodes "most coefficients are zero, a few are large." If the prior predictive
showed a broad Normal blob instead, we would have mis-specified the shrinkage.

---

## 4. Step 4 — Inference (NUTS settings)

`draws=1000, tune=1000, chains=4, target_accept=0.95`, for both models. The high
`target_accept` shrinks the step size, which the horseshoe needs even when
non-centered (the funnel is tamed, not eliminated). If divergences persist, the
remedies are: confirm the non-centered parameterization, raise `target_accept` to
0.99, and consider reparameterizing $\tau$. We keep both idatas for Step 7.

---

## 5. Step 5 — Computational diagnostics

For the non-centered horseshoe, expect few or zero divergences and $\hat R\approx1$.
The key project-specific diagnostic: **if divergences flood in, suspect a centered
parameterization** (the classic funnel). `az.plot_energy` (a mismatch between the
marginal and energy-transition distributions flags poor exploration) and the raw
divergence count are the tools. The broken notebook is built around this exact
failure so students learn to read it.

---

## 6. Step 6 — Posterior predictive & sparsity recovery

The headline visual is a **coefficient forest** of all 20 $\beta_j$ under each
prior, with the true nonzero values marked:

- The **ridge** scatters the 17 noise coefficients away from zero with non-trivial
  intervals — it cannot tell signal from noise.
- The **horseshoe** collapses the 17 noise coefficients onto zero and cleanly
  isolates the 3 real signals at indices 2, 7, 13.

We also run `az.plot_ppc` to confirm the horseshoe reproduces the response
distribution.

---

## 7. Step 7 — Model comparison (LOO)

`az.compare({...}, ic="loo")`. The instructive result is usually *not* a huge
predictive gap — with $N=120$ and only 3 signals, both models can predict the
response. The horseshoe's advantage shows up in **`p_loo`**: it achieves the same
(or better) fit using **far fewer effective parameters**, because it has switched
off 17 coefficients. This is the model-comparison lesson of shrinkage: the payoff
is *parsimony at equal fit*, which LOO's complexity penalty rewards and which
generalizes better out of sample.

We also verify recovery — the nonzero coefficients land near 2.5, -1.8, 1.4 — and
quantify sparsity via the largest $|\beta_j|$ among the true-zeros (much smaller
under the horseshoe than the ridge).

---

## 8. Step 8 — Decision, communication & the double-dipping warning

### 8.1 The pitfall: double-dipping / selection bias

The tempting WRONG workflow: fit the model, pick the predictor with the largest
coefficient, then **re-fit a simple regression on only that predictor** and report
its now-narrow interval / tiny p-value as "significance." This uses the data
**twice** — once to *select* the predictor, once to *test* it — and grossly
overstates confidence. The selected coefficient was chosen *because* it looked
large in this sample, so re-testing it on the same sample is circular. This is the
second seeded bug in the broken notebook.

### 8.2 The Bayesian remedy

Let the **shrinkage prior do selection inside one joint fit**, and report the full
posterior over *all* coefficients — including the uncertainty about which are
nonzero. Never re-fit on a data-selected subset. We report, for each predictor, the
posterior probability that $|\beta_j|$ exceeds a small threshold, which honestly
conveys both the selection and its uncertainty.

`summary_onepager.md` carries the non-technical version.

---

## 9. Common pitfalls (the project's key traps)

1. **Double-dipping / selection bias.** THE pitfall. Selecting on the data and
   testing on the same data fakes significance. Use a joint shrinkage fit instead.
2. **Centered horseshoe → divergences.** The funnel geometry is unsamplable
   centered. Always use the non-centered parameterization.
3. **Interpreting a ridge as feature selection.** A wide Normal does not produce
   sparsity; small noise coefficients stay non-zero.
4. **Cranking $\tau_0$ to zero.** Over-aggressive global shrinkage also kills
   genuine weak signals; set $\tau_0$ from a prior guess at the number of relevant
   predictors.
5. **Reading LOO as a big predictive win.** The horseshoe's gain is often
   parsimony (`p_loo`), not raw `elpd`; interpret accordingly.

---

## 10. File map

| File | Role |
|------|------|
| `data/generate_data.py` | sparse linear DGP (20 predictors, 3 nonzero), known truth |
| `model.py` | `build_model`/`fit` for `horseshoe` (non-centered) and `ridge`; `centered` flag for the bug |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow with `az.compare` and honest reporting |
| `notebook_broken.ipynb` | centered-funnel + double-dipping debugging exercise |
| `test_recovery.py` | recovery of nonzero coefficients + sparsity + divergence check |
| `sbc.py` / `SBC_REPORT.md` | SBC on a couple of coefficients |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | global-scale $\tau_0$ comparison |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension prompt |
| `lessons.md` | narrative lessons report |
| `summary_onepager.md` | non-technical decision summary |
