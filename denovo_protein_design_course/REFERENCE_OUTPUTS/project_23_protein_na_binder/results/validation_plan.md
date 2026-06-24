# Protein-NA Binder Validation Plan (Project 23 - by <your name>, <date>)

## Candidates
Top 11 confident-AND-specific candidates carried forward ({'ligandmpnn': 4, 'proteinmpnn': 7}); see results/top_candidates.csv.
Target nucleic acid: TGACGTCA (na_type from your design). EVERY in-silico number is a HYPOTHESIS until
measured - pae_interaction is confidence, specificity_score is a computational proxy, NEITHER is a K_D.

## Expression / reagents
- Protein binders: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (40-90 aa) -> high yield expected.
- Target nucleic acid: synthesize the TGACGTCA oligo (DNA: HPLC-purified duplex; RNA: in-vitro transcribed
  or synthesized, with a 5' fluorophore (FAM/Cy5) for anisotropy). Order a SCRAMBLED-NA oligo of the SAME
  length/base-composition as the specificity control.

## Assays (go/no-go -> binding -> specificity)
1. Go/no-go: express -> SDS-PAGE -> SEC (monodisperse? not aggregated?).
2. Binding: EMSA (gel-shift) titration of protein vs labeled target NA -> apparent affinity from the shift;
   AND/OR fluorescence anisotropy/polarization titration (labeled NA, protein dilution series) -> apparent K_D.
3. SPECIFICITY (the point): repeat the SAME titration against the SCRAMBLED-NA control. A specific binder
   shifts/binds the intended motif at much lower protein concentration than the scramble. Report the RATIO,
   not just the intended-motif number.
4. Stability: DSF (Tm) of the protein. Deep (optional): co-crystal / cryo-EM of the protein-NA complex;
   competition with a known motif-binding protein.

## Controls (MANDATORY)
- Negative (scrambled-NA): the SAME assay vs a scrambled motif (same composition) -> a specific binder
  should bind it MUCH more weakly. This is the cleanest specificity control and is REQUIRED.
- Negative (dead-mutant): YOUR OWN top design with its predicted NA-interface residues mutated (e.g. the
  base-reading residues -> Ala) -> must LOSE binding to the intended motif.
- Negative (unrelated protein): an unrelated protein of similar size/charge -> should not shift the NA.
- Positive: a known binder of TGACGTCA (the natural protein / a published designed binder, if available)
  to confirm the labeled NA reagent and the assay are working.

## Realistic expectations
Protein-NA design is NEWER and HARDER than protein-protein; SEQUENCE SPECIFICITY is the main failure mode
(designs grip the generic phosphate backbone, not the bases). Expect many in-silico hits to bind
non-specifically or not at all. Report the experimental hit rate AND the specificity ratio honestly.
Do NOT imply a working binder or fabricate a K_D.

## Timeline + costed reagents (fill in)
- Gene synthesis (11 binders + dead-mutant negatives): $<...>, <...> weeks (IGSC-screened provider).
- Labeled target NA + scrambled-NA control oligos (+ unlabeled for EMSA): $<...>.
- Anisotropy plate reader / EMSA gel time + a positive-control reagent: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Designed nucleic-acid-binding proteins for gene-editing modulation / RNA-targeting therapeutics /
synthetic transcription factors (therapeutic / basic-science; low dual-use). Default neutralizing/
therapeutic framing. Gene synthesis via a biosecurity-screening provider; wet lab under institutional
biosafety/ethics approval.
