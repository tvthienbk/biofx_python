# Project 05 — Binary Outcomes (Logistic Regression / Bernoulli GLM)

> **The guideline.** This is the long-form teaching document for Project 05. It
> walks the full eight-step Bayesian workflow on a logistic regression, with the
> project's signature skill — **link functions and priors on the probability
> scale** — woven through every step. Read it alongside `notebook.ipynb` (the
> clean run), `notebook_broken.ipynb` (the debugging exercise), and the
> per-artifact reports (`SBC_REPORT.md`, `PRIOR_SENSITIVITY.md`, `BROKEN_BUGS.md`).

---

## 0. Where this project sits in the portfolio

Project 01 estimated a single probability $\theta$ with a Beta–Binomial model.
That was the whole workflow on one parameter, with a conjugate answer to check
against. Project 05 is the first **regression**: the probability is no longer a
single number but a *function of a covariate*. To make a linear predictor produce
a valid probability we need a **link function**, and the moment we introduce a
nonlinear link, our intuition about "wide = uninformative" priors breaks. That
broken intuition is the lesson of this project.

The environment (PyMC 5.28, ArviZ 0.23, numpy 2.x, scipy) is shared across the
portfolio; see the top-level `environment.yml` / `requirements.txt`. Do not
re-create those here.

---

## 1. Step 1 — Problem & the data-generating story

### 1.1 The scientific scenario

A ligand is incubated with a receptor in each of $N$ independent wells. In each
well the ligand either **binds** (outcome $y=1$) or **does not bind** ($y=0$).
The chance of binding depends on a continuous covariate $x$ — think of a
standardized concentration, a hydrophobicity score, or a docking score. We want
to learn how binding probability changes with $x$, with honest uncertainty.

### 1.2 The generative model

The data are generated on the **log-odds (logit) scale**:

$$
\operatorname{logit}(p_i) \;=\; \log\frac{p_i}{1-p_i} \;=\; \alpha + \beta\,x_i,
\qquad
y_i \sim \text{Bernoulli}(p_i).
$$

We standardize $x$ to mean 0, SD 1. This is not cosmetic: it makes $\alpha$ the
log-odds of binding **at the mean covariate**, and it decorrelates $\alpha$ from
$\beta$ in the posterior, which keeps NUTS happy. The known truth is

| parameter | value | meaning |
|-----------|-------|---------|
| $\alpha$  | 0.3   | log-odds at mean $x$; $p=\operatorname{logit}^{-1}(0.3)\approx0.57$ |
| $\beta$   | 1.4   | each $+1$ SD of $x$ multiplies the **odds** by $e^{1.4}\approx 4.1$ |

`data/generate_data.py` implements exactly this and saves `data/data.npz`.
Because we *chose* the truth, every later step can be checked against it.

### 1.3 Assumptions, stated out loud

The workflow demands we flag assumptions, not bury them:

1. **Independence.** Wells do not influence each other. (Plate-position or
   batch effects would violate this; a later hierarchical project handles that.)
2. **Linearity on the log-odds scale.** The effect of $x$ is linear in
   *log-odds*, not in probability. This is the modeling choice the link encodes.
3. **No measurement error in $x$.** We treat the covariate as known exactly.
   (Project 12 relaxes this with an errors-in-variables model.)
4. **No omitted confounder.** Any unmodeled variable correlated with both $x$
   and binding would bias $\beta$.
5. **Binary, correctly recorded outcomes.** No ambiguous / partial binding.

---

## 2. Step 2 — Model specification: likelihood, link, and justified priors

### 2.1 Likelihood and link

$$
y_i \sim \text{Bernoulli}(p_i),\qquad
p_i = \operatorname{logit}^{-1}(\eta_i) = \frac{1}{1+e^{-\eta_i}},\qquad
\eta_i = \alpha + \beta\,x_i .
$$

