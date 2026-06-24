# Project 19 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This project follows the **enzyme-family template** (Project 18): theozyme → scaffold → LigandMPNN
(catalytic residues fixed) → catalytic-geometry filter. The twist for PET hydrolases is that the
chemistry is *known* (a serine-hydrolase Ser-His-Asp triad + oxyanion hole) — so the campaign is
decided not by catalytic novelty but by **thermostability**: industrial PET digestion runs hot
(~65–70 °C, where PET becomes accessible) and wild-type IsPETase is fragile there. Keep two messages
front of mind all semester: *a design is a hypothesis* and *in-silico catalytic geometry (and an MD
stability proxy) do not guarantee activity or real thermostability — only assays decide.*

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand serine-hydrolase / PETase catalysis + the thermostability bottleneck, and reproduce the theozyme hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Austin 2018 (IsPETase structure/
    engineering), Tournier 2020 (engineered LCC, *Nature*), Lauko 2025 (de novo serine hydrolases,
    *Science*), Schnettler 2025 (Riff-Diff), Dauparas 2024 (LigandMPNN). Write a half-page on de novo
    enzyme design, the honest hit-rate history, and **why thermostability is the bottleneck for PET
    hydrolysis**. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (IsPETase / cutinase candidates
    **6EQE / 5XJH**); PET-hydrolase entries are numerous and get superseded. Note which you could and
    could not confirm. `[core]`
  - Read the **serine-hydrolase mechanism**: how the His-activated Ser nucleophile attacks the ester
    carbonyl, why the **oxyanion hole** (two backbone-NH donors) stabilises the tetrahedral
    intermediate, and what the acyl-enzyme + deacylation steps look like. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g.
    "N designs with catalytic-geometry RMSD < 0.5 Å, active-site pLDDT ≥ 90, **and** a thermostability
    proxy in the top quartile") and the controls you will need (natural reference, heat-killed, empty
    vector, catalytic-Ser→Ala dead mutant). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then `01_define_and_explore.ipynb`
    (mock `build_theozyme("ester_hydrolysis")` → triad + oxyanion-hole geometry table + a mock scaffold). `[core]`
  - Start filling `data/inputs/theozyme_def.txt` with real geometry from the literature/a QM TS
    model (replace the PLACEHOLDERs); cite each value. `[extension]`

**D0 deliverable:** problem statement (success criteria + controls) + printout of the reproduced
theozyme hello-world (triad + oxyanion-hole spec + mock scaffold record).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run
  the `enzyme_tools.py` smoke test; confirm the mock theozyme→scaffold→sequence→geometry→thermostability
  path runs end-to-end with no GPU. `[core]`
- **Week 4:** Finalise the **theozyme** (`data/inputs/theozyme_def.txt`): the **Ser-His-Asp triad**
  (catalytic Ser-OG, His-NE2, Asp-OD), the **oxyanion hole** (two backbone-NH donors to the carbonyl
  O), and the ester-TS-relative distances/angles from literature/QM. Encode them in
  `enzyme_tools.build_theozyme` and cite sources. `[core]`
- **Week 5:** Run a **small real scaffolding demo** — RFdiffusion motif scaffolding (free-tier T4)
  for tens of backbones presenting the triad+oxyanion motif; or run the mock path at scale if no GPU
  yet. Then LigandMPNN on a couple of backbones with the **catalytic triad fixed**. `[core]`
- **Week 6:** Predict the small batch with AF2/ESMFold; compute a first **catalytic-geometry RMSD**
  for each and a first **thermostability-MD proxy** (RMSF / melting-proxy) on the best; visualise the
  best active site. Write a short "what worked / what's slow / what's my A100 budget for the real
  campaign + the MD ranking" note. `[extension]`

**D1 deliverable:** working minimal pipeline + first (small) design batch with catalytic-geometry
RMSD + a thermostability proxy computed + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering).

- **Weeks 7–8:** **Scaffold at scale** — 1000s of backbones presenting the triad+oxyanion-hole motif
  with **RFdiffusion2 / Riff-Diff** (A100/HPC; verify the current release first). Bias toward
  **thermostable topologies** (compact α/β-hydrolase-like folds). Manage GPU time carefully —
  scaffolding is the compute bottleneck; batch and log every config + seed. `[core]`
