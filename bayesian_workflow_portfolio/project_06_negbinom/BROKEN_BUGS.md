# Broken Notebook — Answer Key (Project 06)

`notebook_broken.ipynb` reproduces this project's pitfall: **forcing a Poisson
model on overdispersed data and failing to notice.** This is the instructor key.

---

## Bug 1 — Poisson likelihood on overdispersed data

**Code.** `pm.Poisson('y', mu=mu, observed=y)` on data with var/mean ~ 14.

**Symptom.** The model **converges cleanly** — $\hat R=1.00$, good ESS, zero
divergences — so it is tempting to declare success. But the Poisson is locked to
$\operatorname{Var}(y)=\mu$, while the data have variance ~14× their mean. The fit
gets the *mean* roughly right and the *variance* catastrophically wrong.

**Diagnostic.** Two things expose it:
- A **posterior-predictive check**: replicated count distributions are far too
  narrow; predicted variance ($\approx$ predicted mean $\approx 10$) is an order
  of magnitude below the observed variance ($\approx 150$).
- **LOO comparison** against an NB model: the NB wins by many `dse`.

**Fix.** Use a Negative-Binomial likelihood with a free dispersion:
```python
alpha = pm.Gamma('alpha', 2, 0.1)
pm.NegativeBinomial('y', mu=mu, alpha=alpha, observed=y)
```

---

## Bug 2 — Stopping at convergence diagnostics (no PPC)

**Code.** The broken notebook prints `az.summary` (R-hat, ESS) and stops, as if
convergence implied adequacy.

**Symptom.** Nothing *looks* wrong, because $\hat R$ and ESS are blind to
misspecification. The model is wrong but the sampler is happy.

**Diagnostic.** Always follow convergence with a **posterior-predictive check**.
The broken notebook includes the variance comparison that reveals the gap
(observed var >> predicted var). Internalize the slogan: *convergence checks the
sampler; the PPC checks the model.*

**Fix.** Add `az.plot_ppc` and/or the predicted-vs-observed variance comparison to
the workflow, and never conclude from $\hat R$ alone.

---

## Bug 3 (implicit) — No competing model to compare against

**Code.** Only the Poisson is fit; there is no NB and no `az.compare`.

**Symptom.** With a single model you can describe its fit but cannot *rank* it. A
plausible-looking Poisson is accepted by default for lack of an alternative.

**Diagnostic.** The discipline of count modeling is to fit *both* the Poisson and
the NB and let PSIS-LOO adjudicate.

**Fix.**
```python
idata_nb = fit(data, model='nb', ...)
cmp = az.compare({'poisson': idata_pois, 'negbinom': idata_nb}, ic='loo')
```
`negbinom` comes out rank 0 with a large, significant `elpd_diff`.

---

## Meta-lesson

The Poisson's danger is that it **fails silently**: it converges, fits the mean,
and reports a falsely precise effect with a wildly underestimated variance. Only
model criticism — a posterior-predictive check and an explicit LOO comparison
against the Negative-Binomial — exposes it. For count data, treat overdispersion
as the default hypothesis and make Poisson earn its place via `az.compare`.
