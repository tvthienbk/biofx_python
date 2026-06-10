# Project 13 — Subpopulations (finite mixture)

> **Workflow focus:** latent component membership and the *label-switching*
> pitfall. A bimodal biophysical signal is modelled as a 2-component Gaussian
> mixture; the new skill is reasoning about a *latent discrete label* attached to
> every observation, and the new failure mode is the permutation symmetry of the
> component labels.

This project is part of the 20-project Bayesian-workflow teaching portfolio.
It assumes you have read Projects 01–12 (single parameter → hierarchical →
errors-in-variables). Here we take the first explicit step into **latent
structure**: each data point secretly belongs to one of several subpopulations,
and we must infer both the subpopulation parameters and the membership.

## Compute requirements

Heavier than the early projects but still light:

| Step | Command | Approx wall-clock (2 cores, no BLAS) |
|------|---------|--------------------------------------|
| data | `python3 data/generate_data.py` | < 1 s |
| fit  | `python3 model.py` | ~ 6 s |
| notebooks | `python3 build_notebook.py` | < 1 s |
| validate | `python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb` | < 1 s |
| test | `python3 -m pytest test_recovery.py -q` | ~ 15 s |
| SBC | `python3 sbc.py` | ~ 2–3 min (40 light refits) |
| prior sweep | `python3 prior_sensitivity.py` | ~ 30 s |

Sampling uses `draws=500, tune=1000, chains=2–4, target_accept=0.9`,
`progressbar=False`, fixed `random_seed`. The shared environment is described in
the top-level `environment.yml` / `requirements.txt` — do not create a per-project
environment.

---

## The 8-step workflow

### Step 1 — Problem & the data-generating story

**Scenario.** A single-molecule FRET (or SAXS) experiment reports a continuous
signal that depends on a molecule's *conformational state*. Suppose the molecule
populates **two** states — call them "low" and "high" — and that, at the instant
of measurement, each molecule is in one state or the other. The two states emit
signals that are Gaussian-distributed around two different means. We collect a
pooled sample of `N = 300` independent measurements. We never observe which
state produced each measurement; we only see the **bimodal histogram** of the
pooled signal.

This is the canonical *finite mixture* problem. The generative story is:

```
for each molecule i = 1..N:
    z_i ~ Categorical(w)           # latent state (0=low, 1=high), HIDDEN
    y_i ~ Normal(mu[z_i], sigma)   # observed signal
```

with known truth `w = (0.35, 0.65)`, `mu = (-2.0, 1.5)`, `sigma = 0.7`. The
`z_i` are the **latent component memberships** — the new object in this project.

**Why a mixture and not two separate datasets?** Because we cannot label the
points. If we could sort molecules by state ahead of time we would just fit two
Gaussians. The entire difficulty (and the entire lesson) is that the labels are
unobserved and must be inferred *jointly* with the parameters.

**Assumptions, made explicit:**

1. **Exactly K = 2 components.** Choosing K is itself a modelling decision. Here
   the science (two known conformers) and the visibly bimodal histogram justify
   K = 2. Over-specifying K is the analogue of Project 15's "too many factors"
   pitfall: extra empty components are non-identified.
2. **Gaussian emissions with a shared spread `sigma`.** A shared spread is a
   simplification; allowing per-component `sigma_k` is a natural extension but
   adds another label-symmetric pair of parameters.
3. **Independent draws.** No temporal correlation between successive
   measurements. If the state *persists in time* (a molecule stays open for a
   while), that is a hidden **Markov** model — Project 14.
4. **A molecule is in exactly one state when measured** (hard membership), not a
   blend.

### Step 2 — Model specification with justified priors

We do **not** sample the discrete `z_i`. Instead we marginalize them out
analytically — the sum over the two states is cheap and gives a smooth density
that NUTS can sample. PyMC's `pm.NormalMixture` does exactly this:

$$
y_i \sim \sum_{k=0}^{1} w_k\,\mathcal{N}(\mu_k,\ \sigma),
\qquad
w \sim \text{Dirichlet}(2, 2),\quad
\sigma \sim \text{HalfNormal}(1).
$$

Marginalizing the labels has two benefits: (a) the posterior geometry is
continuous, so we keep gradient-based NUTS rather than slow discrete samplers;
(b) we sidestep the *within-observation* identifiability of individual `z_i`
(which we rarely care about) and focus on the population-level parameters.

**The crucial prior is on the means.** The mixture likelihood is **invariant
under permuting the labels**: swapping `(w_0, mu_0)` with `(w_1, mu_1)` yields the
identical density. There are therefore (at least) `K! = 2` equivalent posterior
modes. NUTS, exploring faithfully, will visit *both* — and if different chains
settle in different modes, or one chain hops between them, the per-component
marginals become a useless blend of the two true states. This is **label
switching**.

The fix used here is an **ordered transform** on the means:

```python
import pymc.distributions.transforms as tr
mu = pm.Normal("mu", 0.0, 3.0, shape=2,
               transform=tr.ordered, initval=np.array([-1.0, 1.0]))
```

`tr.ordered` reparameterizes the vector so that `mu[0] < mu[1]` *always*. The
sorted `initval` starts the chains on the correct side of the constraint. With
the ordering in place, label 0 is *defined* to be the lower-mean state and the
symmetry is broken: there is now a single mode and the marginals are meaningful.

