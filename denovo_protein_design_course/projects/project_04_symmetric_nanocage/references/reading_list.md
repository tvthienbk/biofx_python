# Project 04 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Watson et al. 2023, *Nature*** — RFdiffusion (including **symmetric** generation). Read for: how
  symmetric mode + symmetric contigs build Cn/Dn assemblies, and the realistic success rates.
- **Dauparas et al. 2022, *Science*** — ProteinMPNN, including **tied positions**. Read for: why
  tying symmetry-related residues to one sequence is what makes an assembly truly symmetric.
- **Evans et al. 2021 (AlphaFold-Multimer, bioRxiv/Nat. Methods)** — Read for: predicting and scoring
  multimer interfaces (interface pAE / ipTM) — the validation signal at the heart of this project.

## Tier 2 — build-time references
- **Wicky et al. 2022, *Science*** — hyperstable de novo **symmetric assemblies** with an end-to-end
  design + validation pipeline. Read for: the experimental confirmation pipeline (nsEM/SEC/MS) and
  realistic assembly-success accounting — the model for your D4 plan.
- **King et al. 2012/2014, *Science/Nature*** & **Bale et al. 2016, *Science*** — designed
  **two-component protein nanomaterials / nanocages**. Read for: how subunits are designed to
  co-assemble into a target architecture (the I3-01 / I53-50 family context).
- **Marcandalli et al. 2019, *Cell*** — RSV-F **nanoparticle vaccine**. Read for: the
  antigen-display rationale (why multivalent presentation boosts immunogenicity) framing your
  responsible-research and antigen-graft extension.
- **SEC-MALS / nsEM methods reference** — any rigorous methods paper or review on SEC-MALS for
  absolute molar-mass / oligomeric-state determination and negative-stain EM for assembly
  confirmation. Read for: how the *actual* oligomeric state is measured (not predicted).

## Tier 3 — depth / frontier
- **Hsia et al. 2016, *Nature*** — a designed **icosahedral** nanocage (I3-01). Read for: the
  stretch toward higher point groups (tetrahedral/octahedral/icosahedral cages).
- A recent **frontier symmetric-design** paper (e.g., single-component cyclic/dihedral oligomer
  design, or a symmetric-RFdiffusion application). Read for: where the field is now and what success
  rates current methods actually report. (Verify the current state of the art at generation time.)
- A paper analysing **oligomeric-state prediction / wrong-oligomer error** with AF-Multimer. Read
  for: how reliably predicted interface confidence maps to the true assembled state — directly the
  necessary-not-sufficient caveat your filter rests on.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (RFdiffusion, ProteinMPNN,
  ColabFold/AF2-Multimer).
- Results/Discussion: compare your assembly-success rates and wrong-oligomer rates to what the
  symmetric-design literature reports, and explain any differences (symmetry order, subunit size,
  filter cutoffs).
- Data: cite the source paper + entry + license for every reference homo-oligomer / nanocage you use.
