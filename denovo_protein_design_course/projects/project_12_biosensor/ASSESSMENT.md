# Project 12 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the sensor works.** A
campaign with a meticulously reported **low** binder hit rate, a fair switch-architecture comparison,
an honest **affinity-vs-dynamic-range** analysis, and a controlled functional-readout plan earns an A.
A single "great-looking" construct with no hit-rate accounting, no controls, and a cherry-picked
dynamic range does not — no matter how high that number is. **A binder is a hypothesis;
`pae_interaction` is not affinity; a modeled dynamic range is not a measured signal; there is no LOD
until a real dose-response is fit.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 12 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear point-of-care motivation; analyte + readout chosen on purpose; both switch architectures understood; measurable success criteria (incl. a dynamic-range target) + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Binder pipeline + switch module + integration run end-to-end; seeds + tool versions + commits logged; honest A100-vs-T4 scoping |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Both binder pools at honest scale (BindCraft 50–200; RFdiffusion 500–1000→MPNN) + ≥1 switch architecture; every config + seed in the design log; no premature filtering |
| Filtering, integration & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) per paradigm; **integration** + ON/OFF two-state reasoning; switch-architecture benchmark; affinity-vs-dynamic-range trade-off; honest hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | Luminescence/FRET **dose-response** + **LOD estimate from data**; **no-analyte/blank** + **off-target** controls; expression strategy; costed reagents + timeline |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend the analyte/readout choice, the switch-architecture comparison, and the limits ("this is a hypothesis until a dose-response") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; analyte/readout justified; dynamic-range target named | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned BindCraft vs RFdiffusion + switch-architecture choice + why AF2-Multimer/two-state | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Binder at scale + switch + integration; multi-layer filter; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest hit rates + failure forensics + fair switch benchmark + affinity-vs-dynamic-range reasoning | Some limitations noted | Superficial | None |
| Experimental plan | Detailed luminescence/FRET dose-response + LOD, controlled (no-analyte + off-target), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, architecture boxplots, trade-off scatter), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria incl. a dynamic-range target + controls) +
  analyte/readout choice + epitope list + screenshot of the reproduced mock hello-world.
- **D1 (Wk 6):** repo link; minimal binder pipeline demo (target → a few designs → AF2-Multimer metrics)
  + a first mock integration; `LOG.md` started; version-verify output captured.
- **D2 (Wk 12):** `results/bindcraft_designs.csv` + `results/rfdiffusion_designs.csv` +
  `results/switch_designs.csv` (full config/seed log) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per paradigm; integrated constructs with
  ON/OFF (`results/constructs.csv`); switch-architecture benchmark (`results/p12_architecture.png`);
  affinity-vs-dynamic-range (`results/p12_tradeoff.png`); `results/top_constructs.csv`.
- **D4 (Wk 22):** validation report + luminescence/FRET dose-response + LOD plan with controls
  (no-analyte/blank + off-target, `results/offtarget_controls.csv`), expression strategy, costed
  reagent list + timeline; (stretch) multiplexing concept.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `05_validation_plan` on the **mock**
backend and reproduce the survival-funnel + switch-architecture figures from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions, pinned
commits, and seeds in the report. **Mock numbers (binder metrics, ON/OFF, dynamic range, dose-response)
are `SYNTHETIC` and must never appear in the report as real results — and there is no fabricated LOD.**
