# Assembly Validation Plan (Project 04 — <your name>, <date>)

Goal: determine the ACTUAL oligomeric state of the ranked C3/C4/D2 candidates.
In-silico interface pAE is necessary, not sufficient — these assays confirm the real state.

## Expression & purification
- Host: E. coli BL21(DE3), 16-18 C overnight (mammalian only if a glycosylated antigen is grafted).
- Purify by IMAC -> SEC; carry the SEC trace into characterization.

## Oligomeric-state determination (the core)
| Assay | What it tells you | Go/No-go |
|-------|-------------------|----------|
| SEC | apparent size / homogeneity | single symmetric peak at expected volume |
| SEC-MALS | ABSOLUTE molar mass -> oligomeric number | mass = n_subunits x monomer mass |
| negative-stain EM (nsEM) | assembly architecture / particle shape | particles match target point group |
| native-MS | stoichiometry (intact assembly mass) | dominant species = intended order |
| (if warranted) cryo-EM | high-res structure of the assembly | matches the design |

## Controls (mandatory)
- Positive: a known nanocage / a VERIFIED natural homo-oligomer of the target symmetry.
- Negative: a scrambled-interface OR monomeric variant of the SAME design -> must NOT assemble.
- Unrelated-protein control.

## Honest reporting
- Report the assembly-success rate (N forming the intended state / N expressed), per symmetry.
- Wrong-oligomer outcomes are common; report them. NEVER claim a cage "will assemble."

## Timeline & cost (fill in)
- Weeks, reagents, instrument time (SEC-MALS / EM grid prep / native-MS) — cost it out.
