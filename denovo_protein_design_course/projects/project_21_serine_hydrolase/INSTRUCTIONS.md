# Project 21 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This project follows the **enzyme-family template** (Project 18, Kemp eliminase): theozyme → scaffold
→ LigandMPNN (catalytic residues fixed) → catalytic-geometry filter. Your reaction is **ester
hydrolysis** via the **Ser-His-Asp triad + oxyanion hole**, and your headline is reproducing the
**2025 Science de novo serine-hydrolase** result on a general esterase. Keep two messages front of
mind all semester: *a design is a hypothesis* and *in-silico catalytic geometry does not guarantee
activity — the pNP-ester assay (with the Ser→Ala dead mutant) decides.*

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand de novo enzyme design + the serine-hydrolase mechanism, and reproduce the theozyme hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Lauko 2025 (de novo serine
    hydrolases), Schnettler 2025 (Riff-Diff), Dauparas 2024 (LigandMPNN), Dauparas 2025
    (RFdiffusion2), and an alpha/beta-hydrolase mechanism reference. Write a half-page on the state of
    de novo enzyme design and the honest hit-rate reality. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (the candidate cutinase/lipase
    references); serine-hydrolase entries are numerous and get superseded. Note which you could and
    could not confirm. `[core]`
  - Read the serine-hydrolase **mechanism**: how His activates Ser-OG, how Ser-OG attacks the ester
    carbonyl to form the **tetrahedral intermediate**, why the **oxyanion hole** is decisive, and the
    acyl-enzyme/deacylation steps. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g. "N designs
    with catalytic-geometry RMSD < 0.5 Å, active-site pLDDT ≥ 90, and a substrate that docks oriented
    toward Ser-OG") and the controls you will need (natural reference, empty vector, **catalytic-Ser→Ala
    dead mutant**). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then `01_define_and_explore.ipynb`
    (mock `build_theozyme` → triad + oxyanion-hole geometry table + a mock scaffold). `[core]`
  - Start filling `data/inputs/theozyme_def.txt` with real geometry from the literature/a QM
    tetrahedral-intermediate model (replace the PLACEHOLDERs); cite each value. `[extension]`

**D0 deliverable:** problem statement (success criteria + controls) + printout of the reproduced
theozyme hello-world (triad + oxyanion-hole spec + mock scaffold record).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  `enzyme_tools.py` smoke test; confirm the mock theozyme→scaffold→sequence→dead-mutant path runs
  end-to-end with no GPU. `[core]`
- **Week 4:** Finalise the **theozyme** (`data/inputs/theozyme_def.txt`): the catalytic Ser/His/Asp
  triad **and the oxyanion-hole donors**, with tetrahedral-intermediate-relative distances/angles
  from literature/QM. Encode them in `enzyme_tools.build_theozyme` and cite sources. `[core]`
- **Week 5:** Run a **small real scaffolding demo** — RFdiffusion motif scaffolding (free-tier T4) for
  tens of backbones presenting the motif; or run the mock path at scale if no GPU yet. Then LigandMPNN
  on a couple of backbones with the **triad + oxyanion-hole donors fixed**. `[core]`
- **Week 6:** Predict the small batch with AF2/ESMFold; compute a first **catalytic-geometry RMSD** for
  each; dock a pNP-ester to eyeball **pocket accessibility**; visualise the best active site. Write a
  short "what worked / what's slow / what's my A100 budget" note. `[extension]`

**D1 deliverable:** working minimal pipeline + first (small) design batch with catalytic-geometry RMSD
computed + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering).

- **Weeks 7–8:** **Scaffold at scale** — 1000s of backbones presenting the triad + oxyanion-hole motif
  with **RFdiffusion2 / Riff-Diff** (A100/HPC; verify the current release first). Bias toward compact
  alpha/beta-hydrolase-like folds with an open, solvent-accessible pocket. Manage GPU time carefully —
  scaffolding is the compute bottleneck; batch and log every config + seed. `[core]`
- **Weeks 9–10:** **LigandMPNN sequence design** for every viable backbone, **fixing the catalytic
  triad AND the oxyanion-hole donors** (pass the ligand/ester-TS context + a fixed-positions list).
  Generate several sequences per backbone; vary temperature. LigandMPNN is CPU-fast, so this scales
  easily. `[core]` Explore scaffolding parameters / pocket-lining variants for different acyl-chain
  lengths. `[extension]`
