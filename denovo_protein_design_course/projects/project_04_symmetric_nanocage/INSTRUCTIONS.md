# Project 04 — Student Instructions (24 weeks)

**How to use this guide:** each phase ends in a graded **deliverable (D0–D5)**. Keep a running
`LOG.md` (date · command · GPU · outcome) — it is graded as part of reproducibility. Tasks are
tagged `[core]` (everyone), `[extension]` (most), `[stretch]` (going deep / MSc track).

This is a **symmetric-design** project: your goal is subunits that reliably close into a *target*
point group (C3, C4, D2) and **not** the wrong oligomer. Every notebook runs on a deterministic
**mock** backend first, so you can build the plumbing before spending GPU time. **A full C3/C4/D2
campaign needs an A100** — a free T4 realistically runs only a small C3 demo. Plan compute early.

---

## Phase 0 — Orient (Weeks 1–2) → **D0**
**Goal:** understand symmetry contigs, tied positions, and oligomeric-state error, and reproduce a small C3.

- **Week 1**
  - Read the tiered reading list (`references/reading_list.md`): Watson 2023 (symmetric RFdiffusion),
    Dauparas 2022 (tied ProteinMPNN), Evans 2021 (AF2-Multimer), Wicky 2022 (symmetric assembly
    validation). Write a half-page on the state of symmetric / nanocage design. `[core]`
  - **Verify the data accessions** in `data/README.md` on RCSB — pick at least one natural **Cn** and
    one **Dn** homo-oligomer and confirm the biological-assembly symmetry on the RCSB "Symmetry /
    Assembly" tab. **Nanocage and oligomer PDB IDs are easy to mis-remember; do not trust an
    unverified ID.** Fill the verified IDs into `download_data.py`. `[core]`
