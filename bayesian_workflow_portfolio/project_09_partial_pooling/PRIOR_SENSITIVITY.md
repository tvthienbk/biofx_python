# Prior Sensitivity — Project 09: Partial Pooling

**Model:** hierarchical Normal (non-centered); we vary the prior on the
between-group SD `tau`.
**Script:** `prior_sensitivity.py`

---

## 1. The question

In a hierarchical model with **few groups**, the prior that matters most is the
one on `tau`, the between-group SD. `tau` controls **shrinkage**: small `tau`
forces each group toward the grand mean (strong pooling); large `tau` lets groups
float free (weak pooling). With only J=12 groups the data constrain `tau` weakly,
so its prior has real leverage on both `tau` itself and the degree of pooling — a
sharp contrast with Project 01, where N=80 made every prior irrelevant.

We refit the same data under three HalfNormal priors on `tau`:

| Prior | Character |
|---|---|
| `HalfNormal(0.5)` | **Tight** — strong a-priori pull toward complete pooling. |
| `HalfNormal(2.0)` | **Default** — our weakly-informative choice. |
| `HalfNormal(10)`  | **Vague** — almost no constraint on between-group spread. |

The hyperprior on `mu` and the within-group `sigma` are held fixed.

---

## 2. Procedure

Reproduce with `python3 prior_sensitivity.py`. The script fits the non-centered
model (chains=2, tune=1000, `target_accept=0.95`) under each prior and reports the
posterior mean of `mu` and `tau` plus `tau`'s 94% HDI. True values: `mu=5.0`,
`tau=0.8`, `sigma=1.0`.

---

## 3. Results

```
Data: J=12 groups x 4 obs; true mu=5.0, tau=0.8, sigma=1.0

                 tau prior   mu mean   tau mean           tau 94% HDI
     tight HalfNormal(0.5)     5.257      0.645  [ 0.245,  1.024]
   default HalfNormal(2.0)     5.264      0.781  [ 0.282,  1.248]
      vague HalfNormal(10)     5.255      0.812  [ 0.342,  1.316]

Spread in posterior mean tau across priors: 0.167
Spread in posterior mean mu  across priors: 0.009
```

| `tau` prior | posterior mean `mu` | posterior mean `tau` | `tau` 94% HDI |
|---|---|---|---|
| tight `HalfNormal(0.5)` | 5.257 | 0.645 | [0.245, 1.024] |
| default `HalfNormal(2.0)` | 5.264 | 0.781 | [0.282, 1.248] |
| vague `HalfNormal(10)` | 5.255 | 0.812 | [0.342, 1.316] |

---

## 4. Interpretation

**`mu` is robust; `tau` is not.** The grand mean `mu` is essentially unchanged
across priors (spread 0.009) — it is pinned down by all 48 observations together.
But the posterior mean of `tau` moves by 0.167 (from 0.645 to 0.812), a ~20%
swing, and the tight prior visibly biases `tau` *downward* toward its mode at 0.

This matters because **`tau` drives shrinkage**. Under the tight prior the model
believes the plates are more alike than they are, shrinks per-group estimates
harder, and understates real plate-to-plate variation. The vague prior recovers
`tau` closest to truth (0.8) here, but at the cost of admitting implausibly large
spreads a priori — and with even fewer groups the vague prior can let `tau` run
away entirely.

**The lesson generalizes.** Unlike a location parameter, a **variance/scale
parameter in a hierarchical model with few groups is genuinely prior-sensitive**.
You cannot wave it away with "the data will sort it out" — there are only 12 data
points (group means) informing `tau`. The right posture:

> Choose a **weakly-informative** prior on `tau` (e.g. `HalfNormal` scaled to the
> plausible between-group spread), state it explicitly, and report the sensitivity.
> Avoid both a tight prior (which manufactures pooling) and a vague one (which
> permits absurd spread). The `default HalfNormal(2.0)` here is the defensible
> middle.

---

## 5. What to report to a collaborator

> "The overall mean is rock-solid regardless of assumptions. The estimate of how
> much plates differ (~0.8) depends somewhat on the prior — a more skeptical prior
> pulls it down to ~0.65. We used a mild, neutral prior and report this
> sensitivity; if a decision hinges on the exact plate-to-plate spread, we should
> collect more plates rather than lean harder on the prior."
