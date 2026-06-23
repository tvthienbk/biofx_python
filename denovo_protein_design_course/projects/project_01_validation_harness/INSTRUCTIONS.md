# Project 01 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **foundational tooling project**: you are building the calibrated validation harness
that Projects 02–25 will use. Treat the cohort as your customer.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the metrics deeply and reproduce a single working prediction.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): AF2 (Jumper 2021), self-consistency (Dauparas 2022), Boltz-2 (Wohlwend 2025), ESMFold (Lin 2023). Write a half-page on *what each confidence metric measures and what it does **not***. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt; note superseded entries and record each item's source DOI + license. `[core]`
- **Week 2**
  - Write **metric definitions in your own words**: pLDDT, PAE, pTM/ipTM, self-consistency scRMSD, TM-score/novelty. State the common misreadings (e.g., "pLDDT ≠ stability"). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then the single-sequence prediction section of `01_define_and_explore.ipynb` on one natural protein (e.g., ubiquitin). `[core]`

**D0 deliverable:** metric-definitions write-up (with explicit "what it does not mean" notes) + screenshot/printout of the reproduced prediction with its confidence values.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working prediction wrapper that turns *any sequence* into parsed confidence metrics.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Get ESMFold running end-to-end on 3–5 sequences. `[core]`
- **Week 4:** Add ColabFold (AF2) to the wrapper; parse pLDDT + PAE from its outputs. Handle the T4 memory ceiling (sequence-length limits, batching). `[core]`
- **Week 5:** Add Boltz-2; unify all three behind one function `predict(sequence, tool) → {pdb, plddt, pae, ptm}`. Run on a tiny labeled subset (5–10). `[core]`
- **Week 6:** Add self-consistency scRMSD (designed-vs-predicted) and TM-score/novelty via TM-align/Foldseek; write a "what's fast / what's my compute budget per 100 sequences" note. `[extension]`

**D1 deliverable:** working prediction wrapper (AF2/ESMFold/Boltz → parsed confidence) + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the labeled dataset and all its predictions (the raw material for calibration).

- **Weeks 7–8:** Curate the **labeled dataset**: ≥40 designed proteins with *known* experimental outcomes (folded?/expressed?/bound?) from de novo design papers' supplementary data, + ≥10 natural positive references. Record provenance (DOI, table, license) per item in `data/dataset.csv`. `[core]`
- **Weeks 9–10:** Predict every item with all three tools; store outputs systematically. Add an **MSA-depth ablation** for AF2 (full MSA vs single-sequence) on a subset. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full prediction table (one row per design × tool, all metrics); finalize the **design/prediction log** (tool version + params + seed + runtime). Interim report. `[core]`

**D2 deliverable:** curated labeled dataset (≥40 designs + ≥10 natural refs, with provenance) + complete prediction table + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** the calibration study that turns predictions into evidence-based cutoffs.

- **Weeks 13–14:** Wire your table into the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`); confirm the self-consistency + orthogonal layers run on your data. `[core]`
- **Weeks 15–16:** Run the **benchmark**: ROC and PR curves for each metric vs experimental outcome; report AUC. Find the best **single** predictor, then a **composite** (e.g., logistic regression on scRMSD + pLDDT + PAE). Compare **AF2 vs ESMFold vs Boltz agreement**. `[core]` / `[extension]`
- **Weeks 17–18:** Per-design-type calibration (monomer vs binder vs enzyme, where labels allow); honest accounting of where the predictor fails (false positives/negatives, by type). `[core]` / `[extension]`

**D3 deliverable:** calibration study — ROC/PR per metric (with AUC), best single + composite predictor, AF2/ESMFold/Boltz agreement analysis, and a failure-mode breakdown.

---

## Phase 4 — Validate + plan (Weeks 19–22) → **D4**
**Goal:** turn the calibration into a usable SOP and harden the shared module.

- **Weeks 19–20:** Convert findings into a **Validation SOP card**: recommended cutoffs by design type, with the evidence (AUC, N) behind each. Harden them into `filtering_pipeline.py`'s `DEFAULT_CUTOFFS` + self-consistency/orthogonal layers via pull request. `[core]`
- **Weeks 21–22:** *(Boltz-2 affinity, `[stretch]`)* If any dataset items have measured K_D, compare Boltz-2 predicted affinity vs measured and report correlation + caveats. Write the "how the cohort should use this harness" guide, including controls every downstream project must run. `[core]` / `[stretch]`

**D4 deliverable:** Validation SOP (calibrated cutoffs by design type, with evidence) + hardened, documented `filtering_pipeline.py` contribution + cohort usage guide.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release the cohort can reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params · Results w/ ROC/PR + agreement + calibration · Discussion w/ failure forensics · Cohort SOP · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned `requirements.txt` + version stamp from `00_setup`). `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (the cohort's official validation harness).

---

### A note on scope discipline
It is tempting to keep adding tools and metrics. Don't. A *small, well-calibrated, honestly
characterized* harness is worth far more to the cohort than a sprawling one with unvalidated
cutoffs. When in doubt, deepen the calibration rather than widen the toolset.
