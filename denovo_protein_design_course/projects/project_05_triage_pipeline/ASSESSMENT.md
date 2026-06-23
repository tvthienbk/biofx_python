# Project 05 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether any protein works.**
This is an infrastructure project: a clean, **tested**, documented filter engine that *honestly
reports* an imperfect discrimination ability and maps where it fails earns an A. An engine that
ranks designs with confident-looking cutoffs but no tests, no enrichment analysis, and no honest
discrimination writeup does not — no matter how polished the figures. Synthetic `EXAMPLE_DATA`
numbers presented as real results are an automatic integrity problem.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 05 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | API spec is correct; the discrimination problem (filters enrich, not guarantee) is stated precisely, not hand-waved |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | All 4 layers implemented behind clean boundaries; `python scripts/test_filtering.py` passes; seeds + versions logged; 03 imports the **shared** module |
| Engine rigor (tests, controls, logging) | 15% | D2 | Unit tests assert known-good passes / known-bad fails per layer **and** per design type; planted designs documented; design log complete |
| Filtering, benchmarking & critical analysis | 20% | D3 | Survival + **enrichment** (precision/recall) per layer on the labeled pool; cutoff-sensitivity sweep; explicit false-positive/false-negative discussion |
| Validation / adoption plan (usefulness, evidence) | 15% | D4 | Optional Layer-4 hook with its planted test; cutoff changes justified by enrichment + N; PR-based cohort-adoption guide (no silent overwrite) |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; engine adopted as `shared/filtering_pipeline.py` |
| Oral defense | 10% | D5 | Can defend each cutoff and own the engine's limits (where it fails to discriminate) |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, measurable; discrimination problem understood precisely | Clear but generic | Vague | Absent / "filter = guarantee" misunderstanding |
| Tool selection & justification | Reasoned cutoffs per design type, each justified | Correct, thin justification | No rationale | Wrong / unjustified cutoffs |
| Computational execution | All 4 layers, clean boundaries, **passing tests**, reproducible | Complete, basic tests | Incomplete / untested | Non-working |
| Critical analysis | Enrichment per layer + cutoff sensitivity + explicit FP/FN forensics | Some limitations noted | Superficial | None / synthetic-as-real |
| Validation / adoption plan | Layer-4 hook + evidence-backed cutoff changes + PR adoption guide | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival/enrichment/sensitivity), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page API spec (`Design` fields + layer signatures/contracts) + printout of Layer 1 passing the planted known-good and failing the known-bad `EXAMPLE_DATA` design.
- **D1 (Wk 6):** repo link; minimal engine (Layer 1 + `rank_designs` + `report`) demo on `results/pool.csv`; `LOG.md` started; first passing test.
- **D2 (Wk 12):** Layers 2 + 3 implemented; `python scripts/test_filtering.py` exits 0 (known-good/known-bad per layer and per type); design log; 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: ranked CSV + survival figure from the **shared** module, enrichment-per-layer (precision/recall) on the labeled pool, cutoff-sensitivity sweep, FP/FN table.
- **D4 (Wk 22):** optional Layer-4 (short MD) hook + its planted test; cutoff-sensitivity study; cohort-adoption (PR) guide + pip-package scaffold (shown, not committed).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release; the engine landed as `shared/filtering_pipeline.py`.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot (a) run `python scripts/test_filtering.py` against the
shared `filtering_pipeline` and see it pass, and (b) rerun `00_setup` → `03_filter_and_rank` on Colab
and reproduce the survival figure from the tagged release, the reproducibility components are capped
at "Adequate" until fixed. State exact tool versions + seeds in the report; label every
`EXAMPLE_DATA` figure as synthetic.
