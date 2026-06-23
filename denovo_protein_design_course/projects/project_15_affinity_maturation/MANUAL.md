# Project 15 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** You are **maturing an existing antibody** — lead optimization, not de novo
design. Starting from a *known* antibody-antigen complex with a *measured* KD, you propose a **small,
testable set** of **CDR** mutations that should raise affinity while keeping **developability**. The
**framework is FIXED**; only CDR positions (especially the long, dominant **CDR3**) are varied. Most of
the work is *scoring* mutations (cheap) and *verifying the binding pose survives* (the heavy check).

**Key concepts you must understand:**
- **Affinity maturation as editing.** You inherit a real paratope and a real starting KD. A mutation is
  an edit to a CDR contact residue; you rank edits, you do not invent affinities.
- **CDR contact residues (the paratope).** Compute antibody residues within ~4.5 Å of any antigen atom
  (Biopython `NeighborSearch`) and intersect with the CDR spans — focus mutations there. Derive CDR
  boundaries with a real numbering scheme (**ANARCI**: IMGT/Kabat/Chothia), not by eye.
- **ESM-1v (Meier 2021).** A general protein language model; its masked-marginal Δ-log-likelihood
  log P(mut) − log P(wt) **ranks** point mutations (> 0 = model-favored). It does **not** see the
  antigen and is **not** an affinity or a ΔΔG — always cross-check with the structure.
- **AbLang / AbLang2 (Olsen 2022).** An *antibody-specific* language model (trained on OAS repertoires);
  scores how "natural-looking" an antibody sequence is — a developability/expressibility prior that a
  general PLM lacks. Use it to sanity-check CDR sequences and ProteinMPNN redesigns.
- **ProteinMPNN CDR redesign (framework fixed).** Conditioned on the complex backbone, it proposes new
  CDR-loop sequences while a **design mask fixes** every framework (and non-target-CDR) position —
  exploring multi-residue loop changes single-mutation scanning misses.
- **Pose maintenance (the decisive filter).** AF2-Multimer `pae_interaction` (interface confidence;
  ≤ 12) + `scrmsd` (variant Fv vs the **parent** pose; ≤ 3.0). The question is "does it still dock the
  antigen the same way", **not** "is affinity higher". A high ESM-1v rank with a broken pose is a false
  lead.
- **Developability liabilities.** A mutation can introduce a chemical liability into a CDR: **NG/NS** Asn
  deamidation, **DG/DS** Asp isomerization, exposed **Met/Trp** oxidation, an **N-glyc sequon**, or an
  **unpaired Cys**. Triage these *before* synthesis. The functions in `maturation_tools.py` are
  **teaching heuristics, NOT** real TAP / structure-based predictors — swap in the real tools for claims.
- **Epistasis.** Combined mutations are not the sum of singles; they can reinforce or interfere
  (especially when close in 3-D). Only SPR confirms a combo; in silico you reason + re-check the pose.

**Why this is hard / realistic success.** Computational maturation **ranks**; it does not measure
affinity, and **most predicted improvers do not validate.** A strong project produces a *small, ranked,
pose-maintained, developable* candidate set and a sound SPR/DSF plan with controls. **Never fabricate
KD/ΔΔG numbers** — rank only. Success = a rigorous, honestly-reported campaign, not a "tighter binder".

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### ESM-1v (protein-LM mutation scoring)
- **What it does / where it fits:** ranks single CDR mutations by masked-marginal Δ-log-likelihood (the
  cheap, high-value first pass). `maturation_tools.esm1v_score(seq, mutation)`.
- **Install:** `https://github.com/facebookresearch/esm` (pip `fair-esm`; weights download on first use).
  **Verify it still exists and pin the commit** before the course starts.
- **Key parameters:** the `esm1v_t33_650M_UR90S_{1..5}` models (**ensemble all 5** for the published
  score); mask each CDR position; score the 19 substitutions.
- **Compute:** **light — CPU/T4 fine.** This is *not* the bottleneck.
- **Typical call (schematic):**
  ```python
  # fair-esm; pin the commit. Ensemble the 5 esm1v models, masked-marginal scoring.
  # for each CDR position p: mask p -> logits -> score = logP(mut) - logP(wt)
  ```

