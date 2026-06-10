# Lessons — Project 10: Varying Intercepts (Hierarchical Logistic)

This report records what Project 10 teaches, the failure modes met while building
it, and how hierarchical GLM structure generalizes. The headline skill is
**group-level structure inside a GLM**; the headline hazard is **over-pooling with
few groups** (compounded by the centered-parameterization funnel).

---

## 1. What this project is really about

Project 09 put a hierarchy on a *mean*. Project 10 puts the same hierarchy on an
*intercept inside a logistic link*. That one move — a group-varying intercept in a
GLM — is the workhorse of applied multilevel modeling: patients within hospitals,
wells within plates, families within an assay. Everything from Project 09 carries
over (exchangeability, shrinkage, the funnel, non-centering), now wrapped in a
non-conjugate, non-linear link.

The model:

```
mu    ~ Normal(0, 1.5)        # population-mean intercept (log-odds)
tau   ~ HalfNormal(1)         # between-family SD of intercepts
beta  ~ Normal(0, 1.5)        # global covariate slope
alpha_g = mu + tau * z_g,  z_g ~ Normal(0,1)      # non-centered intercepts
logit(p_i) = alpha_{g[i]} + beta * x_i
y_i ~ Bernoulli(p_i)
```

---

## 2. Takeaways

### 2.1 Priors live on the log-odds scale, and 1.5 is already wide

A beginner reflex is to slap `Normal(0, 10)` on a logistic intercept "to be
uninformative". On the log-odds scale that is the opposite of uninformative: it
puts almost all prior probability mass on binding rates of essentially 0 or 1. The
prior predictive check (Step 3) makes this visible — with a sane prior the implied
dataset binding rates spread across [0,1]; with a vague one they pile at the
extremes. `Normal(0, 1.5)` already spans ~0.05 to ~0.95 in probability.

### 2.2 Over-pooling is a *prior* failure as much as a model failure

The project's pitfall is pooling too aggressively. The cleanest way to *cause* it is
not a bad likelihood but a too-tight prior on `tau`: `HalfNormal(0.05)` collapses
every family intercept onto `mu_hat`. With only 10 families the data cannot overrule
it. The lesson: in a hierarchical GLM, **the group-level scale prior is a pooling
dial**, and tightening it does not "regularize" — it over-pools.

### 2.3 Fixed effects are robust; group-level scales are fragile (with few groups)

The prior-sensitivity run drove this home: across tight/default/vague `tau` priors,
the global slope `beta` barely moved (0.895 → 0.960), informed by all 120
observations, while the family-intercept spread swung from 0.054 to ~1.0. Population
*fixed effects* are well-identified; the *between-group scale* is weakly identified
when groups are few. Report the slope with confidence and the spread with a caveat.

### 2.4 The funnel does not care about the link

Non-centering was a Normal-likelihood trick in Project 09, but the funnel is a
property of the *prior geometry* (`alpha_g` coupled to `tau`), not the likelihood.
It reappears unchanged in the logistic model, and the same non-centered
reparameterization fixes it. This is why non-centering is the default move for
*any* multilevel model.

---

## 3. Surprises & failures encountered while building

### 3.1 Recovery of `mu` and `tau` is loose, and that is honest

With 10 families the posterior for `mu` is wide (SD ~0.29) and `tau` is recovered
low (~0.54 vs truth 0.9) though still covered. This is not a bug — 10 group-level
"data points" simply cannot pin down a population mean and SD tightly. The recovery
test asserts *coverage* and a bounded z-score, not a tight point estimate, which is
the right standard for a hierarchical model with few groups.

### 3.2 The two broken-notebook bugs reinforce each other

Bug 1 (tight `tau` prior) pushes `tau` toward 0; Bug 2 (centered parameterization)
makes the funnel worst exactly at small `tau`. Together they produce both the
over-pooling pathology *and* divergences. Untangling them is instructive: fixing
only the parameterization still leaves the intercepts over-pooled; fixing only the
prior still leaves divergences. Both must be addressed — a good reminder that
"the diagnostics look bad" can have more than one cause.

### 3.3 Empirical log-odds need a continuity correction

To plot per-family no-pooling intercepts I converted empirical rates to log-odds,
which blows up for families at rate 0 or 1. A small `eps=0.5` continuity correction
keeps the plot finite — a minor but real bit of GLM hygiene that the hierarchical
model sidesteps entirely (it never computes a raw empirical log-odds).

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Group-varying intercepts in a GLM | The default multilevel model; everywhere grouped binary/count data appear. |
| Priors on the log-odds / link scale | Every GLM — logistic (here), Poisson/NegBinom (P06), ordinal. |
| Over-pooling as a prior-scale failure | Any hierarchy with few groups, including LKJ scales (P11). |
| Non-centering across likelihoods | Confirms non-centering is link-agnostic — used in every later multilevel model. |
| Fixed-effect robustness vs scale fragility | The standard way to triage which hierarchical estimates to trust. |

Project 10 is the bridge from hierarchical *means* (P09) to hierarchical *regression*
(P11, varying slopes). Master varying intercepts in a GLM here and the only new idea
in P11 is letting the slopes vary too — and modeling their correlation with the
intercepts.

---

## 5. Concrete next experiments (for the reader)

- Sweep the `tau` prior SD from 0.05 to 5 and plot the family-intercept spread
  against it: watch over-pooling smoothly give way to honest spread.
- Add families one at a time (G = 5, 10, 20, 40) and watch the posterior for `tau`
  tighten — the cure for scale fragility is more groups, not a tighter prior.
- Give each family its own slope `beta_g` and compare LOO — a preview of Project 11.
- Break SBC on purpose with the centered + tight-prior model and confirm `tau`'s
  ranks skew (the over-pooling bias made visible in calibration).
