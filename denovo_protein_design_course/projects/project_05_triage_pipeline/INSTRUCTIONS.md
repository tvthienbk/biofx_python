# Project 05 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **foundational infrastructure project**: you are building the 4-layer filter engine that
becomes `shared/filtering_pipeline.py` for the whole cohort. Projects 01/03 produce the design pools
it consumes; Projects 06–25 depend on it. Treat the cohort as your customer, and treat *tests and
documentation* as first-class deliverables — an untested filter no one trusts is worthless.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the discrimination problem and the engine's API, and implement Layer 1.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): the 4-layer validation concept, Dauparas 2022 (self-consistency), Jumper 2021 (AF2 confidence), Pacesa 2025 (the BindCraft discrimination caveat). Write a half-page on **why filters enrich but do not guarantee**. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt; note any superseded entries and record each item's source + license. `[core]`
- **Week 2**
  - Write a 1-page **API spec** in your own words: walk through the `Design` dataclass fields and the *signatures and contracts* of `self_consistency`, `orthogonal_check`, `physics_filter`, `dynamics_filter`, `rank_designs`, `run_pipeline`, `report` (read them in `shared/filtering_pipeline.py`). State the explicit success criteria for this project (clean, tested layers; justified cutoffs; honest analysis) and the "controls" — your planted known-good/known-bad designs. `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb` then the Layer-1 section of `01_define_and_explore.ipynb`. Confirm a planted known-good `EXAMPLE_DATA` design **passes** Layer 1 and a known-bad one **fails** (inline asserts). `[core]`

**D0 deliverable:** API spec write-up (with explicit success criteria + the known-good/known-bad controls) + printout of Layer 1 passing/failing the planted designs.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a minimal working engine — Layer 1 + ranking + report — running end-to-end on a labeled pool.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Build the labeled teaching pool: `python scripts/make_example_pool.py` → `results/pool.csv` (deterministic seed; every row labeled `EXAMPLE_DATA`, each carrying a hidden `truth` column for later enrichment checks). `[core]`
- **Week 4:** Verify Layer 1 against the pool — confirm planted good designs survive and planted bad ones are cut. Write down *why* each `DEFAULT_CUTOFFS["monomer"]` value is what it is (cite the self-consistency literature). `[core]`
- **Week 5:** Wire `rank_designs()` + `report()` end-to-end: run the engine with `use_layers=(1,)` on the pool, emit `results/pool_ranked.csv` + the survival figure. `[core]`
- **Week 6:** Write the `scripts/test_filtering.py` skeleton (plain asserts, runnable via `python scripts/test_filtering.py`); add the first Layer-1 known-good/known-bad assertions. Write a short "what's fast / what needs a GPU upstream / where the boundaries are" note. `[extension]`

**D1 deliverable:** working minimal engine (Layer 1 + `rank_designs` + `report`) + the labeled `EXAMPLE_DATA` pool + initialized repo with `LOG.md` and a passing first test.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** implement and unit-test Layers 2 (orthogonal) + 3 (physics) — the heart of the engine.

- **Weeks 7–8:** Implement/verify **Layer 2 — `orthogonal_check()`**: a second predictor (ESMFold/Boltz) must agree with the design (`scrmsd_orthogonal ≤ max_scrmsd`). Add unit tests: a planted design that *only* AF2 likes (good scRMSD, bad orthogonal) must fail Layer 2. Reason about why orthogonal agreement catches AF2 overconfidence. `[core]`
- **Weeks 9–10:** Implement/verify **Layer 3 — `physics_filter()`**: solubility/aggregation (CamSol-style score) and, for binders, interface energy (`rosetta_dG`) + shape complementarity. Add unit tests for each design type. Keep PyRosetta/FreeBindCraft/CamSol *behind the boundary* — the layer scores numbers; the notebooks (on Colab) produce them. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full mixed pool (monomer/binder/enzyme/antibody/oligomer rows); finalize the **design log** (every cutoff choice + seed + the test command + outcome). Make `scripts/test_filtering.py` cover all three layers and all planted cases; confirm `python scripts/test_filtering.py` exits 0. Interim report. `[core]`

