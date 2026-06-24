# Project 25 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions/commits of any tool you actually run. This is the **capstone**, so it pulls
from *all prior projects' references* plus the data-driven-design and active-learning literature.

## Tier 1 — essential (read before Week 3)
- **Pacesa et al. 2025 — BindCraft.** *Why read this:* the canonical statement of the project's core
  problem — that AF2 confidence metrics **do not cleanly discriminate** true from false binders. The
  discrimination caveat is the motivation for the whole ML success-predictor exercise.
- **An ML-for-design-filtering / data-driven-design paper** (e.g. a paper learning to predict
  experimental success from in-silico features, or a learned filter/ranker for de novo designs).
  *Why read this:* the method model for your success predictor — what features, what model, what
  validation, and the honest enrichment numbers others report.
- **A "closing the DBTL loop" frontier paper** (high-throughput design→build→test→learn campaign with
  experimental feedback). *Why read this:* the template for the whole capstone — how a real campaign
  feeds measured outcomes back into the next design round.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science* — ProteinMPNN.** *Why read this:* sequence design + the
  self-consistency (scRMSD) idea that produces one of your most important features.
- **Jumper et al. 2021, *Nature* — AlphaFold2.** *Why read this:* what pLDDT and PAE *are* (and are
  not) — the features your predictor learns from, and why they are overconfident on de novo sequences.
- **Wohlwend et al. 2025 — Boltz-2.** *Why read this:* an orthogonal predictor and a predicted-affinity
  signal; another feature source and a sober view of what affinity prediction can and cannot do.
- **A scikit-learn methods reference** (the user guide / API for `LogisticRegression`,
  `RandomForestClassifier`, `cross_val_score`, ROC-AUC). *Why read this:* to cross-validate correctly,
  read feature importances right, and avoid overfitting on small N.
- **An XGBoost methods reference** (the docs / the gradient-boosting paper). *Why read this:* the
  optional stronger estimator and how to keep it shallow on a small cohort.
- **A second frontier "closing the loop" paper** (e.g. a campaign that integrated experimental labels
  to retrain its filter). *Why read this:* concrete tactics for integrating wet-lab outcomes and
  reporting the honest hit rate.

## Tier 3 — depth / frontier
- **An active-learning-for-experiment-design paper** (Bayesian optimization / acquisition functions for
  choosing which design to test next). *Why read this:* the basis for the `[stretch]` active-learning
  loop — exploit (highest P) vs explore (most uncertain).
- **Papers reporting failure modes of AF2/ESMFold on de novo or orphan sequences** (overconfidence,
  MSA dependence). *Why read this:* directly informs your failure-forensics section — the signature of
  confident-but-wrong designs.
- **The tool papers + family template for YOUR chosen campaign** (e.g. Watson 2023 RFdiffusion for
  binders; an RFantibody / nanobody paper for antibodies; a theozyme/RFdiffusion2 enzyme paper). *Why
  read this:* the authoritative methods + realistic hit rates for the campaign you actually run.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (campaign tools + scikit-learn /
  XGBoost), and state the cohort table's provenance.
- Results/Discussion: compare your **CV-AUC, feature importance, and enrichment-vs-cutoffs** to what the
  data-driven-design literature reports; explain differences (N, cohort composition, design types).
- Always report the hit rate (classical filter vs learned predictor) with N, state that a passing design
  is a **hypothesis** until measured, and never present `EXAMPLE_DATA` or any unmeasured value as real.
