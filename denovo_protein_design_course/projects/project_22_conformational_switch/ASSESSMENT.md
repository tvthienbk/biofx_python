# Project 22 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the switch works.**
Multi-state design is VERY hard: one sequence folding to two defined states and toggling between them
is rare, and AF2 may only ever show you one of the two states. A campaign that honestly reports
*"5% of designs passed both states, of those the energy gap was switchable for only one, and AF2
could not confirm state B"* — with sharp failure analysis — earns an A. A single cherry-picked
"switch" picture with no per-state hit rate, no benchmark, and no energy-gap caveat does not, no
matter how pretty it looks. **Report the hit rate, not the cherry.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 22 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Two states + an explicit, physically plausible trigger + *measurable* success criteria; correct grasp of per-state scRMSD and the energy gap, and what each does **not** mean |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | RFdiffusion ×2 → multi-state MPNN → AF2-both-states runs end-to-end; seeds + pinned versions logged; mock backend reproduces anywhere |
| Campaign rigor (diversity, provenance, controls, logging) | 15% | D2 | Two distinct backbones + a real shared-sequence pool with **per-state** scores; clean `multistate_designs.csv`; design log; accessions verified |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter applied to **BOTH** states; single- vs multi-state benchmark; energy-gap distribution; honest N(A)/N(B)/N(BOTH)/N(switchable) ladder + the energy-gap caveat |
| Validation plan (usefulness, evidence, feasibility) | 15% | D4 | A state-change read-out (FRET/protease/SAXS) that actually proves a switch, with paired controls (positive, single-state "locked" negative, unrelated) + costed reagents |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; the multi-state design + its two-state validation + the read-out plan |
| Oral defense | 10% | D5 | Can defend the two-state definition, own the multi-state-designability and energy-gap limits, and explain why AF2 may not see both states |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Two states + trigger specific, motivated, measurable; correct metric understanding (gap ≠ ΔΔG) | Clear but generic | Vague / one state under-specified | Absent / metrics misunderstood |
| Tool selection & justification | Reasoned (why two backbones, why *tied* MPNN, why predict *both* states) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; both states generated; multi-state MPNN; AF2-both; reproducible | Complete, basic | Incomplete (e.g. only one state) | Non-working |
| Critical analysis | Per-state hit rates + benchmark + energy-gap distribution + the "AF2 may not see both states" caveat | Some limitations noted | Superficial | None / overclaims a working switch |
| Validation plan | State-change read-out with paired controls + cost-aware, feasible protocol | Reasonable, gaps | Vague | Absent / no controls |
| Communication | Clear prose, professional figures (both states, gap distribution, survival), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** problem statement (two states + trigger + measurable criteria + controls) in
  `data/inputs/two_state_def.txt` + screenshot/printout of the reproduced hello-world (one sequence →
  two per-state predictions + energy gap).
- **D1 (Wk 6):** repo link; working minimal pipeline (two states → multi-state MPNN → per-state
  prediction → energy gap) on ≥1 real design; first small batch; `LOG.md` started.
- **D2 (Wk 12):** two state backbones + `results/multistate_designs.csv` (one row per design:
  per-state scrmsd, per-state pLDDT, energy gap, per-state MPNN scores, seed) + design log + 3–4 page
  interim report.
- **D3 (Wk 18):** notebook + figures: per-state filter survival for **BOTH** states, AF2-both-states,
  energy-gap distribution, single- vs multi-state benchmark, and the N(A)/N(B)/N(BOTH)/N(switchable) ladder.
- **D4 (Wk 22):** validation report + costed, controlled state-change read-out plan (FRET/protease/SAXS)
  + the selected multi-state design (D★); optional LOV light-switch extension.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment, including
  the multi-state design + its two-state validation + the read-out plan.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab (mock
backend at minimum) and reproduce the headline survival/energy-gap figure from the tagged release,
the reproducibility components are capped at "Adequate" until fixed. State exact tool versions + seeds
in the report, and label every synthetic number `EXAMPLE_DATA`.
