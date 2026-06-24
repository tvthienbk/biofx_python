# Project 25 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** This is the **integrative capstone**: one complete turn of the Design–Build–
Test–Learn cycle on a real, advisor-approved target, plus a data-driven *Learn* step that the earlier
projects could not do — **learning from the whole cohort which in-silico features actually predict
experimental success.** The field's central bottleneck is the **gap between in-silico scores and
experimental success**: *no single metric perfectly separates true binders (or enzymes) from false.* A
low `pae_interaction` is AF2-Multimer's *confidence* about a relative placement, not a measured K_D;
low `scrmsd` is *self-consistency*, not stability or function. Standard filters **enrich** the hit
rate; they do not guarantee hits, and most designs that pass still fail at the bench.

**Key concepts a student must understand:**
- **DBTL spine.** Define (target, function, success criteria, controls) → Design (generate → sequence →
  filter) → Build/Test (plan or execute, with controls) → **Learn** (failure forensics + an ML model on
  accumulated data). This project does all five, with the *Learn* step elevated to the deliverable.
- **The in-silico→experimental gap.** Predictors are trained on natural proteins and are overconfident
  on de novo sequences; a single cutoff is a blunt instrument. The capstone replaces "trust one metric"
  with "learn the right *combination* from data — and prove it beats the single metric."
- **Cohort feature table.** One row per design: in-silico features (`scrmsd`, `plddt`,
  `pae_interaction`, `solubility`, `rosetta_dG`, `shape_complementarity`, `tm_to_pdb`) → a `success`
  label (experimental where it exists; an in-silico-derived proxy, clearly flagged, where it does not).
- **Success predictor.** A *small* model (LogisticRegression / shallow RandomForest; XGBoost optional)
  cross-validated on the table. Headline = **CV ROC-AUC (mean ± std) and N**, plus **feature
  importance** and **enrichment vs single-metric cutoffs**.
- **Active learning.** Wet-lab tests are scarce, so spend them where they teach the model most:
  *exploit* (highest `P(success)`) and *explore* (most uncertain, `P≈0.5`).

**Why this is hard and what realistic success looks like.** The cohort is a **small, biased, multi-
target** dataset. The honest result is an ML predictor that **beats single-metric cutoffs by some
margin** (better precision/enrichment and/or recall at a comparable selection size) — *or* a clear-eyed
report that, at this N, it doesn't yet. Both are excellent capstones. **Success ≠ a perfect
classifier.** Expect modest enrichment, report CV-AUC + N, own the overfitting risk, and never
fabricate experimental labels or hit rates.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** the **design campaign** uses the full heavy stack and realistically wants an
> **A100** (Colab Pro+ or a cluster) — the capstone aggregates a cohort's worth of compute. The
> **ML success predictor is light / CPU-OK** (scikit-learn / XGBoost on a feature table — seconds). The
> notebooks run end-to-end on a deterministic **`mock` / `EXAMPLE_DATA`** path with no GPU; switch to
> the real backends on Colab. **Pin upstream commits and verify them** (version-verify cell).

### scikit-learn (the success predictor — always)
- **What it does / where it fits:** trains + cross-validates the success predictor (notebook 04);
  `LogisticRegression` (interpretable, signed coefficients) and `RandomForestClassifier` (non-linear).
  Also ROC-AUC, StratifiedKFold, StandardScaler.
- **Install:** `pip install scikit-learn` (light, T4/CPU-fine). Upstream
  `https://github.com/scikit-learn/scikit-learn` (pin a release tag; verify it exists).
- **Key parameters:** `class_weight="balanced"` (the cohort is imbalanced), CV folds bounded by the
  minority class, `max_depth` small for RF (avoid overfitting on small N).
- **Compute:** CPU, seconds. No GPU.
- **Typical call:**
  ```python
  import ml_predictor as ml
  X, y, cols = ml.features_and_label(ml.build_cohort_table())
  bundle = ml.train_success_predictor(X, y, feature_names=cols, model="logreg", cv=5)
  ```

