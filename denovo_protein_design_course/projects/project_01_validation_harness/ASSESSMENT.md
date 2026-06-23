# Project 01 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether any protein works.**
This is a tooling project: a meticulously calibrated harness that *honestly reports* an imperfect
AUC and maps its own failure modes earns an A. A harness that claims a single "best" cutoff with
no ROC curve, no N, and no failure analysis does not — no matter how clean it looks.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 01 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Metric definitions are correct *and* state what each does **not** mean (esp. pLDDT ≠ stability) |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | `predict()` runs all three tools, parses confidence robustly, seeds + versions logged |
| Dataset rigor (provenance, controls, logging) | 15% | D2 | ≥40 labeled designs + ≥10 refs, each with DOI/table/license; clean prediction table |
| Calibration, benchmarking & critical analysis | 20% | D3 | ROC/PR with AUC + CIs; composite vs single; AF2/ESMFold/Boltz agreement; explicit failure modes |
| Validation SOP (usefulness, evidence, feasibility) | 15% | D4 | Cutoffs by design type, each backed by AUC + N; clear cohort usage guide + required controls |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can actually rerun |
| Oral defense | 10% | D5 | Can defend metric choices and own the harness's limits |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; correct metric understanding | Clear but generic | Vague | Absent / metrics misunderstood |
| Tool selection & justification | Reasoned (why AF2 *and* ESMFold *and* Boltz) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; robust parsing; ablation; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest limits + failure forensics + AUC/CIs + where the predictor breaks | Some limitations noted | Superficial | None |
| Validation SOP | Calibrated, evidence-backed, with required controls + cost-aware guidance | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (ROC/PR/agreement), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page metric write-up + screenshot of one reproduced prediction with values.
- **D1 (Wk 6):** repo link; `predict(sequence, tool)` demo on ≥5 sequences; `LOG.md` started.
- **D2 (Wk 12):** `data/dataset.csv` (≥40 designs + ≥10 refs, full provenance) + `predictions.csv` + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: ROC/PR per metric (AUC), composite model, AF2/ESMFold/Boltz agreement, failure-mode table.
- **D4 (Wk 22):** `SOP.md` card (cutoffs by design type, evidence per row) + merged `filtering_pipeline.py` PR + cohort usage guide.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab and
reproduce the headline ROC figure from the tagged release, the reproducibility components are
capped at "Adequate" until fixed. State exact tool versions + seeds in the report.
