# Project 12 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** A biosensor has two parts: a **recognition element** (here, a de novo binder
to a chosen biomarker/analyte) and a **transduction element** (a switch that converts binding into a
measurable signal). The whole point is to turn **binding → signal** so that the presence of an analyte
produces luminescence or FRET you can read at the point of care. We design the binder with the
binder-family workflow (BindCraft / RFdiffusion-binder + ProteinMPNN, scored by AF2-Multimer) and
couple it to a switch from one of two families.

**The two switch architectures (choose one to build on):**
- **Split-reporter.** The reporter (e.g. **split-luciferase / NanoBiT**, or a **split-fluorophore**
  for FRET) is broken into two fragments. A binding event brings the fragments together (or the
  conformational change releases them), reconstituting luminescence/FRET. Conceptually simple; the
  design challenge is geometry — binding must reliably move the fragments into (or out of) contact.
- **Conformational switch (LOCKR).** A de novo **cage + latch + key** (Langan 2019): the latch holds a
  functional/reporter element caged (OFF); the analyte (or a key peptide it exposes) displaces the
  latch, releasing the element (ON). More design freedom and tunability; harder to get right.

**Key concepts a student must understand:**
- **Self-consistency (scRMSD), pLDDT, `pae_interaction`** — exactly as in the binder family. The binder
  must pass the binder bar (`pae_interaction ≤ 10` is the key binder metric) before it is worth coupling.
- **Dynamic range = on_signal / off_signal** (fold-change) — **the headline sensor metric.** A great
  binder bolted to a switch with a leaky OFF state (high background) is a **poor sensor.** Report
  dynamic range, not just "it binds."
- **The affinity-vs-dynamic-range trade-off** — a genuine tension. A **too-tight** binder can lock the
  switch ON regardless of analyte (no switching); a **too-weak** one never forms the ON state. The best
  *sensor* is not always the best *binder*; tune deliberately.
- **Two-state modeling** — the OFF and ON conformations are *different structures*. Modeling both (and
  the relative signal between them) is how you reason about ON/OFF in silico before any wet-lab work.
- **LOD (limit of detection)** — depends on dynamic range AND assay noise. You **estimate** it from a
  *planned* dose-response with replicates and a blank; you never read it off a model.

**Why this is hard and what realistic success looks like.** Two hard problems stack: in-silico binder
hit rates **vary widely** (single-digit to tens of percent passing the filter, and most in-silico hits
fail experimentally), and coupling binding to a **clean ON/OFF signal** with usable dynamic range is
its own design problem that **usually needs iteration** (linker length/rigidity, latch redesign,
reporter placement). A passing binder is a *hypothesis*; a modeled dynamic range is **not** a measured
signal; there is **no LOD** until a dose-response is fit. Success for this capstone = a rigorous,
honestly-reported binder campaign **plus** an integrated construct with an ON/OFF analysis and a
controlled functional-readout plan — **not** a guaranteed working sensor.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** BindCraft, RFdiffusion (binder + scaffold), AF2-Multimer, and **two-state**
> modeling at campaign scale want an **A100** (Colab Pro+ or a cluster). A free **T4** runs only a
> *small fallback* (FreeBindCraft, small `num_designs`, a small RFdiffusion batch + ESMFold triage,
> small two-state runs). The notebooks run end-to-end on a deterministic **`mock`** backend with no
> GPU so you can build the plumbing anywhere; switch to the real backend on Colab Pro / A100. **Pin
> upstream commits and verify them** (the version-verify cell) — these tools change fast.

### BindCraft (or FreeBindCraft) — binder module
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes binder backbone **and** sequence together, pre-filtered on interface confidence. Binder
  paradigm #1 in notebook 02.
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**;
  replaces the PyRosetta dependency for free-tier use). *Verify both before the course starts.*
- **Key parameters:** `target_pdb` (cleaned analyte), `hotspot_residues` (the chosen epitope),
  `binder_length` (≈40–80), `num_designs` (50–200 on A100; far fewer on T4).
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  # On Colab Pro (A100) via the BindCraft notebook / CLI; pin the commit you used.
  python bindcraft.py --settings analyte_settings.json   # target=biomarker, hotspots=epitope, n=50-200
  ```

### RFdiffusion (binder mode + scaffold/switch) + ProteinMPNN
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a binder backbone docked against
  the epitope (binder paradigm #2); RFdiffusion **scaffold generation** builds a switch scaffold to
  present a split-reporter. **ProteinMPNN** designs sequences for both. Notebook 02.
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; the binder protocol +
  ProteinMPNN are exposed via ColabDesign `https://github.com/sokrypton/ColabDesign`. Pin commits.
- **Key parameters:** binder mode — `contigs` / `hotspot_res` (the epitope residues), `binderlen`,
  diffusion `noise_scale`, `num_designs`; ProteinMPNN `temperature` (0.1–0.3), `num_seq_per_target`.
  Scaffold mode — scaffold length/topology to host the split-reporter or latch.
