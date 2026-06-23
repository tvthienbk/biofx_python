# Project 19 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | Serine-hydrolase/PETase mechanism + the thermostability bottleneck; verify accessions (6EQE/5XJH); build the triad+oxyanion theozyme spec; reproduce the mock hello-world | **D0:** Problem statement + reproduced theozyme hello-world |
| **P1 — Baseline** | 3–6 | Finalise the theozyme (Ser-His-Asp triad + oxyanion hole + ester-TS geometry); small RFdiffusion scaffolding demo + LigandMPNN (triad fixed); first catalytic-geometry RMSD + thermostability proxy | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Scaffold 1000s of backbones into stable folds (RFdiffusion2 / Riff-Diff, A100); LigandMPNN sequence design fixing the triad; AF2/ESMFold triage; optional engineered-natural track | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | `filtering_pipeline` (enzyme): scrmsd/plddt/plddt_cat/cat_geom; **MD-thermostability ranking** (RMSF, melting-proxy); engineered-natural-vs-de-novo comparison; PET-mimic pocket docking | **D3:** Ranked candidates + thermostability benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Confirm geometry + thermostability on the <96 set (geometry + MD + docking); write the activity (pNP-ester/PET-film+HPLC) + DSF plan with controls (incl. catalytic-Ser→Ala dead mutant) | **D4:** Validation report + costed activity + DSF assay plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release; surface-redesign-for-solubility (and optional directed-evolution) plan for hits | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Scaffolding (Weeks 7–8) is the compute bottleneck and the real risk.** RFdiffusion2 / Riff-Diff
  on 1000s of backbones wants an **A100** (Colab Pro+ or HPC); verify the current release early and
  pin it. Free Colab T4 can only do a **small RFdiffusion motif-scaffolding demo** — plan batch sizes
  around that and reserve A100 time in advance.
- **The thermostability-MD ranking (Weeks 15–16) is the second compute load** and the project's
  headline. Short triage MD runs on small systems are T4-feasible, but the production ranking
  (longer / replica / elevated-temperature runs over many survivors) wants **A100/HPC**. It is a
  **proxy, not a Tm** — budget time and state that limit plainly.
- **LigandMPNN (Weeks 9–10) is cheap** (CPU-fast) — the expensive part is upstream. The only thing
  that must be right here is the **fixed-positions list** (Ser, His, Asp **and** the oxyanion-hole
  residues) and the ester/TS context, or you redesign away your active site.
- **The catalytic-geometry layer (Weeks 13–14) is where most designs die** — expect the steepest drop
  in the survival funnel there; then the **thermostability ranking** thins the survivors further.
- **Theozyme construction (Weeks 1–4) is background work** — start filling `data/inputs/theozyme_def.txt`
  in Week 1; the placeholder geometry must become real, cited values before the campaign.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` (engineered-natural-vs-de-novo comparison,
scaffolding-parameter exploration, deeper in-silico validation) to most, `[stretch]`
(surface-residue solubility redesign, directed-evolution plan, wet-lab go/no-go) to strong/MSc-track
students.