- **Weeks 11–12:** Assemble the full design pool (backbones × sequences); predict with AF2/ESMFold
  triage; finalise the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** full design pool (scaffolds + LigandMPNN sequences with the catalytic triad fixed)
+ complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`,
  `design_type="enzyme"`). Build `fp.Design` objects carrying `plddt`, `plddt_catalytic`, `scrmsd`, and
  `catalytic_geom_rmsd`; run `fp.run_pipeline(...)` + `fp.report(...)`; produce the
  survival-at-each-layer figure. Cutoffs: scrmsd ≤ 2.0, plddt ≥ 85, **plddt_cat ≥ 90, cat_geom ≤ 0.5**. `[core]`
- **Weeks 15–16:** Run the project's benchmark: **catalytic-geometry preservation rate** (what fraction
  of designs hold the triad within 0.5 Å after prediction) and a **scaffolding-method comparison**
  (RFdiffusion2 vs Riff-Diff vs classic motif scaffolding). `[core]` / `[extension]`
- **Weeks 17–18:** **Pocket accessibility** — dock the pNP-ester (AutoDock Vina) on survivors to check
  the pocket fits the substrate and the carbonyl points at Ser-OG; **short active-site MD** (OpenMM)
  for stability; **substrate-scope** scan across the acyl-chain series (C2/C4/C6/C8) to read
  esterase- vs lipase-like preference. `[extension]` Rank top candidates; **honest hit-rate
  accounting** (N pass / N generated at each layer). `[core]`

**D3 deliverable:** ranked top candidates + catalytic-geometry, pocket-accessibility & scaffolding-
method benchmark figures + a filtering report including the survival-at-each-layer analysis and honest
hit rate.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Deepen the in-silico case on the top set: confirm the **triad geometry** holds under
  AF2 (and an orthogonal predictor), docking poses orient the ester toward Ser-OG, the active site is
  MD-stable, and record each design's predicted **substrate scope** (which acyl chains fit). Pick the
  **<96 designs** for synthesis. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **pNP-ester kinetic-assay plan**: express in *E. coli*, purify, run the
  **pNP-ester steady-state assay** (follow p-nitrophenolate release at ~405 nm), fit steady-state
  **kcat/KM**; add **DSF** for fold/stability. **Controls (mandatory):** a **natural/reference serine
  hydrolase** (positive), **empty-vector** lysate, a **blank** (buffer + substrate, for the non-
  enzymatic background rate), and the **catalytic-Ser→Ala "dead" mutant** (the cleanest negative — same
  fold, no nucleophile; loss of activity pins catalysis to the serine). Add a timeline + costed reagent
  list. `[core]`
  - Sketch the **enantioselectivity** concept: a chiral pNP-ester / kinetic-resolution readout and the
    E-value, and which pocket features set face selectivity. `[stretch]`
  - *(Optional, if your lab has capacity)* express the go/no-go tier (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report (geometry + docking + MD + substrate scope on the <96 set) +
costed, controlled pNP-ester kinetic-assay + DSF plan with the catalytic-Ser→Ala dead-mutant negative.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro (serine hydrolases as the biocatalysis
  workhorse + the Lauko-2025 frontier) · Methods w/ exact tool versions+params · Results w/
  catalytic-geometry preservation rate, pocket-accessibility/substrate-scope, method comparison,
  hit-rate accounting · Discussion w/ failure forensics and "geometry ≠ activity" · pNP-ester
  kinetic-assay + DSF plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. Flesh out
  the **enantioselectivity / kinetic-resolution** plan for any hit (chiral-ester E-value screen). `[stretch]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (+ enantioselectivity
plan for hits).

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table for RFdiffusion2/Riff-Diff/LigandMPNN/AF2/Vina/OpenMM).
- Conceptual questions (triad mechanism, oxyanion hole, tetrahedral-intermediate geometry) → `references/reading_list.md` + advisor office hours.
- Compute limits (the A100 scaffolding step) → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks) + `MANUAL.md §2`.
