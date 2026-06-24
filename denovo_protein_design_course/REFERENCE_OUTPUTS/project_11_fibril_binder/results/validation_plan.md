# Conformation-Specific Fibril-Binder Validation Plan (Project 11 — by <your name>, <date>)

## Candidates
Top 5 FIBRIL-SELECTIVE candidates carried forward ({'rfdiffusion': 5}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured — `pae_interaction` is confidence (not affinity),
and the `specificity_gap` is a model proxy (not a measured fold-selectivity). The monomer is
disordered, so its model is itself uncertain. The fibril-vs-monomer assay below is the real test.

## Target conformations (the whole point)
- ON-target: the AMYLOID FIBRIL (tau PHF from 5O3L/5O3T, or alpha-synuclein fibril from 6CU7/6H6B).
  Prepare recombinant fibrils in vitro (seeded aggregation); confirm fibrils by ThT fluorescence + TEM/cryo-EM.
- OFF-target (counter): the MONOMER of the SAME protein (freshly purified, kept monomeric; verify by SEC).
- OFF-target (cross-amyloid): the OTHER amyloid fibril (tau vs alpha-syn) for diagnostic discrimination.

## Expression strategy
- Binders: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (50-90 aa) -> high yield expected.
- Antigens: recombinant tau / alpha-synuclein; prepare BOTH a monomer prep AND an in-vitro fibril prep
  from the same construct (this matched pair is what makes the selectivity readout clean).

## Assays (go/no-go -> basic -> the selectivity test)
1. Go/no-go: express binder -> SDS-PAGE -> SEC (monodisperse?).
2. Binding: SPR or BLI vs immobilized FIBRIL -> apparent K_D + kinetics. Test a dilution series.
3. THE SELECTIVITY TEST (the point): fibril-vs-monomer ELISA/SPR -> signal on FIBRIL must be >> signal
   on MONOMER (report the selectivity RATIO measured here; do NOT report the in-silico gap as the result).
4. Cross-amyloid: same readout vs the OTHER amyloid fibril (must be low for a discriminating tracer).
5. (Diagnostic deep dive) tissue staining / fibril pulldown from patient-derived material under approval.

## Controls (MANDATORY)
- Positive: a known conformation-specific anti-fibril antibody/tracer (e.g., a conformational mAb or a
  validated amyloid PET-tracer scaffold) -> assay + fibril prep are active and conformation-discriminating.
- Negative (scrambled-interface): YOUR OWN top design with its fibril-contacting residues scrambled
  -> must LOSE fibril binding (cleanest specificity control).
- Negative (monomer): the MONOMER of the same protein -> a selective binder must NOT bind it.
- Negative (unrelated): an unrelated mini-protein / an unrelated amyloid -> should not bind.

## Diagnostic-tracer framing
The intended use is DIAGNOSTIC (a conformation-selective probe for PET imaging or a fibril-detection
assay) and/or an aggregation MODULATOR — recognizing pathological aggregates, not the physiological
monomer. This is a defensible, in-scope neurodegeneration application (low dual-use). A clinical PET
tracer additionally needs BBB penetration, radiolabeling chemistry, and pharmacokinetics — out of
scope for this capstone but named here as the translational path.

## Realistic expectations
Conformational selectivity is VERY hard: the binder must REJECT the abundant monomer. The MAJORITY of
in-silico "selective" designs will fail the monomer counter-test experimentally. Report the measured
selectivity ratio and the experimental hit rate honestly. Do NOT imply a working tracer or fabricate
a K_D / selectivity number.

## Timeline + costed reagents (fill in)
- Gene synthesis (5 binders + scrambled-interface negatives): $<...>, <...> weeks (IGSC-screened provider).
- Recombinant tau / alpha-syn (monomer + fibril preps) + ThT + TEM time + SPR/BLI chips + positive-control mAb: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Conformation-selective binders to pathological amyloid aggregates for neurodegeneration DIAGNOSTICS /
aggregation modulation (in scope; low dual-use). Gene synthesis via a biosecurity-screening provider;
any patient-derived material + wet lab under institutional biosafety/ethics approval.
