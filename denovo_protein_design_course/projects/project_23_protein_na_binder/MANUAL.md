# Project 23 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** We want a **small de novo protein** (≈40–90 aa) that binds a **chosen DNA or
RNA sequence motif** — a transcription-factor box, an operator, an RNA hairpin, etc. Such proteins are
the basis of **gene-editing modulators, RNA-targeting therapeutics, and synthetic transcription
factors**. We scaffold a backbone **near the nucleic acid** (RFdiffusion), design its sequence with the
**nucleic-acid-aware LigandMPNN**, model the protein–NA complex, and triage in silico — then plan an
EMSA / fluorescence-anisotropy assay. The target is a nucleic acid, not a protein; that changes both the
sequence designer (LigandMPNN, not ProteinMPNN) and the validation assay (EMSA/anisotropy, not SPR
against a protein).

**Key concepts a student must understand:**
- **How proteins read nucleic acids:** *base-specific* contacts (side-chain H-bonds/vdW to base edges,
  mostly in the DNA **major groove**) + *shape readout* (sequence-dependent groove geometry) encode
  **specificity**; *backbone/phosphate* contacts are strong but **generic** and do **not** encode which
  sequence is bound. A binder that uses only backbone contacts sticks to *any* NA.
- **Why LigandMPNN, not ProteinMPNN:** ProteinMPNN designs from protein backbone context only — it is
  **blind to the nucleic acid** and cannot place residues to read specific bases. **LigandMPNN
  conditions on non-protein atoms, including DNA/RNA**, so its interface residues are chosen with the NA
  in context. That difference is the scientific core of this project (notebook 04 benchmarks the two).
- **Self-consistency (scRMSD):** design a backbone → design its sequence → predict that sequence →
  Cα-RMSD between designed and predicted. `< 2.5 Å` is the binder self-consistency bar.
- **`pae_interaction` (protein–NA complex model):** the predicted aligned error **across the
  protein–NA interface** — the key complex-confidence metric (low ≈ confident *relative* placement of
  protein and nucleic acid). It is **not** affinity and **not** specificity.
- **Specificity (the real metric):** `specificity_score = score(scrambled motif) − score(intended
  motif)`. **Positive and large ⇒ prefers your motif ⇒ specific.** Confidence layers do not test this;
  the **specificity gate** (notebook 03) does, and the wet-lab **scrambled-NA control** (notebook 05)
  is what actually proves it.

**Why this is hard and what realistic success looks like.** Protein–NA design is **newer and harder
than protein–protein** binder design. The dominant failure mode is **non-specific backbone gripping**:
confident-looking designs that bind the generic phosphate backbone, not your bases. Expect many
in-silico hits to be non-specific, and the confident→specific drop to be steep. A passing design is a
**hypothesis**: `pae_interaction` is confidence, the computational specificity score is a *proxy*, and
**EMSA / fluorescence-anisotropy with a scrambled-NA control is mandatory**. There is **no fabricated
K_D** in this project. Success = a rigorous, honestly-reported campaign with a clear
confidence-vs-specificity hit-rate accounting and a controlled validation plan — **not** a guaranteed
binder.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** **RFdiffusion near the nucleic acid** and **protein–NA complex modeling**
> (Boltz-2 / AF3-style) at campaign scale want an **A100** (Colab Pro+ or a cluster). **LigandMPNN and
> ProteinMPNN are CPU-cheap** — the sequence-design step is *not* the bottleneck; the modeling is. A
> free **T4** runs only a *small fallback campaign* (few backbones, a small modeling batch). The
> notebooks run end-to-end on a deterministic **`mock`** backend with no GPU so you can build the
> plumbing anywhere; switch to the real backend on Colab Pro / A100. **Pin upstream commits and verify
> them** (the version-verify cell) — and **especially verify LigandMPNN's nucleic-acid model and
> RFdiffusion's NA protocol**, which evolve.

### LigandMPNN (nucleic-acid-aware) — the central tool
- **What it does / where it fits:** designs a protein sequence for a backbone **with the DNA/RNA in
  context**, so interface residues are chosen to contact the bases/backbone. The core of notebook 02.
- **Install:** upstream `https://github.com/dauparas/LigandMPNN` (pin a commit). *Verify the
  nucleic-acid (`ligand_mpnn`) model is the current one before the course.*
- **Key parameters that matter here:** `--pdb_path` (backbone **+ NA** complex), `--model_type
  ligand_mpnn` (NA-aware), `--temperature` (0.1–0.3; lower = more conservative), `--number_of_batches`/
  `--batch_size` (sequences per backbone), `--fixed_residues`/`--redesigned_residues` (focus the
  interface). For the NA-blind baseline, run **ProteinMPNN** (or LigandMPNN with the NA removed).
- **Compute:** CPU-cheap; runs on a T4 or even CPU. **Not** the bottleneck.
- **Typical call:**
  ```bash
  # NA-aware design (pin commit). The PDB MUST include the DNA/RNA chain as context.
  python run.py --model_type ligand_mpnn --pdb_path backbone_with_NA.pdb \
      --out_folder out/ --temperature 0.1 --number_of_batches 8
  ```

