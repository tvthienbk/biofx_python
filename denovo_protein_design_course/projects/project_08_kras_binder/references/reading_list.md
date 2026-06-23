# Project 08 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track. Cite the
exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **A KRAS druggability / RAS structural-biology review** (a recent review of RAS structure, the
  nucleotide cycle, the switch I/II regions, and why KRAS was "undruggable"). *Why read this:* it frames
  the whole project — the surface you target, the nucleotide state, and the isoform problem all come from
  here.
- **Sotorasib / adagrasib — the G12C-inhibitor papers** (e.g. Canon et al. 2019 / the AMG 510 and MRTX849
  discovery papers, plus a clinical report). *Why read this:* the proof that KRAS is druggable and the
  template for **allele-specific** targeting (the switch-II pocket of the GDP state) — and a sober view of
  why other alleles/isoforms remain hard.
- **Pacesa et al. 2025 — BindCraft** — the primary one-shot binder-design method here. *Why read this:*
  it is the BindCraft paradigm you run, with its hit-rate caveats and the AF2-in-the-loop logic.
- **Cao et al. 2022, *Nature* — target-structure-only mini-binders** — de novo binders from just the
  target surface. *Why read this:* the conceptual foundation for designing a minibinder to a chosen
  epitope on a hard surface like KRAS, with a realistic view of hit rates.
- **Watson et al. 2023, *Nature* — RFdiffusion** — the diffusion backbone generator (binder mode is the
  second paradigm). *Why read this:* how diffusion-then-sequence binder design works and where it differs
  from BindCraft.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science* — ProteinMPNN** — sequence design for the RFdiffusion backbones.
  *Why read this:* the self-consistency idea and the temperature/diversity knobs you tune.
- **Evans et al. 2021 — AlphaFold-Multimer** — complex prediction. *Why read this:* where
  `pae_interaction` (your key binder metric) comes from, and how the **same** scorer drives the
  isoform-specificity panel.
- **Bennett et al. 2023 — binder design benchmarking** — head-to-head evaluation of binder-design
  pipelines. *Why read this:* the method model for your BindCraft-vs-RFdiffusion comparison and hit-rate
  accounting on a hard target.
- **An SPR/BLI methods reference** (a surface-plasmon-resonance or bio-layer-interferometry protocol
  review). *Why read this:* to write a credible, controlled affinity + **isoform-panel** measurement plan
  in D4 (and how to immobilize a nucleotide-loaded GTPase).

## Tier 3 — depth / frontier
- **The original KRAS / RAS structure paper(s)** (the depositions behind 4OBE / 6OIM, plus a switch I/II
  conformational study). *Why read this:* the authoritative source for the switch residues you turn into
  hotspots and the GDP-vs-GTP conformational difference — verify the numbering against the actual PDB.
- **A frontier RAS-targeting design / biologic paper** (e.g. a designed binder, monobody, DARPin, or
  pan-KRAS/allele-selective biologic against the switch regions or an allele pocket). *Why read this:* the
  current state of the art on whether RAS-selective binders are achievable, and how the field validates.
- **A second frontier RAS-targeting paper** (e.g. on **isoform/allele selectivity** or
  nucleotide-state-specific recognition of RAS). *Why read this:* the centerpiece of this project is
  selectivity — this paper is your model for reasoning about, and testing, KRAS-vs-HRAS/NRAS and
  allele discrimination.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BindCraft, RFdiffusion, ProteinMPNN,
  ColabFold/AF2-Multimer; Boltz-2 if used).
- Results/Discussion: compare your hit rates, the BindCraft-vs-RFdiffusion outcome, and your **selectivity
  gaps** to what the literature reports, and explain differences (epitope, nucleotide state, isoform
  conservation, scale, filter cutoffs).
- Data: cite the KRAS/HRAS/NRAS structure papers + PDB accessions + access dates + nucleotide states.
- Always state that a passing design is a **hypothesis** until SPR/BLI + the isoform panel; never imply
  measured binding or measured selectivity, and never report a fabricated K_D.
