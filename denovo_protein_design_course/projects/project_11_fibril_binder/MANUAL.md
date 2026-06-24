# Project 11 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** Tau (in Alzheimer's) and α-synuclein (in Parkinson's and other synucleinopathies)
are **intrinsically disordered as monomers** — they have no single stable fold. In disease they
assemble into **amyloid fibrils**: an ordered, repetitive **cross-β** stack whose protofilament
surface is now resolved by cryo-EM. We want a **small de novo binder** (≈50–90 aa) that sits on the
**exposed fibril surface** and — the crux — **recognizes the fibril conformation while rejecting the
disordered monomer**. A conformation-selective binder of this kind is the molecular basis of a
diagnostic **PET tracer** or fibril-detection assay, or an aggregation **modulator**. The binder is
targeted at the ordered cross-β core surface drawn from the cryo-EM fibril structure; the monomer is
the off-state it must avoid.

**Key concepts a student must understand:**
- **Conformation as the target.** The "target" is not a protein but a **conformation** of a protein.
  The fibril surface and the monomer are the *same sequence* in *different states*; the design must
  discriminate them.
- **Fibril-surface epitope / hotspots:** the exposed cross-β surface residues the binder grips. A good
  fibril epitope is **solvent-exposed on the protofilament** AND distinct from anything ordered in the
  (disordered) monomer — that is what makes selectivity possible.
- **Self-consistency (scRMSD):** design a backbone → design its sequence → predict that sequence →
  measure Cα-RMSD between designed and predicted. `< 2.5 Å` is the binder self-consistency bar.
- **`pae_interaction` (AF2-Multimer):** the predicted aligned error across the binder–target interface
  — the **key binder metric**. Low (`≤ 10 Å`) means AF2-Multimer is confident about the *relative*
  placement of binder and target. Here you compute it **per conformer** (fibril and monomer).
- **`specificity_gap` = `pae_monomer − pae_fibril`:** the project's signature metric. **Positive &
  large ⇒ the binder prefers the fibril** (good fibril confidence, poor monomer confidence). ~0 or
  negative ⇒ cross-reacts with (or prefers) the monomer ⇒ reject. It is a **teaching proxy on a model
  metric**, not a measured fold-selectivity; the monomer is disordered so its model adds uncertainty.
- **Interface energy (`rosetta_dG`, REU) + shape complementarity (`sc`):** the physics layer — is the
  fibril interface actually favorable and well-packed, not just confidently placed.
- **Two paradigms:** *BindCraft* hallucinates a binder with AF2 in the loop (one-shot); *RFdiffusion
  binder mode* diffuses a backbone against the fibril surface, then *ProteinMPNN* designs a sequence.
  Different inductive biases → different hit rates and folds.

**Why this is hard and what realistic success looks like.** A normal binder only has to bind. A
**conformation-specific** binder also has to **NOT bind** the abundant monomer — a much harder, dual
constraint. In-silico binder hit rates already vary widely by target and tool (single-digit to tens of
percent passing the filter), the flat cross-β fibril surface is a hard target, and the
**conformational-selective** rate on top of that is **lower still**; the **great majority of in-silico
hits fail experimentally.** A selective-looking design is a *hypothesis*: a low `pae_interaction` is
**not** a measured affinity, the `specificity_gap` is **not** a measured selectivity, and the
**fibril-vs-monomer assay is mandatory**. Success for this capstone = a rigorous, honestly-reported
campaign with a clear fibril hit rate, a clear **selective fraction**, and a controlled selectivity
validation plan — **not** a guaranteed working tracer.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** BindCraft, RFdiffusion binder mode, and AF2-Multimer at campaign scale want an
> **A100** (Colab Pro+ or a cluster) — and you run AF2-Multimer **twice per design** (fibril +
> monomer), so the per-design AF2 cost roughly **doubles**. A free **T4** runs only a *small fallback
> campaign* (FreeBindCraft, small `num_designs`, a small RFdiffusion batch + ESMFold triage). The
> notebooks run end-to-end on a deterministic **`mock`** backend with no GPU so you can build the
> plumbing anywhere; switch to the real backend on Colab Pro / A100. **Pin upstream commits and verify
> them** (the version-verify cell) — these tools change fast.

