# Project 09 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **peptide / macrocycle binder project**: you design **linear and cyclic** peptide binders to
the **p53-binding cleft of MDM2**, compare **linear vs cyclic** and **peptide vs mini-protein**
modalities, and write a **peptide-specific** synthesis/validation plan. It follows the **binder-family
template** (Project 06) — the filter and head-to-head workflow are the same; the chemistry (peptides,
macrocycles, SPPS) and the validation are what differ.

> **Compute reality up front (be honest):** peptides are small, so AF2/Boltz-2 scoring and **Boltz-2
> affinity on small inputs run on a free T4**. A **full macrocycle campaign prefers Colab Pro**. The
> notebooks run end-to-end on a deterministic **mock** backend with no GPU so you build the plumbing
> anywhere; switch to the real backends on Colab. **Predicted affinity for short peptides is
> unreliable — rank, never trust an absolute number, and never fabricate a K_D.** Verify the **BoltzGen
> public release** exists before relying on it (it is moving). See `MANUAL.md §2` and
> `MASTER_BLUEPRINT.md §3`.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand PPI inhibition + peptide therapeutics, prep the MDM2 cleft, reproduce a mini-run.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): BoltzGen 2025 (verify the release),
    EvoBind2 (Bryant), Kussie 1996 (MDM2–p53 / 1YCR), a macrocycle/oral-peptide therapeutic review,
    and the Boltz-2 paper. Write a half-page on the state of the field. `[core]`
  - **Verify the data accession** in `data/README.md` on RCSB (**1YCR** is a *candidate*). Note any
    superseded entry; record the resolution, chains, which chain is MDM2, and that the p53 peptide is
    resolved. `[core]`
  - Run `python data/download_data.py`; inspect `data/provenance.csv`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥N
    designs passing all binder layers with `pae_interaction` ≤ 10 and cleft-overlap ≥ 0.5") and the
    controls you will need (positive: a known p53-peptide/stapled peptide; negative: scrambled-sequence
    version of your own design; unrelated peptide). `[core]`
  - **Target cleft prep:** clean the MDM2 N-terminal domain, remove the p53 peptide and waters, and
    from the MDM2–p53 interface identify the **cleft residues** lining the three sub-pockets that bury
    p53 **Phe19 / Trp23 / Leu26** — these are your design site. Reproduce the "hello-world": run
    `00_setup.ipynb` then the mock mini-run in `01_define_and_explore.ipynb` (a few linear + cyclic
    designs). `[core]`

**D0 deliverable:** problem statement (with success criteria + controls) + a cleaned MDM2 target +
cleft-residue list + screenshot/printout of the reproduced mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal peptide pipeline producing a first (small, possibly bad) batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab; run the
  **version-verify cell** (BoltzGen — *verify the release exists* — EvoBind2, Boltz, ColabFold URLs). `[core]`
