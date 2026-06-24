# Project 25 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is the **integrative capstone**: you run a *complete* DBTL campaign on a real target **and** train
an ML success predictor on the cohort's accumulated design→outcome data to improve the shared filter.
It reuses the campaign workflow of the family it borrows from (binders = `project_06_pdl1_binder/`;
antibodies = `project_17_nanobody_taa/`; enzymes = `project_18_kemp_eliminase/`) — the notebooks use a
**binder** as the worked example, but your `design_type` is whatever you and your advisor choose.

> **Compute reality up front (be honest):** the campaign aggregates a cohort's worth of compute and
> realistically wants an **A100** (Colab Pro+ or a cluster) — a free **T4** runs only a small fallback.
> The **ML part is light / CPU-OK** (scikit-learn / XGBoost on a feature table). Every notebook runs
> end-to-end on a deterministic `mock` / `EXAMPLE_DATA` path with no GPU; switch to the real backends
> on Colab. See `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`.

> **RESPONSIBLE RESEARCH (mandatory gate):** your **advisor must approve your chosen target against
> `MASTER_BLUEPRINT.md §7` BEFORE you start the design campaign (P2).** Default any ambiguous target to
> a neutralizing / diagnostic / inhibitory / industrial framing. No out-of-scope targets.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** choose + justify the target, set success criteria + controls, frame the ML question, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Pacesa 2025 (BindCraft discrimination
    caveat), an ML-for-design-filtering paper, a "closing the DBTL loop" paper, plus the tool papers
    for the campaign you choose. Write a half-page on the in-silico-vs-experimental gap. `[core]`
  - **Choose your target** and write the **responsible-research justification** (function, in-scope
    framing, structural source). **Get advisor §7 approval — this is a hard gate before P2.** `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt; note superseded entries. Run
    `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria and the controls
    you will need (positive, scrambled-interface/dead-mutant negative, unrelated). `[core]`
  - Set `DESIGN_TYPE`; reproduce the "hello-world": run `00_setup.ipynb` then the mock mini-run +
    `EXAMPLE_DATA` cohort peek in `01_define_and_explore.ipynb`. `[core]`

**D0 deliverable:** problem statement (success criteria + controls) + **advisor-approved target** +
reproduced mock mini-run + `LOG.md` started.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small, possibly bad) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (scikit-learn/XGBoost + your campaign's design-tool URLs). `[core]`
- **Week 4:** Prepare inputs — clean the target structure / define the motif or theozyme / pick
  hotspots, as relevant to your `design_type`. `[core]`
- **Week 5:** Run the minimal campaign end-to-end on a tiny scale (a few designs) → score → metrics
  (mock if you only have a T4 this week; real backend on A100). `[core]`
- **Week 6:** Visualize the first batch; build the first slice of the **cohort feature table** and run
  `ml_predictor.py`'s smoke test; write a short "what's slow / what's my A100 budget per 100 designs"
  note. `[extension]`

**D1 deliverable:** working minimal pipeline + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real campaign at scale **and** the assembled cohort feature table (diversity before filtering).

- **Weeks 7–8:** Scale the campaign on your target (catalog scale for your family; e.g. binder 50–200
  BindCraft or 500–1000 RFdiffusion backbones → MPNN). Log every config + seed + tool **commit**. `[core]`
- **Weeks 9–10:** Score every design (AF2(-Multimer)/ESMFold/Boltz-2); parameter exploration. Begin
  **assembling the cohort design→outcome table** from Projects 01–24 outputs (in-silico metrics +
  sequences + any experimental labels). `[core]` / `[extension]`
- **Weeks 11–12:** Finalize the campaign pool (`results/campaign_designs.csv`) and the cohort table
  (`results/cohort_table.csv` / `data/cohort_design_outcomes.csv`); finalize the **design log**. Interim
  report. `[core]`

**D2 deliverable:** full campaign pool + assembled cohort feature table + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the **trained success predictor** that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type=...)` + `fp.report(...)`). Report
  the **classical-filter** survival + hit rate — the baseline. `[core]`
- **Weeks 15–16:** **Train + cross-validate the ML success predictor** (`04_validate.ipynb` →
  `ml_predictor.py`): CV-AUC (mean ± std) + N; **feature importance**; **enrichment vs single-metric
  cutoffs**. `[core]` Compare estimators (LogReg / RandomForest / XGBoost). `[extension]`
- **Weeks 17–18:** Cross-target generalization (leave-one-design-type-out); rank top candidates; honest
  hit-rate accounting (classical filter vs learned predictor). `[core]` / `[extension]`

**D3 deliverable:** ranked top candidates + trained success predictor (CV-AUC, feature importance,
enrichment vs cutoffs) + a filtering report including survival-at-each-layer and the honest verdict.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** close the loop — plan/execute validation, integrate labels, do the forensics.

- **Weeks 19–20:** Orthogonal re-prediction of top hits; **integrate any real experimental labels** into
  the predictor (`label_origin="experimental"`; never fabricated) and re-train; **honest hit-rate +
  failure forensics** (the signature of confident-but-failed designs). `[core]` / `[extension]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy, purification, the
  right assay for your design_type (SPR/BLI for binders; activity assay for enzymes; binding +
  developability for antibodies), **controls** (positive + scrambled-interface/dead-mutant negative +
  unrelated), timeline, costed reagent list. Design the **active-learning loop** (which design to test
  next — exploit vs explore). `[core]` / `[stretch]`
  - *(Optional, if your lab has capacity)* execute the go/no-go tier (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled experimental plan + integrated labels +
honest hit-rate + failure forensics (+ optional go/no-go data).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce — and a better shared filter.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro w/ the in-silico-vs-experimental gap ·
  Methods w/ exact versions+params · Results w/ hit rates, distributions, CV-AUC + feature importance +
  enrichment · Discussion w/ failure forensics · Experimental plan · References · Reproducibility
  statement). Write the cohort-wide **"lessons learned"** synthesis and the concrete
  `filtering_pipeline.py` improvement proposal. `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; **pull-request the improved
  success predictor back into `shared/`** so the cohort's filter improves; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release + the D★ success-predictor module.

---

### A note on what makes this the capstone
The scientific heart is **closing the DBTL loop with data**: you do not just run one campaign and
filter it — you *learn from the whole cohort* which features actually predict success, prove (or
honestly disprove) that the learned rule beats single-metric cutoffs, and feed it back. Generate at
honest scale, report CV-AUC and N (never a single-split brag), own the small-N/overfitting caveats, and
report the hit rate, not the cherry.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
