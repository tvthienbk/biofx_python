# Project 09 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** MDM2 binds the **p53 transactivation helix** through a hydrophobic N-terminal
cleft, burying three p53 side chains — **Phe19, Trp23, Leu26** — in three sub-pockets. When MDM2 is
over-active, it sequesters and degrades p53, silencing the tumor suppressor. A peptide or macrocycle
that **mimics the p53 helix**, occupies that cleft, and **out-competes p53** can free p53 and restore
its signalling. We want a **short linear peptide** (~8–20 aa) or a **macrocycle** (~7–15 aa, head-to-
tail or side-chain cyclized) that sits on the MDM2 p53-cleft at the Phe19/Trp23/Leu26 sub-pockets.
This is the **peptide/macrocycle analog of mini-binder design** (Project 06): the cleft residues are
the "hotspots," and the same in-silico filter applies — only the modality and the validation change.

**Key concepts a student must understand:**
- **The cleft (the "hotspots"):** the MDM2 residues lining the p53 sub-pockets. Steering the peptide
  to **mimic Phe19/Trp23/Leu26** is what makes it a *p53 competitor*, not just a surface sticker.
- **Linear vs macrocyclic peptides:** a **linear** peptide is flexible, protease-labile, and usually
  cell-impermeable; a **macrocycle** (ring closure) rigidifies the bound conformation, can resist
  proteases, and sometimes gains permeability — at a real **synthesis cost**. Cyclization is the
  central design lever here.
- **Self-consistency (scRMSD):** design a peptide → predict it in the complex → measure Cα-RMSD
  between designed and predicted. `< 2.5 Å` is the bar (peptides are short, so this is noisier).
- **`pae_interaction` (AF2 / Boltz-2):** the **key interface metric** — predicted aligned error across
  the **peptide–MDM2 interface**. Low (`≤ 10 Å`) means the model is confident about the *relative*
  placement of peptide and MDM2. pLDDT alone does not tell you this.
- **Boltz-2 affinity score — a RELATIVE RANK, not a K_D:** Boltz-2 emits an affinity *signal* for the
  complex. For short peptides this is **unreliable**; use it only to **prioritize** which hits to
  synthesize first. **Never report it as a measured affinity, and never fabricate a K_D**
  (`MASTER_BLUEPRINT.md §9`).
- **Two generators:** *BoltzGen* (peptide-anything / macrocycle-anything protocols) and *EvoBind2*
  (MSA-free, AF2-objective cyclic/linear peptide binder design). Different inductive biases → different
  hit rates and folds. The **mini-protein foil** (Project-06 binder workflow) is the third arm for the
  peptide-vs-protein comparison.

**Why this is hard and what realistic success looks like.** De novo **peptide and macrocycle** hit
rates are **modest and chemistry-dependent**, and predicted affinity for short peptides is
**unreliable** — *rank, don't trust absolute numbers*. A peptide that passes every layer is a
*hypothesis*: a low `pae_interaction` is **not** a measured affinity, the Boltz-2 score is **not** a
K_D, and a peptide that "binds" in silico may be **degraded by proteases or unable to cross
membranes**. Success for this capstone = a rigorous, honestly-reported campaign with linear-vs-cyclic
and peptide-vs-protein comparisons, honest hit-rate accounting, and a **peptide-appropriate**
(SPPS + stability + permeability) validation plan — **not** a guaranteed working peptide.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** peptides are small, so **AF2/Boltz-2 scoring and Boltz-2 affinity on small
> inputs run on a free T4**. A **full macrocycle campaign prefers Colab Pro** (more designs, the
> macrocycle protocol). The notebooks run end-to-end on a deterministic **`mock`** backend with no GPU
> so you can build the plumbing anywhere; switch to the real backend on Colab. **Pin upstream commits
> and verify them** (the version-verify cell) — and the **BoltzGen public release is moving, so verify
> it explicitly**.

### BoltzGen (peptide-anything / macrocycle-anything)
- **What it does / where it fits:** the primary generator — proposes **linear-peptide** (peptide-
  anything) and **macrocycle** (macrocycle-anything) binders against the target cleft. The core of
  notebook 02.
- **Install:** upstream BoltzGen release — **VERIFY the current public release + URL before the course
  starts** (it is moving; mark clearly which release you used and pin it). The version-verify cell
  HTTP-checks the pinned URL.
- **Key parameters that matter here:** `target_pdb` (cleaned MDM2 cleft), cleft/hotspot residues (the
  p53 sub-pockets), peptide `length`, the **`cyclic`** flag (head-to-tail), `num_designs`.
- **Compute:** small linear peptides T4-tractable; a **macrocycle campaign prefers Pro**.
- **Typical call:**
  ```bash
  # On Colab; pin the release you used. VERIFY the public BoltzGen interface first.
  # peptide-anything (linear) / macrocycle-anything (cyclic) against the cleaned MDM2 cleft.
  boltzgen design --target mdm2_cleft.pdb --hotspots A54,A67,A73,A93,A100 \
      --length 12 --cyclic --num_designs 200   # interface is illustrative — verify the real CLI
  ```

