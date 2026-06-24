# Project 13 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** Cytokines signal by **clustering their receptor chains**. IL-2 is the model:
its receptor has three chains — **IL-2Rα (CD25)**, **IL-2Rβ (CD122)**, and **γc (CD132)**. α is a
high-affinity *capture* chain that does **not** signal; the signaling competent complex is the
**IL-2Rβ + γc** heterodimer, which juxtaposes the receptor-associated JAK1/JAK3 kinases, triggering
**STAT5** phosphorylation. Which cells respond depends on which subunits they express: CD25-high
regulatory T cells (Tregs) are exquisitely IL-2-sensitive via the trimeric αβγ receptor, whereas
effector/memory T and NK cells respond through the dimeric βγ receptor. Native IL-2's promiscuous α
engagement (plus a short half-life and instability) is what makes it toxic and pleiotropic.

A **de novo cytokine mimetic** sidesteps this: design a small, hyperstable protein that engages a
**chosen** subunit combination. **Neo-2/15** (Silva et al. 2019) is the landmark — a ~100-residue de
novo four-helix mini-protein that binds **IL-2Rβ and γc** (so it signals through the dimeric receptor)
but has **no IL-2Rα site at all**, so it is a **βγ-biased agonist**: it activates effector T/NK cells
while sparing CD25-high Tregs, and it is far more stable than IL-2. This project reproduces that *kind*
of design decision computationally: choose the subunits, steer a de novo mini-protein onto their
surfaces, and **prove selectivity in silico** by modeling against each subunit separately.

**Key concepts a student must understand:**
- **Receptor subunits & what they do:** α = high-affinity capture (no signaling), **β + γc = the
  signaling pair**. Engaging βγ *without* α is the Neo-2/15 selectivity that spares Tregs and reduces
  toxicity. Decide which subunits you engage and which you spare, and **write it down**.
- **Agonism = receptor dimerization, not just binding.** The mimetic must bridge β and γc with the
  right geometry so JAK1/JAK3 are juxtaposed and STAT5 fires. **Binding is necessary but not
  sufficient** — a mini-protein can bind β and γc and still not signal. Only a **cell pSTAT5 assay**
  decides agonism.
- **Self-consistency (scRMSD):** design a backbone → design its sequence → predict that sequence →
  Cα-RMSD between designed and predicted. `< 2.5 Å` is the binder self-consistency bar.
- **`pae_interaction` per subunit (AF2-Multimer):** the **key metric**, computed **once per receptor
  subunit**. Low to β and γc (`≤ 10 Å`) = AF2-Multimer is confident the mimetic sits on the signaling
  chains; **high to α** = it does *not* engage the capture chain. The *vector* `(pae_to_α, pae_to_β,
  pae_to_γ)` is the **selectivity profile** — the deliverable that distinguishes this project.
- **Selectivity margin:** a single number summarizing the profile, e.g.
  `margin = pae_to_alpha − max(pae_to_beta, pae_to_gamma)`. Large positive ⇒ engages βγ, spares α.
- **Interface energy (`rosetta_dG`, REU) + shape complementarity (`sc`):** the physics layer — is each
  engaged interface actually favorable and well-packed.
- **Stability vs the native cytokine:** the Neo-2/15 selling point. De novo mimetics can be **far more
  thermostable** than IL-2; report a stability comparison (proxy in silico, DSF Tm in the wet-lab plan).

**Why this is hard and what realistic success looks like.** De novo **agonist** design with **clean
subunit selectivity is harder than a plain binder**: you need a favorable interface to *two* chosen
chains, the right dimerizing geometry, *and* the absence of a fourth (α) site. In-silico hit rates vary
widely by target and tool, and the **great majority of in-silico hits fail experimentally** — and here
even an experimental *binder* may fail to *signal*. A mimetic that passes every layer is a *hypothesis*:
a low `pae_interaction` is not affinity, and binding is not signaling. **SPR per subunit + a cell pSTAT5
assay are mandatory.** Success for this capstone = a rigorous, honestly-reported campaign with a clear
**selectivity profile**, a stability comparison, and a controlled signaling-validation plan — **not** a
guaranteed working agonist. **Never fabricate an EC50, K_D, or pSTAT response.**

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