### RFdiffusion (scaffold near the nucleic acid)
- **What it does / where it fits:** diffuses a protein binder backbone **docked against the NA target**,
  holding the nucleic acid as fixed context so the backbone forms a complementary recognition surface.
  Sequence is designed afterwards by LigandMPNN. The first step of notebook 02.
- **Install:** `https://github.com/RosettaCommons/RFdiffusion` (pin a commit). **Verify the current
  nucleic-acid protocol** — RFdiffusion's NA support is evolving; if NA-context diffusion is
  unavailable in your build, scaffold against the protein chain of a known protein–NA complex and
  re-introduce the NA at the modeling step.
- **Key parameters:** `contigmap.contigs` (binder length; keep the NA chain fixed), diffusion
  `noise_scale`, `inference.num_designs` (hundreds of backbones on A100; a few on T4).
- **Compute:** small batches OK on T4; **hundreds of backbones want A100/HPC.**
- **Typical call:**
  ```bash
  # RFdiffusion with the NA held as fixed context (pin commit; verify the NA protocol).
  ./scripts/run_inference.py 'contigmap.contigs=[<NA chain fixed>/0 50-90]' \
      inference.num_designs=200 inference.output_prefix=out/na_binder
  ```

### Boltz-2 (protein–NA complex modeling) — the key metric source
- **What it does / where it fits:** models each **protein–NA complex** and yields `pae_interaction`
  (interface PAE between the protein and the NA chain) + interface pLDDT. The self-consistency/
  confidence check for the complex (notebook 02/04). Boltz-2 supports nucleic-acid chains.
- **Install:** `https://github.com/jwohlwend/boltz` (pin a commit). AF3-style servers also model
  protein–NA; ColabFold/AF2 is a weaker protein–protein-only fallback (no general NA support).
- **Key parameters:** build a YAML/FASTA with the protein sequence + the DNA/RNA motif; run `boltz
  predict`; parse the protein↔NA interface PAE → `pae_interaction`, mean pLDDT, and scRMSD.
- **Compute:** the slow step — small inputs OK on T4; campaign-scale prefers A100. Batch overnight.

### Shared `filtering_pipeline.py` (+ the specificity gate)
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. We reuse the `"binder"`
  **confidence** cutoffs (scRMSD/pLDDT/pae) and **leave `rosetta_dG`/`sc` unset** (those are
  protein–protein interface metrics). Do **not** fork the module — iterate against `shared/` and PR back.
- **Specificity gate** (notebook 03, project-specific, on top of the shared layers): keep only designs
  that pass the confidence layers **and** have `specificity_score ≥ margin`. This is the protein–NA
  layer the shared module does not encode.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → choose DNA/RNA motif + protein–NA recognition / LigandMPNN-NA theory + metrics table + mock hello-world
