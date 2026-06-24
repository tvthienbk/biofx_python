# Project 02 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** ProteinMPNN is an *inverse-folding* model: given a fixed
backbone, it predicts amino-acid identities position by position. You control its output mostly with
three knobs — **sampling temperature** (how greedily it picks the most-likely residue), **backbone
noise** (Gaussian noise added to backbone coordinates before encoding, which regularizes against an
over-idealized input), and **sequences-per-backbone** (how many independent samples you draw). Those
knobs trade off four things you care about, and the goal of this project is to *map* that trade-off:

- **Sequence recovery** — fraction of positions matching a native/reference sequence. A sanity check,
  **not** a quality target; typical ProteinMPNN recovery is ~40–50% and higher is not automatically
  better (high recovery can just mean low diversity).
- **Recapitulation / foldability** — design the sequence, *predict* its structure (AF2/ESMFold), and
  measure the Cα-RMSD back to the input backbone (**scRMSD**; < 2 Å is the field-standard
  self-consistency bar). This is the single most important design metric here. It says the sequence
  is *consistent with* the fold — it does **not** prove the protein folds, is stable, or expresses.
- **Diversity** — per-position **Shannon entropy** across the sampled sequences. Low temperature
  collapses diversity; you want enough to give the downstream filter real choices.
- **Expressibility (proxies only)** — net charge at pH 7.4, hydrophobic-patch fraction, and a
  CamSol-style heuristic. These are *predictors of solubility/aggregation risk*, **not** measurements
  of expression. Treat them as triage, not truth.

**The key concepts a student must understand:** inverse folding vs forward folding; self-consistency
(design → predict → scRMSD); the temperature/noise/seqs grid and what each axis does; per-position
entropy as a diversity measure; and the difference between a *heuristic solubility score* and a real
expression result.

**Why this is hard and what realistic success looks like.** There is **no single best setting**:
lower temperature buys recovery and foldability but kills diversity; higher temperature and noise buy
diversity at the cost of foldability; solubility proxies and foldability do not always agree. A
realistic outcome is a **Pareto map** of settings (you cannot improve foldability without losing
diversity, etc.) plus a **settings cheat-sheet** that says "for goal X, use setting Y," with honest
caveats. Typical numbers: recovery ~40–50%; recapitulation success and predicted solubility both
*vary with settings* and with backbone quality. Success = a clean, honest, reproducible map — not a
record number, and never a fabricated expression result.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### ProteinMPNN
- **What it does / where it fits:** the core inverse-folding step — backbone → sequence. The object
  of study in this project.
- **Install:** clone the upstream repo `https://github.com/dauparas/ProteinMPNN`. *Verify it still
  exists and pin the commit before the course starts* (the version-verify cell in `02_generate`
  HTTP-checks this URL). These repos change — pin a commit hash in your `LOG.md`.
- **Key parameters that matter for this project:**
  - `--sampling_temp` — the **temperature** axis: sweep `{0.1, 0.2, 0.3, 0.5}`. Lower = greedier,
    higher recovery, lower diversity.
  - `--backbone_noise` — the **noise** axis: sweep `{0.0, 0.1, 0.2}`. Adds coordinate noise; small
    amounts can improve robustness on idealized de novo backbones.
  - `--num_seq_per_target` — the **seqs/backbone** axis: sweep `{8, 16, 48}`.
  - `--pdb_path` / `--pdb_path_chains`, `--out_folder`, `--seed`, optional `--fixed_positions_jsonl`.
- **Compute:** **free T4 (or even CPU) — seconds per backbone.** MPNN is *not* your bottleneck.
- **Typical command / call:**
  ```bash
  # Pin a commit; this is the documented real call the mock backend stands in for.
  python ProteinMPNN/protein_mpnn_run.py \
      --pdb_path data/inputs/backbone_001.pdb \
      --out_folder results/mpnn/backbone_001 \
      --num_seq_per_target 16 --sampling_temp "0.2" --backbone_noise "0.1" --seed 37
  ```