> **Compute honesty:** RFdiffusion binder mode, BindCraft, and AF2-Multimer at campaign scale want an
> **A100** (Colab Pro+ or a cluster) — and modeling against **three** subunits roughly **triples** the
> AF2-Multimer cost. A free **T4** runs only a *small fallback campaign* (a small RFdiffusion batch +
> ESMFold triage, or FreeBindCraft with small `num_designs`). The notebooks run end-to-end on a
> deterministic **`mock`** backend with no GPU so you can build the plumbing anywhere; switch to the
> real backend on Colab Pro / A100. **Pin upstream commits and verify them** (the version-verify cell).

### RFdiffusion (binder mode) + ProteinMPNN
- **What it does / where it fits:** RFdiffusion *binder mode* diffuses a mini-protein backbone docked
  against the chosen receptor-subunit surfaces (the IL-2Rβ/γc hotspots); **ProteinMPNN** then designs a
  sequence for each backbone. The primary paradigm in notebook 02 (generate 500–1000 backbones → MPNN).
  A four-helix-bundle-like topology that can bridge β and γc is what you are steering toward.
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; the official binder protocol
  is exposed via ColabDesign `https://github.com/sokrypton/ColabDesign`. ProteinMPNN ships with
  RFdiffusion / ColabDesign. Pin commits; *verify before the course.*
- **Key parameters:** `contigs` / `hotspot_res` (the IL-2Rβ/γc residues; supply a multi-chain target so
  the binder can bridge both chains), `binderlen` (≈50–90), diffusion `noise_scale`, `num_designs`
  (500–1000 backbones; small batch on T4); ProteinMPNN `temperature` (0.1–0.3), `num_seq_per_target`.
- **Compute:** small batches OK on T4; **500–1000 backbones want A100/HPC.** ProteinMPNN is CPU-cheap.
  AF2-Multimer re-prediction (×3 subunits) is the real bottleneck.
- **Typical call:**
  ```bash
  # RFdiffusion binder mode (pin commit); contigs/hotspots target the IL-2Rβ/γc signaling surfaces.
  # Supply BOTH receptor chains so the mini-protein can bridge them (agonist geometry).
  ./scripts/run_inference.py 'contigmap.contigs=[B1-200/0 C1-180/0 60-90]' \
      'ppi.hotspot_res=[B41,B42,C100,C102]' inference.num_designs=1000 inference.output_prefix=out/il2mimetic
  # then ProteinMPNN over the backbones, then AF2-Multimer against EACH subunit.
  ```

### BindCraft (or FreeBindCraft)
- **What it does / where it fits:** one-shot binder *hallucination* with AF2-Multimer in the loop —
  proposes a mini-protein backbone **and** sequence together, pre-filtered on interface confidence. An
  alternative/second paradigm in notebook 02; useful as a foil to RFdiffusion.
- **Install:** upstream `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback
  **FreeBindCraft** `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**;
  replaces the PyRosetta dependency for free-tier use). *Verify both before the course starts.*
- **Key parameters:** `target_pdb` (the receptor surface), `hotspot_residues` (the β/γc set),
  `binder_length` (≈50–90), `num_designs` (50–200 on A100; fewer on T4).
- **Compute:** **A100 strongly recommended.** Free T4 → FreeBindCraft, small `num_designs` only.
- **Typical call:**
  ```bash
  python bindcraft.py --settings il2_betagamma_settings.json   # target=IL-2Rβ/γc, hotspots=signaling face
  ```

### AF2-Multimer (ColabFold) — run **per subunit** (this is the selectivity step)
- **What it does / where it fits:** re-predicts each (mimetic, receptor-subunit) **complex** and yields
  `pae_interaction` (plus interface pLDDT). **Run it three times per design** — against IL-2Rα, IL-2Rβ,
  and γc separately — to build the **selectivity profile**. This is the orthogonal/self-consistency
  check *and* the selectivity measurement.
- **Install:** ColabFold `https://github.com/sokrypton/ColabFold` (AF2-Multimer mode); pin the commit.
- **Key parameters:** `model_type=multimer`, `num_recycles` (raise for hard interfaces), pairing/MSA
  mode. Parse `pae_interaction` (mean PAE on inter-chain residue pairs) **for each subunit**.
- **Compute:** small complexes OK on T4; campaign-scale ×3-subunits prefers A100. The slowest step —
  batch overnight; consider ESMFold for a cheap first-pass triage on the engaged subunits only.

