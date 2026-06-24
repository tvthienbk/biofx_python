# MDM2 Peptide / Macrocycle Validation Plan (Project 09 — by <your name>, <date>)

## Candidates
Top 3 candidates carried forward ({'linear': 1, 'macrocycle': 1, 'miniprotein': 1}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured. `pae_interaction` is confidence, not affinity;
the Boltz-2 affinity score is a RELATIVE RANK, not a K_D. Predicted affinity for short peptides is unreliable.

## Synthesis strategy (peptides are NOT made in E. coli)
- Linear peptides: solid-phase peptide synthesis (SPPS, Fmoc); HPLC purify; confirm by mass spec.
- Macrocycles: SPPS + cyclization (head-to-tail lactam / side-chain / disulfide, or a hydrocarbon staple).
  D-amino acids / N-methylation introduced here (raises synthesis complexity — see the stretch below).

## Assays (binding -> stability -> permeability -> function)
1. Binding: SPR/BLI vs immobilized MDM2, OR a fluorescence-polarization DISPLACEMENT assay of a labeled
   p53 peptide (does the design displace p53 from MDM2?). Test a dilution series.
2. Protease stability (the key reason to cyclize): serum / trypsin / chymotrypsin half-life, linear vs cyclic.
3. Permeability (the key reason a macrocycle could be oral/cell-penetrant): PAMPA and/or Caco-2.
4. Function (the point): cell-based p53-pathway reactivation (e.g. p53-reporter / p21 induction) in MDM2-amplified cells.

## Controls (MANDATORY)
- Positive: a KNOWN p53-mimetic / stapled peptide (e.g. the ATSP-7041 lineage) -> assay + MDM2 reagent are active.
- Negative (scrambled-sequence): YOUR OWN top design with its sequence scrambled -> must LOSE binding (cleanest specificity control).
- Negative (unrelated): an unrelated peptide of similar length -> should not bind MDM2.

## Realistic expectations
De novo peptide/macrocycle hit rates are MODEST and chemistry-dependent; predicted affinity is
UNRELIABLE for short peptides. Expect to synthesize many to find a few real, stable, permeable binders.
Report the experimental hit rate honestly. Do NOT imply a working peptide or fabricate a K_D.

## Timeline + costed reagents (fill in)
- SPPS synthesis (3 peptides + scrambled-sequence negatives; macrocyclization adds steps): ${'<...>'}, <...> weeks.
- MDM2 reagent + labeled p53 peptide (FP) or SPR/BLI chips + positive-control peptide: $<...>.
- Protease-stability + PAMPA/Caco-2 assays: $<...>.
- Personnel / instrument time: <...> weeks.

## Responsible research
Competitive p53-mimetic peptides to a human oncology PPI (MDM2) to restore p53 function (in scope).
Synthesis via a biosecurity-screening provider; wet lab under institutional biosafety/ethics approval.
