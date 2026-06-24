# Project 07 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — graded as part of reproducibility. Tasks are tagged
`[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

**Defensive framing (read first):** every design in this project is steered to *block / neutralize*
the virus at the ACE2-binding face. Enhancing viral fitness, affinity, or escape is out of scope (see
`README.md` → Responsible research and `MASTER_BLUEPRINT.md §7`). Get advisor sign-off on your epitope
choice before the campaign (P2).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the target and pick a defensible, conserved epitope.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): de novo ACE2-mimetic/RBD minibinders (Cao 2020), BindCraft (Pacesa 2025), RFdiffusion (Watson 2023). Write a half-page on conserved vs variable RBD epitopes. `[core]`
  - **Verify every accession** in `data/README.md` on RCSB/UniProt; note superseded entries. `[core]`
- **Week 2**
  - Map **conserved RBD epitopes** (conservation across sarbecoviruses/variants); write a 1-page problem statement with measurable success criteria (e.g., predicted breadth across N variants) and controls. `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then the mini-run in `01_define_and_explore.ipynb` (mock backend). `[core]`

**D0 deliverable:** conserved-epitope map + problem statement (success criteria + controls) + reproduced mini-run output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal binder pipeline producing a first small batch.

- **Week 3:** Set up the repo + `LOG.md`; confirm `env/requirements.txt` on Colab; clean the RBD target structure (chain selection, remove ACE2, define the epitope hotspots). `[core]`
- **Week 4:** Reproduce a small BindCraft mini-run against the chosen epitope (FreeBindCraft on free tier). `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on ~10 designs (mock → real); parse AF2-Multimer `pae_interaction`. `[core]`
- **Week 6:** Visualize the first batch; write a "what's slow / compute budget per 100 designs" note. `[extension]`

**D1 deliverable:** working minimal binder pipeline + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real two-paradigm design campaign at the conserved epitope.

- **Weeks 7–8:** BindCraft campaign (50–200 designs) at the conserved epitope; manage GPU budget. `[core]`
- **Weeks 9–10:** RFdiffusion binder campaign (500–1000 backbones → ProteinMPNN → AF2-Multimer). `[core]`
- **Weeks 11–12:** Assemble the full pool; finalize the design log (config + seed + output per run); interim report. `[core]`

**D2 deliverable:** full design pool (both paradigms) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** triage + the breadth analysis that makes this a study, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`, `design_type="binder"`); honest survival-at-each-layer. `[core]`
- **Weeks 15–16:** **Breadth:** model each top binder vs a panel of variant RBDs (AF2-Multimer `pae_interaction` across variants); report the **worst-case** variant, not the best. Compare conserved- vs variable-epitope targeting. `[core]` / `[extension]`
- **Weeks 17–18:** Head-to-head BindCraft vs RFdiffusion (hit rate, interface energy, novelty); ACE2-competition reasoning (does the binder cover the ACE2 footprint?). `[core]`

**D3 deliverable:** ranked top candidates + cross-variant breadth analysis + filtering report with survival accounting.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design a controlled, biosafe experiment.

- **Weeks 19–20:** Orthogonal prediction (ESMFold/Boltz) on top hits; finalize the breadth table across the variant panel; Boltz-2 affinity as a *relative rank* only (never a K_D). `[core]` / `[extension]`
- **Weeks 21–22:** Write the **validation + breadth-testing plan**: expression, SPR/BLI vs RBD, **ACE2-competition** assay, **pseudovirus neutralization** across the variant panel (standard BSL-2 surrogate, with IBC approval), controls (a known neutralizing binder positive, a scrambled-interface negative, an irrelevant-antigen negative), timeline, costed reagents. State biosafety/IBC oversight explicitly. `[core]`

**D4 deliverable:** validation report + costed, controlled breadth-testing plan (with biosafety oversight).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a reproducible release.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ versions+params · Results w/ hit rates + breadth distributions · Discussion w/ failure forensics · Validation plan · References · Reproducibility statement). `[core]`
- **Week 24:** 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks).
- Dual-use questions → `MASTER_BLUEPRINT.md §7` + advisor, **before** designing.
