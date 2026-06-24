# Project 07 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects), instantiated with this project's tasks. Milestones
D0–D5 are the graded deliverables. See `ASSESSMENT.md` for weighting, `INSTRUCTIONS.md` for detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Map conserved vs variable RBD epitopes; verify accessions; reproduce a mini-run | **D0:** Conserved-epitope map + problem statement + mini-run |
| **P1 — Baseline** | 3–6 | Clean the RBD target; BindCraft mini-run; minimal binder pipeline (AF2-Multimer pae) | **D1:** Working pipeline + first batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft (50–200) + RFdiffusion (500–1000 → MPNN) at the conserved epitope | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & breadth** | 13–18 | Shared binder filter; cross-variant breadth (worst-case pae); conserved-vs-variable; head-to-head | **D3:** Ranked candidates + breadth analysis + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal checks; ACE2-competition + pseudovirus-neutralization breadth plan with controls + IBC | **D4:** Validation report + costed breadth-testing plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Epitope choice (Weeks 1–2) is load-bearing:** a variable epitope dooms breadth. Get advisor
  sign-off on a *conserved* epitope before the campaign.
- **The campaign (Weeks 7–10) is compute-bound:** BindCraft + RFdiffusion + AF2-Multimer realistically
  want an **A100**. Budget cluster/Colab-Pro time; FreeBindCraft + small batches on free T4 only.
- **Breadth (Weeks 15–16) is the result:** modeling each candidate across a variant panel multiplies
  AF2-Multimer cost by the panel size — plan for it.

### Instructor scaling knob
`[core]` to all; `[extension]` (conserved-vs-variable comparison, orthogonal checks) to most;
`[stretch]` (Boltz-2 relative affinity, larger variant panels) to strong/MSc-track students.
