# Project 10 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **defensive anti-AMR binder project**: you design small de novo binders to the **NDM-1
di-zinc active-site rim** to **occlude substrate access and inhibit** the enzyme (restore carbapenem
efficacy), with **two** paradigms, and you reason explicitly about *inhibition* (binding ≠
inhibition). It follows the **binder-family template** (Project 06, PD-L1); the twists are the di-zinc
target prep, the occlusion + off-target-specificity analysis, and the enzyme-kinetics inhibition assay.

> **Compute reality up front (be honest):** a real binder campaign wants an **A100** (Colab Pro+ or a
> cluster). A free **T4** runs only a *small fallback* campaign: FreeBindCraft, a small `num_designs`,
> a small RFdiffusion batch with ESMFold triage. **Do not claim a full binder campaign runs free on
> Colab.** Plan batch sizes around your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

> **Responsible-research reminder (read before Week 1):** the goal is to **inhibit** NDM-1 so a
> last-resort antibiotic works again. It is **out of scope** to enhance resistance, pathogen fitness,
> or to protect/stabilize the enzyme. Keep every design framed as an inhibitor / β-lactam adjuvant.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand AMR + metallo-β-lactamase biology + binder design, prep the di-zinc target, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): an NDM-1 / metallo-β-lactamase
    structure paper, a metallo-β-lactamase-inhibitor review, Pacesa 2025 (BindCraft), Dauparas 2024
    (LigandMPNN), Watson 2023 (RFdiffusion). Write a half-page on why NDM-1 has no clinical inhibitor
    and what "occlusion" means here. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (3SPU, 4EYL are *candidates*). Note
    any superseded entries; record the resolution, chains, and — critically — that **both Zn²⁺ ions
    are present** in the model you choose. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N
    designs passing all binder layers with `pae_interaction` ≤ 10, `rosetta_dG` ≤ −30, **and**
    `occlusion` ≥ 0.5") and the controls you will need (off-target human-metalloenzyme control,
    scrambled-interface negative, a no-binder enzyme-only positive control for the assay). `[core]`
  - **Target prep (the di-zinc twist):** clean NDM-1, **keep both catalytic Zn²⁺ ions as heteroatoms**
    (do NOT strip the metals), remove waters/buffer/hydrolyzed-substrate ligands, and read off the
    **active-site-rim residues** (the walls of the substrate-access groove around the di-zinc site) as
    your **occluding hotspots**. Do **not** design over the Zn-coordinating residues themselves.
    Reproduce the "hello-world": run `00_setup.ipynb` then the mock mini-run in
    `01_define_and_explore.ipynb`. `[core]`

**D0 deliverable:** problem statement (success criteria incl. an occlusion threshold + controls) +
cleaned di-zinc target (Zn preserved) + active-site-rim hotspot list + screenshot/printout of the
reproduced mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/**LigandMPNN**/ColabFold URLs). `[core]`
- **Week 4:** Finalize target prep — fix the NDM-1 chain, **confirm both Zn²⁺ are retained**, define
  the active-site-rim hotspot residues as the binder target, and decide binder length (40–80 aa is
  typical for minibinders). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a **BindCraft mini-run** (a few
  designs) on A100, or the `mock` backend if you only have a T4 this week, and a small RFdiffusion
  binder batch → **LigandMPNN** (Zn-aware). `[core]`
- **Week 6:** Run AF2-Multimer on those few designs; visualize the binder–NDM-1 interface and check it
  sits over the substrate-access rim (not a distal patch); write a short "what worked / what's slow /
  what's my A100 budget per 100 designs" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline (target → designs → AF2-Multimer → metrics) +
first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real two-paradigm campaign at scale (diversity before filtering).

- **Weeks 7–8:** **BindCraft campaign** — 50–200 designs against the **active-site-rim** hotspots
  (A100; on a T4, FreeBindCraft with a smaller `num_designs`). Keep the di-zinc target intact. Log
  every config, seed, and the hotspot set. `[core]`
