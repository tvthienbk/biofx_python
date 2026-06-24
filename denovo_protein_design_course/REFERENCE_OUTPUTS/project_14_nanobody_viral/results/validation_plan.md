# Project 14 — Yeast-display screen + neutralization plan (DRAFT)

## Pooled library for display (top candidates; SYNTHETIC ids in this dry run)
['EXAMPLE_DATA_mock_0070', 'EXAMPLE_DATA_mock_0039', 'EXAMPLE_DATA_mock_0137', 'EXAMPLE_DATA_mock_0186', 'EXAMPLE_DATA_mock_0006', 'EXAMPLE_DATA_mock_0084', 'EXAMPLE_DATA_mock_0066', 'EXAMPLE_DATA_mock_0106']

## Yeast-display screen (the workhorse for low-hit-rate de novo antibodies)
1. Synthesize the designed VHH pool; clone into a yeast-surface-display vector.       [build]
2. FACS against labeled conserved antigen; enrich binders over rounds.                [select]
3. Deep-sequence winners; pick a diverse panel; express solubly (E. coli/yeast).      [recover]
4. SPR/BLI vs antigen (K_D, kinetics); IgFold-check CDR geometry of winners.          [characterize]

## Neutralization + breadth (defensive; biosafe)
5. Pseudovirus neutralization across the STRAIN PANEL (IC50 per strain).              [breadth; BSL-2, IBC-approved]
   - Report IC50 for EACH strain; rank by WORST-CASE strain, not best.

## Controls (mandatory)
- Positive: a known neutralizing nanobody.
- Negative: scrambled-CDR variant of each candidate.
- Negative: an irrelevant-antigen VHH (specificity).

## Biosafety / responsible research
- Pseudovirus assays + any viral material: institutional biosafety committee (IBC) approval at the
  appropriate containment level. Gene synthesis via an IGSC biosecurity-screening provider.
- Defensive/neutralizing purpose only; no enhancement of viral fitness/affinity/escape (MASTER_BLUEPRINT §7).

## Cost + timeline
- [fill in library synthesis, display reagents, FACS time, SPR, pseudovirus panel, and a Gantt].
