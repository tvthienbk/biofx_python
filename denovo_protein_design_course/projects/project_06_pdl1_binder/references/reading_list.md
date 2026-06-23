# Project 06 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Pacesa et al. 2025 — BindCraft** — the primary one-shot binder-design method here. *Why read this:*
  it is the BindCraft paradigm you run, with its hit-rate caveats and the AF2-in-the-loop logic.
- **Cao et al. 2022, *Nature* — target-structure-only mini-binders** — de novo binders from just the
  target surface. *Why read this:* the conceptual foundation for designing a minibinder to a chosen
  epitope, and a sober view of realistic hit rates.
- **Watson et al. 2023, *Nature* — RFdiffusion** — the diffusion backbone generator (binder mode is
  the second paradigm). *Why read this:* how diffusion-then-sequence binder design works and where it
  differs from BindCraft.
- **PD-1/PD-L1 structural biology / checkpoint-blockade review** (e.g., a recent review of the
  PD-1/PD-L1 interface and checkpoint inhibitors). *Why read this:* to choose hotspots on the
  competitive (PD-1) face and frame the therapeutic rationale correctly.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science* — ProteinMPNN** — sequence design for the RFdiffusion backbones.
  *Why read this:* the self-consistency idea and the temperature/diversity knobs you tune.
- **Evans et al. 2021 — AlphaFold-Multimer** — complex prediction. *Why read this:* where
  `pae_interaction` (your key binder metric) comes from and how to read interface confidence.
- **Bennett et al. 2023 — binder design benchmarking** — head-to-head evaluation of binder-design
  pipelines. *Why read this:* the method model for your BindCraft-vs-RFdiffusion comparison and hit-rate
  accounting.
- **An SPR/BLI methods reference** (a surface-plasmon-resonance or bio-layer-interferometry protocol
  review). *Why read this:* to write a credible, controlled affinity-measurement plan in D4.

## Tier 3 — depth / frontier
- **Original PD-1/PD-L1 co-crystal structure paper** (the deposition behind 4ZQK / 5O45). *Why read
  this:* the authoritative source for the interface residues you turn into hotspots — verify the
  numbering against the actual PDB.
- **A frontier de novo binder paper** (e.g., a recent high-throughput experimental validation of
  designed minibinders, or a BoltzGen/peptide-binder paper). *Why read this:* current state of the art
  on what fraction of in-silico binders actually bind, and how the field validates.
- **A second frontier binder paper** (e.g., on epitope-targeted or affinity-tuned de novo binders).
  *Why read this:* context for epitope-competition reasoning and affinity expectations.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BindCraft, RFdiffusion,
  ProteinMPNN, ColabFold/AF2-Multimer; Boltz-2 if used).
- Results/Discussion: compare your hit rates and the BindCraft-vs-RFdiffusion outcome to what the
  literature reports, and explain differences (target, hotspots, scale, filter cutoffs).
- Data: cite the PD-1/PD-L1 structure paper + PDB accession + access date for the target you used.
- Always state that a passing design is a **hypothesis** until SPR/BLI; never imply measured binding.