### Shared `filtering_pipeline.py` + Boltz-2 (stretch)
- **`filtering_pipeline.py`** (notebook 03): the cohort's 4-layer filter; call
  `fp.run_pipeline(designs, design_type="binder")` then `fp.report(...)`, filtering on the **engaged**
  subunits' metrics. Do **not** fork it — iterate against `shared/` and PR back. The **selectivity**
  logic lives in `scripts/cytokine_tools.py` (`subunit_selectivity`, `selectivity_profile`), layered on
  top of the shared filter.
- **Boltz-2** (stretch, notebook 05): predicted affinity on top hits **per subunit** — **scaffold
  only**; report *relative ranking* and caveats, **never fabricate a K_D/EC50**.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → cytokine-signaling + de novo mimetic theory; pick target subunits + desired selectivity;
                      separate the receptor subunits; per-subunit hotspots; metrics table; mock hello-world (D0)
02_generate         → agonist campaign: RFdiffusion-binder (500-1000 -> ProteinMPNN) and/or BindCraft (50-200) at the
                      chosen surfaces; AF2-Multimer vs EACH subunit; results CSV (mock; real calls + A100 note + version-verify)
03_filter_and_rank  → import filtering_pipeline as fp; build fp.Design binders; fp.run_pipeline(design_type="binder")
                      + fp.report; filter on engaged subunits; survival -> ranked CSV (D3 pt1)
04_validate         → SUBUNIT-SELECTIVITY modeling (engages βγ but NOT α) + selectivity-margin + stability-vs-native
                      figures (D3 pt2)
05_validation_plan  → per-subunit SPR + cell STAT-phosphorylation assay plan, controls, expression; thermostability +
                      Boltz-2 affinity stretch (scaffold)
