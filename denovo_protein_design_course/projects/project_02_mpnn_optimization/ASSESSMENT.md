# Project 02 — Assessment

Instantiated from the shared rubric (`MASTER_BLUEPRINT.md §5`). Same six criteria the field uses;
weighting may be adjusted by the instructor.

## Grading philosophy (read this first)
You are graded on **rigor, reasoning, and reproducibility — not on whether any protein works.**
This is a sequence-design tooling project: a meticulous sweep that *honestly maps* the Pareto
trade-off and states "no single setting is best, here is the cheat-sheet and where it fails" earns an
A. A report that declares one "optimal" setting with no diversity/solubility accounting, no
per-setting hit rate, and no honest statement that solubility proxies are not expression does not —
no matter how clean it looks. **Never fabricate expression results;** any example distributions in
notebooks must be labeled `EXAMPLE_DATA`.

## Weighting (mapped to deliverables)
| Component | Weight | Deliverable | What "excellent" looks like for Project 02 |
|-----------|--------|-------------|--------------------------------------------|
| Problem definition & literature | 10% | D0 | Trade-off framed precisely; metrics table states what each metric does **not** mean (recovery ≠ quality; proxy ≠ expression) |
| Pipeline execution & reproducibility | 20% | D1–D3, repo | Backbone → MPNN → recapitulation → recovery runs end-to-end; seeds + tool versions + commit pins logged |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 | Full grid swept across 20–30 backbones; every setting on every row of `sequences.csv`; diversity reported, not just recovery |
| Filtering, benchmarking & critical analysis | 20% | D3 | Shared filter run (monomer); per-setting recovery/recapitulation/diversity/solubility; **Pareto-optimal settings** identified; honest per-setting hit rate |
| Validation plan (controls, feasibility, cost) | 15% | D4 | Codon/tag strategy + express→SDS-PAGE→SEC→DSF/CD plan; controls incl. the high-hydrophobic-patch negative; costed + timed |
| Final report & reproducible release | 10% | D5 | Thesis-quality; `v1.0` tag others can rerun; the cheat-sheet is usable |
| Oral defense | 10% | D5 | Can defend the trade-off, the Pareto choices, and the limits of the solubility proxies |

## Rubric (applied to the final report)
| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, measurable trade-off criteria; correct metric understanding (recovery ≠ quality, proxy ≠ expression) | Clear but generic | Vague | Absent / metrics misunderstood |
| Tool selection & justification | Reasoned (why MPNN *and* ESM-IF; why ESMFold for triage + AF2 for confirmation) | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete grid; recapitulation loop; diversity + solubility; reproducible | Complete, basic | Incomplete | Non-working |
| Critical analysis | Pareto map + honest per-setting hit rate + "no best setting" + proxy limits | Some limitations noted | Superficial | None |
| Experimental plan | Codon/tag + express→SDS-PAGE→SEC→DSF/CD, controlled (incl. hydrophobic-patch negative), costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures (Pareto, per-setting heatmaps), logical flow | Mostly clear | Disorganized | Poor |

## Deliverable specifications
- **D0 (Wk 2):** ≤2-page problem statement + metrics table (means / does-not-mean) + printout of one-backbone design with recovery + recapitulation scRMSD.
- **D1 (Wk 6):** repo link; minimal pipeline demo (backbone → MPNN → recapitulation → recovery) on 2–3 backbones; `LOG.md` started.
- **D2 (Wk 12):** `results/sequences.csv` (hundreds of sequences, every setting per row) + design log (configs, seeds, versions, runtimes) + 3–4 page interim report.
- **D3 (Wk 18):** notebook + figures: per-setting recovery/recapitulation/diversity/solubility tables, the Pareto map, MPNN vs ESM-IF, survival-at-each-layer, per-setting hit rates.
- **D4 (Wk 22):** settings-recommendation tool/heuristic + codon/tag guidance + `plan.md` (express→SDS-PAGE→SEC→DSF/CD, controls, timeline, costed reagents).
- **D5 (Wk 24):** thesis chapter + slides + `v1.0` tagged release + the **MPNN settings cheat-sheet**.

## Reproducibility gate (pass/fail overlay)
Independent of grade band: if a grader cannot rerun `00_setup` → `03_filter_and_rank` on Colab (with
the `mock` backend, no GPU) and reproduce the survival/Pareto plumbing from the tagged release, the
reproducibility components are capped at "Adequate" until fixed. State exact tool versions, commit
pins, and seeds in the report.
