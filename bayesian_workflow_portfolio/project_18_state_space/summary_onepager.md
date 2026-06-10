# One-Pager — Reading a Drifting Sensor Signal (Project 18)

**Audience:** a collaborator with a noisy time series (a sensor, a growth assay)
who wants to know the *true underlying level* and whether it is moving.

## The question

Your measurements jump around from reading to reading. Some of that jumping is the
**real underlying quantity drifting**; some is just **measurement noise**. You want
to separate the two: what is the true level right now, and is it trending?

## What we did

We fit a **state-space model**. It treats the true level as a hidden quantity that
drifts slowly over time, observed through noisy measurements. The method estimates
(1) the hidden level at every time point, with an uncertainty band, and (2) how
much of the jumpiness is genuine drift versus measurement error.

## The core difficulty (and how we handled it)

A wiggly signal can be explained two ways: the level is really bouncing around, or
the level is steady and the instrument is noisy. The data alone can't fully decide.
We resolved this by telling the model, up front, that **drift is modest and
measurement noise may be larger** -- a reasonable, disclosed assumption -- and by
using a long enough series. We checked that this assumption isn't doing all the
work (the recovered noise levels match the truth on simulated data).

## What we found

- The hidden level is recovered accurately (average error < 0.5 on the simulated
  benchmark), inside a band **tighter than the raw measurement scatter** -- the
  model genuinely sees through the noise.
- Both noise levels -- the drift rate and the measurement error -- are recovered
  near their true values.

## What you can do with it

- Read the **current level** and its credible interval instead of the last noisy
  reading.
- Read the **trend**: we report the probability the level rose over the recent
  window -- act on that, not on a single up-tick.
- For forecasting, the band fans out into the future: the model honestly says it
  becomes less sure the further ahead you look.

## Bottom line

We separated real drift from measurement noise and produced a smoothed, uncertainty
-aware estimate of the underlying level and its trend. Decide on the *level and its
direction*, not on individual noisy readings.
