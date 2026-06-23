<!-- MANUAL_TEMPLATE.md — Claude Code fills {{TOKENS}} with project-specific theory, tools,
exact commands/parameters, and a troubleshooting table for THIS project's tools. -->
# Project {{NN}} — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
{{THEORY_SECTION}}
- The design problem in one paragraph.
- The key concepts a student must understand (e.g., self-consistency, scRMSD, pAE; theozyme; CDR loops; symmetry contigs — whichever apply).
- Why this is hard and what realistic success looks like ({{REALISTIC_HIT_RATE}}).

## 2. Tools used (exact versions pinned in `env/requirements.txt`)
{{PER_TOOL_BLOCK}}  <!-- For EACH tool, include: -->
### {{TOOL_NAME}}
- **What it does / where it fits in the pipeline.**
- **Install:** upstream repo/notebook URL (pinned). *Verify it still exists before the course starts.*
- **Key parameters that matter for this project:** {{PARAMS_WITH_RECOMMENDED_VALUES}}
- **Compute:** {{TOOL_COMPUTE_TIER}} (free T4 OK? needs A100? fallback?).
- **Typical command / call:**
  ```bash
  {{EXAMPLE_COMMAND}}
  ```

## 3. The pipeline, step by step
{{PIPELINE_WALKTHROUGH}}  <!-- map each notebook 00–05 to what it does, inputs, outputs -->
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → {{STEP_01}}
02_design_campaign  → {{STEP_02}}
03_filter_and_rank  → multi-layer filter via shared/filtering_pipeline.py → ranked CSV + figures
04_analysis_figures → {{STEP_04}} (benchmark/ablation)
05_validation_plan  → {{STEP_05}} (docking/MD as relevant + experimental-plan generator)
```

## 4. Filtering cutoffs for this design type
{{CUTOFF_TABLE}}  <!-- from MASTER_BLUEPRINT/validation-ref, e.g.: -->
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | {{}} | self-consistency |
| pLDDT | {{}} | confidence (NOT stability) |
| pAE_interaction (complexes) | {{}} | interface confidence |
| {{PROJECT_SPECIFIC_METRIC}} | {{}} | {{}} |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they do not guarantee. Expect false positives and report them.

## 5. Interpreting results
{{INTERPRETATION_GUIDANCE}}
- What a good vs bad design looks like in each metric.
- How to read the survival-at-each-layer plot.
- How to compute and report a hit rate.

## 6. Troubleshooting
{{TROUBLESHOOTING_TABLE}}  <!-- project-specific, e.g.: -->
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for campaign size | Reduce `num_designs`; batch; use ESMFold for triage; move heavy jobs to A100/HPC |
| Upstream install fails | Notebook/repo changed | Check the pinned repo; update the install cell; log it |
| All designs fail self-consistency | Backbone/sequence mismatch, bad inputs | Re-check target prep; lower MPNN temperature; regenerate backbones |
| {{PROJECT_SYMPTOM}} | {{CAUSE}} | {{FIX}} |

## 7. Experimental validation reference (for the D4 plan)
{{VALIDATION_REFERENCE}}
- Expression: typically *E. coli* BL21(DE3), 16–18 °C overnight; note when mammalian expression is needed.
- Characterization tiers: go/no-go (express → SDS-PAGE → SEC) → basic (DSF, CD, {{ASSAY}}) → deep (structure, SEC-MALS/SAXS).
- **Controls:** positive ({{POSITIVE_CONTROL}}), negative ({{NEGATIVE_CONTROL}} — e.g., scrambled interface or catalytic dead-mutant), unrelated-protein control.

## 8. Responsible research
{{RESPONSIBLE_RESEARCH_PARAGRAPH}} See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: {{LEGITIMATE_PURPOSE}}. Synthesis screening + institutional approval required for any wet-lab work.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used in your report.
