# Project 16 — Student Instructions (24 weeks)

How to use this guide: each phase ends in a graded **deliverable (D0–D5)**. Keep a running `LOG.md`
(date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are tagged `[core]`
(everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This project follows the **antibody-family pattern** (template: Project 17): a deterministic mock,
`design_type="antibody"` filter hand-off, and a controlled validation plan. Your task here is to
**humanize an existing non-human antibody** and quantify the **humanness↔stability trade-off**.

**Compute note:** this is one of the few antibody-family projects that is genuinely **free-tier (Colab
T4) friendly** — humanness scoring, an IgFold/ImmuneBuilder Fv model, and ΔΔG proxies are all light. No
A100 required.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand humanization strategies, pick your antibody + frameworks, reproduce the mock hello-world.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Prihoda 2022 (Hu-mAb/BioPhi/OASis),
    Olsen 2022 (AbLang), Gao 2013 (T20), a CDR-grafting/resurfacing humanization review. Write a half-page
    on the state of antibody humanization — including the **honest humanness↔stability trade-off**. `[core]`
  - **Pick + verify your inputs:** a **published non-human (murine/chimeric) therapeutic antibody** VH/VL
    sequence (record the paper/DOI; mark "verify") and the **human germline framework(s)** to graft onto
    (IMGT/OAS — pick the closest human germlines by V/J gene). Verify both in `data/README.md`. `[core]`
  - Note how to obtain the **IMGT / OAS germline database** (downloaded separately, not committed —
    document the size). Run `data/download_data.py --dry-run` to see the provenance scaffold. `[core]`
- **Week 2**
  - Write a 1-page **problem statement**: the antibody, the germline framework(s), the humanization
    **strategy** (grafting vs resurfacing vs germline-content), and **measurable** success criteria
    (target humanness band + acceptable ΔΔG / retained-binding bar + the controls). `[core]`
  - Reproduce the "hello-world": run `00_setup.ipynb`, then `01_define_and_explore.ipynb` on the `mock`
    backend (graft CDRs, score humanness + ΔΔG proxy, list Vernier back-mutations on 1 variant). `[core]`
  - Read the **CDR / framework / Vernier-zone** section of `MANUAL.md §1`; identify the Vernier positions
    on your *verified* antibody (not the EXAMPLE placeholders). `[core]`

**D0 deliverable:** problem statement (antibody + germline + strategy + success criteria + controls) +
printout of the reproduced mock humanization hello-world (graft + Vernier back-mutations + SYNTHETIC
humanness/ΔΔG).

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal humanization pipeline producing a first (mock, then real) variant batch.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the full
  mock pipeline (`01`→`05`) end-to-end so the plumbing is solid before any tool installs. `[core]`
- **Week 4:** Prepare inputs: clean/number your antibody VH/VL (ANARCI / Kabat/Chothia/IMGT scheme), fix
  the candidate **human germline frameworks**, and finalize the **Vernier-zone position list** on the real
  sequence. `[core]`
- **Week 5:** Run a **real humanness score** on the parental + one graft (OASis/Hu-mAb via BioPhi, or
  AbLang) end-to-end on a T4; pin the tool commit/host. Model the Fv with IgFold/ImmuneBuilder. `[core]`
- **Week 6:** Visualize the parental vs grafted Fv (py3Dmol); write a short "what worked / what's slow /
  what's my budget" note (this project is cheap — note that explicitly). `[extension]`

**D1 deliverable:** working minimal humanization pipeline + first variant batch (mock + a real humanness
score) + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real humanization campaign (diversity of frameworks + strategies before filtering).

- **Weeks 7–8:** Graft the CDRs onto **several candidate human germline frameworks** (the closest human
  germlines). Generate, for each: a bare graft, a graft + Vernier back-mutations, and a resurfacing variant
  `[extension]`. Add the two controls: the **parental** antibody and an **over-humanized decoy**. `[core]`
- **Weeks 9–10:** Score every variant: **humanness** (OASis/Hu-mAb/T20/AbLang — real tools) + **ΔΔG**
  (FoldX/Rosetta on the IgFold Fv model). Explore parameters (CDR-definition scheme; which Vernier residues
  to restore). Optionally run **ProteinMPNN** framework optimization with CDRs fixed. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full pool into `results/campaign.csv`; finalize the **design log** (parental
  antibody, candidate frameworks, scheme, back-mutation sets, seed, tool/commit, runtime). Interim report.
  `[core]`

**D2 deliverable:** full variant pool (`campaign.csv`: grafts, back-mutated, resurfaced + parental +
over-humanized-decoy controls) + complete design log + 3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the trade-off study that makes this a *study*.

- **Weeks 13–14:** Apply the shared 4-layer filter (`03_filter_and_rank.ipynb` →
  `shared/filtering_pipeline.py`) with `design_type="antibody"` (scRMSD ≤ 3.0, pLDDT ≥ 70,
  pae_interaction ≤ 12) plus a **humanness floor** at the physics layer. Report **survival at each layer**;
  confirm the over-humanized decoy fails and the parental fails the humanness floor. `[core]`
- **Weeks 15–16:** Run the benchmark/ablations in `04_validate.ipynb`: the **humanness↔stability (ΔΔG)
  trade-off** figure (the headline), the **Vernier back-mutation** ladder (ΔΔG regained vs humanness lost),
  and **CDR grafting vs resurfacing** `[extension]`. `[core]` / `[extension]`
- **Weeks 17–18:** Build the **immunogenicity-risk summary** (residual non-human content + risk band per
  variant); rank candidates with honest hit-rate accounting. Use the **real** humanness/ΔΔG tools for any
  reportable claim (the in-notebook heuristics are for plumbing). `[core]`

**D3 deliverable:** antibody-filtered ranked variants + trade-off / back-mutation / grafting-vs-resurfacing
figures + a filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** finalize the trade-off conclusion and design the experiment.

- **Weeks 19–20:** Orthogonal validation: confirm the ΔΔG ranking with a second method where possible
  (FoldX vs Rosetta, or a second Fv model); re-check Vernier choices; finalize which variants you would
  carry forward (most human that still passes the binding + stability bars). `[core]` / `[extension]`
- **Weeks 21–22:** Write the **validation plan** (`05_validation_plan.ipynb`): express each variant +
  controls (mammalian Fab/IgG), **ELISA / SPR / BLI** for **retained binding** vs the parental, **DSF** for
  **stability (Tm)** vs the parental, plus the **immunogenicity-risk summary**. Specify the mandatory
  **controls** (positive = **parental** antibody; negative = **over-humanized decoy**; isotype control);
  costed reagent list + timeline. `[core]`
  - *(Stretch)* add a real **T-cell-epitope predictor** to the immunogenicity-risk summary and/or a
    **germline-content optimization** loop (ProteinMPNN + humanness in the objective). `[stretch]`

**D4 deliverable:** validation report + ELISA/SPR/DSF plan + immunogenicity-risk summary + controls
(parental + over-humanized decoy) + costed, controlled experimental plan.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro w/ humanization + ADA rationale · Methods
  w/ exact tools/commits/params · Results w/ the trade-off, distributions, back-mutation analysis ·
  Discussion w/ failure forensics + the humanness≠low-ADA caveat · Validation plan · References ·
  Reproducibility statement). `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment. `[core]`

**D5 deliverable:** thesis report + presentation + tagged reproducible release.

---

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (this project is **T4-friendly**; no A100 needed).
