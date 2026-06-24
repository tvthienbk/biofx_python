# Project 11 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **conformation-specific binder project**: you design small de novo binders to the **fibril**
surface of tau (Alzheimer's) or α-synuclein (Parkinson's) with **two** paradigms, then prove
(in silico) that they **prefer the fibril over the monomer**. It follows the **binder-family template**
(Project 06); the project-specific addition is the **conformational-specificity** test.

> **Compute reality up front (be honest):** a real binder campaign wants an **A100** (Colab Pro+ or a
> cluster), and you run AF2-Multimer **twice per design** (fibril and monomer), so budget accordingly.
> A free **T4** runs only a *small fallback* campaign: FreeBindCraft, a small `num_designs`, a small
> RFdiffusion batch with ESMFold triage. **Do not claim a full binder campaign runs free on Colab.**
> Plan batch sizes around your actual GPU (see `MANUAL.md §2` and `MASTER_BLUEPRINT.md §3`).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand amyloid/fibril structural biology + binder design, choose the target conformation,
prep the fibril surface, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Fitzpatrick 2017 (tau PHF cryo-EM), a
    Schweighauser/α-syn fibril paper, Pacesa 2025 (BindCraft), Watson 2023 (RFdiffusion), Dauparas 2022
    (ProteinMPNN), and an amyloid-PET-tracer / conformational-antibody reference. Write a half-page on
    the state of the field — emphasize **why conformational selectivity is the crux.** `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (tau **5O3L/5O3T**, α-syn **6CU7/6H6B**
    are *candidates*). Note any superseded entries; record the ordered-core range, chains, and which
    chains form a protofilament. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N designs
    passing all binder layers with `pae_interaction` ≤ 10 AND a `specificity_gap` ≥ chosen margin") and
    the controls you will need (positive conformational anti-fibril antibody, **scrambled-interface**
    negative, **monomer** negative, unrelated negative). `[core]`
  - **Target-conformation choice + fibril prep:** isolate one protofilament, keep the ordered cross-β
    core, remove waters/heteroatoms, and from the **exposed fibril surface** identify the **epitope
    residues** (the hotspots). Assemble a **monomer model** (AFDB/ensemble) for the counter-test and
    note the disorder caveat. Reproduce the "hello-world": run `00_setup.ipynb` then the mock mini-run
    in `01_define_and_explore.ipynb` (including the monomer-vs-fibril gap preview). `[core]`

**D0 deliverable:** problem statement (with success criteria + controls) + a cleaned fibril
protofilament + fibril-surface epitope list + a monomer model + screenshot/printout of the reproduced
mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BindCraft/FreeBindCraft/RFdiffusion/ColabDesign/ColabFold URLs). `[core]`
- **Week 4:** Finalize fibril prep — fix the protofilament chains, define the exposed-surface epitope
  residues as the binder target, decide binder length range (50–90 aa is typical when spanning a flat
  cross-β groove), and lock the **monomer** counter-test model. `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a **BindCraft mini-run** (a few
  designs) on A100, or the `mock` backend if you only have a T4 this week, and a small RFdiffusion
  binder batch → ProteinMPNN, then **score both conformers** (fibril + monomer) on a couple of
  designs. `[core]`
- **Week 6:** Run AF2-Multimer on those few designs (both conformers); visualize a binder–fibril
  interface; write a short "what worked / what's slow / what's my A100 budget per 100 designs (×2 for
  two conformers)" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline (fibril target → designs → AF2-Multimer (fibril +
monomer) → metrics + `specificity_gap`) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real two-paradigm campaign at scale against the fibril (diversity before filtering).

- **Weeks 7–8:** **BindCraft campaign** — 50–200 designs against the fibril-surface epitope (A100; on a
  T4, FreeBindCraft with a smaller `num_designs`). Log every config, seed, and the epitope set. `[core]`
- **Weeks 9–10:** **RFdiffusion binder campaign** — 500–1000 backbones in binder mode against the same
  fibril surface → ProteinMPNN sequence design (several sequences per backbone). Explore noise scale /
  epitope subsets. Expect an **even lower** per-backbone hit rate than a typical globular target — the
  flat cross-β surface is hard. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble **both** pools into one results table (one row per design, tagged by
  paradigm); finalize the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** the two-paradigm design pool (BindCraft + RFdiffusion, `results/*.csv`) against the
fibril + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the **conformational-specificity** analysis that is the heart of this
project, plus the head-to-head benchmark.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Report survival-at-each-layer for each paradigm (this ranks **fibril** binders). `[core]`
- **Weeks 15–16:** Run the **conformational-specificity test** (`04_validate.ipynb`): model each
  survivor vs the **monomer** and the **fibril**, compute `specificity_gap = pae_monomer − pae_fibril`,
  define + **justify** a selectivity margin (`GAP_MIN`), and report the **fibril-selective** fraction
  per paradigm. Build the selectivity figures (gap distribution, the selectivity quadrant). `[core]`
- **Weeks 17–18:** Run the **BindCraft-vs-RFdiffusion benchmark** (hit rate, interface energy, novelty)
  and the **cross-amyloid** specificity extension (tau vs α-syn); select **top fibril-selective 10–20
  each**; honest accounting (N pass / N generated / N selective, per paradigm). `[core]` / `[extension]`

**D3 deliverable:** ranked top fibril-selective candidates + the **fibril-vs-monomer specificity
analysis** + BindCraft-vs-RFdiffusion benchmark figures + cross-amyloid figures + a filtering report
including survival-at-each-layer and the selective-fraction accounting.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment around the selectivity readout.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent
  predictor (both conformers), finalize the cross-amyloid analysis, and *(stretch)* run **Boltz-2
  affinity prediction** on the top hits — **scaffold only; report relative ranking + caveats, never a
  fabricated K_D or selectivity ratio**. `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (E. coli for the
  binders; recombinant tau / α-synuclein with **matched monomer + in-vitro-fibril preps**, confirmed by
  ThT + TEM/cryo-EM), the right assay (**fibril-vs-monomer ELISA/SPR** — the selectivity test) + a
  **cross-amyloid** readout, **controls** (positive: a known conformational anti-fibril antibody/tracer;
  negative: a **scrambled-interface** version of your own top design; **monomer** negative;
  unrelated-protein negative), the **diagnostic-tracer** framing (PET / assay; BBB + radiochemistry as
  the translational path), a timeline, and a costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC) + a quick ThT-fibril binding check. `[stretch]`

**D4 deliverable:** validation report + costed, controlled **fibril-vs-monomer** ELISA/SPR plan
(+ optional go/no-go wet-lab data) with the diagnostic-tracer framing.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ fibril hit rates, the **selective fraction**, distributions, and the head-to-head ·
  Discussion w/ failure forensics — including how many failed the **monomer counter-test** ·
  Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on the hard part
The scientific heart of this project is **conformational selectivity**: a binder that grips the
fibril and **rejects the monomer**. It is much harder than a normal binder problem, and **most designs
will fail the monomer counter-test** — that is the expected, honest outcome. Report the selective
fraction and the failure modes; do not cherry-pick the one design with the biggest gap. The
`specificity_gap` is an in-silico proxy on a model metric (and the monomer is disordered, so its model
is itself uncertain) — selectivity is only **proven** by the fibril-vs-monomer assay.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks; remember
  two conformers per design doubles the AF2-Multimer cost).
