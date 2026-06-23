# Project 15 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the protein works.**
Computational maturation **ranks** candidates; it does not measure affinity, and **most predicted
affinity-improving mutations do not validate.** A meticulous campaign that proposes a SMALL, ranked,
pose-maintained, developable mutation set and an honest SPR/DSF plan with controls earns an A — even if
the report's expectation is that few will validate. A single "great-looking" mutation with a fabricated
or implied KD, no pose check, and no controls does not — no matter how clean it looks. Computational
candidates are **hypotheses to test**, never validated higher-affinity binders. **Never fabricate
KD/ΔΔG numbers; rank only.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 15 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Chosen SAbDab complex + its **measured KD** (value + citation) + CDR contacts + measurable success criteria; honest that most improvers won't validate |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Mock pipeline runs end-to-end; real ESM-1v/AbLang/ProteinMPNN/AF2-Multimer wired with pinned commits; seeds + versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Exhaustive single-mutation scan + CDR redesigns (framework FIXED); full design log; diversity in scoring before filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | `design_type="antibody"` filter; pose maintenance; survival/hit-rate; ESM-1v/AbLang/MPNN agreement + developability + epistasis figures |
| Validation plan (controls, feasibility, cost) | 15% | D4 | SPR-kinetics + DSF plan vs the measured KD + the three mandatory controls (WT + destabilizing decoy + specificity panel) + costed list |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun (mock path runs anywhere) |
| Oral defense | 10% | D5 | Can defend the mutation ranking, own that most won't validate, and explain why the SPR/DSF controls are essential |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Complex + measured KD + CDR contacts specific, motivated, measurable | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned (ESM-1v vs AbLang vs ProteinMPNN; AF2-Multimer pose check; real vs heuristic developability) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; antibody filter; pose maintenance; reproducible; pinned commits | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest "most won't validate" + failure forensics + pose/developability caveats + no fabricated KD | Some limitations noted | Superficial | None / fabricated affinities |
| Experimental plan | Detailed SPR-kinetics + DSF + 3 controls (WT + decoy + specificity), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival/pose/developability), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (chosen complex + **measured KD** with citation + CDR contact
  residues + measurable criteria + controls) + printout of the reproduced **mock** hello-world (top-
  ranked single mutations + SYNTHETIC pose/liability metrics).
- **D1 (Wk 6):** repo link; full mock pipeline run + a tiny real ESM-1v/AbLang/MPNN demo + one AF2-
  Multimer pose check; `LOG.md` started with pinned commits.
- **D2 (Wk 12):** `results/campaign.csv` (single mutations + CDR redesigns, with ranking scores) +
  design log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer, pose-maintenance (pae vs scRMSD),
  ESM-1v/AbLang/MPNN agreement, developability liabilities, epistasis/combos; honest hit-rate table.
- **D4 (Wk 22):** `results/spr_dsf_plan.json` + `results/dsf_and_specificity.json` +
  `results/controls.json` + `experimental_plan.csv` (real quotes replacing EXAMPLE_DATA).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `05_validation_plan` on the **mock**
backend and reproduce the survival figure + the plan artifacts, the reproducibility components are
capped at "Adequate" until fixed. State exact tool versions/commits + seeds in the report; never present
mock/`EXAMPLE_DATA` ranking numbers as real affinities, and never assert a KD/ΔΔG you did not measure.
