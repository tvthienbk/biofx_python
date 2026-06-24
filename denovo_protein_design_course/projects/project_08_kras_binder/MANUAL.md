# Project 08 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** **KRAS** is a small GTPase that cycles between a **GDP-bound "off"** state and
a **GTP-bound "on"** state; in the "on" state it engages effectors (RAF, PI3K, RalGDS) to drive
proliferation. Activating mutations (most often at codon 12 — **G12C, G12D, G12V**) lock KRAS "on" and
drive ~25% of human cancers. For decades KRAS was **"undruggable"**: its surface is small, smooth,
highly charged, and lacks a deep small-molecule pocket, and its nucleotide affinity is picomolar so you
cannot out-compete GTP. The **covalent G12C inhibitors** (sotorasib, adagrasib) changed that by
trapping the mutant cysteine in the **switch-II pocket** of the GDP state — but they are allele-specific
(G12C only), and **G12D and the other isoforms remain hard**. A **de novo binder** can read a larger,
shape-complementary epitope than a small molecule, so designing binders to the **switch I / switch II**
regions or to an **allele-specific surface** is a genuine frontier. The binder is targeted at a cleaned
KRAS G-domain **in a defined nucleotide state**, at hotspot residues drawn from the chosen epitope.

**Key concepts a student must understand:**
- **Epitope / hotspots:** the small set of KRAS residues the binder is steered to contact — switch I
  (~res 30–38), switch II (~res 60–76), or an allele pocket (e.g. the G12C cysteine, or the surface
  around G12D). Choosing them on purpose is the design decision that matters.
- **Nucleotide state:** GDP "off" vs GTP/analog "on" present **different switch conformations**, so the
  binder surface you are targeting **only exists in one state**. Common non-hydrolyzable GTP analogs:
  **GppNHp / GMPPCP**. Record the state on every design (`BinderDesign.nucleotide_state`).
- **Isoform selectivity (the hard part):** KRAS, HRAS, and NRAS are ~90%+ identical in the G-domain and
  **nearly identical across the switch regions**. A binder that hits KRAS usually hits HRAS/NRAS too. The
  project's centerpiece is to **model each candidate vs HRAS/NRAS** and report a **selectivity gap**.
- **Allele selectivity:** does the binder exploit the **mutant-specific** surface (e.g. G12C/G12D) so it
  spares WT KRAS? This is what makes a binder a *precision* therapeutic, not a pan-RAS toxin.
- **Self-consistency (scRMSD):** design backbone → design sequence → predict → Cα-RMSD designed-vs-predicted.
  `< 2.5 Å` is the binder bar.
- **`pae_interaction` (AF2-Multimer):** the **single most important binder metric** — predicted aligned
  error *across the binder–target interface*. Low (`≤ 10 Å`) ⇒ AF2-Multimer is confident about the
  *relative* placement of binder and KRAS. It is **confidence, not affinity**.
- **Interface energy (`rosetta_dG`, REU) + shape complementarity (`sc`):** the physics layer — is the
  interface favorable and well-packed, not just confidently placed.
- **Effector competition (extension):** a binder covering the switch regions could **block RAF/effector
  engagement**; switch-region footprint overlap is a geometry proxy for that blockade.
- **Two paradigms:** *BindCraft* hallucinates a binder with AF2 in the loop (one-shot); *RFdiffusion
  binder mode* diffuses a backbone against the target, then *ProteinMPNN* designs its sequence.

**Why this is hard and what realistic success looks like.** KRAS sits at the **harder end** of binder
targets — small, smooth, charged surface, and the real wall is **selectivity** (isoform and allele). In-silico
binder hit rates **vary widely by target and tool**, and the **great majority of in-silico hits fail
experimentally**; a low isoform `pae` delta is **not** measured selectivity. A binder that passes every
layer is a *hypothesis*: SPR/BLI **and an isoform panel** are mandatory. Success for this capstone = a
rigorous, honestly-reported campaign with hit-rate accounting, a **selectivity analysis**, and a
controlled validation plan — **not** a guaranteed working (or selective) binder. **No K_D is ever
fabricated.**

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** BindCraft, RFdiffusion binder mode, and AF2-Multimer at campaign scale want an
> **A100** (Colab Pro+ or a cluster). A free **T4** runs only a *small fallback campaign* (FreeBindCraft,
> small `num_designs`, a small RFdiffusion batch + ESMFold triage). The notebooks run end-to-end on a
> deterministic **`mock`** backend with no GPU so you can build the plumbing anywhere; switch to the real
> backend on Colab Pro / A100. **Pin upstream commits and verify them** (the version-verify cell).

### BindCraft (or FreeBindCraft)
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes binder backbone **and** sequence together, pre-filtered on interface confidence. Paradigm #1
  in notebook 02.
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**; replaces
  the PyRosetta dependency). *Verify both before the course starts.*
