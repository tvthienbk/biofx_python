# One-Page Summary — Concentration & Measurement Noise

**For:** the collaborator who needs the sample's concentration and how reproducible it is
**Question:** what is the true concentration, and how noisy is a single measurement?
**Data:** 30 replicate measurements of the same sample

---

## Bottom line

> **The sample's concentration is about 4.9 mg/mL (94% CI roughly [4.4, 5.4]), and a
> single measurement carries about ±1.5 mg/mL of noise.**

| What we report | Value | Plain-language meaning |
|---|---|---|
| Concentration (`mu`) | **~4.85 mg/mL** | Best estimate of the true concentration. |
| 94% credible interval for `mu` | **[4.4, 5.4]** | 94% sure the true concentration is in this range. |
| Measurement noise (`sigma`) | **~1.45 mg/mL** | Typical scatter of one measurement around the truth. |
| 94% credible interval for `sigma` | **[1.1, 1.9]** | 94% sure the noise level is in this range. |

The 30 replicates had an average of 4.84 mg/mL and a spread (SD) of 1.39 mg/mL.

---

## Why both numbers matter

Most reports give only the average. The **noise** is just as important:

- The concentration estimate (`mu`) tells you the sample's true value.
- The noise estimate (`sigma`) tells you **how much a single future measurement will
  scatter** around that value. With `sigma ~ 1.5`, any one measurement could easily
  land a point or more away from 4.85 — so do not over-interpret a single reading.
- The two are reported with their own uncertainties: we have averaged out much of the
  noise across 30 replicates, so the *concentration* is known far more precisely
  (±0.3) than any *single measurement* is (±1.5).

---

## What this means for a decision

- **Reporting the sample's concentration:** use 4.85 mg/mL ± ~0.3 (the credible
  interval for the average), not ± 1.5.
- **Predicting a single future measurement:** expect ~4.85 ± ~1.5 — the noise, not the
  average's uncertainty, governs one-shot predictions.
- **If you need a tighter concentration estimate:** the average's uncertainty shrinks
  like 1/sqrt(number of replicates). Roughly 4× more replicates halves it.

---

## How confident should you be in these numbers?

The standard checks passed:

- **The method is calibrated.** A simulation-based calibration test confirmed the
  procedure produces correctly-sized uncertainty intervals for *both* the concentration
  and the noise — neither over- nor under-confident.
- **The answer does not depend on our assumptions.** We re-derived the noise estimate
  under three different prior choices; it changed by less than 0.01 — negligible.
- **The model fits the data.** Posterior predictive checks show the observed scatter is
  typical of what the model expects.

---

## The one caveat worth stating

These numbers assume the noise level is **constant** across all 30 replicates and the
measurements are **independent and symmetric** (no drift, no outliers, no
heavy-tailed errors). If the instrument drifted, or one or two readings were gross
outliers, the true uncertainty could differ. If you suspect either, flag it and we
will fit a model that allows changing noise or robust (heavy-tailed) errors.

---

## Recommendation

Report the concentration as **~4.85 mg/mL with about ±0.3 of uncertainty in the
average**, and note that **single measurements scatter by about ±1.5 mg/mL**. Collect
more replicates only if you need the average pinned down more tightly than ±0.3.