### LigandMPNN
- **What it does / where it fits:** the successor that is ligand/metal/nucleic-acid-aware; for this
  monomer project it is an alternative backend and a forward pointer to ligand-binding projects.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the commit; verify it exists).
- **Key parameters:** similar temperature/seqs knobs; `--model_type protein_mpnn` reproduces
  ProteinMPNN behavior, so you can run both from one install.
- **Compute:** free T4 / CPU, seconds.
- **Typical call:**
  ```bash
  python LigandMPNN/run.py --model_type protein_mpnn \
      --pdb_path data/inputs/backbone_001.pdb --out_folder results/ligmpnn/backbone_001 \
      --number_of_batches 1 --batch_size 16 --temperature 0.2
  ```

### ColabFold (AlphaFold2) / ESMFold — recapitulation
- **What they do / where they fit:** predict the designed sequence's structure so you can measure
  **scRMSD** back to the input backbone. **ESMFold** (single-sequence, seconds) is the triage
  predictor; **AF2 full-MSA** is the more trusted but slower confirmation. This is the **compute
  bottleneck** of the project at sweep scale — batch and triage.
- **Install:** ESMFold via HuggingFace `transformers` (`EsmForProteinFolding`); ColabFold via the
  official notebook / `localcolabfold` (pin the commit).
- **Key parameters:** ESMFold sequence-length limit on T4 (~400 aa); AF2 `num_recycles`, `msa_mode`.
- **Compute:** ESMFold free T4 (seconds–min); AF2 free T4 OK for monomers but slow at scale —
  **batch overnight or triage with ESMFold first.**
- **Typical call:** see `scripts/mpnn_tools.py` (recapitulation is wrapped behind a `recapitulate()`
  TODO) and Project 01's `scripts/predict.py` for the prediction wrapper pattern.

### Solubility / expressibility proxies (Biopython + heuristics)
- **What they do:** cheap in-silico predictors of solubility/aggregation risk computed from sequence:
  **net charge at pH 7.4**, **hydrophobic-patch fraction** (run-length of hydrophobic residues), and a
  **CamSol-style** linear combination. They live in `scripts/mpnn_tools.py`.
- **Important:** the `camsol_like` score is a **teaching heuristic, NOT real CamSol** (Sormanni 2015,
  which uses a calibrated per-residue intrinsic-solubility profile and a structurally-corrected
  variant). Label every figure that uses it as a heuristic.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → metrics table + stand up mpnn_tools + a mock recapitulation; design ONE backbone, print recovery + scRMSD
