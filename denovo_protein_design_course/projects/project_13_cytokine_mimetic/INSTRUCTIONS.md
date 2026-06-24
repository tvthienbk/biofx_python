# Project 13 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **target-directed agonist project**: you design a de novo cytokine-mimetic mini-protein that
engages a **chosen IL-2-receptor subunit combination** (e.g., IL-2Rβ/γc) with **tuned selectivity**,
following the Neo-2/15 paradigm. It follows the **binder-family template** (Project 06), with one
defining twist: you model each candidate against **each receptor subunit separately** and report a
**subunit-selectivity profile** — engaging the right subunits is the whole point.

> **Compute reality up front (be honest):** a real agonist campaign wants an **A100** (Colab Pro+ or a
> cluster). A free **T4** runs only a *small fallback* campaign: a small RFdiffusion batch + ESMFold
> triage, or FreeBindCraft with a small `num_designs`. **Do not claim a full campaign runs free on
> Colab.** Plan batch sizes around your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand cytokine signaling + de novo mimetics, choose your target subunits + selectivity, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Silva 2019 (Neo-2/15), Watson 2023
    (RFdiffusion), Pacesa 2025 (BindCraft), Dauparas 2022 (ProteinMPNN), an IL-2/IL-2R structural-biology
    paper, and a JAK/STAT cytokine-signaling review. Write a half-page on the state of the field:
    *why* a de novo IL-2 mimetic, and *what* selectivity buys you clinically. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (2B5I is a *candidate*). Note any
    superseded entries; record resolution, chains, and which chain is IL-2 vs IL-2Rα/β/γc. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - **Choose your target subunits + desired selectivity** and write it down explicitly: e.g.,
    *"βγ-biased agonist — engage the IL-2Rβ/γc surfaces, **avoid** IL-2Rα/CD25, to spare Tregs and
    reduce vascular-leak toxicity"* (the Neo-2/15 choice). Define the **selectivity criterion** you will
    measure (engages β and γc with low `pae_interaction`; α `pae_interaction` stays high). `[core]`
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N designs
    passing all binder layers with `pae_interaction` ≤ 10 to **both** β and γc **and** ≥ 14 to α") and
    the controls you will need (positive: native IL-2 or Neo-2/15 as a reference; negative:
    scrambled-interface; an unrelated mini-protein; and the **binding-but-not-signaling** caveat). `[core]`
  - **Target prep:** from the IL-2/IL-2R complex, isolate the receptor surfaces, **separate** the three
    subunits (IL-2Rα, IL-2Rβ, γc) into individual targets, and read off the IL-2 contact residues on
    each as your **hotspots**. Reproduce the "hello-world": run `00_setup.ipynb` then the mock mini-run
    in `01_define_and_explore.ipynb` (it prints a mock per-subunit selectivity profile). `[core]`

**D0 deliverable:** problem statement (with success criteria + controls) + a written
target-subunit/selectivity choice + per-subunit hotspot lists + screenshot/printout of the reproduced
mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal agonist pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/ColabDesign/ColabFold URLs). `[core]`
- **Week 4:** Finalize target prep — fix the receptor chains, define the **per-subunit hotspots**
  (the surfaces you want to engage vs the one you want to spare), and decide mini-protein length range
  (≈50–90 aa; Neo-2/15 is ~100 aa with a four-helix-bundle topology). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a small RFdiffusion binder batch →
  ProteinMPNN (A100), or the `mock` backend if you only have a T4 this week. `[core]`
- **Week 6:** Run AF2-Multimer on those few designs **against each subunit separately**; build a first
  per-subunit `pae_interaction` table; write a short "what worked / what's slow / what's my A100 budget
  per 100 designs × 3 subunits" note (note that modeling vs 3 subunits ~triples the AF2 cost). `[extension]`

**D1 deliverable:** working minimal agonist pipeline (target → designs → AF2-Multimer **per subunit** →
metrics) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real agonist campaign at scale (diversity before filtering).

