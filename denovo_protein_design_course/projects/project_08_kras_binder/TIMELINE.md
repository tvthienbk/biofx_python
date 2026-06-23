# Project 08 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for
weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | KRAS druggability + binder literature; verify accessions (4OBE/6OIM + HRAS/NRAS); choose **epitope/allele/nucleotide state**; clean KRAS; pick switch I/II (or allele-pocket) hotspots; reproduce a mock mini-run | **D0:** Problem statement + epitope/allele/state choice + target prep + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal binder pipeline (target → BindCraft/RFdiffusion mini-batch → ProteinMPNN → AF2-Multimer → metrics + first mock isoform panel); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | BindCraft campaign (50–200) **and** RFdiffusion-binder campaign (500–1000 → ProteinMPNN) at the chosen surface; assemble both pools (tagged by paradigm/allele/state); design log | **D2:** Two-paradigm design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on both pools; BindCraft-vs-RFdiffusion hit rate / interface energy / novelty; **isoform-specificity analysis (KRAS vs HRAS/NRAS, selectivity gap)**; allele-selectivity + effector-competition reasoning; top 10–20 each | **D3:** Ranked top candidates + benchmark figures + isoform-specificity analysis + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction; finalize isoform panel + effector-competition footprint; (stretch) Boltz-2 affinity scaffold; costed SPR/BLI + **isoform-specificity panel** + nucleotide-state test + controls | **D4:** Validation report + costed, controlled experimental plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** A real campaign wants an **A100** (Colab Pro+ or a
  cluster). Secure A100 access (or scope down to a FreeBindCraft/T4 fallback) **before Week 7** — don't
  discover the limit mid-campaign.
- **AF2-Multimer is the slow step, and the isoform panel multiplies it by ~3** (KRAS + HRAS + NRAS per
  survivor). Triage with cheaper signals first, batch the AF2-Multimer runs overnight, and budget per-100
  GPU time (including the panel) in Week 6.
- **Nail the nucleotide state and the epitope before generating.** The switch surface only exists in one
  state; designing against the wrong state (or a conserved patch) wastes the whole campaign.
- **Selectivity is the deliverable, not just binding.** Run the isoform panel on survivors and report the
  gap honestly — a pan-RAS binder is a weaker result than a selective one.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (parameter/epitope sweeps, the
isoform-specificity analysis, effector-competition reasoning), `[stretch]` (Boltz-2 affinity scaffold;
nucleotide-state-dependence experiment design; wet-lab go/no-go tier) to strong/MSc-track students.
