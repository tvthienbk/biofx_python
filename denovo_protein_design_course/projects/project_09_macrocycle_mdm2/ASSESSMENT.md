# Project 09 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the peptide works.** A
peptide/macrocycle campaign with a meticulously reported **modest** hit rate, a fair
**linear-vs-cyclic** and **peptide-vs-protein** comparison, and a controlled **peptide-specific**
validation plan earns an A. A single "great-looking" macrocycle with no hit-rate accounting, no
controls, and a cherry-picked metric does not — no matter how low its `pae_interaction` or how high its
Boltz-2 score. **A design is a hypothesis; `pae_interaction` is not affinity; the Boltz-2 affinity
score is a relative rank, not a K_D; synthesis + binding + stability assays are mandatory.**

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 09 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Clear MDM2–p53 PPI-restoration motivation; cleft residues justified from the 1YCR interface (Phe19/Trp23/Leu26 sub-pockets); measurable success criteria + controls named upfront |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Peptide + macrocycle pipeline runs end-to-end on the mock backend; seeds + tool versions + commits logged; honest T4-vs-Pro scoping + BoltzGen-release verification |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Linear and macrocyclic pools generated at honest scale across a length/constraint sweep; mini-protein foil generated; every config + seed in the design log; no premature filtering |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter (`design_type="binder"`); survival-at-each-layer per modality; **linear-vs-cyclic** and **peptide-vs-protein** comparison; Boltz-2 used for ranking only; honest hit-rate accounting |
| Validation plan (controls, feasibility, cost) | 15% | D4 | **SPPS** synthesis + **protease-stability** + **permeability** assays (not E. coli); positive (known p53-peptide), **scrambled-sequence** negative, unrelated negative; costed reagents + timeline |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun on the mock backend |
| Oral defense | 10% | D5 | Can defend cleft choice, the linear-vs-cyclic / modality comparison, and the limits ("this is a hypothesis until synthesis + binding/stability assays; the Boltz-2 score is not a K_D") |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable criteria; cleft justified on the p53-mimetic pocket | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned BoltzGen vs EvoBind2 choice + why AF2/Boltz-2 + the mini-protein foil | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Both modalities at scale; multi-layer filter; reproducible; honest T4-vs-Pro scoping | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest hit rates + failure forensics + fair linear-vs-cyclic / peptide-vs-protein comparison + "affinity is unreliable" caveat | Some limitations noted | Superficial | None |
| Experimental plan | Detailed SPPS + protease-stability + permeability, controlled (incl. scrambled-sequence), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (survival funnels, modality distributions), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement (success criteria + controls) + cleaned MDM2 + cleft-residue
  list (from 1YCR) + screenshot of the reproduced mock mini-run.
- **D1 (Wk 6):** repo link; minimal pipeline demo (cleft → a few linear + cyclic designs → AF2/Boltz-2
  metrics); `LOG.md` started; version-verify output captured (incl. BoltzGen release check).
- **D2 (Wk 12):** `results/linear_designs.csv` + `results/macrocycle_designs.csv` (both pools, full
  config/seed log, length/constraint sweep) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: survival-at-each-layer per modality, **linear-vs-cyclic** and
  **peptide-vs-protein** comparison, ranked top candidates, cleft-engagement overlap, cyclization
  feasibility notes.
- **D4 (Wk 22):** validation report + **SPPS + protease-stability + permeability** plan with controls
  (incl. scrambled-sequence negative), synthesis strategy, costed reagent list + timeline.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock**
backend and reproduce the survival-funnel figure from the tagged release, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions, pinned commits, and seeds
in the report. **Mock numbers are `SYNTHETIC` and must never appear in the report as real results, and
no K_D is ever fabricated — the Boltz-2 affinity score is a relative rank only.**