- **Weeks 9–10:** **RFdiffusion binder campaign** — 500–1000 backbones in binder mode against the same
  rim hotspots → **LigandMPNN** sequence design (Zn-aware near the metal; several sequences per
  backbone). Explore noise scale / hotspot subsets (rim vs distal is the ablation). `[core]` /
  `[extension]`
- **Weeks 11–12:** Assemble **both** pools into one results table (one row per design, tagged by
  paradigm); finalize the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** the two-paradigm design pool (BindCraft + RFdiffusion→LigandMPNN, `results/*.csv`)
+ complete design log + 3–4 page interim report.

---

## Phase 3 — Filter, occlusion & specificity (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the occlusion/specificity analysis that makes this an *inhibitor* study, not a sticker demo.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Report survival-at-each-layer for each paradigm. `[core]`
- **Weeks 15–16:** **Substrate-occlusion modeling** — for survivors, score how much of the
  carbapenem-access channel each binder occludes (`occlusion_score`; pocket-volume / SASA proxy on
  Colab). **Specificity vs human metalloenzymes** — counter-test each design against a panel
  (carbonic anhydrase, an MMP, glyoxalase II) with `offtarget_specificity`; a di-zinc binder that
  hits human Zn-enzymes is a safety liability. `[core]` / `[extension]`
- **Weeks 17–18:** Run the **BindCraft-vs-RFdiffusion benchmark** (hit rate, interface energy,
  occlusion, specificity, novelty) and the **epitope ablation** (active-site rim vs a distal patch:
  the distal patch should bind but **not** occlude). Select **top 10–20 each**; honest hit-rate
  accounting (N pass / N generated at each layer, per paradigm). `[core]` / `[extension]`

**D3 deliverable:** ranked top 10–20 per paradigm + occlusion + specificity-vs-human-metalloenzymes
analysis + BindCraft-vs-RFdiffusion benchmark + rim-vs-distal ablation + a filtering report including
survival-at-each-layer.

---

## Phase 4 — Validate (in silico) + plan the inhibition assay (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment that tests *inhibition*.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent
  predictor, finalize the occlusion footprint analysis over the di-zinc site, and *(stretch)* sketch
  the **β-lactam-adjuvant** concept (binder + carbapenem restoring efficacy) and/or a Boltz-2
  affinity scaffold — **scaffold only; report relative ranking + caveats, never a fabricated number.**
  `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: express NDM-1 and the binders;
  the right assay is an **enzyme-kinetics INHIBITION assay** — **nitrocefin** (chromogenic
  cephalosporin) or a **carbapenem-hydrolysis** readout — measuring **IC50** (and ideally K_i + mode
  of inhibition), with **controls**: an **off-target human-metalloenzyme** control (the binder must
  NOT inhibit it), a **scrambled-interface** negative version of your own top design (must LOSE
  inhibition), and enzyme-only / no-inhibitor positive controls; timeline, and a costed reagent list.
  **`[stretch]`** add a **β-lactam-adjuvant** checkerboard (binder + meropenem MIC restoration in a
  resistant strain). `[core]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC), then a preliminary nitrocefin inhibition screen. `[stretch]`

**D4 deliverable:** validation report + costed, controlled **nitrocefin/carbapenem inhibition (IC50)**
plan (off-target-metalloenzyme + scrambled-interface controls; β-lactam-adjuvant stretch).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro: AMR + why NDM-1 has no inhibitor ·
  Methods w/ exact versions+params (incl. LigandMPNN, di-zinc prep) · Results w/ hit rates,
  occlusion/specificity distributions, the head-to-head, and the rim-vs-distal ablation · Discussion
  w/ failure forensics and the binding≠inhibition caveat · Experimental plan · References ·
  Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on mechanism (the heart of this project)
The scientific heart here is **inhibition mechanism**, not just affinity. Three things make this an
*inhibitor* project: (1) the hotspots are on the **active-site rim** so the binder **occludes**
substrate; (2) the **occlusion score** distinguishes a *blocker* from a mere *sticker*; (3) the
**specificity** counter-test vs human metalloenzymes guards safety. And the non-negotiable caveat:
**binding ≠ inhibition** — only the enzyme-kinetics assay (IC50) in notebook 05 measures it.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