- **Week 2**
  - Write a 1-page **problem statement** with explicit, *measurable* success criteria (e.g., "≥X% of
    C3 designs pass subunit scRMSD < 2.5 Å **and** interface pAE < 10 **and** symmetry RMSD < 2 Å")
    and the controls you will need (a known nanocage / natural homo-oligomer as positive; a
    scrambled-interface or monomeric variant as negative). `[core]`
  - Reproduce the "hello-world": run `notebooks/00_setup.ipynb`, then the small-C3 section of
    `01_define_and_explore.ipynb` — generate one C3 (mock), tied-MPNN it, AF2-Multimer-predict it,
    and read the three metrics. Re-run with the real backend if you have an A100. `[core]`

**D0 deliverable:** problem statement (measurable success criteria + controls) + screenshot/printout
of the reproduced small-C3 output with its subunit scRMSD / interface pAE / symmetry RMSD.

---

## Phase 1 — Baseline (Weeks 3–6) → **D1**
**Goal:** a working minimal symmetric pipeline producing a first (small) C3 batch end-to-end.

- **Week 3:** Set up your git repo + `LOG.md`; confirm `env/requirements.txt` works on Colab. Run the
  full `00`–`01` chain on the mock backend so the plumbing is solid. `[core]`
- **Week 4:** Prepare inputs: study `data/inputs/symmetry_defs.txt`; understand how a per-subunit
  contig + a point group define an assembly, and how `tied_positions()` groups symmetry-mates so they
  share a sequence. Stand up `scripts/sym_tools.py` and run its smoke test. `[core]`
- **Week 5:** Run the minimal pipeline end-to-end on a tiny scale (5–10 C3 designs): symmetric
  generation → **tied** ProteinMPNN → AF2-Multimer. On a T4 this is the realistic demo size; on an
  A100 you can go larger. `[core]`
- **Week 6:** Produce + visualize the first batch (py3Dmol); write a short "what worked / what's slow /
  what's my A100 budget per 100 designs" note. Confirm the wrong-oligomer column is populated. `[extension]`

**D1 deliverable:** working minimal symmetric pipeline (generate → tied-MPNN → AF2-Multimer) + first
small C3 batch + initialized repo with `LOG.md`.

---

## Phase 2 — Campaign (Weeks 7–12) → **D2**
**Goal:** the real campaign — C3, C4, and D2 at scale (diversity before filtering).

- **Weeks 7–8:** Scale generation to **hundreds of designs across C3 / C4 / D2** with symmetric
  contigs (use the families in `symmetry_defs.txt`); manage A100 time carefully — diffusion and
  multimer prediction are the cost, not MPNN. `[core]`
- **Weeks 9–10:** Sequence-design every backbone with **tied** ProteinMPNN (symmetry-related positions
  share one amino acid); generate several sequences per backbone; explore sampling temperature. Also
  run an **untied** set on a subset for the Week-15 tied-vs-untied benchmark. `[core]` / `[extension]`
- **Weeks 11–12:** Assemble the full pool into `results/assemblies.csv` (one row per design × sequence
  with symmetry, subunit length, tied/untied, seed, config); finalize the **design log**. Interim
  report. `[core]`

**D2 deliverable:** full C3/C4/D2 design pool (`results/assemblies.csv`) + complete design log +
3–4 page interim report.

---

## Phase 3 — Filter & benchmark (Weeks 13–18) → **D3**
**Goal:** reproducible triage + the benchmark that makes this a *study*, not a demo.

- **Weeks 13–14:** Apply the shared filter (`03_filter_and_rank.ipynb` → `shared/filtering_pipeline.py`)
  with `design_type="oligomer"`: subunit scRMSD ≤ 2.5 Å, pLDDT ≥ 80, interface pAE ≤ 10. Add a
  **symmetry-RMSD** screen (does it close into the intended order?) and an interface-energy column.
  Produce the survival-at-each-layer figure. `[core]`
- **Weeks 15–16:** Run the benchmark/ablation: **symmetry order vs success** (do C3 designs succeed
  more often than C4 or D2?) and **tied vs untied** sequence design (does tying improve the
  pass rate?). Report both as rates with N. `[core]` / `[extension]`
- **Weeks 17–18:** Rank top assemblies per symmetry; **honest assembly-success accounting** (N pass /
  N generated at each layer, per symmetry). Flag designs whose interface pAE passes but whose symmetry
  RMSD is poor — confident interface, wrong global arrangement. `[core]`

**D3 deliverable:** ranked top assemblies + benchmark figures (symmetry-order-vs-success,
tied-vs-untied) + filtering report including the survival-at-each-layer analysis.

---

## Phase 4 — Validate (in silico) + plan (wet-lab) (Weeks 19–22) → **D4**
**Goal:** deepen confidence, catch wrong-oligomer risk, and design the experiment.

- **Weeks 19–20:** **Wrong-oligomer risk analysis** `[extension]`: for your top designs, model
  *alternative* oligomeric states (e.g., predict the same sequence as a dimer, trimer, tetramer) and
  ask whether the design *also* scores well as the wrong order — a design that does is a red flag.
  Report which top picks are "symmetry-clean" vs "ambiguous." `[core]` / `[extension]`
- **Weeks 21–22:** Write the **experimental validation plan**: expression strategy (*E. coli*
  BL21(DE3) for many designed assemblies; note when mammalian is needed for glycosylated antigens),
  purification, then the assays that actually determine oligomeric state — **SEC-MALS** (absolute
  molar mass → oligomeric number), **negative-stain EM** (assembly architecture), **native-MS**
  (stoichiometry) — with **controls** (positive = a known nanocage / natural homo-oligomer; negative =
  a scrambled-interface or monomeric variant; unrelated-protein control), a timeline, and a costed
  reagent list. `[core]`
  - *(Antigen-display extension, `[extension]`)* graft a **neutralizing/benign** epitope onto the cage
    surface and model the displayed-antigen construct (vaccine framing only — see Responsible Research).
  - *(Optional, if your lab has capacity)* express your top C3 design and run the go/no-go tier
    (express → SDS-PAGE → SEC). `[stretch]`

**D4 deliverable:** validation report (incl. wrong-oligomer risk analysis) + costed, controlled
nsEM/SEC-MALS/native-MS experimental plan.

---

## Phase 5 — Synthesize (Weeks 23–24) → **D5**
**Goal:** thesis, defense, and a release someone else could reproduce.

- **Week 23:** Write the thesis-chapter report (Abstract · Intro · Methods w/ exact versions + the
  RFdiffusion/ColabFold commit pins + params · Results w/ assembly-success rates & distributions,
  per symmetry · Discussion w/ wrong-oligomer forensics · Experimental plan · References ·
  Reproducibility statement). Include the **assembly design report**: the ranked C3/C4/D2 candidate
  set with its validation plan. `[core]`
- **Week 24:** Prepare + give a 15-minute talk; tag a `v1.0` release; archive the environment (pinned
  `requirements.txt` + version stamp from `00_setup` + the diffusion/multimer commit pins). `[core]`
  - *(Stretch)* extend toward **tetrahedral / higher-symmetry** cages — note this needs a different
    protocol and far more compute (A100/HPC); treat as future work unless you have the budget. `[stretch]`

**D5 deliverable:** thesis report + assembly design report + presentation + tagged reproducible release.

---

### A note on scope discipline
It is tempting to chase the biggest, prettiest cage. Don't. A *small, honestly characterized* C3/C4/D2
campaign with rigorous wrong-oligomer analysis is worth far more than an unverified tetrahedral
cartoon. When compute is tight, de-scope to fewer symmetries or a tied-MPNN-only study on a small C3
pool — and say so. Never claim a cage "will assemble"; the in-silico filter enriches, it does not prove.

### Where to get help
- Tool errors / parameters → `MANUAL.md` (troubleshooting table).
- Conceptual questions → `references/reading_list.md` + advisor office hours.
- Compute limits → `MASTER_BLUEPRINT.md §3` (free-tier fallbacks; this project's A100 need).
