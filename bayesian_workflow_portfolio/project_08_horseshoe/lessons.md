# Lessons — Project 08: Many Predictors (Regularized Horseshoe)

This is the lessons report for the high-dimensional / shrinkage project. It records
what the project teaches, the surprises met while building and running it, and how
the ideas generalize.

---

## 1. What this project is really about

On the surface it picks which of 20 predictors matter. The real subject is two
things at once: **shrinkage priors** as a principled, single-fit alternative to
ad-hoc feature selection, and the **double-dipping / selection-bias** trap that
makes naive selection so dangerous. A third, computational lesson rides along: the
horseshoe's funnel geometry forces the **non-centered parameterization**, the same
reparameterization idea that recurs throughout hierarchical modeling.

The eight workflow steps map to artifacts as usual; SBC, prior sensitivity, and the
broken notebook (centered funnel + double-dipping) round it out.

---

## 2. Takeaways

### 2.1 Shrinkage is selection done honestly

A wide-Normal "ridge" prior treats every coefficient as equally free, so finite-data
noise leaves all 20 coefficients non-zero — you cannot tell signal from noise. The
horseshoe's global/local scale structure crushes the irrelevant coefficients toward
zero while letting the few real ones escape, *all within one joint posterior*. This
replaces the dangerous "fit, eyeball, re-test" ritual with a single coherent fit
that reports uncertainty about which predictors are active. Selection and
estimation happen together, with multiplicity already accounted for.

### 2.2 Non-centered or bust

The single most transferable computational lesson. Sampling $\beta_j\sim
N(0,\tau\lambda_j)$ directly (centered) ties each coefficient to its own scale in a
pinched funnel that NUTS cannot traverse — a flood of divergences. Sampling a
standardized $z_j\sim N(0,1)$ and forming $\beta_j=z_j\tau\tilde\lambda_j$
(non-centered) decouples the geometry. Whenever a parameter's *scale* is itself
uncertain — hierarchical models, horseshoes, varying slopes — reach for the
non-centered form first.

### 2.3 Double-dipping fakes significance

The signature pitfall. Selecting the largest coefficient and then re-testing it on
the same data is circular: the predictor was chosen *because* it looked large in
this sample, so re-testing it in isolation manufactures a narrow interval that
excludes zero. Even pure noise produces a "winner" that looks significant this way.
The remedy is never to select-then-refit; let the shrinkage prior select inside one
fit and report the full posterior.

### 2.4 LOO's payoff here is parsimony, not a big elpd gap

A surprise worth internalizing: with strong signals and enough data, the ridge and
horseshoe predict the response about equally well, so the `elpd_loo` gap is modest.
The horseshoe's advantage shows up in **`p_loo`** — it achieves the same fit with
far fewer effective parameters. Shrinkage buys parsimony at equal fit, which
generalizes better and which LOO's complexity accounting rewards. Don't expect (or
require) a dramatic predictive win to justify shrinkage.

### 2.5 Global shrinkage has a sweet spot

Cranking `tau0` toward zero shrinks noise harder — but also kills genuine weak
signals. The principled `tau0` encodes a prior guess at the number of relevant
predictors (Piironen & Vehtari's formula). More shrinkage is not strictly better.

---

## 3. Surprises & failure modes encountered while building

### 3.1 ArviZ var_names don't match coordinate labels

A practical snag in the recovery test: `az.summary(idata, var_names=['beta[2]'])`
fails, because ArviZ matches the *variable* name `beta`, not the coordinate label
`beta[2]`. The fix was a small helper that lifts the selected coefficients into
their own scalar posterior variables (named like the truth keys) before handing
them to `check_recovery`. A reminder that indexed parameters need care when you
want per-element checks.

### 3.2 An xarray coordinate collision

After `isel(beta_dim_0=j)`, the leftover `beta_dim_0` coordinate caused an xarray
merge error when assembling the scalar dataset. Dropping the stale coordinate
(`drop_vars('beta_dim_0', errors='ignore')`) resolved it. Small, but the kind of
thing that silently breaks a test harness.

### 3.3 The horseshoe is slow, and that shaped the SBC/sensitivity design

Even non-centered, the horseshoe with `target_accept=0.95` samples slowly. SBC and
prior-sensitivity had to be trimmed (small $P$, few sims, modest draws) to stay
within the time budget. The principle held: SBC validates the machinery over a
*representative* slice, not exhaustively. For the prior-sensitivity sweep, a
slightly lower `target_accept` (0.9) and fewer draws kept runtime in check without
changing the qualitative conclusion.

### 3.4 The ridge wasn't terrible — which is the point

It would be tempting to make the ridge fail dramatically. It doesn't: it recovers
the three signals fine and only leaves the noise coefficients mildly non-zero. The
honest lesson is subtler than "ridge bad, horseshoe good" — it is that the
horseshoe gives *cleaner sparsity and better parsimony*, which matters most for
interpretation and out-of-sample generalization, not necessarily for in-sample fit.

---

## 4. How this generalizes

- The **non-centered parameterization** is the through-line to every hierarchical
  project (09–11): varying intercepts and slopes have the same funnel, cured the
  same way.
- The **LOO / `az.compare`** machinery is shared with Project 06 (Poisson vs NB) and
  Project 07 (Normal vs Student-t); the new wrinkle here is reading `p_loo` as the
  decisive quantity.
- The **double-dipping** lesson generalizes far beyond regression: any pipeline that
  uses the same data to choose a hypothesis and to test it (gene selection,
  threshold tuning, post-hoc subgroup analysis) inherits the bias. The Bayesian
  joint-fit posture is the general antidote.

The portable rule: **for many-predictor problems, use a shrinkage prior with a
non-centered parameterization to do selection inside one joint fit, judge it by
parsimony (`p_loo`) as much as fit, and never select-then-retest on the same data.**
