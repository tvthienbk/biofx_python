# Project 04 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Symmetry contigs + tied positions + oligomeric-state error; verify Cn/Dn accessions; reproduce a small C3 (mock → real) | **D0:** Problem statement + reproduced small-C3 output |
| **P1 — Baseline** | 3–6 | Minimal symmetric pipeline: generate → tied-MPNN → AF2-Multimer on a tiny C3 batch end-to-end | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Generate C3/C4/D2 (100s of designs) with symmetric contigs; tied ProteinMPNN; `results/assemblies.csv` | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Filter (oligomer cutoffs: subunit scRMSD, interface pAE<10, symmetry RMSD); symmetry-order-vs-success + tied-vs-untied benchmark | **D3:** Ranked assemblies + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Wrong-oligomer risk analysis (model alternative states); nsEM/SEC-MALS/native-MS plan; antigen-display extension | **D4:** Validation report + experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter + assembly design report; tagged reproducible release | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Compute is the bottleneck, and it is real.** Symmetric RFdiffusion + AF2-Multimer are heavy; a
  free T4 realistically runs only a **small C3 demo**. Budget **A100 time** (Colab Pro+, an
  institutional GPU, or a cloud platform) for the full C3/C4/D2 campaign in Weeks 7–12. Tied
  ProteinMPNN itself is cheap (CPU/T4 fine) — the cost is diffusion and multimer prediction.
- **Wrong-oligomer error is the scientific core, not an afterthought.** Reserve Weeks 19–20 to model
  *alternative* oligomeric states for your top designs — a design that also scores well as the wrong
  order is a red flag, and catching it is the most valuable thing this project teaches.
- **AF2-Multimer pAE is necessary-not-sufficient.** Passing the in-silico filter does not prove
  assembly; the D4 plan (nsEM, SEC-MALS, native-MS) is what actually confirms the state. Write it as
  a real experiment with controls, not a formality.

### Instructor scaling knob
Assign all `[core]` tasks to everyone; `[extension]` (wrong-oligomer alternative-state modelling;
epitope-graft antigen-display) to most; `[stretch]` (tetrahedral / higher-symmetry cages) to
strong / MSc-track students. Scale the campaign size to the compute you can secure: a tied-MPNN-only
or C3-only campaign is a legitimate de-scope on a T4-only budget.
