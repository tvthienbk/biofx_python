# Project 09 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | PPI + peptide-therapeutic literature; verify accession (1YCR); clean MDM2 + define the p53-binding cleft (Phe19/Trp23/Leu26 sub-pockets); reproduce a peptide-design mini-run (mock) | **D0:** Problem statement + cleft prep + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal peptide pipeline (cleft → linear/macrocyclic mini-batch → AF2/Boltz-2 pAE → metrics); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | Linear peptide campaign **and** macrocyclic campaign (vary length / cyclization constraint); assemble both pools; design log | **D2:** Linear + macrocyclic pools + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`); Boltz-2 affinity (ranking only) + AF2 pAE; **linear-vs-cyclic** and **peptide-vs-protein** (mini-binder foil) comparisons; cyclization-feasibility notes | **D3:** Ranked top candidates + modality figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction; cleft-engagement footprint analysis; **peptide** validation plan — SPPS + protease-stability + permeability (NOT just E. coli), controls; D-amino-acid / stapling stretch | **D4:** Validation report + costed, controlled SPPS/stability/permeability plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is modest but honest about the macrocycle arm.** Peptides are small, so AF2/Boltz-2
  scoring and **Boltz-2 affinity on small inputs run on a free T4**; a **full macrocycle campaign
  prefers Colab Pro**. Decide your T4-vs-Pro plan **before Week 7** — and verify the **BoltzGen public
  release** exists (the version-verify cell) before relying on it; that interface is moving.
- **Predicted affinity is unreliable for short peptides — rank, don't trust.** Treat the Boltz-2
  affinity score as a *relative* prioritization signal, never a K_D. This shapes both the filter and
  the validation plan (you test many; you do not believe an absolute number).
- **Generate both modalities at honest scale before filtering.** The linear-vs-cyclic and
  peptide-vs-protein comparisons only work if the linear, macrocyclic, and mini-protein-foil pools are
  all real-sized; resist filtering one early.
- **Validation is peptide-specific, not E. coli.** Peptides are made by **SPPS** and need
  **protease-stability and permeability** assays — budget that into P4, do not copy a mini-binder
  expression plan.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (length/constraint sweeps, the
mini-protein-foil modality comparison, cyclization-chemistry feasibility notes), `[stretch]`
(D-amino-acid / stapling chemistry; wet-lab go/no-go synthesis) to strong/MSc-track students.
