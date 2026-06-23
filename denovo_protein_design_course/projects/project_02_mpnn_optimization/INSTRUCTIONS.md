# Project 02 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **foundational sequence-design project**: you are characterizing the MPNN settings that
the rest of the cohort's pipelines (binders, enzymes, antibodies) all depend on. Treat the cohort
as your customer — your cheat-sheet is the product.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the recovery ↔ foldability ↔ expressibility trade-off and reproduce one working MPNN run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): ProteinMPNN (Dauparas 2022), LigandMPNN (Dauparas 2024), MPNN-for-expression (Sumida 2024), and the recapitulation predictors (AF2 Jumper 2021, ESMFold Lin 2023). Write a half-page on *why* temperature/noise/seqs-per-backbone move foldability and expression. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt; note superseded entries and record each item's source DOI + license. Decide where your **de novo backbones** come from (Project 03 outputs or a public design set) and log their provenance. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with measurable success criteria (e.g., "find settings with recapitulation ≥ X% while keeping per-position entropy ≥ Y") and the controls you will need. Build the **metrics table**: for each metric, what it means and what it does **not** mean. `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then the hello-world section of `01_define_and_explore.ipynb` — design sequences for **one** backbone, compute sequence recovery and a (mock) recapitulation scRMSD, and print them. `[core]`

**D0 deliverable:** problem statement (success criteria + controls + metrics table) + screenshot/printout of the reproduced one-backbone design with its recovery + recapitulation values.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal pipeline: backbone → MPNN → recapitulation → recovery, end to end.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Reproduce the **ProteinMPNN tutorial** on the official repo and design sequences for 2–3 backbones with default settings. `[core]`
- **Week 4:** Prepare inputs: collect 20–30 de novo backbones + your natural references; clean and renumber them; confirm `scripts/mpnn_tools.py` loads each. Run `data/download_data.py` for the natural references. `[core]`
- **Week 5:** Stand up the **recapitulation loop** (designed sequence → ESMFold/AF2 → scRMSD vs the input backbone) on a tiny scale (one backbone, a few sequences). Use ESMFold for speed; reserve AF2 full-MSA for later. `[core]`
- **Week 6:** Produce + inspect the first batch across 2–3 backbones at default settings; write a short "what worked / what's slow / what's my compute budget per 100 sequences" note. MPNN itself is seconds; **recapitulation is the bottleneck** — measure it. `[extension]`

**D1 deliverable:** working minimal pipeline (backbone → MPNN → recapitulation → recovery) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the systematic sweep at scale (diversity before filtering).

- **Weeks 7–8:** Run the **sweep** over the grid: temperature {0.1, 0.2, 0.3, 0.5} × backbone noise {0.0, 0.1, 0.2} × seqs/backbone {8, 16, 48}, across your 20–30 backbones. That is **hundreds of sequences**; with the `mock` backend the loop runs anywhere, then switch to the real ProteinMPNN command on Colab. Manage GPU time carefully. `[core]`
- **Weeks 9–10:** Recapitulate the designed sequences (ESMFold for triage; batch AF2 overnight on the subset that matters). Compute per-sequence recovery and the solubility proxies. Store everything in `results/sequences.csv` with the full setting on every row. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full design pool; finalize the **design log** (every config + seed + tool version + runtime). Write the 3–4 page interim report describing the sweep and the compute budget you actually spent. `[core]`

**D2 deliverable:** full sweep → `results/sequences.csv` (hundreds of sequences, every setting logged) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the Pareto analysis that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`): build `fp.Design` objects (`design_type="monomer"`) from recapitulation scRMSD/pLDDT + solubility, call `fp.run_pipeline(..., design_type="monomer")`, and `fp.report(...)`. Report survival at each layer. `[core]`
- **Weeks 15–16:** Run the benchmark/ablation: the **temperature × noise grid** of recovery, recapitulation, diversity (per-position Shannon entropy), and solubility; identify **Pareto-optimal settings** (foldability ↔ diversity ↔ solubility). Compare **ProteinMPNN vs ESM-IF** (and FAMPNN if available). `[core]` / `[extension]`
- **Weeks 17–18:** **Consensus-design vs single-sequence** comparison (does taking the per-position consensus of N sequences beat the single best?). Honest hit-rate accounting (N recapitulating / N generated, per setting). `[core]` / `[extension]`

**D3 deliverable:** ranked survivors + per-setting metric tables + the Pareto map of settings + a filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** turn the Pareto map into a usable recommendation tool and design the experiment.

- **Weeks 19–20:** Build a **lightweight settings-recommendation heuristic/model**: given a backbone (length, secondary-structure class) and a goal (max foldability vs max diversity vs max solubility), recommend a setting and predict "likely expresses" from the in-silico features. Keep it simple and report where it fails. `[extension]`
- **Weeks 21–22:** Write the **experimental validation plan**: codon optimization for the host, tag strategy, expression in *E. coli* BL21(DE3) at 16–18 °C, then express → SDS-PAGE → SEC → DSF/CD, with **controls** (positive = a known-good natural sequence; negative = a deliberately high-hydrophobic-patch design; unrelated-protein control), a timeline, and a costed reagent list. `[core]`
  - *(Stretch)* **MPNNsol / surface-redesign** comparison: redesign only surface positions for solubility and re-score. `[stretch]`

**D4 deliverable:** settings-recommendation tool + codon/tag guidance + costed, controlled experimental validation plan.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release the cohort can reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params · Results w/ the Pareto map, recovery/recapitulation/diversity/solubility distributions, and hit rates · Discussion w/ failure forensics · Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned `requirements.txt` + version stamp from `00_setup`). Publish the **MPNN settings cheat-sheet**. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release + the cohort's MPNN settings cheat-sheet.

---

### A note on scope discipline
It is tempting to add more tools (every new inverse-folding model, more solubility predictors) than
to deepen the sweep. Don't. A *clean, honestly-characterized* Pareto map over the specified grid is
worth far more to the cohort than a sprawling comparison with shaky statistics. When in doubt, add
backbones and replicates, not tools.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks; recapitulation is your bottleneck).
