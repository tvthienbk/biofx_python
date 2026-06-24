# Project 23 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Dauparas et al. 2024 (LigandMPNN)** — the central tool. Read for: how LigandMPNN conditions sequence
  design on **nucleic-acid (and ligand/metal) context**, which makes protein-NA design tractable.
- **Watson et al. 2023, *Nature* (RFdiffusion)** — read for: scaffolding a backbone around a fixed
  context (here, the nucleic acid), the generative half of the pipeline.
- **A protein-nucleic-acid recognition review** — read for: base-specific readout vs backbone contacts,
  major/minor-groove reading, and why sequence specificity is hard (verify a current review).

## Tier 2 — build-time references
- **Wohlwend et al. 2025 (Boltz-2)** — protein-NA complex modeling for the orthogonal check (verify release).
- **Dauparas et al. 2022 (ProteinMPNN)** — the NA-blind baseline for the ProteinMPNN-vs-LigandMPNN benchmark.
- **A designed DNA-binding-protein paper** (e.g., engineered zinc fingers / TALEs / de novo DNA binders) —
  read for: what "programmable specificity" has meant historically and where ML changes it.
- **EMSA / fluorescence-anisotropy methods** — for: how you will actually measure binding + specificity.

## Tier 3 — depth
- **CRISPR-modulator / anti-CRISPR literature** — context for the [extension] "bind a Cas surface" framing.
- **RNA-targeting therapeutic reviews** — context for RNA-motif binders as a modality.
- **Papers benchmarking in-silico protein-NA design vs experiment** — the honest hit-rate question your
  project asks; compare your specificity gap to theirs.

## How to use these in your report
- Methods: cite LigandMPNN + the exact versions you ran; state your motif and template provenance.
- Results: report the intended-vs-scrambled specificity gap and an honest hit rate, not just the best design.
- Data: cite the template complex (PDB) + the source of your motif for every input.
