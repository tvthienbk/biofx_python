# Project 03 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** RFdiffusion is a denoising diffusion model over protein
backbones: starting from noise, it iteratively produces 3-D Cα/backbone coordinates, optionally
conditioned on a target length and a secondary-structure (and block-adjacency) bias. The backbone
carries no sequence — so you redesign it with **ProteinMPNN**, then **fold the designed sequence
back** with AlphaFold2/ESMFold and ask: does the prediction match the backbone you designed? That
backbone-vs-prediction Cα-RMSD is **self-consistency RMSD (scRMSD)**, the field-standard proxy for
foldability. Separately, you ask how *new* the backbone is by comparing it to every fold in the PDB
with **Foldseek / TM-align**: the **TM-score** to the nearest natural fold measures novelty.

**Key concepts you must understand:**
- **scRMSD (foldability).** Design backbone → ProteinMPNN sequence(s) → predict structure → Cα-RMSD
  between designed and predicted backbone. **scRMSD < 2 Å** is the standard "self-consistent" bar.
  Because each backbone gets several MPNN sequences (e.g., 8), report the **best-of-N** scRMSD.
- **pLDDT.** Per-residue local confidence of the refold (0–100). High pLDDT supports a low scRMSD but
  is **not** a stability or ΔG measurement — a near-universal misreading.
- **TM-score / novelty.** TM-align or Foldseek vs the PDB; **TM < 0.5** to the nearest natural fold
  indicates a *novel* fold. TM-score is length-normalized and ranges 0–1. Novelty is a **coordinate,
  not a verdict** — a TM of 0.3 does not mean the design is wrong, only that it is structurally far
  from anything natural.
- **The frontier.** Plot novelty (x: 1 − TM, or TM itself) against scRMSD (y). The interesting object
  is the **Pareto frontier** — the envelope of designs that are simultaneously as novel and as
  foldable as possible — and how that envelope shifts with length and topology.

**Why this is hard and what realistic success looks like.** Predictors are trained on natural
proteins, so they (and the diffusion prior) are most reliable near natural fold space. **Self-consistency
success is high for short idealized helical (all-α) folds and drops steeply as novelty rises and
length grows; all-β topologies are the hardest** (β-sheets need precise long-range register that both
the generator and the predictor get wrong more often). A realistic outcome is **not** a uniform pass
rate but a clear trade-off: e.g., near-100% foldable at length 80 all-α, collapsing for length-300
all-β. Success = an honestly-reported frontier and a defensible **novelty budget**, not a hero design.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion (via the ColabDesign notebook)
- **What it does / where it fits:** generates monomer backbones (unconditional or
  secondary-structure-biased) — the campaign's first stage.
- **Install:** upstream repo `https://github.com/RosettaCommons/RFdiffusion`; the most robust Colab
  route is the **ColabDesign** RFdiffusion notebook `https://github.com/sokrypton/ColabDesign`.
  *Pin a commit/tag in a comment and verify both URLs still exist before the course starts (these
  tools change). The `00`/`02` version-verify cell HTTP-checks them.*
- **Key parameters that matter for this project:** `contigs` (e.g., `"80-80"` for a fixed-length
  monomer), `length`, secondary-structure / block-adjacency conditioning (the **all-α / all-β / mixed**
  bias), `num_designs`, `diffuser.T` (denoising steps, ~50), `seed`.
- **Compute:** **T4 only for small batches**; the full sweep (100s of backbones across lengths up to
  300 and three topologies) realistically needs an **A100 / HPC**. Do not try to run the whole campaign
  on a free T4 — batch a slice on T4, move the sweep to A100/Pro+ or a cluster.
- **Typical call:**
  ```bash
  # via the ColabDesign RFdiffusion notebook (pin the commit):
  ./run_inference.py 'contigmap.contigs=[80-80]' inference.num_designs=10 \
      inference.output_prefix=out/len80_alpha 'scaffoldguided.ss_bias=alpha'
  ```

### ProteinMPNN
- **What it does / where it fits:** designs a sequence for each generated backbone (no fixed
  positions for an unconditional monomer).
