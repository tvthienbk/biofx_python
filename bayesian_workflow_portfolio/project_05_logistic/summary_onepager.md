# One-Page Summary — Ligand Binding vs a Covariate

**Audience:** a bench collaborator who needs a decision, not a posterior.

## The question

Does the chance that our ligand binds the receptor increase with the covariate
$x$ (a standardized concentration / hydrophobicity score), and at what level of
$x$ is binding 50/50? We ran the assay in 120 independent wells, recorded
bind / no-bind, and fit a logistic regression.

## What we found

- **Binding clearly increases with $x$.** The probability that the effect is
  positive is essentially 1 ($P(\beta>0\mid\text{data})\approx 1.00$). Each one
  standard-deviation increase in $x$ multiplies the **odds** of binding by roughly
  4 (95% credible range about 3–9).
- **The half-maximal point** — the $x$ at which binding is a coin flip — sits near
  the *mean* covariate value, with a fairly tight credible interval. Below it
  binding is unlikely; above it, increasingly likely.
- **The model is well-calibrated:** when we predict, say, 70% binding, about 70%
  of those wells actually bind. No sign of a missing nonlinearity over the range
  tested.

## What this means for the bench

- To **maximize binding**, work at $x$ around $+1$ SD or higher (predicted binding
  $\gtrsim 80\%$).
- To **probe the transition** (e.g. for a titration), center your next experiment
  on the half-maximal point near the mean $x$, where the response changes fastest.
- The effect is strong and certain enough that **no further replication is needed
  to confirm direction**; spend the next experiment characterizing the curve's
  shape at the extremes instead.

## Caveats (one line each)

- We assumed binding rises *smoothly* with $x$ (linear in log-odds). The
  calibration check supports this over the tested range; extrapolation beyond it
  is unwarranted.
- We assumed $x$ is measured accurately and wells are independent. Plate or batch
  effects, if present, would widen the real uncertainty.

## Bottom line

Binding is strongly and reliably driven by $x$. Set working concentrations using
the half-maximal point near the mean covariate, and target high $x$ when maximal
binding is the goal.
