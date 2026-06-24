# Project 13 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the mimetic works.** An
agonist campaign with a meticulously reported **low** hit rate, a clean **per-subunit selectivity
profile** (engages βγ, spares α), a stability comparison to native IL-2, and a controlled validation
plan earns an A. A single "great-looking" design with no selectivity analysis, no hit-rate accounting,
and no controls does not — no matter how low its `pae_interaction`. **A design is a hypothesis;
`pae_interaction` is not affinity; and binding is not signaling — the cell pSTAT5 assay decides agonism.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 13 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear cytokine-mimetic motivation; **explicit subunit/selectivity choice** (which subunits to engage, which to spare, and why); measurable success criteria + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Agonist pipeline runs end-to-end; AF2-Multimer modeled **per subunit**; seeds + tool versions + commits logged; honest A100-vs-T4 scoping |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Pool generated at honest scale (RFdiffusion 500–1000→MPNN, and/or BindCraft 50–200); every design scored against **all three** subunits; every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) on engaged subunits; **subunit-selectivity profile** + selectivity margin (engages βγ, spares α); **stability-vs-native** comparison; survival-at-each-layer; honest hit-rate **and** selectivity accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | **Per-subunit SPR/BLI** + a **cell STAT-phosphorylation (pSTAT5)** assay; positive (native IL-2 / Neo-2/15), **scrambled-interface** negative, unrelated negative; expression strategy; costed reagents + timeline; explicit "binding ≠ signaling" |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend the subunit/selectivity choice, the selectivity profile, and the limits ("selective in silico ≠ an agonist until pSTAT5") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; subunit/selectivity choice justified (engage βγ, spare α, to reduce toxicity) | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned RFdiffusion/BindCraft choice + why AF2-Multimer **per subunit** | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Pool at scale; per-subunit modeling; multi-layer filter; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest hit rates + **selectivity profile** + selectivity margin + stability comparison + binding-vs-signaling caveat + failure forensics | Some limitations noted | Superficial | None |
| Experimental plan | Detailed per-subunit SPR + **pSTAT5 signaling** assay, controlled (incl. scrambled-interface), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, selectivity profile, stability comparison), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria + controls) + written
  target-subunit/selectivity choice + per-subunit hotspot lists + screenshot of the reproduced mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (target → a few designs → AF2-Multimer **per subunit**
  metrics); `LOG.md` started; version-verify output captured.
- **D2 (Wk 12):** `results/designs.csv` with per-subunit metrics (`pae_to_alpha/beta/gamma`) + full
  config/seed log + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer, **per-subunit selectivity profile** +
  selectivity margin, **stability-vs-native** comparison, ranked top candidates.
- **D4 (Wk 22):** validation report + **per-subunit SPR/BLI + cell STAT-phosphorylation** plan with
  controls (incl. scrambled-interface), expression strategy, costed reagent list + timeline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock**
backend and reproduce the survival-funnel figure and the selectivity profile from the tagged release,
the reproducibility components are capped at "Adequate" until fixed. State exact tool versions, pinned
commits, and seeds in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as
real results — no fabricated EC50/K_D/pSTAT values.**
