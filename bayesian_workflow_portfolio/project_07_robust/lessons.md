# Lessons — Project 07: Robust Regression (Student-t)

This is the lessons report for the robust-regression project. It records what the
project teaches, the surprises met while building and running it, and how the
ideas generalize.

---

## 1. What this project is really about

On the surface it fits a line through noisy points. The real subject is the
**noise model** and the fact that the default Normal likelihood is *fragile*:
because it penalizes residuals quadratically, a few gross outliers can dominate
the entire fit. The Student-t likelihood, with heavy tails controlled by a
degrees-of-freedom parameter $\nu$, makes far points cheap to explain and the fit
robust. The project teaches you to *recognize* outlier domination, *fix* it with a
heavy-tailed likelihood, and *confirm* the fix with LOO.

Structurally it rhymes with Project 06: a flexible model (Student-t / NB) nests a
rigid one (Normal / Poisson), both converge fine, only model criticism exposes the
rigid one, and `az.compare` adjudicates.

The eight workflow steps map to artifacts as usual; SBC, prior sensitivity, and
the broken notebook round it out.

---

## 2. Takeaways

### 2.1 The Normal likelihood's quadratic penalty is the whole problem

A Normal log-likelihood contributes $-\tfrac{1}{2}(\text{residual}/\sigma)^2$ per
point. A residual of 15 SD contributes $-112$ to the log-density — astronomically
costly — so the optimizer/sampler will tilt the line and inflate $\sigma$ to avoid
it. The Student-t's log-density grows only *logarithmically* in the residual, so a
far point costs little and the bulk of the data drives the fit. Robustness is not
a trick; it is a direct consequence of tail weight.

### 2.2 nu must be a free parameter

The single most transferable practical lesson. A "Student-t" with $\nu$ fixed
large is a Normal in disguise. Make $\nu$ a parameter with a prior that permits
small values, and the data will choose the tail weight. A *small posterior $\nu$
is itself a diagnostic*: it is the model telling you outliers are present.

### 2.3 Convergence is not adequacy (again)

As in Project 06, the non-robust model converges perfectly. $\hat R$ and ESS are
blind to the fact that the fit is inadequate. The tells are in the *estimates*
(inflated $\sigma$ ~3 vs clean 0.6, and a slope ~6× more uncertain than the robust
fit's; with these balanced low-leverage outliers the slope *mean* is not itself
dragged, but with one-sided/high-leverage outliers it would be), the *fitted line
overlay*, and the *LOO comparison* — never in the convergence diagnostics.

### 2.4 Don't compare the Student-t scale to the Normal SD

A subtle but important point. The Student-t's $\sigma$ is a *scale*, not the
marginal standard deviation; the marginal variance is $\sigma^2\nu/(\nu-2)$ for
$\nu>2$ and undefined for smaller $\nu$. With heavy tails the estimated scale
legitimately sits below the Normal noise SD. Recovery tests should target the
scientifically meaningful, scale-free parameters (slope, intercept), not $\sigma$.

### 2.5 Robust likelihoods fix vertical outliers, not leverage

The outliers here are vertical and low-leverage by design, which the Student-t
handles cleanly. High-leverage points at extreme $x$ act through the *design
matrix*, not the residual distribution, and a robust likelihood alone may not save
you — you would need a contamination model or robust-design methods. Knowing the
*type* of corruption you face is part of choosing the tool.

---

## 3. Surprises & failure modes encountered while building

### 3.1 The "clean" data weren't automatically clean

The first data seed produced clean points whose own least-squares slope was 2.2,
not 2.0 — an unlucky noise draw. The robust model dutifully recovered ~2.3 (the
truth *of that dataset*), and the recovery test failed against the nominal 2.0.
The lesson: when the recovery target is a "clean line," make sure the clean points
actually realize it. We searched seeds for one where the clean-point OLS slope is
within ~0.05 of the true slope, so the test measures robustness to *outliers*
rather than sensitivity to a noise fluke.

### 3.2 SBC's scale parameter failed — because the test harness was wrong

The most instructive surprise. An early SBC simulated data with a *fixed* $\nu=6$
while the model fit $\nu$ from its prior. The rank histogram for $\sigma$ came out
non-uniform (p=0.001) — alarming, until we realized the simulator and model
disagreed about the data-generating process. SBC's core requirement is that the
simulator draw **every** parameter (including $\nu$) from the model's exact prior.
Once $\nu$ was drawn from the same Gamma in both places, the calibration was clean.
A non-uniform SBC histogram can mean a broken sampler *or* a broken harness; check
the harness first.

### 3.3 Prior sensitivity on nu is benign; the danger is fixing nu

We expected a Normal-leaning $\nu$ prior to drag the slope. It barely did — the 6
clear outliers force the tails heavy regardless of a mildly Normal-leaning prior.
The real robustness-killer is not a soft prior but a *hard constraint* ($\nu$
fixed large), which removes the data's freedom to express heavy tails. This
reframed the broken-notebook bug from "wrong prior" to "wrong model structure."

---

## 4. How this generalizes

- **Project 06 (Negative-Binomial)** is the count analogue: a flexible likelihood
  nesting a rigid one, chosen via LOO. The "convergence ≠ adequacy" and
  "PPC/LOO-first" lessons are shared.
- **Project 12 (errors-in-variables)** handles the *leverage* side of outliers
  that a robust likelihood cannot.
- The **scale-mixture-of-Normals** view of the Student-t connects directly to
  hierarchical and mixture models later in the portfolio.

The portable rule: **when data may contain outliers, model the tails — use a
Student-t (or a mixture) with the tail-weight parameter free — and confirm the
choice with a fitted-line overlay and an explicit LOO comparison. Never fix the
degrees of freedom large.**