The **inverse-logit (logistic sigmoid)** is the link's inverse: it maps the
unconstrained linear predictor $\eta\in(-\infty,\infty)$ into a valid probability
$p\in(0,1)$. We *never* place a prior on $p$ directly and we *never* let a raw
linear combination play the role of a probability. (Both of those are seeded bugs
in the broken notebook — see §8.)

Why the logit link specifically?

- It guarantees $p\in(0,1)$ for any real $\eta$.
- Coefficients are **log-odds ratios**, the natural currency of binary data.
- It is the *canonical* link for the Bernoulli/Binomial family, giving the
  simplest sufficient statistics and well-behaved geometry.

Alternatives exist (probit = Normal CDF link; cloglog for asymmetric tails). The
logit is the default and the most interpretable; we note the others but use logit.

### 2.2 Priors — and why "wide" is a trap here

We use $\alpha,\beta \sim \text{Normal}(0,1.5)$. The temptation is to reach for a
"non-informative" $\text{Normal}(0,10)$. **On the log-odds scale that looks
harmless. On the probability scale it is a disaster.** Push $\text{Normal}(0,10)$
through the sigmoid and the implied $p$ is a U-shaped distribution pinned almost
entirely at 0 and 1: the "vague" prior secretly asserts the assay is nearly
deterministic before any data arrive. $\text{Normal}(0,1.5)$ instead yields an
implied $p$ spread broadly and unimodally around 0.5 — the genuinely agnostic
belief. This is the single most important idea in the project and is demonstrated
quantitatively in Step 3.

`model.py` exposes `build_model(data, prior_sd=1.5)` and
`fit(data, prior_sd=..., ...)` so the notebook, test, SBC, and prior-sensitivity
scripts all share one definition.

---

## 3. Step 3 — Prior predictive checks (on the probability scale)

A prior predictive check simulates parameters from the prior, pushes them through
the model, and asks whether the *implied data* are reasonable. For a GLM the
non-negotiable version of this check is **on the response (probability) scale**,
because that is where the link's nonlinearity bites.

Concretely: draw $\alpha\sim\text{Normal}(0,\text{sd})$, compute
$p=\operatorname{logit}^{-1}(\alpha)$ (the binding probability at mean $x$), and
histogram $p$.

- **Normal(0, 1.5):** $p$ spreads broadly across $(0,1)$, mound near 0.5. Good.
- **Normal(0, 10):** $p$ is a sharp U at 0 and 1. Pathological.

The broken notebook's Bug 3 is precisely the failure to do this check on the
right scale — it histograms the log-odds (a pretty bell curve) and so *hides* the
pathology. The lesson: **a prior predictive check is only as good as the scale you
view it on.**

---

## 4. Step 4 — Inference (NUTS settings)

Settings: `draws=1000, tune=1000, chains=4, random_seed=101, progressbar=False`.

- **Tune = 1000** lets NUTS adapt step size and mass matrix; with standardized
  $x$ the geometry is benign and this is ample.
- **4 chains** give a reliable split-$\hat R$ and let us see chain disagreement.
- **Standardized $x$** is itself a sampling decision: it decorrelates the
  posterior and removes the funnel-ish geometry that un-centered predictors cause.

No `target_accept` bump is needed for this easy model (later projects need it).

---

## 5. Step 5 — Computational diagnostics

Always compute and read:

- **$\hat R$** (split potential-scale-reduction): want $\approx 1.00$; $>1.01$
  means chains disagree.
- **ESS** (bulk and tail effective sample size): want $\gtrsim 400$ each.
- **Divergences** (`idata.sample_stats.diverging.sum()`): expect 0 here; any
  divergence in a logistic GLM usually signals an extreme prior or separation.
- **Trace plots**: well-mixed "fuzzy caterpillars".

**What to do when they fail.** High $\hat R$ / low ESS in a logistic GLM most
often comes from (a) un-standardized predictors causing $\alpha$–$\beta$
correlation — fix by centering/scaling $x$; (b) **separation**, where a covariate
perfectly predicts the outcome and the MLE runs to $\pm\infty$ — fix with a
weakly-informative prior (which we have), the Bayesian cure for separation.
Divergences call for raising `target_accept` to 0.95 and re-examining priors.

