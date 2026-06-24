# Project 14 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects), instantiated with this project's tasks. Milestones
D0–D5 are the graded deliverables. See `ASSESSMENT.md` for weighting, `INSTRUCTIONS.md` for detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Choose a conserved neutralizing epitope + humanized framework; verify accessions; mini-run | **D0:** Epitope/framework choice + problem statement + mini-run |
| **P1 — Baseline** | 3–6 | Clean the antigen; small RFantibody run; minimal VHH pipeline (AF2-Multimer pae + CDR geometry) | **D1:** Working pipeline + first batch + repo |
| **P2 — Campaign** | 7–12 | RFantibody CDR design (500+) + AF2-Multimer/IgFold + developability; BoltzGen head-to-head | **D2:** VHH pool (500+) + design log + interim report |
| **P3 — Filter & breadth** | 13–18 | Shared antibody filter; developability/humanness gate; cross-strain breadth (worst-case) | **D3:** Ranked + filtered candidates + breadth + report |
| **P4 — Validate + plan** | 19–22 | Orthogonal checks; yeast-display screen plan + neutralization/breadth plan with controls + IBC | **D4:** Screen plan + neutralization/breadth plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Epitope choice (Weeks 1–2) is load-bearing:** a non-conserved epitope dooms breadth.
- **Low hit rate ⇒ generate 500+ (Weeks 7–8):** de novo antibody success is low; the pool feeds a display screen.
- **The campaign is compute-bound:** RFantibody + AF2-Multimer realistically want an **A100**. Breadth modeling across the strain panel multiplies AF2-Multimer cost.

### Instructor scaling knob
`[core]` to all; `[extension]` (BoltzGen head-to-head, larger strain panels) to most; `[stretch]`
(real developability tools, deeper breadth panels) to strong/MSc-track students.
