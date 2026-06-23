# Project 11 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the binder works.** A
campaign with a meticulously reported **low** fibril hit rate and an even **lower** conformational-
selective rate, a fair BindCraft-vs-RFdiffusion comparison, and a controlled fibril-vs-monomer
validation plan earns an A. A single "great-looking" design with no hit-rate accounting, no monomer
counter-test, and a cherry-picked `specificity_gap` does not — no matter how big that gap looks. **A
design is a hypothesis; `pae_interaction` is not affinity; the `specificity_gap` is not a measured
selectivity; the fibril-vs-monomer assay is mandatory.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 11 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear neurodegeneration-diagnostic motivation; **target conformation chosen** + fibril-surface epitope justified from the cryo-EM structure; monomer counter-test set up; measurable success criteria (incl. a selectivity margin) + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Two-paradigm pipeline runs end-to-end; AF2-Multimer run **per conformer** (fibril + monomer); seeds + tool versions + commits logged; honest A100-vs-T4 scoping (incl. the ×2 conformer cost) |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Both pools generated at honest scale (BindCraft 50–200; RFdiffusion 500–1000→MPNN) against the fibril; every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) on both pools; **conformational-specificity test** (monomer vs fibril; `specificity_gap`; justified `GAP_MIN`; selective fraction per paradigm); head-to-head; cross-amyloid; honest fibril-AND-selective hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | **Fibril-vs-monomer** ELISA/SPR (the selectivity test) + cross-amyloid readout; positive (conformational anti-fibril antibody/tracer), **scrambled-interface** negative, **monomer** negative, unrelated negative; matched monomer/fibril preps; costed reagents + timeline; diagnostic-tracer framing |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend the epitope/conformation choice, the specificity test, and the limits ("this is a hypothesis until the fibril-vs-monomer assay; the monomer model is itself uncertain") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; conformation + epitope justified on a fibril-specific surface | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned BindCraft vs RFdiffusion choice + why AF2-Multimer per conformer | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Both paradigms at scale; multi-layer filter; **conformational-specificity test**; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest fibril AND selective hit rates + failure forensics (how many failed the monomer counter-test) + fair head-to-head + cross-amyloid reasoning | Some limitations noted | Superficial | None |
| Experimental plan | Detailed fibril-vs-monomer ELISA/SPR, controlled (incl. scrambled-interface + monomer negatives), matched preps, costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, selectivity quadrant, head-to-head distributions), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria incl. a selectivity margin + controls) +
  cleaned fibril protofilament + fibril-surface epitope list + monomer model + screenshot of the
  reproduced mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (fibril target → a few designs → AF2-Multimer (fibril
  + monomer) metrics + `specificity_gap`); `LOG.md` started; version-verify output captured.
- **D2 (Wk 12):** `results/bindcraft_designs.csv` + `results/rfdiffusion_designs.csv` (both pools vs the
  fibril, full config/seed log) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per paradigm, the **conformational-
  specificity** analysis (`results/specificity.csv`, the selectivity quadrant), head-to-head hit
  rate / interface-energy / novelty, cross-amyloid (`results/cross_amyloid.csv`), ranked top
  fibril-selective 10–20 each (`results/top_candidates.csv`).
- **D4 (Wk 22):** validation report + **fibril-vs-monomer** ELISA/SPR plan with controls (incl.
  scrambled-interface + monomer negatives), matched monomer/fibril preps, costed reagent list +
  timeline, diagnostic-tracer framing.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `04_validate` on the **mock** backend
and reproduce the survival-funnel + selectivity-quadrant figures from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions, pinned
commits, and seeds in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as
real results — including the `specificity_gap`, which is a model proxy, never a measured selectivity.**
