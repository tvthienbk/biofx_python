# Project 10 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** NDM-1 (New Delhi metallo-β-lactamase) is a **class B metallo-β-lactamase**:
its active site holds **two catalytic Zn²⁺ ions** (Zn1 coordinated by three His; Zn2 by Asp/Cys/His)
bridged by a hydroxide. That hydroxide attacks the β-lactam carbonyl, opening the ring and
**hydrolyzing carbapenems** — our last-resort antibiotics. Unlike the serine β-lactamases (blocked by
clavulanate/avibactam), NDM-1 has **no clinical inhibitor**. We want a **small de novo binder**
(≈40–80 aa) that sits on the **active-site rim** — the walls of the substrate-access channel over the
di-zinc site — and **occludes** carbapenem access, **inhibiting** the enzyme and **restoring antibiotic
efficacy** (a β-lactam *adjuvant*). The binder is targeted at the rim residues read off the cleaned
di-zinc structure; **both Zn²⁺ ions are preserved** (they are part of the epitope), and the binder
sits on the rim — it does **not** replace the metal ligands.

**Key concepts a student must understand:**
- **Hotspots / occluding epitope:** the small set of **active-site-rim** residues the binder is
  steered to contact. Choosing them on the **substrate-access channel** is what makes the binder an
  *occluder/inhibitor*, not just a sticker. Distal hotspots (the rim-vs-distal ablation) give a binder
  that sticks but does **not** inhibit.
- **Preserve the di-zinc site:** AF2/RFdiffusion do not natively model Zn²⁺ — keep the two metals as
  target **heteroatoms** in prep, never strip them, and never design over the Zn-coordinating
  His/Cys/Asp residues. Sequence design near the metal uses **LigandMPNN** (Zn-aware), not vanilla
  ProteinMPNN.
- **Self-consistency (scRMSD):** design a backbone → design its sequence → predict that sequence →
  measure Cα-RMSD between designed and predicted. `< 2.5 Å` is the binder self-consistency bar.
- **`pae_interaction` (AF2-Multimer):** the **single most important binder metric** — the predicted
  aligned error *across the binder–target interface*. Low (`≤ 10 Å`) means AF2-Multimer is confident
  about the *relative* placement of binder and target. pLDDT alone does not tell you this.
