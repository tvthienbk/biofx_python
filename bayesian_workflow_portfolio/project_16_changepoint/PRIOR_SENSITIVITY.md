# Prior Sensitivity — change-point model

## What we vary and why

The prior most specific to a change-point model is the **prior over `tau`** — where
we believe the shift is likely to be. The default is a flat `DiscreteUniform` over
all interior times (no prior knowledge). When the shift is sharp and
well-separated, the likelihood dominates and the `tau` prior barely matters; when
the shift is weak or the series is short, the `tau` prior can steer the answer. We
refit under three priors (implemented as a weighted discrete prior on `tau` via a
`pm.Potential`) and compare the `tau` mode and the pre/post rates:

| Prior on `tau` | Character |
|----------------|-----------|
| uniform  | flat over 1..T-1 (default; no information) |
| early    | linearly favours earlier shift times |
| centered | triangular, favours the middle of the series |

## Results

From `python3 prior_sensitivity.py`:

```
Data: T=120, true tau=70, lam0=4.0, lam1=11.0

   tau prior  tau mode  lam0 mean  lam1 mean
     uniform        70      4.128     11.292
       early        69      4.131     11.298
    centered        69      4.131     11.298

tau mode range across priors: [69, 70] (true 70)
```

## Interpretation

The shift in this dataset is **sharp and well-separated** (rate jumps from ~4 to
~11), so the likelihood pins the change-point: the `tau` mode moves by at most one
bin across the three priors, and the rate estimates are essentially unchanged. The
posterior is **robust** to the `tau` prior here.

**When would the prior matter?** For a *weak* shift (rates close together) or a
*short* series, several change times become nearly equally likely — the `tau`
posterior spreads out or splits into multiple modes — and the prior then visibly
tilts the answer toward the favoured region. That is precisely the regime where the
**multimodal-tau pitfall** bites: the prior choice and the choice of summary
(mode/credible-set vs mean) both become first-order decisions, not formalities.

**Practical guidance.** Report the flat-prior result by default, but always run the
sweep. If `tau` is not sharply pinned, present the full `P(tau | y)` under each
prior and be explicit that the timing estimate is partly prior-driven.
