# NDM-1 Inhibitor (Binder) Validation Plan (Project 10 — by <your name>, <date>)

## Purpose (defensive anti-AMR)
INHIBIT NDM-1 (a carbapenem-hydrolyzing metallo-beta-lactamase) to RESTORE last-resort antibiotic
efficacy. Out of scope: enhancing resistance / pathogen fitness / stabilizing the enzyme.

## Candidates
Top 9 candidates carried forward ({'rfdiffusion': 9}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured. pae_interaction is confidence, occlusion is a
structural proxy -> BINDING != INHIBITION. There is NO in-silico IC50.

## Expression strategy
- Binders: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (40-80 aa) -> high yield expected.
- NDM-1: express the soluble construct; purify WITH Zn2+ in the buffer to keep the DI-ZINC site intact;
  confirm activity on nitrocefin BEFORE testing binders.

## Assays (go/no-go -> INHIBITION kinetics -> functional)
1. Go/no-go: express -> SDS-PAGE -> SEC (monodisperse binder?).
2. INHIBITION kinetics (the point): pre-incubate NDM-1 with a binder DILUTION SERIES, then add
   substrate and measure residual hydrolysis RATE:
     - nitrocefin (chromogenic cephalosporin; absorbance shift on hydrolysis), or
     - a carbapenem (imipenem/meropenem) hydrolysis readout (UV absorbance drop).
   Fit IC50 (and ideally K_i + mode: competitive / non-competitive / uncompetitive).
3. Stability: DSF (Tm). Deep (optional): co-crystal / cryo-EM of the binder-NDM-1 complex over the di-zinc site.

## Controls (MANDATORY)
- OFF-TARGET human-metalloenzyme control: run the SAME inhibition assay against a human Zn/metalloenzyme
  (e.g. carbonic anhydrase) -> the binder must NOT inhibit it (specificity / safety; mirrors nb-04 specificity).
- Negative (scrambled-interface): YOUR OWN top design with its interface residues scrambled/mutated
  -> must LOSE inhibition (cleanest specificity control).
- Enzyme-only / no-inhibitor positive: NDM-1 + substrate, no binder = 100% activity baseline; a known
  metallo-beta-lactamase chelator/inhibitor probe (e.g. EDTA / a captopril analogue) confirms the assay.

## (Stretch) beta-lactam ADJUVANT readout (the therapeutic point)
Checkerboard of binder x carbapenem (e.g. meropenem) in a resistant strain: does the binder RESTORE
the antibiotic's MIC (synergy / FIC index)? This is the defensive-anti-AMR proof-of-concept: the
binder makes a last-resort antibiotic work again.

## Realistic expectations
In-silico binder hit rates vary widely; the MAJORITY of in-silico hits fail experimentally, and
BINDING != INHIBITION. Expect to test many to find a few real inhibitors. Report the experimental hit
rate (and IC50s) honestly. Do NOT imply a working inhibitor or fabricate an IC50/K_i.

## Timeline + costed reagents (fill in)
- Gene synthesis (9 binders + scrambled-interface negatives): $<...>, <...> weeks (IGSC-screened provider).
- NDM-1 + human off-target enzyme + nitrocefin/carbapenem substrate + plate reader time: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Defensive anti-AMR: inhibit NDM-1 to restore carbapenem efficacy (in scope, MASTER_BLUEPRINT §7).
Out of scope: enhancing resistance / pathogen fitness. Gene synthesis via a biosecurity-screening
provider; wet lab under institutional biosafety/ethics approval.
