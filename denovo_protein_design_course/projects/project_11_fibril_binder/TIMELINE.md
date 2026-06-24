# Project 11 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Amyloid/fibril structural biology; verify accessions (tau 5O3L/5O3T, α-syn 6CU7/6H6B); choose target conformation, clean a protofilament + pick the exposed fibril-surface epitope; assemble a monomer model; reproduce a mini-run (mock) | **D0:** Problem statement + target-conformation choice + fibril prep + monomer model + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal binder pipeline (fibril target → BindCraft/RFdiffusion mini-batch → ProteinMPNN → AF2-Multimer (fibril + monomer) → metrics + specificity_gap); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft campaign (50–200) **and** RFdiffusion-binder campaign (500–1000 → ProteinMPNN) against the fibril surface; assemble both pools; design log | **D2:** Two-paradigm design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on both pools; **conformational-specificity test** (monomer vs fibril, `specificity_gap`, selective fraction); BindCraft-vs-RFdiffusion hit rate / interface energy / novelty; cross-amyloid (tau vs α-syn); top fibril-selective 10–20 each | **D3:** Ranked fibril-selective candidates + specificity analysis + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction (both conformers); cross-amyloid analysis; (stretch) Boltz-2 affinity scaffold; costed **fibril-vs-monomer** ELISA/SPR plan with controls + diagnostic-tracer framing | **D4:** Validation report + costed, controlled experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free — and here it roughly doubles.** A real campaign wants
  an **A100** (Colab Pro+ or a cluster), and you run AF2-Multimer **twice per design** (fibril +
  monomer) for the specificity test. Secure A100 access (or scope down to a FreeBindCraft/T4 fallback)
  **before Week 7** — and budget the ×2 conformer cost.
- **AF2-Multimer re-prediction of every design (×2 conformers) is the slow step**, not generation.
  Triage with cheaper signals first, batch the AF2-Multimer runs overnight, and budget per-100-designs
  GPU time in Week 6.
- **The fibril surface is a hard target.** Expect a lower per-backbone RFdiffusion hit rate than a
  typical globular target, and a **much lower** conformational-selective rate on top — that is normal.
- **Generate both paradigms at honest scale before filtering.** The head-to-head and the
  selective-fraction comparison only work if both pools are real-sized; resist filtering one early.
- This project follows the **binder-family template** (Project 06): the BindCraft/RFdiffusion-binder +
  AF2-Multimer + shared-filter workflow is shared; the addition is the conformational-specificity test.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (parameter sweeps, cross-amyloid
specificity, RFdiffusion noise exploration), `[stretch]` (Boltz-2 affinity scaffold; wet-lab go/no-go +
ThT-fibril check) to strong/MSc-track students.