### BindCraft (or FreeBindCraft)
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes binder backbone **and** sequence together, pre-filtered on interface confidence. The primary
  paradigm in notebook 02. The target PDB is the cleaned **fibril protofilament** (not the monomer).
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**;
  replaces the PyRosetta dependency for free-tier use). *Verify both before the course starts.*
- **Key parameters that matter here:** `target_pdb` (cleaned fibril protofilament), `hotspot_residues`
  (the exposed fibril-surface set), `binder_length` range (≈50–90), `num_designs` (50–200 on A100; far
  fewer on T4), `design_models` / filter thresholds.
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  # On Colab Pro (A100) via the BindCraft notebook / CLI; pin the commit you used.
  python bindcraft.py --settings tau_phf_settings.json   # target=fibril surface, hotspots=exposed core, n=50-200
  ```

### RFdiffusion (binder mode) + ProteinMPNN
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a binder backbone docked against
  the fibril-surface hotspots; **ProteinMPNN** then designs a sequence for each backbone. The second
  paradigm in notebook 02 (generate 500–1000 backbones → MPNN).
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; the official binder protocol
  is exposed via ColabDesign `https://github.com/sokrypton/ColabDesign`. ProteinMPNN ships with
  RFdiffusion / ColabDesign. Pin commits; *verify before the course.*
- **Key parameters:** `contigs` / `hotspot_res` (the exposed fibril-surface residues), `binderlen`,
  diffusion `noise_scale`, `num_designs` (500–1000 backbones; small batch on T4); ProteinMPNN
  `temperature` (0.1–0.3) and `num_seq_per_target` (e.g., 8). The flat cross-β surface often needs a
  longer `binderlen` to span a groove.
- **Compute:** RFdiffusion small batches OK on T4; **500–1000 backbones want A100/HPC.** ProteinMPNN is
  CPU-cheap. AF2-Multimer re-prediction (×2 conformers) is the real bottleneck.
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs target the exposed fibril-surface hotspots.
  ./scripts/run_inference.py 'contigmap.contigs=[A1-73/0 60-90]' \
      'ppi.hotspot_res=[A306,A310,A315,A320]' inference.num_designs=1000 inference.output_prefix=out/tauphf
  # then ProteinMPNN over the backbones, then AF2-Multimer (fibril AND monomer).
  ```

### AF2-Multimer (ColabFold) — run PER CONFORMER
- **What it does / where it fits:** re-predicts each binder–target **complex** and yields the key metric
  `pae_interaction` (plus interface pLDDT). For this project you run it **twice per design** — once vs
  the **fibril** (the design target) and once vs the **monomer** (the counter-test) — and take the
  difference as the `specificity_gap`.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles` (raise for hard interfaces). Parse
  `pae_interaction` from the output (mean PAE on inter-chain residue pairs). For the **monomer** run,
  use a disordered/ensemble monomer model and report the modeling caveat.
- **Compute:** small complexes OK on T4; campaign-scale re-prediction (×2 conformers) prefers A100. This
  is usually the slowest step — batch overnight.

### Shared `filtering_pipeline.py` + Boltz-2 (stretch)
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. It ranks **fibril** binders;
  the conformational-selectivity test (notebook 04) is applied on top. Do **not** fork it — iterate
  against `shared/` and PR back.