- **Weeks 7–8:** **Design campaign** — engage the chosen receptor surfaces. RFdiffusion binder mode:
  500–1000 backbones steered at the IL-2Rβ/γc hotspots → ProteinMPNN (several sequences per backbone);
  and/or a BindCraft campaign (50–200) at the same surfaces. Log every config, seed, and hotspot set. `[core]`
- **Weeks 9–10:** Sequence design (ProteinMPNN `temperature` 0.1–0.3, several seqs/backbone); explore
  noise scale, the hotspot subset (β-only vs β+γc), and length. The agonist must bridge **two** chains
  to dimerize the receptor — keep designs that contact both β and γc. `[core]` / `[extension]`
- **Weeks 11–12:** Score **every** design with AF2-Multimer **against each of the three subunits
  separately**; assemble the pool into one results table (one row per design, with `pae_to_alpha`,
  `pae_to_beta`, `pae_to_gamma`). Finalize the **design log** (every config + seed + output path).
  Interim report. `[core]`

**D2 deliverable:** the agonist design pool (`results/*.csv`, with per-subunit metrics) + complete
design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the **selectivity modeling** that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Filter on the **engaged** subunits (β, γc). Report survival-at-each-layer. `[core]`
- **Weeks 15–16:** Build the **subunit-selectivity profile** (`04_validate.ipynb`): for each design,
  combine `pae_to_alpha / beta / gamma` into a selectivity call (**engages βγ but NOT α**, or whatever
  you chose). Quantify the selectivity margin (e.g., `pae_to_alpha − max(pae_to_beta, pae_to_gamma)`).
  Compare the **stability** of the de novo designs vs the **native cytokine** (the Neo-2/15 selling
  point). Build the figures. `[core]` / `[extension]`
- **Weeks 17–18:** Select **top candidates**; report selectivity vs the native-cytokine interface as the
  benchmark; honest hit-rate accounting (N pass / N generated at each layer, **and** N that are also
  selective). State plainly which survivors are *selective agonist candidates* vs merely *binders*. `[core]`

**D3 deliverable:** ranked top candidates + the **per-subunit selectivity profile** + stability-vs-native
figures + a filtering report including survival-at-each-layer and the selectivity analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment — including the assay that tests *signaling*, not just binding.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent predictor,
  finalize the selectivity-margin analysis, and *(stretch)* run **Boltz-2 affinity prediction** on the
  top hits against each subunit — **scaffold only; report relative ranking + caveats, never a fabricated
  K_D**. *(Stretch)* compute a **thermostability proxy** and compare to native IL-2. `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (E. coli for the
  mini-protein; the receptor-subunit ectodomain reagents), purification, **per-subunit SPR/BLI**
  (measure K_D to IL-2Rα, IL-2Rβ, γc separately → confirm selectivity), **and the functional readout —
  a cell-based STAT-phosphorylation assay** (pSTAT5 by flow/Western on IL-2-responsive cells; dose-
  response; ideally on cells ± CD25 to confirm the α-independence), **controls** (positive: native IL-2
  and/or Neo-2/15; negative: a **scrambled-interface** version of your own top design; unrelated-protein
  negative), timeline, and a costed reagent list. State explicitly that **binding ≠ signaling** — the
  pSTAT5 assay is the one that decides agonism. `[core]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC) + DSF thermostability. `[stretch]`

**D4 deliverable:** validation report + costed, controlled **per-subunit SPR + cell STAT-phosphorylation**
plan (+ optional go/no-go wet-lab + thermostability data).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ hit rates, the selectivity profile, and the stability comparison · Discussion w/ failure
  forensics and the binding-vs-signaling caveat · Experimental plan · References · Reproducibility
  statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on what makes this project hard
The scientific heart of this project is **selectivity + agonism**, and both are subtle. (1) *Selectivity*
means modeling each candidate against **each subunit separately** and showing it engages the ones you
chose and *spares* the one you didn't — a single good interface is not enough. (2) *Agonism* means the
mini-protein must geometrically **dimerize** the receptor chains (β and γc) so the JAK/STAT cascade
fires; **binding is not signaling**, and only a cell-based pSTAT assay can confirm it. Report both
honestly: a beautiful βγ interface that doesn't trigger pSTAT5 is a negative result worth reporting.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
