# Project 19 — Mechanistic Model: 1-Compartment PK (Bayesian ODE)

> **Workflow focus:** fitting a *mechanistic* model whose structure comes from
> physics/biology, not curve-fitting. **New skill:** ODE inference,
> identifiability, and solver cost. **Key pitfall:** *practical
> non-identifiability* of the rate constants plus slow/stiff sampling.

---

## 0. Compute requirements (read first) — IMPORTANT

This is one of the four "heavy" projects (#17-20), and the *one most shaped by
compute*.

- **The model has a closed-form solution.** A 1-compartment IV-bolus PK model
  obeys `dC/dt = -kC`, `C(0) = D/V`, with the exact solution
  `C(t) = (D/V) exp(-k t)`. We fit this **analytic** form in the main model
  (`build_model`/`fit`). It is exact and fast.
- **Why analytic, and why we still teach the ODE workflow.** The brief permits
  using a closed form for speed while teaching the ODE-inference workflow, and
  *prefers* `pymc.ode.DifferentialEquation` if it samples in reasonable time. On
  this tiny dataset the DifferentialEquation model *does* sample, but each NUTS
  step calls a numerical integrator (with sensitivities), so it is **far slower**
  than the analytic likelihood. We therefore: (a) use the analytic model for the
  main fit, tests, SBC, and prior sensitivity; (b) include the genuine
  `DifferentialEquation` model (`build_ode_model`/`fit_ode`) and exercise it on
  tiny settings in the notebook's Step 7 to show the real workflow and its cost.
  **For an ODE *with* a closed form, using the closed form is the responsible
  engineering choice**; reserve the numerical solver for systems without one
  (e.g. saturable Michaelis-Menten elimination).
- **BLAS is not linked**; PyMC's multiprocess sampler can hang, so we sample with
  `cores=1`.
- Expected serial CPU wall-clock:
  - `python3 model.py` (analytic, 400 draws): ~20-40 s
  - `python3 -m pytest test_recovery.py -q` (analytic, 400 draws): ~30-50 s
  - `python3 sbc.py` (25 analytic refits): ~90-150 s
  - `python3 prior_sensitivity.py` (3 analytic fits): ~60-120 s
  - The notebook's `fit_ode` (100 draws) is the slow part (~30-90 s) and is
    deliberately tiny; the notebook is **validated statically**, not executed.

---

## 1. Problem & data-generating story (Step 1)

A known dose `D = 100` mg is given as an instantaneous IV bolus into a single
compartment of volume `V`. The drug is eliminated by a first-order process with
rate constant `k`. The concentration solves the ODE and decays exponentially. We
sample noisy concentrations at 10 timepoints spanning 0.25-10 h.

**Data-generating process** (`data/generate_data.py`): `k = 0.35`/h, `V = 8` L,
`sigma = 0.4` mg/L. **Recoverable truths:** `k`, `V` (and `sigma`); clearance
`CL = k*V` and half-life `t_1/2 = ln2 / k` are derived.

The design deliberately includes **early** timepoints (where `C ~ C0 = D/V`, which
pins down `V`) and **late** timepoints (where the log-linear slope pins down `k`).
This is what makes `k` and `V` separately identifiable.

**Assumptions, made explicit:**
1. One well-mixed compartment.
2. First-order (linear) elimination — no saturation. (If elimination saturated,
   we'd need Michaelis-Menten kinetics, which has *no* closed form — the genuine
   ODE case.)
3. Instantaneous IV bolus at `t = 0`.
4. Additive Gaussian measurement noise (a multiplicative/log-normal error is a
   common alternative for concentrations).

---

## 2. Model specification with justified priors (Step 2)

We sample `k` and `V` on the **log scale** (both positive, span orders of
magnitude):

```
log k ~ Normal(-1, 0.7)     # k ~ exp(-1) ~ 0.37 /h
log V ~ Normal( 2, 0.5)     # V ~ exp(2)  ~ 7.4 L
sigma ~ HalfNormal(1.0)
C(t)  = (D / V) * exp(-k t)
y     ~ Normal(C(t), sigma)
```

Mechanistic models *should* use informative priors: `k` and `V` have known
physiological ranges, and the prior is genuine domain knowledge, not a nuisance.
The log scale keeps both positive and gives NUTS a clean geometry.

### The identifiability story (the pitfall)

`k` and `V` enter the model in a partly entangled way. The concentration is
`(D/V) exp(-k t)`:
- the **intercept** `C0 = D/V` depends on `V` (and the known `D`),
- the **slope** of `log C` depends on `k`.

If you only sample on the log-linear tail (late times), you measure the slope well
but barely constrain the intercept — so `V` floats, and to compensate `k` shifts:
`k` and `V` become **practically non-identifiable** and correlate. This is the PK
analogue of the **Vmax/Km correlation** in Michaelis-Menten kinetics. The cure is
*design* (sample early *and* late) and *informative priors*. The broken notebook
drops the early points to make the ridge appear.

Often a *combination* is better identified than either factor: clearance
`CL = k*V` is constrained by the area under the curve and stays tight even when
`k` and `V` individually wobble — a useful thing to report.

---

## 3. Prior predictive checks (Step 3)

We simulate concentration curves implied by the priors: they should be plausible
decay profiles (right order of magnitude for `C0`, sensible half-lives), not
absurd. A mis-scaled `log V` prior would show up as wildly wrong starting
concentrations here.

---

## 4. Inference / NUTS settings (Step 4)

```
draws=600, tune=1000, chains=2, target_accept=0.9, cores=1, random_seed=101
```

The log parameterisation plus the analytic likelihood make this fast and
well-behaved. `cores=1` avoids the multiprocess hang.

---

## 5. Computational diagnostics & identifiability (Step 5)

Report `R-hat`, ESS, divergences. The decisive plot is the **`(k, V)` pair plot**:
a compact blob with the full design, a diagonal ridge under a poor design. We also
report `corr(k, V)` and the clearance `CL = k*V` (often better identified).

**If diagnostics fail:** (a) a strong `(k, V)` ridge / high R-hat → practical
non-identifiability; fix the *design* (add early samples) or tighten priors, not
the sampler; (b) for genuine ODEs, divergences/slowness can come from a **stiff**
system or a too-loose solver tolerance → tighten `rtol`/`atol` or reparameterise;
(c) low ESS → more draws.

---

## 6. Posterior predictive checks (Step 6)

Overlay posterior-predictive concentration curves on the data (`az.plot_ppc`); the
observed points should sit inside the predictive band. A systematic miss (e.g.
curvature the single-compartment model can't capture) would argue for a
two-compartment model.

---

## 7. Model criticism & the genuine ODE solver (Step 7)

We fit the **same** model with `pymc.ode.DifferentialEquation` on tiny settings
and confirm it agrees with the analytic fit. This demonstrates the real
ODE-inference workflow you'd use for a system *without* a closed form, and makes
the **compute cost** explicit (time the call). Agreement between the analytic and
numerical fits is also a correctness check on both.

---

## 8. Decision & communication (Step 8)

We report dosing-relevant derived quantities with credible intervals: the
**half-life** `t_1/2 = ln2 / k` and the **clearance** `CL = k*V`. These are the
numbers a pharmacologist uses to choose a dosing interval — far more actionable
than the raw rate constants.

---

## Common pitfalls (tied to this project's key pitfall)

- **Identifying both `k` and `V` from a poor design** (e.g. only late samples).
  The ridge / Vmax-Km-style correlation. Fix the design; report `CL` and `t_1/2`.
- **Forcing a numerical solver when a closed form exists.** Slow for no benefit.
- **Too-loose solver tolerance** (for genuine ODEs). Causes biased gradients,
  divergences, or silent inaccuracy. Tighten `rtol`/`atol`.
- **Linear-error model for concentrations.** Concentrations are often
  log-normally distributed; consider a multiplicative error.

---

## File index

| File | Role |
|---|---|
| `data/generate_data.py` | DGP; closed form + truths; writes `data.npz` |
| `model.py` | analytic (`build_model`/`fit`) + `DifferentialEquation` (`build_ode_model`/`fit_ode`) |
| `build_notebook.py` | emits `notebook.ipynb` + `notebook_broken.ipynb` |
| `notebook.ipynb` | clean 8-step workflow incl. ODE-solver demo |
| `notebook_broken.ipynb` | seeded identifiability-trap (no early points) bugs |
| `test_recovery.py` | recovers `k` and `V` (analytic model) |
| `sbc.py` / `SBC_REPORT.md` | very-light SBC on `k` (analytic) |
| `prior_sensitivity.py` / `PRIOR_SENSITIVITY.md` | rate-constant prior sweep |
| `BROKEN_BUGS.md` | instructor answer key |
| `rubric.md` | grading rubric + extension |
| `lessons.md` | takeaways |
| `summary_onepager.md` | non-technical decision summary |

Environment: portfolio-level `requirements.txt` / `environment.yml` (PyMC 5.28,
ArviZ 0.23, numpy, scipy).