- **Boltz-2** (stretch, notebook 05): predicted binding affinity on top hits — **scaffold only**; report
  *relative ranking* and caveats, **never fabricate a K_D or a selectivity ratio** (and it is even less
  reliable for a large repetitive fibril assembly).

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → fibril prep (clean protofilament) + fibril-surface epitope ID + monomer model + metrics table + mock hello-world (incl. monomer-vs-fibril gap preview)
02_generate         → two-paradigm campaign vs the fibril: BindCraft (50-200) + RFdiffusion-binder (500-1000 -> ProteinMPNN); AF2-Multimer; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per paradigm -> ranked CSV
04_validate         → THE HARD PART: conformational-specificity test (binder vs monomer vs fibril; specificity_gap) + BindCraft-vs-RFdiffusion head-to-head + cross-amyloid (tau vs alpha-syn) + figures
05_validation_plan  → fibril-vs-monomer ELISA/SPR plan, controls (conformational positive, scrambled-interface negative, monomer negative, unrelated), expression + matched monomer/fibril preps, diagnostic-tracer framing; Boltz-2 affinity stretch (scaffold)
```
For Project 11 the standard slots map to: *02 = the two-paradigm binder campaign vs the fibril* (the
core), *04 = the conformational-specificity test + head-to-head* (the hard part), *05 = the
fibril-vs-monomer validation plan*.

## 4. Filtering cutoffs for this design type
These are the shared `"binder"` cutoffs (`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`), applied to the
**fibril** interface. The conformational-selectivity margin is applied on top in notebook 04.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs AF2-predicted binder backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the binder (NOT stability) |
| **pae_interaction** (fibril) | **≤ 10 Å** | **interface confidence — the key binder metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality |
| **specificity_gap** | **≥ GAP_MIN (you justify; e.g. ~4 Å)** | **conformational selectivity — prefers fibril over monomer** |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail) |

> Reminder: **no in-silico metric perfectly separates true from false binders**, and **none proves
> conformational selectivity.** Filters enrich; they do not guarantee. `pae_interaction` is the best
> single binder predictor (confidence, not affinity); the `specificity_gap` is a model proxy, not a
> measured selectivity. Expect false positives and report them.

## 5. Interpreting results
- A *good* fibril-selective design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` (fibril) ≤ 10**,
  `rosetta_dG` ≤ −30 REU, `sc` ≥ 0.6, **AND a positive, sizeable `specificity_gap`** (poor monomer
  confidence) — and a footprint that covers the exposed fibril surface.
- A *suspicious* one: low `pae_interaction` on the fibril but **also** low on the monomer (gap ≈ 0 → not
  selective); or a great fibril interface with weak `rosetta_dG`; or coverage of the fibril surface but
  a cross-reactive monomer score.
- **Survival-at-each-layer plot:** read it as a funnel — steep drops show which layer discriminates. The
  **selectivity quadrant** (pae_fibril vs pae_monomer) is the project's signature plot: selective
  designs sit **upper-left** (low fibril PAE, high monomer PAE).
- **Hit rates to report:** the **fibril** hit rate (`N passing all layers / N generated`) AND the
  **selective** rate (`N also clearing GAP_MIN / N generated`), separately for BindCraft and
  RFdiffusion, with the layer-by-layer survival counts. Report the *distribution*, not just the best.
- **Head-to-head:** compare fibril hit rate, **selective fraction**, `rosetta_dG`, diversity, and
  novelty across the two paradigms; discuss their different failure modes honestly.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for a binder campaign (and ×2 conformers) | Use FreeBindCraft + small `num_designs`; small RFdiffusion batch + ESMFold triage; move full campaign to A100/HPC; batch the monomer runs separately |
