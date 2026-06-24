# Project 02 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run, and pin the upstream commit.

## Tier 1 — essential (read before Week 3)
- **Dauparas et al. 2022, *Science*** — ProteinMPNN. *Why read this:* the core method and the
  temperature/noise/sampling knobs you will sweep; the self-consistency idea is the backbone of this
  whole project.
- **Sumida et al. 2024, *JACS*** — ProteinMPNN for improved expression/stability. *Why read this:*
  the direct evidence that MPNN redesign changes whether proteins express and fold — the motivation
  for the expressibility half of your study.
- **Jumper et al. 2021, *Nature*** — AlphaFold2. *Why read this:* what pLDDT/PAE mean and how to read
  the recapitulation prediction that defines your foldability metric.

## Tier 2 — build-time references
- **Dauparas et al. 2024 — LigandMPNN** — *Why read this:* the ligand/metal/NA-aware successor; how
  to run it as a ProteinMPNN-equivalent backend and where it matters for later projects.
- **Lin et al. 2023, *Science*** — ESMFold / ESM-2. *Why read this:* the fast, MSA-free predictor you
  use to triage recapitulation at sweep scale (your compute bottleneck).
- **Hsu et al. 2022, *ICML*** — ESM-IF (inverse folding from structure + sequence). *Why read this:*
  the benchmark alternative to ProteinMPNN in your tool comparison.
- **Sormanni, Aprile & Vendruscolo 2015, *JMB*** — CamSol. *Why read this:* the real
  intrinsic-solubility method your `camsol_like` heuristic only *imitates* — read it to state exactly
  how your teaching score differs from calibrated CamSol.

## Tier 3 — depth / MSc track
- **Chennakesavalu & Rotskoff (or a current SAP / aggregation-propensity paper)** — spatial
  aggregation propensity. *Why read this:* the structure-aware basis for hydrophobic-patch scoring;
  context for why a sequence-only proxy is limited.
- **A codon-optimization / heterologous-expression review** (e.g., on *E. coli* codon usage, rare
  codons, and soluble expression of de novo proteins). *Why read this:* turns your in-silico picks
  into an orderable, expressible gene for the D4 plan.
- **A frontier MPNN-variant paper** — e.g., **FAMPNN** (full-atom MPNN) or another current
  inverse-folding model. *Why read this:* the moving frontier your tool comparison should acknowledge;
  verify the current public release at generation time.
- **A second frontier inverse-folding / consensus-design paper** — e.g., on consensus/ancestral
  sequence reconstruction for stability. *Why read this:* grounds the consensus-vs-single-sequence
  extension task.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (ProteinMPNN/LigandMPNN change).
- Results/Discussion: compare your recovery (~40–50% typical) and recapitulation rates to what the
  literature reports, and explain differences (backbone quality, settings, predictor choice).
- Data: cite the source (Project 03 run, or paper DOI + supplementary file + license) for **every**
  backbone you sweep.
- Solubility: state explicitly that `camsol_like` is a heuristic, not CamSol (Sormanni 2015), and
  that no in-silico proxy substitutes for express → SDS-PAGE → SEC.