- **Occlusion score (mechanism #1):** a structural proxy for *does the binder block substrate access?*
  — rim coverage + a pocket-fit / channel-volume term. A binder can have a great interface and still
  sit just off the groove and never inhibit. **Occlusion ≠ inhibition** (see below).
- **Off-target specificity (mechanism #2):** does the di-zinc binder cross-react with **human**
  metalloenzymes (carbonic anhydrase, MMPs, glyoxalase II)? Higher specificity = safer; this is the
  in-silico mirror of the off-target-metalloenzyme control in the assay.
- **Two paradigms:** *BindCraft* hallucinates a binder with AF2 in the loop (one-shot); *RFdiffusion
  binder mode* diffuses a backbone against the target, then **LigandMPNN** designs a (Zn-aware)
  sequence. Different inductive biases → different hit rates and folds.

**Why this is hard and what realistic success looks like.** In-silico binder hit rates **vary widely
by target and tool** — from single-digit to tens of percent passing the filter — and the **great
majority of in-silico hits fail experimentally**. And the central caveat of *this* project:
**binding is not inhibition.** A binder that passes every layer and scores high on occlusion is a
*hypothesis*: a low `pae_interaction` is **not** a measured affinity, occlusion is a structural
proxy, and **an enzyme-kinetics IC50 assay is mandatory**. Success for this capstone = a rigorous,
honestly-reported campaign with occlusion + specificity analysis, a clear hit-rate accounting, and a
controlled inhibition-assay plan — **not** a guaranteed working inhibitor. **No IC50 is produced
in-silico anywhere in this project; that would be fabricated.**

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** BindCraft, RFdiffusion binder mode, LigandMPNN, and AF2-Multimer at campaign
> scale want an **A100** (Colab Pro+ or a cluster). A free **T4** runs only a *small fallback campaign*
> (FreeBindCraft, small `num_designs`, a small RFdiffusion batch + ESMFold triage). The notebooks run
> end-to-end on a deterministic **`mock`** backend with no GPU so you can build the plumbing anywhere;
> switch to the real backend on Colab Pro / A100. **Pin upstream commits and verify them** (the
> version-verify cell) — these tools change fast.

### BindCraft (or FreeBindCraft)
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes binder backbone **and** sequence together, pre-filtered on interface confidence. The
  primary paradigm in notebook 02.
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**;
  replaces the PyRosetta dependency for free-tier use). *Verify both before the course starts.*
- **Key parameters that matter here:** `target_pdb` (cleaned NDM-1 with **both Zn²⁺ kept as
  heteroatoms**), `hotspot_residues` (the **active-site-rim** set), `binder_length` range (≈40–80),
  `num_designs` (50–200 on A100; far fewer on T4).
- **Di-zinc note:** AF2/BindCraft do not place Zn²⁺ — keep the metals as heteroatoms and **confirm the
  binder docks onto the substrate-access rim**, not a distal patch.
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  # On Colab Pro (A100) via the BindCraft notebook / CLI; pin the commit you used.
  python bindcraft.py --settings ndm1_settings.json   # target=NDM-1 (Zn kept), hotspots=active-site rim, n=50-200
  ```

### RFdiffusion (binder mode) + LigandMPNN (Zn-aware)
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a binder backbone docked
  against the rim hotspots; **LigandMPNN** then designs a sequence **aware of the di-zinc ligand
  context** (Dauparas 2024) — this is the key swap vs the PD-L1 template (which used vanilla
  ProteinMPNN). The second paradigm in notebook 02 (generate 500–1000 backbones → LigandMPNN).
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; **LigandMPNN**
  `https://github.com/dauparas/LigandMPNN`; the binder protocol is exposed via ColabDesign
  `https://github.com/sokrypton/ColabDesign`. Pin commits; *verify before the course.*
- **Key parameters:** `contigs` / `ppi.hotspot_res` (the **active-site-rim** residues), `binderlen`,
  diffusion `noise_scale`, `num_designs` (500–1000 backbones); LigandMPNN `temperature` (0.1–0.3),
  `num_seq_per_target`, and the **Zn²⁺ ligand context passed in** so interface residues near the metal
  are designed metal-aware.
- **Compute:** RFdiffusion small batches OK on T4; **500–1000 backbones want A100/HPC.** LigandMPNN is
  CPU-cheap. AF2-Multimer re-prediction of each design is the real bottleneck.
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs target the active-site-rim hotspots; Zn kept in target.
  ./scripts/run_inference.py 'contigmap.contigs=[A1-270/0 60-80]' \
      'ppi.hotspot_res=[A120,A220,A228]' inference.num_designs=1000 inference.output_prefix=out/ndm1
  # then LigandMPNN over the backbones (passing the Zn ions), then AF2-Multimer.
  ```

### AF2-Multimer (ColabFold)
- **What it does / where it fits:** re-predicts each binder–NDM-1 **complex** and yields the key
  metric `pae_interaction` (plus interface pLDDT). The orthogonal/self-consistency check for binders.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles` (raise for hard interfaces), pairing/MSA
  mode. Parse `pae_interaction` from the output. **Note:** AF2 does not place Zn²⁺ — keep the metal as
  a target heteroatom and sanity-check that the predicted binder sits over the substrate-access rim.
- **Compute:** small complexes OK on T4; campaign-scale prefers A100. This is usually the slowest step
  — batch overnight.

### Mechanism helpers (`scripts/binder_tools.py`) + shared filter + stretch
- **`occlusion_score(binder, active_site)`** (notebook 04): structural proxy for substrate-access
  occlusion (rim coverage + pocket-fit; on Colab: pocket-volume/SASA with-vs-without binder, optional
  carbapenem docking). **Occlusion ≠ inhibition.**
- **`offtarget_specificity(binder, human_metalloenzyme)`** (notebook 04): off-target AF2-Multimer
  panel vs human metalloenzymes (CA2/MMP/GLO2); higher = more NDM-1-selective.
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`. Do **not** fork it — iterate
  against `shared/` and PR back.
- **β-lactam adjuvant / Boltz-2** (stretch, notebook 05): adjuvant-checkerboard concept; predicted
  affinity on top hits — **scaffold only**; relative ranking + caveats, **never a fabricated K_D or
  IC50**.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → di-zinc target prep (Zn preserved) + active-site-rim hotspot ID + binder/occlusion metrics + mock hello-world
02_generate         → two-paradigm campaign: BindCraft (50-200) + RFdiffusion-binder (500-1000 -> LigandMPNN); AF2-Multimer; results CSVs (mock here; real calls + A100 note + version-verify shown)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder") + fp.report; survival per paradigm -> ranked CSV
04_validate         → occlusion modeling + specificity vs human metalloenzymes + BindCraft-vs-RFdiffusion benchmark + rim-vs-distal ablation + figures
05_validation_plan  → nitrocefin/carbapenem INHIBITION assay (IC50), controls (off-target metalloenzyme, scrambled-interface negative, enzyme-only), expression strategy; beta-lactam-adjuvant stretch (scaffold)
```
For Project 10 the standard slots map to: *02 = the two-paradigm binder campaign* (the core), *04 =
the occlusion + specificity analysis and head-to-head*, *05 = the nitrocefin/carbapenem inhibition
(IC50) validation plan*.

## 4. Filtering cutoffs for this design type
These are the shared `"binder"` cutoffs (`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`), **plus** the
project-specific occlusion/specificity thresholds (applied in notebook 04, not in the shared module).
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs AF2-predicted binder backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the binder (NOT stability) |
| **pae_interaction** | **≤ 10 Å** | **interface confidence — the key binder metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality |
| **occlusion** | **≥ 0.5** (project) | does the binder block the substrate-access channel? (mechanism, not inhibition) |
| **specificity vs human metalloenzymes** | **≥ 0.5** (project) | low predicted off-target binding (safety) |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail) |

