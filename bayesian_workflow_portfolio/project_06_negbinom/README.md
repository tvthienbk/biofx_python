# Project 06 — Overdispersed Counts (Negative-Binomial GLM)

> **The guideline.** Long-form teaching document for Project 06. It walks the full
> eight-step Bayesian workflow on a count regression, with the project's signature
> skill — **overdispersion and count models** — woven through. The defining move
> is that we fit **two** models (Poisson and Negative-Binomial) and let LOO decide.
> Read it with `notebook.ipynb`, `notebook_broken.ipynb`, and the per-artifact
> reports (`SBC_REPORT.md`, `PRIOR_SENSITIVITY.md`, `BROKEN_BUGS.md`).

---

## 0. Where this project sits in the portfolio

Project 05 introduced the link function for binary data (the logit). Project 06
keeps the *log link* idea but moves to **counts**, and introduces the first
genuine **model comparison**: Poisson vs Negative-Binomial, adjudicated by
`az.loo` / `az.compare`. The scientific motivation is that almost all real count
data — RNA-seq reads, colony counts, spike trains — are **overdispersed**: their
variance exceeds their mean. The Poisson cannot represent that; the NB can. This
project teaches you to *detect* overdispersion and to *choose* the right family
with a quantitative criterion rather than by eye.

Environment (PyMC 5.28, ArviZ 0.23, numpy 2.x, scipy) is shared; see the
top-level `environment.yml` / `requirements.txt`.

---

## 1. Step 1 — Problem & the data-generating story

### 1.1 Scenario

We measure read counts for a gene across $N=150$ samples. Expression depends on a
continuous covariate $x$ (a standardized treatment dose or latent condition
score). The counts are overdispersed by construction.

### 1.2 Generative model

$$
\log(\mu_i)=\beta_0+\beta_1 x_i,\qquad
y_i\sim\text{NB}(\mu_i,\alpha),\qquad
\operatorname{Var}(y_i)=\mu_i+\frac{\mu_i^2}{\alpha}.
$$

PyMC parameterizes the NB by mean $\mu$ and dispersion $\alpha$. **Small $\alpha$
= strong overdispersion; $\alpha\to\infty$ recovers the Poisson** (Var = mean).
We standardize $x$ so $\beta_0$ is the log-mean at the average covariate. Known
truth: $\beta_0=2.2$ ($\mu\approx 9$ at mean $x$), $\beta_1=0.8$ (each $+1$ SD of
$x$ multiplies the mean by $e^{0.8}\approx 2.2$), $\alpha=2.0$ (strongly
overdispersed; the synthesized data have var/mean $\approx 14$).

`data/generate_data.py` builds this and saves `data/data.npz`. Note the
`(mu,\alpha) \to (r,p)` conversion needed for numpy's `negative_binomial`:
$p=\alpha/(\alpha+\mu)$, $r=\alpha$.

### 1.3 Assumptions, stated out loud

1. **Independence** of samples.
2. **Log-linearity of the mean** in $x$ (the link choice).
3. **Constant dispersion** — a single $\alpha$ for all samples. (Gene-specific or
   mean-dependent dispersion is a real extension; see `rubric.md`.)
4. **No zero-inflation** beyond what the NB itself produces.
5. **Counts correctly measured** (no library-size normalization issue ignored;
   in real RNA-seq you would add an offset for sequencing depth).

---

## 2. Step 2 — Two models: Poisson and Negative-Binomial

Both models share the log-linear mean $\log(\mu_i)=\beta_0+\beta_1 x_i$. They
differ only in the likelihood:

- **Poisson:** $y_i\sim\text{Poisson}(\mu_i)$, forcing $\operatorname{Var}=\mu$.
- **Negative-Binomial:** $y_i\sim\text{NB}(\mu_i,\alpha)$, with a free dispersion.

`model.py` exposes one `build_model(data, model="nb" | "poisson")` and a matching
`fit(...)`, so the notebook, test, SBC and prior-sensitivity scripts all share a
single definition and we can fit either family with one call.

### Priors (weakly informative on the log scale)

| parameter | prior | rationale |
|-----------|-------|-----------|
| $\beta_0$ | $\text{Normal}(0,2)$ | broad on the log-mean; $e^{\pm4}$ spans plausible means |
| $\beta_1$ | $\text{Normal}(0,1)$ | a $\pm1$ SD effect is $\sim e^{\pm1}$ fold, a wide but sane range |
| $\alpha$  | $\text{Gamma}(2,0.1)$ | mean 20, heavy-tailed; supports both mild and strong dispersion |

Because the NB nests the Poisson ($\alpha\to\infty$), the comparison is fair: if
the data were truly equidispersed, the NB would simply push $\alpha$ large and the
two models would tie. They do not tie here — which is the whole point.

