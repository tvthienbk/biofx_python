# One-Page Summary — Dose-Response Effect

**For:** the collaborator deciding whether dose drives the response, and by how much
**Question:** how much does the response change per unit of dose, and what response
should we expect at a given dose?
**Data:** 40 dose-response measurements, doses spanning 100 to 600 units

---

## Bottom line

> **Each additional unit of dose raises the response by about 0.015 (94% CI roughly
> [0.011, 0.019]). At a dose of 400 the expected response is about 8.**

| What we report | Value | Plain-language meaning |
|---|---|---|
| Dose effect (slope) | **~0.015 / unit dose** | Response rises 0.015 per unit of dose. |
| 94% credible interval | **[0.011, 0.019]** | 94% sure the true effect is in this range. |
| Effect clearly positive? | **Yes** | The interval is well above zero — dose matters. |
| Predicted response at dose 400 | **~8** | What to expect from a typical sample at dose 400. |

---

## What this means for a decision

- **Does dose matter?** Yes. The estimated effect (0.015 per unit) is clearly positive —
  its entire 94% interval lies above zero. Over the studied range (100 to 600), that
  amounts to a response increase of about 7–8 units from the lowest to the highest dose.
- **Predicting a response:** at dose 400, expect ~8; the relationship is linear, so each
  100 units of dose adds about 1.5 to the response.
- **How precise is the effect?** The effect is pinned to about ±0.004 (per unit). If you
  need it tighter, more measurements — especially spread across the dose range — will
  narrow it.

---

## A note on how we estimated this

We **standardized** the dose internally (rescaled it to a common scale centred at the
average dose) before fitting. This is a routine, exact transformation that makes the
estimation numerically stable and the priors easy to set — it does not change the
science. We then translated everything **back to the natural dose units** you care about,
so every number above is on the original scale. You never have to think about the
standardized scale; it is purely an internal device for reliable computation.

---

## How confident should you be in these numbers?

The standard checks passed:

- **The method is calibrated.** A simulation-based calibration test confirmed the
  procedure produces correctly-sized uncertainty intervals for the slope, intercept, and
  noise — neither over- nor under-confident.
- **The answer does not depend on our assumptions.** We re-derived the effect under
  several prior choices; it barely moved.
- **The model fits the data.** Posterior predictive checks show the data scatter evenly
  around the fitted line across the whole dose range, with no systematic curvature.

---

## The one caveat worth stating

These numbers assume the dose-response is **linear** with **constant noise** across the
dose range, and that **doses are known exactly**. If the true relationship curves
(saturates at high dose, say), a straight line will mis-predict at the extremes. The
residual check showed no curvature here, but if you expect saturation biologically, flag
it and we will fit a curved (e.g. quadratic or saturating) model.

---

## Recommendation

Treat the dose effect as **~0.015 response units per unit dose (94% CI [0.011, 0.019])**,
clearly positive. Predict responses linearly across the studied range (100–600). Collect
more points, spread across doses, only if you need the effect pinned tighter than ±0.004.
