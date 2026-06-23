# Project 12 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Biosensor architectures (allosteric/LOCKR switches + split-reporters); choose analyte (verify accession) + readout; reproduce the mock hello-world (binder → switch → ON/OFF) | **D0:** Problem statement + analyte/readout choice + reproduced hello-world |
| **P1 — Baseline** | 3–6 | Minimal binder pipeline (target → BindCraft/RFdiffusion mini-batch → ProteinMPNN → AF2-Multimer → metrics) + a first mock integration; repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft campaign (50–200) **and** RFdiffusion-binder campaign (500–1000 → ProteinMPNN); **switch module** (RFdiffusion scaffold + split-reporter and/or borrowed LOCKR cage); design log | **D2:** Binder pool + switch module + design log + interim report |
| **P3 — Filter & integrate** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on both binder pools; **integrate** binder + switch; ON/OFF two-state reasoning; switch-architecture benchmark; affinity-vs-dynamic-range | **D3:** Filtered binders + integrated constructs + ON/OFF + benchmark figures |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction; off-target specificity panel; costed **luminescence/FRET dose-response** + **LOD** plan with **no-analyte/blank** + **off-target** controls | **D4:** Validation report + costed, controlled functional-readout plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** A real binder campaign **plus** switch + two-state
  modeling wants an **A100** (Colab Pro+ or a cluster). Secure A100 access (or scope down to a
  FreeBindCraft/T4 fallback) **before Week 7** — don't discover the limit mid-campaign.
- **Two hard problems stack.** The binder must clear the binder bar *before* it is worth integrating;
  then coupling binding to a clean ON/OFF signal is its own design problem that **usually needs
  iteration** (linker, latch, reporter placement). Budget time for the integration loop, not just generation.
- **AF2-Multimer re-prediction + two-state modeling are the slow steps**, not generation. Triage with
  cheaper signals first, batch AF2 runs overnight, and budget per-100-designs + per-two-state GPU time.
- **Filter the binder pool at honest scale before integrating.** The switch-architecture benchmark and
  the affinity-vs-dynamic-range figure only work if the binder pool is real-sized; resist cherry-picking.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (RFdiffusion noise exploration, two-state
AF2 modeling, off-target panels), `[stretch]` (wet-lab go/no-go dose-response; multiplexing concept) to
strong/MSc-track students.
