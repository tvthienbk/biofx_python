# One-pager — How does the channel switch between open and closed?

**Audience:** the electrophysiologist (or MD scientist) who recorded the trace. No
statistics background assumed.

## The question

Your single-channel recording flickers between two levels. We want to quantify the
**gating kinetics**: how often does it open, how long does it stay open, and what
fraction of the time is it open? — all from a noisy trace where the true open/closed
state at each instant is uncertain.

## What we did

We fit a model that assumes the channel is, at each instant, either **closed** or
**open**, and that it switches between them with fixed per-step probabilities. The
model accounts for the measurement noise and, crucially, integrates over *all*
possible hidden open/closed sequences rather than guessing one — so the kinetic
estimates honestly reflect the uncertainty. We then checked that simulated traces
from the fitted model reproduce the statistics of your recording.

## What we found (with the synthetic demonstration numbers)

- **Occupancy:** the channel is **open about 37% of the time**.
- **Opening is rare:** from the closed state it opens with probability ≈ 0.08 per
  step, i.e. a mean **closed dwell of ~12 steps**.
- **Once open, it stays open ~7 steps** on average (closing probability ≈ 0.15 per
  step).
- The two current levels are cleanly separated relative to the noise, so the state
  assignment is confident for most of the trace.

## What this means for your decision

- **Open probability (~37%) is the headline kinetic readout** to compare across
  conditions (voltage, mutant, drug). Re-run the identical analysis on each
  condition and compare the posterior open probabilities with their credible
  intervals.
- The **dwell times** distinguish *mechanism*: a drug that increases open
  probability could do so by making the channel open more often (raising p_open) or
  by making it stay open longer (lowering p_close). This model separates those two
  routes.

## Important caveats (plain language)

- We assumed **two states** and that switching is "memoryless" (the chance of
  switching doesn't depend on how long it's already been open). Real channels can
  have extra hidden sub-states, which show up as dwell times that don't match the
  simple model — our predictive check is the guard, and if it fails the fix is more
  states.
- The labels "open"/"closed" are defined by current level (we fix "open" as the
  higher level). The robust, comparable numbers are the **occupancy** and the
  **dwell times**, which is what we report.
- These specific numbers come from a synthetic validation trace; on your real
  recording the workflow is identical and the posterior is the deliverable.

**Bottom line:** the channel is open ~37% of the time, opening rarely but staying
open ~7 steps once it does — a compact kinetic fingerprint you can compare across
your experimental conditions.