- **Compute:** small batches OK on T4; **500–1000 binder backbones + scaffold generation want A100/HPC.**
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs target the analyte epitope hotspots.
  ./scripts/run_inference.py 'contigmap.contigs=[A1-110/0 60-80]' \
      'ppi.hotspot_res=[A12,A45,A60]' inference.num_designs=1000 inference.output_prefix=out/sensor
  # then ProteinMPNN over the backbones, then AF2-Multimer. Scaffold mode for the switch separately.
  ```

### LOCKR-style switch / split-reporter (literature-driven) — switch module
- **What it does / where it fits:** the transduction element. Either an RFdiffusion scaffold presenting
  a **split-luciferase/NanoBiT or split-FP FRET** pair, or a borrowed/adapted **LOCKR** cage+latch
  (Langan 2019) whose latch the analyte displaces. Notebook 02 (`design_switch`) + notebook 04
  (`integrate_binder_switch`, `model_two_state`).
- **Install:** no single package — this is literature + reuse. LOCKR designs: Langan et al. 2019
  (Nature) supplementary; de novo biosensors: Quijano-Rubio et al. 2021 (Nature); NanoBiT
  split-luciferase: Dixon et al. 2016. Adapt published scaffolds; redesign the latch/interface with
  ProteinMPNN/RFdiffusion.
- **Key parameters:** reporter choice (luminescence vs FRET), latch length/affinity (sets the OFF
  leak), **linker length/rigidity** between binder and switch (too floppy → leaky OFF; too rigid → no
  toggle). These are the knobs you iterate.
- **Compute:** scaffold generation on A100; two-state modeling on A100 (extension).

### AF2-Multimer (ColabFold) — scoring + two-state modeling
- **What it does / where it fits:** re-predicts each binder–analyte **complex** and yields
  `pae_interaction` (the key binder metric). Also drives **two-state** modeling of the switch (model
  the OFF/closed and ON/open conformations; notebook 04 `[extension]`).
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles`; for two-state, use templates / state-specific
  MSAs to bias toward each conformation. Parse `pae_interaction` (mean inter-chain PAE).
- **Compute:** small complexes OK on T4; campaign-scale + two-state prefers A100. Usually the slowest step.

### Shared `filtering_pipeline.py`
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(binders, design_type="binder")` then `fp.report(...)`. The binder is filtered with
  binder cutoffs; the **switch/sensor** is evaluated separately on dynamic range (notebook 04). Do
  **not** fork the module — iterate against `shared/` and PR back.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → biosensor architectures + analyte/readout choice + binder & sensor metrics table + mock hello-world (binder->switch->ON/OFF)
02_generate         → binder campaign (BindCraft 50-200 + RFdiffusion-binder 500-1000 -> ProteinMPNN) + switch module (RFdiffusion scaffold / LOCKR); AF2-Multimer; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per paradigm -> ranked CSV
04_validate         → integrate binder + switch; model the construct; ON/OFF two-state reasoning; switch-architecture benchmark + affinity-vs-dynamic-range figures -> top_constructs.csv
05_validation_plan  → luminescence/FRET dose-response + LOD estimate plan + controls (no-analyte/blank, off-target) + multiplexing concept (stretch)
```
For Project 12 the standard slots map to: *02 = binder campaign + switch module* (the core), *04 = the
integration + ON/OFF reasoning + switch-architecture benchmark*, *05 = the functional-readout
(dose-response/LOD) plan*.