---

## 3. Step 3 — Prior predictive checks

Count priors are deceptively easy to set absurdly: a wide prior on $\beta_0$
exponentiates into astronomically large means. We simulate counts from the NB
prior and confirm the implied counts are heavy-tailed but plausible (we clip the
extreme upper tail only for plotting). The check guards against a prior that, post
exponentiation, implies counts in the millions.

---

## 4. Step 4 — Inference (NUTS settings)

`draws=1000, tune=1000, chains=4, random_seed=101, progressbar=False`, for *both*
models. Standardized $x$ and a log link give benign geometry; default NUTS
suffices. We keep both `InferenceData` objects for the comparison in Step 7.

A crucial teaching note: **the Poisson model converges perfectly.** Its $\hat R$
is 1.00, ESS is healthy, divergences are zero. Convergence is *not* how the
Poisson reveals its inadequacy. That is the trap of the broken notebook (§8).

---

## 5. Step 5 — Computational diagnostics

Report $\hat R$, ESS (bulk/tail) and divergences for both models. Both pass. The
only diagnostic difference you might notice is an inflated `p_loo` (effective
number of parameters) for the Poisson in Step 7 — a LOO-level symptom of
misspecification, not a sampling problem.

---

## 6. Step 6 — Posterior predictive checks (where Poisson fails)

This is where the misspecification becomes visible.

- **`az.plot_ppc`** for the Poisson shows replicated count distributions that are
  far **too narrow** — they cannot reach the observed heavy tail.
- The NB's replicated distributions cover the observed spread.
- We quantify it: compute the **posterior-predictive variance** for each model and
  compare to the observed variance. The Poisson's predicted variance roughly
  equals its predicted mean (~10), an order of magnitude below the observed
  variance (~150). The NB matches.

The portable lesson: **convergence diagnostics check the sampler; posterior
predictive checks check the model.** You need both, and only the PPC catches
forced equidispersion.

---

## 7. Step 7 — Model comparison with LOO

We rank the models with PSIS-LOO via `az.compare({...}, ic="loo")`:

- `negbinom` is **rank 0**.
- The Poisson's `elpd_diff` is large and many `dse` (diff standard errors) below
  zero, so the preference is decisive, not marginal.
- The Poisson's `p_loo` may be inflated — high-influence observations (the
  large counts the Poisson cannot accommodate) drive up its effective complexity.

Watch for Pareto-$k$ warnings: if many $k>0.7$, LOO's importance sampling is
unreliable and you would fall back to refitting or `az.compare(..., method="BB-pseudo-BMA")`.
For this well-behaved example LOO is trustworthy.

This is the formal, quantitative version of the visual PPC story: ignoring
overdispersion is not just cosmetically wrong, it costs measurable predictive
accuracy.

---

## 8. Step 8 — Decision & communication

The effect a collaborator wants is the **fold-change per unit $x$**:
$e^{\beta_1}\approx 2.2$, with a 94% interval, and $P(\beta_1>0)\approx 1$.

The decision-level message is twofold: (1) expression rises ~2.2-fold per SD of
$x$; (2) we used the NB, so the reported uncertainty is honest. A Poisson would
have produced a *falsely precise* effect and a wild underestimate of count
variability — dangerous if the next step sizes an experiment on that variance.

`summary_onepager.md` carries the non-technical version.

---

## 9. Common pitfalls (the project's key trap)

1. **Forcing Poisson on overdispersed data.** THE pitfall. The Poisson converges,
   looks fine on $\hat R$, and lies about uncertainty. Always check var/mean and
   run a PPC on the count spread.
2. **Stopping at convergence diagnostics.** $\hat R=1.00$ says nothing about model
   adequacy. The PPC and LOO are mandatory for count models.
3. **No competing model.** Without fitting the NB and running `az.compare`, you
   have no quantitative basis to prefer one family.
4. **Wide priors on the log-mean** exploding after exponentiation.
5. **Ignoring sequencing depth** — real RNA-seq needs a per-sample offset
   ($\log(\text{depth})$) in the linear predictor; omitting it confounds the mean.

---

## 10. File map

| File | Role |
|------|------|
| `data/generate_data.py` | overdispersed NB count DGP, fixed seed, known truth |
| `model.py` | `build_model`/`fit` for both `poisson` and `nb`; log link |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow with `az.compare` |
| `notebook_broken.ipynb` | Poisson-forced debugging exercise |
| `test_recovery.py` | fast recovery test of $(\beta_0,\beta_1,\alpha)$ |
| `sbc.py` / `SBC_REPORT.md` | simulation-based calibration of the NB model |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | dispersion-prior comparison |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension prompt |
| `lessons.md` | narrative lessons report |
| `summary_onepager.md` | non-technical decision summary |
