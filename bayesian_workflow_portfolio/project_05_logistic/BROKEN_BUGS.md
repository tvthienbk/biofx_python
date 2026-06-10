# Broken Notebook — Answer Key (Project 05)

`notebook_broken.ipynb` contains three seeded bugs, all centred on this project's
pitfall: link functions and priors on the probability scale. This is the
instructor key — students should attempt the fixes before reading it.

---

## Bug 1 — Absurdly wide coefficient priors

**Code.** `alpha = pm.Normal('alpha', 0.0, 10.0)`, same for `beta`.

**Symptom.** On its own this would "work" numerically, but it makes the model
behave as if it already believes binding is near-deterministic. Combined with
Bug 2 it amplifies the divergences; if Bug 2 were fixed in isolation, you would
see wider-than-necessary posteriors and a prior predictive (done correctly) that
piles implied $p$ at 0 and 1.

**Diagnostic.** A prior predictive check **on the probability scale**: draw
$\alpha\sim\text{Normal}(0,10)$, compute $\operatorname{logit}^{-1}(\alpha)$, and
histogram. You see a U pinned at 0 and 1 instead of a spread around 0.5.

**Fix.** Use weakly-informative priors: `pm.Normal('alpha', 0, 1.5)` and
`pm.Normal('beta', 0, 1.5)`.

---

## Bug 2 — No link function (modeling the probability directly)

**Code.**
```python
p = alpha + beta * x          # WRONG: a raw linear predictor, not a probability
pm.Bernoulli('y', p=p, observed=y)
```

**Symptom.** `p = alpha + beta*x` is not constrained to $(0,1)$. For many draws
it is negative or exceeds 1, so `Bernoulli(p)` receives an out-of-support
probability. The sampler diverges en masse, `logp` is `-inf` for swaths of
parameter space, $\hat R$ is large, ESS collapses, and (depending on PyMC
version) you may get an outright sampling error or absurd coefficient estimates.

**Diagnostic.** Read the error / divergence count; inspect the range of the
implied `p` — it leaves $[0,1]$. The conceptual tell: there is no sigmoid
anywhere, so the *link function* has been dropped.

**Fix.** Restore the inverse-logit link:
```python
p = pm.math.sigmoid(alpha + beta * x)   # = logit^{-1}(eta)
pm.Bernoulli('y', p=p, observed=y)
```
Equivalently use `pm.Bernoulli('y', logit_p=alpha + beta*x, ...)`, which applies
the link internally and is numerically more stable.

---

## Bug 3 — Prior predictive check on the wrong scale

**Code.**
```python
a = rng.normal(0, 10.0, size=5000)
plt.hist(a)                 # histograms the LOG-ODDS, not sigmoid(log-odds)
```

**Symptom.** The "check" shows a clean, reassuring bell curve and the student
concludes the prior is fine — when in fact it is pathological. The check hides the
very problem it should expose.

**Diagnostic.** Ask: *what scale is this histogram on?* It is the log-odds. The
quantity that matters for a binary outcome is the **probability**.

**Fix.** Transform before plotting:
```python
p0 = 1 / (1 + np.exp(-a))   # sigmoid -> implied probability at mean x
plt.hist(p0)                # now the U-shape at 0/1 is visible for Normal(0,10)
```
Repeat with `sd=1.5` to see the sensible, mound-shaped spread of the good prior.

---

## Meta-lesson

All three bugs share one root cause: **forgetting that a GLM lives on two scales.**
Parameters and priors are on the linear-predictor (log-odds) scale; meaning,
checks, and decisions are on the response (probability) scale. Every prior
predictive check, every prior justification, and every sanity plot must cross to
the probability scale through the link.
