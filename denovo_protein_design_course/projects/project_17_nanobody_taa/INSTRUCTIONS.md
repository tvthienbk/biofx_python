# Project 17 — Student Instructions (24 weeks)

How to use this guide: each phase ends in a graded **deliverable (D0–D5)**. Keep a running `LOG.md`
(date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are tagged `[core]`
(everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is the **antibody-family template** project: the workflow you build (RFantibody/BoltzGen →
AF2-Multimer/IgFold → developability → `design_type="antibody"` filter → display screen) is reused by
Projects 14–16. Build it cleanly.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the TAA + nanobody biology, choose your epitope, and reproduce the mock hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): RFantibody (Bennett 2025), ImmuneBuilder
    (Abanades 2023), the HER2/EGFR structural papers. Write a half-page on the state of de novo
    nanobody design for tumor antigens — including the **honest, low hit rates**. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt (`1N8Z`, `1IVO`, any model).
    Note superseded entries; record each DOI + license. `[core]`
  - Run `data/download_data.py` (or `--dry-run`); inspect `provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement**: the TAA, the **epitope choice** (overlapping vs
    non-overlapping with an approved mAb, with justification), measurable success criteria, and the
    controls you will need. `[core]`
  - Reproduce the "hello-world": run `00_setup.ipynb`, then `01_define_and_explore.ipynb` on the `mock`
    backend (pick TAA + epitope + framework; generate + score 5 mock VHHs). `[core]`
  - Read the **CDR/VHH structure** section of `MANUAL.md §1`; identify your epitope residues off the
    *verified* antigen surface (not the EXAMPLE placeholders). `[core]`

**D0 deliverable:** problem statement (TAA + epitope choice + success criteria + controls) + printout of
the reproduced mock VHH hello-world (CDR3 length + SYNTHETIC metrics).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal VHH pipeline producing a first (mock, then tiny-real) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  full mock pipeline (`01`→`05`) end-to-end so the plumbing is solid before any GPU spend. `[core]`
- **Week 4:** Prepare inputs: clean the verified TAA structure, fix the **humanized VHH framework**, and
  finalize the **epitope residue list** (read off the real surface; for "overlapping", off the mAb
  interface). `[core]`
- **Week 5:** Run a **tiny real RFantibody demo** (free-tier feasible at very small N) end-to-end:
  design a handful of VHHs, score one (VHH, antigen) complex with AF2-Multimer. Pin the tool commit. `[core]`
- **Week 6:** Visualize the first batch (py3Dmol); write a short "what worked / what's slow / what's my
  A100 budget per 100 designs" note. `[extension]`

**D1 deliverable:** working minimal VHH pipeline + first design batch (mock + a tiny real demo) +
initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real VHH design campaign at scale (diversity before filtering).

- **Weeks 7–8:** Scale generation on an **A100**: 500+ VHH designs against your epitope (low hit rate ⇒
  large pool). Manage GPU time; run the **version-verify** cell and pin every tool commit. `[core]`
- **Weeks 9–10:** Sequence design is inside RFantibody (ProteinMPNN over the diffused CDR loops);
  explore parameters (CDR3 length range, number of sequences per backbone). Score each complex with
  AF2-Multimer (`pae_interaction`) + IgFold/NanoBodyBuilder2 (CDR geometry). `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full pool into `results/campaign.csv`; finalize the **design log** (every
  config + seed + tool/commit + runtime). Interim report. `[core]`
  - *(Optional)* BoltzGen nanobody-mode pool for the `[extension]` head-to-head in P3. `[extension]`

**D2 deliverable:** full VHH design pool (`campaign.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the epitope/specificity/developability study that makes this a *study*.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`) with `design_type="antibody"` (scRMSD ≤ 3.0, pLDDT ≥ 70,
  pae_interaction ≤ 12). Report **survival at each layer** and the honest hit rate. `[core]`
- **Weeks 15–16:** Run the benchmark/ablation: **epitope choice** (overlapping vs non-overlapping) and
  **specificity within the receptor family** (HER2 vs EGFR/HER3/HER4) via `04_validate.ipynb`. `[core]` /
  `[extension]` *(RFantibody vs BoltzGen head-to-head is the [extension].)*
- **Weeks 17–18:** Developability + humanness figures (TAP-like / CamSol-like / humanness — **swap in the
  real tools** for any reportable claim); epitope-binning reasoning; rank top candidates with honest
  hit-rate accounting. `[core]`

**D3 deliverable:** antibody-filtered ranked candidates + epitope/specificity/developability figures + a
filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen specificity confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation + specificity deepening: model survivors against the full
  **receptor-family panel** (target vs relatives), report the specificity margin; confirm CDR-loop
  geometry with IgFold/NanoBodyBuilder2. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **display-screen plan** (`05_validation_plan.ipynb`): pooled yeast/phage
  display → FACS selection on labeled TAA → NGS enrichment → recover + express + confirm by SPR/BLI;
  choose a **downstream format** (VHH-Fc imaging or CAR binder); specify **controls** (positive known
  anti-TAA nanobody, irrelevant-antigen negative, unrelated-binder negative); costed reagent list +
  timeline. `[core]`
  - *(Stretch)* design a **biparatopic/bispecific** concept by pairing a non-overlapping VHH with an
    overlapping one. `[stretch]`

**D4 deliverable:** validation report + display-screen plan + downstream construct + receptor-family
specificity panel + costed, controlled experimental plan.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro w/ TAA + epitope rationale · Methods w/
  exact tools/commits/params · Results w/ hit rates, distributions, specificity · Discussion w/ failure
  forensics · Display-screen + downstream plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (A100 need; free-tier = tiny RFantibody demo only).
