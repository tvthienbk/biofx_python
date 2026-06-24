# Project 07 — Validation + breadth-testing plan (DRAFT)

## Candidates (broadest by worst-case pae; SYNTHETIC ids in this dry run)
['EXAMPLE_DATA_rfdiffusion_0088', 'EXAMPLE_DATA_rfdiffusion_0142', 'EXAMPLE_DATA_rfdiffusion_0070', 'EXAMPLE_DATA_rfdiffusion_0018', 'EXAMPLE_DATA_rfdiffusion_0151']

## Tiered experiments (each with controls)
1. Express + purify (E. coli BL21(DE3)); QC by SDS-PAGE + SEC.            [go/no-go]
2. SPR / BLI vs RBD: K_D, kinetics.                                       [binding]
3. ACE2-competition assay: does the binder block ACE2-RBD?               [mechanism = neutralization proxy]
4. Pseudovirus neutralization across the variant panel (IC50 per variant). [breadth; BSL-2 surrogate, IBC-approved]

## Controls (mandatory)
- Positive: a known neutralizing binder/nanobody.
- Negative: scrambled-interface variant of each candidate.
- Negative: an irrelevant-antigen binder (specificity).

## Breadth read-out
- Report IC50 for EACH variant; rank candidates by WORST-CASE variant, not best.

## Biosafety / responsible research
- Pseudovirus assays + any viral material: institutional biosafety committee (IBC) approval at the
  appropriate containment level. Gene synthesis via an IGSC biosecurity-screening provider.
- Defensive/neutralizing purpose only; no enhancement of viral fitness/affinity/escape (MASTER_BLUEPRINT §7).

## Cost + timeline
- [fill in reagent costs, gene-synthesis quote, instrument time, and a Gantt for ~8-12 weeks of wet lab].
