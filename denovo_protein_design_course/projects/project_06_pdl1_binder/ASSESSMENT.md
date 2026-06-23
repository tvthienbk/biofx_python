# Project 06 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the binder works.** A
binder campaign with a meticulously reported **low** hit rate, a fair BindCraft-vs-RFdiffusion
comparison, and a controlled validation plan earns an A. A single "great-looking" design with no
hit-rate accounting, no controls, and a cherry-picked metric does not — no matter how low its
`pae_interaction`. **A design is a hypothesis; `pae_interaction` is not affinity; SPR/BLI is mandatory.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 06 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear checkpoint-blockade motivation; PD-1-face hotspots justified from the PD-1/PD-L1 interface; measurable success criteria + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Two-paradigm pipeline runs end-to-end; seeds + tool versions + commits logged; honest A100-vs-T4 scoping |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Both pools generated at honest scale (BindCraft 50–200; RFdiffusion 500–1000→MPNN); every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) on both pools; survival-at-each-layer **per paradigm**; head-to-head hit rate / interface energy / novelty; epitope-competition vs PD-1; honest hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | SPR/BLI + **PD-1-competition** assay; positive (known PD-L1 binder), **scrambled-interface** negative, unrelated negative; expression strategy; costed reagents + timeline |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend hotspot choice, the paradigm comparison, and the limits ("this is a hypothesis until SPR") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; hotspots justified on the competitive epitope | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned BindCraft vs RFdiffusion choice + why AF2-Multimer | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Both paradigms at scale; multi-layer filter; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest hit rates + failure forensics + fair head-to-head + epitope-competition reasoning | Some limitations noted | Superficial | None |
| Experimental plan | Detailed SPR/BLI + PD-1-competition, controlled (incl. scrambled-interface), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, head-to-head distributions), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria + controls) + cleaned PD-L1 + hotspot
  list + screenshot of the reproduced mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (target → a few designs → AF2-Multimer metrics);
  `LOG.md` started; version-verify output captured.
- **D2 (Wk 12):** `results/bindcraft_designs.csv` + `results/rfdiffusion_designs.csv` (both pools, full
  config/seed log) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per paradigm, head-to-head hit
  rate / interface-energy / novelty, ranked top 10–20 each, epitope-competition vs PD-1.
- **D4 (Wk 22):** validation report + SPR/BLI + PD-1-competition plan with controls (incl.
  scrambled-interface), expression strategy, costed reagent list + timeline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock**
backend and reproduce the survival-funnel figure from the tagged release, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions, pinned commits, and seeds
in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as real results.**
