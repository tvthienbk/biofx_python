# Lessons — Project 11: Varying Slopes (Correlated Random Effects, LKJ)

This report records what Project 11 teaches, the failure modes met while building
it, and how correlated random effects generalize. The headline skill is **modeling
the correlation between group-level intercepts and slopes with an LKJ prior**; the
headline hazard is **ignoring that correlation** (and, as always, the funnel).

---

## 1. What this project is really about

Projects 09 and 10 varied a single quantity by group (a mean, then an intercept).
Project 11 varies **two** — an intercept and a slope — and, decisively, lets them
**co-vary**. The new machinery is `pm.LKJCholeskyCov`, which puts a prior on the
2x2 random-effect covariance via the LKJ distribution on its correlation matrix.
The new idea is that "add a varying slope" is incomplete: you must also decide
whether intercept and slope are correlated, and the honest default is to *estimate*
that correlation rather than assume it is zero.

The model:

```
mu = [mu_a, mu_b] ~ Normal(0, 5)
chol, corr, sds ~ LKJCholeskyCov(n=2, eta=2, sd_dist=HalfNormal(1))
effects = mu + (chol @ z).T,   z ~ Normal(0,1) shape (2, G)    # non-centered
y_ij = effects[g,0] + effects[g,1]*x_ij + Normal(0, sigma)
```

---

## 2. Takeaways

### 2.1 Independence is a strong, usually wrong, default

Letting both intercept and slope vary feels like enough flexibility, but modeling
them as *independent* hard-codes `rho = 0`. The data here have `rho = 0.6`, so the
independent model is structurally incapable of the truth — and it does not even
expose a `rho` parameter to inspect. The LKJ model adds exactly one shape parameter
(`eta`) and recovers the correlation. The lesson: whenever two group-level effects
vary, ask whether they co-vary, and model it.

### 2.2 The correlation is the hardest thing to identify

With G = 8 lines, `rho` has by far the widest posterior (here ~[0.0, 0.96]). That is
not a failure — it is honest. A correlation is estimated from the *scatter of group
effects*, and 8 points carry little information about a correlation. The recovery
test reflects this: it requires only *coverage* for `rho`, not a tight z-score,
while demanding tighter recovery of the population means and SDs.

### 2.3 The LKJ eta is a real prior choice when groups are few

Prior sensitivity made this concrete: as `eta` went 1 → 2 → 8, the posterior mean
of `rho` fell 0.68 → 0.51 → 0.21, while the population means barely moved (mu_a
spread 0.038). A skeptical `eta` pulls the correlation toward 0. With many groups
the data would dominate; with 8, `eta` matters and must be reported.

### 2.4 Non-centering generalizes to the multivariate case

The funnel is not scalar-specific. Here the non-centered trick uses the Cholesky
factor: `effects = mu + (L @ z).T` with `z` standard normal. This is the
multivariate analogue of `theta = mu + tau*z`, and it keeps the LKJ model
divergence-free where a centered version diverges.

---

## 3. Surprises & failures encountered while building

### 3.1 No BLAS makes LKJ sampling slow

The environment warns "PyTensor could not link to a BLAS installation", so the
matrix operations in `LKJCholeskyCov` run on a slow fallback. This made the LKJ
refits markedly slower than the scalar hierarchical models, which forced SBC down
to 24 light simulations to stay within the time budget. The lesson for builders:
multivariate hierarchical SBC is expensive *and* sensitive to the linear-algebra
backend; budget accordingly and keep it light.

### 3.2 `LKJCholeskyCov` returns three things, and the order matters

With `compute_corr=True` it returns `(chol, corr, sds)`. Getting `rho` requires
`corr[0,1]`, and the non-centered reconstruction needs the *Cholesky factor* `chol`,
not the correlation. Wiring these wrong is a silent bug — the model still samples but
estimates the wrong covariance. Exposing `rho`, `sd_a`, `sd_b` as named
`Deterministic`s made recovery checks and debugging far easier.

### 3.3 Population means need named deterministics

`mu` is a length-2 vector (`mu[alpha]`, `mu[beta]`), which `check_recovery` cannot
address by a scalar truth key. Adding `mu_a = Deterministic(mu[0])` and `mu_b =
Deterministic(mu[1])` let the same recovery helper work unchanged — a small pattern
worth reusing whenever truths are scalars but the model parameter is vectorized.

### 3.4 The point-estimate scatter still tilts in the broken model

A subtle teaching point: even the *independent* (broken) model's recovered
`(alpha_g, beta_g)` scatter shows a tilt, because the data have one. The bug is not
that the point estimates lose the tilt — it is that the model's *predictive
covariance* assumes zero correlation, so it mis-predicts new lines. The error is in
the assumed structure, not always visibly in the point estimates.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| `LKJCholeskyCov` for correlated random effects | Any multilevel model with ≥2 varying effects (random intercept + slope is ubiquitous). |
| Non-centering via the Cholesky factor | The standard fix for multivariate hierarchical funnels. |
| "Independence is an assumption" | Every varying-slopes model; also seemingly-unrelated regressions. |
| Identifiability of correlations with few groups | Any covariance/correlation estimated from a handful of units. |
| LKJ `eta` as a regularizer | Tuning correlation priors throughout multilevel modeling. |

Project 11 completes the hierarchical arc: P09 (varying means) → P10 (varying
intercepts in a GLM) → P11 (varying, correlated slopes). The remaining
measurement-error project (P12) shifts from grouping structure to latent variables.

---

## 5. Concrete next experiments (for the reader)

- Refit the independent vs LKJ models and compare with `az.compare` (LOO): the
  correlated model should win, quantifying the cost of ignoring `rho`.
- Sweep G (5, 8, 20, 50) and watch the posterior SD of `rho` shrink — the cure for a
  fuzzy correlation is more groups.
- Sweep `eta` (1, 2, 4, 8) and trace the posterior `rho`: see the prior take over as
  the data thin out.
- Add a quadratic dose term so the covariance is 3x3 and study which of the three
  correlations are identifiable from 8 lines.
