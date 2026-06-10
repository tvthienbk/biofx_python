# Grading Rubric — Project 12: Errors-in-Variables

Total: **100 points** across the eight workflow steps plus the measurement-error
skill. An open-ended extension follows.

| # | Workflow step | Criteria | Points |
|---|---|---|---|
| 1 | Problem & data story | Explains noise in BOTH variables; states the attenuation factor; documented DGP, fixed seed, known truth. | 10 |
| 2 | Model & priors | Both naive and EIV models; **justifies** the latent-predictor population prior and treating `tau_x` as known; correct measurement + structural models. | 14 |
| 3 | Prior predictive | Checks implied `y` is on a sensible scale. | 6 |
| 4 | Inference | Fits both models; sensible NUTS settings; `target_accept` raised for the latent-heavy EIV model. | 10 |
| 5 | Diagnostics | R-hat, ESS, divergences; notes `sigma_y` is the weakly-identified parameter while the slope `beta` is well-behaved. | 12 |
| 6 | Posterior predictive | PPC; notes a good fit to `y` does **not** vindicate the naive slope. | 8 |
| 7 | Naive vs EIV / criticism | Overlays the two slope posteriors vs truth; explains attenuation and its correction. | 18 |
| 8 | Decision & communication | Recovers `(alpha, beta)`; one-pager explains the slope is understated without correction and that `tau_x` calibration is part of the result. | 10 |
| — | SBC & prior sensitivity | SBC ranks for `(alpha, beta)`; prior-sensitivity traces the de-attenuation curve vs assumed `tau_x`. | 12 |

**Deductions.** Reporting the naive slope as the effect (−10). Treating a good `y`-PPC
as evidence the naive model is fine (−6). A latent-variable indexing bug
(misaligned `x_true`) left undetected (−8). Claiming the EIV model "estimates" `tau_x`
from `(x_obs, y)` alone when it does not (−6).

---

## Open-ended extension prompt

The model assumes `tau_x` is **known**. In practice it often is not. Investigate
identifiability:

1. **Replicate measurements.** Simulate two noisy readings `x_obs1`, `x_obs2` of each
   unit's true predictor. With replicates, `tau_x` **is** identified (the
   within-unit spread estimates it). Extend the model to estimate `tau_x` jointly and
   show the slope is still recovered — now without assuming the noise SD.
2. **Sensitivity vs identifiability.** Without replicates, put a prior on `tau_x` and
   show the slope is only as good as that prior (connect to `prior_sensitivity.py`).
   How informative must the `tau_x` prior be to pin down `beta` to within 10%?

Deliver a notebook with the replicate-measurement model, an SBC check on `beta`, an
`az.compare` (LOO) against the known-`tau_x` model, and a paragraph on when you can
get away with assuming `tau_x` versus when you must measure it.
