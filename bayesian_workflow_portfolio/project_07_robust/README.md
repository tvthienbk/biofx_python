# Project 07 — Robust Regression (Student-t Likelihood)

> **The guideline.** Long-form teaching document for Project 07. It walks the full
> eight-step Bayesian workflow on a linear regression with outliers, with the
> project's signature skill — **heavy-tailed likelihoods and $\nu$ as a parameter**
> — woven through. We fit **two** models (Normal and Student-t) and let LOO decide.
> Read it with `notebook.ipynb`, `notebook_broken.ipynb`, and the per-artifact
> reports (`SBC_REPORT.md`, `PRIOR_SENSITIVITY.md`, `BROKEN_BUGS.md`).

---

## 0. Where this project sits in the portfolio

Projects 05–06 changed the *link* and the *count family*. Project 07 changes the
**noise model**. The default linear-regression assumption — Normal (Gaussian)
errors — is fragile: because the Normal log-likelihood penalizes residuals
*quadratically*, a single gross outlier exerts enormous influence and can tilt the
entire fit. The cure is a **heavy-tailed likelihood**, the Student-t, whose tails
make far-from-the-line points cheap to explain. The structural lesson mirrors
Project 06: a more flexible model (Student-t / NB) nests the rigid one (Normal /
Poisson), and `az.compare` decides whether the flexibility is warranted.

Environment (PyMC 5.28, ArviZ 0.23, numpy 2.x, scipy) is shared; see the
top-level `environment.yml` / `requirements.txt`.

---

## 1. Step 1 — Problem & the data-generating story

### 1.1 Scenario

A calibration experiment relates a known input $x$ to a measured response $y$,
expected linear. Most points are clean; a few ($\sim 10\%$) are **gross outliers**
— a pipetting error, an air bubble, a mis-read plate.

### 1.2 Generative model

Clean points: $y_i=\alpha+\beta x_i+\varepsilon_i$, $\varepsilon_i\sim N(0,\sigma)$.
A small set of points is then shifted by a large amount. The **known truth is the
clean line**: $\alpha=1$, $\beta=2$, $\sigma=0.6$.

Two deliberate design choices make the recovery target fair:

1. **Outliers are low-leverage.** They sit at central $x$ (small $|x|$), so they
   contaminate the vertical scatter without manufacturing a slope artefact.
2. **Outlier signs are balanced** (half up, half down), so they do not
   systematically shift the intercept either.

The seed is chosen so the *clean points'* own least-squares line is very close to
$(\alpha,\beta)=(1,2)$ — i.e. the unlucky-noise slop is small — so "recover the
clean line" genuinely tests robustness rather than a noise fluke.

### 1.3 Assumptions, stated out loud

1. **Linearity** of the underlying calibration.
2. **Most points clean, a minority gross outliers** (a contamination model).
3. **Vertical outliers** — corruptions are in $y$, not high-leverage $x$ errors.
4. **Inputs $x$ known** (errors-in-variables is Project 12).
5. **One global scale** for the clean noise.

---

## 2. Step 2 — Two likelihoods: Normal and Student-t

Both share $\mu_i=\alpha+\beta x_i$. They differ only in the noise distribution:

$$
\text{Normal: } y_i\sim N(\mu_i,\sigma),\qquad
\text{Student-t: } y_i\sim t_\nu(\mu_i,\sigma).
$$

The Student-t adds **degrees of freedom $\nu$**, which controls tail weight:

- **Small $\nu$** (say 1–4): heavy tails. Far points are plausible tail events, so
  the likelihood does not over-penalize them — the fit is **robust**.
- **Large $\nu$** ($\to\infty$): the Student-t *is* the Normal. No robustness.

Because the t nests the Normal, the comparison is fair: on clean data $\nu$ simply
grows and the two models agree. `model.py` exposes one
`build_model(data, model="normal" | "studentt")` and a matching `fit(...)`.

### Priors (weakly informative)

| parameter | prior | rationale |
|-----------|-------|-----------|
| $\alpha,\beta$ | $N(0,5)$ | broad on the $O(1)$–$O(10)$ scale of the data |
| $\sigma$ | $\text{HalfNormal}(5)$ | positive scale, weakly informative |
| $\nu$ | $\text{Gamma}(2,0.1)$ | mass on small $\nu$ (allows heavy tails) but lets $\nu$ grow if data are clean |

The $\nu$ prior is the crux. It must **permit** small $\nu$, or the model cannot be
robust. A common mistake is to fix $\nu$ at a large value (Bug 2 in the broken
notebook), which silently turns the "robust" model back into a Normal.

---

## 3. Step 3 — Prior predictive checks

