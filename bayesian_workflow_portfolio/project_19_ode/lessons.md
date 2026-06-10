# Lessons — Project 19 (Mechanistic / Bayesian ODE PK)

## Headline takeaways

1. **Mechanistic models trade flexibility for interpretability.** Unlike the GP
   (Project 17), where parameters are nuisance hyperparameters, here every
   parameter — `k`, `V` — is a quantity a pharmacologist cares about. The model
   structure is a scientific claim, and the priors are genuine domain knowledge.

2. **Identifiability is about design, not just sample size.** `k` and `V` are
   identified only because the design samples both the early phase (which pins
   `C0 = D/V`, hence `V`) and the tail (which pins the slope `k`). Drop the early
   points and no amount of late-time data separates them — they correlate along a
   ridge. This is the PK twin of the Michaelis-Menten `Vmax/Km` correlation.

3. **A combination can be identified while its factors are not.** Clearance
   `CL = k*V` (and half-life `t_1/2 = ln2/k`) stays well-constrained even when `k`
   and `V` individually wobble. Report the identified quantity.

4. **Use the closed form when you have one.** A generic ODE solver inside the
   sampler integrates at every leapfrog step; for a system with an analytic
   solution that cost buys nothing. We use the analytic likelihood for everything
   that runs repeatedly (fit, test, SBC, prior sensitivity) and demonstrate the
   genuine `DifferentialEquation` workflow once, on tiny settings.

## Failures and surprises encountered while building this

- **Multiprocess sampling hung** without a linked BLAS; `cores=1` fixed it.
- **The analytic model is *dramatically* cheaper.** The analytic fit takes ~30 s;
  the `DifferentialEquation` fit on a fraction of the draws takes comparable or
  longer. This made the compute argument concrete: closed form first.
- **`sigma` is slightly over-estimated** (the clipping of negative simulated
  concentrations at `1e-3` mildly distorts the noise model). It still covers the
  truth; a log-normal error model would be a cleaner fit for concentrations.
- **The ridge is easy to summon and easy to miss.** Dropping the early points in
  the broken notebook produces a textbook diagonal pair plot, but the marginal `k`
  and `V` summaries can still look superficially reasonable — you must look at the
  joint and at `CL`.

## How to generalise the technique

- **Saturable elimination (Michaelis-Menten).** `dC/dt = -Vmax*C/(Km + C)` has
  **no** closed form — the genuine ODE-inference case. `Vmax` and `Km` are
  classically correlated unless the design spans both the linear (`C << Km`) and
  saturated (`C >> Km`) regimes.
- **Multi-compartment PK.** Two- or three-compartment models (distribution +
  elimination) capture curvature a one-compartment model misses; compare via LOO.
- **Stiff systems.** When timescales differ by orders of magnitude, use a stiff
  solver and tighten `rtol`/`atol`; a too-loose tolerance biases gradients and
  causes divergences.
- **Population PK (hierarchical).** Partial-pool `k`, `V` across subjects — this
  ties directly into the hierarchical machinery of the capstone (Project 20).
- **Decision use.** The deliverable is a dosing decision: half-life and clearance
  set the dosing interval and maintenance dose; propagate the full posterior into
  those derived quantities rather than plugging in point estimates.
