# Project 17 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for
weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | TAA + nanobody/CDR biology; choose epitope (overlap vs not); verify accessions; reproduce the mock VHH hello-world | **D0:** Problem statement (TAA + epitope choice) + reproduced hello-world |
| **P1 — Baseline** | 3–6 | Clean target + fix framework + epitope list; run the full mock pipeline; a tiny real RFantibody demo | **D1:** Working minimal VHH pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | A100 VHH campaign (500+); ProteinMPNN CDR design; AF2-Multimer + IgFold scoring → `campaign.csv` | **D2:** Full VHH pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Antibody filter (`design_type="antibody"`); epitope-choice + receptor-family specificity + developability/humanness figures | **D3:** Ranked candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Specificity panel deepening; display-screen plan + downstream format (imaging/CAR) + controls + costed plan | **D4:** Validation report + display-screen + experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release (the antibody-family template) | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Compute is the bottleneck, not curation.** The real VHH campaign wants an **A100**; a free T4 runs
  only a *tiny* RFantibody demo. Book A100/HPC time for Weeks 7–10 early, and remember **AF2-Multimer
  scoring is the slow step** — batch it overnight.
- **The epitope decision (P0) gates everything.** Choosing overlapping vs non-overlapping (and reading
  the *right* residues off the *verified* structure) determines the whole campaign and the downstream
  bispecific/biparatopic option. Don't rush it.
- **Hit rates are low.** Budget for a large pool + a display screen; survivors are screening inputs, not
  finished binders. Plan the screen (P4) as a real deliverable, not an afterthought.
- This project is the **antibody-family template** (Projects 14–16 reuse its structure): keep
  `antibody_tools.py`, the notebook flow, and the `design_type="antibody"` filter hand-off clean.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (RFantibody-vs-BoltzGen head-to-head;
parameter exploration; specificity deepening), `[stretch]` (biparatopic/bispecific concept) to
strong/MSc-track students.
