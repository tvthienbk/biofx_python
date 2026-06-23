# Project 05 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. Each entry has a one-line "why read this."

## Tier 1 — essential (read before Week 3)
- **The 4-layer validation concept (validation-ref lineage)** — the worked example's
  validation-reference (Project 01's harness + `MASTER_BLUEPRINT.md §0`). *Why:* it is the origin of
  the self-consistency → orthogonal → physics → dynamics filter you are implementing; your engine is
  its packaged, tested form.
- **Dauparas et al. 2022, *Science* — ProteinMPNN.** *Why:* the **self-consistency** idea (design →
  predict → scRMSD) that Layer 1 rests on; understand why scRMSD < ~2 Å is the field bar.
- **Jumper et al. 2021, *Nature* — AlphaFold2.** *Why:* what pLDDT and PAE *are* (and are **not** —
  pLDDT ≠ stability), the confidence signals Layer 1 thresholds.
- **Pacesa et al. 2025 — BindCraft.** *Why:* the **discrimination caveat** at the heart of this
  project — in-silico metrics enrich but do not guarantee; false positives survive every filter.

## Tier 2 — build-time references
- **Lin et al. 2023, *Science* — ESMFold / ESM-2.** *Why:* the single-sequence (MSA-free) predictor
  that provides Layer 2's **orthogonal** opinion; different inductive bias catches AF2 overconfidence.
- **Wohlwend et al. 2025 — Boltz-2.** *Why:* open structure + affinity predictor; a third orthogonal
  signal and the affinity input for binder physics reasoning. (Verify the current release at generation time.)
- **Norn et al. 2021, *PNAS* — energy landscapes / funnels for design.** *Why:* the physics
  intuition behind Layers 3–4 — a design needs a funneled landscape, not just a good single-point
  score; motivates why dynamics (MD) catches "folds-but-melts" cases.
- **A software-engineering / reproducibility reference on testing scientific code** (e.g., Wilson et
  al. 2014/2017 "Good/Best Practices for Scientific Computing", *PLOS Biology / Comput. Biol.*).
  *Why:* this is a *software* deliverable — unit tests, fixed seeds, clean function boundaries, and
  reproducible releases are graded; read this for how to test scientific code well.

## Tier 3 — depth / frontier
- **An ML-for-design-filtering / learned-scoring paper** (e.g., a learned binder-success classifier
  or an AF2-confidence calibration study). *Why:* shows where a *learned* filter beats hand-set
  cutoffs — and where it overfits; context for the limits of your fixed-cutoff engine.
- **A second ML-for-design-ranking / active-learning-for-design paper.** *Why:* how labs use model
  scores to *prioritize* (rank), not just pass/fail — directly relevant to `rank_designs()` and to
  the cutoff-sensitivity question.
- **Papers reporting AF2/ESMFold failure modes on de novo or orphan sequences** (overconfidence,
  MSA dependence). *Why:* the empirical basis for your false-positive forensics — which designs slip
  through every layer.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** for each metric source (AF2, ESMFold,
  Boltz, PyRosetta, OpenMM), and the testing-practices reference for your engineering choices.
- Results/Discussion: frame your enrichment + cutoff-sensitivity findings against the discrimination
  caveat (Pacesa 2025); state explicitly where your filter fails to separate true from false.
- Data: cite the source paper + table + license for **every** item in any production pool you score;
  label all `EXAMPLE_DATA` figures as synthetic.