> Reminder: **no in-silico metric perfectly separates true inhibitors from non-inhibitors.** Filters
> and the occlusion score *enrich*; they do not guarantee. `pae_interaction` is the best single binder
> predictor, but a low value is *confidence*, not *affinity* — and **binding ≠ inhibition**. Only the
> nitrocefin/carbapenem kinetics assay (IC50) measures inhibition.

## 5. Interpreting results
- A *good* inhibitor-candidate design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10**,
  `rosetta_dG` ≤ −30 REU, `sc` ≥ 0.6, **`occlusion` ≥ 0.5** (covers the substrate-access rim), and
  **high specificity** (low predicted off-target binding to human metalloenzymes).
- A *suspicious* one: low `pae_interaction` but **low occlusion** (binds off the substrate groove —
  a sticker, not a blocker), or high occlusion but **low specificity** (likely hits human Zn-enzymes
  too — a safety problem), or a great interface that misses the rim entirely.
- **Survival-at-each-layer plot:** read it as a funnel — steep drops show which layer discriminates.
  Report it **per paradigm** so the head-to-head is fair.
- **Hit rate:** report `N passing all layers / N generated`, separately for BindCraft and RFdiffusion,
  with the layer-by-layer survival counts, **and** how many survivors also clear the occlusion +
  specificity thresholds. Report the *distribution*, not just the best.
- **Rim-vs-distal ablation:** distal-patch binders should bind (good `pae_interaction`) but **not**
  occlude (low `occlusion`) — the cleanest demonstration that epitope choice drives inhibition.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for a binder campaign | Use FreeBindCraft + small `num_designs`; small RFdiffusion batch + ESMFold triage; move full campaign to A100/HPC |
