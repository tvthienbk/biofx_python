# Project 22 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Multi-state/allostery literature; verify switch/hinge accessions; define two states + trigger; reproduce the mock hello-world (one sequence → two states + gap) | **D0:** Problem statement (two states + trigger + measurable criteria + controls) + reproduced hello-world |
| **P1 — Baseline** | 3–6 | Stand up `multistate_tools.py` on the mock backend; wire the real backends on Colab/A100 (RFdiffusion ×2 → multi-state MPNN → predict-both); first tiny batch | **D1:** Working minimal pipeline + first small batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Generate the **two state backbones**; run **multi-state ProteinMPNN** (tied across both) for a shared-sequence pool; predict both states; assemble `results/multistate_designs.csv` | **D2:** Two backbones + shared-sequence pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared filter on **BOTH** states (`design_type="monomer"`); AF2-predicts-both + energy-gap; **single- vs multi-state** benchmark; honest hit-rate ladder | **D3:** Per-state-filtered candidates + energy-gap analysis + benchmark + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal/state-biased prediction; (ext) transition MD; **state-change read-out plan** (FRET/protease/SAXS) with paired controls; (stretch) LOV light-switch | **D4:** Validation report + costed, controlled read-out plan + selected design (D★) |
| **P5 — Synthesize** | 23–24 | Thesis chapter (with the multi-state designability + energy-gap caveats); 15-min talk; tagged reproducible release | **D5:** Thesis + talk + `v1.0` release |

### Critical-path notes
- **Compute is the bottleneck, and it is severe.** Two RFdiffusion backbone runs + multi-state MPNN +
  AF2 predicting **both** states (×2 per design) + optional transition MD is the most expensive
  workflow in the course. **Budget A100/HPC time for Weeks 7–16**; a free T4 runs only a small
  fallback (short backbones, few designs, ESMFold triage). Do not plan the full campaign on a T4.
- **Weeks 9–10 (multi-state MPNN) are scientifically decisive, not just slow.** A single sequence
  satisfying two states well is rare; expect a low yield and start the A-vs-B trade-off analysis the
  moment the first batch lands. Don't wait for the full pool to notice the trade-off.
- **The benchmark (Weeks 15–16) IS the result.** Design each backbone alone with normal MPNN and show
  those single-state sequences fail the *other* state — that contrast is the headline. Reserve real
  time for it; it is not an afterthought.
- **The energy-gap caveat is load-bearing.** AF2 may only ever return one state, so a "switchable"
  flag is a hypothesis. Plan Weeks 17–20 to stress-test every switchable pick (state-biased
  prediction) before you trust it.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (transition MD; tying-scheme parameter
exploration), `[stretch]` (LOV light-switch integration; executing a wet-lab go/no-go tier) to
strong/MSc-track students with A100/HPC and lab access.
