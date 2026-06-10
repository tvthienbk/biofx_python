# Prior Sensitivity — Project 01: Estimating a Proportion

**Model:** `y_i ~ Bernoulli(theta)`, `theta ~ Beta(a, b)`
**Script:** `prior_sensitivity.py`

---

## 1. The question

A Bayesian posterior is a compromise between the prior and the likelihood. When a
collaborator asks "but how much does your answer depend on the prior you picked?",
the honest reply is not a philosophical defence of the prior — it is an
**experiment**: refit the *same data* under several defensible priors and show how
little (or how much) the conclusion moves. That is a prior sensitivity analysis.

For a proportion the natural prior family is the `Beta(a, b)`. We compare three
priors that a reasonable analyst might reach for:

| Prior | Parameters | Character |
|---|---|---|
| **Jeffreys** | `Beta(0.5, 0.5)` | Reference prior; U-shaped, piles mass at the 0/1 edges. |
| **Uniform** | `Beta(1, 1)` | "Flat"; often *mistaken* for "no assumptions". |
| **Weak-info** | `Beta(2, 2)` | Our default; mild, unimodal, pulls gently off the edges. |

Because `Beta` is conjugate to the Bernoulli/Binomial likelihood, each posterior
is exactly `Beta(a + k, b + n - k)`. We can therefore report posterior means, SDs,
and central 94% intervals analytically — no sampling noise to muddy the comparison.

---

## 2. Procedure

Reproduce with:

```bash
python3 prior_sensitivity.py
```

The script loads the fixed synthetic dataset (`k = 47` successes out of `n = 80`,
true `theta = 0.62`), forms each conjugate posterior, and prints the posterior
mean, SD, and the central 94% credible interval from the Beta quantile function.

---

## 3. Results

```
Data: k=47 successes of n=80 (true theta=0.62)

                   prior  post mean   post sd               94% HDI
  Jeffreys Beta(0.5,0.5)      0.586     0.054  [ 0.483,  0.687]
       Uniform Beta(1,1)      0.585     0.054  [ 0.482,  0.685]
     Weak-info Beta(2,2)      0.583     0.053  [ 0.481,  0.682]

Max difference in posterior mean across priors: 0.0031
```

| Prior | Posterior mean | Posterior SD | 94% interval |
|---|---|---|---|
| Jeffreys `Beta(0.5,0.5)` | 0.586 | 0.054 | [0.483, 0.687] |
| Uniform `Beta(1,1)` | 0.585 | 0.054 | [0.482, 0.685] |
| Weak-info `Beta(2,2)` | 0.583 | 0.053 | [0.481, 0.682] |

**Maximum spread in posterior mean across priors: 0.0031.**

---

## 4. Interpretation

The three posteriors are, for all practical purposes, the same distribution. The
posterior means differ by 0.003 — far smaller than the posterior SD of ~0.054 and
utterly negligible against the [0.48, 0.69]-wide credible interval. Any decision
that flips between these priors was never supported by the data in the first place.

**Why so robust?** With `n = 80` observations the likelihood carries roughly
`a + b = 80` "pseudo-observations" of weight, while the priors carry only `1`, `2`,
or `4`. The prior is outvoted ~20-to-1. The Jeffreys prior's heavy edge mass and
the uniform prior's flatness simply do not survive contact with 80 data points.

**The crucial caveat — robustness is a property of the data, not the prior.**
It would be a serious error to conclude "the prior never matters here". Re-run the
script with `n = 5` (edit `N_TRIALS` in `data/generate_data.py` or pass `n=5` to
`generate`) and the three posterior means visibly separate, because now the prior
carries a meaningful fraction of the total weight. The lesson generalizes:

> A prior sensitivity analysis must be performed **at the sample size you actually
> have**. Demonstrated robustness at `n = 80` says nothing about robustness at
> `n = 5`, and conclusions drawn from small samples can hinge entirely on the
> prior.

This is also why the project insists on `Beta(2, 2)` over `Beta(1, 1)` as the
*default* even though they barely differ here: the habit of choosing a weakly
informative prior costs nothing when data are plentiful and protects you when they
are scarce — and in later projects (a variance in Project 02, a slope in Project
04, a hierarchical scale in the hierarchical projects) a flat prior genuinely
breaks inference rather than merely nudging it.

---

## 5. What to report to a collaborator

> "We checked three different priors — a reference prior, a flat prior, and a
> mildly informative one. The estimated success rate changed by less than 0.003
> across all three, which is negligible compared with our uncertainty of about
> ±0.05. The conclusion does not depend on the prior at this sample size."

That sentence — not the posterior plot — is the deliverable of a sensitivity
analysis.