| BindCraft/RFdiffusion install fails | upstream repo/commit changed; PyRosetta license | Use the pinned commit; try FreeBindCraft (no PyRosetta); log the path you used |
| All designs fail self-consistency | bad fibril prep, wrong protofilament/chains, wrong epitope | Re-clean the protofilament, confirm the ordered-core range, re-derive surface hotspots from the cryo-EM structure; lower MPNN temperature |
| **`specificity_gap` ≈ 0 for everything** | epitope not fibril-specific (also present/exposed in the monomer model), or the monomer model is wrong | Pick a fibril-surface patch that is **buried/absent** in the monomer; rebuild the monomer model (prefer an ensemble); re-run both conformers |
| **`specificity_gap` is negative** | binder prefers the disordered monomer | Reject; it is not conformation-selective — re-target a more clearly fibril-specific groove |
| Monomer model looks meaningless | the monomer is intrinsically disordered (no fixed fold) | Expected — use an **ensemble** or treat the monomer score as a soft signal; lean on the wet-lab fibril-vs-monomer assay for the real answer; state the caveat |
| `pae_interaction` good but `rosetta_dG` weak | confident placement, poor interface packing | Keep as a flagged case; tighten `sc`/`rosetta_dG`; prefer designs strong on both |
| Cross-reacts with the other amyloid (tau↔α-syn) | epitope shared/similar across amyloids | Add the cross-amyloid counter-test (nb 04); re-select a target-unique surface |
| RFdiffusion produces few foldable binders | flat cross-β surface; noise/contigs/length off | Sweep `noise_scale`, increase `binderlen` to span a groove, regenerate; a low per-backbone hit rate is **normal and lower here** |
| Hit/selective rate looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N (fibril AND selective), not the best |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** binders in *E. coli* BL21(DE3), 16–18 °C overnight (small, His-tagged). The **antigens**
  are recombinant tau / α-synuclein — prepare **both a monomer prep and an in-vitro fibril prep** from
  the same construct (seeded aggregation); confirm fibrils by **ThT** fluorescence + **TEM/cryo-EM**.
  This matched monomer↔fibril pair is what makes the selectivity readout clean.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF stability; **SPR/BLI** vs
  immobilized **fibril** for apparent K_D/kinetics) → **the selectivity test** (**fibril-vs-monomer
  ELISA/SPR**: signal on fibril must be ≫ signal on monomer; report the measured **selectivity ratio**)
  → cross-amyloid (same readout vs the other fibril) → deep (tissue staining / patient-derived fibril
  pulldown, under approval).
- **Controls (mandatory):**
  - **Positive:** a known **conformational anti-fibril antibody / validated amyloid tracer** → confirms
    the assay and the fibril prep are active and conformation-discriminating.
  - **Negative (scrambled-interface):** your **own** top design with its fibril-contacting residues
    scrambled/mutated → must **lose** fibril binding (cleanest specificity control).
  - **Negative (monomer):** the **monomer** of the same protein → a selective binder must **not** bind it.
  - **Unrelated-protein negative:** an unrelated mini-protein / an unrelated amyloid → should not bind.
- **Diagnostic-tracer note:** a clinical PET tracer additionally needs **BBB penetration**, radiolabeling
  chemistry, and pharmacokinetics — out of scope for this capstone but named as the translational path.

## 8. Responsible research
This project designs **conformation-selective** binders to **pathological amyloid aggregates** (tau /
α-synuclein fibrils) for **neurodegeneration diagnostics** (PET tracers, fibril assays) and
**aggregation modulation** — an in-scope diagnostic/therapeutic purpose under `MASTER_BLUEPRINT.md §7`,
with **low dual-use** risk (the target is a disease aggregate; the intent is to detect or modulate it).
In-scope purpose here: neurodegeneration diagnostics/therapeutics only. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, immune-evasion tools, or any design intended to cause harm. Any real
gene-synthesis order must go through a biosecurity-screening provider (IGSC member); wet-lab work —
including any **patient-derived material** — requires institutional biosafety/ethics approval. Students
must not overstate results or imply experimental validation that was not done — a design is a
hypothesis, and conformational selectivity is proven only by the fibril-vs-monomer assay.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Pacesa 2025
(BindCraft), Watson 2023 (RFdiffusion), Dauparas 2022 (ProteinMPNN), Evans 2021 (AF2-Multimer),
Fitzpatrick 2017 (tau PHF cryo-EM), a Schweighauser/α-syn fibril cryo-EM paper, and an amyloid-PET-tracer
/ conformational-antibody reference.
