# Lessons — Project 12: Errors-in-Variables

This report records what Project 12 teaches, the failure modes met while building it,
and how measurement-error modeling generalizes. The headline skill is **modeling
noise in a predictor via a latent true variable**; the headline hazard is
**attenuation bias** when that noise is ignored.

---

## 1. What this project is really about

Projects 09–11 built grouping structure (hierarchies). Project 12 introduces a
different kind of latent variable: a **per-observation true predictor** `x*` that we
never observe directly. The conceptual jump is that the *predictor*, not just the
response, carries noise — and that noise biases the regression in a specific,
predictable way.

The two models:

```
naive:  y_i ~ Normal(alpha + beta * x_obs_i, sigma_y)              # biased

eiv:    x_true_i ~ Normal(mu_x, sd_x)                              # latent population
        x_obs_i  ~ Normal(x_true_i, tau_x)                        # measurement model
        y_i      ~ Normal(alpha + beta * x_true_i, sigma_y)       # structural model
```

---

## 2. Takeaways

### 2.1 Attenuation is a bias, not noise — data does not cure it

The single most important lesson. Classical measurement error in a predictor
multiplies the slope by the reliability ratio `var(x*)/(var(x*)+tau_x^2) ≈ 0.74`,
pulling the true 2.0 down to ~1.5. This is a *systematic* error: more data tightens
the interval around the *wrong* value, breeding false confidence. You cannot
out-sample a bias; you must model it.

### 2.2 A good fit to `y` does not vindicate the slope

Both the naive and EIV models can produce a perfectly adequate posterior-predictive
fit to the observed `y`. The bias lives in the *coefficient*, not in the fit. This is
a sobering reminder that PPC adequacy is necessary, not sufficient — a model can
predict `y` well and still get the causal slope wrong.

### 2.3 The fix is a latent variable plus a measurement model

The EIV model adds (a) a population prior for the unobserved `x*`, (b) a measurement
model tying `x_obs` to `x*` with the calibrated noise `tau_x`, and (c) the structural
model in terms of `x*`. With `tau_x` known, the slope de-attenuates to ~2.0. The
latent `x*` is estimated for every observation — a high-dimensional nuisance — but
the coefficients are what we report.

### 2.4 The correction is only as good as `tau_x`

`tau_x` is **assumed known**, and it is the model's load-bearing input. The prior-
sensitivity curve shows the slope walking from 1.5 (tau_x=0, naive) through 2.05
(true tau_x=0.6) to 2.22 (over-stated tau_x=0.9). Get `tau_x` wrong and you trade
attenuation for over-correction. `tau_x` is *not* identified from `(x_obs, y)` alone —
it must come from calibration or replicate measurements.

---

## 3. Surprises & failures encountered while building

### 3.1 `sigma_y` is weakly identified and mixes poorly

The honest surprise: the EIV model's `sigma_y` (response noise) is the hardest
parameter to sample — low ESS, occasionally `r_hat > 1.05` — because it trades off
against the latent-predictor scale. The *slope* `beta`, our target, is well-behaved.
The response was to (a) target the recovery test and SBC at `(alpha, beta)` rather
than `sigma_y`, and (b) raise `tune` and `target_accept`. The lesson: in a latent-
variable model, identify which parameters are the inferential target and which are
nuisances that may mix poorly, and judge the fit on the former.

### 3.2 The indexing bug is silent

Reversing the latent vector (`x_true[::-1]`) in the structural model — Bug 2 — raises
no error: shapes match, the model samples, and the slope just collapses to ~0. There
is no diagnostic that screams "misalignment"; the only defense is knowing that the
latent must share the observations' indexing and sanity-checking it. Latent variables
introduce a new bug class (alignment) that scalar models never have.

### 3.3 The latent vector makes everything slow

With one latent per observation, the EIV posterior is high-dimensional, and (with no
BLAS in this environment) refits are slow. SBC had to drop to 18 light simulations at
N=60 to fit the time budget. The general lesson: measurement-error and latent-
variable models scale their cost with the data size, so SBC and prior sweeps must be
kept deliberately small.

### 3.4 tau_x = 0 *is* the naive model

A small elegance: the prior-sensitivity sweep does not need a separate naive code
path conceptually — assuming zero predictor noise (`tau_x = 0`) collapses the EIV
model to the naive regression. This makes the de-attenuation curve a single
continuous story from "ignore the noise" to "over-correct".

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Latent true predictor + measurement model | Any setting with noisy inputs: calibration, proxy variables, jittered covariates. |
| Attenuation bias awareness | Every regression on a measured (not exact) predictor. |
| "Good `y`-fit ≠ correct coefficient" | All causal/structural modeling; instrumental variables. |
| Known vs identified nuisance parameters | Any model with assumed-known scales (measurement SDs, offsets). |
| Latent-vector alignment hygiene | Every per-observation latent model (factor models, state-space, this). |

Project 12 closes the hierarchical/latent-variable block of the portfolio by shifting
from *grouping* latent structure (P09–11) to *measurement* latent structure. The
shared thread is that the right model often requires representing something you did
not directly observe.

---

## 5. Concrete next experiments (for the reader)

- Add replicate measurements `x_obs1`, `x_obs2` per unit and estimate `tau_x` jointly
  — now the noise SD is identified and you need not assume it (the rubric extension).
- Sweep the true `tau_x` in `generate_data.py` and watch the naive slope's
  attenuation deepen as the reliability ratio falls.
- Deliberately misalign the latent (`x_true[::-1]`) and confirm `beta` collapses — feel
  how silent the bug is.
- Compare naive vs EIV with `az.compare` (LOO) and discuss why LOO on `y` does not
  straightforwardly reward the less-biased slope.
