# Project 06 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **target-directed binder project**: you design small de novo binders to the PD-1-binding
face of PD-L1 with **two** paradigms and compare them head-to-head. It is also the **binder-family
template** — keep the workflow clean, because Projects 07–13 and 23 will follow it.

> **Compute reality up front (be honest):** a real binder campaign wants an **A100** (Colab Pro+ or a
> cluster). A free **T4** runs only a *small fallback* campaign: FreeBindCraft, a small `num_designs`,
> a small RFdiffusion batch with ESMFold triage. **Do not claim a full binder campaign runs free on
> Colab.** Plan batch sizes around your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand checkpoint blockade + binder design, prep the target, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Pacesa 2025 (BindCraft), Cao 2022
    (target-structure-only minibinders), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN), and
    a PD-1/PD-L1 structural-biology review. Write a half-page on the state of the field. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (4ZQK, 5O45 are *candidates*). Note
    any superseded entries; record the resolution, chains, and which chain is PD-L1. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N
    designs passing all binder layers with `pae_interaction` ≤ 10 and `rosetta_dG` ≤ −30") and the
    controls you will need (positive known binder, scrambled-interface negative, unrelated protein). `[core]`
  - **Target prep:** clean the PD-L1 ectodomain (IgV domain), remove PD-1 and waters, and from the
    PD-1/PD-L1 interface identify the **PD-1-binding hotspot residues** on PD-L1 (the competitive
    epitope). Reproduce the "hello-world": run `00_setup.ipynb` then the mock mini-run in
    `01_define_and_explore.ipynb`. `[core]`

**D0 deliverable:** problem statement (with success criteria + controls) + a cleaned target +
hotspot list + screenshot/printout of the reproduced mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/ColabDesign/ColabFold URLs). `[core]`
- **Week 4:** Finalize target prep — fix the PD-L1 chain, define hotspot residues as the binder
  target, and decide binder length range (40–80 aa is typical for minibinders). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a **BindCraft mini-run** (a few
  designs) on A100, or the `mock` backend if you only have a T4 this week, and a small RFdiffusion
  binder batch → ProteinMPNN. `[core]`
- **Week 6:** Run AF2-Multimer on those few designs; visualize the binder–PD-L1 interface; write a
  short "what worked / what's slow / what's my A100 budget per 100 designs" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline (target → designs → AF2-Multimer → metrics) +
first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real two-paradigm campaign at scale (diversity before filtering).

- **Weeks 7–8:** **BindCraft campaign** — 50–200 designs against the PD-1-face hotspots (A100; on a
  T4, FreeBindCraft with a smaller `num_designs`). Log every config, seed, and the hotspot set. `[core]`
- **Weeks 9–10:** **RFdiffusion binder campaign** — 500–1000 backbones in binder mode against the
  same hotspots → ProteinMPNN sequence design (several sequences per backbone). Explore noise scale /
  hotspot subsets. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble **both** pools into one results table (one row per design, tagged by
  paradigm); finalize the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** the two-paradigm design pool (BindCraft + RFdiffusion, `results/*.csv`) +
complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the head-to-head benchmark that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Report survival-at-each-layer for each paradigm. `[core]`
- **Weeks 15–16:** Run the **BindCraft-vs-RFdiffusion benchmark**: hit rate, interface-energy
  (`rosetta_dG`) distribution, shape complementarity, and **novelty** (TM-score to PDB). Build the
  comparison figures. `[core]` / `[extension]`
- **Weeks 17–18:** Select **top 10–20 each**; do **epitope-competition reasoning vs PD-1** (does the
  binder overlap the PD-1 footprint enough to block it?); honest hit-rate accounting (N pass / N
  generated at each layer, per paradigm). `[core]` / `[extension]`

**D3 deliverable:** ranked top 10–20 per paradigm + BindCraft-vs-RFdiffusion benchmark figures + a
filtering report including survival-at-each-layer and the epitope-competition analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent
  predictor, finalize the PD-1-competition footprint analysis, and *(stretch)* run **Boltz-2 affinity
  prediction** on the top hits — **scaffold only; report relative ranking + caveats, never a
  fabricated K_D**. `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (E. coli for the
  binders; PD-L1 ectodomain reagent), purification, the right assay (**SPR/BLI** vs immobilized
  PD-L1) + a **PD-1-competition** assay, **controls** (positive: a known PD-L1 binder/antibody Fab;
  negative: a **scrambled-interface** version of your own top design; unrelated-protein negative),
  timeline, and a costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled SPR/BLI + PD-1-competition plan
(+ optional go/no-go wet-lab data).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ hit rates, distributions, and the head-to-head comparison · Discussion w/ failure
  forensics · Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on the two paradigms
The scientific heart of this project is the **head-to-head**: BindCraft (one-shot,
hallucination-based, AF2-in-the-loop) vs RFdiffusion-binder + ProteinMPNN (diffuse a backbone, then
design a sequence). They have different hit rates, diversity, and failure modes. Generate **both**
pools at honest scale, filter **both** identically, and report the comparison — don't cherry-pick a
winner before the data is in.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
