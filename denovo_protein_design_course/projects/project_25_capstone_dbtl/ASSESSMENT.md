# Project 25 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the protein works, and not
on whether your ML model is a perfect classifier.** A capstone with a meticulously reported **low**
campaign hit rate, an honest **CV-AUC with N** for the success predictor (even if it only modestly
beats — or honestly *fails* to beat — single-metric cutoffs), sharp **failure forensics**, and a
controlled validation plan earns an A. A "great-looking" single design with no hit-rate accounting, no
controls, a cherry-picked metric, or an ML model bragging a single-split accuracy on tiny N does not.
**A design is a hypothesis; CV-AUC + N is the honest headline; no experimental label is fabricated.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 25 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | The in-silico-vs-experimental gap framed clearly; **target justified + advisor §7 approval recorded**; measurable success criteria + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Campaign + ML pipeline run end-to-end (mock path reproduces anywhere); seeds + tool versions + commits logged; honest A100-vs-T4 scoping |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Campaign at honest scale; cohort feature table assembled with provenance; every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (classical baseline) + **trained success predictor**: CV-AUC (mean ± std) + N, **feature importance**, **enrichment vs single-metric cutoffs**, cross-target generalization; honest verdict |
| Validation plan (controls, feasibility, cost) | 15% | D4 | Right assay for the design_type; positive + scrambled-interface/dead-mutant + unrelated controls; integrated real labels (no fabrication); honest hit-rate + failure forensics; costed + timed |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock path; **D★ predictor PR'd into `shared/`** |
| Oral defense | 10% | D5 | Can defend the target choice, the predictor's CV-AUC/N limits, and "this is a hypothesis until measured" |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; the in-silico→experimental gap framed; target justified + §7 approved | Clear but generic | Vague | Absent / target not approved |
| Tool selection & justification | Reasoned campaign-tool choice + why LogReg/RF/XGBoost for the predictor | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Campaign at scale + cross-validated predictor; multi-layer filter; reproducible; honest compute scoping | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest hit rates + CV-AUC/N + feature importance + enrichment verdict + failure forensics | Some limitations noted | Superficial | None |
| Experimental plan | Right assay, controlled (incl. scrambled/dead-mutant), costed, timed; active-learning loop | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnel, feature importance, enrichment), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria + controls) + **advisor-approved target**
  (responsible-research justification) + screenshot of the reproduced mock mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (target → a few designs → metrics); `LOG.md` started;
  version-verify output captured.
- **D2 (Wk 12):** `results/campaign_designs.csv` + cohort feature table
  (`results/cohort_table.csv` / `data/cohort_design_outcomes.csv`, provenance) + design log + interim report.
- **D3 (Wk 18):** notebook + figures: classical-filter survival funnel; **success predictor** CV-AUC
  (mean ± std) + N, feature-importance figure, enrichment-vs-cutoffs table + figure, cross-target
  generalization; honest verdict.
- **D4 (Wk 22):** validation report + costed, controlled experimental plan (right assay; positive +
  scrambled-interface/dead-mutant + unrelated); integrated real labels (or the wiring + caveat); honest
  hit-rate + failure-forensics table; active-learning next-batch ranking.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release + the **D★ success-predictor module**
  PR'd into `shared/` + cohort-wide lessons-learned synthesis.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `04_validate` on the **mock /
EXAMPLE_DATA** path and reproduce the survival funnel + the enrichment-vs-cutoffs table from the tagged
release, the reproducibility components are capped at "Adequate" until fixed. State exact tool versions,
pinned commits, and seeds in the report. **All synthetic numbers are `EXAMPLE_DATA` and must never
appear in the report as real results; no experimental label is fabricated.**