Other ways to break the symmetry (not used here, but worth knowing): order the
**weights** instead of the means; or post-hoc relabel draws by sorting (works
offline but doesn't help the sampler mix). Ordering the means is the cleanest
when the means are well separated, as they are here.

> **Priors in plain words.** `Dirichlet(2,2)` is a mild, symmetric prior on the
> two weights that gently discourages a degenerate single-component fit.
> `HalfNormal(1)` keeps `sigma` positive with most mass below ~2, reasonable for
> a standardized signal. `Normal(0,3)` on each (ordered) mean is broad relative
> to the data scale.

### Step 3 — Prior predictive checks

We draw datasets implied by the prior and look at their histograms. We want to
see **plausible bimodal signals** with varied separations and weights — not
absurdities like means at ±50 or a single spike. The notebook overlays several
prior-predictive histograms. If they looked pathological we would tighten the
mean or sigma prior before ever touching the real data.

### Step 4 — Inference (NUTS settings)

`draws=500, tune=1000, chains=4, target_accept=0.9`. We use **four chains
deliberately**: with four chains, split-R-hat is a reliable detector of label
switching. `target_accept=0.9` keeps the step size small enough to avoid
divergences around the slightly funnel-shaped sigma geometry. The fit is fast
(~6 s) because the mixture density is cheap to evaluate.

### Step 5 — Computational diagnostics

Compute and read:

- **R-hat** for `mu`, `w`, `sigma`. With ordering, all should be ≈ 1.00. *Without*
  ordering (see the broken notebook), `mu`'s R-hat explodes (often > 1.5) — that
  is the signature of label switching, and **no amount of extra tuning fixes
  it**; the cure is the constraint, not the sampler.
- **ESS** (bulk/tail) — want ≳ 400 for the quantities you will report.
- **Divergences** — should be 0; if not, raise `target_accept` to 0.95.
- **Trace plot** — each `mu` component should be one tight, well-mixed band with
  the four chains overlapping. A *bimodal* per-label trace (two chains near
  `(-2, 1.5)`, two near `(1.5, -2)`) is label switching.

### Step 6 — Posterior predictive checks

Overlay posterior-predictive densities on the observed histogram with
`az.plot_ppc`. A good fit reproduces the bimodal shape, the relative peak
heights (the weights), and the peak widths (`sigma`). Systematic misfit — e.g. a
third bump the model can't capture — would suggest K is wrong.

### Step 7 — Model criticism & the identifiability lesson

The central lesson: **report only label-invariant quantities.** Even with the
ordered transform, the "raw" labels mean only "the lower one" and "the higher
one" — fine here, but in general the robustly identifiable, science-relevant
summaries are:

- the **separation** `mu[1] - mu[0]` (how distinct are the states?),
- the **shared spread** `sigma`,
- the **weight of the higher-mean component** `w[1]` (what fraction is in the
  high state?).

`test_recovery.py` checks these (plus the ordered means) against truth. If you
later relax to per-component `sigma_k` or K > 2, always re-express conclusions in
permutation-invariant terms.

LOO/WAIC is available (we compute the pointwise log-likelihood where feasible)
for comparing K = 1 vs K = 2 vs K = 3; the clean fit's adequacy plus the
non-identifiability of extra components is usually decisive without it.

### Step 8 — Decision & communication

Translate to a collaborator's question: *"What fraction of molecules occupy the
high-FRET state, and are the two states well resolved?"* The posterior answers
both — e.g. "≈ 65% in the high state (94% CI ...), with the states separated by
≈ 3.5 signal units, cleanly resolved." See `summary_onepager.md`.

---

## Common pitfalls (tied to this project's key pitfall)

1. **Label switching (THE pitfall).** Symptom: huge R-hat on `mu`, bimodal
   per-label marginals, chains that disagree. Diagnosis: trace plot + R-hat.
   Fix: ordered transform on the means (or weights) with a sorted `initval`.
2. **Reporting per-label means as if identified.** Averaging a label-switched
   `mu[0]` gives the *overall* mean — a confident, wrong number. Always report
   label-invariant quantities.
3. **Over-specifying K.** Extra components are non-identified (empty or
   duplicated), causing poor mixing. Prefer the smallest K the data support;
   compare with posterior predictive / LOO.
4. **Sampling the discrete `z` directly.** Tempting, but mixes poorly and breaks
   gradient-based NUTS. Marginalize with `NormalMixture`.

## Files in this project

```
README.md                this guideline
data/generate_data.py    synthetic bimodal signal, known truth
model.py                 build_model / fit (ordered mixture) + add_separation
build_notebook.py        emits notebook.ipynb + notebook_broken.ipynb
notebook.ipynb           clean end-to-end workflow
notebook_broken.ipynb    label-switching debugging exercise
test_recovery.py         recovers identifiable quantities
sbc.py / SBC_REPORT.md   simulation-based calibration
prior_sensitivity.py / PRIOR_SENSITIVITY.md   sigma-prior robustness
BROKEN_BUGS.md           instructor answer key for the broken notebook
rubric.md                grading rubric + extension prompt
lessons.md               narrative takeaways
summary_onepager.md      non-technical decision summary
```
