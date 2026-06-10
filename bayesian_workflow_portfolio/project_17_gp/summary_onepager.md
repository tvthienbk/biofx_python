# One-Pager — Fitting a Smooth Response Curve (Project 17)

**Audience:** a lab collaborator who has a melt / dose-response dataset and wants a
trustworthy curve, not a regression lecture.

## The question

You measured a response at a range of inputs (temperature, dose). You want the
underlying curve - and crucially, *how sure we are about it* - without forcing the
data into a logistic or polynomial that might be the wrong shape.

## What we did

We fit a **Gaussian process**: instead of assuming a formula for the curve, we
assumed only that the curve is **smooth**, and let the data decide the rest. The
method returns a best-estimate curve **plus a shaded uncertainty band** that is
narrow where you have data and widens where you don't.

## What we found

- The estimated curve recovers the true underlying response to within a small
  error (mean absolute error < 0.25 on the simulated benchmark, where we know the
  truth).
- The estimated measurement noise matches the true noise level.
- The curve shows a clear transition plus a secondary feature that a single
  logistic would have smoothed away - a reminder that flexible models can reveal
  structure rigid ones hide.

## The one knob that matters

The result hinges on a single setting: **how wiggly we allow the curve to be**
(the "length-scale"). We deliberately told the model the curve varies on roughly a
fifth of the input range. If you leave this fully open, the model becomes confused
- it can't tell genuine signal from noise - and the fit becomes unreliable. So
this is a judgement we make explicitly and disclose, not a hidden default.

## What you can do with it

- Read off a **midpoint / crossing point** (e.g. where the response passes a
  threshold) **with its uncertainty** - report both, never the point alone.
- Trust the band: where it is wide, collect more data there before deciding.
- Do **not** trust the curve far outside the measured input range - the method
  honestly admits it knows nothing there (the band balloons).

## Bottom line

We have a defensible, uncertainty-aware estimate of your response curve. The next
action is to use the crossing-point estimate and its band to decide where to
sample next or where to set an operating point - not to over-read a single number.