### XGBoost (optional gradient-boosted predictor)
- **What it does / where it fits:** an optional stronger estimator (`model="xgb"`); `ml_predictor.py`
  **falls back to RandomForest with a note** if XGBoost is not installed, so the module runs anywhere.
- **Install:** `pip install xgboost`. Upstream `https://github.com/dmlc/xgboost` (pin a tag; verify).
- **Key parameters:** `n_estimators`, `max_depth` (keep shallow, e.g. 3, on small N), `learning_rate`.
- **Compute:** CPU-fine for a feature table this size.

### The design stack (the campaign — A100; verify the ones YOU use)
- **RFdiffusion / RFdiffusion2 / Riff-Diff:** backbone generation (monomer/binder/symmetric; enzyme
  scaffolding). `https://github.com/RosettaCommons/RFdiffusion` (pin a commit). A100 for campaign scale.
- **BindCraft (/ FreeBindCraft):** one-shot binder hallucination with AF2-Multimer in the loop.
  `https://github.com/martinpacesa/BindCraft` (pin a commit; FreeBindCraft = free-tier fallback, verify).
- **RFantibody:** antibody/nanobody design (if your target is an antibody campaign). A100.
- **ProteinMPNN / LigandMPNN:** sequence design over backbones (CPU-cheap).
- **AF2(-Multimer) (ColabFold) / ESMFold / Boltz-2:** prediction + the key metrics (`pae_interaction`,
  `plddt`, `scrmsd`); `https://github.com/sokrypton/ColabFold` (pin a commit). The slow step at scale.
- Pick your family template: binders `project_06_pdl1_binder/`, antibodies `project_17_nanobody_taa/`,
  enzymes `project_18_kemp_eliminase/`.

### Shared `filtering_pipeline.py`
- The cohort's 4-layer filter (notebook 03): `fp.run_pipeline(designs, design_type=...)` then
  `fp.report(...)`. Do **not** fork it — iterate against `shared/` and PR back. The capstone's D★ output
  (the learned predictor) is exactly such a PR.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → choose+justify target (responsible-research check) + success criteria + controls + ML framing + mock hello-world