- **Install:** upstream `https://github.com/dauparas/ProteinMPNN` (also bundled in ColabDesign). Pin the commit.
- **Key parameters:** `--sampling_temp` (0.1–0.2 for foldable designs), `--num_seq_per_target` (8),
  `--backbone_noise` (0.0 for clean backbones), `--seed`.
- **Compute:** **CPU-fine / trivial on T4** — seconds per backbone.
- **Typical call:**
  ```bash
  python protein_mpnn_run.py --pdb_path backbone.pdb --num_seq_per_target 8 \
      --sampling_temp 0.1 --out_folder out/mpnn --seed 0
  ```

### ColabFold (AlphaFold2) / ESMFold
- **What it does / where it fits:** folds each designed sequence to measure self-consistency scRMSD.
  Use **ESMFold for fast triage** (MSA-free, seconds) and AF2 for the trusted check on top picks.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (pin commit); ESMFold via HuggingFace
  `transformers` (`EsmForProteinFolding`). Both are wrapped in `00_setup`'s helpers.
- **Key parameters:** AF2 `num_recycles` (3; raise for hard cases), `msa_mode`; ESMFold `chunk_size`.
- **Compute:** free **T4 OK** for monomers up to a few hundred residues; long sequences / many
  recycles approach the T4 ceiling — batch and watch memory.
- **Typical call:**
  ```python
  from transformers import AutoTokenizer, EsmForProteinFolding   # ESMFold triage
  # then ca_rmsd(designed_pdb, predicted_pdb) from filtering_pipeline for scRMSD
  ```

### Foldseek / TM-align (novelty scoring)
- **What it does / where it fits:** scores each design's structural novelty against the PDB (and
  optionally AFDB) — the novelty coordinate of the frontier.
- **Install:** Foldseek `https://github.com/steineggerlab/foldseek` (binary; pin the release);
  TM-align binary for exact pairwise TM-scores on top hits.
- **Key parameters:** Foldseek `easy-search` vs `easy-cluster`; the **PDB/AFDB database is downloaded
  separately** (`foldseek databases PDB pdb tmp`) and is **large — not committed** (see `data/README.md`).
