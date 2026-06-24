# Project 24 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This project follows the **enzyme-family template** (Project 18): cofactor-site spec → scaffold pocket
→ LigandMPNN (coordinating residues fixed) → coordination-geometry filter. The difference: the "active
site" is a **cofactor-coordination pocket** (default: **bis-His heme**), the goal is **coordination /
incorporation** of a redox/O₂ cofactor (not catalysis), and the assay is **spectroscopy** (UV-vis
Soret / EPR). Keep two messages front of mind all semester: *a design is a hypothesis* and
**coordination geometry ≠ cofactor incorporation ≠ function — only spectroscopy confirms it.**

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand de novo metalloprotein design + cofactor coordination, and reproduce the hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): a designed-heme/de-novo-metalloprotein
    paper (DeGrado maquettes or Baker lab), Dauparas 2024 (LigandMPNN), a cytochrome/ferredoxin
    reference, Watson 2023 (RFdiffusion). Write a half-page on the state of de novo cofactor-binder
    design and the honest history (coordination achievable; tuning function is the hard part). `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (1MBN, the b-type cytochrome candidate,
    the ferredoxin candidate); cofactor proteins have many variants and entries get superseded. Note
    which you could and could not confirm. `[core]`
  - Read the **coordination chemistry**: for your cofactor, which residues coordinate the metal, the
    metal-ligand distances, the coordination number/polyhedron, and how oxidation/spin state changes
    the geometry (bis-His heme = two axial His, Fe-N ~2.0-2.2 Å, His-Fe-His ~180°). `[core]`
- **Week 2**
  - **Choose your cofactor + coordination scheme** (default **bis-His heme**; alternatives: His/Met
    heme, proximal-His O₂-binding heme, [4Fe-4S]-4Cys ferredoxin, Cys2His2 Zn). Write a 1-page
    **problem statement** with explicit, *measurable* success criteria (e.g. "N designs with
    coordination-geometry RMSD < 0.5 Å and site pLDDT ≥ 90") and the controls you will need (apo
    protein, coordinating-residue→Ala mutant). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then `01_define_and_explore.ipynb`
    (mock `build_cofactor_spec` → coordinating-group geometry table + a mock scaffold). `[core]`
  - Start filling `data/inputs/cofactor_site_def.txt` with real geometry read off your verified
    reference structure (replace the PLACEHOLDERs); cite each value. `[extension]`

**D0 deliverable:** problem statement (cofactor choice + success criteria + controls) + printout of the
reproduced cofactor-site hello-world (coordinating-group spec + a mock scaffold record).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  `cofactor_tools.py` smoke test; confirm the mock spec→scaffold→sequence path runs end-to-end with no
  GPU. `[core]`
- **Week 4:** Finalise the **cofactor-site spec** (`data/inputs/cofactor_site_def.txt`): the cofactor,
  the coordinating residues (e.g. the two axial His), and the metal-ligand distances/angles read off
  your **verified** reference structure (myoglobin / b-type cytochrome / ferredoxin). Encode them in
  `cofactor_tools.build_cofactor_spec` (override the `CoordinatingGroup` values) and cite sources. `[core]`
- **Week 5:** Run a **small real scaffolding demo** — RFdiffusion motif scaffolding (free-tier T4) for
  tens of backbones presenting the coordination motif; or run the mock path at scale if no GPU yet.
  Then **cofactor-aware LigandMPNN** on a couple of backbones with the **coordinating residues fixed**
  and the cofactor passed as context. `[core]`
- **Week 6:** Predict the small batch with AF2/ESMFold; compute a first **coordination-geometry RMSD**
  for each (remember AF2 gives the apo backbone — place the metal/cofactor first); visualise the best
  site. Write a short "what worked / what's slow / what's my A100 budget" note. `[extension]`

**D1 deliverable:** working minimal pipeline + first (small) design batch with coordination-geometry
RMSD computed + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering).

- **Weeks 7–8:** **Scaffold at scale** — 1000s of backbones presenting the coordination motif with
  **RFdiffusion2 / Riff-Diff** (A100/HPC; verify the current release first). Cofactor-pocket placement
  is harder than a single-sidechain motif (e.g. two axial His on opposite helices at the right Fe
  distance) — budget extra backbones, batch carefully, and log every config + seed. `[core]`
- **Weeks 9–10:** **Cofactor-aware LigandMPNN sequence design** for every viable backbone, **fixing the
  coordinating residues** and **passing the cofactor as atom context**. Generate several sequences per
  backbone; vary temperature. LigandMPNN is CPU-fast, so this scales easily — the only thing that must
  be right is the fixed-positions list + the cofactor context. `[core]` Explore scaffolding parameters
  / coordination-scheme variants. `[extension]`
- **Weeks 11–12:** Assemble the full design pool (backbones × sequences); predict with AF2/ESMFold
  triage (read **site pLDDT**); finalise the **design log** (every config + seed + output path).
  Interim report. `[core]`

**D2 deliverable:** full design pool (scaffolds + cofactor-aware LigandMPNN sequences with coordinating
residues fixed) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`,
  `design_type="enzyme"`). Build `fp.Design` objects carrying `plddt`, `plddt_catalytic` (here =
  **site** pLDDT), `scrmsd`, and `catalytic_geom_rmsd` (here = **coordination**-geometry RMSD); run
  `fp.run_pipeline(...)` + `fp.report(...)`; produce the survival-at-each-layer figure. Cutoffs:
  scrmsd ≤ 2.0, plddt ≥ 85, **plddt_cat ≥ 90 (site), cat_geom ≤ 0.5 (coordination)**. `[core]`
