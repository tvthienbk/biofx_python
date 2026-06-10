# One-pager — How many hidden drivers explain your measurements, and how noisy are they?

**Audience:** the collaborator who collected the multi-channel data (spectra,
omics panel, ...). No statistics background assumed.

## The question

Your samples each carry `D` correlated readings. Those readings move together
because a few **hidden drivers** (latent factors) influence all of them at once.
How many drivers are there, how much of the signal do they explain, and how noisy
is each channel?

## What we did

We fit a model that says each sample is a weighted combination of a small number
of hidden factors, plus measurement noise. We let the data tell us the noise level
and the overall structure, and — importantly — we report only quantities that are
**well-defined**. (The individual "factor loadings" are *not* uniquely defined:
the math allows the factor axes to be rotated freely without changing the fit, so
any single loading number is arbitrary. We therefore report the things that do not
depend on that arbitrary rotation.)

## What this means in plain terms

- **A small number of hidden factors (here, two) explain the bulk of the
  variation** across your channels. The rest is measurement noise.
- **The per-channel noise level is small** (≈ 0.4 in the demo units), so the
  factor structure is real, not an artifact of noise.
- The model **reconstructs your channel-to-channel correlation pattern** accurately
  — strong evidence that the low-dimensional picture is right.

## What this means for your decision

- **Dimensionality is the headline.** If two factors capture the structure, you can
  summarize each sample by two numbers instead of `D`, simplifying downstream
  comparisons, clustering, or QC.
- **Use the reconstruction, not the raw loadings.** When comparing samples or
  conditions, compare them in terms of the reconstructed signal or the factor
  *subspace*, which are well-defined — not in terms of individual loading values,
  which can be rotated arbitrarily.
- The **noise estimate** tells you how repeatable a single measurement is, useful
  for power calculations and QC thresholds.

## Important caveats (plain language)

- We assumed the hidden drivers combine **linearly** and the noise is the same size
  in every channel. If a channel is much noisier than the rest, a small extension
  (per-channel noise) is warranted.
- **The number of factors is a choice we checked**, not an assumption: adding more
  factors does not improve the reconstruction, which is why we stop at two.
- The factor *directions* are not unique (they can be rotated). Any interpretation
  that hangs on a specific loading number is not trustworthy; interpret the
  reconstruction and the dimensionality.
- These numbers come from a synthetic validation dataset; on your real data the
  workflow is identical and the posterior is the deliverable.

**Bottom line:** a couple of hidden factors explain most of the cross-channel
structure with low per-channel noise — so you can describe each sample with a few
numbers, as long as you compare reconstructions/subspaces rather than raw loadings.
