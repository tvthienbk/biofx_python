# Project 03 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **generative backbone-design project**. The central question is empirical and quantitative:
*how much novelty can a monomer afford before it stops folding self-consistently?* You answer it by
mapping a frontier, not by polishing one design. **Diversity before filtering** is the governing rule.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand the novelty↔foldability trade-off deeply and reproduce a working baseline.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): RFdiffusion (Watson 2023), ProteinMPNN/self-consistency (Dauparas 2022), AF2 (Jumper 2021), Foldseek (van Kempen 2024), TM-score/TM-align (Zhang & Skolnick 2004). Write a half-page on the state of generative backbone design and *why novelty trades off against foldability*. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB/UniProt. Note any superseded entries. `[core]`
  - Read `MANUAL.md §1` and write, in your own words, what **scRMSD** and **TM-score/novelty** each measure — and what each does **not** mean (novelty is *not* a pass/fail of correctness). `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "scRMSD < 2 Å for foldable; TM < 0.5 to the PDB for novel") and the controls you will need (a conservative fold; an unrelated control). `[core]`
  - Reproduce the project's "hello-world": run `notebooks/00_setup.ipynb` then `01_define_and_explore.ipynb` to generate 10 backbones (mock backend runs anywhere; switch to the real RFdiffusion ColabDesign call on Colab/A100), measure self-consistency + novelty, and visualize one with py3Dmol. `[core]`

**D0 deliverable:** problem statement (with measurable novelty/foldability criteria + controls) + screenshot/printout of the reproduced 10-backbone tutorial output.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) backbone batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Stand up `scripts/rfdiff_tools.py` and confirm `generate_backbones`, `self_consistency`, and `novelty_tm` all run on the deterministic `mock` backend. `[core]`
- **Week 4:** Wire in the **real backends on Colab/A100**: the RFdiffusion ColabDesign notebook for `generate_backbones`, ProteinMPNN for sequence design, AF2/ESMFold for `self_consistency`. Confirm one real backbone goes generate → MPNN → predict end-to-end. Note the GPU you used. `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a tiny scale (10 backbones at length 80, all-α). Compute scRMSD and a Foldseek/TM-align novelty score for each. `[core]`
- **Week 6:** Produce + visualize the first batch; write a short "what worked / what's slow / what's my compute budget per 100 backbones" note — be explicit that a **T4 handles small batches but the full campaign needs an A100/HPC**. `[extension]`

**D1 deliverable:** working minimal pipeline (generate → MPNN → self-consistency → novelty) + first small batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real design campaign at scale (diversity before filtering).

- **Weeks 7–8:** Scale generation across the grid — lengths {80, 120, 200, 300} × SS-bias {all-α, all-β, mixed} → **hundreds of backbones**. Manage GPU time carefully: a T4 only handles a *slice* of this; reserve the full sweep for an **A100 / HPC** and batch overnight. Log every config + seed. `[core]`
- **Weeks 9–10:** Sequence design with **ProteinMPNN, ~8 sequences/backbone** (temperature ~0.1–0.2); fold each back with AF2 (or ESMFold for fast triage) to compute self-consistency scRMSD per backbone (best-of-8). Parameter exploration: how does MPNN temperature affect scRMSD? `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full design pool into `results/backbones.csv` (one row per backbone: length, ss_bias, scrmsd, plddt, tm_to_pdb, seed); finalize the **design log** (every config + seed + output path). Interim report on early frontier shape. `[core]`

**D2 deliverable:** full backbone pool (`results/backbones.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark/ablation that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`). Build `fp.Design` objects with `design_type="monomer"`, populating `scrmsd`, `plddt`, and `tm_to_pdb`; run `fp.run_pipeline(..., design_type="monomer")` and `fp.report(...)`. **Note: TM-score novelty is *reported*, not filtered as pass/fail** — foldability gates, novelty is a coordinate. `[core]`
- **Weeks 15–16:** Run the project's core analysis: the **novelty-vs-scRMSD Pareto frontier** scatter, plus per-topology and per-length success rates (fraction with scRMSD < 2 Å). Then the benchmark/ablation: **RFdiffusion vs FrameFlow vs Genie2** on diversity / speed / foldability — *scaffold the comparison honestly; do not fabricate numbers* — and the length sweep. `[core]` / `[extension]`
- **Weeks 17–18:** Novelty checks (confirm TM < 0.5 picks are genuinely novel, not artifacts of poor alignment); rank top candidates; **honest hit-rate accounting** (N pass / N generated at each layer, broken down by topology and length). Derive a first-draft **novelty budget**. `[core]`

**D3 deliverable:** ranked top candidates + novelty-vs-scRMSD frontier figure + per-topology/length success-rate tables + a filtering report including survival-at-each-layer.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation (re-fold top picks with the *other* predictor — ESMFold if you used AF2, and vice versa — and confirm agreement); finalize the **novelty budget** guideline. *(Stretch)* run a **short MD stability check** (OpenMM, 10–50 ns) on the top picks to see whether the predicted fold stays put. `[core]` / `[stretch]`
- **Weeks 21–22:** Write the **experimental validation plan**: select a **novel-but-foldable design set**, and a synthesis/expression strategy with **paired controls** — one HIGH-novelty risky design and one conservative (low-novelty, high-confidence) design tested side by side, plus an unrelated-protein control. Specify expression (*E. coli* BL21(DE3)), purification, and characterization assays (SEC, CD, DSF), a timeline, and a costed reagent list. `[core]`
  - *(Optional, if your lab has capacity)* execute the go/no-go tier (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report + costed, controlled synthesis/expression plan + the selected novel-but-foldable set (D★).

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params · Results w/ the frontier, hit rates & distributions · Discussion w/ failure forensics + the novelty budget · Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned `requirements.txt` + version stamp from `00_setup`). `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release, including the **novelty budget guideline**.

---

### A note on scope discipline
The temptation is to chase one spectacular novel fold. Resist it. The deliverable is a **frontier and
a budget**, not a hero design — a campaign that honestly reports *"all-β backbones above length 200
fail self-consistency 90% of the time"* is worth far more than a single lucky scRMSD = 1.1 Å picture.
Generate broadly, filter on foldability, report novelty as a coordinate.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks; the full sweep needs A100/HPC).
