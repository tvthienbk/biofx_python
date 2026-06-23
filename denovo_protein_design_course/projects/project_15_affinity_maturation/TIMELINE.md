# Project 15 — Timeline (24 weeks)

Six fixed phases (shared across all 25 projects so cohorts stay synchronized), instantiated with this
project's specific tasks. Milestones D0–D5 are the graded deliverables. See `ASSESSMENT.md` for
weighting and `INSTRUCTIONS.md` for the week-by-week detail.

| Phase | Weeks | This project's focus | Milestone |
|-------|-------|----------------------|-----------|
| **P0 — Orient** | 1–2 | affinity-maturation + developability theory; **pick** a SAbDab complex (measured KD); identify CDR contacts; reproduce the mock hello-world | **D0:** Problem statement (complex + measured KD + CDR contacts) + reproduced hello-world |
| **P1 — Baseline** | 3–6 | clean the complex + compute paratope + fix framework; full mock pipeline; a tiny real ESM-1v/AbLang/MPNN demo + one AF2 pose check | **D1:** Working minimal maturation pipeline + first scored batch + repo + `LOG.md` |
| **P2 — Campaign** | 7–12 | score single CDR mutations (ESM-1v ensemble + AbLang); ProteinMPNN CDR redesigns (framework fixed) → `campaign.csv` | **D2:** Candidate mutation set + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | antibody filter (`design_type="antibody"`, pose maintenance via batched AF2-Multimer); ESM-1v/AbLang/MPNN agreement; developability + epistasis figures | **D3:** Ranked candidates + benchmark figures + filtering report |
| **P4 — Validate + plan** | 19–22 | specificity/pose deepening; SPR-kinetics + DSF plan + controls (WT + destabilizing decoy + specificity panel) + costed plan | **D4:** Validation report + SPR/DSF plan |
| **P5 — Synthesize** | 23–24 | thesis chapter; tagged reproducible release | **D5:** Thesis + 15-min talk + `v1.0` release |

### Critical-path notes
- **Scoring is light; AF2-Multimer is the bottleneck.** ESM-1v/AbLang/ProteinMPNN run on a free T4
  (CPU-OK) — do them broadly and early. The **pose check is the heavy step**: keep N small, pose-check
  only the *scored survivors*, and **batch overnight**. That is why the realistic tier is **T4–Pro**.
- **The complex + its measured KD (P0) gate everything.** Pick a SAbDab complex WITH a published KD,
  verify the accession, and read the CDR contacts off the *verified* structure. The KD is your baseline;
  never invent one. Don't rush this.
- **The deliverable is a SMALL ranked set + the experiment.** Computational maturation ranks; most
  predicted improvers do not validate. Plan the SPR/DSF experiment (P4) as a real deliverable with
  controls (WT + decoy + specificity panel), not an afterthought.
- This project follows the **antibody-family template** (Project 17): keep `maturation_tools.py`, the
  notebook flow, and the `design_type="antibody"` filter hand-off clean.

### Instructor scaling knob
Assign all `[core]` tasks to everyone, `[extension]` to most (ESM-1v vs AbLang vs ProteinMPNN agreement;
ProteinMPNN parameter exploration; specificity/pose deepening), `[stretch]` (a combinatorial-block +
epistasis read-out) to strong/MSc-track students.