### AbLang / AbLang2 (antibody-specific LM)
- **What it does / where it fits:** antibody-naturalness/likelihood score; sanity-checks CDR sequences +
  ProteinMPNN redesigns. `maturation_tools.ablang_score(seq)`.
- **Install:** `https://github.com/oxpig/AbLang` — **AbLang2 supersedes it; VERIFY the current public
  repo at course start and pin it.**
- **Key parameters:** heavy/light model matching your chain; pseudo-log-likelihood over the chain.
- **Compute:** **light — CPU/T4 fine.**

### ProteinMPNN (CDR redesign, framework FIXED)
- **What it does / where it fits:** redesigns one CDR loop on the complex backbone while a design mask
  **fixes** all framework + non-target-CDR positions. `maturation_tools.mpnn_cdr_redesign(...)`.
- **Install:** `https://github.com/dauparas/ProteinMPNN` (pin the commit).
- **Key parameters:** `--fixed_positions` / a design mask so ONLY the chosen CDR varies; temperature
  (~0.1–0.3); number of sequences per loop.
- **Compute:** **CPU-fine / light.**

### AF2-Multimer (ColabFold) — pose maintenance (the HEAVY step)
- **What it does / where it fits:** scores each (variant Fv, antigen) complex → `pae_interaction` +
  scRMSD vs the parent pose. `maturation_tools.af2_pose_check(...)`. Drives the antibody filter.
- **Install:** `https://github.com/sokrypton/ColabFold` (prefer the official notebook; pin the commit).
- **Key parameters:** `model_type=multimer`, `num_recycles`.
- **Compute:** the **slow step** — small complexes OK on T4, but **batch overnight** and keep N small;
  Colab Pro helps. This is what makes the realistic tier **T4–Pro**.

### Developability (TAP / CamSol / deamidation) — REAL tools vs the teaching heuristics
- **What they do:** TAP (Raybould 2019) flags structure-based liabilities; CamSol (Sormanni 2015)
  predicts solubility; structure-based predictors flag deamidation/isomerization/oxidation hotspots.
- **In this project:** `maturation_tools.developability_scan()` flags **sequence** liability motifs in
  the CDRs as **clearly-labelled teaching heuristics** so the pipeline runs with no extra installs.
  **Swap in the real tools for any reportable developability claim.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → affinity-maturation + developability theory; pick the complex (measured KD); CDR contacts; metrics table; mock hello-world
