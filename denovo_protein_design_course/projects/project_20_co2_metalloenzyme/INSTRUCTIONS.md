# Project 20 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This follows the **enzyme-family template** (Project 18): theozyme → scaffold → LigandMPNN (catalytic
residues fixed) → catalytic-geometry filter — specialised here to a **metal active site**. Carbonic
anhydrase is the model: a **Zn-His₃-OH** centre that hydrates CO₂ near the diffusion limit. Keep three
messages front of mind all semester: *a design is a hypothesis*, *in-silico metal geometry does not
guarantee activity*, and *geometry does not even guarantee the metal binds* — that is a separate,
measured check (ICP).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand de novo metalloenzyme design + the CA mechanism, and reproduce the metal-site theozyme hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Hu 2024 (GRACE), Dauparas 2024
    (LigandMPNN), a carbonic-anhydrase mechanism paper, a de novo metalloprotein review (DeGrado).
    Write a half-page on the state of de novo **metalloenzyme** design and the honest GRACE hit-rate
    story (large pool + screening). `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (2CAB / 3KS3 are *candidates*); CA
    has many deposited variants and entries get superseded. Note which you could/could not confirm. `[core]`
  - Read the **CA mechanism**: how the Zn lowers the water pKa to ~7, how the **Zn-hydroxide** attacks
    CO₂, and why **three His** + a proton-shuttle His are the canonical groups. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g.
    "N designs with metal-ligand RMSD < 0.5 Å, active-site pLDDT ≥ 90, and a clean Zn-N₃ tetrahedron")
    and the controls you'll need (natural CA, **apo** enzyme, ligand→Ala metal-knockout). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then `01_define_and_explore.ipynb`
    (mock `build_theozyme("co2_hydration")` → Zn-His₃-OH spec + a mock scaffold). `[core]`
  - Start filling `data/inputs/metal_site_def.txt` with real Zn-N distances / N-Zn-N angles read off a
    verified CA structure (replace the PLACEHOLDERs); cite each value. `[extension]`

**D0 deliverable:** problem statement (success criteria + controls) + printout of the reproduced
metal-site theozyme hello-world (Zn-His₃-OH spec + mock scaffold record).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) design batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  `enzyme_tools.py` smoke test; confirm the mock theozyme→scaffold→**metal-aware** sequence path runs
  end-to-end with no GPU. `[core]`
- **Week 4:** Finalise the **metal site** (`data/inputs/metal_site_def.txt`): the Zn ion, the three
  His ligand atoms (NE2/ND1), the Zn-bound hydroxide, with real Zn-N distances + N-Zn-N angles from a
  verified CA structure / QM TS. Encode them in `enzyme_tools.build_theozyme` and cite sources. `[core]`
- **Week 5:** Run a **small real scaffolding demo** — RFdiffusion motif scaffolding (free-tier T4) for
  tens of backbones presenting the Zn + His₃ motif; or run the mock path at scale if no GPU yet. Then
  **metal-aware LigandMPNN** on a couple of backbones with the **three His ligands fixed** + the Zn as
  atom context. `[core]`
- **Week 6:** Predict the small batch with AF2/ESMFold; compute a first **metal-ligand geometry**
  (Zn-N distances, N-Zn-N angles, RMSD) for each — remember **AF2 does not place the Zn**, so add it
  from the His₃ geometry. Visualise the best metal site. Write a short "what worked / what's slow /
  what's my A100 budget for the ~10k pool" note. `[extension]`

**D1 deliverable:** working minimal pipeline + first (small) design batch with metal-ligand geometry
computed + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering — GRACE used ~10k).

- **Weeks 7–8:** **Scaffold at scale** — a **large pool** of backbones presenting the Zn-His₃ motif
  with **RFdiffusion2 / Riff-Diff** (A100/HPC; verify the current release first). Metal-site placement
  is harder than a sidechain motif, so budget extra backbones. Manage GPU time carefully —
  scaffolding is the bottleneck; batch and log every config + seed. `[core]`
- **Weeks 9–10:** **Metal-aware LigandMPNN sequence design** for every viable backbone, **fixing the
  three His ligands** and **passing the Zn as atom context** (`--ligand_mpnn_use_atom_context 1`).
  Generate several sequences per backbone; vary temperature. LigandMPNN is CPU-fast, so this scales.
  Also run a **metal-blind ProteinMPNN** set on the same backbones (His positions fixed, no metal
  context) for the notebook-04 benchmark. `[core]` Explore scaffolding parameters / metal-motif
  placement variants. `[extension]`
- **Weeks 11–12:** Assemble the full design pool (backbones × sequences); predict with AF2/ESMFold
  triage; add the **CLEAN-style functional classification** + a solubility score (GRACE-style triage);
  finalise the **design log** (every config + seed + output path). Interim report. `[core]`

**D2 deliverable:** full design pool (scaffolds + metal-aware LigandMPNN sequences with the His₃
ligands fixed, plus the ProteinMPNN baseline set) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmarks that make this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`,
  `design_type="enzyme"`). Build `fp.Design` objects carrying `plddt`, `plddt_catalytic`, `scrmsd`,
  and **`catalytic_geom_rmsd`** (= the **metal-ligand RMSD**); run `fp.run_pipeline(...)` +
  `fp.report(...)`; produce the survival-at-each-layer figure. Cutoffs: scrmsd ≤ 2.0, plddt ≥ 85,
  **plddt_cat ≥ 90, cat_geom ≤ 0.5**. Add solubility + CLEAN-style functional classification. `[core]`
