# Project 02 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Understand the recovery↔foldability↔expressibility trade-off; verify accessions; reproduce one MPNN + recapitulation run | **D0:** Problem statement + metrics table + reproduced one-backbone design |
| **P1 — Baseline** | 3–6 | Build the minimal pipeline (backbone → MPNN → recapitulation → recovery); collect 20–30 backbones | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | The systematic sweep: temperature × noise × seqs across all backbones (hundreds of sequences) | **D2:** `results/sequences.csv` + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared filter (monomer); per-setting recovery/recapitulation/diversity/solubility; **Pareto-optimal settings**; MPNN vs ESM-IF | **D3:** Ranked survivors + Pareto map + filtering report |
| **P4 — Validate + plan** | 19–22 | Settings-recommendation heuristic; codon/tag strategy; experimental plan with controls; (stretch) MPNNsol surface redesign | **D4:** Recommendation tool + costed, controlled plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged release; the **MPNN settings cheat-sheet** for the cohort | **D5:** Thesis + 15-min talk + `v1.0` release + cheat-sheet |

### Critical-path notes
- **Recapitulation is the compute bottleneck, not MPNN.** ProteinMPNN runs in seconds; predicting
  every swept sequence with AF2 full-MSA does not fit a free T4 at scale. Triage with ESMFold
  (seconds), reserve AF2 for survivors, batch overnight. Budget P2/P3 around this.
- **Backbone assembly (Weeks 3–4) is finicky archival work,** not compute. The 20–30 de novo
  backbones come from Project 03 outputs or a public design set — start sourcing and logging their
  provenance in Week 1, not Week 3.
- This project's output is **shared know-how**: budget Week 23–24 to publish the settings cheat-sheet
  so later cohort projects (binders, enzymes, antibodies — all of which run MPNN) adopt your defaults.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (consensus-vs-single design;
recommendation model; MPNN vs ESM-IF), `[stretch]` (MPNNsol / surface-redesign comparison) to
strong/MSc-track students.
