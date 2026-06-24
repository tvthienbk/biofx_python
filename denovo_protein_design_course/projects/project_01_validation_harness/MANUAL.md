# Project 01 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
A structure predictor takes a sequence and returns a 3-D model plus *confidence* estimates.
In de novo design we use these in two ways: (a) to ask "does this sequence fold to the shape I
designed?" (**self-consistency**), and (b) to triage thousands of candidates down to a few worth
making. The metrics:

- **pLDDT** (0–100): per-residue confidence in the *local* structure. High pLDDT means the model
  is confident about local geometry — it is **not** a thermostability or ΔG measurement, a
  near-universal misreading. Mean pLDDT > 80 is a common "well-folded" heuristic.
- **PAE** (predicted aligned error, Å): expected error in the relative position of residue pairs.
  Low inter-domain / inter-chain PAE (often < 10 Å, and `pae_interaction` for complexes) signals
  a confident *relative* arrangement — critical for binders/complexes, where pLDDT alone misleads.
- **pTM / ipTM**: global (and interface) fold-confidence scalars.
- **Self-consistency scRMSD**: design the backbone → design a sequence for it → *predict* that
  sequence's structure → measure Cα-RMSD between designed and predicted backbones. **scRMSD < 2 Å**
  is the field-standard "self-consistent" bar. This is the single most important design metric.
- **TM-score / novelty**: TM-align or Foldseek vs the PDB; TM < 0.5 to the nearest natural fold
  indicates a *novel* fold.

Why this is hard and what realistic success looks like: **no single metric perfectly separates
experimental successes from failures.** Predictors are trained on natural proteins and can be
overconfident on de novo sequences. A realistic outcome for this project is a **composite**
predictor with good-but-imperfect AUC, plus an honest map of where it fails (e.g., overconfident
on idealized helical bundles, underconfident on novel folds). Success = calibrated, reproducible,
honestly characterized — not "100% accurate."

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### ColabFold (AlphaFold2)
- **What it does / where it fits:** MSA-based structure prediction; the reference standard for
  self-consistency and the most trusted confidence signal.
- **Install:** the official ColabFold notebook / `localcolabfold`. *Verify the repo and notebook
  still exist and pin the commit before the course starts.*
- **Key parameters:** `num_recycles` (3 default; raise for hard cases), `msa_mode`
  (full MSA vs single-sequence — the **ablation** in P2), `model_type`, `num_models`.
- **Compute:** free T4 OK for monomers up to a few hundred residues; long sequences/many recycles
  approach the T4 ceiling — batch and watch memory.
- **Typical call:**
  ```bash
  # via the ColabFold batch API inside the notebook
  colabfold_batch input.fasta out_dir/ --num-recycle 3 --msa-mode mmseqs2_uniref_env
  ```

### ESMFold
- **What it does / where it fits:** single-sequence (MSA-free) predictor; *fast* triage and a
  useful **orthogonal** check against AF2 (different inductive bias).
- **Install:** HuggingFace `transformers` (`EsmForProteinFolding`). Pin `transformers` version.
- **Key parameters:** sequence-length limit on T4 (~400 aa comfortable); `chunk_size` to fit memory.
- **Compute:** free T4 OK; much faster than AF2 because it skips MSA generation.
- **Typical call:**
  ```python
  from transformers import AutoTokenizer, EsmForProteinFolding
  # load fp16/low-mem on T4; output.plddt and output.positions
  ```

### Boltz-2
- **What it does / where it fits:** open all-atom structure + affinity predictor; a *third*
  orthogonal opinion and (stretch) a predicted-affinity signal for complexes.
- **Install:** the Boltz repo (`pip install boltz`). Pin the version; verify the weights download.
- **Key parameters:** `--recycling_steps`, `--diffusion_samples`; affinity mode for complexes.
- **Compute:** heavier than ESMFold; small monomers OK on T4, complexes/affinity prefer A100.
- **Typical call:**
  ```bash
  boltz predict input.yaml --out_dir out/ --recycling_steps 3
  ```