- **Weeks 15–16:** Run the project's benchmarks: **LigandMPNN vs ProteinMPNN at the metal site**
  (metal-geometry preservation rate — does the metal context help hold the Zn-N₃ cage?) and
  **pool-size vs hit-rate** (subsample the pool; how does the survivor count scale — does it justify
  ~10k?). `[core]` / `[extension]`
- **Weeks 17–18:** **Substrate fit** (AutoDock Vina) on survivors — does CO₂ / the pNPA proxy reach
  the Zn-OH? — and a **short metal-site MD** (OpenMM) for stability, **with the classical-metal-FF
  caveat written down**. Rank top candidates; **honest hit-rate accounting** (N pass / N generated at
  each layer). `[core]`

**D3 deliverable:** ranked top candidates + metal-geometry preservation, LigandMPNN-vs-ProteinMPNN,
and pool-size-vs-hit-rate benchmark figures + a filtering report with the survival-at-each-layer
analysis and honest hit rate.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Deepen the in-silico case on the top set: confirm the **metal-ligand geometry**
  holds under AF2 (and an orthogonal predictor), the substrate reaches the Zn-OH, the site is
  MD-stable (caveated), and the CLEAN-style classifier agrees. Pick the **<96 designs** for synthesis.
  `[core]` / `[extension]`
- **Weeks 21–22:** Write the **activity + metal-incorporation assay plan**: express in *E. coli*,
  purify, run the **esterase-proxy assay** (pNPA → p-nitrophenolate, a fast chromogenic readout)
  and/or the **CO₂-hydration assay** (Wilbur-Anderson units — rate of pH drop), and **check metal
  incorporation by ICP-MS / a PAR colorimetric assay** (does Zn actually bind?). **Controls
  (mandatory):** a **natural CA** (positive), the **apo enzyme** (metal stripped with chelator — the
  metalloenzyme analogue of a dead mutant), an **empty-vector** lysate, and a **buffer-only** blank
  (CO₂ hydration and pNPA both have non-zero uncatalysed rates — subtract them). Add a timeline +
  costed reagent list. `[core]`
  - **Alternative metal — Co(II) substitution** test: Co(II) is active in CA and is spectroscopically
    visible (unlike Zn(II)); plan an apo→Co(II) reconstitution + a UV-vis/activity check as an
    orthogonal confirmation that the designed site is a real metal site. `[stretch]`
  - *(Optional, if your lab has capacity)* express the go/no-go tier (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report (geometry + CLEAN + caveated MD on the <96 set) + costed,
controlled activity + metal-incorporation assay plan (apo + natural-CA controls; ICP metal check).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro (CA as the CO₂-hydration model +
  GRACE) · Methods w/ exact tool versions+params + your metal-site MD model · Results w/ metal-geometry
  preservation rate, LigandMPNN-vs-ProteinMPNN, pool-size-vs-hit-rate, hit-rate accounting ·
  Discussion w/ failure forensics and "geometry ≠ metal incorporation ≠ activity" · Activity +
  metal-incorporation assay plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. Write
  up the **Co(II)-substitution** stretch result/plan and any directed-evolution path for hits. `[stretch]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release (+ Co-substitution /
evolution plan for hits).

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table for RFdiffusion2/Riff-Diff/LigandMPNN/ProteinMPNN/AF2/CLEAN/Vina/OpenMM).
- Conceptual questions (metal site, Zn-OH mechanism, coordination geometry) → `references/reading_list.md` + advisor office hours.
- Compute limits (the A100 large-pool scaffolding step) → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks) + `MANUAL.md §2`.
