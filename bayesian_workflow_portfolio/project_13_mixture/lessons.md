# Lessons — Project 13 (finite mixture)

## The one-sentence takeaway

A finite mixture is **permutation-symmetric**, so the labels are not identified
until you break the symmetry (here: an ordered transform on the means), and you
should report only **label-invariant** quantities regardless.

## What was new here

This is the first project with **latent discrete structure**. Each observation
carries a hidden label `z_i` saying which subpopulation produced it. The mental
shift from earlier projects: parameters are no longer a flat vector describing one
population; they describe *several* populations plus the membership that ties data
to them.

The practical move that makes it tractable is **marginalization**: we never sample
`z_i`. Summing over the (two) possible labels analytically gives a smooth density
that gradient-based NUTS handles well. `pm.NormalMixture` packages this. The
general lesson — *marginalize discrete latents when you can* — recurs in Project 14
(forward algorithm for an HMM) and Project 16 (a marginalized change-point).

## Failures and surprises encountered while building this

1. **`idata_kwargs={"log_likelihood": True}` crashed with the ordered transform.**
   The custom sorted `initval` triggers PyMC's "non-default initial_values" path,
   and inline log-likelihood computation refuses to convert such a model
   (`NotImplementedError: Cannot convert models with non-default initial_values`).
   Fix: drop the inline kwarg and call `pm.compute_log_likelihood(idata)` after
   sampling, wrapped in a try/except so the fit stays robust. *Lesson:* convenience
   kwargs can silently assume a "vanilla" model; latent-structure models often
   need the post-hoc API.

2. **`check_recovery` could not address `mu[0]` / `w[1]` by name.** The shared
   helper passes the dict keys straight to `az.summary(var_names=...)`, which
   filters by *base* variable name, not by indexed label. Fix: expose the
   identifiable quantities as **named scalar deterministics**
   (`mu_low`, `mu_high`, `separation`, `w_high`) via `add_separation`. *Lesson:*
   design your posterior to surface the quantities you actually test, as scalars.

3. **SBC is genuinely expensive for mixtures.** Prior draws occasionally place the
   two means almost on top of each other, producing a near-degenerate, slow fit;
   40 light simulations blew the time budget. We cut to 18 simulations with
   `N=100, draws=150`. *Lesson:* SBC for a slow model is a *smoke test*, not a
   high-resolution audit, unless you can afford hundreds of refits.

## How to read the diagnostics here

- **R-hat on `mu` is the label-switching detector.** ≈ 1.00 → identified; ≫ 1.01
  with bimodal per-label marginals → switching. The cure is the constraint, never
  more tuning.
- A **bimodal `mu[k]` marginal** is the visual fingerprint; its **mean** lands in
  the empty valley and is meaningless.
- The **posterior predictive** should reproduce both peaks and their relative
  heights (the weights) and widths (`sigma`).

## How to generalize the technique

- **More components (K > 2).** Ordering still breaks symmetry, but empty/duplicated
  components become non-identified — the analogue of Project 15's over-specified
  factors. Use a sparse Dirichlet (small concentration) to prune, and compare K by
  LOO + posterior predictive.
- **Per-component spreads `sigma_k`.** Another symmetric pair; keep them tied to
  the ordered means so the constraint still identifies labels.
- **Temporal persistence.** If the latent state *persists*, you need a Markov
  chain over states — that is exactly Project 14 (HMM), where the same ordered-mean
  trick fixes the same label symmetry.
- **Always re-express conclusions in permutation-invariant terms** (separations,
  weights, reconstructed densities), which transfer across all of the above.

## If I built it again

I would add a K=1 vs K=2 LOO comparison cell to the clean notebook (the
log-likelihood is now computed), and a sparse-Dirichlet K=5 demo to *show* empty
components, rather than only describing them in the extension prompt.
