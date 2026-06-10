# One-pager — When did the rate change, and by how much?

**Audience:** the collaborator who collected the count time series (events per time
bin). No statistics background assumed.

## The question

Your event counts look low for a while and then jump higher. **When** did the
change happen, and **how big** was it? And how sure are we about the timing?

## What we did

We fit a model that assumes the underlying event rate was constant at one level,
then switched to a second level at a single unknown time. The model infers the two
rates and a full probability distribution over *when* the switch occurred —
honestly reflecting any uncertainty in the timing. We also fit the same problem a
second, independent way (summing over all possible switch times) and confirmed the
two agree.

## What we found (with the synthetic demonstration numbers)

- **The switch happened at about bin 70**, with the timing pinned tightly (a narrow
  credible range of a few bins).
- **The rate jumped from ~4 to ~11 events per bin** — roughly a **2.7-fold
  increase**.
- Both independent fits agree on the timing and the rates, which gives us
  confidence the result is not an artifact of one method.

## What this means for your decision

- **The change-point timing** tells you *when* the intervention/transition took
  effect — line it up with your experimental timeline (when the catalyst was added,
  the stimulus applied, etc.).
- **The fold-change** quantifies the size of the effect, with an uncertainty range
  you can report.
- If you compare conditions, compare both the *timing* and the *fold-change* with
  their credible intervals.

## Important caveats (plain language)

- We assumed **exactly one** abrupt switch. If the rate changed gradually, or more
  than once, the picture is incomplete — the predictive check is the guard, and the
  model can be extended to multiple or gradual shifts.
- **Report the timing honestly.** When the switch is sharp (as here) the timing is a
  single confident value. When the data are ambiguous, the timing distribution can
  have **two peaks** — meaning two different times are both plausible. In that case
  we report *both* candidate times, not a single average (an average of two peaks
  points at a time the data argue against).
- We assumed the counts follow a Poisson pattern (spread tied to the level). If your
  counts are much more variable than that, a small model change handles it.
- These numbers come from a synthetic validation series; on your real data the
  workflow is identical and the posterior is the deliverable.

**Bottom line:** the event rate jumped ~2.7-fold (from ~4 to ~11 per bin) at about
bin 70, with tight timing — a clear, datable, quantifiable regime shift you can
align with your experimental events.
