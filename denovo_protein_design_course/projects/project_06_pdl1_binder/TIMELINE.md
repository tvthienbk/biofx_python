# Project 06 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Checkpoint-blockade + binder literature; verify accessions (4ZQK/5O45); clean PD-L1 + pick PD-1-face hotspots; reproduce a BindCraft mini-run (mock) | **D0:** Problem statement + target prep + hotspots + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal binder pipeline (target → BindCraft/RFdiffusion mini-batch → ProteinMPNN → AF2-Multimer → metrics); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft campaign (50–200) **and** RFdiffusion-binder campaign (500–1000 → ProteinMPNN); assemble both pools; design log | **D2:** Two-paradigm design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on both pools; BindCraft-vs-RFdiffusion hit rate / interface energy / novelty; top 10–20 each; epitope-competition vs PD-1 | **D3:** Ranked top candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction; PD-1-competition footprint analysis; (stretch) Boltz-2 affinity scaffold; costed SPR/BLI + PD-1-competition plan with controls | **D4:** Validation report + costed, controlled experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** A real campaign wants an **A100** (Colab Pro+ or
  a cluster). Secure A100 access (or scope down to a FreeBindCraft/T4 fallback) **before Week 7** —
  don't discover the limit mid-campaign.
- **AF2-Multimer re-prediction of every design is the slow step**, not generation. Triage with cheaper
  signals first, batch the AF2-Multimer runs overnight, and budget per-100-designs GPU time in Week 6.
- **Generate both paradigms at honest scale before filtering.** The head-to-head only works if
  BindCraft and RFdiffusion pools are both real-sized; resist filtering one early.
- This project is the **binder-family template** (Projects 07–13, 23): keep the workflow clean and
  documented so the rest of the family can reuse it.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (parameter sweeps, epitope-competition,
RFdiffusion noise exploration), `[stretch]` (Boltz-2 affinity scaffold; wet-lab go/no-go tier) to
strong/MSc-track students.