- **Key parameters that matter here:** `target_pdb` (cleaned KRAS **in the chosen nucleotide state**),
  `hotspot_residues` (switch I/II or the allele pocket), `binder_length` (≈50–90), `num_designs`
  (50–200 on A100; far fewer on T4).
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  # On Colab Pro (A100) via the BindCraft notebook / CLI; pin the commit you used.
  python bindcraft.py --settings kras_settings.json   # target=KRAS-GDP, hotspots=switch I/II, n=50-200
  ```

### RFdiffusion (binder mode) + ProteinMPNN
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a binder backbone docked against
  the KRAS hotspots; **ProteinMPNN** then designs a sequence per backbone. Paradigm #2 (500–1000 backbones).
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; binder protocol via ColabDesign
  `https://github.com/sokrypton/ColabDesign`. ProteinMPNN ships with both. Pin commits; *verify before the course.*
- **Key parameters:** `contigs` / `hotspot_res` (the switch I/II or allele-pocket residues), `binderlen`,
  diffusion `noise_scale`, `num_designs` (500–1000 backbones; small batch on T4); ProteinMPNN `temperature`
  (0.1–0.3) and `num_seq_per_target` (e.g., 8).
- **Compute:** RFdiffusion small batches OK on T4; **500–1000 backbones want A100/HPC.** ProteinMPNN is
  CPU-cheap. AF2-Multimer re-prediction of each design is the real bottleneck.
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs target the switch I/II hotspots on the KRAS chain.
  ./scripts/run_inference.py 'contigmap.contigs=[A1-169/0 60-90]' \
      'ppi.hotspot_res=[A32,A35,A38,A60,A71]' inference.num_designs=1000 inference.output_prefix=out/kras
  # then ProteinMPNN over the backbones, then AF2-Multimer.
  ```

### AF2-Multimer (ColabFold) — scoring AND the isoform panel
- **What it does / where it fits:** re-predicts each binder–KRAS **complex** → `pae_interaction` (key
  metric) + interface pLDDT. The **same** scorer, pointed at HRAS/NRAS, drives the **isoform-specificity
  panel** (`scripts/binder_tools.isoform_specificity` / `specificity_panel`).
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles` (raise for hard interfaces), pairing/MSA mode.
  Parse `pae_interaction` (mean PAE on inter-chain residue pairs).
- **Compute:** small complexes OK on T4; campaign-scale + isoform panel (×3 isoforms) prefers A100. This
  is usually the slowest step — batch overnight.

### Structural alignment (Biopython) — isoform analysis
- **What it does / where it fits:** align KRAS to HRAS/NRAS (and across alleles) to map which epitope
  residues actually differ, so you can reason about *whether selectivity is even achievable* at your
  chosen surface. Biopython's `Superimposer` (already used by `filtering_pipeline.ca_rmsd`) and a sequence
  alignment of the G-domains are enough at teaching grade; note where the switch residues are conserved.

### Shared `filtering_pipeline.py` + Boltz-2 (stretch)
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. Do **not** fork it — iterate
  against `shared/` and PR back.
- **Boltz-2** (stretch, notebook 05): predicted binding affinity on top hits — **scaffold only**; report
  *relative ranking* and caveats, **never fabricate a K_D**.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → KRAS biology; choose epitope/allele/NUCLEOTIDE STATE; clean KRAS G-domain; hotspot ID; binder metrics table; mock hello-world (incl. mock isoform panel)
