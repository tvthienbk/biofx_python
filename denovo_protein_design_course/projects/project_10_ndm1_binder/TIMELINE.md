# Project 10 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | AMR + metallo-β-lactamase literature; verify accessions (3SPU/4EYL); **di-zinc target prep (preserve both Zn²⁺)** + pick active-site-rim (occluding) hotspots; reproduce a mini-run (mock) | **D0:** Problem statement + di-zinc target prep + rim hotspots + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal binder pipeline (target → BindCraft/RFdiffusion mini-batch → **LigandMPNN** → AF2-Multimer → metrics); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft campaign (50–200) **and** RFdiffusion-binder campaign (500–1000 → **LigandMPNN**, Zn-aware) at the active-site rim; assemble both pools; design log | **D2:** Two-paradigm design pool + design log + interim report |
| **P3 — Filter, occlusion & specificity** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on both pools; **occlusion** modeling (substrate-access channel) + **specificity vs human metalloenzymes**; BindCraft-vs-RFdiffusion + rim-vs-distal ablation; top 10–20 each | **D3:** Ranked top candidates + occlusion + specificity + benchmark + filtering report |
| **P4 — Validate + plan inhibition** | 19–22 | Orthogonal re-prediction; occlusion footprint over the di-zinc site; (stretch) β-lactam-adjuvant / affinity scaffold; costed **nitrocefin/carbapenem inhibition (IC50)** plan with controls | **D4:** Validation report + costed, controlled inhibition-assay plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** A real campaign wants an **A100** (Colab Pro+ or
  a cluster). Secure A100 access (or scope down to a FreeBindCraft/T4 fallback) **before Week 7** —
  don't discover the limit mid-campaign.
- **Preserve the di-zinc site from Week 1.** Stripping the Zn²⁺ ions silently breaks the epitope and
  every downstream design; confirm both metals are retained before generating anything.
- **AF2-Multimer re-prediction of every design is the slow step**, not generation. Triage with cheaper
  signals first, batch the AF2-Multimer runs overnight, and budget per-100-designs GPU time in Week 6.
- **Generate both paradigms at honest scale before filtering.** The head-to-head and the rim-vs-distal
  ablation only work if BindCraft and RFdiffusion pools are both real-sized; resist filtering one early.
- **Binding ≠ inhibition.** Occlusion + specificity are in-silico *enrichment*; the IC50 comes only
  from the nb-05 nitrocefin/carbapenem kinetics assay. Never report an in-silico IC50.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (occlusion modeling, specificity panel,
rim-vs-distal ablation, RFdiffusion noise exploration), `[stretch]` (β-lactam-adjuvant checkerboard;
Boltz-2 affinity scaffold; wet-lab go/no-go + nitrocefin screen) to strong/MSc-track students.