02_generate         → score single CDR mutations (ESM-1v/AbLang) + ProteinMPNN CDR redesigns (framework fixed) → results/campaign.csv (+ version-verify cell)
03_filter_and_rank  → fp.Design objects → fp.run_pipeline(design_type="antibody") → fp.report() → ranked CSV + survival figure (enforces pose maintenance)
04_validate         → pose maintenance (pae vs scRMSD); developability liability scan; epistasis/combination reasoning
05_validation_plan  → SPR/BLI kinetics + DSF stability plan + specificity panel + controls (WT + destabilizing decoy)
```
The mock backend in `scripts/maturation_tools.py` lets every notebook run with no GPU; switch each
`tool="mock"` to `"esm1v"` / `"ablang"` / `"proteinmpnn"` / `"af2"` on Colab. All mock numbers are
**SYNTHETIC ranking scores** — never affinities.

## 4. Filtering cutoffs for this design type
From `shared/filtering_pipeline.DEFAULT_CUTOFFS["antibody"]`. Start here; justify any change.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD (vs parent pose) | ≤ 3.0 Å | self-consistency / pose maintenance (lenient — CDR loops are flexible) |
| pLDDT | ≥ 70 (mean) | local model confidence (NOT stability/affinity) |
| pae_interaction | ≤ 12 Å | variant Fv–antigen interface confidence (pose maintenance, NOT affinity) |
| developability liabilities | fewer = better | NG/DG deamidation, Met/Trp oxidation, N-glyc sequon, unpaired Cys in CDRs (**heuristic** — use real TAP) |
| ESM-1v Δ-LL | > 0 to prioritise | model-favored mutation (**ranking** signal, NOT a KD/ΔΔG) |
| AbLang naturalness | higher = better | antibody-natural CDR sequence (**ranking**/developability prior) |

> Reminder: **no in-silico metric measures affinity.** ESM-1v/AbLang rank; AF2-Multimer checks the pose;
> developability flags liabilities. Passing the filter means "still binds in the parent pose and is
> developable", **not** "binds tighter". Only SPR confirms a tighter KD. Report the rate, not the cherry.

## 5. Interpreting results
- A *promising* candidate: ESM-1v > 0 (model-favored), AbLang high, pose maintained
  (pae_interaction ≤ 12 **and** scRMSD ≤ 3.0 vs the parent), and **no new CDR liability** introduced.
- A *suspicious* one: high ESM-1v but a broken pose (high pae / high scRMSD — the LM never saw the
  antigen); a redesign with a great AbLang score that introduces an NG sequon or an exposed Met; a
  "specific" claim with no off-target counter-screen.
- **Survival-at-each-layer** (`fp.report`): how many candidates keep the pose + stay developable — your
  honest funnel. Compute N(pass)/N(scored) at each layer.
- **The small set is the point.** End with ≤ ~10 ranked mutations to TEST, plus the WT + decoy controls.
  A sprawling library is a failure of triage, not a strength.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| AF2-Multimer pose check is impossibly slow | it is the heavy step; too many variants | Keep N small; **batch overnight**; use Colab Pro; score singles/AbLang first (light) and only pose-check survivors |
| ESM-1v / AbLang install or weight download fails | repo/weights changed | Use the pinned commit; for AbLang **verify AbLang2** is the current repo; log the version |
| Every variant fails pose maintenance | bad complex prep / wrong parent chain / wrong CDR mapping | Re-clean the complex; re-extract the antibody chain; re-run ANARCI; superpose against the PARENT, not an arbitrary frame |
| ProteinMPNN changes framework residues | the design mask is wrong | Fix it: mask EVERY framework + non-target-CDR position; only the chosen CDR may vary |
| Every candidate "passes" on mock | you're on the deterministic mock backend | Mock numbers are SYNTHETIC ranking scores — switch to `tool="esm1v"`/`"af2"` for real metrics |
| A great-looking variant has no KD | you confused a ranking score for affinity | ESM-1v/AbLang/pae are NOT KD; only SPR (notebook 05) measures affinity — never report a predicted KD |
| Developability looks perfect | you used the heuristic scan, not real tools | Re-run with real TAP/CamSol + a structure-based deamidation predictor before any claim |

## 7. Experimental validation reference (for the D4 plan)
The realistic path **measures affinity directly** on a SMALL ranked set — there is no in-silico shortcut.
- **SPR/BLI kinetics:** capture the antibody/Fab; flow the antigen as analyte over a concentration
  series; global 1:1 fit → kon, koff, **KD**; compare KD_variant vs the parent's **measured** KD against
  a **pre-registered improvement margin**. Use monovalent Fab to avoid avidity artifacts.
- **DSF stability:** measure Tm; a tighter binder that drops Tm or aggregates is not a developable win.
- **Specificity panel:** the target antigen vs a related off-target (paralog/family member) vs an
  irrelevant protein (e.g., BSA) — confirm the variant did not broaden binding.
- **Controls (mandatory):** **positive = the WT parent** at its measured KD (the baseline every variant
  is compared to); **negative = a destabilizing decoy** (a deliberately bad mutation expected to LOSE
  affinity/stability — proves the assay detects a loss); plus the **specificity panel**.
- **Honest reporting:** report **N improved / N tested** — most predicted improvers will not validate.

## 8. Responsible research
This is a **therapeutic-antibody lead-optimization** project: maturing an existing antibody against its
(non-pathogen) target to raise affinity and keep developability. Dual-use risk is **low** — it improves a
therapeutic candidate, it does not create a hazard. In-scope purpose: therapeutic/diagnostic antibody
optimization. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended
to cause harm. Real gene-synthesis orders must go through a biosecurity-screening provider (IGSC member);
wet-lab work requires institutional biosafety/ethics approval. Do not overstate computational candidates
as validated higher-affinity binders. See `MASTER_BLUEPRINT.md §7`.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions/commits you actually used:
Meier 2021 (ESM-1v), Olsen 2022 (AbLang), Dauparas 2022 (ProteinMPNN), Evans 2021 (AF-Multimer),
Raybould 2019 (TAP), Dunbar 2014 (SAbDab), plus the deposition + the KD-reporting paper for your complex.
