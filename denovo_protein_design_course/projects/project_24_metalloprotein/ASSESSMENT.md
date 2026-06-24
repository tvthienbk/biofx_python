# Project 24 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether the metalloprotein works.**
De novo cofactor-binding / metalloprotein design is a long-standing grand challenge and hit rates are
**low**, and **coordination-geometry preservation does not guarantee cofactor incorporation, let alone
function** — three caveats stack (geometry ≠ incorporation ≠ function; AF2 gives the apo backbone;
classical MD models the metal site poorly). A meticulous campaign that honestly reports a low hit
rate, a clean coordination-geometry-preservation analysis, a sound cofactor/scheme comparison, and a
rigorous **spectroscopic**-assay plan with the coordinating-residue→Ala and apo controls earns an A. A
single nice-looking bis-His pocket with no controls, no geometry accounting, and no hit-rate reporting
does not.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 24 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Correct cofactor/coordination understanding (e.g. bis-His heme, Fe–Nε2/angle) + measurable success criteria; honest hit-rate history; "geometry ≠ incorporation ≠ function" stated |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | cofactor-spec→scaffold→cofactor-aware LigandMPNN(coordinating residues fixed)→coordination-geometry runs end-to-end; seeds + tool versions logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | 1000s of backbones; coordinating residues provably fixed AND cofactor passed as atom context; full design log (config+seed+path) |
| Filtering, benchmarking & critical analysis | 20% | D3 | enzyme-cutoff filter (cat_geom = coordination geometry, plddt_cat = site confidence); coordination-geometry preservation rate; cofactor/scheme comparison; honest hit rate |
| Validation plan (controls, feasibility, cost) | 15% | D4 | UV-vis Soret (heme) / EPR (Fe-S) assay + cofactor titration; controls incl. coordinating-residue→Ala and apo protein; costed/timed; no fabricated spectra |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; "coordination geometry ≠ incorporation ≠ function" stated plainly |
| Oral defense | 10% | D5 | Can defend the coordination geometry, why LigandMPNN (not ProteinMPNN) is required, and own the campaign's limits |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable; correct cofactor/coordination understanding (scheme + Fe–ligand geometry) | Clear but generic | Vague | Absent / coordination chemistry wrong |
| Tool selection & justification | Reasoned (why **cofactor-aware** LigandMPNN fixes coordinating residues + passes the cofactor; why RFdiffusion2 vs Riff-Diff) | Correct, thin justification | No rationale | Wrong tools (e.g. cofactor-blind ProteinMPNN) |
| Computational execution | Complete; coordinating residues fixed; metal placed before scoring; multi-layer filter; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Honest hit rate + coordination-geometry preservation rate + "geometry ≠ incorporation ≠ function" + failure forensics | Some limitations noted | Superficial | None |
| Experimental plan | UV-vis Soret / EPR, cofactor titration, coordinating-residue→Ala + apo controls, costed, timed; no fabricated spectra | Reasonable, gaps | Vague | Absent / no controls |
| Communication | Clear prose, professional figures (survival funnel, coordination-geometry distribution, scheme comparison), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** 1-page problem statement (measurable criteria + controls) + printout of the
  reproduced cofactor-site hello-world (coordination-group spec + a mock scaffold record).
- **D1 (Wk 6):** repo link; minimal cofactor-spec→scaffold→LigandMPNN(coordinating fixed)→coordination-
  geometry pipeline on a small batch with the coordination-geometry RMSD computed; `LOG.md` started.
- **D2 (Wk 12):** full design pool (scaffolds + cofactor-aware sequences, coordinating residues fixed)
  + `design_log` (every config+seed+output) + 3–4 page interim report.
- **D3 (Wk 18):** `03`/`04` notebooks + figures: survival-at-each-layer, coordination-geometry
  preservation rate, cofactor/scheme comparison, ranked top candidates, honest hit-rate table.
- **D4 (Wk 22):** validation report (coordination geometry + cofactor docking + site pLDDT + caveated
  MD on the <96 set) + **spectroscopic**-assay plan (UV-vis Soret for heme / EPR for Fe-S; a cofactor
  titration) with controls (coordinating-residue→Ala mutant, apo protein, natural reference), costed +
  timed; **no fabricated spectra**.
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release with archived environment
  (+ redox-tuning reasoning for any hits) `[extension]`.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on the **mock
backend** and reproduce the survival-at-each-layer figure from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions + seeds in
the report, clearly mark every synthetic/`EXAMPLE_DATA` number as such, and **never present a mock
value or a fabricated spectrum as a real result.**
