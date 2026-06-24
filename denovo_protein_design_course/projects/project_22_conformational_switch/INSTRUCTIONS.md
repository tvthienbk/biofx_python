# Project 22 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **multi-state generative-design project at the frontier of the field**. The central
question is hard and concrete: *can ONE sequence fold to TWO defined states and switch between them
on a trigger?* You answer it by **defining the two states**, searching for a shared sequence with
multi-state ProteinMPNN, validating **both** states, and reasoning honestly about the energy gap.
**Diversity before filtering**, and **a design is a hypothesis** — doubly so here, because even AF2
may only show you one of the two states.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand allostery + multi-state design deeply and reproduce a working baseline.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): LOCKR (Langan 2019), a hinge / two-state design paper, a multi-state ProteinMPNN / ensemble-design reference, RFdiffusion (Watson 2023), AF2 (Jumper 2021), an allosteric-design review, OpenMM (Eastman 2017). Write a half-page on the state of multi-state / switch design and **why one sequence rarely satisfies two states**. `[core]`
  - **Verify every data accession** in `data/README.md` on RCSB (LOCKR / hinge / LOV designs are deposited under varied names — confirm each; note superseded entries). `[core]`
  - Read `MANUAL.md §1` and write, in your own words, what **per-state scRMSD** and the **state energy gap** each measure — and what each does **not** mean (the gap proxy is *not* a real ΔΔG; a low per-state scRMSD is *not* proof the switch toggles). `[core]`
- **Week 2**
  - Write a 1-page **problem statement** by filling in `data/inputs/two_state_def.txt`: the **two states + the trigger** (pH / ligand / light / temperature), explicit *measurable* success criteria (per-state scRMSD < 2 Å for BOTH states; an energy gap inside the switchable band; a defined read-out), and the **controls** (a single-state "locked" negative; an unrelated control). `[core]`
  - Reproduce the project's "hello-world": run `notebooks/00_setup.ipynb` then `01_define_and_explore.ipynb` to define a mock two-state problem, design one shared sequence (mock multi-state MPNN), predict **both** states, and compute the energy gap (mock backend runs anywhere; switch to the real RFdiffusion/MPNN/AF2 calls on Colab/A100). `[core]`

**D0 deliverable:** problem statement (two states + trigger + measurable criteria + controls) + screenshot/printout of the reproduced hello-world (one sequence → two per-state predictions + energy gap).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal end-to-end pipeline producing a first (small) multi-state batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Stand up `scripts/multistate_tools.py` and confirm `generate_two_states`, `multistate_mpnn`, `af2_predict_state`, and `energy_gap` all run on the deterministic `mock` backend. `[core]`
- **Week 4:** Wire in the **real backends on Colab/A100**: RFdiffusion (ColabDesign) for the **two** state backbones, ProteinMPNN in **multi-state / tied** mode for the shared sequence, AF2/ESMFold for per-state prediction. Confirm one real design goes two-states → multi-state MPNN → predict-both end-to-end. Note the GPU you used. `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a tiny scale (one topology, ~8 shared sequences). Predict **both** states for each and compute the energy gap per design. `[core]`
- **Week 6:** Produce + visualize the first batch (both backbones for one design); write a short "what worked / what's slow / what's my compute budget" note — be explicit that **two-backbone generation + multi-state MPNN + AF2 ×2 needs an A100/HPC; a T4 runs only a small fallback**. `[extension]`

**D1 deliverable:** working minimal pipeline (two states → multi-state MPNN → per-state prediction → energy gap) + first small batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real multi-state design campaign at scale (diversity before filtering).

- **Weeks 7–8:** Generate the **two state backbones** (RFdiffusion, ColabDesign) for your chosen topology + trigger — and, where useful, a small *ensemble* per state so the multi-state design has room. Manage GPU time carefully: **two backbone-generation runs plus the downstream prediction load realistically need an A100/HPC**; a T4 only handles a slice. Log every config + seed. `[core]`
- **Weeks 9–10:** Run **multi-state ProteinMPNN** to find a shared sequence compatible with **both** backbones — residue identities **tied** across the two states, ~8–many sequences, temperature ~0.1–0.2. Record the **per-state MPNN score** for A and B separately (a good switch fits BOTH, not just one). Parameter exploration: how does tying scheme / temperature change the A-vs-B trade-off? `[core]` / `[extension]`
- **Weeks 11–12:** Predict **both states** from each shared sequence (AF2 for trusted picks, ESMFold for triage); assemble the full pool into `results/multistate_designs.csv` (one row per design: per-state scrmsd, per-state pLDDT, energy gap, MPNN scores, seed); finalize the **design log**. Interim report on the early A-vs-B trade-off and how often *anything* satisfies both states. `[core]`

**D2 deliverable:** two state backbones + multi-state shared-sequence pool (`results/multistate_designs.csv`) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark/ablation that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`) **to BOTH states**. Build **two** `fp.Design` objects per design (one for state A, one for state B), each with `design_type="monomer"`, populating per-state `scrmsd` and `plddt`; run `fp.run_pipeline(..., design_type="monomer")` and `fp.report(...)` for each state. A design only counts as a switch candidate if it passes the monomer foldability bar for **A AND B**. `[core]`
- **Weeks 15–16:** Run the project's core analysis (notebook 04): **AF2 predicts both states from one sequence** and the **energy-gap reasoning** (close enough to switch, distinct enough to define OFF/ON; flag designs inside the switchable band). Then the benchmark/ablation: **single-state vs multi-state design** (design each backbone alone with normal MPNN and show the single-state sequences fail the *other* state — that contrast is the result) and the **state energy-gap distribution**. *(Extension)* a short **transition MD** on a top pick to probe whether A↔B is plausible. `[core]` / `[extension]`
- **Weeks 17–18:** Sanity-check the "switchable" picks (is the gap real, or an artifact of AF2 only seeing one state?); rank candidates; **honest hit-rate accounting** — N(passes A) / N(passes B) / N(passes BOTH) / N(switchable). Report the **energy-gap caveat** explicitly. `[core]`

