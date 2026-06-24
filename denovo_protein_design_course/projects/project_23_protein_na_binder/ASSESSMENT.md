# Project 23 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the binder works.** A
campaign with a meticulously reported **low specificity rate**, a fair LigandMPNN-vs-ProteinMPNN
comparison, and a controlled EMSA/anisotropy plan earns an A. A single "great-looking" design with no
hit-rate accounting, no controls, and a cherry-picked `pae_interaction` does not — no matter how
confident the model. **A design is a hypothesis; `pae_interaction` is confidence (not affinity); the
computational specificity score is a proxy (not a measured ΔΔG); EMSA / fluorescence-anisotropy with a
scrambled-NA control is mandatory; and no K_D is fabricated.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 23 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear gene-editing-modulator / RNA-therapeutic / synthetic-TF motivation; a **justified DNA/RNA target motif**; measurable success criteria + controls (incl. scrambled-NA) named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Scaffold→LigandMPNN→complex-model pipeline runs end-to-end; seeds + tool versions + commits logged; honest A100-vs-T4 scoping; LigandMPNN NA-model + RFdiffusion NA-protocol verified |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Backbones scaffolded near the NA at honest scale; **LigandMPNN (NA-aware) + ProteinMPNN (NA-blind) on the same backbones**; every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`) + **specificity gate** on both pools; survival per designer; **LigandMPNN-vs-ProteinMPNN** confidence **and** specificity rates; intended-vs-scrambled specificity analysis; honest **two-number** hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | **EMSA / fluorescence-anisotropy** assay; **scrambled-NA** negative (required) + **dead-mutant** + unrelated + positive; expression strategy; costed reagents (incl. labeled + scrambled oligos) + timeline; no fabricated K_D |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend the motif choice, why LigandMPNN over ProteinMPNN, and the limits ("confident ≠ specific; this is a hypothesis until EMSA") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; motif justified; specificity framed as the central challenge | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned LigandMPNN-over-ProteinMPNN choice + why Boltz-2 for protein–NA | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Both designers at scale on shared backbones; multi-layer filter + specificity gate; reproducible; honest compute scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest **two** hit rates + failure forensics (non-specific gripping) + fair head-to-head + confidence-vs-specificity reasoning | Some limitations noted | Superficial | None |
| Experimental plan | Detailed EMSA/anisotropy, controlled (incl. **scrambled-NA** + dead-mutant), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnel, head-to-head, specificity scatter), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria + controls) + chosen DNA/RNA motif (+ its
  scrambled control) + screenshot of the reproduced mock mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (motif → a few designs → complex model → metrics +
  specificity); `LOG.md` started; version-verify output captured (incl. NA-model/NA-protocol checks).
- **D2 (Wk 12):** `results/ligandmpnn_designs.csv` + `results/proteinmpnn_designs.csv` (both pools on the
  same backbones, full config/seed log) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per designer, the **specificity gate**
  drop, LigandMPNN-vs-ProteinMPNN confidence **and** specificity rates, the intended-vs-scrambled
  scatter, ranked top confident+specific candidates.
- **D4 (Wk 22):** validation report + **EMSA / fluorescence-anisotropy** plan with controls (incl.
  **scrambled-NA** + dead-mutant), expression strategy, costed reagent list (labeled + scrambled
  oligos) + timeline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock**
backend and reproduce the survival-funnel + specificity-gate output from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions, pinned
commits, and seeds in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as
real results, and no K_D is fabricated.**
