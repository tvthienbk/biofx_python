# Lessons — Project 16 (change-point)

## The one-sentence takeaway

A discrete change-point posterior can be **multimodal**, so summarize `tau` by its
**mode and a credible set** (never the mean), and prefer **marginalizing** the
discrete tau over sampling it.

## What was new here

This project is about a discrete **structural** change: a single unknown time at
which the data-generating regime switches. It connects two earlier threads:

- Like the HMM (Project 14), it has a **discrete latent** (the change time), and
  the robust move is again to **marginalize** it — here trivially, because `tau`
  has only `T-1` possible values, so we sum the likelihood over all of them with a
  cumulative-Poisson + `logsumexp` trick.
- Like every latent-structure project, the **summary** matters as much as the fit:
  a correct posterior reported with the wrong statistic (the mean of a multimodal
  discrete variable) is a wrong answer.

We ship **two implementations** and cross-check them: the classic
`pm.DiscreteUniform` + `switch` model (NUTS for rates, Metropolis for `tau`) and a
fully-marginalized model (pure NUTS, `tau` summed out, `P(tau | y)` reconstructed
afterward). Agreement between the two is strong evidence both are coded right.

## Failures and surprises encountered while building this

1. **The index convention is a genuine trap.** `switch(cond, a, b)` returns `a`
   where `cond` is true. With `tau` defined as the *first post-shift index*, the
   correct rate is `switch(tau > t, lam0, lam1)` — and it must match
   `generate_data.py` exactly, or recovery silently returns swapped rates. I pinned
   the convention in both files and made the off-by-one a seeded bug. *Lesson:*
   write the data generator and the model against the *same* explicit convention,
   and let a recovery test guard it.

2. **The marginalized likelihood needs careful cumulative sums.** `c0[k] = sum_{t<k}
   logp0` and `c1[k] = sum_{t>=k} logp1` must be aligned so that `c0[tau] + c1[tau]`
   is the log-likelihood for change index `tau`. Getting the prepended-zero offsets
   right (so `tau` indexes correctly into the cumulative arrays) was the fiddly
   part; the cross-check against the discrete model caught my first off-by-one.

3. **Reconstructing `P(tau | y)` requires a compiled pytensor function.** Since the
   marginal model never samples `tau`, I expose `tau_posterior_from_marginal`,
   which compiles the per-tau joint log-weights and averages `softmax`ed weights
   over posterior `(lam0, lam1)` draws. *Lesson:* marginalizing a latent doesn't
   lose it — you can always recover its posterior by re-weighting after the fact.

## How to read the diagnostics here

- **Rates:** R-hat ≈ 1.0, healthy ESS. These are the clean, identifiable results.
- **tau:** look at the *whole* `P(tau | y)`. A single sharp peak (as here) → report
  the mode and a tight credible set. Multiple peaks → report *all* candidate times;
  the multimodality is information, not noise, and the **mean is meaningless**.
- **Discrete vs marginal:** the two `P(tau | y)` curves and the two rate posteriors
  should overlay. Divergence → an index/normalization bug.

## How to generalize the technique

- **Multiple change-points:** ordered pairs/tuples of taus (discrete) or a
  marginalization over ordered combinations; or a non-parametric prior over the
  number of segments.
- **Gradual transitions:** replace the hard `switch` with a logistic ramp and infer
  the sharpness — `s → 0` recovers the abrupt case.
- **Over-dispersed counts:** swap Poisson for Negative-Binomial within each regime
  (cf. Project 06).
- **Other emissions:** the marginalization trick works for any per-observation
  likelihood (Gaussian level shift, variance change, etc.) — just swap the
  cumulative log-prob.

## The deepest lesson

A **correct posterior summarized incorrectly is a wrong result.** The change-point
posterior over `tau` is exactly right, but its *mean* points at an unsupported
time when the posterior is multimodal or skewed. Choosing the right summary
(mode + credible set, or "both peaks") is part of the analysis, not an afterthought
— and it is the single most transferable habit from this project.

## If I built it again

I would add a deliberately *weak* shift (rates close together) as a second dataset
in the notebook to actually *exhibit* a multimodal/diffuse `tau` posterior, rather
than only warning about it on the sharp-shift data where `tau` happens to be
unimodal.