### EvoBind2 (cyclic / linear peptide binder design)
- **What it does / where it fits:** MSA-free peptide binder design that optimizes a (cyclic) peptide
  sequence against the target with an AF2-based objective. The second generator in notebook 02.
- **Install:** `https://github.com/patrickbryant1/EvoBind` (pin a commit; **verify it still exists**).
- **Key parameters:** target structure + receptor residues (the cleft), peptide length, a **cyclic**
  flag for macrocycles, optimization iterations.
- **Compute:** small inputs are T4-tractable; longer optimizations are slower.
- **Typical call:**
  ```bash
  # EvoBind2 (pin commit); receptor = cleaned MDM2 cleft, target the p53 sub-pockets.
  python evobind.py --receptor mdm2_cleft.pdb --target_residues A54,A67,A73,A93,A100 \
      --peptide_length 12 --cyclic   # verify the exact flags against the pinned repo
  ```

### AF2 / Boltz-2 (ColabFold; jwohlwend/boltz)
- **What it does / where it fits:** re-predicts each peptide–MDM2 **complex** and yields
  `pae_interaction` (interface confidence) + interface pLDDT; **Boltz-2** additionally emits an
  **affinity ranking signal**. The orthogonal/self-consistency check + the ranking signal for the
  filter.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2); Boltz
  `https://github.com/jwohlwend/boltz` (Boltz-2). Pin commits/versions.
- **Key parameters:** complex (peptide + MDM2) input; for Boltz-2, the affinity head. Parse
  `pae_interaction` (mean inter-chain PAE) and the affinity score (**relative only**).
- **Compute:** small peptide complexes OK on **T4**, including Boltz-2 affinity. Campaign-scale
  re-prediction is the slow step — batch overnight.

### RFpeptides (concepts) + mini-protein foil
- **RFpeptides** — cyclic-peptide design *concepts* (read the paper for the macrocycle design logic;
  verify current availability). Used as conceptual grounding, not a required install.
- **Mini-protein foil** — for the **peptide-vs-protein** comparison, `scripts/peptide_tools.py`
  exposes `design_miniprotein_foil(...)`; the real path defers to the **Project-06 binder workflow**
  (BindCraft / RFdiffusion-binder + ProteinMPNN, **A100**). See `projects/project_06_pdl1_binder`.

### Shared `filtering_pipeline.py` + Boltz-2 ranking
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. Do **not** fork it — iterate
  against `shared/` and PR back.
- **Boltz-2 affinity** (notebooks 03/05): **scaffold / relative ranking only** — report which hits to
  test first, **never a fabricated K_D**.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (peptides small; T4 often enough, Pro for macrocycle campaign)
