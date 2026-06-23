# Project 20 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with
this project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md`
for weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | CA mechanism + de novo metalloenzyme / GRACE literature; verify accessions; build the Zn-His₃-OH metal-site spec; reproduce the mock hello-world | **D0:** Problem statement + reproduced metal-site theozyme hello-world |
| **P1 — Baseline** | 3–6 | Finalise the metal site (Zn + His₃ ligands + Zn-hydroxide + geometry); small RFdiffusion scaffolding demo + **metal-aware** LigandMPNN (His₃ fixed, Zn context); first metal-ligand geometry | **D1:** Working minimal pipeline + first batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | Scaffold a **large pool** (~10k; RFdiffusion2 / Riff-Diff, A100); metal-aware LigandMPNN fixing the His₃ ligands + a ProteinMPNN baseline; AF2/ESMFold triage; CLEAN-style classification + solubility | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | `filtering_pipeline` (enzyme): scrmsd/plddt/plddt_cat/cat_geom(=metal-ligand) + solubility + CLEAN; **LigandMPNN-vs-ProteinMPNN** + **pool-size-vs-hit-rate**; docking + caveated MD | **D3:** Ranked candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | Confirm metal geometry on the <96 set (geometry + CLEAN + MD); write the activity + **metal-incorporation** assay plan with controls (apo, natural CA); Co(II) substitution `[stretch]` | **D4:** Validation report + costed assay plan |
| **P5 — Synthesize** | 23–24 | Thesis chapter; tagged reproducible release; Co-substitution / evolution plan for hits | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Scaffolding (Weeks 7–8) is the compute bottleneck and the real risk.** A **large metal-motif pool**
  (GRACE used ~10k) with RFdiffusion2 / Riff-Diff wants an **A100** (Colab Pro+ or HPC); verify the
  current release early and pin it. Free Colab T4 can only do a **small RFdiffusion metal-motif demo** —
  plan batch sizes around that and reserve A100 time in advance. Metal-site placement is harder than a
  sidechain motif, so budget extra backbones.
- **Metal-aware LigandMPNN (Weeks 9–10) is cheap** (CPU-fast) — the expensive part is upstream. The
  things that must be right here: the **fixed-positions list** (all three His ligands) and the **Zn
  atom context** (`--ligand_mpnn_use_atom_context 1`), or you redesign away / mis-pack the metal site.
- **The metal-geometry layer (Weeks 13–16) is where most designs die** — expect the steepest drop in
  the survival funnel there. Remember **AF2 does not place the Zn**, so build the metal in before
  scoring. Budget time to inspect *why* (cage not held vs atom-mapping error).
- **Metal-site MD (Weeks 17–18) is a weak, caveated proxy** — classical fixed-charge FFs model a
  coordinated metal poorly. Decide your metal model (bonded/dummy) and cite it; never treat MD as
  evidence of catalysis.
- **Metal-site construction (Weeks 1–4) is background work** — start filling
  `data/inputs/metal_site_def.txt` from a verified CA structure in Week 1; the placeholder geometry
  must become real, cited Zn-N distances / N-Zn-N angles before the campaign.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` (LigandMPNN-vs-ProteinMPNN and pool-size-vs-hit-rate
benchmarks, parameter exploration, deeper in-silico validation) to most, `[stretch]` (Co(II)-substitution
test, wet-lab go/no-go execution, directed evolution) to strong/MSc-track students.
