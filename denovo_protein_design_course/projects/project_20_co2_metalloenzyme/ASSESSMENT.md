# Project 20 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the enzyme works.** De
novo **metalloenzyme** hit rates are low (GRACE reached functional CA-style designs only via a large
pool + screening), and **metal geometry does not guarantee activity — nor that the metal even binds**.
A meticulous campaign that honestly reports a low hit rate, a clean metal-geometry-preservation
analysis, a sound **LigandMPNN-vs-ProteinMPNN** and **pool-size-vs-hit-rate** benchmark, and a
rigorous activity + **metal-incorporation** assay plan with the **apo** and **natural-CA** controls
earns an A. A single nice-looking design with no controls, no geometry/metal accounting, and no
hit-rate reporting does not.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 20 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Correct CA mechanism (Zn-OH nucleophile) + metal-site reasoning; measurable success criteria; honest GRACE hit-rate story |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | theozyme→scaffold→**metal-aware** LigandMPNN(His₃ fixed, Zn context)→metal geometry runs end-to-end; seeds + tool versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | a large pool (toward ~10k); His₃ ligands provably fixed + Zn in context; ProteinMPNN baseline generated; full design log (config+seed+path) |
| Filtering, benchmarking & critical analysis | 20% | D3 | enzyme-cutoff filter + solubility + CLEAN-style class; metal-geometry preservation rate; **LigandMPNN vs ProteinMPNN**; **pool-size vs hit-rate**; honest hit rate |
| Validation plan (controls, feasibility, cost) | 15% | D4 | pNPA / Wilbur-Anderson activity + **ICP metal-incorporation** check; controls incl. **apo** + His→Ala knockout + natural CA + blank; costed/timed; Co(II) substitution `[stretch]` |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; "geometry ≠ metal incorporation ≠ activity" stated plainly; metal-MD caveat owned |
| Oral defense | 10% | D5 | Can defend the metal-site geometry, why LigandMPNN (not ProteinMPNN), and own the campaign's limits |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable; correct CA / Zn-OH mechanism + metal-site reasoning | Clear but generic | Vague | Absent / mechanism wrong |
| Tool selection & justification | Reasoned (why metal-aware LigandMPNN over ProteinMPNN; why RFdiffusion2 vs Riff-Diff; metal-MD model choice) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete; His₃ fixed + Zn context; multi-layer filter incl. metal geometry; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest hit rate + metal-geometry-preservation rate + "geometry ≠ incorporation ≠ activity" + metal-FF caveat + failure forensics | Some limitations noted | Superficial | None |
| Experimental plan | pNPA/WA activity, **ICP metal check**, apo + His→Ala + natural-CA + blank controls, costed, timed | Reasonable, gaps | Vague | Absent / no controls |
| Communication | Clear prose, professional figures (survival funnel, metal-geometry distribution, LigandMPNN-vs-ProteinMPNN, pool-size-vs-hit-rate), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** 1-page problem statement (measurable criteria + controls) + printout of the
  reproduced metal-site theozyme hello-world (Zn-His₃-OH spec + a mock scaffold record).
- **D1 (Wk 6):** repo link; minimal theozyme→scaffold→metal-aware-LigandMPNN(His₃ fixed)→metal-geometry
  pipeline on a small batch with metal-ligand geometry computed; `LOG.md` started.
- **D2 (Wk 12):** full design pool (scaffolds + metal-aware sequences with His₃ fixed + ProteinMPNN
  baseline) + `design_log` (every config+seed+output) + 3–4 page interim report.
- **D3 (Wk 18):** `03`/`04` notebooks + figures: survival-at-each-layer, metal-geometry preservation
  rate, **LigandMPNN-vs-ProteinMPNN**, **pool-size-vs-hit-rate**, ranked top candidates, honest
  hit-rate table.
- **D4 (Wk 22):** validation report (geometry + CLEAN + caveated MD on the <96 set) + activity +
  metal-incorporation assay plan (pNPA / Wilbur-Anderson + ICP) with controls (apo, His→Ala, natural
  CA, blank), costed + timed; Co(II) substitution plan `[stretch]`.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment
  (+ Co-substitution / evolution plan for hits).

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock
backend** and reproduce the survival-at-each-layer figure from the tagged release, the reproducibility
components are capped at "Adequate" until fixed. State exact tool versions + seeds + your metal-site MD
model in the report, and clearly mark every synthetic/`EXAMPLE_DATA` number as such.
