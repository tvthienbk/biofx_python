# BROKEN_BUGS.md — Project 20 (instructor answer key)

`notebook_broken.ipynb` seeds the capstone's signature failures: **ranking by raw
(unpooled) means** (the winner's curse) and **stopping at the posterior** without a
loss function, plus a centred-hierarchy sampling bug. Don't reveal this file until
students have attempted the debug.

---

## Bug 1 — Rank by raw means (winner's curse)

```python
raw_pick = int(np.argmax(data['raw_means']))   # BROKEN
```

- **Symptom.** The "winner" is a compound with very few replicates and a lucky-high
  mean; it differs from the true best. Advancing it wastes resources on a fluke.
- **Diagnostic.** Look at the replicate count of the raw winner (here `n = 2`) and
  compare to the true best. Plot raw means with error bars sized by `1/sqrt(n)` —
  the raw winner's interval is huge.
- **Fix.** Fit a **hierarchical (partial-pooling)** model so low-`n` means are
  shrunk toward the population; rank by the shrunken (posterior) effects, not raw
  means.

---

## Bug 2 — Stop at the posterior (no decision theory)

```python
pm_pick = int(idata.posterior['theta'].mean(...).argmax())   # BROKEN: not a decision
```

- **Symptom.** Ranking by posterior mean ignores uncertainty: it can't say how
  *sure* we are, can't trade off expected gain against the chance of being beaten,
  and gives no `P(best)` or expected regret.
- **Diagnostic.** Two compounds with similar posterior means but very different
  spreads get treated identically — clearly wrong for a decision.
- **Fix.** Define a utility/loss and compute **expected utility**,
  **probability-of-being-best**, and **expected regret** per compound; recommend the
  **min-expected-regret** compound (see `model.decision_table` and the clean
  notebook's Step 8).

---

## Bug 3 — Centred hierarchy -> funnel and divergences

```python
theta = pm.Normal('theta', mu=mu, sigma=tau, shape=J)   # BROKEN: centred
```

- **Symptom.** Non-zero divergences, especially when `tau` is small; poor ESS for
  `tau` and `theta`.
- **Diagnostic.** Divergence count > 0; a funnel in the `(tau, theta_j)` joint
  (small `tau` -> pinched neck).
- **Fix.** Use the **non-centred** parameterisation `theta_j = mu + tau*z_j`,
  `z_j ~ N(0,1)` (as in `model.build_model`).

---

## Summary table

| Bug | Symptom | Diagnostic | Fix |
|---|---|---|---|
| 1. Raw-mean ranking | low-`n` fluke wins | replicate count of winner; shrinkage plot | hierarchical partial pooling |
| 2. Stop at posterior | no uncertainty in the decision | similar means, different spreads treated alike | expected utility / regret / P(best) |
| 3. Centred hierarchy | divergences, funnel | divergence count, funnel geometry | non-centred parameterisation |

Meta-lesson: the analysis is finished only when the calibrated posterior has been
turned into a **decision under an explicit loss** — and the model behind it must
pool partially (to beat the winner's curse) and be parameterised so NUTS can sample
it (non-centred).
