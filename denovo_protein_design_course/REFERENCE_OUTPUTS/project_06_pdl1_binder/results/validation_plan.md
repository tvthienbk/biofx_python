# PD-L1 Mini-Binder Validation Plan (Project 06 — by <your name>, <date>)

## Candidates
Top 14 candidates carried forward ({'bindcraft': 3, 'rfdiffusion': 11}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured — `pae_interaction` is confidence, not affinity.

## Expression strategy
- Binders: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (40-80 aa) -> high yield expected.
- PD-L1 ectodomain (IgV) reagent: mammalian/insect expression or commercial; confirm it is active
  (binds PD-1) before testing binders.

## Assays (go/no-go -> basic -> functional)
1. Go/no-go: express -> SDS-PAGE -> SEC (monodisperse?).
2. Affinity: SPR or BLI vs immobilized PD-L1 -> K_D + kinetics (k_on/k_off). Test a dilution series.
3. Functional (the point): PD-1-COMPETITION assay -> does the binder displace PD-1 from PD-L1?
   (SPR competition, or a cell-based PD-1/PD-L1 blockade reporter assay.)
4. Stability: DSF (Tm). Deep (optional): co-crystal / cryo-EM of the binder-PD-L1 complex.

## Controls (MANDATORY)
- Positive: a known PD-L1 binder (anti-PD-L1 Fab/antibody, or PD-1 ectodomain) -> assay + reagent are active.
- Negative (scrambled-interface): YOUR OWN top design with its interface residues scrambled/mutated
  -> must LOSE binding (cleanest specificity control).
- Negative (unrelated): an unrelated mini-protein of similar size -> should not bind.

## Realistic expectations
In-silico binder hit rates vary widely; the MAJORITY of in-silico hits fail experimentally. Expect
to test many to find a few real binders. Report the experimental hit rate honestly. Do NOT imply a
working binder or fabricate a K_D.

## Timeline + costed reagents (fill in)
- Gene synthesis (14 binders + scrambled-interface negatives): $<...>, <...> weeks (IGSC-screened provider).
- PD-L1 reagent + SPR/BLI chips + anti-PD-L1 positive control: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Blocking binders to a human checkpoint protein for cancer immunotherapy/diagnostics (in scope).
Gene synthesis via a biosecurity-screening provider; wet lab under institutional biosafety/ethics approval.
