# Project 21 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the enzyme works.** De novo
enzyme hit rates are low (often <5% active without directed evolution), and **catalytic-geometry
preservation does not guarantee activity**. A meticulous campaign that honestly reports a low hit rate,
a clean catalytic-geometry-preservation analysis, a sound scaffolding-method comparison, a
pocket-accessibility / substrate-scope analysis, and a rigorous pNP-ester kinetic-assay plan with the
**catalytic-Ser→Ala dead-mutant** control earns an A. A single nice-looking design with no controls, no
geometry accounting, and no hit-rate reporting does not.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 21 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Correct serine-hydrolase mechanism + triad/oxyanion-hole reasoning; measurable success criteria; honest hit-rate reality |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | theozyme→scaffold→LigandMPNN(triad fixed)→geometry runs end-to-end; seeds + tool versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | 1000s of backbones; triad + oxyanion-hole provably fixed; full design log (config+seed+path) |
| Filtering, benchmarking & critical analysis | 20% | D3 | enzyme-cutoff filter; catalytic-geometry preservation rate; scaffolding-method comparison; pocket-accessibility/substrate-scope; honest hit rate |
| Validation plan (controls, feasibility, cost) | 15% | D4 | pNP-ester kcat/KM assay + DSF; controls incl. catalytic-Ser→Ala dead mutant, natural reference, empty vector, blank; costed/timed |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; "geometry ≠ activity" stated plainly |
| Oral defense | 10% | D5 | Can defend the triad geometry, the method choice, and own the campaign's limits |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable; correct serine-hydrolase/triad understanding | Clear but generic | Vague | Absent / mechanism wrong |
| Tool selection & justification | Reasoned (why LigandMPNN fixes the triad + oxyanion hole; why RFdiffusion2 vs Riff-Diff) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; triad + oxyanion hole fixed; multi-layer filter; pocket/scope checks; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest hit rate + geometry-preservation rate + "geometry ≠ activity" + failure forensics | Some limitations noted | Superficial | None |
| Experimental plan | pNP-ester kinetics + DSF, catalytic-Ser→Ala + reference + empty-vector controls, costed, timed | Reasonable, gaps | Vague | Absent / no controls |
| Communication | Clear prose, professional figures (survival funnel, geometry distribution, method comparison, substrate-scope), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** 1-page problem statement (measurable criteria + controls) + printout of the reproduced
  theozyme hello-world (triad + oxyanion-hole spec + a mock scaffold record).
- **D1 (Wk 6):** repo link; minimal theozyme→scaffold→LigandMPNN(triad fixed)→geometry pipeline on a
  small batch with catalytic-geometry RMSD computed; `LOG.md` started.
- **D2 (Wk 12):** full design pool (scaffolds + sequences, triad + oxyanion hole fixed) + `design_log`
  (every config+seed+output) + 3–4 page interim report.
- **D3 (Wk 18):** `03`/`04` notebooks + figures: survival-at-each-layer, catalytic-geometry preservation
  rate, scaffolding-method comparison, pocket-accessibility + substrate-scope figures, ranked top
  candidates, honest hit-rate table.
- **D4 (Wk 22):** validation report (geometry + docking + MD + substrate scope on the <96 set) + pNP-ester
  kinetic-assay + DSF plan with controls (catalytic-Ser→Ala dead mutant, natural reference, empty
  vector, blank), costed + timed.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment (+ an
  enantioselectivity / kinetic-resolution plan for hits `[stretch]`).

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock
backend** and reproduce the survival-at-each-layer figure from the tagged release, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions + seeds in the report, and
clearly mark every synthetic/`EXAMPLE_DATA` number as such (no fabricated kcat/KM/ee).
