# Project 24 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for
weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | De novo metalloprotein literature; coordination chemistry; choose cofactor + scheme (default bis-His heme); verify accessions; reproduce the mock hello-world | **D0:** Problem statement + reproduced cofactor-site hello-world |
| **P1 — Baseline** | 3–6 | Finalise the cofactor-site spec (coordinating residues + metal-ligand geometry from a verified reference); small RFdiffusion scaffolding demo + cofactor-aware LigandMPNN (coordinating residues fixed); first coordination-geometry RMSD | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Scaffold 1000s of backbones (RFdiffusion2 / Riff-Diff, A100); cofactor-aware LigandMPNN fixing coordinating residues + passing the cofactor as context; AF2/ESMFold triage (site pLDDT) | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | `filtering_pipeline` (enzyme): scrmsd/plddt/plddt_cat(site)/cat_geom(coordination); coordination-geometry preservation rate; cofactor/scheme comparison; cofactor docking + caveated MD | **D3:** Ranked candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Confirm coordination geometry on the <96 set (geometry + docking + site pLDDT + MD); redox-tuning reasoning; write the UV-vis Soret / EPR assay plan + cofactor titration with controls (apo, coordinating-residue→Ala) | **D4:** Validation report + costed spectroscopic-assay plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release; redox-tuning / function-engineering plan for hits | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Scaffolding (Weeks 7–8) is the compute bottleneck and the real risk.** RFdiffusion2 / Riff-Diff on
  1000s of backbones wants an **A100** (Colab Pro+ or HPC); verify the current release early and pin it.
  Free Colab T4 can only do a **small RFdiffusion motif-scaffolding demo** — plan batch sizes around
  that and reserve A100 time in advance. Cofactor-pocket placement (e.g. two axial His on opposite
  helices at the right Fe distance) is harder than a single-sidechain motif — budget extra backbones.
- **Cofactor-aware LigandMPNN (Weeks 9–10) is cheap** (CPU-fast) — the expensive part is upstream. The
  only things that must be right here are the **fixed-positions list** (every coordinating residue) and
  **passing the cofactor as atom context**, or you redesign away your coordination site.
- **The coordination-geometry layer (Weeks 13–16) is where most designs die** — expect the steepest
  drop in the survival funnel there. Budget time to inspect *why* (motif not held vs atom-mapping/metal-
  placement error; remember AF2 gives the apo backbone).
- **Cofactor-site spec construction (Weeks 1–4) is background work** — start filling
  `data/inputs/cofactor_site_def.txt` in Week 1; the placeholder geometry must become real, cited values
  (read off a verified reference structure) before the campaign.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` (cofactor/scheme comparison, parameter exploration,
deeper in-silico validation, redox-tuning reasoning) to most, `[stretch]` (redox-tuning/function-
engineering plan, wet-lab go/no-go + spectroscopy execution) to strong/MSc-track students.