### TM-align / Foldseek, Biopython, scikit-learn, py3Dmol
- TM-align/Foldseek for TM-score + novelty; Biopython for parsing/Cα-RMSD; scikit-learn for
  ROC/PR and the composite logistic model; py3Dmol for in-notebook 3-D visualization.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → metric definitions + a unified predict() wrapper; predict ONE sequence, visualize
02_design_campaign  → curate the labeled dataset (designs w/ known outcomes + natural refs); predict ALL; MSA-depth ablation
03_filter_and_rank  → load predictions into shared/filtering_pipeline.py; run self-consistency + orthogonal layers; ranked CSV + figures
04_analysis_figures → ROC/PR per metric (AUC); best single + composite predictor; AF2/ESMFold/Boltz agreement
05_validation_plan  → write the Validation SOP card (calibrated cutoffs by type) + cohort usage guide
```
For Project 01 the standard notebook slots map to: *02 = dataset curation + prediction* (instead of
generative design), *04 = the calibration analysis*, *05 = the SOP* (instead of a wet-lab plan).

## 4. Filtering cutoffs for this design type
This project's *output* is the calibrated version of this table; start from the blueprint defaults
and **replace them with your measured cutoffs** (with AUC + N behind each).
| Metric | Starting cutoff | Why |
|--------|-----------------|-----|
| scRMSD | < 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT | > 80 (mean) | local confidence (NOT stability) |
| pAE_interaction (complexes) | < 10 Å | interface confidence (when labels include complexes) |
| TM-score to PDB | < 0.5 = novel | novelty, not a pass/fail of correctness |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they
> do not guarantee. Report false positives and negatives explicitly.

## 5. Interpreting results
- A *good* design: scRMSD < 2 Å, high mean pLDDT, low PAE, agreement across AF2/ESMFold/Boltz.
- A *suspicious* one: high pLDDT but high scRMSD (confident about the wrong fold), or large
  disagreement between predictors (often a sign of a hard/novel case — interesting, flag it).
- **ROC/PR:** plot true-positive vs false-positive rate as you sweep each metric's threshold; AUC
  summarizes separability. PR is more informative when positives are rare.
- **Composite:** fit a simple logistic regression on the standardized metrics; report its
  cross-validated AUC vs the best single metric. Resist overfitting — keep it to a few features
  and report N.
- **Agreement:** correlate the three predictors' pLDDT/scRMSD; disagreement maps your harness's
  blind spots.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | sequence too long / MSA too deep for T4 | use ESMFold for triage; cap length; reduce recycles; move AF2 full-MSA to A100 |
| ColabFold install fails | upstream notebook/repo changed | use the pinned commit; update the install cell; log it |
| ESMFold very slow | running on CPU | confirm GPU runtime; load in fp16/low-mem |
| scRMSD looks random | mismatched residue numbering in Cα-RMSD | align by sequence first; check chain IDs; use Biopython superimposer correctly |
| ROC AUC ≈ 0.5 | label noise or wrong metric sign | re-check outcome labels + provenance; verify metric direction (lower scRMSD = better) |
| Tiny dataset, unstable curves | too few labeled items | add items; report confidence intervals; bootstrap the AUC |

## 7. Experimental validation reference (for the D4/SOP)
This project does no wet lab itself, but your SOP tells downstream projects what to do:
- Expression: typically *E. coli* BL21(DE3), 16–18 °C overnight; note when mammalian expression is needed.
- Characterization tiers: go/no-go (express → SDS-PAGE → SEC) → basic (DSF, CD, binding assay) → deep (structure, SEC-MALS/SAXS).
- **Controls every downstream project must run** (put this in your SOP): positive control (a known-good design/natural protein), negative control (scrambled-interface or catalytic dead-mutant), and an unrelated-protein control.

## 8. Responsible research
This project analyses existing published sequences and designs no new functional proteins, so its
dual-use surface is low. See `MASTER_BLUEPRINT.md §7`. In-scope purpose: building safe, calibrated
validation infrastructure. If you extend the dataset, exclude sequences whose primary function is
harmful and log provenance/license for each item. Any wet-lab follow-up by other projects requires
synthesis screening + institutional approval.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Jumper 2021 (AF2), Dauparas 2022 (ProteinMPNN/self-consistency), Lin 2023 (ESMFold),
Wohlwend 2025 (Boltz-2), plus the source papers for every dataset item.
