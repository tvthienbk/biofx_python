# Project 14 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the nanobody works.** A
controlled campaign with an honest (even ~0%) hit rate, a careful breadth + developability analysis,
and a defensible epitope choice earns an A. A single good-looking design with no controls, no breadth
profile, and no hit-rate accounting does not.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 14 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Conserved-epitope + framework choice justified; defensive framing explicit |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | RFantibody runs; AF2-Multimer pae + CDR geometry parsed; seeds + versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | 500+ designs; complete design log; survivors framed as screening inputs |
| Filtering, breadth & critical analysis | 20% | D3 | Survival accounting + developability gate + cross-strain breadth (worst-case) + failure modes |
| Validation plan (controls, feasibility, biosafety, cost) | 15% | D4 | Yeast-display + neutralization/breadth plan; controls; **IBC oversight named**; costed |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` others can rerun |
| Oral defense | 10% | D5 | Can defend the epitope, the breadth result, and the responsible-research framing |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Conserved epitope justified + measurable breadth criteria + defensive framing | Clear but generic | Vague | Absent / unsafe framing |
| Tool selection & justification | Reasoned (RFantibody, AF2-Multimer, developability) | Correct, thin | No rationale | Wrong tools |
| Computational execution | Complete; 500+; breadth panel; developability; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest (low) hit rate + breadth + developability + failure forensics | Some limits noted | Superficial | None |
| Validation plan | Display screen + neutralization, controlled, costed, biosafe (IBC) | Reasonable, gaps | Vague | Absent / unsafe |
| Communication | Clear prose, professional figures (breadth/developability), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** epitope + framework choice + ≤2-page problem statement + reproduced mini-run.
- **D1 (Wk 6):** repo; VHH pipeline demo on ≥10 designs; `LOG.md` started.
- **D2 (Wk 12):** `results/` VHH pool (500+) + design log + 3–4 page interim report.
- **D3 (Wk 18):** ranked CSV + survival figure + developability + cross-strain breadth + filtering report.
- **D4 (Wk 22):** yeast-display screen plan + neutralization/breadth plan (controls, IBC, cost).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release.

## Reproducibility gate (pass/fail overlay)
If a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab (mock backend) and reproduce the
headline survival figure from the tagged release, the reproducibility components are capped at
"Adequate" until fixed. State exact tool versions + seeds.
