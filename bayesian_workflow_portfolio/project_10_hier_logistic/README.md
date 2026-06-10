# Project 10 — Varying Intercepts (Hierarchical Logistic)

> **New skill:** group-level structure inside a GLM — a hierarchical logistic
> regression with group-varying intercepts.
> **Key pitfall:** with few groups it is easy to **pool too aggressively**,
> collapsing real group differences toward a single intercept. The pooling dial is
> the between-group SD `tau` and its prior; a too-tight prior over-pools.

This is the project guideline. It walks all eight workflow steps on a hierarchical
logistic model, flags every assumption, and ends with a pitfalls section tied to
over-pooling. Shared dependencies live in the portfolio-root `environment.yml` /
`requirements.txt`.

Files: `data/generate_data.py`, `model.py`, `build_notebook.py` (writes
`notebook.ipynb` + `notebook_broken.ipynb`), `sbc.py` + `SBC_REPORT.md`,
`prior_sensitivity.py` + `PRIOR_SENSITIVITY.md`, `test_recovery.py`,
`BROKEN_BUGS.md`, `rubric.md`, `summary_onepager.md`, `lessons.md`.

---

## Step 1 — Problem & data-generating story

**Scenario.** A binary binding assay ("does this protein bind the ligand?") is run
across `G = 10` protein **families**, ~`n = 12` assays per family. Each family has
its own baseline binding propensity — a group-varying intercept on the log-odds
scale — and a global covariate `x` (a standardized physicochemical score) shifts
the binding odds for every assay.

Families are **exchangeable**: their intercepts come from a common population. The
data-generating model:

```
alpha_g ~ Normal(mu_true, tau_true)            # family intercepts (log-odds)
logit(p_i) = alpha_{g[i]} + beta_true * x_i
y_i ~ Bernoulli(p_i)
```

with truth `mu_true = -0.3`, `tau_true = 0.9`, `beta_true = 1.2`. We use few
observations per family so group structure matters and over-pooling is a real risk.

**Assumptions made explicit.**
1. **Exchangeability** of families (no family special a priori).
2. **Normal population** of intercepts on the log-odds scale.
3. **A single global slope** `beta` shared by all families (no varying slopes — that
   is Project 11).
4. **Bernoulli** outcomes; independence given the family intercept and covariate.

---

## Step 2 — Model specification with justified priors

```
mu    ~ Normal(0, 1.5)      # population-mean intercept (log-odds)
tau   ~ HalfNormal(1)       # between-family SD
beta  ~ Normal(0, 1.5)      # global slope
alpha_g = mu + tau * z_g,   z_g ~ Normal(0,1)      # NON-CENTERED
logit(p_i) = alpha_{g[i]} + beta * x_i
y_i ~ Bernoulli(p_i)
```

**Why these priors — and why the scale matters.** These are priors on the
**log-odds** scale. `Normal(0, 1.5)` is weakly informative there: an SD of 1.5
already spans binding probabilities from ~0.05 to ~0.95. A naive "vague"
`Normal(0, 10)` would be the *opposite* of uninformative — it puts almost all mass
on probabilities of essentially 0 or 1. The prior predictive (Step 3) is where we
verify the implied probability scale is sane.

`tau ~ HalfNormal(1)` is the **pooling dial**. It must be weakly informative: tight
enough to avoid inventing spurious spread from 10 families, loose enough not to
force them all to share one intercept. An over-tight `tau` prior (e.g.
`HalfNormal(0.05)`) is *the* way to cause over-pooling — see the broken notebook.

**Non-centered** (`alpha_g = mu + tau z_g`) because the funnel is a property of the
prior geometry, not the likelihood: it reappears unchanged from Project 09 and the
same reparameterization fixes it. `model.build_model(data, parameterization=...)`
exposes both forms; `fit` defaults to non-centered.

---

## Step 3 — Prior predictive checks

We simulate datasets from the prior and check the implied **dataset binding rates**
spread sensibly across [0,1] rather than piling at 0 or 1. This is the single most
important guard against a mis-scaled log-odds prior. If the implied rates were
bimodal at the extremes, we would tighten the priors before inference.

---

## Step 4 — Inference (NUTS, non-centered)

`draws=800, tune=1000, chains=4, target_accept=0.9`, fixed seed. Four chains for
reliable split-R-hat; a mild `target_accept` bump for hierarchical geometry. `fit`
attaches prior + posterior predictive and `log_likelihood` for LOO.

---

## Step 5 — Computational diagnostics (and what to do when they fail)

Read, in order: **R-hat** (≈1.00), **ESS** (watch `tau`'s tail ESS),
**divergences** (must be ~0; non-centered gives 0), and the **energy plot**
(`az.plot_energy`) — a marginal/transition mismatch is the funnel fingerprint and is
worth checking even when R-hat looks fine.

**When diagnostics fail.** Divergences → non-center (the cure) and/or raise
`target_accept`. Over-pooled, near-zero `tau` with low ESS → check the `tau` prior is
not too tight (the over-pooling bug). Persistent high R-hat → suspect
non-identifiability.

---

## Step 6 — Posterior predictive checks

Overlay posterior-predictive datasets on the observed outcomes with `az.plot_ppc`.
A good fit reproduces the spread of per-family binding rates. Systematic
under-dispersion of family rates would flag over-pooling (too-small `tau`).

---

## Step 7 — Varying intercepts & shrinkage (model criticism)

The central plot compares each family's no-pooling empirical log-odds to its
partial-pooling posterior intercept `alpha_g`, with `mu_hat` as reference. Families
are pulled toward `mu_hat`; the noisiest/most extreme are pulled most. This is the
GLM version of Project 09's shrinkage.

**The pitfall lives here.** If `tau` (via its prior) is too small, all `alpha_g`
collapse onto `mu_hat` — the model erases real family differences. The broken
notebook shows exactly this collapse (intercept spread ~0.05 vs the healthy ~0.9).

---

## Step 8 — Decision & communication

Recover `mu`, `tau`, `beta` and check against truth with
`shared.bayes_utils.check_recovery`. For a collaborator:

- `beta > 0`, robustly — higher score raises binding odds.
- Families differ in baseline (`tau ≈ 0.9`), but with ~12 assays each, report the
  **shrunken** per-family intercepts, not raw rates.

`summary_onepager.md` translates this into an action: use the score predictor, trust
the shrunken family baselines, and add families (not assays) to sharpen family-level
conclusions.

---

## Common pitfalls (tied to this project's key hazard)

1. **Over-pooling via a too-tight `tau` prior.** *The* pitfall. `HalfNormal(0.05)`
   collapses family intercepts onto `mu_hat`. Use a weakly-informative scale prior;
   see `notebook_broken.ipynb` and `BROKEN_BUGS.md`.
2. **"Vague" priors on the log-odds scale.** `Normal(0,10)` on an intercept implies
   probabilities of 0 or 1 — check the prior predictive on the probability scale.
3. **The centered-parameterization funnel.** Identical to Project 09; non-center.
4. **Over-reading the group-level scale.** With 10 families, `tau` is prior-sensitive
   and loosely identified — report it with a caveat; report `beta` with confidence.
5. **Shipping raw per-family rates.** The shrunken estimates are better, especially
   for small/noisy families.

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

All steps are light (well under a couple of minutes each on CPU).