---

## 6. Step 6 — Posterior predictive checks

Two complementary views:

1. **`az.plot_ppc`** on the 0/1 outcomes — the replicated proportion of 1s should
   bracket the observed proportion.
2. **A calibration curve** — bin wells by predicted probability $\hat p$ and plot
   the observed binding fraction in each bin against $\hat p$. A well-specified
   logistic model tracks the diagonal. Systematic departures (e.g. an S-shape)
   signal a missing nonlinearity in $x$.

The calibration view is the GLM-specific PPC worth internalizing: for binary data
the raw outcomes are uninformative individually, so we check the model's *probability
predictions* against *binned empirical frequencies*.

---

## 7. Step 7 — Model criticism, comparison & prior sensitivity

With a single model there is no LOO/WAIC race (later projects with $\ge 2$ models
use `az.compare`). Criticism here means:

- **Recovery against known truth** via `shared.bayes_utils.check_recovery`: the
  94% HDIs for $\alpha,\beta$ should cover 0.3 and 1.4 with small $|z|$.
- **Prior sensitivity** (`prior_sensitivity.py`, `PRIOR_SENSITIVITY.md`): refit
  under tight / weak / vague coefficient priors. The posterior for $\beta$ is
  essentially identical for weak vs vague (the $N=120$ likelihood dominates),
  while the tight Normal(0, 0.5) visibly shrinks $\beta$ toward 0. The deeper
  point — that the vague prior is pathological *a priori* — is the Step 3 story,
  not a Step 7 posterior difference. This distinction (a prior can be both
  "harmless once you have data" *and* "absurd before data") is worth stating
  explicitly to collaborators.

---

## 8. Step 8 — Decision & communication

The posterior is the input to a decision, not the deliverable. For this scenario:

- **$P(\beta>0\mid\text{data})$** — is binding genuinely increasing in $x$? Here
  $\approx 1$.
- **The $p=0.5$ crossover**, $x_{50}=-\alpha/\beta$, with a 94% interval — the
  covariate level at half-maximal binding, the quantity an experimentalist will
  actually use to set a working concentration.

`summary_onepager.md` translates this into a non-technical recommendation.

---

## 9. Common pitfalls (the project's key trap)

1. **Treating a "wide" prior as uninformative under a nonlinear link.** This is
   THE pitfall. Normal(0, 10) on logistic coefficients is an *edge-seeking* prior
   on probability. Always view priors on the response scale.
2. **Modeling the probability directly.** Writing `p = alpha + beta*x` and feeding
   it to `Bernoulli(p)` discards the link; $p$ leaves $(0,1)$ and the model is
   invalid. Always squash through the sigmoid.
3. **Prior predictive checks on the wrong scale.** A check on the log-odds hides
   exactly the pathology you are trying to catch.
4. **Forgetting to standardize $x$**, inviting $\alpha$–$\beta$ correlation and
   sampler trouble.
5. **Ignoring separation**, which produces runaway coefficients under flat priors;
   the weakly-informative prior is the fix.

---

## 10. File map

| File | Role |
|------|------|
| `data/generate_data.py` | Bernoulli/logistic DGP, fixed seed, known truth |
| `model.py` | `build_model` / `fit`; logit link, Normal(0,1.5) priors |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow |
| `notebook_broken.ipynb` | seeded-bug debugging exercise |
| `test_recovery.py` | fast recovery test of $(\alpha,\beta)$ |
| `sbc.py` / `SBC_REPORT.md` | simulation-based calibration |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | prior-width comparison |
| `BROKEN_BUGS.md` | instructor answer key for the broken notebook |
| `rubric.md` | grading rubric + extension prompt |
| `lessons.md` | narrative lessons report |
| `summary_onepager.md` | non-technical decision summary |
