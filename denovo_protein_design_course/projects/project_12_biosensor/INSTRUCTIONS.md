# Project 12 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **binder → biosensor** project: you design a de novo binder to a chosen biomarker (the
Project-06 two-paradigm binder workflow), couple it to a **conformational switch / split-reporter**,
reason about the binding→signal transduction, and plan a functional readout. The binder module follows
the **binder-family template** (Project 06); the switch / split-reporter module is the new layer.

> **Compute reality up front (be honest):** a real binder campaign **plus** switch / two-state
> modeling wants an **A100** (Colab Pro+ or a cluster). A free **T4** runs only a *small fallback*
> campaign: FreeBindCraft, a small `num_designs`, a small RFdiffusion batch with ESMFold triage, and
> small two-state runs. **Do not claim a full campaign runs free on Colab.** Plan batch sizes around
> your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand biosensor architectures, choose an analyte + readout, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Langan 2019 (LOCKR switches),
    Quijano-Rubio 2021 (de novo biosensors), a split-luciferase/NanoBiT reference (Dixon 2016),
    Pacesa 2025 (BindCraft), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN). Write a half-page
    on the state of the field (how binding is turned into signal). `[core]`
  - **Choose your analyte** (STUDENT CHOICE: a small protein biomarker — a cytokine or a cardiac
    marker, etc.) and **verify its accession on RCSB** (the candidate in `data/README.md` is flagged
    "candidate — verify"). Record resolution, chains, and the epitope you will target. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g. "≥N
    binders passing all binder layers with `pae_interaction` ≤ 10, and ≥1 integrated construct with a
    target modeled dynamic range") and the controls you will need (**no-analyte/blank**, **off-target**). `[core]`
  - **Choose your readout** (split-luciferase/NanoBiT luminescence, or split-FP FRET) and **switch
    family** (split-reporter vs LOCKR-style). Reproduce the "hello-world": run `00_setup.ipynb` then
    the mock mini-run in `01_define_and_explore.ipynb` (binder → switch → ON/OFF). `[core]`

**D0 deliverable:** problem statement (success criteria + controls) + analyte/readout choice +
epitope list + screenshot/printout of the reproduced mock hello-world output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/ColabDesign/ColabFold URLs). `[core]`
- **Week 4:** Finalize target prep — clean the biomarker structure, define the epitope residues as the
  binder target, decide binder length range (40–80 aa minibinder is typical), and decide which switch
  family/reporter you will integrate. `[core]`
- **Week 5:** Run the minimal binder pipeline end-to-end on a *tiny* scale: a **BindCraft mini-run** (a
  few designs) on A100, or the `mock` backend if you only have a T4 this week, and a small RFdiffusion
  binder batch → ProteinMPNN. `[core]`
- **Week 6:** Run AF2-Multimer on those few designs; design **one** mock/borrowed switch and do a
  first mock integration (binder → switch → ON/OFF). Write a short "what worked / what's slow / what's
  my A100 budget per 100 designs + per two-state model" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline (target → designs → AF2-Multimer → metrics) +
first design batch + a first mock integration + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real binder campaign at scale **and** the switch module (diversity before filtering).

- **Weeks 7–8:** **BindCraft campaign** — 50–200 binders against the analyte epitope (A100; on a T4,
  FreeBindCraft with a smaller `num_designs`). Log every config, seed, and the epitope set. `[core]`
- **Weeks 9–10:** **RFdiffusion binder campaign** — 500–1000 backbones in binder mode against the same
  epitope → ProteinMPNN sequence design (several sequences per backbone). Explore noise scale /
  epitope subsets. `[core]` / `[extension]`
- **Weeks 11–12:** **Switch module** — design an RFdiffusion scaffold presenting a split-reporter
  (luminescence/FRET) **and/or** borrow + adapt a LOCKR-style cage (Langan 2019). Score switches on
  intrinsic toggle quality. Assemble the binder pools (one row per design, tagged by paradigm) +
  the switch pool; finalize the **design log**. Interim report. `[core]`

**D2 deliverable:** the two-paradigm binder pool (`results/*.csv`) + the switch module
(`results/switch_designs.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & integrate (Weeks 13–18) → **D3**
**Goal:** reproducible triage of the binder, then the **integration + ON/OFF reasoning** that makes
this a sensor study, not a binder demo.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** binder pools (`03_filter_and_rank.ipynb`
  → `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Report survival-at-each-layer for each paradigm; honest hit-rate accounting. `[core]`
- **Weeks 15–16:** **Integrate** the top binders with the switch(es) (`04_validate.ipynb`); model the
  integrated construct and reason about **ON/OFF states**; benchmark **switch architecture**
  (split-reporter vs LOCKR) on dynamic range; plot the **affinity-vs-dynamic-range trade-off**. `[core]`
- **Weeks 17–18:** **Two-state AF2 modeling** of the switch — model the OFF (closed/split-apart) and
  ON (open/reconstituted) conformations and derive a relative signal; select the top integrated
  constructs ranked by dynamic range. `[extension]`

**D3 deliverable:** filtered/ranked binders (survival funnels per paradigm) + integrated constructs
with ON/OFF + switch-architecture benchmark + affinity-vs-dynamic-range figure + `results/top_constructs.csv`.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the functional experiment.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top binders with an independent
  predictor; finalize the two-state ON/OFF analysis; sketch the **off-target** specificity panel
  (re-model the construct against a related/unrelated analyte — the dynamic range should collapse). `[extension]`
- **Weeks 21–22:** Write the **functional-readout validation plan** (`05_validation_plan.ipynb`):
  expression strategy (E. coli for the construct; recombinant analyte reagent), the **luminescence/FRET
  dose-response** (titrate analyte → fit signal vs [analyte] → EC50 + dynamic range → **estimate LOD**
  from the fit), **controls** (**no-analyte/blank** for the OFF floor + LOD; **off-target** for
  specificity; a positive/calibrator), timeline, and a costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* express the top construct + run a single dose-response. `[stretch]`
  - *(Stretch)* sketch a **multiplexing** concept (orthogonal reporters / arrays + cross-talk controls). `[stretch]`

**D4 deliverable:** validation report + costed, controlled luminescence/FRET dose-response + LOD plan
(no-analyte/off-target controls) (+ optional go/no-go wet-lab data; + optional multiplexing concept).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ hit rates, distributions, the switch-architecture benchmark, and the
  affinity-vs-dynamic-range trade-off · Discussion w/ failure forensics · Functional-readout plan ·
  References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on the two hard problems
The scientific heart of this project is **two** coupled hard problems: (1) designing a binder that
engages the analyte at all, and (2) coupling that binding to a **clean ON/OFF signal** with usable
dynamic range. They pull against each other (the affinity-vs-dynamic-range trade-off). Generate the
binder pool at honest scale, filter it identically, then integrate and report the dynamic range
**distribution** — don't cherry-pick the one construct that looked good. A modeled dynamic range is a
hypothesis until a real dose-response is fit.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
