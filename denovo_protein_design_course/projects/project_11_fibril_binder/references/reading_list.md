# Project 11 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Fitzpatrick et al. 2017, *Nature* — cryo-EM structures of tau filaments from Alzheimer's brain.**
  *Why read this:* the authoritative tau PHF/SF fibril structure (the 5O3L/5O3T deposition) — the
  ordered cross-β core and the **exposed surface** you read your fibril epitope off. This is your
  target conformation.
- **Schweighauser et al. 2020, *Nature* (or Guerrero-Ferreira et al. 2018, *eLife*) — α-synuclein fibril
  cryo-EM structures.** *Why read this:* the α-synuclein fibril fold (the 6CU7/6H6B family) — the
  second candidate target and the tau↔α-syn **cross-amyloid** off-target for the discrimination
  extension.
- **Pacesa et al. 2025 — BindCraft.** *Why read this:* the primary one-shot binder-design method you
  run (AF2-in-the-loop), with its hit-rate caveats — and a sober view of how hard binder design is
  before you add the conformational-selectivity requirement.
- **Watson et al. 2023, *Nature* — RFdiffusion.** *Why read this:* the diffusion backbone generator
  (binder mode is the second paradigm); how diffusion-then-sequence binder design works and where it
  differs from BindCraft.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science* — ProteinMPNN.** *Why read this:* sequence design for the
  RFdiffusion backbones; the self-consistency idea and the temperature/diversity knobs you tune.
- **Evans et al. 2021 — AlphaFold-Multimer.** *Why read this:* where `pae_interaction` (your key binder
  metric) comes from and how to read interface confidence — which here you must compute **per
  conformer** (fibril and monomer) for the specificity test.
- **An amyloid-PET-tracer / conformation-specific-antibody reference** (e.g., a review of tau/amyloid PET
  tracers such as flortaucipir/PI-2620, or a conformational anti-fibril antibody paper). *Why read
  this:* the real-world precedent for conformation-selective amyloid probes — what selectivity is
  needed, how it is measured, and the diagnostic-tracer translational path (BBB, radiochemistry).
- **An ELISA/SPR (and conformational-selectivity assay) methods reference.** *Why read this:* to write
  a credible, controlled **fibril-vs-monomer** affinity/selectivity plan in D4 (matched monomer +
  in-vitro-fibril preps, ThT/TEM confirmation, the selectivity ratio).

## Tier 3 — depth / frontier
- **Original fibril cryo-EM deposition paper(s)** behind the exact PDBs you use (5O3L/5O3T, 6CU7/6H6B).
  *Why read this:* the authoritative source for the surface residues you turn into hotspots — verify
  the numbering and the ordered-core range against the actual PDB.
- **A frontier conformation-specific / state-selective binder paper** (e.g., de novo or engineered
  binders that discriminate one conformational/aggregation state of a target from another). *Why read
  this:* current state of the art on the hardest part of this project — rejecting the off-state
  (here, the monomer) — and how the field validates conformational selectivity experimentally.
- **A second frontier de novo binder paper** (e.g., a high-throughput experimental validation of
  designed minibinders, or an epitope-targeted/affinity-tuned binder paper). *Why read this:* realistic
  context for what fraction of in-silico binders actually bind, and how the field reports hit rates.
- **An intrinsically-disordered-protein / amyloid-aggregation review** (tau or α-synuclein aggregation
  mechanism). *Why read this:* why the monomer has no fixed fold (the modeling caveat for the
  counter-test) and how monomer→fibril conversion creates the conformational epitope you target.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BindCraft, RFdiffusion,
  ProteinMPNN, ColabFold/AF2-Multimer; Boltz-2 if used).
- Results/Discussion: compare your fibril hit rate AND your **conformational-selective** rate, and the
  BindCraft-vs-RFdiffusion outcome, to what the literature reports; explain differences (target,
  epitope, scale, GAP_MIN cutoff).
- Data: cite the fibril cryo-EM paper(s) + PDB accession + access date for the target you used, and the
  monomer-model source.
- Always state that a passing, "selective" design is a **hypothesis** until the fibril-vs-monomer assay;
  never imply measured binding or a measured fold-selectivity, and never fabricate a K_D.
