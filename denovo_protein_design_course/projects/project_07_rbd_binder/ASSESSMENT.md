# Project 07 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the binder works.** A
controlled campaign with an honest (even low) hit rate, a careful breadth analysis, and a defensible
epitope choice earns an A. A single good-looking design with no controls, no breadth profile, and no
hit-rate accounting does not.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 07 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Conserved-epitope choice is justified (conservation data) with a clear defensive framing |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Both paradigms run; AF2-Multimer pae parsed robustly; seeds + versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Hundreds of designs across both paradigms; complete design log |
| Filtering, breadth & critical analysis | 20% | D3 | Survival accounting + cross-variant breadth (worst-case) + honest failure modes |
| Validation plan (controls, feasibility, biosafety, cost) | 15% | D4 | ACE2-competition + pseudovirus breadth plan; controls; **IBC oversight named**; costed |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` others can rerun |
| Oral defense | 10% | D5 | Can defend the epitope choice, the breadth result, and the responsible-research framing |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Conserved epitope justified + measurable breadth criteria + defensive framing | Clear but generic | Vague | Absent / unsafe framing |
| Tool selection & justification | Reasoned (why BindCraft *and* RFdiffusion) | Correct, thin | No rationale | Wrong tools |
| Computational execution | Complete; both paradigms; breadth panel; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest hit rate + breadth + failure forensics | Some limits noted | Superficial | None |
| Validation plan | Controlled, costed, biosafe (IBC), breadth-testing | Reasonable, gaps | Vague | Absent / unsafe |
| Communication | Clear prose, professional figures (breadth/ROC), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** conserved-epitope map + ≤2-page problem statement + reproduced mini-run.
- **D1 (Wk 6):** repo; binder pipeline demo on ≥10 designs; `LOG.md` started.
- **D2 (Wk 12):** `results/` design pool (both paradigms) + design log + 3–4 page interim report.
- **D3 (Wk 18):** ranked CSV + survival figure + cross-variant breadth table/figure + filtering report.
- **D4 (Wk 22):** validation + breadth-testing plan (ACE2-competition, pseudovirus, controls, IBC, cost).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release.

## Reproducibility gate (pass/fail overlay)
If a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab (mock backend) and reproduce the
headline survival figure from the tagged release, the reproducibility components are capped at
"Adequate" until fixed. State exact tool versions + seeds.
