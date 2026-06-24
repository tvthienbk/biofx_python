# Project 03 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether any protein works.**
This is a generative-design project: a meticulously mapped novelty-vs-foldability **frontier** that
*honestly reports* per-topology/length pass rates (including the cells where almost nothing folds)
earns an A. A single cherry-picked novel design with scRMSD = 1.1 Å, no frontier, and no hit-rate
accounting does not — no matter how striking the picture. **Diversity before filtering; report the
rate, not the cherry.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 03 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Measurable novelty/foldability criteria; states what scRMSD and TM-score do **and do not** mean (novelty ≠ pass/fail) |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | generate→MPNN→AF2/ESMFold→Foldseek runs end-to-end; seeds + tool versions logged; mock path reproducible anywhere |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Hundreds of backbones across the full length×topology grid; every config + seed logged; `results/backbones.csv` clean |
| Filtering, benchmarking & critical analysis | 20% | D3 | Frontier figure + per-topology/length success rates; foldability gated, novelty reported; FrameFlow/Genie2 comparison scaffolded honestly (no fabricated numbers) |
| Validation plan (controls, feasibility, cost) | 15% | D4 | Novelty budget + paired risky-vs-conservative controls + unrelated control; costed, timed synthesis/expression plan |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun |
| Oral defense | 10% | D5 | Can defend why novelty is a coordinate not a filter, and own the frontier's failure cells |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable; correct scRMSD/novelty understanding | Clear but generic | Vague | Absent / metrics misunderstood |
| Tool selection & justification | Reasoned (why RFdiffusion, why MPNN best-of-8, why Foldseek + TM-align) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Full grid, robust scRMSD, novelty checks, reproducible; honest A100 compute notes | Complete, basic | Incomplete | Non-working |
| Critical analysis | Per-cell hit rates + failure forensics (where/why folding collapses) + the frontier | Some limitations noted | Superficial | None |
| Experimental plan | Paired risky/conservative + unrelated controls, costed, timed; novelty budget justified | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional frontier/survival figures (metric, cutoff, N captioned), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤1-page problem statement (measurable novelty/foldability criteria + controls) + screenshot of the reproduced 10-backbone tutorial with scRMSD/novelty printed.
- **D1 (Wk 6):** repo link; pipeline demo generating→MPNN→folding→novelty on a small batch; `LOG.md` started; compute-budget note (T4 slice vs A100 full).
- **D2 (Wk 12):** `results/backbones.csv` (hundreds of backbones, full length×topology grid, with provenance/seed) + design log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: novelty-vs-scRMSD frontier, per-topology/length success-rate tables, survival-at-each-layer, FrameFlow/Genie2 comparison scaffold, failure-mode breakdown.
- **D4 (Wk 22):** validation report + `synthesis_plan` (selected novel-but-foldable set, paired controls, costed/timed) + the **novelty budget** guideline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `04_validate` on Colab (mock backend
for the plumbing; real backends where a GPU is available) and reproduce the headline frontier figure
from the tagged release, the reproducibility components are capped at "Adequate" until fixed. State
exact tool versions + seeds in the report; label any synthetic teaching data `EXAMPLE_DATA`.
