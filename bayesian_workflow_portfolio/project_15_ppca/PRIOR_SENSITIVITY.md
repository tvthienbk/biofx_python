# Prior Sensitivity — Probabilistic PCA

## What we vary and why

The prior most specific to PPCA is the **loading-scale prior** — the `Normal(0, s)`
on the entries of `W`. It controls how much variance the model attributes to the
latent factors versus the isotropic noise. A too-tight prior shrinks the loadings
and pushes structure into `sigma` (under-fitting the factors); a very vague prior
is barely informative. We refit the same dataset under three scales and compare the
**identifiable** summaries: `sigma` and the reconstructed-covariance error
(rotation-invariant).

| Prior on W scale | Character |
|------------------|-----------|
| `Normal(0, 0.5)` | tight (risk: shrinks real loadings) |
| `Normal(0, 1.0)` | default (weakly-informative) |
| `Normal(0, 3.0)` | vague |

## Results

From `python3 prior_sensitivity.py`:

```
Data: N=150 x D=6, K=2; true sigma=0.40

      prior on W scale  sigma mean  recon-cov rel err
  tight  Normal(0,0.5)       0.384              0.149
 default Normal(0,1.0)       0.384              0.097
  vague  Normal(0,3.0)       0.384              0.089

Max spread: sigma=0.0004, recon-cov rel err range=[0.089, 0.149]
```

## Interpretation

The noise estimate `sigma` is **essentially prior-independent** (spread < 0.001):
the data covariance pins it tightly regardless of the loading prior. The
reconstructed-covariance error is also small under all three priors, but the
**tight** `Normal(0, 0.5)` prior is slightly worse (rel err 0.15 vs 0.09) — exactly
the expected behaviour, because a too-tight loading prior shrinks the true loadings
and mildly under-reconstructs the covariance. The default and vague priors are
indistinguishable.

**Takeaway.** The identifiable quantities (sigma, reconstructed covariance) are
**robust** to the loading-scale prior over a reasonable range; the only real risk is
an *over-tight* prior that shrinks genuine structure. Since the reconstruction is
rotation-invariant, the data covariance constrains it no matter how `W` itself is
rotated.

**Practical guidance.** Use the default `Normal(0, 1)`; if you have reason to expect
small loadings, check that a tighter prior is not silently shrinking real signal
(watch the reconstruction error). As always, never read prior sensitivity off the
raw loadings — they are non-identified — only off the invariants.