02_design_campaign  → RFdiffusion near the NA → LigandMPNN (NA-aware) design (+ ProteinMPNN NA-blind baseline) → Boltz-2 complex model; specificity vs scrambled; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; + specificity gate; survival per designer → ranked CSV + specific_candidates.csv
04_analysis_figures → LigandMPNN-vs-ProteinMPNN benchmark (confidence + specificity rate) + intended-vs-scrambled specificity scatter + novelty; CRISPR-modulator framing (extension)
05_validation_plan  → EMSA / fluorescence-anisotropy plan, scrambled-NA + dead-mutant + unrelated controls, expression strategy; CRISPR-modulator validation (stretch)
```
For Project 23 the standard slots map to: *02 = scaffold-near-NA + LigandMPNN campaign* (the core),
*04 = the LigandMPNN-vs-ProteinMPNN benchmark + specificity analysis*, *05 = the EMSA/anisotropy plan
with scrambled-NA controls*.

## 4. Filtering cutoffs for this design type
We reuse the shared `"binder"` **confidence** cutoffs and add a **specificity gate** on top.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs predicted protein backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the protein (NOT stability) |
| **pae_interaction** | **≤ 10 Å** | **protein–NA interface confidence — the key complex metric** |
| **specificity_score (dScore)** | **≥ ~1.5 (tune)** | **prefers the intended motif over a scrambled one — the protein–NA-specific gate** |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail) |
| rosetta_dG / sc | *unset* | protein–protein interface metrics; not used for protein–NA here |

> Reminder: **no in-silico metric perfectly separates true from false binders, and confidence is not
> specificity.** Filters enrich; they do not guarantee. A low `pae_interaction` with `specificity_score
> ≈ 0` is a non-specific backbone-gripper. Expect false positives and report them. The computational
> specificity score is a **proxy** — the scrambled-NA EMSA/anisotropy control is the real test.

## 5. Interpreting results
- A *good* NA-binder design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10**, **and a
  clearly positive `specificity_score`** (prefers the intended motif over the scramble).
- A *suspicious* one: great `pae_interaction` but `specificity_score ≈ 0` (confident but non-specific —
  reads the backbone, not the bases), or a model that places the protein along the phosphate backbone
  rather than in the major groove / on the base edges.
- **Survival-at-each-layer plot:** read it as a funnel — and remember the **specificity gate** is the
  extra protein–NA drop the shared `report()` figure does not draw; report it explicitly.
- **Hit rate:** report **two** numbers — the *confidence* hit rate (`N passing the shared layers / N
  generated`) **and** the *confident-AND-specific* rate — separately for **LigandMPNN** and
  **ProteinMPNN**. The gap is the specificity problem, quantified.
- **Head-to-head:** the value of LigandMPNN should show up in the **specificity rate** (NA conditioning
  helps it read the bases), not necessarily in raw confidence. Report the distribution, not the best.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for RFdiffusion-near-NA or complex modeling | Use a few backbones + a small Boltz-2 batch; move the full campaign to A100/HPC. LigandMPNN itself is cheap. |
| LigandMPNN ignores the NA | wrong model or NA not in the input PDB | Use `--model_type ligand_mpnn` and confirm the DNA/RNA chain is present in `--pdb_path`; verify the current NA model commit |
| RFdiffusion has no NA protocol | upstream changed / build lacks NA support | Verify the pinned commit's NA protocol; fallback: scaffold against the protein chain of a known complex, re-add the NA at modeling |
| `normalize_motif` raises on your motif | IUPAC ambiguity code (e.g. S, W, N) or wrong alphabet | Expand the motif to a concrete A/C/G/T (DNA) or A/C/G/U (RNA) sequence; RNA uses U, DNA uses T |
| Great `pae_interaction`, `specificity_score ≈ 0` | non-specific backbone-gripper | Keep as a flagged case; tighten the specificity gate; prefer designs strong on **both**; re-derive interface residues to read bases |
| All designs non-specific | backbone-only interface, wrong scaffold placement, NA not in LigandMPNN context | Re-scaffold so the protein sits in the major groove / on base edges; confirm NA-aware design; expect a low specific rate (it is normal) |
| Boltz-2 won't model the NA | NA chain mis-specified / unsupported residue | Check the YAML/FASTA NA chain format; confirm Boltz-2 supports your NA type; AF3-style server as fallback |
| Hit rate looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report **both** confidence and specificity rates + N, not the best design |

## 7. Experimental validation reference (for the D4 plan)
- **Expression / reagents:** protein binders in *E. coli* BL21(DE3), His-tagged, 16–18 °C overnight;
  IMAC + SEC (small 40–90 aa → high yield expected). Synthesize the **target NA oligo** (DNA: HPLC
  duplex; RNA: IVT or synthesized) with a **5′ fluorophore** (FAM/Cy5) for anisotropy; **also order a
  scrambled-NA oligo** of the same length/composition.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → **binding** (**EMSA** gel-shift
  and/or **fluorescence anisotropy/polarization** titration vs the labeled target NA → apparent
  affinity) → **specificity** (repeat the *same* titration vs the **scrambled-NA** control; report the
  ratio) → deep (co-crystal / cryo-EM of the protein–NA complex; competition assays).
- **Controls (mandatory):**
  - **Scrambled-NA negative:** the same assay vs a scrambled motif (same composition) — a specific binder
    binds it much more weakly. **Required** — this is the cleanest specificity control.
  - **Dead-mutant negative:** your **own** top design with its predicted NA-interface (base-reading)
    residues mutated (→ Ala) — must lose binding to the intended motif.
  - **Unrelated-protein negative:** an unrelated protein of similar size/charge — should not shift the NA.
  - **Positive:** a known binder of the motif (the natural protein, or a published designed binder) to
    confirm the labeled-NA reagent and assay are working.

## 8. Responsible research
This project designs **nucleic-acid-binding proteins** for **gene-editing modulation, RNA-targeting
therapeutics, and synthetic transcription factors** — defensible therapeutic / basic-science purposes
under `MASTER_BLUEPRINT.md §7`, with **low dual-use risk**. In-scope purpose here: neutralizing/
therapeutic / basic-science framing only (e.g., an anti-CRISPR-like modulator that makes editing
*safer/more controllable*; an RNA element you *block*). Out of scope: enhancing pathogen
transmissibility/virulence, toxins, evasion of biosecurity screening, or any design intended to cause
harm — including a CRISPR modulator used to defeat safety safeguards. Any real gene-synthesis order
(protein genes **and** NA oligos) must go through a biosecurity-screening provider (IGSC member), and
wet-lab work requires institutional biosafety/ethics approval. Students must not overstate results or
imply experimental validation that was not done — a design is a hypothesis, and **no K_D is fabricated**.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Dauparas
2024 (LigandMPNN — nucleic-acid support), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN),
Wohlwend 2025 (Boltz-2, protein–NA), a protein–DNA/RNA recognition review, a designed-DNA-binding-protein
paper, and an EMSA / fluorescence-anisotropy methods reference.