**D2 deliverable:** Layers 2 + 3 implemented + a passing `scripts/test_filtering.py` (known-good passes / known-bad fails, per layer and per design type) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** run the **shared** engine on the pool and produce the discrimination-problem analysis.

- **Weeks 13–14:** In `03_filter_and_rank.ipynb`, `import filtering_pipeline as fp` from `shared/`, build `fp.Design` objects from `results/pool.csv`, call `fp.run_pipeline(pool, design_type=...)` + `fp.report(...)`. Confirm survival-at-each-layer matches your tests. **Do not fork the module into the project** — iterate locally against the shared one. `[core]`
- **Weeks 15–16:** Run the **enrichment analysis** (`04_validate.ipynb`): using the hidden `truth` labels in the `EXAMPLE_DATA` pool, compute the fraction of true-good designs among survivors *at each layer* (precision / enrichment) and how many true-good you lose (recall). Show that each layer enriches but none is perfect — there will be false positives among survivors and true hits among the cut. `[core]` / `[extension]`
- **Weeks 17–18:** **Cutoff-sensitivity sweep:** vary each cutoff (e.g., scRMSD 1.5–3.0 Å, pLDDT 70–90) and plot how survival count, enrichment, and the top-N ranking shift. Identify where ranking is brittle. Honest hit-rate accounting: N pass / N total at each layer, with the false-positive/false-negative breakdown. `[core]`

**D3 deliverable:** ranked CSV + survival figure produced **by the shared module**, enrichment-per-layer on the labeled pool, the cutoff-sensitivity figures, and the discrimination-problem writeup (where no single metric separates true/false).

---

## Phase 4 — Validate (in silico) + plan (adoption) (Weeks 19–22) → **D4**
**Goal:** add the optional dynamics hook, finalize the analysis, and plan cohort adoption.

- **Weeks 19–20:** Implement/verify the optional **Layer 4 — `dynamics_filter()`** hook (short MD: structure should not drift far, `md_rmsd ≤ max_md_rmsd`). Add a planted "folds-but-melts" design (good static metrics, high `md_rmsd`) that only Layer 4 catches. Discuss when the MD layer is worth its cost (it usually is not, at scale — say so). `[core]` / `[extension]`
- **Weeks 21–22:** Write the **cohort-adoption plan**: how a student proposes a cutoff change to `DEFAULT_CUTOFFS` via **pull request** (evidence: enrichment + N), reviewed, never silently overwriting `shared/filtering_pipeline.py`. *(Stretch)* package the engine as a minimal pip-installable module — show a `pyproject.toml` scaffold in a cell (do **not** commit it as a real package). Document the API for downstream projects. `[core]` / `[stretch]`

**D4 deliverable:** cutoff-sensitivity study + optional Layer-4 (short MD) hook with its planted test + the cohort-adoption (PR) guide + the packaging scaffold.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release the cohort can reproduce and adopt.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro: the triage problem · Methods: the 4-layer API + cutoffs + their justification · Results: survival + enrichment + cutoff sensitivity, all `EXAMPLE_DATA`-labeled · Discussion: the discrimination problem + where the filter fails · Cohort-adoption guide · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned `requirements.txt` + version stamp from `00_setup`). Land your engine as the cohort's `shared/filtering_pipeline.py`. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (the cohort's official filter engine).

---

### A note on scope discipline
It is tempting to keep adding metrics and layers. Don't. A *small, well-tested, honestly
characterized* engine is worth far more to the cohort than a sprawling one with unvalidated cutoffs.
When in doubt, deepen the tests and the discrimination analysis rather than widen the layer count.
And never present synthetic `EXAMPLE_DATA` enrichment as a real experimental result.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (the filter is CPU-fine; the *upstream* metric sources are the GPU step).
