# Project 16 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for weighting
and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Humanization strategies (grafting/resurfacing/germline-content); pick + verify antibody + human germline framework(s); reproduce the mock hello-world | **D0:** Problem statement (antibody + germline + strategy) + reproduced hello-world |
| **P1 — Baseline** | 3–6 | Number the antibody (ANARCI); fix candidate frameworks + Vernier list; run the full mock pipeline; a real humanness score (T4) | **D1:** Working minimal humanization pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Graft CDRs onto several human frameworks (+ resurfacing + controls); real humanness (OASis/Hu-mAb/AbLang) + ΔΔG (FoldX/Rosetta on IgFold) → `campaign.csv` | **D2:** Full variant pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Antibody filter (`design_type="antibody"`) + humanness floor; humanness↔stability trade-off + Vernier back-mutation + grafting-vs-resurfacing figures; immunogenicity-risk summary | **D3:** Ranked variants + trade-off figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal ΔΔG check; ELISA/SPR/DSF plan (retained binding + Tm) + immunogenicity-risk + controls (parental, over-humanized decoy) + costed plan | **D4:** Validation report + experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Compute is NOT the bottleneck here.** This project is genuinely **free-tier (Colab T4) friendly**:
  humanness scoring, an IgFold/ImmuneBuilder Fv model, and ΔΔG (FoldX/Rosetta) are all light. The real
  bottleneck is **curation + reasoning**: picking the right human germline and the right Vernier
  back-mutations.
- **The antibody + germline choice (P0) gates everything.** A poorly matched human germline (far from the
  parental V/J gene) means more framework mutations, higher ΔΔG, and more back-mutations. Choose the
  closest human germlines and read the Vernier positions off the *verified, numbered* sequence.
- **The humanness↔stability trade-off is the deliverable.** Grafting often loses affinity/stability and
  needs back-mutations; budget P3 for the full trade-off study (curve + ladder + grafting-vs-resurfacing),
  not a single "best" variant.
- **Controls are mandatory** even in the plan: the **parental** antibody and an **over-humanized decoy**
  are what make the validation interpretable.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (resurfacing comparison; ProteinMPNN framework
optimization; parameter exploration), `[stretch]` (T-cell-epitope predictor in the risk summary;
germline-content optimization loop) to strong/MSc-track students.