**D3 deliverable:** per-state-filtered candidates + AF2-both-states + energy-gap analysis + single- vs multi-state benchmark + a filtering report including survival-at-each-layer for BOTH states.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence and design the experiment.

- **Weeks 19–20:** Orthogonal validation (re-predict top picks with the *other* predictor and, where possible, **bias prediction toward each state** — templates / initial guess — to test whether both states are genuinely accessible to one sequence); finalize the energy-gap reasoning. *(Extension)* run a **short transition MD** (OpenMM, 10–50 ns) on the top pick to check the predicted states stay put and whether A↔B is plausible. `[core]` / `[extension]`
- **Weeks 21–22:** Write the **experimental validation plan**: a **state-change read-out** that actually proves a switch — **FRET** (donor/acceptor reporting the A↔B distance change), **protease accessibility** (a site exposed in one state, buried in the other), or **SAXS** (solution shape change on trigger) — with **paired controls**: a positive (a design / natural protein known to switch), a **single-state "locked" negative** (a sequence that should NOT switch), and an unrelated control. Specify expression (*E. coli* BL21(DE3)), purification, the trigger titration, a timeline, and a costed reagent list. `[core]`
  - *(Stretch)* design a **light-switch (LOV-domain) integration** — fuse/embed a LOV photoswitch so the trigger is light; note the added validation (dark/lit states). `[stretch]`
  - *(Optional, if your lab has capacity)* execute the go/no-go tier (express → SDS-PAGE → SEC) and a first trigger titration. `[stretch]`

**D4 deliverable:** validation report + costed, controlled state-change read-out plan (FRET/protease/SAXS) + the selected multi-state design (D★); optional LOV light-switch extension.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions+params · Results w/ per-state hit rates, the A-vs-B trade-off & the energy-gap distribution · Discussion w/ failure forensics + **the multi-state designability + energy-gap caveats** · Experimental plan · References · Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned `requirements.txt` + version stamp from `00_setup`). `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release, including the multi-state design + its two-state validation + the read-out plan.

---

### A note on scope discipline
The temptation is to chase one spectacular switch. Resist it. Multi-state design is hard; a campaign
that honestly reports *"5% of designs passed both states, and of those the energy gap was switchable
for only 1, with AF2 unable to confirm state B"* is worth far more than a single cherry-picked
picture. **Define two states clearly, search for one sequence that fits both, validate both states,
report the rate — and own the caveat that AF2 may not capture both states.**

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (the full multi-state campaign needs A100/HPC; T4 = small fallback).
