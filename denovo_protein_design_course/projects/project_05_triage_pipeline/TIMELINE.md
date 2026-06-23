# Project 05 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Master the discrimination problem; spec the `Design` + layer API; implement Layer 1; verify data accessions | **D0:** API spec write-up + Layer 1 passing/failing planted designs |
| **P1 — Baseline** | 3–6 | Build the labeled `EXAMPLE_DATA` pool; wire Layer 1 + `rank_designs` + `report` end-to-end; first test | **D1:** Minimal engine + labeled pool + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Implement + unit-test Layers 2 (orthogonal) + 3 (physics) on known-good/known-bad designs | **D2:** Layers 2+3 + passing `test_filtering.py` + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Run the **shared** engine; survival-at-each-layer; enrichment per layer; cutoff-sensitivity; discrimination analysis | **D3:** Ranked CSV + survival figure + enrichment + sensitivity figures |
| **P4 — Validate + plan** | 19–22 | Optional Layer 4 (short MD) hook; cohort-adoption-via-PR guide; (stretch) pip-package scaffold | **D4:** Layer-4 hook + sensitivity study + adoption guide |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged release that becomes the cohort's `shared/filtering_pipeline.py` | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **The tests are the spine, not an afterthought.** Build `scripts/test_filtering.py` alongside each
  layer (Weeks 4, 7–10) so every cutoff change is checked against the planted known-good/known-bad
  designs. A layer with no failing planted case is untested.
- **Compute is NOT the bottleneck here** — the engine is pure-Python scoring that runs on CPU. The
  GPU-bound work (running AF2/ESMFold/Boltz/MD to *produce* the metrics) belongs to Projects 01/03;
  this project consumes their numbers. Budget your time on *design of cutoffs, tests, and the honest
  analysis*, not on GPU queues.
- **Weeks 15–18 (enrichment + cutoff sensitivity) are the real intellectual work**: showing that
  each layer enriches but none separates cleanly, and that the ranking is cutoff-sensitive.
- This project's output is **shared infrastructure**: budget Weeks 21–24 to land your engine as
  `shared/filtering_pipeline.py` via reviewed pull request, so Projects 01–25 adopt it.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (Layer-3 per-type tests; enrichment
curves), `[stretch]` (Layer 4 / short-MD hook; pip-packaging scaffold; per-design-type cutoff
re-calibration with evidence) to strong/MSc-track students.
