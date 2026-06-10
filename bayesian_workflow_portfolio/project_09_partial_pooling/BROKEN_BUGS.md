# BROKEN_BUGS.md — Project 09 (instructor answer key)

`notebook_broken.ipynb` reproduces the project's central pitfall: a **centered**
hierarchical parameterization that falls into **Neal's funnel** and produces
divergences. Below is each seeded bug, its symptom, the diagnostic that reveals
it, and the fix. Do not show students this file before they attempt the exercise.

---

## Bug 1 — Centered parameterization (the funnel)

```python
theta = pm.Normal('theta', mu=mu, sigma=tau, dims='group')   # centered
```

**What is wrong.** Writing `theta_j ~ Normal(mu, tau)` directly makes the
posterior width of each `theta_j` depend on `tau`. As `tau -> 0` the joint
density of `(log tau, theta_j)` collapses into a sharp **funnel neck**. NUTS uses
a single step size tuned to the *average* curvature, so it is simultaneously too
large for the neck (causing the leapfrog integrator to diverge) and too small for
the mouth.

**Symptom.**
- A non-zero divergence count: "There were N divergences after tuning."
- `tau`'s tail ESS is depressed; occasionally `r_hat` for `tau` creeps above 1.01.
- The posterior for `tau` is biased *upward* — the sampler avoids the small-`tau`
  neck it cannot enter, so it never reports the low-`tau` region.

**Diagnostic.**
1. **Divergence count:** `idata.sample_stats['diverging'].sum()` > 0.
2. **Energy plot** (`az.plot_energy`): the marginal-energy and energy-transition
   densities are visibly *mismatched* (low BFMI) — the canonical hierarchical
   funnel signature.
3. **Pairs plot** (`az.plot_pair(..., var_names=['tau','theta'],
   coords={'group':[0]}, divergences=True)`): the red divergent points pile up in
   the **narrow neck** where `tau` is small.

**Fix.** Use the **non-centered** parameterization:

```python
z = pm.Normal('z', 0.0, 1.0, dims='group')
theta = pm.Deterministic('theta', mu + tau * z, dims='group')
```

Now `z_j ~ Normal(0,1)` has a geometry independent of `tau`, so the neck
disappears and the sampler explores the full range of `tau` freely.

---

## Bug 2 — `target_accept` too low for the geometry

```python
idata = pm.sample(..., target_accept=0.8)   # too low here
```

**What is wrong.** A lower acceptance target means a larger step size, which makes
divergences in the funnel neck *more* likely. `0.8` is PyMC's default and fine for
benign geometries, but hierarchical models routinely need `0.9–0.95`.

**Symptom.** Inflated divergence count relative to a higher target; raising it
partially suppresses divergences even before reparameterizing.

**Diagnostic.** Re-run with `target_accept=0.95` and watch the divergence count
drop. If raising it *alone* eliminates divergences, the geometry was borderline;
if divergences persist, the parameterization itself is the problem (it is here).

**Fix.** Raise `target_accept` to `0.95` **and** (the real fix) reparameterize.
Bumping `target_accept` is a band-aid; non-centering is the cure. The clean
notebook uses `target_accept=0.9` *with* non-centering and gets 0 divergences.

---

## How the fix is demonstrated

The final cell of the broken notebook rebuilds the model non-centered with
`target_accept=0.95` and prints `divergences after fix: 0` (or very nearly).
Side-by-side, students see the same data, the same priors, the same truth — only
the *parameterization* changed, and the pathology vanished. That is the entire
lesson of Project 09 in one comparison.

---

## Teaching note — never ignore divergences

A handful of divergences is **not** a rounding error to wave away. Each divergence
marks a region of parameter space the sampler could not enter, which biases every
downstream summary (here, `tau` upward and thus shrinkage downward). The correct
responses, in order: (1) reparameterize (non-centering), (2) raise
`target_accept`, (3) reconsider the priors on scale parameters. Suppressing the
*warning* without fixing the *geometry* produces confidently wrong inference.