- **Weeks 15–16:** Run the project's benchmark: **coordination-geometry preservation rate** (what
  fraction of designs hold the coordination motif within 0.5 Å after prediction) and a **cofactor /
  coordination-scheme comparison** (e.g. bis-His heme vs His/Met heme vs [4Fe-4S], and/or a
  coordinating-residue-preservation check: does LigandMPNN keep all ligands?). `[core]` / `[extension]`
- **Weeks 17–18:** **Cofactor docking** (AutoDock Vina) on survivors to check the cofactor fits the
  pocket and the metal sits between the coordinating ligands, and a **short pocket MD** (OpenMM — note
  the classical-metal-FF caveat) for stability. Rank top candidates; **honest hit-rate accounting**
  (N pass / N generated at each layer). `[core]`

**D3 deliverable:** ranked top candidates + coordination-geometry & cofactor/scheme-comparison benchmark
figures + a filtering report including the survival-at-each-layer analysis and honest hit rate.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Deepen the in-silico case on the top set: confirm the **coordinating-residue
  geometry** holds under AF2 (and an orthogonal predictor), docking poses place the cofactor's metal
  between the ligands, the **site pLDDT** is high, and the pocket is MD-stable (caveated). Reason about
  **redox tuning** — how second-shell residues, the axial-ligand identity (His vs Met), and pocket
  hydrophobicity/polarity would shift the redox midpoint potential or O₂ affinity. Pick the **<96
  designs** for synthesis. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **spectroscopic assay plan**: express in *E. coli*, purify, and confirm
  cofactor binding by **spectroscopy** — **UV-vis Soret band** for heme (position/intensity reports
  coordination + oxidation state; run a **heme/cofactor titration** to a stoichiometric endpoint) **or**
  **EPR** for a [4Fe-4S] cluster / high-spin heme. **Controls (mandatory):** an **apo protein**
  (no cofactor added — baseline), a **coordinating-residue→Ala mutant** (the cleanest negative — same
  protein, no ligand → loss of the coordinated signature pins binding to that residue), and a **natural
  reference** cofactor protein (positive — confirms the assay works). Add a timeline + costed reagent
  list. `[core]`
  - *(Optional, if your lab has capacity)* express the go/no-go tier (express → SDS-PAGE → SEC → record
    a UV-vis spectrum) and run the titration. `[stretch]`

**D4 deliverable:** validation report (geometry + docking + site pLDDT + caveated MD on the <96 set) +
costed, controlled spectroscopic assay plan with the apo + coordinating-residue→Ala controls.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro (de novo metalloproteins as a grand
  challenge) · Methods w/ exact tool versions+params · Results w/ coordination-geometry preservation
  rate, cofactor/scheme comparison, hit-rate accounting · Discussion w/ failure forensics and
  "geometry ≠ incorporation ≠ function" · Spectroscopic-assay + redox-tuning plan · References ·
  Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. Write the
  **redox-tuning / function-engineering plan** for any hits (axial-ligand swaps, second-shell mutations,
  the same spectroscopic readout as the screen). `[stretch]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (+ redox-tuning plan for hits).

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table for RFdiffusion2/Riff-Diff/LigandMPNN/AF2/Vina/OpenMM).
- Conceptual questions (coordination geometry, oxidation/spin state, spectroscopy) → `references/reading_list.md` + advisor office hours.
- Compute limits (the A100 scaffolding step) → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks) + `MANUAL.md §2`.
