# Synthesis & Expression Plan (Project 03 — by <name>, <date>)

## Designs to synthesize (codon-optimized, gene synthesis via an IGSC-screening provider)
1. TEST    — one HIGH-novelty design (lowest TM, scRMSD<2): the risky case.
2. CONTROL+ — one CONSERVATIVE design (high TM ~>0.6, very low scRMSD, high pLDDT): expected to fold.
3. CONTROL- — an UNRELATED natural protein of similar size (e.g., a small natural monomer): orthogonal control.
   (The risky vs conservative PAIR directly tests the novelty budget.)

## Expression
- Host: E. coli BL21(DE3); T7 vector; His6 tag + TEV site; 16-18 C overnight induction.
- Note: switch to a refolding protocol or mammalian expression only if the novel design is insoluble.

## Characterization (go/no-go -> basic -> deep)
- go/no-go : express -> SDS-PAGE (right MW?) -> SEC (monodisperse monomer?).
- basic    : CD (secondary-structure content vs the DESIGNED topology), DSF (Tm / thermostability).
- deep     : crystallography or cryo-EM to CONFIRM the novel fold; SEC-MALS / SAXS for solution shape.

## Read-out tied to the hypothesis
- Does the HIGH-novelty design fold (SEC monomer + CD matching topology) as well as the conservative one?
- If the conservative folds and the novel does not, the novelty budget was exceeded for that topology/length.

## Controls, timeline, cost
- Controls: positive (conservative design), negative (unrelated protein); both run in parallel.
- Timeline: synthesis ~2-3 wk; expression/purification ~2 wk; characterization ~3-4 wk.
- Cost: gene synthesis (3 constructs) + expression reagents + SEC/CD/DSF time — itemize for your advisor.

## Responsible research
- Low dual-use: novel monomers with no designed function. Synthesis through an IGSC-screening provider;
  institutional biosafety/ethics approval before any wet-lab work. Re-evaluate under MASTER_BLUEPRINT §7
  if a fold is later repurposed toward a functional target.
