# Prior Sensitivity — 2-component mixture

## What we vary and why

The prior most likely to influence a mixture fit is the **component-spread
prior** — the `HalfNormal` scale on `sigma`. It governs the tug-of-war between
"two narrow, well-separated Gaussians" and "one wide blob": a prior that strongly
favours small `sigma` forces the model to explain spread as *separation between
components*, while a vague prior lets a single fat component absorb the data. We
therefore refit the same `N = 300` dataset under three scales:

| Prior on `sigma` | Scale | Character |
|------------------|-------|-----------|
| tight  | `HalfNormal(0.5)` | pulls `sigma` small |
| default| `HalfNormal(1.0)` | our weakly-informative choice |
| vague  | `HalfNormal(3.0)` | barely informative |

We compare the posteriors of the **identifiable** quantities: separation `sigma`,
and the high-mean weight `w[1]`.

## Results

From `python3 prior_sensitivity.py`:

```
Data: N=300, true separation=3.50, sigma=0.70, w_high=0.65

          prior on sigma   sep mean  sigma mean  w_high mean
  tight  HalfNormal(0.5)      3.483       0.660        0.656
 default HalfNormal(1.0)      3.481       0.663        0.657
  vague  HalfNormal(3.0)      3.489       0.662        0.657

Max spread across priors: separation=0.009, sigma=0.003, w_high=0.001
```

## Interpretation

The three posteriors are **essentially identical** — the maximum spread in any
posterior mean is < 0.01. With a clearly bimodal sample of 300 points the
likelihood is highly informative about both the separation and the spread, so the
data dominate the `sigma` prior. Our conclusions about the subpopulation
structure are **robust** to this prior choice.

**When would the prior matter?** If the two states were poorly separated
(separation comparable to `sigma`) or the sample were small, the `sigma` prior
would meaningfully steer whether the model "sees" one component or two. In that
regime prior sensitivity is not a formality but a genuine source of conclusion
uncertainty, and the tight-vs-vague disagreement would be the headline result.

**Practical guidance.** Report the default `HalfNormal(1)` result, but always run
this sweep. If the identifiable summaries move appreciably across reasonable
priors, say so explicitly and let the decision-maker see the range — do not hide
prior dependence behind a single number.
