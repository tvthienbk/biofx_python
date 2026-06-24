<!-- INSTRUCTIONS_TEMPLATE.md — Claude Code fills {{TOKENS}} with the catalog's P0–P5 tasks,
preserving [core]/[extension]/[stretch] tags. Every week must have concrete actions. -->
# Project {{NN}} — Student Instructions (24 weeks)

How to use this guide: each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks
are tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the problem deeply and reproduce a working baseline.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`). Write a half-page on the state of the field for this problem.
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt. Note any superseded entries. `[core]`
  - {{P0_WEEK1_TASK}}
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria and the controls you will need. `[core]`
  - Reproduce the project's "hello-world": run `notebooks/00_setup.ipynb` then the tutorial section of `01_define_and_explore.ipynb`. `[core]`
  - {{P0_WEEK2_TASK}}

**D0 deliverable:** problem statement (with success criteria + controls) + screenshot/printout of the reproduced tutorial output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small, possibly bad) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. {{P1_WEEK3_TASK}} `[core]`
- **Week 4:** Prepare inputs (clean target structure / define motif / build theozyme as relevant). {{P1_WEEK4_TASK}} `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a tiny scale (e.g., 5–10 designs). {{P1_WEEK5_TASK}} `[core]`
- **Week 6:** Produce + visualize the first batch; write a short "what worked / what's slow / what's my compute budget" note. {{P1_WEEK6_TASK}} `[extension]`

**D1 deliverable:** working minimal pipeline + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering).

- **Weeks 7–8:** Scale generation per the catalog ({{P2_GENERATION_SCALE}}); manage GPU time carefully. {{P2_WEEK78_TASK}} `[core]`
- **Weeks 9–10:** Sequence design ({{SEQUENCE_DESIGN_DETAILS}}); parameter exploration. {{P2_WEEK910_TASK}} `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full design pool; finalize the **design log** (every config + seed + output). Interim report. {{P2_WEEK1112_TASK}} `[core]`

**D2 deliverable:** full design pool + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark/ablation that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`). {{P3_WEEK1314_TASK}} `[core]`
- **Weeks 15–16:** Run the project's benchmark/ablation: {{BENCHMARK_ABLATION}}. {{P3_WEEK1516_TASK}} `[core]` / `[extension]`
- **Weeks 17–18:** Novelty/specificity checks; rank top candidates; **honest hit-rate accounting** (N pass / N generated at each layer). {{P3_WEEK1718_TASK}} `[core]`

**D3 deliverable:** ranked top candidates + benchmark figures + a filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation + project-specific deepening ({{P4_INSILICO_DEEPENING}}: e.g., docking, MD, multi-state, specificity panels). {{P4_WEEK1920_TASK}} `[core]` / `[extension]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy, purification, the right assay ({{ASSAY_TYPE}}), **controls** (positive + scrambled-interface/dead-mutant negative + unrelated), timeline, and a costed reagent list. {{P4_WEEK2122_TASK}} `[core]`
  - *(Optional, if your lab has capacity)* execute the go/no-go tier (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled experimental plan {{+OPTIONAL_WETLAB_DATA}}.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params · Results w/ hit rates & distributions · Discussion w/ failure forensics · Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks).
