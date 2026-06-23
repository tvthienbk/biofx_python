# Project 17 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** You are designing the three CDR loops (especially the long, dominant **CDR3**)
of a **nanobody (VHH)** — the single ~15 kDa variable domain of a camelid heavy-chain-only antibody — so
that they form a paratope against a chosen epitope on a **tumor-associated antigen (TAA)**. The
framework is fixed (a humanized VHH germline); the CDRs are the design variables. RFantibody diffuses
CDR-loop backbones onto the framework against the target epitope, then ProteinMPNN designs the loop
sequence; BoltzGen nanobody mode is an alternative generator.

**Key concepts you must understand:**
- **VHH / CDR structure** — one immunoglobulin domain, FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4. CDR3 is long and
  hypervariable and dominates the paratope. A long CDR3 lets VHHs reach concave epitopes (cryptic
  pockets) that conventional antibodies miss — but very long CDR3s are also a developability liability.
- **Epitope choice (the central decision)** — **overlapping** with an approved mAb's footprint (compete
  with / mimic a validated site) vs **non-overlapping / orthogonal** (enables biparatopic / bispecific
  constructs, avoids resistance tied to the mAb site). Bin designs by their contact footprint
  (`epitope_overlap()`).
- **Self-consistency (scRMSD)** — design backbone → design sequence → predict that sequence → measure
  Cα-RMSD designed-vs-predicted. The antibody bar is more lenient (≤ 3.0 Å) than monomers because CDR
  loops are flexible.
- **pae_interaction** — AF2-Multimer's confidence in the VHH–antigen *interface* arrangement; the key
  complex metric (cutoff ≤ 12 Å). It is **not** affinity.
- **CDR geometry / Ramachandran sanity** — IgFold/NanoBodyBuilder2 give a fast, antibody-aware backbone
  to sanity-check CDR-loop conformations (`cdr_geom`).
- **Developability** — TAP (structure-based liability flags), CamSol (solubility), humanness
  (OASis/Hu-mAb): you triage liabilities *before* synthesis. **The functions in `antibody_tools.py` are
  teaching heuristics, NOT these tools** — swap in the real ones for any reportable claim.
- **Specificity within the receptor family** — a TAA (HER2) sits in the HER/ErbB family (EGFR, HER3,
  HER4); a useful VHH must prefer its target over the relatives (the counter-screen).

**Why this is hard / realistic success.** De novo antibody/nanobody **hit rates are LOW.** A strong
campaign produces a *diverse, filtered pool*; the **display screen** (yeast/phage) is what turns that
pool into real binders. Treat every surviving design as a **screening input**, not a finished binder.
Success = a rigorous, honestly-reported campaign with a sensible screen plan — not a "binder".

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFantibody (RFdiffusion-Ab + ProteinMPNN)
- **What it does / where it fits:** the core de novo VHH generator — diffuses CDR-loop backbones onto a
  fixed framework against the target epitope, then ProteinMPNN designs the loop sequence.
- **Install:** `https://github.com/RosettaCommons/RFantibody` (conda env + weights). **Verify it still
  exists and pin the commit** before the course starts.
- **Key parameters:** target PDB + hotspot/epitope residues, the VHH framework, CDR-loop length ranges
  (especially CDR3), `num_designs` (set 500+ for the real campaign), ProteinMPNN temperature / seqs per
  backbone.
- **Compute:** **A100 strongly recommended.** Free T4 → a *tiny demo only* (a handful of designs). Plan
  the batch around the GPU; AF2-Multimer scoring is the slow step.
- **Typical call (schematic):**
  ```bash
  # inside the RFantibody env (see the repo's README; pin the commit)
  rfdiffusion_ab --target target.pdb --hotspots A557,A560,A579 --framework huVHH.pdb --num_designs 500
  proteinmpnn   --cdr_only ...        # design CDR sequences, framework fixed
  ```

