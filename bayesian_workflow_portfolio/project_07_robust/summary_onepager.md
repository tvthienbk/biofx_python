# One-Page Summary — Robust Calibration Line

**Audience:** a bench collaborator who needs a decision, not a posterior.

## The question

We ran a calibration: a known input $x$ versus a measured response $y$, expected
to be a straight line. A few of the 60 measurements are clearly bad (pipetting
slips / bubbles / mis-reads). What is the true calibration line, and did the bad
points distort it?

## The key modeling decision (and why it matters to you)

We used a **robust (Student-t) fit** instead of ordinary least squares. Least
squares treats every point as equally trustworthy and lets a few gross outliers
**tilt the whole line** and **inflate the apparent noise**. The robust fit
automatically down-weights points that are far from the trend, so the calibration
reflects the clean majority. We confirmed (via a held-out predictive score, LOO)
that the robust model genuinely describes the data better.

## What we found

- **Calibration line:** $y \approx 1.0 + 2.0\,x$.
  - slope $\approx 2.0$ (94% credible interval roughly 1.9–2.1),
  - intercept $\approx 1.0$ (94% interval roughly 0.8–1.2).
- **The outliers were real and were handled:** the model's tail parameter came out
  small, which is its way of saying "there are genuine outliers here," and it
  down-weighted them correctly.
- **A naive least-squares fit would have misled you:** it reported a tilted slope
  and a noise level several times too large.

## What this means for the bench

- **Use $y \approx 1.0 + 2.0\,x$** as the working calibration.
- The true measurement-to-measurement noise is **small** (clean SD ~0.6), not the
  large value an ordinary fit would suggest — so the assay is more precise than a
  naive analysis implies.
- The ~6 flagged points are worth a look: re-run them if they matter, but they did
  **not** corrupt the calibration.

## Caveats (one line each)

- The outliers here were ordinary high/low readings (vertical). Bad points at the
  extreme ends of the $x$ range would need a different treatment.
- We assumed the true relationship is a straight line over the tested range.

## Bottom line

The calibration is $y \approx 1.0 + 2.0\,x$ with small noise, recovered cleanly
despite ~10% bad measurements. Trust the robust fit; the bad wells did not move it.
