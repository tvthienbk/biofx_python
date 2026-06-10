# One-pager — Are there two conformational states, and how many molecules are in each?

**Audience:** the experimental collaborator who ran the FRET/SAXS assay. No
statistics background assumed.

## The question

Your pooled signal histogram looks like it has **two bumps**. Are those two real
conformational states, or one broad population? And if two, **what fraction of
molecules sit in the high-signal state**, and are the states cleanly separated?

## What we did

We fit a model that assumes each molecule is in one of two states ("low" or
"high"), each emitting a Gaussian-shaped signal, and we let the data tell us the
two state means, their shared spread, and the mix of the population — *without*
ever being told which molecule is in which state. We then checked that the fitted
model reproduces your histogram and that the answer is stable to reasonable
modelling choices.

## What we found (with the synthetic demonstration numbers)

- **Two states are well resolved.** Their signal means differ by about **3.5
  units**, far larger than the within-state spread (~0.7). This is not one fat
  blob.
- **About 65% of molecules are in the high-signal state**, ~35% in the low state
  (with a tight credible interval).
- The fit reproduces both peaks of your histogram and their relative heights.

## What this means for your decision

- If the high state is the active/folded conformation, roughly **two-thirds of the
  population is active** under these conditions — a number you can compare across
  treatments.
- Because the two states are cleanly separated, **a simple threshold on the signal
  would classify most molecules correctly**; the model additionally quantifies the
  few ambiguous ones near the valley.
- The population fraction is the natural readout to track if you perturb the
  system (mutant, ligand, temperature): re-run the same analysis and compare the
  high-state fraction.

## Important caveats (plain language)

- We **assumed exactly two states**. If a third, rarer state exists, this model
  would miss it; the posterior-predictive check is your guard — if a future
  dataset shows a bump the model can't match, revisit the number of states.
- The labels "low"/"high" are *defined* by their signal value (we force "low" to
  be the smaller mean). The scientifically meaningful, robust numbers are the
  **gap between states** and the **fraction in each** — those are what we report.
- These specific numbers come from a synthetic test dataset built to validate the
  method; on your real data the workflow is identical and the printed posterior
  is the deliverable.

**Bottom line:** there are two clearly separated states, with about 65% of
molecules in the high-signal state — a stable, defensible readout to carry into
your next comparison.