- **Week 4:** Finalize cleft prep — fix the MDM2 chain, define the cleft residues as the design site,
  and decide your length ranges (linear ~8–20 aa; macrocycle ~7–15 aa) and the cyclization constraint
  you will test. `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a *tiny* scale: a few **linear** and a few
  **macrocyclic** designs (real backend on Colab if available, else the `mock` backend), scored by
  AF2/Boltz-2 pAE. `[core]`
- **Week 6:** Add the **Boltz-2 affinity** *ranking* signal on those few designs (relative only — never
  a K_D); visualize a peptide–MDM2 cleft complex; write a short "what worked / what's slow / is the
  macrocycle arm T4-feasible or do I need Pro" note. `[extension]`

**D1 deliverable:** working minimal peptide pipeline (cleft → linear + cyclic designs → AF2/Boltz-2
metrics) + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real linear + macrocyclic campaign at scale (diversity before filtering).

- **Weeks 7–8:** **Linear peptide campaign** against the cleft — vary **length** (e.g., 8/12/16/20 aa)
  across a few hundred designs (BoltzGen peptide-anything and/or EvoBind2 on Colab; `mock` if no GPU
  this week). Log every config, seed, length, and the cleft set. `[core]`
- **Weeks 9–10:** **Macrocyclic campaign** against the same cleft — vary **length and the cyclization
  constraint** (head-to-tail / side-chain). The macrocycle arm prefers Colab Pro. Explore the
  length/constraint grid. `[core]` / `[extension]`
- **Weeks 11–12:** Generate the **mini-protein foil** (a Project-06-style mini-binder pool against the
  same cleft) for the peptide-vs-protein modality comparison; assemble **all** pools into results
  tables (one row per design, tagged by modality); finalize the **design log**. Interim report. `[core]`

**D2 deliverable:** linear + macrocyclic design pools (+ mini-protein foil, `results/*.csv`) +
complete design log (length/constraint sweep) + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the modality comparisons that make this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter to **all** pools (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`, `fp.run_pipeline(..., design_type="binder")` + `fp.report(...)`).
  Use **AF2 pAE** as the key interface metric; use the **Boltz-2 affinity score for ranking only**.
  Report survival-at-each-layer for each modality. `[core]`
- **Weeks 15–16:** Run the two benchmarks: **linear vs cyclic** (hit rate, pAE, cleft overlap,
  stability/feasibility framing) and **peptide vs mini-protein** (the foil). Build the comparison
  figures. `[core]` / `[extension]`
- **Weeks 17–18:** Select the **top candidates per modality**; do **cleft-engagement reasoning** (does
  the peptide cover the Phe19/Trp23/Leu26 sub-pockets enough to displace p53?); write
  **cyclization-chemistry feasibility notes** (can this ring actually be made — head-to-tail vs
  side-chain, ring size); honest hit-rate accounting (N pass / N generated at each layer, per
  modality). `[core]` / `[extension]`

**D3 deliverable:** ranked top candidates per modality + linear-vs-cyclic and peptide-vs-protein
benchmark figures + a filtering report including survival-at-each-layer and the cleft-engagement +
cyclization-feasibility analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design a **peptide-appropriate** experiment.

- **Weeks 19–20:** Orthogonal validation + deepening: re-predict top hits with an independent predictor
  (AF2 ↔ Boltz-2 agreement), finalize the cleft-engagement footprint analysis, and use **Boltz-2
  affinity** to *prioritize* which hits to synthesize first — **relative ranking + caveats, never a
  fabricated K_D**. `[extension]`
- **Weeks 21–22:** Write the **peptide validation plan** — note that peptides are made by **SPPS** (not
  E. coli), and need **protease-stability** (serum / trypsin / chymotrypsin half-life) and
  **permeability** (PAMPA / Caco-2) assays in addition to binding. Specify the **binding assay**
  (SPR/BLI or fluorescence-polarization displacement of a labeled p53 peptide), the **controls**
  (positive: a known p53-peptide / stapled peptide such as the ATSP-7041 lineage; negative: a
  **scrambled-sequence** version of your own top design; unrelated-peptide negative), timeline, and a
  costed reagent list. `[core]`
  - *(Stretch)* **D-amino-acid / stapling extension:** propose specific modifications (D-substitutions,
    a hydrocarbon staple, N-methylation) to buy protease stability/permeability, and discuss the
    synthesis-complexity trade-off. `[stretch]`

**D4 deliverable:** validation report + costed, controlled **SPPS + protease-stability + permeability**
plan (+ optional stapling/D-amino-acid extension).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params ·
  Results w/ hit rates, distributions, and the linear-vs-cyclic / peptide-vs-protein comparisons ·
  Discussion w/ failure forensics + the "predicted affinity is unreliable" caveat · Experimental plan ·
  References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### A note on the modality comparisons
The scientific heart of this project is **two comparisons**: (1) **linear vs cyclic** — does
cyclization improve predicted engagement, and at what synthesis cost / stability benefit? and (2)
**peptide vs mini-protein** — when is a small peptide/macrocycle the right modality versus a
Project-06-style mini-binder? Generate all arms at honest scale, filter them identically, and report
the comparison — don't cherry-pick a winner before the data is in. And remember: **predicted affinity
for short peptides is unreliable; rank, don't trust.**

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MANUAL.md §2` + `MASTER_BLUEPRINT.md §3` (T4-vs-Pro scoping + the macrocycle arm).
