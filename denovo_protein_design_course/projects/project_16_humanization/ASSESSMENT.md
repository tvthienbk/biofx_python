# Project 16 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the protein works.**
Humanization is a **trade-off**: a meticulous campaign that *honestly quantifies* the humanness↔stability
cost, identifies the Vernier back-mutations, compares grafting vs resurfacing, and proposes a sound
ELISA/SPR/DSF validation with controls earns an A. A single "maximally human" variant with no ΔΔG
analysis, no controls, and no retained-binding plan does not — no matter how high the humanness score.
Computational variants are **hypotheses**, and a humanness score is **not** a proven low-ADA outcome.
**NEVER fabricate a ΔΔG or humanness number.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 16 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Antibody + **germline framework** choice + humanization **strategy** justified with measurable success criteria; honest on the trade-off |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Mock pipeline runs end-to-end; real humanness (OASis/Hu-mAb/AbLang) + ΔΔG (FoldX/Rosetta) wired with pinned commits; seeds + versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Several candidate frameworks; grafts + back-mutated + resurfaced + **parental & over-humanized-decoy controls**; full design log |
| Filtering, benchmarking & critical analysis | 20% | D3 | `design_type="antibody"` filter + humanness floor; survival/hit-rate; **humanness↔ΔΔG trade-off**, Vernier ladder, grafting-vs-resurfacing figures |
| Validation plan (controls, feasibility, cost) | 15% | D4 | ELISA/SPR/DSF plan (retained binding + Tm) + immunogenicity-risk summary + the mandatory controls + costed list |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun (mock path runs anywhere) |
| Oral defense | 10% | D5 | Can defend the germline choice, own the stability cost, and explain why over-humanization is the risk |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Antibody + germline + strategy specific, motivated, measurable | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned (OASis/Hu-mAb vs T20 vs AbLang; FoldX vs Rosetta; grafting vs resurfacing) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; antibody filter; trade-off curve + back-mutation ladder; reproducible; pinned commits | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest trade-off + failure forensics + humanness≠low-ADA caveat + ΔΔG-proxy caveats | Some limitations noted | Superficial | None |
| Experimental plan | Detailed ELISA/SPR/DSF + immunogenicity-risk + parental & over-humanized-decoy controls, costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (trade-off / ladder / grafting-vs-resurfacing), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (antibody + germline framework + strategy + measurable criteria
  + controls) + printout of the reproduced **mock** humanization hello-world (graft + Vernier
  back-mutations + SYNTHETIC humanness/ΔΔG).
- **D1 (Wk 6):** repo link; full mock pipeline run + a real humanness score on the parental + one graft;
  `LOG.md` started with pinned commits/hosts.
- **D2 (Wk 12):** `results/campaign.csv` (grafts + back-mutated + resurfaced + parental + over-humanized
  decoy, real humanness + ΔΔG) + design log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer, **humanness↔ΔΔG trade-off**, Vernier
  back-mutation ladder, grafting-vs-resurfacing; `immunogenicity_risk_summary.csv`; honest hit-rate table.
- **D4 (Wk 22):** `results/validation_plan.json` (ELISA/SPR/DSF) + `controls.json` (parental +
  over-humanized decoy) + `immunogenicity_risk_plan.json` + `experimental_plan.csv` (real quotes replacing
  EXAMPLE_DATA).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `05_validation_plan` on the **mock**
backend and reproduce the survival figure + the trade-off figure + the plan artifacts, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions/commits/hosts + seeds in the
report; never present mock/`EXAMPLE_DATA` numbers as real, and never report the humanness/ΔΔG heuristics as
validated-tool results.
