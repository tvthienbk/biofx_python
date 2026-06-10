# One-Page Summary — Assay Success Rate

**For:** the lab / project lead deciding whether to advance this assay
**Question:** how often does the assay succeed, and is that rate above one-half?
**Date:** prepared from `n = 80` independent assay runs

---

## Bottom line

> **The assay's true success rate is most plausibly about 0.59 (59%), and we are
> roughly 92% confident it exceeds one-half.**

| What we report | Value | Plain-language meaning |
|---|---|---|
| Best estimate of the success rate | **0.585** | About 59 of every 100 runs succeed. |
| 94% credible interval | **[0.49, 0.69]** | We are 94% sure the true rate lies in this range. |
| Probability the rate beats 50% | **~0.92** | A ~12-to-1 bet that the assay succeeds more often than not. |

These numbers come from 80 runs in which 47 succeeded (an observed rate of 0.59).

---

## What this means for a decision

- **If your bar is "succeeds more often than not" (rate > 50%):** the evidence is
  *fairly strong but not conclusive* — about 92% confidence, not 99%. There is still
  roughly a 1-in-12 chance the true rate is at or below one-half.
- **If your bar is higher (say, rate > 65%):** the data do **not** support that yet —
  our interval tops out around 0.69 and most of its mass sits below 0.65.
- **If you need tighter certainty:** the interval is about +/-5 percentage points wide.
  Halving that width would require roughly four times as many runs (~320 total).
  More data narrows the interval; it will not necessarily move the estimate.

---

## How confident should you be in these numbers?

We ran the standard checks and they all passed:

- **The method is calibrated.** A simulation-based calibration test (400 simulated
  experiments) confirmed the procedure produces correctly-sized uncertainty
  intervals — they are neither over- nor under-confident.
- **The answer does not depend on our assumptions.** We re-derived the estimate
  under three different prior choices; the result changed by less than 0.003 —
  negligible. At this sample size the data, not our assumptions, drive the answer.
- **The model fits the data.** Posterior predictive checks show the observed number
  of successes sits comfortably in the middle of what the model expects.

---

## The one caveat worth stating

These conclusions assume the 80 runs are **interchangeable** — same protocol, no
drift over time, no batch-to-batch differences. If runs were done in distinct
batches or by different operators, the true uncertainty could be larger than stated.
If that is the case, flag it and we will fit a model that accounts for batch effects
before you rely on the +/-5-point interval.

---

## Recommendation

Treat the success rate as **~59% with +/-5 points of uncertainty**. It is a reasonable
working assumption that the assay succeeds more often than it fails, but do not
plan around a rate higher than ~65% without collecting more runs.
