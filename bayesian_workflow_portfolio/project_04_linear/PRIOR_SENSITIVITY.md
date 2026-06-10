# Prior Sensitivity — Project 04: Slope & Intercept Priors

**Model:** `y_i ~ Normal(alpha + beta * x_std, sigma)` with the **priors on
`(alpha, beta)` varied**
**Script:** `prior_sensitivity.py`

---

## 1. The question

This project's pitfall is un-scaled predictors, and the sensitivity analysis makes the
flip side of that lesson concrete: **once you standardize, priors become easy to set on
a common O(1) scale.** We hold the standardized design fixed and refit under three prior
widths on the intercept and slope:

| Prior on `(alpha, beta)` | Character |
|---|---|
| `Normal(0, 20)` | Vague; very broad on the standardized scale. |
| `Normal(0, 5)` | Weakly-informative; our default. |
| `Normal(0, 1)` | Deliberately tight. |

On the **standardized** scale the true coefficients are `alpha_std ~ 7.0` and `beta_std
~ 1.9` — both O(1)-to-O(10). So `Normal(0, 5)` is a sensible weakly-informative width,
`Normal(0, 20)` is generous, and `Normal(0, 1)` is genuinely tight (its prior SD is
smaller than the true intercept). This spread of widths lets us see when the data
dominate and when a too-tight prior starts to bite.

---

## 2. Procedure

Reproduce with:

```bash
python3 prior_sensitivity.py
```

Each prior is refit with a light sampler (`draws=600, tune=600, chains=2`). We report
the posterior means of `alpha`, `beta`, and `sigma`.

---

## 3. Results

```
Data: n=40 points; standardized truth alpha=6.999, beta=1.882

    prior (alpha,beta)    alpha     beta    sigma
    Vague Normal(0,20)    7.130    1.945    0.775
 Weak-info Normal(0,5)    7.130    1.945    0.779
     Tight Normal(0,1)    7.028    1.917    0.785

Max difference across priors:  alpha=0.1020,  beta=0.0280
```

| Prior | `alpha` | `beta` | `sigma` |
|---|---|---|---|
| `Normal(0, 20)` | 7.130 | 1.945 | 0.775 |
| `Normal(0, 5)` | 7.130 | 1.945 | 0.779 |
| `Normal(0, 1)` | 7.028 | 1.917 | 0.785 |

**Maximum spread:** `alpha` 0.102, `beta` 0.028.

---

## 4. Interpretation

The vague and weakly-informative priors give an **identical** posterior (to three
decimals): with 40 informative points the likelihood dominates and the prior width is
irrelevant across that range. The deliberately **tight** `Normal(0, 1)` prior — whose SD
is smaller than the true intercept of ~7 — pulls the intercept down only modestly (to
7.028) and the slope to 1.917. Even a too-tight prior, on the standardized scale, does
not catastrophically distort the fit because the data are informative enough to overcome
it; it merely shrinks slightly toward zero.

**Why this is the standardization lesson.** All of these priors are *thinkable* because
the coefficients live on a common O(1) scale. On the **raw** scale the true slope is
~0.015 and the true intercept is ~2 (an extrapolation to dose zero), so:

- a `Normal(0, 5)` prior on the raw slope would be wildly diffuse (it allows slopes
  330x the truth), giving essentially no regularization;
- a `Normal(0, 0.5)` prior copied thoughtlessly from the standardized scale would be
  far too tight on the raw intercept's neighbourhood, or far too loose on the raw slope;
- there is no single sensible width, because the slope and intercept live on completely
  different magnitudes.

Standardizing puts both coefficients on the same O(1) footing, which is precisely what
makes a common prior width like `Normal(0, 5)` meaningful. The pitfall (un-scaled x)
destroys this and forces you to hand-tune a different, hard-to-guess width for each
coefficient.

**The usual caveat:** the robustness of the vague-vs-weak comparison is a property of
`N = 40`. At small `N` the tight prior's shrinkage would be more pronounced and the
choice would matter more. Demonstrate robustness at your actual sample size.

---

## 5. What to report to a collaborator

> "We standardized the dose, which lets us use sensible default priors on the slope and
> intercept. The estimate barely moved across a vague and a weakly-informative prior,
> and even a deliberately tight prior changed the slope by under 0.03 (standardized).
> The conclusion is driven by the data."
