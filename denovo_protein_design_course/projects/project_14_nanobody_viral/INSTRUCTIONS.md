# Project 14 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — graded as part of reproducibility. Tasks are tagged
`[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

**Defensive framing (read first):** every design is steered to a **conserved neutralizing** epitope to
*block* the virus. Enhancing viral fitness/affinity/escape is out of scope (`README.md` → Responsible
research, `MASTER_BLUEPRINT.md §7`). Get advisor sign-off on your epitope before the campaign (P2).

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand VHH/CDR structure and pick a conserved neutralizing epitope + framework.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): RFantibody (Bennett 2025), ImmuneBuilder (Abanades 2023), a HA-stem/RSV-F prefusion immunogen paper. Half-page on conserved neutralizing epitopes. `[core]`
  - **Verify every accession** in `data/README.md` on RCSB/UniProt; note superseded entries. `[core]`
- **Week 2**
  - Choose the epitope (conserved, neutralizing) + a humanized VHH framework; write a 1-page problem statement with measurable success criteria (breadth across N strains) + controls. `[core]`
  - Reproduce the "hello-world": run `00_setup.ipynb`, then the mini-run in `01_define_and_explore.ipynb` (mock). `[core]`

**D0 deliverable:** epitope + framework choice + problem statement (criteria + controls) + reproduced mini-run.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal VHH pipeline producing a first small batch.

- **Week 3:** Repo + `LOG.md`; confirm `env/requirements.txt` on Colab; clean the antigen target (chain selection, define the conserved epitope residues). `[core]`
- **Week 4:** Reproduce a small RFantibody run (tiny demo on free tier; A100 for real). `[core]`
- **Week 5:** Minimal pipeline end-to-end on ~10 VHHs (mock → real); parse AF2-Multimer `pae_interaction` + CDR geometry. `[core]`
- **Week 6:** Visualize the first batch; note compute budget per 100 designs. `[extension]`

**D1 deliverable:** working minimal VHH pipeline + first design batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real VHH CDR design campaign (500+, given the low hit rate).

- **Weeks 7–8:** RFantibody CDR design campaign (aim for 500+ designs) at the conserved epitope. `[core]`
- **Weeks 9–10:** Score all with AF2-Multimer + IgFold (CDR geometry) + developability heuristics. BoltzGen nanobody-mode run for the head-to-head. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the pool; finalize the design log (config + seed + output); interim report. `[core]`

**D2 deliverable:** VHH design pool (500+) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** antibody-aware triage + the breadth analysis.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`, `design_type="antibody"`); honest survival accounting. `[core]`
- **Weeks 15–16:** Developability/humanness gate (TAP/CamSol/humanness — swap in real tools); **cross-strain breadth** (AF2-Multimer `pae_interaction` across the strain panel; worst-case). `[core]`
- **Weeks 17–18:** RFantibody vs BoltzGen head-to-head (hit rate, CDR geometry, developability); CDR Ramachandran sanity. `[core]` / `[extension]`

**D3 deliverable:** ranked + developability-filtered candidates + cross-strain breadth + filtering report.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and plan a controlled, biosafe display screen.

- **Weeks 19–20:** Orthogonal checks (IgFold/ESMFold); finalize the breadth table; flag escape-prone (narrow) designs. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **yeast-display screen plan** (pool → FACS vs labeled antigen → sequence winners → express → SPR) + a **neutralization/breadth plan** (pseudovirus surrogate across strains, IBC-approved), controls (a known neutralizing nanobody positive, an irrelevant-antigen negative, a scrambled-CDR negative), timeline, cost. State biosafety/IBC oversight explicitly. `[core]`

**D4 deliverable:** yeast-display screen plan + neutralization/breadth plan (controls, biosafety, cost).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, reproducible release.

- **Week 23:** Thesis-chapter report (Abstract · Intro · Methods w/ versions+params · Results w/ hit rates + breadth + developability · Discussion w/ failure forensics · Screen plan · References · Reproducibility). `[core]`
- **Week 24:** 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks).
- Dual-use questions → `MASTER_BLUEPRINT.md §7` + advisor, **before** designing.
