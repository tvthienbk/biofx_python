# Prior Sensitivity — Project 12: Errors-in-Variables (assumed tau_x)

**Model:** errors-in-variables; we vary the **assumed measurement-error SD** `tau_x`.
**Script:** `prior_sensitivity.py`

---

## 1. The question

The EIV model treats `tau_x` — the predictor's instrument-noise SD — as **known**,
typically from a calibration experiment. This is the model's load-bearing
assumption. `tau_x` controls the **de-attenuation**: the more predictor noise you
assume, the more you inflate the slope to compensate. So the natural question is:
how sensitive is the recovered slope to getting `tau_x` wrong?

We refit under a range of assumed `tau_x`. The `tau_x = 0` case is exactly the naive
regression (no predictor noise), giving the attenuated floor; the true `tau_x = 0.6`
is the reference.

---

## 2. Procedure

`python3 prior_sensitivity.py` fits the EIV model (chains=2, tune=1200,
`target_accept=0.95`) at each assumed `tau_x` and reports the slope posterior. Truth:
`beta = 2.0`, `tau_x = 0.6`.

---

## 3. Results

```
Data: n=120; true beta=2.0, true tau_x=0.6

 assumed tau_x   model  beta mean          beta 94% HDI
           0.0   naive      1.513  [ 1.340,  1.686]
           0.3     eiv      1.614  [ 1.443,  1.799]
           0.6     eiv      2.054  [ 1.794,  2.334]
           0.9     eiv      2.218  [ 1.884,  2.508]
```

| assumed `tau_x` | model | slope `beta` | 94% HDI |
|---|---|---|---|
| 0.0 | naive | 1.513 | [1.340, 1.686] |
| 0.3 | eiv | 1.614 | [1.443, 1.799] |
| **0.6 (true)** | eiv | **2.054** | [1.794, 2.334] |
| 0.9 | eiv | 2.218 | [1.884, 2.508] |

---

## 4. Interpretation

This is a textbook **de-attenuation curve**. Assuming **no** predictor noise
(`tau_x = 0`, the naive fit) leaves the slope attenuated at ~1.51 — a 25%
underestimate of the true 2.0. As the assumed `tau_x` rises, the model corrects
upward: at the **true** `tau_x = 0.6` it recovers `beta ≈ 2.05` (HDI covers 2.0);
**over-stating** `tau_x` (0.9) **over-corrects** to ~2.22.

The lesson is sharp and two-sided:

- **Ignoring predictor noise is not conservative — it is biased.** The naive slope
  is systematically too small, and no amount of data fixes it (attenuation is a
  bias, not variance).
- **But the correction is only as good as your `tau_x`.** The EIV model does not
  estimate `tau_x` from these data (it is not identified from `(x_obs, y)` alone
  without extra information); it *assumes* it. A wrong `tau_x` trades one bias for
  another.

**The rule.** Calibrate `tau_x` from a dedicated measurement (replicate readings of
the instrument), feed it in as known, and **report the slope's sensitivity to
`tau_x`** — exactly this curve. If `tau_x` is genuinely unknown, you need auxiliary
data (e.g. replicate measurements per unit) to identify it, not a vague prior.

---

## 5. What to report to a collaborator

> "The naive slope of ~1.5 understates the real effect by about a quarter because
> the predictor is measured with noise. Correcting for that noise gives a slope near
> 2.0 — but the correction depends on knowing how noisy the instrument is. We used
> the calibrated value; if the instrument noise were 50% larger, the slope would rise
> to ~2.2. The instrument calibration is therefore part of the result."
