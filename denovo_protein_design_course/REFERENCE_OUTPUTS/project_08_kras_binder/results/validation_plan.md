# KRAS Binder Validation Plan (Project 08 — by <your name>, <date>)

## Candidates
Top 8 candidates carried forward ({'bindcraft': 1, 'rfdiffusion': 7}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured — `pae_interaction` is confidence (not affinity),
and the in-silico selectivity gap is NOT measured selectivity. No K_D is reported here.

## Expression strategy
- Binders: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (50-90 aa) -> high yield expected.
- KRAS reagent: express the G-domain (res ~1-169); NUCLEOTIDE-LOAD it deliberately -> prepare BOTH
  GDP-loaded and GppNHp/GMPPCP-loaded KRAS (keep Mg2+). Confirm each is folded/active before testing binders.
- For the isoform panel: express/obtain HRAS and NRAS G-domains under the SAME conditions.

## Assays (go/no-go -> basic -> selectivity/functional)
1. Go/no-go: express -> SDS-PAGE -> SEC (monodisperse?).
2. Affinity: SPR or BLI vs immobilized KRAS -> K_D + kinetics (k_on/k_off). Test a dilution series.
3. ISOFORM-SPECIFICITY PANEL (the centerpiece): run the SAME binder vs KRAS, HRAS, and NRAS under
   identical conditions -> quantify selectivity. A pan-RAS binder is a weaker result; report it.
4. NUCLEOTIDE-STATE TEST [stretch]: compare binding to GDP-loaded vs GppNHp-loaded KRAS -> a
   state-specific binder should discriminate.
5. Functional (extension): effector competition -> does the binder block RAF-RBD binding to KRAS-GTP?
6. Stability: DSF (Tm). Deep (optional): co-crystal / cryo-EM; cell-based KRAS-pathway readout.

## Controls (MANDATORY)
- Positive: a known KRAS binder (published DARPin/monobody/binder, or a G12C-inhibitor complex as a
  state reference) -> assay + KRAS reagent are active.
- Negative (scrambled-interface): YOUR OWN top design with its interface residues scrambled/mutated
  -> must LOSE binding (cleanest specificity control).
- Negative (unrelated): an unrelated mini-protein of similar size -> should not bind.
- Isoform off-targets (HRAS/NRAS) double as the selectivity readout AND a specificity control.

## Realistic expectations
KRAS is a hard target; SELECTIVITY (isoform + allele) is harder still. In-silico hit rates vary widely
and the MAJORITY of in-silico hits fail experimentally. Expect to test many to find a few real, and
fewer still selective, binders. Report the experimental hit rate AND the measured selectivity honestly.
Do NOT imply a working/selective binder or fabricate a K_D.

## Timeline + costed reagents (fill in)
- Gene synthesis (8 binders + scrambled-interface negatives): $<...>, <...> weeks (IGSC-screened provider).
- KRAS/HRAS/NRAS reagents + nucleotide loading (GDP, GppNHp) + SPR/BLI chips + positive control: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Inhibitory/blocking binders to KRAS, a human oncotarget, for cancer therapeutics/diagnostics (in scope).
Gene synthesis via a biosecurity-screening provider; wet lab under institutional biosafety/ethics approval.
