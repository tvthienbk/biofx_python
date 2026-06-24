# Project 23 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Protein–NA recognition + LigandMPNN-NA literature; verify the protein–NA complex accession; **choose a DNA/RNA target motif** (+ scrambled control); reproduce a mock mini-run | **D0:** Problem statement + chosen motif + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal NA-binder pipeline (motif → RFdiffusion-near-NA → LigandMPNN → Boltz-2 complex model → metrics + specificity); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | RFdiffusion scaffolds near the NA (hundreds on A100) → **LigandMPNN (NA-aware)** design (+ **ProteinMPNN** NA-blind baseline on the same backbones) → complex modeling + specificity; assemble both pools; design log | **D2:** Scaffold+LigandMPNN design pool + baseline + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`) + **specificity gate** on both pools; **LigandMPNN-vs-ProteinMPNN** confidence rate / **specificity rate** / scatter; top confident+specific candidates | **D3:** Ranked candidates + benchmark + specificity figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-modeling; specificity analysis; (extension) CRISPR-modulator framing; costed **EMSA / fluorescence-anisotropy** plan with **scrambled-NA** + dead-mutant controls | **D4:** Validation report + costed, controlled experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** **RFdiffusion-near-NA** and **protein–NA complex
  modeling** want an **A100** (Colab Pro+ or a cluster); **LigandMPNN/ProteinMPNN are CPU-cheap**.
  Secure A100 access (or scope down to a T4 fallback) **before Week 7**.
- **Complex modeling (Boltz-2 / AF3-style) of every design is the slow step**, not sequence design.
  Triage with cheaper signals first; batch the modeling overnight; budget per-100-models GPU time in
  Week 6.
- **Specificity, not confidence, is the deliverable.** Generate the LigandMPNN and ProteinMPNN pools at
  honest scale on the *same* backbones, filter and gate both identically, and report the **two** hit
  rates (confidence + confident-AND-specific). Resist cherry-picking a confident-but-non-specific design.
- **Verify the evolving NA tooling.** LigandMPNN's nucleic-acid model and RFdiffusion's NA protocol
  change — the version-verify cell + a Week-3 check are on the critical path.
- This project follows the **binder-family template** (`project_06_pdl1_binder`); the differences are the
  nucleic-acid target, LigandMPNN, the specificity gate, and the EMSA/anisotropy assay.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (ProteinMPNN baseline + benchmark, novelty,
CRISPR-modulator framing, noise/temperature sweeps), `[stretch]` (CRISPR-modulator validation; wet-lab
go/no-go tier) to strong/MSc-track students.
