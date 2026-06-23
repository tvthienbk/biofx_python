# Project 21 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for
weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Serine-hydrolase mechanism + de novo enzyme literature; verify accessions; build the triad + oxyanion-hole theozyme spec; reproduce the mock hello-world | **D0:** Problem statement + reproduced theozyme hello-world |
| **P1 — Baseline** | 3–6 | Finalise the theozyme (Ser-His-Asp triad + oxyanion hole + ester-TS geometry); small RFdiffusion scaffolding demo + LigandMPNN (triad fixed); first catalytic-geometry RMSD + a pocket check | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Scaffold 1000s of backbones (RFdiffusion2 / Riff-Diff, A100); LigandMPNN sequence design fixing the triad + oxyanion-hole donors; AF2/ESMFold triage | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | `filtering_pipeline` (enzyme): scrmsd/plddt/plddt_cat/cat_geom; catalytic-geometry preservation rate; scaffolding-method comparison; pocket accessibility (docking) + substrate-scope scan + MD | **D3:** Ranked candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Confirm triad geometry on the <96 set (geometry + docking + MD + scope); write the pNP-ester kinetic-assay + DSF plan with controls (incl. catalytic-Ser→Ala dead mutant) | **D4:** Validation report + costed kinetic-assay plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release; enantioselectivity / kinetic-resolution plan for hits | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Scaffolding (Weeks 7–8) is the compute bottleneck and the real risk.** RFdiffusion2 / Riff-Diff on
  1000s of backbones wants an **A100** (Colab Pro+ or HPC); verify the current release early and pin it.
  Free Colab T4 can only do a **small RFdiffusion motif-scaffolding demo** — plan batch sizes around
  that and reserve A100 time in advance.
- **LigandMPNN (Weeks 9–10) is cheap** (CPU-fast) — the expensive part is upstream. The only thing that
  must be right here is the **fixed-positions list** (Ser, His, Asp **and both oxyanion-hole donors**)
  and the ligand/TS context, or you redesign away your active site.
- **The catalytic-geometry layer (Weeks 13–16) is where most designs die** — expect the steepest drop in
  the survival funnel there. Then the **pocket-accessibility** check (Weeks 17–18) culls geometrically-
  perfect-but-buried triads. Budget time to inspect *why* (motif not held vs atom-mapping error vs
  closed pocket).
- **Theozyme construction (Weeks 1–4) is background work** — start filling `data/inputs/theozyme_def.txt`
  in Week 1; the placeholder geometry (including the easily-forgotten **oxyanion hole**) must become
  real, cited values before the campaign.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` (scaffolding-method comparison, pocket/substrate-
scope analysis, deeper in-silico validation) to most, `[stretch]` (enantioselectivity / kinetic-
resolution plan, wet-lab go/no-go execution) to strong/MSc-track students.