- **Compute:** CPU; the database download/storage is the real cost, not GPU.
- **Typical call:**
  ```bash
  foldseek easy-search design.pdb pdb_db aln.m8 tmp --format-output "query,target,alntmscore"
  ```

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback) + version-verify cell
01_define_explore   → metric definitions (scRMSD, novelty); stand up rfdiff_tools; generate 10 (mock), self-consistency + novelty, visualize with py3Dmol
02_design_campaign  → the campaign: lengths {80,120,200,300} × SS-bias {α,β,mixed} → ProteinMPNN (8 seqs) → AF2/ESMFold self-consistency → results/backbones.csv  (real RFdiffusion ColabDesign call shown + A100 note)
03_filter_and_rank  → multi-layer filter via shared/filtering_pipeline.py (design_type="monomer"); scrmsd/plddt gate, tm_to_pdb reported → ranked CSV + figures
04_analysis_figures → novelty-vs-scRMSD frontier; per-topology + per-length success rates; RFdiffusion/FrameFlow/Genie2 comparison scaffold [extension]
05_validation_plan  → select novel-but-foldable set; synthesis/expression plan with paired controls; short MD stability check [stretch] (OpenMM scaffold)
```
For Project 03 the standard notebook slots map to: *02 = the generative campaign*, *04 = the frontier
analysis + tool comparison*, *05 = the synthesis plan + novelty budget*.

## 4. Filtering cutoffs for this design type
`design_type="monomer"` in `shared/filtering_pipeline.py` (`DEFAULT_CUTOFFS["monomer"]`).
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | < 2.0 Å | self-consistency / foldability (designed vs refolded backbone; best-of-8 MPNN seqs) |
| pLDDT | > 85 (mean) | local confidence of the refold (NOT stability) |
| TM-score to PDB | < 0.5 = novel | **novelty — REPORTED, not a pass/fail of correctness** |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they do
> not guarantee. **Foldability (scRMSD/pLDDT) gates; novelty (TM-score) is a coordinate you report**,
> never a filter — you would otherwise throw away foldable conservative designs that are valuable
> controls. Expect false positives and report them.

## 5. Interpreting results
- A *good* novel design: scRMSD < 2 Å **and** TM < 0.5 — foldable *and* far from natural fold space.
  These sit on the lower-left of a (TM-score, scRMSD) plot and define the frontier.
- A *suspicious* one: high pLDDT but high scRMSD (confident about the *wrong* fold — the predictor
  refolded the sequence into something other than the designed backbone), or a TM < 0.5 that is
  actually a Foldseek alignment artifact (too short / poor coverage) — re-check with TM-align.
- **The frontier plot:** scatter novelty (x) vs scRMSD (y), colored by topology and sized by length.
  The **Pareto envelope** is the set of designs no other design beats on both axes. Read the
  **novelty budget** off it: the most novelty (lowest TM) still achievable at scRMSD < 2 Å, per
  topology/length.
- **Survival-at-each-layer plot:** how many backbones pass self-consistency, then orthogonal
  agreement. For this project, break it down **by topology and length** — that breakdown *is* the result.
- **Hit rate:** N(scRMSD < 2 Å) / N(generated), reported per topology × length cell. Expect it to fall
  off toward long all-β.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for the full campaign (long backbones, many designs) | Reduce `num_designs`/length; batch; use ESMFold for triage; move the full sweep to A100/HPC |
| RFdiffusion/ColabDesign install fails | Upstream notebook/repo changed | Use the pinned commit; update the install cell; run the version-verify cell; log it |
| All designs fail self-consistency | MPNN temperature too high, or backbone genuinely unfoldable | Lower `--sampling_temp` to ~0.1; increase seqs/backbone; check the backbone isn't pathological (clashes, broken chain) |
| all-β designs almost never pass | Expected — β register is hard for generator + predictor | Report it honestly as a frontier result; don't over-tune to force passes |
| TM-score "novel" looks too good (TM≈0.2) | Foldseek alignment too short / low coverage | Confirm with pairwise TM-align; require reasonable alignment coverage before calling a fold novel |
| Foldseek DB download huge / fills disk | The PDB/AFDB database is large (tens of GB; AFDB far larger) | Use the PDB-only DB for the course; mount Drive or use HPC scratch; never commit it (see `data/README.md`) |

## 7. Experimental validation reference (for the D4 plan)
- Expression: typically *E. coli* BL21(DE3), 16–18 °C overnight; de novo monomers usually express
  solubly when they pass self-consistency, but novelty raises risk — note when mammalian expression
  might be needed for hard cases.
- Characterization tiers: go/no-go (express → SDS-PAGE → SEC for monodispersity) → basic (CD for
  secondary-structure content vs the designed topology, DSF for thermostability) → deep (crystallography
  or cryo-EM to confirm the *novel* fold; SEC-MALS/SAXS for solution shape).
- **Controls (mandatory, paired by design):** positive — a **conservative low-novelty, high-confidence
  design** expected to fold; the test case — a **HIGH-novelty risky design**; plus an **unrelated
  natural protein** control. The paired risky-vs-conservative comparison is the whole point: it tells
  you whether your *novelty budget* held up experimentally.

## 8. Responsible research
This is a methods/tooling project generating **novel monomeric proteins** and measuring foldability
and novelty; it designs no binder, toxin, or pathogen component, so its **dual-use surface is low**.
See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: building safe generative-design infrastructure
and characterizing the novelty–foldability trade-off. If a generated novel scaffold is later
repurposed toward a functional target (a binder, an enzyme), it must be re-evaluated under §7 before
proceeding. Synthesis screening (an IGSC-member provider) + institutional biosafety/ethics approval
are required for any wet-lab work. Do not overstate results: a low scRMSD is a *hypothesis* of
foldability, not experimental proof.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN/self-consistency), Jumper 2021 (AF2),
Lin 2023 (ESMFold), van Kempen 2024 (Foldseek), Zhang & Skolnick 2004 (TM-score/TM-align), and the
comparison methods you scaffold (Yim 2024 FrameFlow; Lin & AlQuraishi 2024 Genie2).