02_design_campaign  → the systematic sweep over temperature × noise × seqs across 20–30 backbones → results/sequences.csv
03_filter_and_rank  → multi-layer filter via shared/filtering_pipeline.py (design_type="monomer") → ranked CSV + figures
04_analysis_figures → per-setting recovery/recapitulation/diversity/solubility; Pareto-optimal settings; consensus vs single
05_validation_plan  → the MPNN settings cheat-sheet + codon/tag strategy + experimental plan with controls
```
For Project 02 the standard notebook slots map to: *02 = the parameter sweep* (the "campaign" is a
settings sweep, not novel backbone generation), *04 = the Pareto/trade-off analysis*, *05 = the
cheat-sheet + wet-lab plan*.

## 4. Filtering cutoffs for this design type (`design_type="monomer"`)
Start from the blueprint monomer defaults; this project's *output* refines which settings reach them.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD (recapitulation) | < 2.0 Å | self-consistency: predicted structure matches the input backbone |
| pLDDT (mean) | > 85 | local confidence of the recapitulation (NOT stability, NOT expression) |
| pae_interaction | n/a | monomer — no interface |
| Net charge at pH 7.4 | avoid |z| ≫ 0 extremes | very high net charge can hurt solubility (proxy, soft cutoff) |
| Hydrophobic-patch fraction | lower is safer | large exposed hydrophobic runs raise aggregation risk (proxy) |
| `camsol_like` heuristic | higher = more soluble (relative) | teaching heuristic, NOT real CamSol — use to *rank*, not to gate |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they do
> not guarantee. The solubility proxies are *heuristics* — report false positives and never present a
> proxy score as an expression result.

## 5. Interpreting results
- A *good* design at a given setting: scRMSD < 2 Å, high mean pLDDT, moderate net charge, low
  hydrophobic-patch fraction, and a favorable `camsol_like` score *relative to the batch*.
- A *suspicious* one: high pLDDT but high scRMSD (confident about the wrong fold), or a great
  recapitulation paired with a big exposed hydrophobic patch (likely folds in silico, risky to
  express).
- **Per-setting tables / Pareto map:** for each (temperature, noise, seqs) cell, report mean
  recovery, recapitulation rate (fraction with scRMSD < 2 Å), per-position entropy, and the
  solubility proxies. A setting is **Pareto-optimal** if no other setting beats it on every objective
  at once; plot the foldability ↔ diversity ↔ solubility frontier and read the cheat-sheet off it.
- **Diversity:** per-position Shannon entropy across the N sequences of a backbone; near-zero entropy
  means temperature is too low to give the filter choices.
- **Hit rate:** report `N recapitulating / N generated` *per setting*, not a single cherry. Include
  the settings that failed.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM during recapitulation | ESMFold/AF2 sequence too long for T4 | cap length (~400 aa for ESMFold); triage with ESMFold; batch AF2 overnight; move full-MSA AF2 to A100 |
| ProteinMPNN install/run fails | upstream repo changed | use the pinned commit; re-check `protein_mpnn_run.py` flags; log the version |
| Sweep takes forever | you're recapitulating *every* sequence with AF2 | recapitulate with ESMFold first; only run AF2 on the survivors; MPNN itself is seconds, the predictor is the cost |
| Sequence recovery looks ~5% (random) | reference/native sequence misaligned to the backbone, or scoring gaps | align by residue numbering first; ignore non-standard residues; check chain IDs |
| All sequences identical (entropy ≈ 0) | temperature too low | this is expected at temp 0.1 — that's the finding; raise temperature for diversity |
| `camsol_like` "predicts expression" claim | conflating a heuristic with a measurement | it does not — relabel as an aggregation-risk *proxy*; only wet-lab express→SDS-PAGE→SEC measures expression |
| Designs fail self-consistency at high noise | backbone noise 0.2 perturbs an already-idealized backbone | lower `--backbone_noise`; report the noise sensitivity as a result |

## 7. Experimental validation reference (for the D4 plan)
This project does no wet lab itself, but your plan tells a lab how to test the settings you recommend:
- **Codon optimization:** optimize the chosen sequences for the expression host (e.g., *E. coli*
  codon usage), avoid strong mRNA secondary structure near the start codon, and consider an
  N-terminal His-tag (cleavable) for purification. Order genes only through a biosecurity-screening
  provider (IGSC member).
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight induction (low temperature favors
  soluble expression of de novo monomers); note when a different host is needed.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF/CD for fold + thermal
  stability) → deep (structure, SEC-MALS/SAXS).
- **Controls:** positive control = a **known-good natural monomer sequence** (expresses + folds);
  negative control = a **deliberately high-hydrophobic-patch design** (expected to express poorly /
  aggregate — tests that your proxy points the right way); unrelated-protein control.

## 8. Responsible research
This is a methods/tooling project optimizing a sequence-design step for foldable, soluble **monomers**;
it designs no binder, antibody, toxin, or pathogen-targeting protein, so its dual-use surface is low.
See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: building safe, well-characterized MPNN
sequence-design know-how for the cohort. If you later apply these settings to a functional target,
adopt that project's responsible-research framing first. Synthesis screening (IGSC-member provider) +
institutional biosafety/ethics approval are required for any wet-lab work.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Dauparas 2022 (ProteinMPNN), Dauparas 2024 (LigandMPNN), Sumida 2024 (MPNN for expression/stability),
Jumper 2021 (AF2), Lin 2023 (ESMFold), Hsu 2022 (ESM-IF), Sormanni 2015 (CamSol).
