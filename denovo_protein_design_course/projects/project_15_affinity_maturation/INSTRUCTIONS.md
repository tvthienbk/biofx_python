# Project 15 — Student Instructions (24 weeks)

How to use this guide: each phase ends in a graded **deliverable (D0–D5)**. Keep a running `LOG.md`
(date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are tagged `[core]`
(everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This project follows the **antibody-family template** (Project 17): the workflow is light ESM-1v/AbLang
+ ProteinMPNN scoring → AF2-Multimer pose check → developability → `design_type="antibody"` filter →
a SMALL ranked set + an SPR/DSF validation plan. The twist: you are **maturing an EXISTING antibody**,
not designing one. Framework FIXED; only CDR positions vary; never fabricate KD/ΔΔG.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand affinity maturation + developability, choose your complex, and reproduce the mock hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): ESM-1v (Meier 2021), AbLang (Olsen
    2022), SAbDab (Dunbar 2014), TAP developability (Raybould 2019), an affinity-maturation review.
    Write a half-page on the state of computational antibody maturation — including the **honest fact
    that most predicted improvers do not validate**. `[core]`
  - **Choose your antibody-antigen complex on SAbDab** (a therapeutic Fab-antigen complex WITH a
    published KD); **verify** the accession on RCSB (current, well-resolved interface) and **confirm the
    KD** exists in a primary paper. Record the exact KD + citation. `[core]`
  - Run `data/download_data.py` (set your accession; or `--dry-run`); inspect `provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement**: the chosen complex, its **measured literature KD**, the CDR
    **contact residues** you will target, measurable success criteria (e.g., "propose ≤10 ranked
    mutations; ≥1 should test as improved at a pre-registered margin"), and the controls. `[core]`
  - Derive the CDR boundaries with a real numbering scheme (IMGT/Kabat/Chothia via **ANARCI**) on your
    verified antibody chain — these are the only mutable positions. `[core]`
  - Reproduce the "hello-world": run `00_setup.ipynb`, then `01_define_and_explore.ipynb` on the `mock`
    backend (score 5 single mutations, assemble a tiny ranked set, pose-check + liability-scan it). `[core]`

**D0 deliverable:** problem statement (complex + measured KD + CDR contacts + success criteria +
controls) + printout of the reproduced mock hello-world (top-ranked single mutations + SYNTHETIC pose/
liability metrics).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal maturation pipeline producing a first (mock, then tiny-real) scored batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  full mock pipeline (`01`→`05`) end-to-end so the plumbing is solid before any GPU spend. `[core]`
- **Week 4:** Prepare inputs: clean the verified complex PDB, extract the parent antibody chain + the
  antigen, and **compute the paratope** (CDR residues within ~4.5 Å of antigen) — these are your
  priority contact positions. Fix the framework. `[core]`
- **Week 5:** Run a **tiny real scoring demo** (free-tier feasible — scoring is light): score a handful
  of single CDR mutations with **ESM-1v**, score the chain with **AbLang**, and run one **ProteinMPNN**
  CDR redesign with the framework masked. Pin every tool commit. `[core]`
- **Week 6:** Run one **AF2-Multimer** pose check on a single variant complex (the heavy step — time it),
  visualize the complex + paratope (py3Dmol), and write a short "what's light vs heavy / my AF2 batch
  budget per N variants" note. `[extension]`

**D1 deliverable:** working minimal maturation pipeline + first scored batch (mock + a tiny real demo) +
initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real candidate-generation campaign (broad scoring, then a small set).

- **Weeks 7–8:** Score **single CDR mutations** exhaustively: every allowed CDR position × the 19
  substitutions, with the **ESM-1v ensemble** (the 5 esm1v models) + **AbLang** naturalness. This is the
  cheap, high-value pass — CPU/T4 fine. `[core]`
- **Weeks 9–10:** Run **ProteinMPNN CDR redesigns** (framework FIXED via a design mask), one CDR at a
  time, to catch multi-residue loop changes single-mutation scanning misses. Explore temperature /
  sequences-per-loop. Cross-check redesigns with AbLang. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the **candidate mutation set** into `results/campaign.csv` (single mutations
  + redesigns, with ranking scores); finalize the **design log** (parent, framework, CDR spans, scan
  settings, MPNN params, seed, tool/commit). Interim report. `[core]`
  - *(Optional)* compare ESM-1v vs AbLang vs ProteinMPNN agreement on which positions/substitutions they
    favor — the benchmark you deepen in P3. `[extension]`

**D2 deliverable:** candidate mutation set (`campaign.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the pose/developability/epistasis study that makes this a *study*.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`)
  with `design_type="antibody"` (scRMSD ≤ 3.0, pLDDT ≥ 70, pae_interaction ≤ 12) — this enforces
  **pose maintenance**. Run **AF2-Multimer** on the candidate set (the heavy step — **batch overnight**,
  keep N small). Report survival at each layer and the honest accounting. `[core]`
- **Weeks 15–16:** Benchmark/ablation: **ESM-1v vs AbLang vs ProteinMPNN agreement** (do they pick the
  same mutations?) and **single vs combined** mutations. Build the pose-maintenance figure
  (pae_interaction vs scRMSD vs parent). `[core]` / `[extension]`
- **Weeks 17–18:** **Developability liability scan** — flag candidates that introduce NG/DG deamidation,
  Met/Trp oxidation, N-glyc sequons, or unpaired Cys into the CDRs; drop them. **Epistasis/combination
  reasoning** — propose a few pairwise combos, re-check the pose. Rank the **small** final set with
  honest accounting (swap in real TAP/CamSol/deamidation tools for any reportable developability claim).
  `[core]` / `[extension]`

**D3 deliverable:** antibody-filtered ranked candidates + pose-maintenance/developability/epistasis
figures + a filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen pose/specificity confidence and design the experiment that measures affinity for real.

- **Weeks 19–20:** Orthogonal/specificity deepening: re-predict the top candidates' complexes (a second
  predictor, e.g., ESMFold/IgFold scRMSD as Layer 2), confirm the pose holds, and model the survivors
  against an **off-target antigen** to confirm specificity did not broaden. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **SPR-kinetics + DSF validation plan** (`05_validation_plan.ipynb`): express
  the SMALL ranked variant set; measure **SPR/BLI** kinetics (kon/koff → **KD**, vs the parent's measured
  KD) with a pre-registered improvement margin; confirm stability by **DSF** (Tm); run the **specificity
  panel**; specify the mandatory **controls** — **WT parent** (the measured-KD baseline) + a
  **destabilizing decoy** (expected loss, proves the assay detects a loss) + the specificity panel;
  costed reagent list + timeline. `[core]`
  - *(Stretch)* design a tiny **combinatorial block** (best singles + their pairwise combos) and the
    epistasis read-out (does the combo beat the best single?). `[stretch]`

**D4 deliverable:** validation report + SPR-kinetics/DSF plan + controls (WT + destabilizing decoy +
specificity panel) + costed, controlled experimental plan.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro w/ the lead + its measured KD · Methods
  w/ exact tools/commits/params · Results w/ the ranked set, pose/developability, and the *honest
  expected validation rate* · Discussion w/ failure forensics · SPR/DSF plan · References ·
  Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (scoring is light/T4-OK; AF2-Multimer is the heavy step — batch it).
