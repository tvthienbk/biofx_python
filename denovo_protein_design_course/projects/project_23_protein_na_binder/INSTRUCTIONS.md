# Project 23 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **nucleic-acid-targeted binder project**: you design a small de novo protein that binds a
**chosen DNA/RNA motif**, using **RFdiffusion** to scaffold near the nucleic acid and the **NA-aware
LigandMPNN** to design the sequence — with a **ProteinMPNN** NA-blind baseline so you can show what the
nucleic-acid conditioning buys you. It follows the **binder-family template**
(`projects/project_06_pdl1_binder/`); the differences are the **nucleic-acid target**, **LigandMPNN** as
the central designer, a **specificity gate**, and an **EMSA / fluorescence-anisotropy** assay.

> **Compute reality up front (be honest):** **RFdiffusion near the nucleic acid** and **protein–NA
> complex modeling** (Boltz-2 / AF3-style) want an **A100** (Colab Pro+ or a cluster).
> **LigandMPNN/ProteinMPNN are CPU-cheap** — they are *not* the bottleneck; the modeling is. A free
> **T4** runs only a *small fallback* (few backbones, a small modeling batch). **Do not claim a full
> campaign runs free on Colab.** Plan batch sizes around your actual GPU (see `MANUAL.md §2` and
> `MASTER_BLUEPRINT.md §3`).
>
> **Protein–NA design is newer and harder than protein–protein** — **sequence specificity** is the
> whole game. Budget for the confidence→specificity drop and for verifying LigandMPNN's NA model +
> RFdiffusion's NA protocol (they evolve).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand protein–NA recognition + LigandMPNN-NA, choose a target motif, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Dauparas 2024 (LigandMPNN — NA support),
    Watson 2023 (RFdiffusion), a protein–DNA/RNA recognition review, Dauparas 2022 (ProteinMPNN), and a
    designed-DNA-binding-protein paper. Write a half-page on the state of the field — emphasizing why
    **specificity** is the hard part. `[core]`
  - **Verify the data accession** in `data/README.md` on RCSB (the protein–NA complex is a *candidate*;
    confirm it is the right protein–DNA/RNA complex, the chains, and the resolution). `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N designs
    passing all confidence layers **and** with `specificity_score ≥ margin`") and the controls you will
    need (**scrambled-NA**, dead-mutant, unrelated protein, positive known binder). `[core]`
  - **Choose your DNA/RNA target motif** (a TF box, operator, RNA hairpin, ...) from the complex/
    literature, write down its **scrambled control**, and decide DNA vs RNA. Reproduce the
    "hello-world": run `00_setup.ipynb` then the mock mini-run in `01_define_and_explore.ipynb`
    (scaffold → LigandMPNN → model → specificity). `[core]`

**D0 deliverable:** problem statement (with success criteria + controls, incl. the scrambled-NA control)
+ chosen DNA/RNA motif + screenshot/printout of the reproduced mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal NA-binder pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (LigandMPNN / RFdiffusion / Boltz / ColabFold URLs) — and check LigandMPNN's
  NA model + RFdiffusion's NA protocol specifically. `[core]`
- **Week 4:** Finalize the target: prepare the NA structure (or the protein–NA complex to scaffold near),
  fix the motif sequence + its scrambled control, decide binder length range (40–90 aa). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a few RFdiffusion backbones near the
  NA (or the `mock` backend if you only have a T4 this week) → LigandMPNN design → a small Boltz-2
  complex model → metrics + specificity. `[core]`
- **Week 6:** Visualize a protein–NA complex (major groove? base contacts? or just the backbone?); write
  a short "what worked / what's slow / what's my A100 budget per 100 complex models" note. `[extension]`

**D1 deliverable:** working minimal NA-binder pipeline (motif → scaffold → LigandMPNN → complex model →
metrics + specificity) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real scaffold-near-NA + LigandMPNN campaign at scale (diversity before filtering).

- **Weeks 7–8:** **RFdiffusion campaign** — scaffold many backbones (hundreds on A100; few on T4) docked
  near the nucleic acid, NA held as context. Log every config, seed, and noise scale. `[core]`
- **Weeks 9–10:** **LigandMPNN (NA-aware)** sequence design — several sequences per backbone, NA in
  context (the central step). On the *same* backbones, also run **ProteinMPNN (NA-blind)** as the
  benchmark baseline. Model each design as a protein–NA complex (Boltz-2 / AF3-style) and score
  motif-vs-scrambled specificity. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble **both** pools into results tables (one row per design, tagged by designer);
  finalize the **design log** (every config + seed + commit + output path). Interim report. `[core]`

**D2 deliverable:** the scaffold-near-NA + LigandMPNN design pool (+ ProteinMPNN baseline,
`results/*.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the LigandMPNN-vs-ProteinMPNN benchmark that makes this a *study*.

- **Weeks 13–14:** Apply the shared 4-layer filter to **both** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`), then
  apply the **specificity gate** (confident **and** prefers the intended motif). Report
  survival-at-each-layer for each designer. `[core]`
- **Weeks 15–16:** Run the **LigandMPNN-vs-ProteinMPNN benchmark**: confidence hit rate, **specificity
  rate**, `pae_interaction` distribution, and the intended-vs-scrambled **specificity scatter**. Build
  the comparison figures; show whether NA conditioning improves specificity. `[core]` / `[extension]`
- **Weeks 17–18:** Select **top confident+specific candidates** per designer; novelty (TM-score to PDB);
  honest **two-number** hit-rate accounting (confidence rate **and** confident-AND-specific rate, per
  designer). `[core]` / `[extension]`

**D3 deliverable:** ranked top confident+specific candidates per designer + LigandMPNN-vs-ProteinMPNN
benchmark + specificity figures + a filtering report including survival-at-each-layer and the
confidence→specificity drop.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation + deepening: re-model top hits with an independent protein–NA
  modeler, finalize the specificity analysis, and *(extension)* the **CRISPR-modulator framing** — bind
  a Cas surface to *modulate* editing (a protein–protein binder problem; reuse the Project 06 workflow,
  optionally with NA context). Keep the framing therapeutic/safety. `[extension]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (E. coli binders;
  synthesized labeled target NA + a scrambled-NA oligo), purification, the right assay (**EMSA** and/or
  **fluorescence anisotropy/polarization** vs the labeled target NA) **repeated against the scrambled-NA
  control**, **controls** (scrambled-NA negative [required]; **dead-mutant** of your own top design;
  unrelated protein; positive known binder), timeline, and a costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* express the top few and run the go/no-go tier (express →
    SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled **EMSA / fluorescence-anisotropy** plan with
**scrambled-NA** controls (+ optional go/no-go wet-lab data).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ **two** hit rates [confidence + specificity], distributions, and the LigandMPNN-vs-ProteinMPNN
  comparison · Discussion w/ failure forensics [non-specific gripping] · Experimental plan · References ·
  Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on the core comparison
The scientific heart of this project is **LigandMPNN (NA-aware) vs ProteinMPNN (NA-blind)** at the
interface, judged on **specificity**, not just confidence. Generate both on the *same* backbones, filter
both identically, gate both on specificity, and report whether nucleic-acid conditioning actually helps
your designs *read the bases*. Don't cherry-pick a winner before the data is in — and remember confidence
≠ specificity, and the computational specificity score is a proxy until the scrambled-NA EMSA/anisotropy.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (A100 need + free-tier fallbacks).