02_design_campaign  → full design campaign on the target (mock here; real backend + A100) + assemble the cohort feature table (EXAMPLE_DATA) → results CSVs; version-verify
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design; fp.run_pipeline(design_type=...) + fp.report; classical-filter survival + hit rate (the baseline)
04_analysis_figures → train + cross-validate the ML success predictor; feature importance; enrichment vs single-metric cutoffs; cross-target generalization
05_validation_plan  → execute-or-plan validation (controls) + integrate labels + honest hit-rate + failure forensics + active-learning loop + lessons-learned synthesis
```
For Project 25 the standard slots map to: *02 = the campaign + cohort-table assembly*, *04 = the ML
success-predictor study* (the signature), *05 = the validation plan + the loop-closing analysis*.

## 4. Filtering cutoffs for this design type
The classical baseline uses the shared cutoffs for **your** `design_type` (the capstone's worked
example is `binder`). The single-metric cutoffs the ML predictor is benchmarked against:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0–2.5 Å | self-consistency (designed vs predicted backbone) |
| pLDDT | ≥ 80 (mean) | local confidence (NOT stability) |
| pae_interaction (complexes) | ≤ 10 Å | interface confidence — key binder metric |
| rosetta_dG (binders) | ≤ −30 REU | favorable interface energy |
| shape complementarity | ≥ 0.6 | interface packing |
| catalytic_geom_rmsd (enzymes) | ≤ 0.5 Å | active-site geometry |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not pass/fail) |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they do
> not guarantee. The whole point of this project is to *learn a better combined rule* and report,
> honestly, whether it beats these single cutoffs.

## 5. Interpreting results
- **Classical filter (nb 03):** read the survival funnel as a funnel; report `N pass / N generated`.
- **Success predictor (nb 04):** the headline is **CV ROC-AUC (mean ± std) + N** — never a single-split
  accuracy. **Feature importance** (signed for LogReg) says which features carry the signal and which
  "trusted" metrics are weak. **Enrichment** (precision / base rate) and **recall** at a comparable
  selection size are how you compare the ML model to each single-metric cutoff.
- **The verdict:** does the ML model enrich better and/or recall more successes than the best single
  metric? State it with N and CV-AUC; if it doesn't, that is a valid, honest finding.
- **Failure forensics (nb 05):** of designs that passed the filter but failed experimentally (false
  positives), what do they share? This is the most useful artifact for the next cohort.
- **Watch for:** CV-AUC ≈ 1.0 (you are leaking / overfitting on tiny N — distrust it); enrichment that
  only looks good because the selection is huge (report `frac_selected` too).

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for the campaign | Reduce `num_designs`; batch; ESMFold for triage; move the campaign to A100/HPC. ML part needs no GPU |
| Upstream install fails | tool repo/commit changed | Use the pinned commit; update the install cell; log it (version-verify cell) |
| CV-AUC ≈ 1.0 or wildly high | overfitting / leakage / tiny N | Keep the model small (shallow); use cross-validation; check no label leaked into a feature; report N + caveat |
| CV fails / "need ≥2 of each class" | too few labelled designs of one class | Add cohort rows; the module guards this and tells you; report the small-N limit honestly |
| ML model loses to a single metric | small/biased N, or features genuinely weak | Report it honestly — a true negative result is valid; try more cohort data + the active-learning loop |
| XGBoost import error | not installed | `ml_predictor.py` auto-falls back to RandomForest with a note; install xgboost if you want it |
| "great" hit rate | mock numbers or cherry-picking | Confirm you are off the `mock` backend; report the full distribution + N, never the best single design |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** designed proteins typically *E. coli* BL21(DE3), 16–18 °C overnight (small, His-
  tagged); the target reagent (e.g. an ectodomain) is often mammalian/insect-expressed or commercial.
  Antibodies/nanobodies → mammalian (Expi293) or yeast display; enzymes → confirm fold (CD/SEC) before
  activity.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF/CD; **SPR/BLI** for
  binders → K_D/kinetics; **activity assay** for enzymes → kcat/KM) → deep (structure, competition/cell
  assays).
- **Controls (mandatory):** **positive** (a known-good binder/enzyme/natural protein — confirms the
  assay); **negative — scrambled-interface / catalytic dead-mutant** (your *own* top design, broken —
  must lose activity; the cleanest specificity control); **unrelated-protein negative**.
- **Closing the loop:** real outcomes become `label_origin="experimental"` rows; re-train the predictor
  and PR the improvement into `shared/filtering_pipeline.py`. **Never fabricate a K_D / kcat / hit rate.**

## 8. Responsible research
This capstone designs against a **student-chosen, advisor-approved real target** and is **dual-use** by
nature. **The advisor MUST approve the target against `MASTER_BLUEPRINT.md §7` BEFORE the design
campaign (P2)** — this is a hard gate (the `ADVISOR_APPROVED` flag in notebook 01). In-scope:
therapeutic, diagnostic, industrial, basic-science targets, framed for **neutralizing / inhibitory /
diagnostic / industrial** purposes; default any ambiguous target to that framing. Out of scope (refuse
and redirect): enhancing pathogen transmissibility/virulence, toxins or toxin delivery, evasion of
biosecurity screening, or any design whose primary purpose is harm — neutralizing a pathogen protein is
fine, making a pathogen *more dangerous* is not. Real gene-synthesis orders go through an IGSC-member
screening provider; wet-lab work requires institutional biosafety/ethics approval. Students must not
overstate results or imply experimental validation that was not done; **no experimental label in this
project is fabricated**, and all teaching data is flagged `EXAMPLE_DATA`.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers + versions/commits you actually used:
Pacesa 2025 (BindCraft — the discrimination caveat), Dauparas 2022 (ProteinMPNN), Jumper 2021 (AF2),
Wohlwend 2025 (Boltz-2), the scikit-learn / XGBoost methods references, an ML-for-design-filtering
paper, an active-learning-for-experiment-design paper, and 1–2 "closing the DBTL loop" frontier papers.