## 4. Filtering cutoffs for this design type
The **binder** is filtered with the shared `"binder"` cutoffs
(`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`). The **sensor** is judged separately on dynamic range.
| Metric | Cutoff / target | Why |
|--------|-----------------|-----|
| scRMSD | ≤ 2.5 Å | binder self-consistency (designed vs AF2-predicted backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the binder (NOT stability) |
| **pae_interaction** | **≤ 10 Å** | **interface confidence — the key binder metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality |
| **dynamic_range** (sensor) | **as high as possible; set a project target** | on/off fold-change — the headline sensor metric (NOT a binder-filter pass/fail) |
| background_leak (switch) | low | OFF-state signal leak; high leak kills dynamic range |

> Reminder: **no in-silico metric perfectly separates true from false sensors.** The binder filter
> enriches for plausible binders; dynamic range is a **modeled** proxy, not a measured signal. A low
> `pae_interaction` is *confidence*, not affinity; a high modeled dynamic range is a hypothesis until a
> luminescence/FRET dose-response is fit. Expect false positives and report them.

## 5. Interpreting results
- A *good* sensor candidate: a binder that clears the binder bar (scRMSD ≤ 2.5, pLDDT ≥ 80,
  `pae_interaction` ≤ 10, `rosetta_dG` ≤ −30, sc ≥ 0.6) **and** an integrated construct with a high
  modeled **dynamic range** and a low OFF-state leak.
- A *suspicious* one: a strong binder whose construct shows **dynamic range ≈ 1** (binds but doesn't
  switch — no transduction), or a high modeled dynamic range driven by an absurdly low OFF that won't
  survive real assay noise.
- **Survival-at-each-layer plot (binder):** read it as a funnel — steep drops show which layer
  discriminates. Report it **per paradigm** so the binder head-to-head is fair.
- **Switch-architecture benchmark:** couple the *same* top binders to each architecture
  (split-reporter vs LOCKR) and compare the **distribution** of dynamic range, not the single best.
- **Affinity-vs-dynamic-range:** plot `pae_interaction` against modeled dynamic range — the best
  *sensor* is often not the best *binder*. Discuss the trade-off honestly.
- **Hit rate:** report `N binders passing all layers / N generated` (per paradigm), then how many of
  those yield an integrated construct above your dynamic-range target. Report the distribution, not the
  cherry.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for a binder campaign + two-state modeling | Use FreeBindCraft + small `num_designs`; small RFdiffusion batch + ESMFold triage; move full campaign + two-state to A100/HPC |
| BindCraft install fails | upstream repo/commit changed; PyRosetta license | Use the pinned commit; try FreeBindCraft (no PyRosetta); log the path you used |
| All binders fail self-consistency | bad target prep, wrong chain, wrong epitope | Re-clean the biomarker, confirm the chain, re-derive epitope residues; lower MPNN temperature |
| Binder binds but construct **doesn't switch** (dynamic_range ≈ 1) | binding not mechanically coupled to the switch; linker too rigid/floppy; latch mistuned | Iterate linker length/rigidity; redesign the latch; re-place the reporter; check the binding geometry actually moves the switch element |
| Dynamic range high but OFF leak high | leaky OFF state (background) | Tighten the latch / reduce reporter pre-association; this is the most common biosensor failure — report it |
| Sensor lights up for the **off-target** | binder not specific enough | Re-select epitope; add the off-target panel earlier; a non-specific sensor is not a sensor |
| Two-state modeling shows one state only | AF2 collapses to the dominant conformation | Use templates / state-specific MSAs to bias each state; treat the output as a proxy, not truth |
| Hit rate / dynamic range looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N, not the best |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** the **construct** (binder + switch fusion) in *E. coli* BL21(DE3), His-tagged,
  16–18 °C overnight; IMAC + SEC. For split-luciferase/NanoBiT, confirm the reporter folds and is
  active in the fusion context. The **analyte reagent** is recombinant (mammalian/insect or commercial)
  — confirm the right isoform/PTM state.
- **Functional assay (the point): dose-response.** Titrate the analyte across a wide range (log-spaced,
  ≥8 points + blank); read **luminescence** (split-luciferase/NanoBiT) or **FRET ratio** (split-FP);
  fit signal vs [analyte] (e.g. 4-parameter logistic) → EC50 + dynamic range; **estimate the LOD** from
  the fit (blank mean + 3·SD, or the lowest distinguishable dose). The LOD is a **measured estimate
  from your data** — never a number from a model.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF stability; reporter
  activity) → functional (the dose-response above) → deep (structure of the ON/OFF states).
- **Controls (mandatory):**
  - **No-analyte / blank:** buffer only → defines the OFF/background signal and the LOD floor. The
    single most important control for a sensor — a leaky OFF state kills dynamic range.
  - **Off-target:** a structurally-related but wrong analyte (or an unrelated protein) → the sensor must
    **not** light up. The specificity control.
  - **Positive / calibrator:** a known concentration of the true analyte (and, if available, an
    established sensor/ELISA) to confirm the assay and cross-calibrate.
- **Multiplexing (stretch):** orthogonal reporters (different luciferase colors / FRET pairs), spatial
  arrays, or barcoded constructs — with **cross-talk** controls (each sensor against the others' analytes).

## 8. Responsible research
This project designs a **diagnostic / point-of-care biosensor** for a disease biomarker — an in-scope
diagnostic purpose with **low dual-use** concern under `MASTER_BLUEPRINT.md §7`. In-scope purpose here:
diagnostic sensing only. Out of scope: enhancing pathogen transmissibility/virulence, toxins,
immune-evasion tools, or any design intended to cause harm. Any real gene-synthesis order must go
through a biosecurity-screening provider (IGSC member), and wet-lab work requires institutional
biosafety/ethics approval. Students must not overstate results or imply experimental validation that
was not done — a design is a hypothesis, a modeled dynamic range is not a measured signal, and there is
no LOD until a real dose-response is fit.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Langan
2019 (LOCKR switches), Quijano-Rubio 2021 (de novo biosensors), Dixon 2016 (NanoBiT split-luciferase),
Pacesa 2025 (BindCraft), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN), Evans 2021
(AF2-Multimer), plus the structural-biology source for your chosen analyte.