- **Weeks 9–10:** **LigandMPNN sequence design** for every viable backbone, **fixing the catalytic
  triad** (pass the ester/TS context + a fixed-positions list covering Ser, His, Asp **and** the
  oxyanion-hole residues). Generate several sequences per backbone; vary temperature. LigandMPNN is
  CPU-fast, so this scales easily. `[core]` Explore scaffolding parameters / motif placement variants;
  optionally start an **engineered-natural** track (graft the triad onto a stable cutinase/IsPETase
  scaffold) to compare against the **fully de novo** track. `[extension]`
- **Weeks 11–12:** Assemble the full design pool (backbones × sequences); predict with AF2/ESMFold
  triage; finalise the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** full design pool (scaffolds + LigandMPNN sequences with the catalytic triad
fixed) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`,
  `design_type="enzyme"`). Build `fp.Design` objects carrying `plddt`, `plddt_catalytic`, `scrmsd`,
  and `catalytic_geom_rmsd`; run `fp.run_pipeline(...)` + `fp.report(...)`; produce the
  survival-at-each-layer figure. Cutoffs: scrmsd ≤ 2.0, plddt ≥ 85, **plddt_cat ≥ 90, cat_geom ≤ 0.5**. `[core]`
- **Weeks 15–16:** Run the project's headline benchmark: **MD-based thermostability ranking** of the
  geometry-passing survivors — a short OpenMM run per candidate giving **RMSF** and a **melting-proxy**
  (e.g. backbone-RMSD growth / fraction of native contacts retained under heating). Then the
  **scaffold comparison: engineered-natural vs fully de novo** scaffolds (which holds the triad *and*
  stays stable?). `[core]` / `[extension]`
- **Weeks 17–18:** **PET-mimic substrate docking** (AutoDock Vina) on survivors to check the pocket
  admits the ester and orients it toward Ser-OG (**pocket accessibility**, not affinity/activity).
  Rank top candidates by combining catalytic geometry + thermostability + pocket accessibility;
  **honest hit-rate accounting** (N pass / N generated at each layer, per track). `[core]`

**D3 deliverable:** ranked top candidates + catalytic-geometry & **thermostability** benchmark
figures + engineered-natural-vs-de-novo comparison + a filtering report including the
survival-at-each-layer analysis and honest hit rate.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Deepen the in-silico case on the top set: confirm the **catalytic-triad geometry**
  holds under AF2 (and an orthogonal predictor), the **thermostability MD** is stable (low RMSF, high
  melting-proxy), and docking orients the PET-mimic ester toward Ser-OG. Pick the **<96 designs** for
  synthesis, **balancing the thermostability ↔ activity trade-off** (don't pick only the most rigid). `[core]` / `[extension]`
- **Weeks 21–22:** Write the **activity + thermostability assay plan**: express in *E. coli*, purify,
  run an **esterase activity assay** — start with a **pNP-ester colorimetric** readout (p-nitrophenyl
  acetate/butyrate; follow p-nitrophenolate at ~405–410 nm) for fast screening, then a **PET-film /
  amorphous-PET digestion assay with HPLC** quantification of released MHET/TPA for the true substrate.
  Measure **thermostability by DSF** (thermal-shift, report Tm). **Controls (mandatory):** a
  **natural/reference** PET hydrolase or cutinase (positive), **heat-killed** enzyme, **empty-vector**
  lysate, and a **catalytic-Ser→Ala "dead" mutant** (the cleanest negative — same protein, no
  nucleophile). Add a timeline + costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* express the go/no-go tier (express → SDS-PAGE → SEC) and a
    quick pNP-ester spot check. `[stretch]`

**D4 deliverable:** validation report (geometry + MD-thermostability + docking on the <96 set) +
costed, controlled activity + DSF assay plan with the catalytic-dead-mutant negative.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro (PET hydrolysis + the
  thermostability bottleneck) · Methods w/ exact tool versions+params · Results w/ catalytic-geometry
  preservation rate, **thermostability ranking**, engineered-natural-vs-de-novo comparison, hit-rate
  accounting · Discussion w/ failure forensics, the **thermostability↔activity trade-off**, and
  "geometry ≠ activity" · Activity + DSF assay plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. Write
  a **surface-residue redesign for solubility** plan (and, optionally, a directed-evolution plan)
  for any hit. `[stretch]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (+ surface-redesign /
directed-evolution plan for hits).

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table for RFdiffusion2/Riff-Diff/LigandMPNN/AF2/Vina/OpenMM-thermostability).
- Conceptual questions (triad, oxyanion hole, ester TS, thermostability) → `references/reading_list.md` + advisor office hours.
- Compute limits (the A100 scaffolding + thermostability-MD steps) → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks) + `MANUAL.md §2`.
