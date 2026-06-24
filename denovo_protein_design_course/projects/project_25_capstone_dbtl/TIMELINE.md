# Project 25 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Choose + justify the target; **advisor §7 responsible-research approval**; success criteria + controls; ML framing; reproduce a mock mini-run | **D0:** Problem statement + approved target + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal campaign pipeline (target → designs → score → metrics) + first cohort-table slice; repo + `LOG.md` + version-verify | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | Full design campaign at honest scale **and** assemble the cohort design→outcome feature table (Projects 01–24) | **D2:** Campaign pool + cohort feature table + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (classical baseline); **train + cross-validate the ML success predictor**; feature importance; **enrichment vs single-metric cutoffs**; cross-target generalization | **D3:** Ranked candidates + trained success predictor + filtering report |
| **P4 — Validate + plan** | 19–22 | Plan/execute validation with controls; **integrate experimental labels**; honest hit-rate + failure forensics; active-learning loop design | **D4:** Validation report + experimental plan + integrated labels + hit-rate analysis |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; **PR the improved success predictor into `shared/`**; `v1.0` tagged release | **D5:** Thesis + talk + release + D★ predictor module |

### Critical-path notes
- **The §7 advisor approval is a hard gate before P2.** Do not start the design campaign until your
  chosen target is approved against `MASTER_BLUEPRINT.md §7`. Default ambiguous targets to a
  neutralizing/diagnostic/inhibitory/industrial framing.
- **Two workstreams run in parallel from P2.** The *campaign* (heavy, A100-bound) and the *cohort table
  assembly* (data wrangling across Projects 01–24) are independent — start the table early; assembling
  trustworthy `features → outcome` rows is slow archival work, not compute.
- **The ML part is light / CPU-OK** — the bottleneck is **data**, not GPU. The honest result is a modest
  enrichment over single-metric cutoffs (or a clear negative); budget time for the analysis + write-up,
  not for chasing a perfect classifier.
- This is the **integrative capstone**: schedule it **last** in a cohort cycle so it can consume the
  design→outcome data the other projects produced.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (estimator comparison, cross-target
generalization, parameter sweeps), `[stretch]` (active-learning loop; integrating real wet-lab labels;
go/no-go execution) to strong/MSc-track students.
