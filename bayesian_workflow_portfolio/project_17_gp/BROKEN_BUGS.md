# BROKEN_BUGS.md — Project 17 (instructor answer key)

`notebook_broken.ipynb` seeds the canonical Gaussian-process failure mode: a
**vague length-scale prior** that makes the length-scale `ell` and the marginal
amplitude `eta` trade off against each other. Don't show students this file until
they've attempted the debug.

---

## Bug 1 — Vague length-scale prior (`HalfFlat`)

```python
ell = pm.HalfFlat('ell')          # BROKEN
```

- **Symptom.** High `R-hat` (often > 1.1) and very low ESS for `ell` and `eta`;
  the posterior for `ell` has a long, heavy tail; the trace for `ell`/`eta` shows
  chains exploring different regions or drifting.
- **Diagnostic.** The `(ell, eta)` **pair plot** shows a diagonal **ridge** rather
  than a compact blob: large `ell` pairs with large `eta`, small with small. This
  is the non-identifiability signature — many `(ell, eta)` explain the data
  equally well.
- **Fix.** Use an **informative, zero-avoiding** length-scale prior:
  ```python
  ell = pm.InverseGamma('ell', alpha=6.0, beta=12.0)
  ```
  This concentrates mass at length-scales that are a sensible fraction of the
  input range and kills the ridge. (This is exactly `model.build_model`.)

---

## Bug 2 — `target_accept` too low for the curved geometry

```python
idata = pm.sample(..., target_accept=0.8)   # BROKEN
```

- **Symptom.** A non-zero (sometimes large) **divergence** count;
  `idata.sample_stats['diverging'].sum() > 0`. Divergences cluster in the part of
  the ridge where the posterior curves sharply.
- **Diagnostic.** Print the divergence count; visualise divergences on the pair
  plot — they line up along the problematic geometry.
- **Fix.** Raise `target_accept=0.95` (smaller step size). Note: this *reduces* the
  symptom but the real cure is Bug 1's prior — sampler tuning cannot rescue a
  genuinely non-identified model.

---

## Bug 3 — Reading the pair plot wrong / stopping too early

The notebook's final cell draws the `(ell, eta)` pair plot but a student may
glance at the marginal summaries (which can look "fine-ish") and miss the ridge.

- **Symptom.** Marginal posterior means for `ell`/`eta` look plausible in
  isolation, so a hurried reader concludes "converged."
- **Diagnostic.** The **joint** pair plot is the tell: identifiability is a
  property of the *joint* posterior, not the marginals. A diagonal smear = trouble
  even when each marginal looks unimodal.
- **Fix.** Always inspect the joint geometry of correlated hyperparameters, and
  combine it with `R-hat`/ESS/divergences before trusting a GP fit. After fixing
  Bug 1, re-plot: the ridge collapses to a blob.

---

## Summary table

| Bug | Symptom | Diagnostic | Fix |
|---|---|---|---|
| 1. Vague `ell` prior | High R-hat, heavy `ell` tail | `(ell,eta)` pair-plot ridge | `InverseGamma(6,12)` |
| 2. Low `target_accept` | Divergences > 0 | divergence count / pair plot | `target_accept=0.95` |
| 3. Reading marginals only | "looks converged" | joint pair plot vs marginals | inspect joint geometry |

The meta-lesson: in a GP, **identifiability lives in the length-scale prior**, and
**you diagnose it in the joint posterior**, not the marginals.
