# Project 01 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Master the confidence metrics on paper; verify data accessions; reproduce one prediction | **D0:** Metric-definitions write-up + reproduced prediction |
| **P1 — Baseline** | 3–6 | Build the unified `predict()` wrapper (ESMFold → AF2 → Boltz); add scRMSD + novelty | **D1:** Working prediction wrapper + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Curate the labeled dataset (≥40 designs + ≥10 refs, with provenance); predict all; MSA-depth ablation | **D2:** Labeled dataset + full prediction table + interim report |
| **P3 — Filter & benchmark** | 13–18 | Calibration study: ROC/PR per metric, best single + composite predictor, AF2/ESMFold/Boltz agreement | **D3:** Calibration study + figures + failure-mode breakdown |
| **P4 — Validate + plan** | 19–22 | Validation SOP card (cutoffs by type, with evidence); harden `filtering_pipeline.py`; (stretch) Boltz affinity vs measured K_D | **D4:** SOP + hardened module + cohort usage guide |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release that becomes the cohort's official harness | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Weeks 7–8 (dataset curation) are the real bottleneck**, not compute. Assembling ≥40 designs
  with *trustworthy* experimental labels from supplementary tables is slow, finicky archival work.
  Start it in Week 1 in the background; don't leave it to Week 7.
- **Predictions (Weeks 9–10)** are embarrassingly parallel but compute-bound on a T4. Triage with
  ESMFold (seconds), reserve AF2 full-MSA for the subset that matters, batch overnight.
- This project's output is **shared infrastructure**: budget Week 19–20 to land your
  `filtering_pipeline.py` calibration via pull request so Projects 02–25 can adopt it.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most, `[stretch]` (Boltz-2 affinity vs
measured K_D; per-design-type calibration) to strong/MSc-track students.