We simulate $y$ from the Student-t prior and confirm the implied responses are
heavy-tailed but plausible. Occasional large $|y|$ are *expected* under the prior
— that is exactly the flexibility that will later absorb the outliers. We clip the
extreme tail only for plotting.

---

## 4. Step 4 — Inference (NUTS settings)

`draws=1000, tune=1000, chains=4, random_seed=101`, for both models. The
Student-t can be slightly stiffer when $\nu$ is small (the tails create mild
funnel-like geometry), but with standardized $x$ default NUTS is adequate; a
`target_accept=0.9` bump is the first remedy if divergences appear. We keep both
idatas for Step 7.

---

## 5. Step 5 — Computational diagnostics

Both models converge ($\hat R\approx1$, healthy ESS, zero divergences). As in
Project 06, **convergence is not adequacy**: the Normal model samples perfectly
and is still wrong. The tell is in the *estimates*:

- The Normal's $\sigma$ is **hugely inflated** — it must absorb the outliers as
  ordinary noise.
- The Normal's slope is dragged off the truth (toward whichever side the net
  outlier mass pulls).
- The Student-t recovers $\alpha\approx1$, $\beta\approx2$, a small scale, and a
  **small $\nu$** — it has identified the heavy tails.

A small posterior $\nu$ is itself a diagnostic: it is the model *telling you* the
data have outliers.

---

## 6. Step 6 — Posterior predictive & the fitted lines

The clearest visual: overlay both fitted lines on the scatter. The Normal line
tilts toward the outliers and the Student-t line tracks the clean trend. We also
run `az.plot_ppc` for the Student-t to confirm the replicated responses cover the
data (including the tails) without absurdity.

---

## 7. Step 7 — Model comparison (LOO) & recovery

`az.compare({...}, ic="loo")` ranks the **Student-t** first: down-weighting
outliers yields better expected held-out predictive density. The Normal's
`elpd_diff` is large and many `dse` below zero. Watch Pareto-$k$: the outliers are
exactly the high-influence points that can produce $k>0.7$ under the *Normal*
model (another symptom of its misspecification); the Student-t's $k$ values are
better behaved because it does not treat outliers as influential.

We then confirm via `check_recovery` that the Student-t recovers the clean
$(\alpha,\beta)$. We deliberately do **not** assert on $\sigma$: the data carry
Normal noise of SD 0.6, but the Student-t fits a *scale* whose relation to the
marginal SD depends on $\nu$ ($\operatorname{Var}=\sigma^2\nu/(\nu-2)$ for $\nu>2$,
undefined for small $\nu$). With heavy tails the estimated scale legitimately sits
below 0.6 — comparing it to the Normal SD would be apples-to-oranges.

---

## 8. Step 8 — Decision & communication

Report the calibration slope and intercept with credible intervals, plus the
estimated $\nu$ as an outlier indicator. The decision-level message: the line is
$y\approx 1.0+2.0x$, recovered cleanly despite ~10% gross outliers, and a naive
least-squares fit would have reported a tilted line and an inflated noise level.

`summary_onepager.md` carries the non-technical version.

---

## 9. Common pitfalls (the project's key trap)

1. **Letting one outlier dominate a Normal fit.** THE pitfall. The quadratic
   penalty gives gross outliers outsized leverage; the line tilts and $\sigma$
   blows up. Switch to a Student-t.
2. **Fixing $\nu$ too large.** A "Student-t" with $\nu=100$ is a Normal in
   disguise and is not robust. Let $\nu$ be a free parameter (or set it small).
3. **Stopping at convergence diagnostics.** The Normal converges fine; only the
   estimates, PPC, and LOO reveal its inadequacy.
4. **Treating the Student-t scale as the noise SD.** They differ by a
   $\nu$-dependent factor; do not over-interpret $\sigma$ when $\nu$ is small.
5. **Assuming outliers are vertical when they are high-leverage.** Robust
   *likelihoods* fix vertical outliers; leverage points in $x$ need robust
   *regression* or an errors-in-variables model.

---

## 10. File map

| File | Role |
|------|------|
| `data/generate_data.py` | linear DGP with balanced low-leverage outliers, known clean truth |
| `model.py` | `build_model`/`fit` for both `normal` and `studentt` |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow with `az.compare` |
| `notebook_broken.ipynb` | Normal-likelihood / nu-fixed debugging exercise |
| `test_recovery.py` | fast recovery test of the clean $(\alpha,\beta)$ |
| `sbc.py` / `SBC_REPORT.md` | simulation-based calibration of the Student-t model |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | $\nu$-prior comparison |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension prompt |
| `lessons.md` | narrative lessons report |
| `summary_onepager.md` | non-technical decision summary |
