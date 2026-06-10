# Prior Sensitivity — Project 19 (rate-constant priors)

## What we vary

Mechanistic priors carry real information (plausible physiological ranges). We
test how much the conclusion leans on them by refitting under three priors on
`(log k, log V)` and comparing the posteriors **and** the `(k, V)` correlation
(`prior_sensitivity.py`):

| Label | `log k` prior | `log V` prior | Character |
|---|---|---|---|
| Informative | `N(-1, 0.7)` | `N(2, 0.5)` | default; plausible ranges |
| Weak | `N(-1, 1.5)` | `N(2, 1.5)` | broad but proper |
| Vague | `N(0, 3)` | `N(0, 3)` | nearly flat on log scale |

## What to expect

- With the **full design** (early + late timepoints), `k` and `V` stay near their
  truths across all three priors — the data identify the mechanism, so the
  posterior is fairly **robust** to the prior.
- The posterior **`corr(k, V)` grows** as the prior loosens. This is the window
  onto the latent practical non-identifiability: the prior was quietly helping to
  keep `k` and `V` separated, and relaxing it lets them correlate more.

## Interpretation

Two lessons sit together here:

1. **With a good design, mechanistic inference is robust** to reasonable prior
   choices — the experiment, not the prior, is doing the work.
2. **The prior is still load-bearing for identifiability.** The rising `corr(k, V)`
   under vague priors previews what happens when the *design* is poor (the broken
   notebook): then the prior is the only thing standing between you and a ridge.

So: invest in the design first; use informative mechanistic priors as a safety
net; and always report a well-identified combination (clearance `CL = k*V`)
alongside the individual constants.
