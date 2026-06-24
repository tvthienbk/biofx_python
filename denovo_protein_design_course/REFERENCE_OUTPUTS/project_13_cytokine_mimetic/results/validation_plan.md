# IL-2 Cytokine-Mimetic Validation Plan (Project 13 — by <your name>, <date>)

## Candidates
Top 9 SELECTIVE-AGONIST candidates carried forward ({'bindcraft': 1, 'rfdiffusion': 8}); see results/top_candidates.csv.
EVERY in-silico number is a HYPOTHESIS until measured. pae_interaction is confidence, not affinity;
SELECTIVE in silico is not an agonist — BINDING IS NOT SIGNALING. Do NOT fabricate an EC50/K_D.

## Expression strategy
- Mimetic: E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC. Small (50-90 aa), de novo ->
  high yield + high stability expected (the Neo-2/15 advantage).
- Receptor-subunit ectodomain reagents (IL-2Ra/CD25, IL-2Rb/CD122, gammaC/CD132): mammalian/insect
  expression or commercial; confirm each is active before testing.

## Assays (go/no-go -> selectivity -> signaling)
1. Go/no-go: express -> SDS-PAGE -> SEC (monodisperse?).
2. SELECTIVITY (per-subunit SPR/BLI): measure K_D + kinetics to IL-2Ra, IL-2Rb, AND gammaC SEPARATELY.
   Expect: binds IL-2Rb and gammaC; does NOT (or weakly) bind IL-2Ra -> confirms the βγ-bias in vitro.
3. SIGNALING (the decisive readout): cell-based STAT-phosphorylation (pSTAT5) assay on IL-2-responsive
   cells (e.g., CTLL-2 or primary T/NK). Dose-response -> EC50, Emax (full vs partial agonist?).
   Run on CD25+ vs CD25- cells to confirm alpha-INDEPENDENT signaling (the selectivity payoff:
   activates effector cells, spares CD25-high Tregs).
4. Stability: DSF (Tm) vs native IL-2 -> quantify the thermostability advantage.
   Deep (optional): co-crystal / cryo-EM of the mimetic-receptor complex; in-vivo Treg-vs-effector.

## Controls (MANDATORY)
- Positive: native IL-2 (and/or Neo-2/15) -> confirms SPR reagents + the pSTAT5 assay/cells respond.
- Negative (scrambled-interface): YOUR OWN top design with its beta/gammaC interface residues
  scrambled/mutated -> must LOSE binding AND signaling (cleanest specificity control).
- Negative (unrelated): an unrelated mini-protein of similar size -> should not bind or signal.

## Realistic expectations
De novo agonist design with clean subunit selectivity is HARD. In-silico hit rates vary widely; the
MAJORITY of in-silico hits fail experimentally, and even an experimental BINDER may fail to SIGNAL
(wrong dimerizing geometry). Report the experimental hit rate honestly. A selective binder that does
NOT trigger pSTAT5 is a negative result worth reporting.

## Timeline + costed reagents (fill in)
- Gene synthesis (9 mimetics + scrambled-interface negatives): $<...>, <...> weeks (IGSC-screened provider).
- Receptor-subunit reagents (a/b/gammaC) + SPR/BLI chips + native IL-2 positive control: $<...>.
- pSTAT5 assay (antibodies, IL-2-responsive cells, CD25+/- lines, flow time): $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
A receptor-selective agonist mimicking a human cytokine for cancer immunotherapy / immune modulation,
whose explicit goal is to REDUCE the toxicity of native IL-2 (βγ-biased -> spares CD25-high Tregs and
vascular-leak toxicity) -> in scope, LOW dual-use risk. Gene synthesis via a biosecurity-screening
provider; cell-based immune assays under institutional biosafety/ethics approval.
