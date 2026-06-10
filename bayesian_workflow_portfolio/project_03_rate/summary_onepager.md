# One-Page Summary — Event Rate per Unit Exposure

**For:** the collaborator who needs the event rate and a prediction for new samples
**Question:** how often do events occur per unit of exposure, and how many should a new
sample show?
**Data:** 50 samples, each with its own exposure; 350 events total over 1100 units of
exposure

---

## Bottom line

> **The event rate is about 0.30 per unit exposure (94% CI roughly [0.27, 0.36]). A new
> sample with exposure 20 should yield about 6 events.**

| What we report | Value | Plain-language meaning |
|---|---|---|
| Event rate (`lambda`) | **~0.30 / unit** | About 3 events per 10 units of exposure. |
| 94% credible interval | **[0.27, 0.36]** | 94% sure the true rate is in this range. |
| Predicted count at exposure 20 | **~6 events** | What to expect from a typical new sample. |

The samples ranged widely in exposure (from ~7 to ~40 units), which is exactly why the
analysis had to account for exposure explicitly.

---

## The one thing that matters most here

> **You must divide by exposure.** The samples had very different exposures, so a sample
> with 40 units of exposure naturally shows ~6x more events than one with 7 units — at
> the *same* underlying rate.

If we had naively averaged the raw counts (ignoring exposure), we would have reported a
"rate" of about **7 events per sample**, which is meaningless and ~20x off the true
per-exposure rate of 0.30. The whole point of the model is to convert raw counts into a
rate that is comparable across samples of different sizes. The headline number (0.30 per
unit) already has exposure correctly accounted for.

---

## What this means for a decision

- **Comparing samples:** use the *rate per unit exposure* (0.30), never the raw count.
  Raw counts mostly reflect how much exposure each sample had, not how active the
  underlying process is.
- **Predicting a new sample:** multiply the rate by that sample's exposure. Exposure 20
  -> ~6 events; exposure 40 -> ~12 events.
- **If you need a tighter rate estimate:** uncertainty shrinks as total events grow.
  Doubling the total exposure (more or larger samples) roughly halves the rate's
  uncertainty.

---

## How confident should you be in these numbers?

The standard checks passed:

- **The method is calibrated.** A simulation-based calibration test confirmed the
  procedure produces correctly-sized uncertainty intervals — neither over- nor
  under-confident.
- **The answer does not depend on our assumptions.** We re-derived the rate under three
  different prior choices; it did not change at all to three decimals.
- **The model fits the data.** Posterior predictive checks show the observed counts are
  typical of what the model expects across the full exposure range.

---

## The one caveat worth stating

These numbers assume a **single common rate** with **no extra sample-to-sample
variability** beyond what counting noise (Poisson) explains, and that **exposures are
known exactly**. If some samples are intrinsically more active than others
(overdispersion), the true uncertainty is larger than stated. If you suspect that, flag
it and we will fit an overdispersed (Negative-Binomial) model.

---

## Recommendation

Report the rate as **~0.30 events per unit exposure (94% CI [0.27, 0.36])** and predict
new-sample counts by **rate x exposure**. Always work in rate-per-exposure, never raw
counts, when comparing samples of different sizes.