```
For Project 13 the standard slots map to: *02 = the agonist campaign* (the core), *04 = the
subunit-selectivity + stability analysis*, *05 = the per-subunit SPR + STAT-signaling validation plan*.

## 4. Filtering cutoffs for this design type
These are the shared `"binder"` cutoffs (`filtering_pipeline.DEFAULT_CUTOFFS["binder"]`), applied to the
**engaged** subunits (β, γc). The **selectivity** thresholds are project-specific (notebook 04).
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.5 Å | self-consistency (designed vs AF2-predicted mini-protein backbone) |
| pLDDT | ≥ 80 (mean) | local confidence of the mimetic (NOT stability) |
| **pae_interaction (to β and to γc)** | **≤ 10 Å** | **interface confidence to each engaged signaling chain — the key metric** |
| rosetta_dG | ≤ −30 REU | interface energy (favorable, well-packed) |
| shape complementarity (sc) | ≥ 0.6 | interface packing quality |
| TM-score to PDB | < 0.5 = novel | novelty (reported, not a pass/fail) |
| **selectivity margin** | **`pae_to_α − max(pae_to_β, pae_to_γ)` ≥ ~4 Å** (project-specific) | engages βγ, **spares α** (the Neo-2/15 selectivity) |

> Reminder: **no in-silico metric perfectly separates true from false agonists**, and **none predicts
> signaling**. Filters enrich; they do not guarantee. A low `pae_interaction` is *confidence*, not
> *affinity*; a selective binder is *not yet* a confirmed agonist. Report false positives.

## 5. Interpreting results
- A *good* mimetic design: scRMSD ≤ 2.5 Å, mean pLDDT ≥ 80, **`pae_interaction` ≤ 10 to both β and
  γc**, `pae_interaction` **high to α** (selectivity margin large), `rosetta_dG` ≤ −30 REU, `sc` ≥ 0.6,
  and a geometry that plausibly bridges β and γc (agonist dimerization).
- A *suspicious* one: low `pae` to all three subunits (engages α too — **not** selective; behaves like
  toxic native IL-2); or low `pae` to β/γc but a poor `rosetta_dG` (confident placement, weak
  interface); or a great interface that doesn't bridge **both** signaling chains (binds but may not
  dimerize → may not signal).
- **Survival-at-each-layer plot:** read it as a funnel; steep drops show which layer discriminates.
- **Selectivity profile:** plot `(pae_to_α, pae_to_β, pae_to_γ)` per design; the selective agonists are
  the corner with **low β, low γc, high α**. Report the **count** of selective survivors, not just the
  best.
- **Hit rate:** report `N passing all layers / N generated`, **and** `N also selective / N passing` —
  two numbers, both honest. Report the *distribution*, not just the best.
- **Stability vs native:** report your stability proxy (and DSF Tm in the wet-lab plan) against IL-2 —
  the de novo mimetic should be the more stable molecule (Neo-2/15 is dramatically so).

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for the campaign (×3-subunit AF2) | Small RFdiffusion batch + ESMFold triage on engaged subunits; FreeBindCraft + small `num_designs`; move full campaign to A100/HPC |
| AF2-Multimer step is 3× slower than expected | you are (correctly) modeling vs 3 subunits | Triage on β/γc first; only model α for designs that already pass on β/γc; batch overnight |
| Designs bind **all three** subunits (no selectivity) | hotspots not specific to the signaling face; α site emerged by chance | Re-pick hotspots strictly on β/γc; penalize α engagement in ranking; raise the selectivity-margin threshold |
| Low `pae` to β but not γc (or vice versa) | binder engages one chain, can't bridge both | Supply **both** receptor chains as the target; steer hotspots on both; expect to dimerize, not mono-bind |
| All designs fail self-consistency | bad target prep, wrong chain, wrong hotspots | Re-clean the receptor, confirm chains, re-derive hotspots from the IL-2/IL-2R interface; lower MPNN temperature |
| `pae_interaction` good but `rosetta_dG` weak | confident placement, poor interface packing | Keep as flagged; tighten `sc`/`rosetta_dG`; prefer designs strong on both |
| "It binds, so it's an agonist" | binding ≠ signaling | **Never** claim agonism from a model; the cell **pSTAT5** assay decides it (notebook 05) |
| Hit rate / selectivity looks "too good" | mock numbers, or cherry-picking | Confirm you are on a real backend (not `mock`); report the full distribution + N, not the best |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** the mimetic in *E. coli* BL21(DE3), 16–18 °C overnight (small, His-tagged) — de novo
  mini-proteins typically express well and are very stable. The **receptor-subunit ectodomain reagents**
  (IL-2Rα, IL-2Rβ, γc) are typically expressed in mammalian/insect cells or bought commercially.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (**DSF Tm**, compared to native
  IL-2; **per-subunit SPR/BLI** for K_D/kinetics to IL-2Rα, IL-2Rβ, and γc *separately* — this confirms
  the **selectivity** in vitro) → **functional (the decisive tier): a cell-based STAT-phosphorylation
  (pSTAT5) assay** on IL-2-responsive cells (e.g., CTLL-2, or primary T/NK), dose–response for an EC50,
  ideally on **CD25⁺ vs CD25⁻** cells to confirm α-independence → deep (co-crystal/cryo-EM of the
  mimetic–receptor complex; in-vivo Treg-vs-effector expansion).
- **Controls (mandatory):**
  - **Positive:** **native IL-2** (and/or **Neo-2/15** as a reference de novo agonist) — confirms the
    SPR reagents and the pSTAT5 assay/cells are responsive.
  - **Negative (scrambled-interface):** take your **own** top design and scramble/mutate the β/γc
    interface residues — it must **lose** binding and signaling. The cleanest specificity control.
  - **Unrelated-protein negative:** an unrelated mini-protein of similar size that should not bind or
    signal.
- **Binding ≠ signaling (state this in the plan):** SPR confirms it *binds the right subunits* with the
  *right selectivity*; only **pSTAT5** confirms it *signals (is an agonist)*. Both are required; report
  the EC50 from the assay, never a number you didn't measure.

## 8. Responsible research
This project designs a **receptor-selective agonist mini-protein** mimicking a human cytokine for
**cancer immunotherapy / immune modulation** — an in-scope therapeutic purpose under
`MASTER_BLUEPRINT.md §7`. In-scope purpose here: a **tuned-selectivity agonist whose explicit goal is to
*reduce* the toxicity of the natural cytokine** (a βγ-biased IL-2 mimetic spares CD25-high Tregs and the
vascular-leak toxicity of high-affinity α engagement). Because the design intent is *safer* than the
molecule it mimics, the **dual-use risk is low**. Out of scope: any design intended to *over-activate*
the immune system to cause harm, to enhance pathogen fitness, toxins, or immune-evasion tools. Any real
gene-synthesis order must go through a biosecurity-screening provider (IGSC member), and wet-lab work
(including cell-based immune assays) requires institutional biosafety/ethics approval. Students must not
overstate results or imply experimental validation that was not done — a design is a hypothesis, and
**binding is not signaling**.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Silva 2019
(Neo-2/15), Watson 2023 (RFdiffusion), Pacesa 2025 (BindCraft), Dauparas 2022 (ProteinMPNN), Evans 2021
(AF2-Multimer), plus an IL-2/IL-2R structural-biology paper and a JAK/STAT cytokine-signaling review.
