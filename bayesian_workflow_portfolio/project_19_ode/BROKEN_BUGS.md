# BROKEN_BUGS.md — Project 19 (instructor answer key)

`notebook_broken.ipynb` seeds the canonical mechanistic-inference failure:
**practical non-identifiability** of the rate constants, caused by a poor design
and made worse by vague priors. Don't reveal this file until students have
attempted the debug.

---

## Bug 1 — Identifiability trap: only late timepoints

```python
mask = full['t'] >= 3.0          # BROKEN: drops all early points
data = {'t': full['t'][mask], ...}
```

- **Symptom.** `k` and `V` posteriors are wide; their means drift from the truth;
  R-hat inflates and ESS drops. Yet the *fit to the late data* looks fine.
- **Diagnostic.** The `(k, V)` **pair plot** is a long diagonal **ridge**: without
  early points, `C0 = D/V` is unconstrained, so any `V` can be matched by a
  compensating `k`. Note the **clearance `CL = k*V`** may still be reasonable —
  the textbook signature of practical non-identifiability (a *combination* is
  identified, the factors are not).
- **Fix.** Restore the early timepoints (a **design** fix). Sampling both near
  `t=0` (pins `C0`, hence `V`) and on the tail (pins the slope `k`) identifies
  both.

---

## Bug 2 — Vague priors remove the last safety net

```python
log_k = pm.Normal('log_k', mu=0.0, sigma=3.0)   # BROKEN
log_V = pm.Normal('log_V', mu=0.0, sigma=3.0)   # BROKEN
```

- **Symptom.** On top of the bad design, the ridge runs even longer; the sampler
  wanders over implausible orders of magnitude for `k` and `V`.
- **Diagnostic.** Compare the `(k, V)` correlation with vague vs informative
  priors (see `prior_sensitivity.py`): it shrinks markedly with informative priors.
- **Fix.** Use the informative mechanistic priors from `model.py`
  (`log k ~ N(-1, 0.7)`, `log V ~ N(2, 0.5)`). They encode real physiological
  ranges and partly rescue even a mediocre design.

---

## Bug 3 — Reading the factors instead of the identified combination

A student may report `k` and `V` point estimates from the broken fit as if they
were trustworthy.

- **Symptom.** Confident-looking `k` and `V` numbers that are actually anywhere
  along the ridge.
- **Diagnostic.** Check `corr(k, V)` and inspect whether `CL = k*V` (or `t_1/2`)
  is tight while the factors are loose. If so, only the combination is identified.
- **Fix.** Report the well-identified quantity (clearance / half-life) with its
  interval, and explicitly flag that the individual constants are not separately
  identified under this design. Then fix the design (Bug 1).

---

## Summary table

| Bug | Symptom | Diagnostic | Fix |
|---|---|---|---|
| 1. Late-only design | wide k,V; biased; high R-hat | `(k,V)` pair-plot ridge; CL still ok | restore early timepoints |
| 2. Vague priors | even longer ridge | corr(k,V) vs informative priors | informative log-scale priors |
| 3. Reporting factors not combo | overconfident k,V | CL/t_1/2 tight while k,V loose | report CL; flag non-identifiability |

Meta-lesson: in mechanistic models, **identifiability is a property of the design
× prior**, not just the data count; and **a combination can be identified while
its factors are not** — always check, and report the identified quantity.

(Compute aside: for ODEs without a closed form, a *fourth* classic bug is a
too-loose solver tolerance, which biases gradients and causes divergences;
tighten `rtol`/`atol`. We use the analytic solution here, so that bug cannot
occur — but the README and rubric call it out.)
