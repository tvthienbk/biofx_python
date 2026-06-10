# Project 20 — Capstone: Compound Prioritization & Decision Under Uncertainty

> **Workflow focus:** integrate **everything** — a hierarchical model with partial
> pooling, full diagnostics + PPC, a LOO model comparison — and then **make a
> decision** with an explicit cost-loss / expected-utility calculation.
> **Key pitfall:** *stopping at the posterior* instead of deciding; and ranking by
> raw (unpooled) means, which falls for the small-sample **winner's curse**.

This is the capstone: the richest README, tying back to the whole portfolio.

---

## 0. Compute requirements (read first)

One of the four "heavy" projects (#17-20), but the lightest of them — the model is
a standard hierarchical Normal model.

- `J = 12` compounds, ~100 total observations. The non-centred parameterisation
  keeps NUTS happy.
- **BLAS is not linked**; PyMC's multiprocess sampler can hang, so we sample with
  `cores=1` (set inside `model.fit`). Do not remove it.
- Expected serial CPU wall-clock:
  - `python3 model.py` (400 draws + decision): ~20-40 s
  - `python3 -m pytest test_recovery.py -q` (400 draws): ~30-50 s
  - `python3 sbc.py` (20 hierarchical refits, J=8): ~120-180 s
  - `python3 prior_sensitivity.py` (3 fits + decisions): ~60-120 s
- The notebook adds a complete-pooling fit and a LOO comparison (~90 s total). It
  is **validated statically**, not executed.

---

## 1. Problem & data-generating story (Step 1)

We screen `J = 12` candidate compounds in a noisy assay and must advance the
single best one. Each compound `j` has a true effect `theta_j`; we observe
replicate readings `y_{j,i} ~ N(theta_j, sigma)`. The compounds are exchangeable:
`theta_j ~ N(mu, tau)`.

**The decisive feature: unequal replication.** Replicate counts run from 20 down
to 2. A compound with only 2 replicates can post a high *raw* mean purely by chance
— the **winner's curse**. The true effects are a genuine population draw
`theta_j ~ N(mu, tau)` (so `mu` and `tau` stay recoverable); a **fixed seed**
(`SEED = 24`) realises a screen in which the trap appears and is correctable. With
that seed the true best is compound **#0** (`theta = 1.35`), which is
**well-replicated** (`n = 20`, hence recoverable), while a **barely-replicated**
compound **#11** (`theta = 0.89`, `n = 2`) draws a lucky-high raw mean (~1.76) that
pushes it above #0's raw mean. A naive "advance the top raw mean" policy picks
**#11** — the wrong compound. Partial pooling shrinks the low-`n` fluke back below
the well-supported true best, restoring #0.

**Data-generating process** (`data/generate_data.py`): `theta_j ~ N(mu, tau)` with
`mu = 0`, `tau = 1`, within-compound noise `sigma = 1`, and unequal replication
`n_reps = [20, 18, …, 2, 2, 2]`. The winner's curse is not hand-engineered into the
effects — it emerges naturally at this seed because the lowest-replicate compound
happens to draw a favourable assay realisation. **Recoverable truths:** `mu`, `tau`,
the per-compound `theta_j`, and the identity of the true-best compound (`#0`).

**Assumptions, made explicit:**
1. Compounds are exchangeable draws from a common population (partial pooling is
   appropriate). If there were known sub-classes, we'd model them.
2. Within-compound noise is Gaussian with a **shared** `sigma` (a per-compound
   `sigma_j` is an extension).
3. Replicates are independent given `theta_j`.
4. The utility of advancing a compound is (increasing in) its true effect.

---

## 2. Model specification with justified priors (Step 2)

Hierarchical partial-pooling model, **non-centred**:

```
mu      ~ Normal(0, 2)            # population mean effect
tau     ~ HalfNormal(1)           # between-compound sd
z_j     ~ Normal(0, 1)            # standardised offsets
theta_j = mu + tau * z_j          # non-centred compound effects
sigma   ~ HalfNormal(1)           # within-compound assay noise
y_{j,i} ~ Normal(theta_j, sigma)
```

### Why partial pooling (the cure for the winner's curse)

Complete pooling (`tau -> 0`) says all compounds are identical — it throws away
real differences. No pooling (separate `theta_j`, flat) trusts every raw mean,
including the lucky low-`n` ones — the winner's curse. **Partial pooling** lets the
data choose the shrinkage: each `theta_j` is pulled toward `mu` by an amount
inversely proportional to its replicate count. Few-replicate compounds get shrunk
hard (their flukes are tamed); well-replicated compounds barely move. This is the
single most important idea in the project.

### Why non-centred

A *centred* hierarchy (`theta_j ~ N(mu, tau)`) funnels as `tau -> 0` and diverges.
The non-centred form `theta_j = mu + tau*z_j` gives NUTS a flat geometry. The
broken notebook uses the centred form to show the funnel.

### Priors

`mu ~ N(0, 2)` (effects are standardised), `tau ~ HalfNormal(1)` (the key lever —
see `PRIOR_SENSITIVITY.md`), `sigma ~ HalfNormal(1)`.

---

## 3. Prior predictive checks (Step 3)

We simulate compound screens from the priors: we want plausible spreads of effects
— not all compounds identical (`tau` prior too tight) nor implausibly extreme (too
loose). This calibrates the `tau` prior before fitting.

---

## 4. Inference / NUTS settings (Step 4)

```
draws=600, tune=1000, chains=2, target_accept=0.95, cores=1, random_seed=101
```

Non-centred + high `target_accept` keep the hierarchical geometry divergence-free.
`cores=1` avoids the multiprocess hang.

---

## 5. Computational diagnostics (Step 5)

Report `R-hat`, ESS, divergences (want 0 — the funnel is the usual culprit, tamed
by non-centring). We visualise **shrinkage** directly: posterior `theta_j` means
vs raw means, coloured by replicate count. Low-`n` compounds should sit visibly
off the no-shrinkage diagonal, pulled toward `mu`.

**If diagnostics fail:** divergences → ensure non-centred + raise `target_accept`;
a `tau`-vs-`theta` funnel → non-centred form; low ESS → more draws.

---

## 6. Posterior predictive checks (Step 6)

`az.plot_ppc` confirms the model reproduces the spread of the replicate data,
capturing both within- and between-compound variation. A miss would suggest a
per-compound `sigma_j` or heavier tails.

---

## 7. Model criticism & comparison via LOO (Step 7)

We compare the **hierarchical** model against a **complete-pooling** model using
LOO (`az.compare`). Both carry `log_likelihood`. When compounds genuinely differ
(as here, `tau = 1`), the hierarchical model should have the higher `elpd_loo`,
justifying the extra structure. (If `tau` were truly ~0, complete pooling would
win — LOO would tell us so.)

---

## 8. Decision under uncertainty (Step 8) — the point of the capstone

A posterior is not a decision. We define a **utility** for advancing compound `j`:
`U_j = theta_j - cost`. From the posterior draws of `theta` we compute, per
compound:

- **expected utility** `E[theta_j] - cost`;
- **probability of being best** `P(theta_j = max_k theta_k)`;
- **expected regret** `E[max_k theta_k - theta_j]` (the loss relative to an oracle
  who always picks the true best).

We **recommend the compound that minimises expected regret**. Key teaching points:

- `P(best)` is spread across several plausible winners — the honest picture the
  raw maximum hides.
- The min-regret choice can differ from the **argmax of the posterior mean** (it
  accounts for the *whole* distribution, including the chance of being beaten).
- It **overturns the raw-mean winner's curse**: the lucky low-`n` raw winner is
  shrunk away and a well-supported compound is advanced.

We communicate the recommendation **with** its probability-of-best and the
runner-up, so the team can decide whether to advance one compound or carry two.

---

## How this ties back to the whole portfolio

- **Proportions / regression (early projects):** the likelihood and prior-predictive
  discipline.
- **Hierarchical models (10-12):** partial pooling, non-centred parameterisation,
  the funnel — all reused here.
- **Model comparison (mixtures, change-point):** LOO / `az.compare` to justify
  structure.
- **Calibration (SBC) and prior sensitivity:** the correctness tier, applied to the
  decision.
- **The new capstone skill:** decision theory — converting a calibrated posterior
  into an action under an explicit loss.

The meta-lesson of the entire portfolio lands here: **the workflow exists to support
a decision.** A beautiful posterior that stops short of the loss function is an
unfinished analysis.

---

## Common pitfalls (tied to this project's key pitfall)

- **Stopping at the posterior.** The headline sin. Always specify the loss and
  compute expected utility / regret.
- **Ranking by raw means.** The winner's curse; few-`n` flukes win. Partial-pool.
- **Ranking by posterior mean only.** Better than raw means, but still ignores
  uncertainty; `P(best)` and expected regret are more honest.
- **Centred hierarchy.** Funnels and diverges; use non-centred.

---

## File index

| File | Role |
|---|---|
| `data/generate_data.py` | DGP; unequal replication, winner's-curse setup; truths |
| `model.py` | hierarchical (`build_model`/`fit`), pooled comparator, `decision_table` |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow incl. LOO comparison + decision |
| `notebook_broken.ipynb` | seeded raw-mean ranking + stop-at-posterior + centred bugs |
| `test_recovery.py` | recovers `mu`, `tau`, and the true-best decision |
| `sbc.py` / `SBC_REPORT.md` | light SBC on `tau` |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | between-compound SD prior sweep |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension |
| `lessons.md` | takeaways |
| `summary_onepager.md` | non-technical decision summary |

Environment: portfolio-level `requirements.txt` / `environment.yml` (PyMC 5.28,
ArviZ 0.23, numpy, scipy).
