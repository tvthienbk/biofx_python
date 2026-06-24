# Project 13 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Cytokine-signaling + de novo mimetic literature; verify accessions (2B5I); **choose target subunits + desired selectivity** (e.g., βγ-biased, spare α); separate the receptor subunits + per-subunit hotspots; reproduce a mini-run (mock) | **D0:** Problem statement + subunit/selectivity choice + reproduced mini-run |
| **P1 — Baseline** | 3–6 | Minimal agonist pipeline (target → RFdiffusion/BindCraft mini-batch → ProteinMPNN → AF2-Multimer **per subunit** → metrics); repo + `LOG.md` | **D1:** Working minimal pipeline + first design batch + repo |
| **P2 — Campaign** | 7–12 | Agonist campaign engaging the chosen surfaces (RFdiffusion-binder 500–1000 → ProteinMPNN, and/or BindCraft 50–200); AF2-Multimer **vs each of α/β/γc**; assemble pool with per-subunit metrics; design log | **D2:** Agonist design pool (per-subunit metrics) + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Shared 4-layer filter (`design_type="binder"`) on engaged subunits; **subunit-selectivity profile** (engages βγ but NOT α) + selectivity margin; **stability vs native cytokine**; top candidates | **D3:** Ranked top candidates + selectivity profile + stability figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Orthogonal re-prediction; selectivity-margin analysis; (stretch) Boltz-2 affinity per subunit + thermostability proxy; costed **per-subunit SPR + cell STAT-phosphorylation** plan with controls | **D4:** Validation report + costed, controlled per-subunit SPR + signaling plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; 15-min talk; `v1.0` tagged reproducible release | **D5:** Thesis + talk + release |

### Critical-path notes
- **Compute is the bottleneck, and it is not free.** A real campaign wants an **A100** (Colab Pro+ or a
  cluster). Secure A100 access (or scope down to a FreeBindCraft/T4 fallback) **before Week 7**.
- **Modeling against three subunits ~triples the AF2-Multimer cost** — the slow step. Triage on the
  engaged chains (β, γc) first; only model α for designs that already pass on β/γc; batch overnight.
- **Selectivity is the deliverable, not a single interface.** Don't filter on one subunit and stop —
  the per-subunit profile (engages βγ, spares α) is what makes this a *study*.
- **Binding ≠ signaling.** Keep the cell pSTAT5 assay central to the D4 plan; an in-silico selective
  binder is a hypothesis until it triggers STAT5.
- This project follows the **binder-family template** (Project 06); its twist is **subunit
  selectivity** — keep that workflow clean.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (parameter sweeps, selectivity-margin
analysis, stability comparison), `[stretch]` (Boltz-2 affinity scaffold; thermostability proxy + DSF;
wet-lab go/no-go tier) to strong/MSc-track students.
