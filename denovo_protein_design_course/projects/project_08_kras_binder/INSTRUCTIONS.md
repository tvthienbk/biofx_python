# Project 08 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **target-directed binder project** against a famously **hard** oncotarget: you design small
de novo binders to a chosen **KRAS** surface (switch I/II or an allele-specific pocket) in a defined
**nucleotide state**, with **two** paradigms, and the scientific heart is **selectivity** — across
**alleles** and across the **HRAS/NRAS isoforms**. It reuses the **binder-family template** (Project
06) and adds a KRAS-specific isoform-specificity layer.

> **Compute reality up front (be honest):** a real binder campaign wants an **A100** (Colab Pro+ or a
> cluster). A free **T4** runs only a *small fallback* campaign: FreeBindCraft, a small `num_designs`,
> a small RFdiffusion batch with ESMFold triage. **Do not claim a full binder campaign runs free on
> Colab.** Plan batch sizes around your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand KRAS druggability + binder design, choose the epitope/allele/state, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): a KRAS druggability/structural-biology
    review, the G12C-inhibitor papers (sotorasib/adagrasib), Pacesa 2025 (BindCraft), Cao 2022
    (target-structure-only minibinders), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN). Write
    a half-page on why KRAS was "undruggable" and what changed. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (4OBE, 6OIM are *candidates*; you also
    need **HRAS/NRAS** for the panel). For each, record the **allele**, the **nucleotide state**
    (GDP vs GTP/analog), the chain, and the resolution. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N
    designs passing all binder layers with `pae_interaction` ≤ 10 and `rosetta_dG` ≤ −30, **and** a
    KRAS-vs-best-off-target `pae` gap ≥ X") and the controls you will need (positive known KRAS binder,
    scrambled-interface negative, unrelated protein, **isoform panel**, **nucleotide-state test**). `[core]`
  - **Choose the epitope, allele, and nucleotide state on purpose:** switch I (~res 30–38), switch II
    (~res 60–76), or an allele pocket (e.g. the G12C cysteine); GDP "off" vs GTP/analog "on". Clean the
    chosen KRAS structure (isolate the chain, keep the bound nucleotide + Mg²⁺ where the switch depends
    on them, remove waters), and read the hotspots off **that** structure/state. Reproduce the
    "hello-world": run `00_setup.ipynb` then the mock mini-run in `01_define_and_explore.ipynb`. `[core]`

**D0 deliverable:** problem statement (with success criteria + controls) + a documented
epitope/allele/nucleotide-state choice + cleaned target + hotspot list + printout of the reproduced
mock mini-run (with its mock isoform panel).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/ColabDesign/ColabFold URLs). `[core]`
- **Week 4:** Finalize target prep — fix the KRAS chain, lock the **nucleotide state**, define the
  hotspot residues as the binder target, and decide the binder length range (≈50–90 aa for KRAS — a
  fair contact area helps on a small, smooth surface). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a **BindCraft mini-run** (a few
  designs) on A100, or the `mock` backend if you only have a T4 this week, and a small RFdiffusion
  binder batch → ProteinMPNN. `[core]`
- **Week 6:** Run AF2-Multimer on those few designs; visualize the binder–KRAS interface at the switch
  regions; run a first **mock isoform panel** (KRAS vs HRAS/NRAS) to see the plumbing; write a short
  "what worked / what's slow / what's my A100 budget per 100 designs" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline (target → designs → AF2-Multimer → metrics + a
first isoform-panel pass) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real two-paradigm campaign at scale (diversity before filtering).

- **Weeks 7–8:** **BindCraft campaign** — 50–200 designs against the chosen KRAS epitope (A100; on a
  T4, FreeBindCraft with a smaller `num_designs`). Log every config, seed, the hotspot set, the allele,
  and the **nucleotide state**. `[core]`
- **Weeks 9–10:** **RFdiffusion binder campaign** — 500–1000 backbones in binder mode against the same
  hotspots → ProteinMPNN sequence design (several sequences per backbone, temperature 0.1–0.3). Explore
  noise scale / hotspot subsets (switch I vs switch II vs combined). `[core]` / `[extension]`
- **Weeks 11–12:** Assemble **both** pools into one results table (one row per design, tagged by
  paradigm, allele, and state); finalize the **design log** (every config + seed + output path).
  Interim report. `[core]`

**D2 deliverable:** the two-paradigm design pool (BindCraft + RFdiffusion, `results/*.csv`) + complete
design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark + the **specificity analysis** that makes this a *study*.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Report survival-at-each-layer for each paradigm. `[core]`
- **Weeks 15–16:** Run the **benchmark + the isoform-specificity analysis**: BindCraft-vs-RFdiffusion
  hit rate, interface-energy (`rosetta_dG`) distribution, novelty (TM-score to PDB); and — the
  centerpiece — **model each survivor vs HRAS/NRAS** (`isoform_specificity` / `specificity_panel`) and
  compute the **selectivity gap** (KRAS `pae` vs best off-target `pae`). Build the comparison figures.
  `[core]` / `[extension]`
- **Weeks 17–18:** Select **top 10–20 each**; do **allele-selectivity reasoning** (does the binder
  exploit the allele-specific surface?) and, as `[extension]`, **effector-competition framing** (does
  the switch-region footprint overlap enough to block RAF/effector engagement?); honest hit-rate
  accounting (N pass / N generated at each layer, per paradigm). `[core]` / `[extension]`

**D3 deliverable:** ranked top 10–20 per paradigm + benchmark figures + **isoform-specificity analysis
(selectivity gap per paradigm)** + a filtering report including survival-at-each-layer.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment around **selectivity**.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent
  predictor, finalize the **isoform-specificity panel** (KRAS vs HRAS/NRAS) and the effector-competition
  footprint analysis, and *(stretch)* run **Boltz-2 affinity prediction** on the top hits — **scaffold
  only; report relative ranking + caveats, never a fabricated K_D**. `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (E. coli for the
  binders; KRAS in the correct **nucleotide-loaded** state as the reagent — load GDP vs GppNHp), the
  right assay (**SPR/BLI** vs immobilized KRAS), an **isoform-specificity panel** (test the binder vs
  KRAS, HRAS, and NRAS), **controls** (positive: a known KRAS binder; negative: a **scrambled-interface**
  version of your own top design; unrelated-protein negative), a **nucleotide-state-dependence test**
  (does binding change between GDP- and GTP-loaded KRAS?), timeline, and a costed reagent list. `[core]`
  - *(Stretch)* design the **nucleotide-state-dependence** experiment in detail (load GDP vs GppNHp;
    expect a state-specific binder to discriminate). `[stretch]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled plan whose centerpiece is the **SPR/BLI +
isoform-specificity panel** with scrambled-interface and nucleotide-state controls (+ optional go/no-go
wet-lab data).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro on KRAS druggability · Methods w/ exact
  versions+params+commits · Results w/ hit rates, distributions, the head-to-head, **and the isoform
  selectivity gap** · Discussion w/ failure forensics + why selectivity is hard · Experimental plan ·
  References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on what makes this project hard
KRAS generation is the easy part. The three decisions that make or break the campaign are **(1) the
epitope** (a small, charged, smooth surface — switch I/II or an allele pocket), **(2) the nucleotide
state** (the switch surface only exists in one state), and **(3) selectivity** (KRAS, HRAS, and NRAS
are nearly identical across the switches, so a binder that hits one usually hits all three). Generate
**both** paradigms at honest scale, filter **both** identically, run the **isoform panel** on
survivors, and report the selectivity gap honestly — a binder that binds KRAS *and* HRAS/NRAS is a far
weaker result than a selective one, and you must say so.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
