# Broken Notebook — Answer Key (Project 07)

`notebook_broken.ipynb` reproduces this project's pitfall: **letting outliers
dominate a non-robust fit.** This is the instructor key.

---

## Bug 1 — Normal likelihood on outlier-contaminated data

**Code.** `pm.Normal('y', mu=mu, sigma=sigma, observed=y)` with ~10% gross
outliers.

**Symptom.** The model **converges cleanly** ($\hat R=1$, good ESS, zero
divergences), so it is tempting to accept it. But the Normal log-likelihood
penalizes residuals *quadratically*, so a handful of far points dominate. Two
visible consequences:
- $\sigma$ is **hugely inflated** (~3 vs the clean 0.6, a 5× inflation — it must
  explain the outliers as ordinary noise);
- the line becomes **far more uncertain**: $\beta$'s posterior SD balloons to ~0.37,
  roughly 6× the Student-t's ~0.06. (These outliers are balanced and low-leverage by
  design, so the Normal slope *mean* stays near the truth ~2.0; the damage is to its
  precision and its noise estimate, not a tilted mean line. With one-sided or
  high-leverage outliers the mean would shift too.)

**Diagnostic.**
- Compare the estimated $\sigma$ (~3) to the true clean noise (0.6) — a 5× inflation.
- Compare the Normal slope SD (~0.37) to the Student-t's (~0.06) — a 6× wider band.
- A **LOO comparison** against a Student-t model: the t wins by many `dse`, and
  the outliers show up as high Pareto-$k$ points under the *Normal*.

**Fix.** Use a heavy-tailed likelihood with a free $\nu$:
```python
nu = pm.Gamma('nu', 2, 0.1)
pm.StudentT('y', nu=nu, mu=mu, sigma=sigma, observed=y)
```

---

## Bug 2 — A "Student-t" with nu fixed far too large

**Code.** `pm.StudentT('y', nu=100.0, mu=mu, sigma=sigma, observed=y)`.

**Symptom.** This *looks* robust — it uses a Student-t — but at $\nu=100$ the
Student-t is numerically indistinguishable from a Normal. The estimates match the
Normal fit's: $\sigma$ still inflated (~3) and the line still over-uncertain
($\beta$ SD ~0.37). The student has paid for robustness and received none.

**Diagnostic.** Note that $\nu=100$ is hard-coded, not estimated. Recall the
limit: $t_\nu\to\text{Normal}$ as $\nu\to\infty$, and convergence is already
essentially complete by $\nu\approx 30$. Inspect the estimates — identical to the
Normal fit's.

**Fix.** Make $\nu$ a **parameter** so the data can choose heavy tails:
```python
nu = pm.Gamma('nu', 2, 0.1)
pm.StudentT('y', nu=nu, mu=mu, sigma=sigma, observed=y)
```
The posterior $\nu$ then collapses to ~1–2, revealing the outliers and restoring
robustness.

---

## Meta-lesson

Robustness lives in the **tails of the likelihood**, and the tails are controlled
by $\nu$. The two ways to lose robustness are (1) using a Normal (no heavy tail at
all) and (2) using a Student-t but pinning $\nu$ large (heavy tail switched off).
Both fits converge and look healthy; only the estimates, the fitted line, and the
LOO comparison expose them. Keep $\nu$ a free parameter with a prior that permits
small values, and let the data tell you whether outliers are present — a small
posterior $\nu$ is the model raising its hand to say "these points are outliers."
