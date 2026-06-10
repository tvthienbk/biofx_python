# Prior Sensitivity — Project 10: Varying Intercepts

**Model:** hierarchical logistic (non-centered); we vary the prior on the
between-family SD `tau`.
**Script:** `prior_sensitivity.py`

---

## 1. The question

With only `G = 10` families, the between-family SD `tau` (on the log-odds
intercept) is weakly identified. Its prior therefore controls **how aggressively
the family intercepts are pooled**: a tight prior near 0 collapses all families
toward one common intercept (over-pooling — the project's pitfall); a vague prior
lets them float. We refit the same data under three HalfNormal priors on `tau` and
read off `tau`, `mu`, `beta`, and — most directly — the **spread of the recovered
family intercepts**.

| Prior | Character |
|---|---|
| `HalfNormal(0.1)` | **Tight** — forces near-complete pooling of intercepts. |
| `HalfNormal(1.0)` | **Default** — weakly informative. |
| `HalfNormal(5.0)` | **Vague** — little constraint. |

---

## 2. Procedure

`python3 prior_sensitivity.py` fits the non-centered model (chains=2, tune=1000,
`target_accept=0.95`) under each prior. Truth: `mu=-0.3`, `tau=0.9`, `beta=1.2`.

---

## 3. Results

```
Data: G=10 families x 12 obs; true mu=-0.3, tau=0.9, beta=1.2

                 tau prior       mu      tau     beta  alpha spread
     tight HalfNormal(0.1)    0.035    0.083    0.895         0.054
   default HalfNormal(1.0)    0.059    0.552    0.960         0.915
     vague HalfNormal(5.0)    0.024    0.630    0.960         0.996

Spread in posterior mean tau across priors: 0.547
Spread in family-intercept range across priors: 0.942
```

| `tau` prior | `mu` | `tau` | `beta` | family-intercept spread |
|---|---|---|---|---|
| tight `HalfNormal(0.1)` | 0.035 | 0.083 | 0.895 | **0.054** |
| default `HalfNormal(1.0)` | 0.059 | 0.552 | 0.960 | 0.915 |
| vague `HalfNormal(5.0)` | 0.024 | 0.630 | 0.960 | 0.996 |

---

## 4. Interpretation

**The over-pooling pathology is stark.** Under the tight `HalfNormal(0.1)` prior,
the recovered family intercepts span just **0.054** log-odds — they have collapsed
onto a single value, erasing the real ~0.9 spread the data contain. Under the
default and vague priors the intercepts spread by ~0.9–1.0, recovering genuine
family-to-family variation. The posterior mean of `tau` moves correspondingly,
from 0.083 (essentially "no families differ") to ~0.6.

**The global slope `beta` is robust** (0.895 → 0.960): it is informed by all 120
observations and barely depends on the intercept prior. The contrast is the lesson:
in a hierarchical GLM, **population-level fixed effects are well-identified while
the group-level scale is prior-sensitive when groups are few.**

**The rule.** Do not reach for a tight `tau` prior to "regularize" — with few
groups it does not regularize, it *over-pools*, manufacturing the conclusion that
families are identical. Choose a weakly-informative scale prior, state it, and
report this sensitivity.

---

## 5. What to report to a collaborator

> "Whether higher score raises binding (the slope) is solid regardless of
> assumptions. *How much families differ* depends on the prior: a skeptical prior
> makes them look identical, a neutral prior reveals real differences. We used a
> neutral prior; if the family differences drive a decision, we should add families
> rather than lean on the prior."