01_define_explore   → MDM2 cleft prep (Phe19/Trp23/Leu26 sub-pockets) + binder metrics table + mock hello-world (linear + cyclic)
02_generate         → linear + macrocyclic campaigns (BoltzGen peptide/macrocycle, EvoBind2); vary length/constraint; AF2/Boltz-2 pAE + Boltz-2 affinity (rank); results CSVs (mock here; real calls + compute note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per modality → ranked CSV
04_validate         → linear-vs-cyclic + peptide-vs-protein (mini-binder foil) figures + cleft-engagement + cyclization-feasibility notes
05_validation_plan  → SPPS + protease-stability + permeability plan; controls (known p53-peptide positive, scrambled-sequence negative, unrelated); D-amino-acid/stapling stretch; Boltz-2 affinity ranking (scaffold)
```
For Project 09 the standard slots map to: *02 = the linear + macrocyclic peptide campaign* (the core),
*04 = the linear-vs-cyclic + peptide-vs-protein modality comparison*, *05 = the
SPPS/protease-stability/permeability validation plan*.

## 4. Filtering cutoffs for this design type
These are the shared `"binder"` cutoffs (`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`). Peptides are
short, so treat these as *enrichment* thresholds, and expect more noise than for a folded mini-binder.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs predicted peptide; noisier for short peptides) |
| pLDDT | ≥ 80 (mean) | local confidence of the peptide (NOT stability, NOT permeability) |
| **pae_interaction** | **≤ 10 Å** | **interface confidence — the key metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) — physics layer |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality in the cleft |
| Boltz-2 affinity score | (no cutoff) | **relative RANK only — NOT a K_D**; use to prioritize, never to pass/fail |
| cleft overlap | ≥ 0.5 (project-specific) | covers enough of the p53 sub-pockets to compete with p53 |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail; less meaningful for short peptides) |

> Reminder: **no in-silico metric perfectly separates true from false binders**, and for **short
> peptides predicted affinity is especially unreliable**. Filters enrich; they do not guarantee.
> `pae_interaction` is the best single interface metric, but a low value is *confidence*, not
> *affinity*. The Boltz-2 affinity score is a *relative rank*, full stop.

## 5. Interpreting results
- A *good* peptide design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10**, favorable
  interface energy, `sc` ≥ 0.6, and a footprint that covers the **Phe19/Trp23/Leu26 sub-pockets** (so
  it can *compete* with p53). For a macrocycle, also a *feasible* ring (sensible head-to-tail / side-
  chain closure, plausible ring size).
- A *suspicious* one: low `pae_interaction` but the footprint **misses the cleft sub-pockets** (won't
  displace p53); or a high Boltz-2 affinity rank treated as if it were a measured K_D (it is not).
- **Survival-at-each-layer plot:** read it as a funnel — steep drops show which layer discriminates.
  Report it **per modality** (linear / macrocycle / mini-protein) so the comparisons are fair.
- **Hit rate:** report `N passing all layers / N generated`, separately per modality, with the
  layer-by-layer survival counts. Report the *distribution*, not just the best.
- **Linear vs cyclic:** compare hit rate, `pae_interaction`, cleft overlap, and the
  stability/feasibility framing (cyclization buys protease stability but costs synthesis effort).
- **Peptide vs mini-protein:** compare against the foil — when is the peptide/macrocycle the right
  modality (oral/cell-penetrant potential) versus a folded mini-binder (higher hit rate, easier
  expression)?

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| BoltzGen install / CLI not found | the public BoltzGen release/interface moved | Re-run the version-verify cell; find the current public release; pin it and log it; if unavailable, run EvoBind2 as the primary generator |
| Colab OOM on the macrocycle arm | macrocycle campaign too large for a T4 | Shrink `num_designs`; switch the macrocycle arm to Colab Pro; keep the linear arm on T4 |
| All peptides fail self-consistency | bad cleft prep, wrong chain, short-peptide noise | Re-clean MDM2, confirm the chain + cleft residues from the p53 interface; expect noisier scRMSD for short peptides; lower the peptide-length where needed |
| `pae_interaction` good but footprint **off the cleft** | cleft residues not the p53 sub-pockets | Re-derive the cleft from the Phe19/Trp23/Leu26 footprint; add the cleft-overlap check (nb 04) |
| Treating the Boltz-2 score as a K_D | misreading the affinity signal | It is a **relative rank only**. Use it to prioritize synthesis order; never report it as affinity or fabricate a K_D |
| Macrocycle "design" can't actually be synthesized | ring chemistry ignored | Add cyclization-feasibility notes (nb 04): head-to-tail vs side-chain, ring size, non-canonical residues; flag infeasible rings |
| Hit rate looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N, not the best |

## 7. Experimental validation reference (for the D4 plan)
> **Peptides are NOT validated like E. coli mini-binders.** They are made by **solid-phase peptide
> synthesis (SPPS)** and need **stability and permeability** assays in addition to binding.
- **Synthesis:** **SPPS** (Fmoc chemistry) for linear peptides; macrocyclization (head-to-tail or
  side-chain, e.g. lactam / disulfide / a hydrocarbon staple) as a post-assembly or on-resin step.
  D-amino acids, N-methylation, and stapling are introduced here (they raise synthesis complexity).
- **Characterization tiers:** purity (HPLC + mass spec) → **binding** (SPR/BLI vs immobilized MDM2, or
  a **fluorescence-polarization displacement** assay of a labeled p53 peptide) → **protease stability**
  (serum / trypsin / chymotrypsin half-life — the key reason to cyclize) → **permeability** (PAMPA /
  Caco-2 — the key reason a macrocycle could be oral/cell-penetrant) → cell-based p53-pathway
  reactivation (functional readout).
- **Controls (mandatory):**
  - **Positive:** a **known p53-mimetic peptide / stapled peptide** (e.g. the ATSP-7041 lineage) to
    confirm the MDM2 reagent and the displacement assay are active.
  - **Negative (scrambled-sequence):** take your **own** top design and **scramble its sequence** — it
    must **lose** binding. This is the cleanest specificity control.
  - **Unrelated-peptide negative:** an unrelated peptide of similar length that should not bind MDM2.
- **Report:** every in-silico number is a **hypothesis** until measured; report the experimental hit
  rate honestly; **never imply measured binding or fabricate a K_D**.

## 8. Responsible research
This project designs **competitive p53-mimetic** peptides/macrocycles to a human oncology **PPI**
target (MDM2) for the **therapeutic purpose of restoring p53 tumor-suppressor function** — an in-scope
therapeutic purpose under `MASTER_BLUEPRINT.md §7`. In-scope purpose here: oncology PPI restoration /
diagnostics only. Out of scope: enhancing pathogen transmissibility/virulence, toxins, immune-evasion
tools, or any design intended to cause harm. Any real peptide synthesis or gene-synthesis order must go
through a biosecurity-screening provider (IGSC member), and wet-lab work requires institutional
biosafety/ethics approval. Students must not overstate results or imply experimental validation that
was not done — a design is a hypothesis, and the Boltz-2 affinity score is a relative rank, not a K_D.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: BoltzGen
2025 (verify the release), EvoBind2 (Bryant), Kussie 1996 (MDM2–p53 / 1YCR), Wohlwend 2025 (Boltz-2),
an RFpeptides / cyclic-peptide-design paper, a macrocycle/oral-peptide therapeutic review, and
Pacesa 2025 (BindCraft) for the mini-protein foil.