| BindCraft install fails | upstream repo/commit changed; PyRosetta license | Use the pinned commit; try FreeBindCraft (no PyRosetta); log the path you used |
| **Zn²⁺ ions missing from the target** | prep stripped heteroatoms | Re-prep keeping both Zn as heteroatoms; they are part of the epitope — never strip them |
| Binder docks **away from the active-site rim** | hotspots not on the substrate channel | Re-derive rim hotspots from the cleaned di-zinc structure; add the occlusion check (nb 04) |
| Good `pae_interaction` but **low occlusion** | binder sticks off the groove — a sticker | Keep as a flagged case; it is unlikely to inhibit; prefer high-occlusion survivors |
| High occlusion but **low specificity** | cross-reacts with human metalloenzymes | Counter-test against the human panel (nb 04); deprioritize; it is a safety liability |
| LigandMPNN ignores the metal context | Zn ligand not passed to LigandMPNN | Pass the Zn ions/ligand context to LigandMPNN so interface residues near the metal are metal-aware |
| Hit rate looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N, not the best |
| Tempted to report an IC50 from a model | confusing binding/occlusion with inhibition | **Never** — there is no in-silico IC50 here; IC50 comes only from the nb-05 kinetics assay |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** binders in *E. coli* BL21(DE3), 16–18 °C overnight (small, His-tagged); **NDM-1** is
  expressed (often the soluble periplasmic/Δ-membrane-anchor construct) and purified with Zn²⁺ in the
  buffer to keep the di-zinc site intact; confirm activity on nitrocefin before testing binders.
- **The assay is an INHIBITION assay (this is the point):**
  1. Go/no-go: express → SDS-PAGE → SEC (monodisperse binder?).
  2. **Inhibition kinetics — nitrocefin** (chromogenic cephalosporin, Δλ on hydrolysis) or a
     **carbapenem-hydrolysis** readout (e.g. imipenem/meropenem absorbance drop): pre-incubate NDM-1
     with a binder dilution series → measure residual hydrolysis rate → fit **IC50** (and ideally
     **K_i** + mode of inhibition: competitive / non-competitive).
  3. Stability: DSF (Tm). Deep (optional): co-crystal / cryo-EM of the binder–NDM-1 complex.
- **Controls (mandatory):**
  - **Off-target human-metalloenzyme control:** run the same inhibition assay against a human Zn/
    metalloenzyme (e.g. carbonic anhydrase) — the binder must **NOT** inhibit it (specificity/safety).
  - **Negative (scrambled-interface):** take your **own** top design and scramble/mutate the interface
    residues — it must **lose** inhibition (cleanest specificity control).
  - **Enzyme-only / no-inhibitor positive control:** NDM-1 + substrate with no binder defines 100%
    activity; a known metallo-β-lactamase chelator (e.g. EDTA/captopril analogue) confirms the assay.
- **β-lactam-adjuvant stretch:** a **checkerboard** of binder × carbapenem (e.g. meropenem) in a
  resistant strain — does the binder **restore** the antibiotic's MIC? This is the therapeutic readout.

## 8. Responsible research
This is a **defensive anti-AMR** project. Its purpose is to **inhibit** a resistance enzyme (NDM-1)
so that a **last-resort antibiotic works again** — an in-scope therapeutic/diagnostic purpose under
`MASTER_BLUEPRINT.md §7` ("AMR enzymes (to *inhibit*)"). The binder is an **inhibitor / β-lactam
adjuvant** that *restores* antibiotic efficacy. It is **explicitly out of scope** to enhance
antimicrobial **resistance**, improve **pathogen fitness/virulence/transmissibility**, protect or
stabilize the enzyme, or otherwise make the pathogen harder to treat — refuse and redirect any
proposal in that direction. Also out of scope: toxins, immune-evasion tools, or any design intended to
cause harm. Any real gene-synthesis order must go through a biosecurity-screening provider (IGSC
member), and wet-lab work requires institutional biosafety/ethics approval. Students must not overstate
results or imply experimental validation that was not done — a design is a hypothesis, and **binding is
not inhibition** until the IC50 assay says so.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: an NDM-1 /
metallo-β-lactamase structure paper, a metallo-β-lactamase-inhibitor review, Pacesa 2025 (BindCraft),
Dauparas 2024 (LigandMPNN), Watson 2023 (RFdiffusion), Evans 2021 (AF2-Multimer), and a nitrocefin/
β-lactamase-kinetics methods reference.
