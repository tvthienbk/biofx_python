# Project 18 — Dynamics & Drift (Local-Level State-Space Model)

> **Workflow focus:** inferring a latent, time-evolving state from noisy
> observations. **New skill:** temporal dependence and latent states.
> **Key pitfall:** the **process** noise and the **observation** noise are
> confounded — both make the observed series wiggly — so separating them needs
> informative priors and enough data.

---

## 0. Compute requirements (read first)

One of the four "heavy" projects (#17-20), though lighter than the GP.

- The latent level is a `T`-dimensional random walk, so the model has `T + few`
  parameters. We keep `T = 100` for the main fit and `T = 40` for SBC.
- **BLAS is not linked** in this environment; PyMC's multiprocess sampler can
  hang, so we sample with `cores=1` (set inside `model.fit`). Do not remove it.
- Expected serial CPU wall-clock:
  - `python3 model.py` (400 draws): ~30-60 s
  - `python3 -m pytest test_recovery.py -q` (400 draws): ~40-70 s
  - `python3 sbc.py` (20 refits, T=40): ~90-150 s
  - `python3 prior_sensitivity.py` (3 fits): ~90-150 s
- The notebook uses `draws=600, tune=1000` for the showcase fit plus an AR(1)
  comparison (~90 s total). It is **validated statically**, not executed.

Reduce `draws`/`tune`/`T`/`N_SIMS` if you need it faster.

---

## 1. Problem & data-generating story (Step 1)

We observe a time series `y_t` (a sensor reading, a growth measurement) that is a
noisy view of an unobserved **level** that itself drifts over time. The
**local-level model** (a.k.a. random-walk-plus-noise) is the canonical structure:

```
level_t = level_{t-1} + w_t,   w_t ~ N(0, sigma_level)     # PROCESS noise
y_t     = level_t       + e_t,  e_t ~ N(0, sigma_obs)       # OBSERVATION noise
```

The latent level is a Gaussian random walk; observations add measurement error.

**Data-generating process** (`data/generate_data.py`): `T = 100`,
`sigma_level = 0.30`, `sigma_obs = 0.60`, `level0 = 5.0`. **Recoverable truths:**
both variances and the latent trajectory.

**Assumptions, made explicit:**
1. The level evolves as a pure random walk — **no mean reversion** (an AR(1) with
   `rho < 1` would mean-revert; we compare against it in Step 7).
2. Both noises are Gaussian and **homoscedastic** (constant over time).
3. Observations are conditionally independent given the level.
4. A single latent level (no trend/seasonal components — those are extensions).

---

## 2. Model specification with justified priors (Step 2)

We implement the random walk **non-centred**: standardised innovations
`z_t ~ N(0,1)` scaled by `sigma_level` and cumulatively summed onto `level0`:

```
sigma_level ~ HalfNormal(0.5)        # process noise: expect modest drift
sigma_obs   ~ HalfNormal(1.0)        # observation noise: can be larger
level0      ~ Normal(mean(y), 5)
z_t         ~ N(0, 1)                # standardised innovations
level_t     = level0 + cumsum(z * sigma_level)
y_t         ~ Normal(level_t, sigma_obs)
```

### Why non-centred?

A *centred* random walk (`level_t ~ N(level_{t-1}, sigma_level)`) couples the
latent states tightly to `sigma_level`. As `sigma_level` shrinks, the posterior
develops a **funnel** (the classic Neal's funnel), and NUTS diverges. The
non-centred form decouples the innovations from their scale, giving NUTS a flat
geometry to explore. The broken notebook deliberately uses the centred form to
show the funnel.

### Why these priors (and not vague ones)?

`sigma_level` and `sigma_obs` are **confounded**: a given amount of observed
wiggle can be attributed to a wandering level (large `sigma_level`) **or** to a
steady level seen through noisy measurement (large `sigma_obs`). The likelihood
alone only weakly separates them. If both priors are vague, the posterior smears
along a ridge where `sigma_level` and `sigma_obs` trade off, and the inferred
level either **overfits** the noise (chases every point) or **oversmooths** it
(flattens out). Mildly informative HalfNormal priors — encoding "drift is modest,
measurement noise may be larger" — break the symmetry enough for the data to do
the rest.

---

## 3. Prior predictive checks (Step 3)

We simulate series implied by the priors. We want plausible drifting series of
roughly the observed magnitude — not explosive random walks (process prior too
wide) nor flat lines (too tight). This catches a mis-scaled `sigma_level` prior
before fitting.

---

## 4. Inference / NUTS settings (Step 4)

```
draws=600, tune=1000, chains=2, target_accept=0.95, cores=1, random_seed=101
```

The non-centred parameterisation plus a raised `target_accept` keep the
random-walk geometry divergence-free. `cores=1` avoids the multiprocess hang.

---

## 5. Computational diagnostics (Step 5)

Report `R-hat`, ESS, and divergences (want 0). The decisive plot is the **joint
posterior of `(sigma_level, sigma_obs)`**: a strong negative correlation is the
confounding signature. With our priors and `T = 100` it is present but mild, and
both variances bracket their truths.

**If diagnostics fail:** (a) divergences → ensure the **non-centred** form and
raise `target_accept` (the centred form funnels); (b) a strong `(sigma_level,
sigma_obs)` ridge with both posteriors huge → priors too vague, tighten them or
get more data; (c) low ESS on the level → more draws.

---

## 6. Posterior predictive checks & latent trajectory (Step 6)

We overlay the inferred latent level (posterior mean + 94% band) on the truth and
the data. A good fit tracks the true level inside a band **tighter than the
observation scatter** — the model "sees through" the noise. We report the
latent-level recovery MAE (`< 0.5` passes).

---

## 7. Model criticism & comparison (Step 7)

We compare the local-level model against a stationary **AR(1)** model via LOO
(`az.compare`). AR(1) assumes mean reversion; the local-level model assumes a
persistent random-walk drift. When the level genuinely drifts (as here), the
local-level model should be competitive or preferred. Both models carry
`log_likelihood` so LOO is well-defined. (Note: the two models are fit on slightly
different targets — the AR(1) conditions on the previous observation — so the LOO
comparison is indicative of fit-per-observation, not a strict nested test; we
discuss this caveat in `lessons.md`.)

---

## 8. Decision & communication (Step 8)

Translate into a decision: the current level estimate (last time point) with its
credible interval, and the probability the level rose over the final stretch — the
kind of statement a process engineer acts on. The headline: report the **level**
and its **trend**, not the raw noisy readings.

---

## Common pitfalls (tied to this project's key pitfall)

- **Vague variance priors.** The #1 state-space mistake: `sigma_level` and
  `sigma_obs` trade off, the level over/under-smooths. Use informative priors.
- **Centred random walk.** Funnels and diverges as `sigma_level` shrinks. Use the
  non-centred form.
- **Reading the level point estimate without its band.** The band is the product.
- **Assuming a random walk when the series mean-reverts.** Compare against AR(1).

---

## File index

| File | Role |
|---|---|
| `data/generate_data.py` | DGP; known variances + latent level; writes `data.npz` |
| `model.py` | local-level (`build_model`/`fit`) + AR(1) (`build_ar1_model`/`fit_ar1`) |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow incl. AR(1) LOO comparison |
| `notebook_broken.ipynb` | seeded vague-prior + centred-RW confounding bugs |
| `test_recovery.py` | recovers both variances + latent level |
| `sbc.py` / `SBC_REPORT.md` | light SBC on `sigma_obs` |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | process/obs prior sweep |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension |
| `lessons.md` | takeaways |
| `summary_onepager.md` | non-technical decision summary |

Environment: portfolio-level `requirements.txt` / `environment.yml` (PyMC 5.28,
ArviZ 0.23, numpy, scipy).
