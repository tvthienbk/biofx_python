# Project 03 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Watson et al. 2023, *Nature*** — RFdiffusion. Read for: how diffusion generates protein
  backbones, unconditional vs conditioned (secondary-structure) generation, and the reported
  self-consistency success rates — the spine of this whole project.
- **Dauparas et al. 2022, *Science*** — ProteinMPNN. Read for: the **self-consistency** idea
  (design backbone → design sequence → predict → scRMSD) and how many sequences per backbone to sample.
- **Jumper et al. 2021, *Nature*** — AlphaFold2. Read for: what pLDDT/PAE mean and how the refold
  prediction you measure scRMSD against is produced (and where it is overconfident).

## Tier 2 — build-time references
- **Lin et al. 2023, *Science*** — ESMFold / ESM-2. Read for: fast MSA-free refolding for
  self-consistency triage, and why it's a useful orthogonal check against AF2.
- **van Kempen et al. 2024, *Nature Biotechnology*** — Foldseek. Read for: fast structure search
  against the PDB/AFDB to score **novelty** at campaign scale.
- **Zhang & Skolnick 2004, *Proteins*** — TM-score / TM-align. Read for: the length-normalized
  TM-score and the **TM < 0.5 ≈ novel fold** convention you use as the novelty coordinate.
- **Dauparas et al. 2024 — LigandMPNN** — Read for: how MPNN extends to context/ligands; useful
  background even though this project's monomers are ligand-free.

## Tier 3 — depth / frontier (comparison methods + MSc track)
- **Yim et al. 2024 — FrameFlow** — flow-matching backbone generation. Read for: the speed/diversity
  comparison scaffold in notebook 04 (do **not** fabricate its numbers — run it or describe honestly).
- **Lin & AlQuraishi 2024 — Genie2** — diffusion backbone generation with motif support. Read for:
  the second comparison point on diversity/foldability.
- **Ingraham et al. 2023, *Nature* — Chroma** — programmable generative model for proteins. Read for:
  another frontier generative-backbone paradigm and how it frames novelty vs designability.
- **Papers reporting *failure modes* of generative backbones** (all-β difficulty, length scaling,
  designability collapse) — directly relevant to your per-topology/length frontier and failure forensics.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (RFdiffusion, ProteinMPNN,
  ColabFold/ESMFold, Foldseek pin from `00_setup`).
- Results/Discussion: compare your per-topology/length success rates and frontier shape to what the
  literature claims (e.g., Watson 2023's designability numbers), and explain differences (length,
  topology mix, MPNN settings, predictor).
- Any tool comparison (RFdiffusion vs FrameFlow vs Genie2) must report **what you actually ran**;
  never present a method's numbers you did not measure.
