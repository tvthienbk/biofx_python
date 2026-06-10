# Prior Sensitivity — Project 02: The Scale Prior

**Model:** `y_i ~ Normal(mu, sigma)` with the **prior on `sigma` varied**
**Script:** `prior_sensitivity.py`

---

## 1. The question

This project's pitfall is the scale prior, so the sensitivity analysis targets it
directly. We hold the location prior on `mu` fixed at `Normal(5, 10)` and refit the
same data under three *proper* scale priors a careful analyst might consider:

| Prior on `sigma` | Character |
|---|---|
| `HalfNormal(5)` | Light-tailed; our default; discourages huge `sigma`. |
| `Exponential(1/5)` | Mean ~5; memoryless; slightly heavier near 0. |
| `HalfCauchy(5)` | Heavy-tailed; permissive about large `sigma`; a classic weakly-informative default. |

Note what is **deliberately excluded**: an improper flat prior on `sigma` (uniform on
`(0, inf)`). That is not a legitimate option to compare — it is the seeded *bug* in the
broken notebook. The lesson of this analysis is that the choice *among proper priors*
is minor, while the choice *between proper and improper* is decisive.

---

## 2. Procedure

Reproduce with:

```bash
python3 prior_sensitivity.py
```

For each scale prior the script refits with a light sampler (`draws=600, tune=600,
chains=2`) and reports the posterior mean and SD for both `mu` and `sigma`.

---

## 3. Results

```
Data: n=30 measurements, empirical mean=4.839, sd=1.389
True mu=5.0, sigma=1.2

       sigma prior   mu mean    mu sd  sigma mean  sigma sd
     HalfNormal(5)     4.852    0.260       1.450     0.211
  Exponential(1/5)     4.837    0.282       1.454     0.210
     HalfCauchy(5)     4.821    0.274       1.454     0.206

Max difference across priors:  mu=0.0310,  sigma=0.0040
```

| `sigma` prior | `mu` mean | `sigma` mean |
|---|---|---|
| `HalfNormal(5)` | 4.852 | 1.450 |
| `Exponential(1/5)` | 4.837 | 1.454 |
| `HalfCauchy(5)` | 4.821 | 1.454 |

**Maximum spread:** `mu` 0.031, `sigma` 0.004.

---

## 4. Interpretation

The three proper scale priors give essentially the same posterior. The `sigma`
estimate moves by 0.004 and `mu` by 0.031 — both negligible against their posterior
SDs of ~0.21 and ~0.27. With `N = 30` informative measurements, the data pin down the
scale well enough that the prior's tail behaviour barely registers.

**Why so robust?** The likelihood for `sigma` is sharply informed by the observed
spread (empirical SD 1.389 over 30 points). The priors differ mainly in their *tails*
(how much mass they place on implausibly large `sigma`), and the data have already
ruled those tails out. A `HalfCauchy` is the most permissive, yet even it lands on the
same answer.

**The real danger lies elsewhere.** Swap any of these for an **improper** flat prior —
`Uniform(0, 1e6)` or an unbounded uniform — and the story changes qualitatively, not
quantitatively. An improper scale prior:

- puts unbounded prior mass on absurdly large variances;
- can leave the posterior with a heavy, slow-to-settle right tail;
- degrades sampler mixing (low ESS on `sigma`, sometimes divergences);
- and, in the worst case (small `N`), yields an *improper posterior* that does not
  integrate to one.

That is the seeded BUG 1 in `notebook_broken.ipynb`. The teaching point:

> Among **proper, weakly-informative** scale priors the choice is a minor robustness
> detail. The choice that matters is **proper vs improper** — always use a proper
> prior on a scale parameter.

**The usual caveat applies:** this robustness is a property of `N = 30`. At `N = 3` the
heavy-tailed `HalfCauchy` would visibly differ from the light-tailed `HalfNormal`, and
the prior's tail would carry real weight. Demonstrate robustness at the sample size you
actually have.

---

## 5. What to report to a collaborator

> "We checked three different priors for the measurement-noise level. The estimated
> noise changed by 0.004 across all three — negligible. Our conclusions do not depend
> on the prior at this sample size. (We avoided an unbounded 'flat' noise prior, which
> is improper and can destabilize the estimate.)"