02_design_campaign  → two-paradigm campaign: BindCraft (50-200) + RFdiffusion-binder (500-1000 -> ProteinMPNN); AF2-Multimer; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per paradigm -> ranked CSV
04_analysis_figures → BindCraft-vs-RFdiffusion benchmark (hit rate, interface energy, novelty) + ISOFORM-SPECIFICITY panel (KRAS vs HRAS/NRAS, selectivity gap) + effector-competition (block RAF) [extension] + figures
05_validation_plan  → SPR/BLI + ISOFORM-SPECIFICITY panel + controls (positive binder, scrambled-interface negative, unrelated) + NUCLEOTIDE-STATE test [stretch]; scrambled negatives; Boltz-2 affinity stretch (scaffold)
```
For Project 08 the standard slots map to: *02 = the two-paradigm binder campaign at the chosen KRAS
surface* (the core), *04 = the head-to-head benchmark **+ the isoform-specificity analysis***, *05 = the
SPR/BLI + isoform-specificity + nucleotide-state validation plan*.

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
| **isoform selectivity gap** | **report it** | KRAS `pae` vs best off-target (HRAS/NRAS) `pae`; positive ⇒ some selectivity — a *project-specific* read-out, not a hard pass/fail |

> Reminder: **no in-silico metric perfectly separates true from false binders**, and AF2-Multimer
> confidence is a **weak** proxy for *selectivity* — the isoforms are nearly identical across the
> switches. Filters enrich; they do not guarantee. `pae_interaction` low is *confidence*, not *affinity*;
> a positive selectivity gap is a *hypothesis* of selectivity, tested only by the isoform panel in the lab.

## 5. Interpreting results
- A *good* binder design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10**, `rosetta_dG`
  ≤ −30 REU, `sc` ≥ 0.6, a footprint on the intended KRAS surface, **and** a clear **selectivity gap**
  (worse `pae` on HRAS/NRAS, and ideally on the off-target alleles).
- A *suspicious* one: low `pae_interaction` but weak `rosetta_dG` (confident placement, poor interface);
  a great KRAS interface that scores **equally well on HRAS/NRAS** (no selectivity — likely pan-RAS); or
  a binder targeting a surface that is **identical** across isoforms (selectivity not even possible there).
- **Survival-at-each-layer plot:** read it as a funnel — steep drops show which layer discriminates.
  Report it **per paradigm**.
- **Selectivity gap:** report KRAS `pae` minus the best (lowest) off-target `pae`, per survivor and per
  paradigm. A binder is only a *KRAS* binder if it is meaningfully worse on HRAS/NRAS. Report the
  *distribution*, and be honest that the gap is a model artifact until tested.
- **Hit rate:** report `N passing all layers / N generated`, separately per paradigm, with the
  layer-by-layer survival counts. Report the *distribution*, not just the best.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for a binder campaign | FreeBindCraft + small `num_designs`; small RFdiffusion batch + ESMFold triage; move full campaign to A100/HPC |
| BindCraft install fails | upstream repo/commit changed; PyRosetta license | Use the pinned commit; try FreeBindCraft (no PyRosetta); log the path you used |
| All designs fail self-consistency | bad target prep, wrong chain, **wrong nucleotide state**, wrong hotspots | Re-clean KRAS, confirm the chain + state, re-derive hotspots from that structure; lower MPNN temperature |
| Binders bind KRAS **and** HRAS/NRAS equally | epitope is conserved across isoforms | Pick a surface with isoform-divergent residues (or an allele pocket); accept that some KRAS surfaces cannot be made selective; report it |
| `pae_interaction` good but `rosetta_dG` weak | confident placement, poor interface packing | Keep as a flagged case; tighten `sc`/`rosetta_dG`; prefer designs strong on both |
| Binder lands **off** the switch regions | hotspots not on the intended epitope | Re-select hotspots from the chosen surface; add the effector-competition check (nb 04) |
| RFdiffusion produces few foldable binders on KRAS | small/smooth surface; noise scale / contigs / length off | Sweep `noise_scale`, lengthen the binder, regenerate; a low per-backbone hit rate on KRAS is **normal** |
| Hit rate / selectivity looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N + the selectivity gap, not the best |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** binders in *E. coli* BL21(DE3), 16–18 °C overnight (small, His-tagged); the **KRAS
  reagent** is expressed (often as the G-domain, residues ~1–169) and **nucleotide-loaded** — prepare
  **GDP-loaded** and **GppNHp/GMPPCP-loaded** KRAS separately so you can test state dependence; keep Mg²⁺.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF stability; **SPR or BLI**
  vs immobilized KRAS for K_D/kinetics) → functional/selectivity (**isoform panel** vs KRAS/HRAS/NRAS;
  **nucleotide-state** comparison; effector-competition: does the binder block RAF-RBD binding to KRAS-GTP?)
  → deep (co-crystal / cryo-EM of the binder–KRAS complex, cell-based KRAS-pathway readout).
- **Controls (mandatory):**
  - **Positive:** a known KRAS binder (e.g. a published DARPin/monobody/binder, or a G12C-inhibitor
    complex as a state reference) → confirms the assay and the KRAS reagent are active.
  - **Negative (scrambled-interface):** take your **own** top design and scramble/mutate the interface
    residues → it must **lose** binding. Cleanest specificity control.
  - **Unrelated-protein negative:** an unrelated mini-protein of similar size → should not bind.
  - **Isoform panel (the centerpiece):** test the binder vs **KRAS, HRAS, and NRAS** under identical
    conditions → quantify selectivity. A pan-RAS binder is a far weaker result; report it honestly.
  - **Nucleotide-state test (`[stretch]`):** compare binding to **GDP-loaded** vs **GppNHp-loaded** KRAS
    → a state-specific binder should discriminate.

## 8. Responsible research
This project designs **inhibitory/blocking** binders to **KRAS**, a human **oncotarget**, for **cancer
therapeutics and diagnostics** — an in-scope therapeutic/diagnostic purpose under `MASTER_BLUEPRINT.md §7`.
In-scope purpose here: oncology therapeutics / diagnostics only. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause harm. Any real
gene-synthesis order must go through a biosecurity-screening provider (IGSC member), and wet-lab work
requires institutional biosafety/ethics approval. Students must not overstate results or imply
experimental validation that was not done — a design is a hypothesis, and a predicted selectivity gap is
not measured selectivity.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: a KRAS
druggability/structural-biology review; the G12C-inhibitor papers (sotorasib/adagrasib); Pacesa 2025
(BindCraft); Cao 2022 (target-structure-only minibinders); Watson 2023 (RFdiffusion); Dauparas 2022
(ProteinMPNN); Evans 2021 (AF2-Multimer); plus 1–2 frontier RAS-targeting design papers.
