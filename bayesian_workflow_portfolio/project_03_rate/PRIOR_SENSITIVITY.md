# Prior Sensitivity — Project 03: The log_rate Prior

**Model:** `y_i ~ Poisson(exposure_i * exp(log_rate))` with the **prior on `log_rate`
varied**
**Script:** `prior_sensitivity.py`

---

## 1. The question

The new modeling idea in this project is the **log link**: we place a Normal prior on
`log_rate` so that `lambda = exp(log_rate)` is automatically positive and the prior is
symmetric on the multiplicative (log) scale. A natural worry is whether the answer
depends on how broad or where-centred that log-scale prior is. We refit the same data
under three Normal priors on `log_rate`:

| Prior on `log_rate` | Character |
|---|---|
| `Normal(0, 5)` | Vague; spans `exp(-10)..exp(10)` — a vast range of rates. |
| `Normal(0, 2)` | Weakly-informative; our default; spans `~exp(-4)..exp(4)`. |
| `Normal(-1, 1)` | Mildly informative; centred near a plausible rate, tighter. |

---

## 2. Procedure

Reproduce with:

```bash
python3 prior_sensitivity.py
```

Each prior is refit with a light sampler (`draws=600, tune=600, chains=2`). We report
the posterior mean and SD of `log_rate` and the posterior mean rate `exp(log_rate)`.

---

## 3. Results

```
Data: n=50 samples, total events=350, total exposure=1100.7
True log_rate=-1.2 (rate=0.301)

                   prior  logr mean   logr sd  rate mean
       Vague Normal(0,5)     -1.147     0.053      0.318
   Weak-info Normal(0,2)     -1.147     0.055      0.318
  Mild-info Normal(-1,1)     -1.147     0.054      0.318

Max difference in posterior mean log_rate across priors: 0.0000
```

| `log_rate` prior | `log_rate` mean | rate mean |
|---|---|---|
| `Normal(0, 5)` | -1.147 | 0.318 |
| `Normal(0, 2)` | -1.147 | 0.318 |
| `Normal(-1, 1)` | -1.147 | 0.318 |

**Maximum spread in posterior mean `log_rate`: 0.0000** (to four decimals).

---

## 4. Interpretation

The three priors give an identical posterior to four decimal places. With 350 total
events across 50 samples, the Poisson likelihood is extremely informative about the
rate, and even the tightest of these priors (`Normal(-1, 1)`) is outvoted. The
posterior `log_rate` of -1.147 corresponds to a rate of 0.318 events per unit exposure,
close to the true 0.301 (the data happened to run slightly hot, and the posterior
faithfully follows the data).

**Why so robust?** Count data are information-rich: 350 events pin the rate down
tightly (`log_rate` SD ~0.054). The priors differ in breadth and centre, but all three
place non-negligible mass near the true value, and the likelihood does the rest.

**The usual caveat:** this robustness is a property of the total event count, not of the
priors. Re-run with a much smaller dataset — few samples and low exposures, so only a
handful of total events — and the `Normal(-1, 1)` prior would visibly pull the
posterior relative to the vague `Normal(0, 5)`. Demonstrate robustness at the data
volume you actually have.

**What this analysis does *not* excuse.** Prior robustness says nothing about *model*
correctness. The far larger danger in this project is not the choice of `log_rate`
prior but **omitting the exposure offset** — a *structural* error that biases the rate
by an order of magnitude regardless of the prior (see `BROKEN_BUGS.md`). A robust prior
on a mis-specified model still gives a confidently wrong answer.

---

## 5. What to report to a collaborator

> "We checked three priors for the rate, from vague to mildly informative. The
> estimated rate did not change at all to three decimals — the conclusion is driven
> entirely by the data. (The estimate *does* depend critically on including the
> exposure offset, which we did.)"
