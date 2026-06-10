# Lessons — Project 15 (probabilistic PCA)

## The one-sentence takeaway

Latent factor models have a **continuous rotation/sign symmetry**, so the raw
loadings are not identified; interpret and calibrate **rotation-invariant**
quantities (noise, reconstructed covariance, subspace) instead.

## What was new here

Projects 13–14 had *discrete* latent structure with a *finite* (permutation)
symmetry, fixed by an ordered transform. PPCA introduces *continuous* latent
structure with a *continuous* symmetry group (the orthogonal group): `W → WR`,
`z → Rᵀz` for any orthogonal `R`. There is no single "ordering" trick that fully
removes a continuous symmetry without privileging arbitrary directions, so the
cleaner posture is to **report invariants**:

- the noise `sigma`,
- the reconstructed covariance `C = W Wᵀ + sigma² I` and its derived quantities
  (trace `total_var`, eigen-spectrum, the subspace `W` spans),
- reconstructions `W z` of individual points.

This "interpret invariants, not raw parameters" idea recurs everywhere there is a
symmetry (mixtures, HMMs, neural-net weights, ICA, embeddings).

## The single most important diagnostic lesson

**Check R-hat for the right thing.** In PPCA, raw `W`'s R-hat is *supposed* to be
large — it reflects the rotation symmetry, not a sampler failure. A newcomer sees
R-hat = 3 and reaches for more tuning, more draws, reparameterization — none of
which help, because the chains are faithfully exploring a genuinely
non-identified, multimodal surface. The correct move is to recognize the symmetry
and read R-hat for `sigma` and the reconstruction, which *are* ≈ 1.0. Knowing
which quantities are estimable is part of model criticism, not an afterthought.

## Failures and surprises encountered while building this

1. **`total_var` mixes poorly even though it covers truth.** Because `total_var =
   trace(W Wᵀ) + D sigma²` involves the badly-mixing `W`, its ESS is low (tens),
   though its posterior mean tracks the truth. I kept it as a recovery target but
   leaned on `sigma` (cleanly mixed) and the **reconstructed covariance Frobenius
   error** (a deterministic function of the posterior) for the tight checks.
   *Lesson:* prefer invariants that are *both* identified *and* well-mixed for
   headline diagnostics.

2. **The recovery test needed a relative, not absolute, tolerance.** The
   reconstructed-covariance error scales with the data magnitude; a relative
   Frobenius tolerance (< 0.20) is robust across seeds where an absolute one would
   be brittle.

3. **SBC is only meaningful for identified quantities.** Trying to SBC raw `W`
   would be nonsense; we calibrate `sigma`. *Lesson:* SBC inherits the
   identifiability constraints of the model — you can only calibrate what is
   estimable.

## How to read the diagnostics here

- `sigma`, `total_var`, reconstructed-cov entries: R-hat ≈ 1.0–1.05 → trust these.
- Raw `W` entries: large R-hat, multimodal marginals → expected; do not interpret.
- The empirical, reconstructed, and true covariances should look the same to the
  eye; the relative Frobenius error quantifies the match.

## How to generalize the technique

- **Choosing K:** reconstruction-vs-K plateaus at the true K; LOO agrees; ARD
  (per-column scales) prunes surplus factors automatically.
- **Factor analysis:** swap isotropic `sigma²I` for a diagonal noise covariance.
- **Identifying constraints:** lower-triangular `W` / positive diagonal, or
  post-hoc Procrustes alignment, *if* loadings must be reported — always stated
  explicitly, because the constraint privileges arbitrary directions.
- **Beyond linear:** the same "interpret invariants" discipline applies to
  GP-LVMs, VAEs, and embeddings, where raw coordinates are likewise
  rotation/permutation-ambiguous.

## If I built it again

I would add an ARD demo (per-column `tau_k`) to the clean notebook so the
factor-pruning is visible, and a reconstruction-error-vs-K curve cell to make the
"how many factors" decision concrete rather than only described.