### BoltzGen (nanobody mode)
- **What it does / where it fits:** an alternative de novo nanobody generator; use it for the
  RFantibody-vs-BoltzGen `[extension]` head-to-head.
- **Install:** **VERIFY the current public release/repo at course start** (the API is newer and changes);
  pin it. Mark this clearly in `LOG.md`.
- **Key parameters:** antigen + epitope, nanobody mode, number of designs.
- **Compute:** A100 recommended; verify the free-tier story for the release you pin.
- **Typical call:** see the release's documentation — do not assume an interface; pin and log it.

### AF2-Multimer (ColabFold)
- **What it does / where it fits:** scores each (VHH, antigen) complex → `pae_interaction` (the key
  metric), interface pLDDT, scRMSD. Also drives the **specificity panel** (VHH vs each receptor).
- **Install:** `https://github.com/sokrypton/ColabFold` (prefer the official notebook; pin the commit).
- **Key parameters:** `model_type=multimer`, `num_recycles`.
- **Compute:** small complexes OK on T4; campaign-scale prefers **A100**. The slow step — batch overnight.

### IgFold / ImmuneBuilder (NanoBodyBuilder2)
- **What it does / where it fits:** fast, antibody-aware VHH structure prediction (no MSA) for CDR-loop
  geometry (`cdr_geom`) and a cheap orthogonal check.
- **Install:** `https://github.com/oxpig/ImmuneBuilder` (pin the commit).
- **Compute:** cheap — **T4 fine.**

### Developability (TAP / CamSol / humanness) — REAL tools vs the teaching heuristics
- **What they do:** TAP (Raybould 2019) flags structure-based liabilities (CDR length, hydrophobic /
  charge patches, charge symmetry); CamSol (Sormanni 2015) predicts solubility; Hu-mAb / OASis / AbLang
  score humanness against human repertoires.
- **In this project:** `antibody_tools.developability()` returns `tap_score` / `camsol_like` /
  `humanness` as **clearly-labelled teaching heuristics** so the pipeline runs with no extra installs.
  **Swap in the real tools for any reportable developability claim** — the heuristics teach the *axes*,
  not the verdict.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → TAA + CDR biology; choose epitope (overlapping vs not) + framework; metrics table; mock VHH hello-world
