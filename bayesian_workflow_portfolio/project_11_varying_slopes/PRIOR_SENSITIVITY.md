# Prior Sensitivity — Project 11: Varying Slopes (LKJ eta)

**Model:** varying slopes with LKJ covariance; we vary the LKJ shape `eta`.
**Script:** `prior_sensitivity.py`

---

## 1. The question

The LKJ prior's shape parameter `eta` is a prior on the **intercept-slope
correlation** `rho`:

| `eta` | Character |
|---|---|
| 1 | Uniform over all valid correlations — no pull. |
| 2 | Mild pull toward 0 — our default. |
| 8 | Strong pull toward 0 — skeptical of any correlation. |

With only G=8 cell lines, `rho` is estimated from the scatter of 8 effect pairs and
is therefore weakly identified — exactly the regime where the prior has leverage. We
refit under three `eta` values and compare the posterior for `rho` (and the
population means, which should be robust).

---

## 2. Procedure

`python3 prior_sensitivity.py` fits the non-centered LKJ model (chains=2, tune=1000,
`target_accept=0.9`) under each `eta`. Truth: `rho=0.6`, `mu_a=2.0`, `mu_b=1.0`.

---

## 3. Results

```
Data: G=8 lines x 10 obs; true rho=0.6, mu_a=2.0, mu_b=1.0

         LKJ prior  rho mean           rho 94% HDI    mu_a    mu_b
     uniform eta=1     0.681  [ 0.205,  1.000]   1.859   1.101
     default eta=2     0.510  [-0.050,  0.969]   1.823   1.084
   skeptical eta=8     0.208  [-0.210,  0.586]   1.861   1.093

Spread in posterior mean rho across eta: 0.473
Spread in posterior mean mu_a across eta: 0.038
```

| LKJ prior | posterior `rho` | `rho` 94% HDI | `mu_a` | `mu_b` |
|---|---|---|---|---|
| uniform `eta=1` | 0.681 | [0.205, 1.000] | 1.859 | 1.101 |
| default `eta=2` | 0.510 | [-0.050, 0.969] | 1.823 | 1.084 |
| skeptical `eta=8` | 0.208 | [-0.210, 0.586] | 1.861 | 1.093 |

---

## 4. Interpretation

**`rho` is strongly prior-sensitive; the population means are not.** As `eta` rises
from 1 to 8, the posterior mean of `rho` falls from 0.68 to 0.21 — a spread of 0.47,
larger than `rho`'s own posterior SD. The skeptical `eta=8` prior pulls the estimate
well below the true 0.6 and even admits negative correlations. Meanwhile `mu_a` and
`mu_b` barely move (mu_a spread 0.038): the population means are pinned down by all
80 observations and are indifferent to the correlation prior.

The reason is sample size **at the level that informs `rho`**: a correlation is
learned from the 8 effect pairs, not the 80 observations, so 8 "data points" leave
the prior with real influence. This is the same lesson as Projects 09–10 (group-
level scales are prior-sensitive with few groups), now applied to a correlation.

**The rule.** Report `eta` explicitly, prefer a mild default (`eta=2`) that neither
forces `rho=0` nor lets it hit `±1` on noise, and present `rho` with its sensitivity
rather than as a precise number. If the correlation drives a decision, the fix is
more groups, not a more confident prior.

---

## 5. What to report to a collaborator

> "That higher-baseline lines respond more steeply (a positive correlation) is
> supported, but *how strong* it is depends on our prior because we only have 8
> lines: a neutral prior says ~0.5–0.7, a skeptical one says ~0.2. The average dose
> effect and baseline are solid regardless. To nail down the correlation, we need
> more cell lines."
