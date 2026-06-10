# One-Page Summary — Which Few Features Matter?

**Audience:** a collaborator who needs a decision, not a posterior.

## The question

We measured 20 candidate features (assay readouts, expression markers, engineered
covariates) on 120 samples and want to know **which features actually drive the
response** — and to avoid fooling ourselves into "discovering" features that are
really noise.

## The method (and why it protects you)

We used a **shrinkage (horseshoe) model**, which does feature selection *inside a
single fit*: it pushes irrelevant features' effects to essentially zero while
letting genuine effects stand out, and it reports honest uncertainty about which
features are active. Critically, we did **not** do the common-but-wrong thing of
eyeballing the biggest effect and then re-testing it on the same data — that
"double-dipping" manufactures false confidence and would let pure noise look
significant. Everything below comes from one joint, multiplicity-aware fit.

## What we found

- **Three features drive the response** (features #2, #7, #13). Their effects are
  large, clearly nonzero, and stable regardless of modeling choices.
- **The other 17 features are indistinguishable from zero.** The model shrinks them
  to negligible values; we have no evidence they matter.
- Directions and rough sizes: feature #2 strongly positive, feature #7 negative,
  feature #13 moderately positive.

## What this means for the bench

- **Focus follow-up on features #2, #7, #13.** These are the candidates worth
  validating in an independent experiment.
- **Do not chase the other 17** based on this dataset; any apparent signal there is
  consistent with noise.
- **Validate on fresh data, not this set.** Because feature selection used this
  data, confirming the three hits requires a *new* sample to avoid circular
  reasoning.

## Caveats (one line each)

- If some features are strongly correlated with each other, the model may spread a
  single underlying effect across them — "which exact feature" can be ambiguous.
- The findings assume the response is linear in the features over the range tested.

## Bottom line

Three of twenty features matter; the rest do not, on present evidence. We reached
this with a shrinkage model in a single honest fit — no cherry-picking — so the
shortlist is trustworthy. Confirm features #2, #7, and #13 on independent data.