02_generate         → the VHH design campaign (RFantibody/BoltzGen; A100) → results/campaign.csv (+ version-verify cell)
03_filter_and_rank  → fp.Design objects → fp.run_pipeline(design_type="antibody") → fp.report() → ranked CSV + survival figure
04_validate         → epitope choice (overlap vs not); receptor-family specificity panel; developability/humanness figures
05_validation_plan  → pooled display-screen plan + downstream format (VHH-Fc imaging / CAR binder) + specificity panel + controls
```
The mock backend in `scripts/antibody_tools.py` lets every notebook run with no GPU; switch each
`tool="mock"` to `"rfantibody"` / `"boltzgen"` / `"af2"` on Colab. All mock numbers are **SYNTHETIC**.

## 4. Filtering cutoffs for this design type
From `shared/filtering_pipeline.DEFAULT_CUTOFFS["antibody"]`. Start here; justify any change.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 3.0 Å | self-consistency (more lenient than monomers — CDR loops are flexible) |
| pLDDT | ≥ 70 (mean) | local confidence (NOT stability/affinity) |
| pae_interaction | ≤ 12 Å | VHH–antigen interface confidence (the key complex metric) |
| CDR geometry RMSD | small | CDR-loop / Ramachandran sanity vs an IgFold/NanoBodyBuilder2 model |
| TAP-like score | fewer = better | developability liabilities (**heuristic** — use real TAP to report) |
| CamSol-like | higher = better | solubility (**heuristic** — use real CamSol to report) |
| humanness | higher = better | human-likeness (**heuristic** — use real Hu-mAb/OASis to report) |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they do
> not guarantee. For de novo nanobodies the pass rate is low by design — that is expected, and it is why
> survivors go to a display screen. Report the hit rate, not the cherry.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 3.0, mean pLDDT ≥ 70, pae_interaction ≤ 12, clean CDR geometry, low
  developability liabilities, target pae clearly below the off-target receptors.
- A *suspicious* one: high pLDDT but high pae_interaction (confident fold, dubious interface); very long
  CDR3 with hydrophobic patches (developability risk); a "specific" claim with no margin over EGFR/HER3/HER4.
- **Survival-at-each-layer** (`fp.report`): how many of the generated pool pass each layer — your honest
  hit-rate table. Compute the rate as N(pass)/N(generated) at each layer.
- **Specificity margin:** best off-target pae minus target pae; > 0 means the VHH prefers the target.
- **Epitope binning:** `epitope_overlap()` of each design's contact footprint vs the approved-mAb
  footprint tells you competing (overlap) vs orthogonal (non-overlap).

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for the campaign | Reduce `num_designs`; run a *tiny* RFantibody demo on T4; move the real campaign to A100/HPC |
| RFantibody install fails | repo/weights changed or env mismatch | Use the pinned commit; follow the repo's conda env exactly; log the version |
| BoltzGen API errors | release changed since pinning | Re-verify the current public release; re-pin; update the call; log it |
| All designs fail self-consistency | bad target prep / wrong epitope residues / framework mismatch | Re-clean the TAA structure; re-read epitope residues off the verified surface; check the framework |
| Every design "passes" on mock | you're on the deterministic mock backend | Mock numbers are SYNTHETIC — switch to `tool="rfantibody"`/`"af2"` on A100 for real metrics |
| "Specific" VHH binds all receptors | epitope on a conserved family surface | Choose a HER2-unique surface patch; report the specificity margin vs EGFR/HER3/HER4 |
| Developability looks great | you used the heuristics, not the real tools | Re-run with real TAP/CamSol/Hu-mAb before claiming developability |

## 7. Experimental validation reference (for the D4 plan)
The realistic path is **pooled display screening**, not direct characterization of single designs.
- **Display screen:** yeast surface display (Aga2p) or phage of the filtered VHH pool → FACS on labeled
  TAA over increasing stringency → NGS enrichment tracking → recover top clones.
- **Expression:** VHHs express well in *E. coli* (periplasm) or yeast; the VHH-Fc imaging format and CAR
  constructs use mammalian expression.
- **Characterization tiers:** go/no-go (display → FACS enrichment) → basic (express recovered clones,
  SPR/BLI K_D, DSF stability) → deep (cell binding on TAA+ vs TAA− lines, structure, in-format function).
- **Controls (mandatory):** positive = a known anti-TAA nanobody spiked into the pool (must enrich);
  negative = the same pool vs an **irrelevant antigen** (winners must not enrich) **and** an
  unrelated/non-binding VHH on display; **receptor-family specificity panel** (HER2 vs EGFR/HER3/HER4) as
  the counter-screen.
- **Downstream format:** VHH-Fc (avidity + half-life) or radiolabeled bare VHH for imaging; or VHH as the
  CAR antigen-binding domain (hinge/TM + 4-1BB + CD3ζ).

## 8. Responsible research
This is a **therapeutic/diagnostic oncology** project: a designed nanobody against a human tumor antigen
(HER2/EGFR/mesothelin) for imaging or as a CAR binder. In-scope purpose: diagnostic/therapeutic
oncotargets. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended
to cause harm. Real gene-synthesis orders must go through a biosecurity-screening provider (IGSC member);
wet-lab work (including CAR-T) requires institutional biosafety/ethics approval. Do not overstate
computational designs as validated binders. See `MASTER_BLUEPRINT.md §7`.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions/commits you actually used:
Bennett 2025 (RFantibody), BoltzGen 2025 (verify), Abanades 2023 (ImmuneBuilder), Evans 2021
(AF-Multimer), Dauparas 2022 (ProteinMPNN), Raybould 2019 (TAP), plus the depositions for every
structure (1N8Z / 1IVO / any model).
