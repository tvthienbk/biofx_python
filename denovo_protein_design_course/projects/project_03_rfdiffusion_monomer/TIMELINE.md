# Project 03 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Master scRMSD vs novelty on paper; verify accessions; reproduce the 10-backbone monomer tutorial | **D0:** Problem statement + reproduced tutorial output |
| **P1 — Baseline** | 3–6 | Stand up `rfdiff_tools` + wire real RFdiffusion→MPNN→AF2/ESMFold→Foldseek; first small batch | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Generate hundreds of backbones across lengths {80,120,200,300} × SS-bias {α,β,mixed}; MPNN (8 seqs) → self-consistency; build `results/backbones.csv` | **D2:** Full backbone pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared filter (monomer); novelty-vs-scRMSD frontier; per-topology/length success rates; RFdiffusion/FrameFlow/Genie2 comparison scaffold | **D3:** Ranked candidates + frontier figure + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal refold of top picks; novelty budget; synthesis/expression plan with paired risky-vs-conservative controls; (stretch) short MD | **D4:** Validation report + synthesis plan + novel-but-foldable set (D★) |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release including the novelty-budget guideline | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Compute is the bottleneck, and it is honest about tiers.** A free **T4 handles small batches**
  (P0–P1 and slices of P2) but the **full lengths×topology sweep needs an A100 or HPC** — schedule
  cluster/Colab-Pro+ access for Weeks 7–10 and batch generation overnight. Do not plan the whole
  campaign on a T4.
- **all-β and length-300 cells are where success collapses** — budget extra generation there so you
  have enough designs to report a *rate*, not an anecdote. A near-empty cell is still a result, but
  confirm it isn't just under-sampled.
- **Novelty scoring needs the Foldseek PDB database** (large, downloaded, never committed). Set up
  that download early (Week 4–5) so it isn't a surprise in P3; store it on Drive/HPC scratch.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (the FrameFlow/Genie2 comparison; MPNN
temperature exploration), `[stretch]` (short MD stability check on top picks) to strong/MSc-track
students.
