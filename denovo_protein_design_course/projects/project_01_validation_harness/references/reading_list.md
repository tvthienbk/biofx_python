# Project 01 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Jumper et al. 2021, *Nature*** — AlphaFold2. Read for: what pLDDT and PAE *are*, how the model
  produces confidence, and the limits of those estimates.
- **Dauparas et al. 2022, *Science*** — ProteinMPNN. Read for: the **self-consistency** idea
  (design → predict → scRMSD) that underpins this whole project.
- **Lin et al. 2023, *Science*** — ESMFold / ESM-2. Read for: single-sequence (MSA-free) prediction
  and why it's a useful *orthogonal* check.

## Tier 2 — build-time references
- **Wohlwend et al. 2025 — Boltz-2** — open structure + affinity prediction; the third predictor
  and the stretch affinity analysis. (Verify the current release/preprint at generation time.)
- **Validation/benchmark methods** — any recent de novo design benchmarking paper that reports
  experimental outcomes alongside in-silico metrics; use these both as *method models* and as
  *sources of labeled data*.
- **TM-score / TM-align (Zhang & Skolnick)** and **Foldseek (van Kempen et al. 2024)** — structure
  comparison + novelty.
- **scikit-learn ROC/PR docs** — for the calibration analysis (AUC, precision-recall, calibration curves).

## Tier 3 — depth
- Papers reporting *failure modes* of AF2/ESMFold on de novo or orphan sequences (overconfidence,
  MSA dependence) — directly relevant to your failure-mode analysis.
- MSA-depth / single-sequence ablation studies — context for your P2 ablation.
- Any paper measuring how well predicted confidence correlates with *experimental* success — the
  exact question your project answers; compare your findings to theirs.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran**.
- Results/Discussion: compare your calibrated cutoffs and AUCs to what the literature claims, and
  explain any differences (dataset composition, design types, MSA settings).
- Data: cite the source paper + table + license for **every** labeled item in `dataset.csv`.
