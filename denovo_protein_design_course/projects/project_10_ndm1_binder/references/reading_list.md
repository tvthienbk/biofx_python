# Project 10 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **An NDM-1 / metallo-β-lactamase structure paper** (e.g., a crystal structure of NDM-1 with its
  di-zinc active site, behind 3SPU/4EYL). *Why read this:* it is the authoritative source for the
  di-zinc geometry and the active-site-rim residues you turn into occluding hotspots — and it tells you
  which residues coordinate the Zn²⁺ (do **not** design over those).
- **A metallo-β-lactamase-inhibitor review** (the inhibitor landscape: why class B enzymes evade the
  serine-β-lactamase inhibitors, and what an NDM-1 inhibitor must do). *Why read this:* to frame the
  defensive-anti-AMR rationale and understand why "occlude the substrate channel" is a credible
  inhibition strategy when no clinical inhibitor exists.
- **Pacesa et al. 2025 — BindCraft** — the primary one-shot binder-design method here. *Why read this:*
  it is the BindCraft paradigm you run, with its hit-rate caveats and the AF2-in-the-loop logic.
- **Dauparas et al. 2024 — LigandMPNN** — ligand/metal-aware sequence design. *Why read this:* you use
  LigandMPNN (not vanilla ProteinMPNN) so interface residues near the **di-zinc site** are designed
  metal-aware; this is the key swap vs the PD-L1 binder template.
- **Watson et al. 2023, *Nature* — RFdiffusion** — the diffusion backbone generator (binder mode is the
  second paradigm). *Why read this:* how diffusion-then-sequence binder design works and where it
  differs from BindCraft.

## Tier 2 — build-time references
- **Evans et al. 2021 — AlphaFold-Multimer** — complex prediction. *Why read this:* where
  `pae_interaction` (your key binder metric) comes from and how to read interface confidence — and why
  AF2 does **not** place Zn²⁺ (keep the metal as a target heteroatom).
- **Cao et al. 2022, *Nature* — target-structure-only mini-binders** — de novo binders from just the
  target surface. *Why read this:* the conceptual foundation for designing a minibinder to a chosen
  epitope (here, the active-site rim), and a sober view of realistic hit rates.
- **A nitrocefin / β-lactamase-kinetics assay methods reference** (a chromogenic-cephalosporin or
  carbapenem-hydrolysis inhibition protocol; IC50/K_i determination). *Why read this:* to write a
  credible, controlled **inhibition** assay in D4 — and to internalize that **binding ≠ inhibition**,
  so the IC50 comes only from the assay.
- **Bennett et al. 2023 — binder design benchmarking** — head-to-head evaluation of binder-design
  pipelines. *Why read this:* the method model for your BindCraft-vs-RFdiffusion comparison and
  hit-rate accounting.

## Tier 3 — depth / frontier
- **A frontier AMR-countermeasure paper** (e.g., a de novo protein/peptide binder or designed inhibitor
  against an antibiotic-resistance enzyme, or a computational metallo-β-lactamase-inhibitor study).
  *Why read this:* current state of the art on neutralizing resistance enzymes by design, and how the
  field validates an inhibitor (the defensible frontier framing for this project).
- **A frontier de novo binder paper** (e.g., a recent high-throughput experimental validation of
  designed minibinders, or a BoltzGen/peptide-binder paper). *Why read this:* current state of the art
  on what fraction of in-silico binders actually bind, and how the field validates.
- **Original NDM-1 structure/mechanism paper** (the deposition behind 3SPU/4EYL + the di-zinc catalytic
  mechanism). *Why read this:* the authoritative source for the rim residues and the catalytic role of
  the two Zn²⁺ — verify the numbering against the actual PDB.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BindCraft, RFdiffusion,
  **LigandMPNN**, ColabFold/AF2-Multimer; Boltz-2 if used).
- Results/Discussion: compare your hit rates and the BindCraft-vs-RFdiffusion + rim-vs-distal outcomes
  to what the literature reports, and explain differences (target, rim hotspots, scale, filter cutoffs).
- Data: cite the NDM-1 structure paper + PDB accession + access date for the target you used; note that
  both Zn²⁺ were retained.
- Always state that a passing design is a **hypothesis** until the nitrocefin/carbapenem IC50 assay;
  **never imply measured binding or inhibition, and never report an in-silico IC50.**
