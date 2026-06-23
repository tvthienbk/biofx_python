# Project 04 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the cage assembles.**
Correct-symmetry assembly is hard and wrong-oligomer outcomes are common: a meticulously analysed
campaign with an honestly-reported low assembly success rate and sharp **wrong-oligomer forensics**
earns an A. A single nice-looking C3 design with no symmetry-RMSD check, no alternative-state
modelling, and no assembly-success accounting does not — no matter how good the cartoon looks. Any
example numbers from the mock backend are `EXAMPLE_DATA`; presenting them as real results fails the
honesty bar.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 04 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Symmetry concepts correct; states what subunit scRMSD / interface pAE / symmetry RMSD do **and do not** mean; oligomeric-state error understood |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | generate → tied-MPNN → AF2-Multimer runs end-to-end; tied positions correct; seeds + tool versions + RFdiffusion/ColabFold pins logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | C3/C4/D2 each at scale; tied design verified; `assemblies.csv` complete with config + seed per design |
| Filtering, benchmarking & critical analysis | 20% | D3 | `oligomer` filter applied; symmetry-order-vs-success + tied-vs-untied benchmark; honest assembly-success accounting (N pass / N generated) |
| Validation plan (controls, feasibility, cost) | 15% | D4 | nsEM + SEC-MALS + native-MS plan with the right controls; wrong-oligomer risk analysis; costed + timed |
| Final report & reproducible release | 10% | D5 | Thesis-quality assembly design report; `v1.0` tag others can rerun |
| Oral defense | 10% | D5 | Can defend symmetry/tool choices and own the wrong-oligomer risk |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable success criteria; correct symmetry-metric understanding | Clear but generic | Vague | Absent / metrics misunderstood |
| Tool selection & justification | Reasoned (why symmetric RFdiffusion + tied MPNN + AF2-Multimer; why these symmetries) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete C3/C4/D2 campaign, multi-layer `oligomer` filter, wrong-oligomer analysis, reproducible | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest limits + wrong-oligomer forensics + assembly-success accounting | Some limitations noted | Superficial | None |
| Experimental plan | nsEM/SEC-MALS/native-MS, controlled, costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival, symmetry-order, agreement), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (measurable success criteria + controls) + reproduced small-C3 output (mock, then a real run if compute allows) with its scores printed.
- **D1 (Wk 6):** repo link; generate → tied-MPNN → AF2-Multimer demo on a tiny C3 batch; `LOG.md` started.
- **D2 (Wk 12):** `results/assemblies.csv` (C3/C4/D2, 100s of designs, tied MPNN, full config/seed provenance) + design log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: `oligomer`-filter survival, symmetry-order-vs-success, tied-vs-untied comparison, ranked top assemblies, assembly-success-rate table.
- **D4 (Wk 22):** validation report + nsEM/SEC-MALS/native-MS plan (controls: positive = a known nanocage / natural homo-oligomer; negative = scrambled-interface or monomeric variant; unrelated control) + wrong-oligomer risk analysis.
- **D5 (Wk 24):** thesis chapter + assembly design report + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab (on
the mock backend at minimum) and reproduce the headline survival figure from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions, the
RFdiffusion/ColabFold commit pins, and seeds in the report.
