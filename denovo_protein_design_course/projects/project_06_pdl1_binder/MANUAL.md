# Project 06 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** PD-L1 (CD274) on tumor and immune cells engages PD-1 on T cells; that
engagement delivers an inhibitory signal that dampens the anti-tumor response. **Blocking** the
PD-1/PD-L1 interaction (as approved antibodies do) re-activates T cells. We want a **small de novo
mini-binder** (≈40–80 aa) that sits on the **PD-1-binding face of PD-L1** and competitively occludes
PD-1 — smaller, cheaper, and more tumor-penetrant than a 150 kDa antibody. The binder is targeted at
the PD-L1 ectodomain (the membrane-distal IgV domain) at hotspot residues drawn from the PD-1/PD-L1
co-crystal interface.

**Key concepts a student must understand:**
- **Hotspots / epitope:** the small set of target residues the binder is steered to contact. Choosing
  them on the **competitive (PD-1) face** is what makes the binder a *blocker*, not just a sticker.
- **Self-consistency (scRMSD):** design a backbone → design its sequence → predict that sequence →
  measure Cα-RMSD between designed and predicted. `< 2.5 Å` is the binder self-consistency bar.
- **`pae_interaction` (AF2-Multimer):** the **single most important binder metric** — the predicted
  aligned error *across the binder–target interface*. Low (`≤ 10 Å`) means AF2-Multimer is confident
  about the *relative* placement of binder and target. pLDDT alone does not tell you this.
- **Interface energy (`rosetta_dG`, REU) + shape complementarity (`sc`):** the physics layer — is the
  interface actually favorable and well-packed, not just confidently placed.
- **Two paradigms:** *BindCraft* hallucinates a binder with AF2 in the loop (one-shot, sequence +
  structure together); *RFdiffusion binder mode* diffuses a backbone against the target, then
  *ProteinMPNN* designs a sequence for it. Different inductive biases → different hit rates and folds.

**Why this is hard and what realistic success looks like.** In-silico binder hit rates **vary widely
by target and tool** — from single-digit to tens of percent passing the filter — and the **great
majority of in-silico hits fail experimentally**. A binder that passes every layer is a *hypothesis*:
a low `pae_interaction` is **not** a measured affinity, and **SPR/BLI validation is mandatory**.
Success for this capstone = a rigorous, honestly-reported head-to-head campaign with a clear hit-rate
accounting and a controlled validation plan — **not** a guaranteed working binder.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** BindCraft, RFdiffusion binder mode, and AF2-Multimer at campaign scale want an
> **A100** (Colab Pro+ or a cluster). A free **T4** runs only a *small fallback campaign*
> (FreeBindCraft, small `num_designs`, a small RFdiffusion batch + ESMFold triage). The notebooks run
> end-to-end on a deterministic **`mock`** backend with no GPU so you can build the plumbing
> anywhere; switch to the real backend on Colab Pro / A100. **Pin upstream commits and verify them**
> (the version-verify cell) — these tools change fast.

### BindCraft (or FreeBindCraft)
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes binder backbone **and** sequence together, pre-filtered on interface confidence. The
  primary paradigm in notebook 02.
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**;
  replaces the PyRosetta dependency for free-tier use). *Verify both before the course starts.*
- **Key parameters that matter here:** `target_pdb` (cleaned PD-L1), `hotspot_residues` (the PD-1-face
  set), `binder_length` range (≈40–80), `num_designs` (50–200 on A100; far fewer on T4),
  `design_models` / filters thresholds.
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  # On Colab Pro (A100) via the BindCraft notebook / CLI; pin the commit you used.
  python bindcraft.py --settings pdl1_settings.json   # target=PD-L1, hotspots=PD-1 face, n=50-200
  ```

### RFdiffusion (binder mode) + ProteinMPNN
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a binder backbone docked
  against the target hotspots; **ProteinMPNN** then designs a sequence for each backbone. The second
  paradigm in notebook 02 (generate 500–1000 backbones → MPNN).
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; the official binder
  protocol is exposed via ColabDesign `https://github.com/sokrypton/ColabDesign`. ProteinMPNN ships
  with RFdiffusion / ColabDesign. Pin commits; *verify before the course.*
- **Key parameters:** `contigs` / `hotspot_res` (the PD-1-face residues), `binderlen`, diffusion
  `noise_scale`, `num_designs` (500–1000 backbones; small batch on T4); ProteinMPNN `temperature`
  (0.1–0.3) and `num_seq_per_target` (e.g., 8).
- **Compute:** RFdiffusion small batches OK on T4; **500–1000 backbones want A100/HPC.** ProteinMPNN
  is CPU-cheap. AF2-Multimer re-prediction of each design is the real bottleneck.
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs target the PD-1-face hotspots.
  ./scripts/run_inference.py 'contigmap.contigs=[A1-115/0 60-80]' \
      'ppi.hotspot_res=[A56,A66,A115]' inference.num_designs=1000 inference.output_prefix=out/pdl1
  # then ProteinMPNN over the backbones, then AF2-Multimer.
  ```

### AF2-Multimer (ColabFold)
- **What it does / where it fits:** re-predicts each binder–PD-L1 **complex** and yields the key
  metric `pae_interaction` (plus interface pLDDT). The orthogonal/self-consistency check for binders.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles` (raise for hard interfaces), pairing/MSA
  mode. Parse `pae_interaction` from the output (mean PAE on inter-chain residue pairs).
- **Compute:** small complexes OK on T4; campaign-scale re-prediction prefers A100. This is usually
  the slowest step — batch overnight.

### Shared `filtering_pipeline.py` + Boltz-2 (stretch)
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. Do **not** fork it — iterate
  against `shared/` and PR back.
