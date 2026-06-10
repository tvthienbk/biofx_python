# Project 12 — Errors-in-Variables (Measurement-Error Model)

> **New skill:** model noise in a *predictor* via a **latent true predictor** `x*`.
> **Key pitfall:** **attenuation bias** — regressing on the noisy observed predictor
> pulls the slope toward 0; ignoring predictor noise understates the effect.

This is the project guideline. It walks all eight workflow steps, fits both a naive
and an errors-in-variables (EIV) model, flags every assumption, and ends with a
pitfalls section tied to attenuation. Shared dependencies live in the portfolio-root
`environment.yml` / `requirements.txt`.

Files: `data/generate_data.py`, `model.py`, `build_notebook.py` (writes
`notebook.ipynb` + `notebook_broken.ipynb`), `sbc.py` + `SBC_REPORT.md`,
`prior_sensitivity.py` + `PRIOR_SENSITIVITY.md`, `test_recovery.py`,
`BROKEN_BUGS.md`, `rubric.md`, `summary_onepager.md`, `lessons.md`.

---

## Step 1 — Problem & data-generating story

**Scenario.** We want the relationship `y = alpha + beta * x*`, but the instrument
adds noise to **both** variables. We never see the true predictor `x*`; we observe a
noisy `x_obs = x* + Normal(0, tau_x)` and a noisy `y = alpha + beta*x* + Normal(0,
sigma_y)`. Regressing `y` on `x_obs` — the obvious move — **attenuates** the slope
toward 0.

```
x_true_i ~ Normal(mu_x, sd_x)
x_obs_i  = x_true_i + Normal(0, tau_x)      # instrument noise in the predictor
y_i      = alpha + beta * x_true_i + Normal(0, sigma_y)
```

Truth: `alpha=1, beta=2, sigma_y=0.5, tau_x=0.6`. The **attenuation factor**
`var(x*)/(var(x*)+tau_x^2) ≈ 0.74` predicts the naive slope will be ~`2 * 0.74 ≈
1.47`.

**Assumptions made explicit.**
1. The structural relationship is **linear in the true `x*`** (not in `x_obs`).
2. Predictor noise is **additive Gaussian with known SD `tau_x`** (from calibration).
3. Predictor noise and response noise are **independent**.
4. `x*` has a Normal population distribution (a prior for the latent values).

---

## Step 2 — Two models

**Naive.** `y_i ~ Normal(alpha + beta * x_obs_i, sigma_y)` — regress on the noisy
predictor. Simple, and biased: the slope is attenuated.

**Errors-in-variables (EIV).** Treat `x*` as a **latent** variable:
```
mu_x ~ Normal(0,5);  sd_x ~ HalfNormal(5)
x_true_i ~ Normal(mu_x, sd_x)              # population of true predictors
x_obs_i  ~ Normal(x_true_i, tau_x)         # measurement model (tau_x known)
y_i      ~ Normal(alpha + beta * x_true_i, sigma_y)   # structural model in x*
```
With `tau_x` known, the slope is **de-attenuated** and recovers the truth.

**Priors.** `alpha, beta ~ Normal(0, 5)` on the coefficients;
`mu_x ~ Normal(0,5)`, `sd_x ~ HalfNormal(5)` for the latent population;
`sigma_y ~ HalfNormal(2)`. `build_model(data, model="eiv"|"naive", tau_x=...)`
exposes both; `fit` defaults to EIV.

---

## Step 3 — Prior predictive checks

Simulate from the prior and confirm the implied `y` is on a sensible scale before
fitting. (The latent-predictor priors are wide; the check guards against absurd
implied responses.)

---

## Step 4 — Inference

Fit both models. The EIV model carries one latent `x*` per observation — a high-
dimensional posterior — so use `target_accept=0.95` and generous tuning
(`tune=1500`). The naive model is trivial to sample.

---

## Step 5 — Computational diagnostics (and what to do when they fail)

Check **R-hat**, **ESS**, **divergences** for both. Expect the EIV model's
**`sigma_y` to be the weakly-identified parameter** (it trades off against the
latent-predictor scale), with the lowest ESS; the **slope `beta` — our target — is
well-behaved**. If `sigma_y` mixes badly, raise `tune`/`target_accept`; the
coefficient estimates are the ones to judge the fit on.

**When diagnostics fail.** Divergences in the latent block → raise `target_accept`.
A slope stuck near 0 in an EIV fit → suspect a **latent-alignment bug** (the latent
`x*` must share the observations' indexing). Persistent poor `sigma_y` mixing is
expected and does not invalidate the slope.

---

## Step 6 — Posterior predictive checks

Overlay posterior-predictive `y` on the observed data. **Important caveat:** both
models can fit `y` adequately — a good `y`-PPC does **not** vindicate the naive
model's *slope*. The bias is in the coefficient, not the fit to `y`.

---

## Step 7 — Naive vs EIV: attenuation and its correction (criticism)

The defining plot overlays the naive and EIV posterior slopes against the true
`beta=2`. The naive posterior sits near the attenuated `~1.5`; the EIV posterior
covers 2.0. This is the whole project in one figure: ignoring predictor noise
understates the effect by ~25%, and the latent-variable model corrects it.

---

## Step 8 — Decision & communication

Recover `(alpha, beta)` of the EIV model and verify against truth with
`shared.bayes_utils.check_recovery`. For a collaborator: the true effect is
`beta ≈ 2`, but the naive regression reports only ~1.5 because the predictor is
measured with noise; quoting the naive slope understates the effect by ~25%. The
correction requires a calibrated `tau_x`. `summary_onepager.md` makes the
non-technical case.

---

## Common pitfalls (tied to this project's key hazard)

1. **Ignoring predictor noise (attenuation).** *The* pitfall. The naive slope is
   biased toward 0 — and more data does not fix a bias. Use the EIV model; see
   `notebook_broken.ipynb` and `BROKEN_BUGS.md`.
2. **Trusting a good `y`-fit.** PPC adequacy on `y` does not certify the slope.
3. **Latent-variable indexing bugs.** The latent `x*` must align row-for-row with
   `x_obs` and `y`; a misalignment silently collapses the slope.
4. **Assuming `tau_x` is identified from `(x_obs, y)`.** It is not — it must be
   calibrated or estimated from replicate measurements. A wrong `tau_x` over- or
   under-corrects (see `prior_sensitivity.py`).

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

The EIV model is heavier than a plain regression (a latent per observation), but each
step stays within a couple of minutes on CPU.
