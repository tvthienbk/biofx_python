# Project 10 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the binder inhibits.** A
campaign with a meticulously reported **low** hit rate, an honest occlusion + specificity analysis, a
fair BindCraft-vs-RFdiffusion comparison, the rim-vs-distal ablation, and a controlled inhibition-assay
plan earns an A. A single "great-looking" design with no hit-rate accounting, no controls, and a
cherry-picked metric does not — no matter how low its `pae_interaction`. **A design is a hypothesis;
`pae_interaction` is not affinity; occlusion is not inhibition; the nitrocefin/carbapenem IC50 assay is
mandatory.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 10 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear defensive-anti-AMR motivation (inhibit NDM-1, restore carbapenems); active-site-rim hotspots justified; di-zinc preserved; measurable success criteria (incl. an occlusion threshold) + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Two-paradigm pipeline (with **LigandMPNN**, Zn-aware) runs end-to-end; seeds + tool versions + commits logged; honest A100-vs-T4 scoping |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Both pools at honest scale (BindCraft 50–200; RFdiffusion 500–1000→LigandMPNN); every config + seed in the design log; no premature filtering; Zn²⁺ retained throughout |
| Filtering, occlusion, specificity & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) on both pools; survival-at-each-layer **per paradigm**; **occlusion** modeling + **specificity vs human metalloenzymes**; head-to-head + rim-vs-distal ablation; honest hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | **Nitrocefin/carbapenem-hydrolysis INHIBITION (IC50)** assay; off-target-human-metalloenzyme control, **scrambled-interface** negative, enzyme-only positive; expression strategy; costed reagents + timeline; β-lactam-adjuvant stretch |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend rim-hotspot choice, the occlusion/specificity logic, the paradigm comparison, and the limits ("binding ≠ inhibition until the IC50 assay") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; rim hotspots justified on the substrate-access channel; di-zinc preserved | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned BindCraft vs RFdiffusion + **why LigandMPNN (Zn-aware)** + why AF2-Multimer | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Both paradigms at scale; multi-layer filter + occlusion + specificity; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest hit rates + failure forensics + fair head-to-head + rim-vs-distal ablation + binding≠inhibition caveat | Some limitations noted | Superficial | None |
| Experimental plan | Detailed nitrocefin/carbapenem IC50 assay, controlled (off-target metalloenzyme + scrambled-interface), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, occlusion/specificity distributions), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria incl. an occlusion threshold + controls)
  + cleaned di-zinc NDM-1 (**both Zn²⁺ retained**) + active-site-rim hotspot list + screenshot of the
  reproduced mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (target → a few designs → AF2-Multimer metrics);
  `LOG.md` started; version-verify output captured.
- **D2 (Wk 12):** `results/bindcraft_designs.csv` + `results/rfdiffusion_designs.csv` (both pools, full
  config/seed log) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per paradigm, **occlusion + specificity**
  distributions, head-to-head + rim-vs-distal ablation, ranked top 10–20 each.
- **D4 (Wk 22):** validation report + **nitrocefin/carbapenem inhibition (IC50)** plan with controls
  (off-target metalloenzyme + scrambled-interface), expression strategy, costed reagent list + timeline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock**
backend and reproduce the survival-funnel figure from the tagged release, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions, pinned commits, and seeds
in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as real results;
there is no in-silico IC50 — that would be fabricated.**
