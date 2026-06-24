# Project 07 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Cao et al. 2020, *Science*** — de novo ACE2-mimetic / RBD **minibinders**. Read for: the canonical
  defensive precedent — small designed proteins that neutralize SARS-CoV-2 by blocking ACE2.
- **Pacesa et al. 2025 (BindCraft)** — read for: the one-shot binder paradigm + the discrimination
  caveat (in-silico filters enrich, they do not guarantee).
- **Watson et al. 2023, *Nature* (RFdiffusion)** — read for: binder mode (diffuse against hotspots) — paradigm #2.

## Tier 2 — build-time references
- **An RBD–ACE2 structural paper / 6M0J deposition** — read for: the ACE2-binding face geometry + which residues to target.
- **A sarbecovirus / variant RBD conservation paper** — read for: which epitopes are conserved vs variable (the breadth rationale).
- **Evans et al. 2021 (AlphaFold-Multimer)** — read for: `pae_interaction` and interface confidence, the key binder metric.
- **Dauparas et al. 2022 (ProteinMPNN)** — read for: sequence design over the RFdiffusion backbones.

## Tier 3 — depth
- **Broadly-neutralizing-antibody / conserved-epitope literature** — context for designing for breadth across variants.
- **Pseudovirus neutralization assay methods** — for the validation plan (the standard, biosafe surrogate).
- **Papers benchmarking de novo binder design vs experiment** — the honest hit-rate question your project asks.

## How to use these in your report
- Methods: cite the tool papers + the versions you ran; state your epitope choice + its conservation evidence.
- Results: report the survival-at-each-layer hit rate **and** the cross-variant breadth profile (worst-case).
- Responsible research: cite §7 and state the defensive (neutralizing) framing + the biosafety oversight for validation.