- **Boltz-2** (stretch, notebook 05): predicted binding affinity on top hits — **scaffold only**;
  report *relative ranking* and caveats, **never fabricate a K_D**.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → target prep (clean PD-L1 IgV) + PD-1-face hotspot ID + binder metrics table + mock hello-world
02_design_campaign  → two-paradigm campaign: BindCraft (50-200) + RFdiffusion-binder (500-1000 -> ProteinMPNN); AF2-Multimer; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per paradigm -> ranked CSV
04_analysis_figures → BindCraft-vs-RFdiffusion benchmark (hit rate, interface energy, novelty) + epitope-competition vs PD-1 + figures
05_validation_plan  → SPR/BLI + PD-1-competition assay, controls (positive binder, scrambled-interface negative, unrelated), expression strategy; Boltz-2 affinity stretch (scaffold)
```
For Project 06 the standard slots map to: *02 = the two-paradigm binder campaign* (the core), *04 =
the head-to-head benchmark*, *05 = the SPR/BLI + PD-1-competition validation plan*.

## 4. Filtering cutoffs for this design type
These are the shared `"binder"` cutoffs (`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`).
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs AF2-predicted binder backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the binder (NOT stability) |
| **pae_interaction** | **≤ 10 Å** | **interface confidence — the key binder metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail) |

> Reminder: **no in-silico metric perfectly separates true from false binders.** Filters enrich; they
> do not guarantee. Expect false positives and report them. `pae_interaction` is the best single
> binder predictor, but a low value is *confidence*, not *affinity*.

## 5. Interpreting results
- A *good* binder design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10**, `rosetta_dG`
  ≤ −30 REU, `sc` ≥ 0.6, and a footprint that overlaps the PD-1 epitope (so it can *compete*).
- A *suspicious* one: low `pae_interaction` but weak `rosetta_dG` (confident placement, poor
  interface), or a great interface that **doesn't overlap the PD-1 footprint** (won't block).
- **Survival-at-each-layer plot:** read it as a funnel — steep drops show which layer discriminates.
  Report it **per paradigm** so the head-to-head is fair.
- **Hit rate:** report `N passing all layers / N generated`, separately for BindCraft and
  RFdiffusion, with the layer-by-layer survival counts. Report the *distribution*, not just the best.
- **Head-to-head:** compare hit rate, `rosetta_dG` distribution, diversity, and novelty across the two
  paradigms; discuss their different failure modes honestly.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for a binder campaign | Use FreeBindCraft + small `num_designs`; small RFdiffusion batch + ESMFold triage; move full campaign to A100/HPC |
| BindCraft install fails | upstream repo/commit changed; PyRosetta license | Use the pinned commit; try FreeBindCraft (no PyRosetta); log the path you used |
| All designs fail self-consistency | bad target prep, wrong chain, wrong hotspots | Re-clean PD-L1, confirm the IgV chain, re-derive hotspots from the PD-1/PD-L1 interface; lower MPNN temperature |
| `pae_interaction` good but `rosetta_dG` weak | confident placement, poor interface packing | Keep as a flagged case; tighten `sc`/`rosetta_dG`; prefer designs strong on both |
| Binder binds but **off the PD-1 face** | hotspots not on the competitive epitope | Re-select hotspots from the PD-1 footprint; add the epitope-competition check (nb 04) |
| RFdiffusion produces few foldable binders | noise scale / contigs / length off | Sweep `noise_scale`, adjust `binderlen`, regenerate; expect a low per-backbone hit rate (it is normal) |
| Hit rate looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N, not the best |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** binders in *E. coli* BL21(DE3), 16–18 °C overnight (small, His-tagged); the **PD-L1
  ectodomain reagent** is typically expressed in mammalian/insect cells or bought commercially
  (glycosylation matters for the reagent, less so for the bacterial binder).
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF stability; **SPR or
  BLI** vs immobilized PD-L1 for K_D/kinetics) → functional (**PD-1-competition** assay: does the
  binder displace PD-1 from PD-L1?) → deep (co-crystal / cryo-EM, cell-based blockade).
- **Controls (mandatory):**
  - **Positive:** a known PD-L1 binder (e.g., an anti-PD-L1 Fab/antibody or PD-1 ectodomain) to
    confirm the assay and the immobilized PD-L1 reagent are active.
  - **Negative (scrambled-interface):** take your **own** top design and scramble/mutate the
    interface residues — it must **lose** binding. This is the cleanest specificity control.
  - **Unrelated-protein negative:** an unrelated mini-protein of similar size that should not bind.
- **PD-1 competition:** the functional readout that the binder is a *blocker* — pre-incubate PD-L1
  with the binder, then measure remaining PD-1 binding (SPR competition or a cell-based assay).

## 8. Responsible research
This project designs **inhibitory/blocking** binders to a human checkpoint protein (PD-L1) for
**cancer immunotherapy and diagnostics** — an in-scope therapeutic/diagnostic purpose under
`MASTER_BLUEPRINT.md §7`. In-scope purpose here: checkpoint-blockade oncology / diagnostics only. Out
of scope: enhancing pathogen transmissibility/virulence, toxins, immune-evasion tools, or any design
intended to cause harm. Any real gene-synthesis order must go through a biosecurity-screening provider
(IGSC member), and wet-lab work requires institutional biosafety/ethics approval. Students must not
overstate results or imply experimental validation that was not done — a design is a hypothesis.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Pacesa
2025 (BindCraft), Cao 2022 (target-structure-only minibinders), Watson 2023 (RFdiffusion), Dauparas
2022 (ProteinMPNN), Evans 2021 (AF2-Multimer), plus a PD-1/PD-L1 structural-biology review.
