# One-Pager — Binding Across Protein Families (non-technical)

## The question

We ran a binary binding assay (binds / doesn't) on **10 protein families**, ~12
assays each, and recorded a physicochemical **score** for every assay. Two things
matter: does the score predict binding, and do families differ in their baseline
tendency to bind?

## The trap we avoided

With only ~12 assays per family, a family's raw binding rate is noisy. Two wrong
shortcuts:

- **Trust each family's raw rate** — you will over-state differences that are just
  noise.
- **Pool everything** (or over-tighten the model) — you erase real family
  differences and pretend all families behave identically.

We used a **hierarchical model with varying intercepts**: each family gets its own
baseline, but families are tied together and noisy ones are pulled toward the
overall average by a data-driven amount. We were careful **not** to over-pool — a
common mistake when groups are few.

## What we found

- **The score predicts binding.** Higher score means higher binding odds, and this
  effect is solid and not sensitive to modeling choices.
- **Families do differ** in baseline binding tendency — a real, moderate spread —
  but the best per-family estimates are the **shrunken** ones, not the raw rates.
- **The honest per-family numbers** pull the most extreme-looking families back
  toward the pack.

## What to do with this

1. **Use the score** as a binding predictor; the relationship is reliable.
2. **Report shrunken per-family baselines**, not raw hit-rates, especially for
   families flagged as unusually high or low on raw data.
3. **To sharpen family-level conclusions, add families**, not just more assays
   within the existing few — the uncertainty about *how much families differ* is
   driven by having only 10 families.

## One caveat worth stating

How *much* families differ is the one number that depends on modeling assumptions
when groups are few; a skeptical model would make families look more alike. The
score effect is robust; treat the family spread as "real but moderate" rather than
an exact figure, and collect more families if a decision hinges on it.
