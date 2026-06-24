# Project 22 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. Multi-state design is a frontier, so verify the
current release/preprint of each method at generation time.

## Tier 1 — essential (read before Week 3)
- **Langan et al. 2019, *Nature* — LOCKR.** The canonical de novo *switchable* protein system: one
  designed chain with a latch/cage that encodes two states. *Why read this:* it is the conceptual
  spine of the whole project — how two states live in one sequence and toggle on a trigger.
- **Watson et al. 2023, *Nature* — RFdiffusion.** Generative backbone design. *Why read this:* you
  run it **twice** to build the two state backbones; understand contigs, partial diffusion, and how
  to make state B a controlled variant of state A.
- **Jumper et al. 2021, *Nature* — AlphaFold2.** What pLDDT/PAE are and how confidence is produced.
  *Why read this:* you predict **both** states from one sequence — and AF2 returns a single dominant
  state, which is the central limitation you must reason about.
- **A multi-state / ensemble ProteinMPNN reference** (Dauparas et al. 2022 *Science* as the base
  method, plus a multi-state/tied-design write-up). *Why read this:* multi-state MPNN ties residue
  identities across both backbones to find one shared sequence — the core design move here.

## Tier 2 — build-time references
- **Praetorius et al. 2023 (or an equivalent hinge / two-state design paper).** A de novo
  hinge/two-state protein. *Why read this:* a concrete, recent example of designing distinct states
  and what success/failure looked like — calibrate your own expectations against it.
- **An allosteric-design review** (designed allostery / switchable proteins, e.g. a Baker-lab or
  conformational-design review). *Why read this:* frames *why* one sequence rarely satisfies two
  states and how the field thinks about the energy gap between them.
- **Eastman et al. 2017, *PLoS Comput Biol* — OpenMM.** *Why read this:* the engine for the
  (extension) transition-plausibility MD; understand what a short MD can and cannot tell you about
  A↔B (it is not a free-energy calculation).
- **ESMFold (Lin et al. 2023, *Science*).** Single-sequence prediction. *Why read this:* fast
  orthogonal triage of both states when AF2 ×2-per-design is too expensive.

## Tier 3 — depth / frontier
- Papers on **biasing structure prediction toward a chosen state** (templates / initial guess /
  state-conditioned prediction). *Why read this:* the only honest way to test whether *both* states
  are accessible to one sequence — directly addresses the AF2-only-sees-one-state problem.
- **Frontier multi-state / switch design** (the most recent switchable-protein or conformational
  free-energy-design preprint you can find at course start). *Why read this:* the field moves fast;
  compare your hit rate and energy-gap reasoning to the current state of the art.
- **Physics-based ΔΔG / free-energy methods** (FoldX / Rosetta ddG / MD free-energy). *Why read
  this:* the energy-gap proxy in `multistate_tools.py` is teaching-grade; this is what a *real* state
  energy difference would require.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion, ProteinMPNN, AF2/ESMFold,
  OpenMM commits/releases).
- Results/Discussion: compare your per-state hit rates and energy-gap distribution to the literature,
  and explain differences (topology, trigger, tying scheme, MSA settings).
- Always foreground the caveat: **AF2 may only show one of the two states**, so an in-silico "switch"
  is a hypothesis, not a measurement — the read-out plan is what would test it.
