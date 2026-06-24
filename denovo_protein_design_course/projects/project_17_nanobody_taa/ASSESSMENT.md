# Project 17 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the protein works.** De novo
nanobody hit rates are LOW: a meticulous campaign that *honestly reports* a low pass rate, bins designs
by epitope, checks receptor-family specificity, and proposes a sound display screen earns an A. A single
"good-looking" design with no controls, no specificity panel, and no hit-rate accounting does not — no
matter how clean it looks. Computational designs are **hypotheses / screening inputs**, never validated
binders.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 17 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | TAA + **epitope choice** (overlap vs not) justified with measurable success criteria; honest on low hit rates |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Mock pipeline runs end-to-end; real RFantibody/AF2-Multimer wired with pinned commits; seeds + versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | 500+ diverse VHHs; full design log (framework, epitope, params, seed, commit); diversity before filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | `design_type="antibody"` filter; survival/hit-rate; epitope-choice + receptor-family specificity + developability figures |
| Validation plan (controls, feasibility, cost) | 15% | D4 | Pooled display-screen plan + downstream format + specificity panel + the three mandatory controls + costed list |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun (mock path runs anywhere) |
| Oral defense | 10% | D5 | Can defend the epitope choice, own the low hit rate, and explain why the screen is essential |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | TAA + epitope choice specific, motivated, measurable | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned (RFantibody vs BoltzGen; AF2-Multimer + IgFold; real vs heuristic developability) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; antibody filter; specificity panel; reproducible; pinned commits | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest low hit rate + failure forensics + specificity margins + developability caveats | Some limitations noted | Superficial | None |
| Experimental plan | Detailed pooled display screen + downstream format + 3 controls, costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival/specificity/developability), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (TAA + epitope choice + measurable criteria + controls) +
  printout of the reproduced **mock** VHH hello-world (CDR3 length + SYNTHETIC metrics).
- **D1 (Wk 6):** repo link; full mock pipeline run + a tiny real RFantibody demo; `LOG.md` started with
  pinned commits.
- **D2 (Wk 12):** `results/campaign.csv` (500+ VHHs on a real run) + design log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer, epitope-choice comparison, receptor-family
  specificity panel, developability/humanness distributions; honest hit-rate table.
- **D4 (Wk 22):** `results/display_screen_plan.json` + downstream construct + `controls_and_specificity.json`
  + `experimental_plan.csv` (real quotes replacing EXAMPLE_DATA).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `05_validation_plan` on the **mock**
backend and reproduce the survival figure + the plan artifacts, the reproducibility components are
capped at "Adequate" until fixed. State exact tool versions/commits + seeds in the report; never present
mock/`EXAMPLE_DATA` numbers as real.
