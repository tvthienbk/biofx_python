# Prior Sensitivity — Project 20 (the between-compound SD prior)

## What we vary

The prior on `tau` (between-compound sd) controls how aggressively the model pools,
which directly shapes the recommendation. We refit under three `tau` priors and —
because the deliverable is a **decision** — compare not just `tau` but the
**recommended compound** and its probability-of-best (`prior_sensitivity.py`):

| Label | `tau` prior | Pooling behaviour |
|---|---|---|
| Default | `HalfNormal(1.0)` | data-driven shrinkage |
| Tight | `HalfNormal(0.3)` | strong pooling (shrinks toward `mu`) |
| Loose | `HalfNormal(3.0)` | weak pooling (closer to raw means) |

## What to expect

- **Default & Loose:** the partial-pooling decision should point to the **true
  best** compound, correcting the raw-mean winner's curse. `P(best)` of the
  recommendation is moderate (honest — the screen is noisy).
- **Tight `HalfNormal(0.3)`:** over-pools — it pulls `tau` down and shrinks every
  compound harder toward `mu`. In this screen the well-replicated true best (#0)
  survives the heavier shrinkage and is still recommended, but the *shrinkage
  pattern* (and hence `P(best)`) is reshaped; with a less dominant true best, this
  over-pooling could flatten genuine differences and erase the signal.

## Interpretation: robustness of the *decision*

The right robustness question for a decision problem is **"does the recommended
compound change?"**, not merely "does `tau` change?". The headline finding:

- The recommendation is **robust** to reasonable `tau` priors (default, loose) —
  partial pooling reliably beats the raw-mean winner's curse.
- It is **at risk** under an over-tight `tau` prior, which over-pools; when the
  true best is less dominant than here, that can erase the signal. So the
  between-compound SD prior is the key lever, and the safe default is a
  weakly-informative prior that lets the data set the shrinkage.

This reframes prior sensitivity for decision-making: always check whether the
*action* is stable, and report the prior regime under which your recommendation
holds.
