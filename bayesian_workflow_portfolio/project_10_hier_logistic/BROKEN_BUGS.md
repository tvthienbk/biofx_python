# BROKEN_BUGS.md — Project 10 (instructor answer key)

`notebook_broken.ipynb` reproduces this project's pitfall: **pooling the family
intercepts too aggressively** with few groups, compounded by a centered
parameterization. Each seeded bug with its symptom, diagnostic, and fix.

---

## Bug 1 — Over-tight prior on `tau` (the over-pooling bug)

```python
tau = pm.HalfNormal('tau', 0.05)   # far too tight
```

**What is wrong.** `tau` is the between-family SD of the intercepts. A
`HalfNormal(0.05)` puts essentially all prior mass at `tau ≈ 0`, which *forces*
`alpha_g ≈ mu` for every family — complete pooling by prior fiat. With only G=10
families the data cannot overrule such a tight prior, so real family-to-family
differences are erased.

**Symptom.**
- Posterior `tau` pinned near 0 (≈ 0.08 vs the truth 0.9).
- The recovered family intercepts `alpha_g` **collapse onto `mu_hat`**: their
  spread shrinks from ~0.9 to ~0.05 log-odds.
- Per-family predictions become nearly identical, ignoring families that genuinely
  bind more or less.

**Diagnostic.**
- **Shrinkage plot:** scatter `alpha_g` posterior means — they sit on top of
  `mu_hat` (the broken notebook's Diagnostic 2). Compare to the clean notebook's
  visible spread.
- **`tau` posterior:** `az.summary(..., var_names=['tau'])` shows `tau` mean ~0.08,
  far below truth, with the prior, not the data, driving it.
- **Prior sensitivity:** `prior_sensitivity.py` shows the family-intercept spread
  jumping from 0.054 (tight) to ~0.92 (default) — the prior, not the data, is in
  control.

**Fix.** Use a weakly-informative scale prior, `tau ~ HalfNormal(1.0)`, that lets
the data express the real between-family spread. The intercepts regain their ~0.9
spread.

---

## Bug 2 — Centered parameterization (the funnel)

```python
alpha = pm.Normal('alpha', mu=mu, sigma=tau, dims='group')   # centered
```

**What is wrong.** As in Project 09, the centered form couples each `alpha_g` to
`tau` and creates Neal's funnel — and the funnel is *worst* exactly where Bug 1's
tight prior pushes `tau` (near 0). The two bugs reinforce each other.

**Symptom.** Non-zero divergences after tuning; depressed ESS for `tau`;
occasionally `r_hat > 1.01`.

**Diagnostic.**
- **Divergence count:** `idata.sample_stats['diverging'].sum()` > 0.
- **Energy plot** (`az.plot_energy`): marginal/transition mismatch (low BFMI) — the
  funnel fingerprint.

**Fix.** Non-center: `z_g ~ Normal(0,1)`, `alpha_g = mu + tau*z_g`, and raise
`target_accept` to 0.95. Combined with the sensible `tau` prior, divergences drop
to ~0.

---

## How the fix is demonstrated

The final cell rebuilds the model with `tau ~ HalfNormal(1)` **and** the
non-centered parameterization at `target_accept=0.95`, then prints both
`divergences after fix: 0` and the restored intercept spread (~0.9). Same data,
same families — only the prior and parameterization changed, and both the
over-pooling and the divergences vanish.

---

## Teaching note — "regularization" is not free

A tempting but wrong instinct is to tighten the `tau` prior to "regularize" a noisy
hierarchical fit. With few groups this does not gently regularize — it *over-pools*,
hard-coding the conclusion that the groups are identical. Partial pooling already
provides principled, data-driven regularization; the prior's job is to be weakly
informative, not to dictate the answer.
