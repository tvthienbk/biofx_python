# PROJECT CATALOG — 25 De Novo Protein Design Capstones

Each entry is a complete specification. Claude Code generates a project folder from **this entry + the templates + `MASTER_BLUEPRINT.md`**. The 6-month structure (phases P0–P5, deliverables D0–D5) and the rubric are shared (see blueprint); below, each project supplies the *project-specific* problem, tools, data, and task breakdown.

**Task tags:** `[core]` (all students) · `[extension]` (most students) · `[stretch]` (strong students / MSc track).
**PDB/accession note:** all accessions are *candidates* — students verify on RCSB/UniProt at project start (structures get superseded).

---

## TIER A — Foundations & Reusable Tooling

### Project 01 — AF2/ESMFold/Boltz Validation Harness & Confidence Calibration
**Skill refs:** validation-ref, sequence-design-ref · **Compute:** free Colab T4.
**Real problem (why now):** Every design pipeline lives or dies by its in-silico filter, yet pLDDT/PAE/scRMSD are routinely misread (e.g., reporting pLDDT as "stability"). Before designing anything, a lab needs a *calibrated, reproducible* validation harness and to know which metric actually predicts experimental success.
**Objectives:** (1) Run and interpret AF2/ColabFold, ESMFold, and Boltz-2; (2) compute scRMSD, pLDDT, PAE, TM-score/novelty; (3) calibrate metrics against *known* experimental outcomes; (4) deliver a reusable validation module the whole cohort uses.
**Tools:** ColabFold (AF2), ESMFold, Boltz-2, Foldseek/TM-align, Biopython, py3Dmol.
**Data:** A curated set of designed proteins with *known* experimental outcomes assembled from published de novo design papers' supplementary data (sequences + whether they folded/bound). Plus 5–10 natural proteins as positive references. Document provenance per item.
**6-month tasks:**
- P0: Read AF2, ProteinMPNN (self-consistency concept), Boltz-2 papers; write metric definitions in your own words. `[core]`
- P1: Build `00_setup` + a prediction wrapper that runs AF2/ESMFold/Boltz on any sequence and parses confidence. `[core]`
- P2: Curate the labeled dataset (≥40 designs, ≥10 natural refs); predict all. `[core]` Add MSA-depth ablation for AF2. `[extension]`
- P3: Compute scRMSD/pLDDT/PAE/TM-score; build ROC/PR curves of each metric vs experimental outcome; find best single + composite predictor. `[core]` Per-design-type calibration. `[extension]`
- P4: Write the "Validation SOP" (recommended cutoffs by design type) and harden into `filtering_pipeline.py`'s self-consistency + orthogonal layers. `[core]` Add Boltz-2 affinity vs measured KD analysis. `[stretch]`
- P5: Thesis + the SOP becomes shared cohort infrastructure.
**Project-specific deliverable:** a validated, documented **validation module** + an SOP card with calibrated cutoffs.
**Benchmark/ablation:** AF2 vs ESMFold vs Boltz agreement; MSA depth; composite vs single metric.
**Key refs:** Jumper 2021 (AF2); Dauparas 2022 (ProteinMPNN/self-consistency); Wohlwend 2025 (Boltz-2); Lin 2023 (ESMFold).

---

### Project 02 — ProteinMPNN Optimization & Expression-Success Prediction
**Skill refs:** sequence-design-ref · **Compute:** free Colab T4.
**Real problem:** ProteinMPNN sits in nearly every pipeline, but temperature, backbone noise, and sequence count strongly affect whether designs express solubly. Labs waste synthesis budget on poorly chosen settings. What settings maximize foldability *and* expressibility?
**Objectives:** (1) Master ProteinMPNN/LigandMPNN parameters; (2) quantify the diversity↔recovery↔foldability trade-off; (3) connect sequence properties (CamSol/SAP, charge, hydrophobic patches) to predicted expression; (4) produce a settings-recommendation tool.
**Tools:** ProteinMPNN, LigandMPNN, ColabFold/ESMFold (recapitulation), CamSol/SAP or netsurfp-style solubility proxies, Biopython.
**Data:** 20–30 de novo backbones (from Project 03 outputs or public design sets) + natural backbones as references.
**6-month tasks:**
- P0–P1: Reproduce the ProteinMPNN tutorial; set up the recapitulation loop (sequence → AF2/ESMFold → scRMSD). `[core]`
- P2: Systematic sweep — temperature {0.1–0.5}, backbone noise {0–0.2}, seqs/backbone {8,16,48}; ≥hundreds of sequences. `[core]`
- P3: Quantify sequence recovery, AF2 recapitulation, diversity (entropy), and solubility proxies vs settings; identify Pareto-optimal settings. `[core]` Consensus-design vs single-sequence comparison. `[extension]`
- P4: Build a lightweight model/heuristic predicting "likely expresses" from in-silico features; write codon-optimization + tag-strategy guidance. `[extension]` MPNNsol surface-redesign comparison. `[stretch]`
- P5: Thesis + a "MPNN settings cheat-sheet" deliverable.
**Benchmark/ablation:** temperature × noise grid; ProteinMPNN vs ESM-IF vs FAMPNN (if available).
**Key refs:** Dauparas 2022, 2024 (LigandMPNN); Sumida 2024 (MPNN for expression/stability).

---

### Project 03 — RFdiffusion Monomer Design: The Novelty–Foldability Frontier
**Skill refs:** backbone-design-ref · **Compute:** Colab T4 (small) / A100 (full campaign).
**Real problem:** Generative models can make "novel" folds, but novelty trades off against foldability and increases experimental risk. Where is the frontier — how novel can a backbone be (low TM-score to PDB) while still self-consistently folding?
**Objectives:** (1) Run RFdiffusion unconditional + topology-constrained generation; (2) pair with ProteinMPNN + AF2 self-consistency; (3) quantify novelty (Foldseek/TM-score to PDB) vs foldability; (4) map the Pareto frontier across length/topology.
**Tools:** RFdiffusion (ColabDesign notebook), ProteinMPNN, ColabFold/ESMFold, Foldseek, py3Dmol/PyMOL.
**Data:** none external for generation; PDB/Foldseek database for novelty scoring.
**6-month tasks:**
- P0–P1: Reproduce monomer-design tutorial; generate 10, filter, visualize. `[core]`
- P2: Generate across lengths {80,120,200,300} and secondary-structure biases (all-α, all-β, mixed); 100s of backbones. `[core]`
- P3: For each, ProteinMPNN→AF2 scRMSD + Foldseek novelty; plot novelty vs scRMSD frontier; per-topology success rates. `[core]` FrameFlow speed/diversity comparison. `[extension]`
- P4: Select a novel-but-foldable set; write a synthesis/expression plan with controls (a high-novelty risky design + a conservative design). `[core]` Short MD stability check on top picks. `[stretch]`
- P5: Thesis + a "novelty budget" guideline.
**Benchmark/ablation:** RFdiffusion vs FrameFlow vs Genie2 (diversity/speed/foldability); length sweep.
**Key refs:** Watson 2023 (RFdiffusion); Yim 2024 (FrameFlow); novelty: TM-score<0.5 convention.

---

### Project 04 — Symmetric Protein Nanocage / Oligomer Design
**Skill refs:** backbone-design-ref (symmetric mode), validation-ref · **Compute:** A100 recommended.
**Real problem:** Self-assembling protein nanocages are a leading platform for **multivalent vaccine antigen display** and for delivery. Designing subunits that reliably form a target symmetry (and not the wrong oligomer) is hard and high-impact.
**Objectives:** (1) Design symmetric assemblies (Cn/Dn) with RFdiffusion symmetric mode; (2) sequence-design with tied positions; (3) validate subunit + interface with AF2-Multimer; (4) reason about oligomeric-state errors.
**Tools:** RFdiffusion (symmetric), ProteinMPNN (tied positions), AF2-Multimer/ColabFold, SymDesign concepts, py3Dmol.
**Data:** reference designed nanocages (e.g., I3-01 family) for comparison; symmetry definitions.
**6-month tasks:**
- P0–P1: Reproduce a small cyclic (C3) design; understand symmetry contigs + tied positions. `[core]`
- P2: Generate C3/C4/D2 assemblies; sequence-design with tied chains; 100s of designs. `[core]`
- P3: AF2-Multimer on subunit + interface (pAE<10), symmetry check, interface energy; rank. `[core]` Wrong-oligomer risk analysis (predict alternative states). `[extension]`
- P4: Top assemblies → propose nsEM/SEC-MALS validation plan; antigen-display extension (graft an epitope). `[extension]` Larger symmetry (tetrahedral). `[stretch]`
- P5: Thesis + assembly design report.
**Benchmark/ablation:** symmetry order vs success; tied vs untied sequence design.
**Key refs:** Watson 2023 (symmetric); Wicky 2022 (symmetric assemblies validation pipeline); nanocage vaccine literature.

---

### Project 05 — Automated Multi-Layer Design-Triage Pipeline (Shared Engine)
**Skill refs:** validation-ref · **Compute:** free Colab T4.
**Real problem:** Campaigns produce thousands of designs; manual triage is irreproducible. Labs need an automated, documented 4-layer filter that ranks designs and emits a report — the **infrastructure later projects depend on.**
**Objectives:** (1) Implement the 4-layer filter (self-consistency → orthogonal → physics → optional MD) as clean, tested functions; (2) define and justify cutoffs per design type; (3) emit ranked tables + figures; (4) document the discrimination problem honestly.
**Tools:** Python (pandas, numpy, matplotlib), ColabFold/ESMFold, Boltz-2, optional PyRosetta/FreeBindCraft relax for physics layer, Biopython.
**Data:** a pre-computed pool of ~100–500 designs with predictions (from Projects 01/03 or public sets).
**6-month tasks:**
- P0–P1: Spec the API (`Design` dataclass; layer functions); implement Layer 1 (self-consistency) with tests. `[core]`
- P2: Implement Layers 2 (orthogonal) + 3 (physics: solubility/aggregation, Rosetta energy where available); unit tests on known-good/known-bad designs. `[core]`
- P3: Implement ranking + `report()` (ranked CSV + survival-at-each-layer figure); validate on a labeled set. `[core]` Optional Layer 4 (short MD) hook. `[extension]`
- P4: Write the "discrimination problem" analysis (no metric perfectly separates true binders); sensitivity of ranking to cutoffs. `[core]` Package as a pip-installable module. `[stretch]`
- P5: Thesis + the engine becomes `shared/filtering_pipeline.py` for the cohort.
**Benchmark/ablation:** enrichment at each layer on labeled data; cutoff sensitivity.
**Key refs:** validation-ref 4-layer filter; Norn 2021; BindCraft discrimination caveat.

---

## TIER B — Binders & Therapeutics

### Project 06 — De Novo Mini-Binder vs PD-L1 (Checkpoint Blockade)
**Skill refs:** binder-design-ref, validation-ref · **Compute:** Colab Pro (A100) or local A100; free-tier fallback = small campaign.
**Real problem:** PD-1/PD-L1 blockade transformed oncology, but antibodies are large, costly, and have PK/penetration limits. Small de novo binders to PD-L1 are an active, real alternative (better tumor penetration, cheaper manufacture).
**Objectives:** (1) Run BindCraft and RFdiffusion binder mode against PD-L1; (2) select hotspots on the PD-1-binding face; (3) apply the full filter; (4) compare the two paradigms head-to-head.
**Tools:** BindCraft (or FreeBindCraft), RFdiffusion binder mode + ProteinMPNN, AF2-Multimer, `filtering_pipeline.py`.
**Data:** PD-L1 ectodomain structure — candidate accessions: PD-1/PD-L1 complex (verify on RCSB, e.g., 4ZQK/5O45) to define the competitive epitope.
**6-month tasks:**
- P0–P1: Target prep (clean structure, identify PD-1-binding hotspots), reproduce a BindCraft mini-run. `[core]`
- P2: BindCraft campaign (50–200 designs) + RFdiffusion campaign (500–1000 backbones → MPNN). `[core]`
- P3: 4-layer filter both pools; head-to-head hit-rate, diversity, interface-energy comparison; top 10–20 each. `[core]` Epitope-competition reasoning vs PD-1. `[extension]`
- P4: Validation plan — SPR/BLI vs PD-L1, PD-1 competition assay, negative controls (scrambled interface), expression strategy. `[core]` Boltz-2 affinity prediction on top hits. `[stretch]`
- P5: Thesis + binder design report.
**Benchmark/ablation:** BindCraft vs RFdiffusion (hit rate, KD-proxy, novelty).
**Responsible-research note:** therapeutic/diagnostic framing only.
**Key refs:** Pacesa 2025 (BindCraft); Cao 2022 (target-structure-only binders); Watson 2023.

---

### Project 07 — De Novo Binder vs SARS-CoV-2 / Pan-Sarbecovirus Spike RBD
**Skill refs:** binder-design-ref · **Compute:** A100 recommended.
**Real problem:** Pandemic preparedness needs fast, broadly cross-reactive countermeasures. Designing minibinders to **conserved** RBD epitopes (vs the variable RBM) is a live research direction for variant-resistant antivirals and diagnostics.
**Objectives:** (1) Choose a conserved vs variable epitope and justify; (2) design binders with BindCraft/RFdiffusion; (3) assess predicted breadth across variants; (4) filter + plan validation. **Defensive/neutralizing framing only.**
**Tools:** BindCraft, RFdiffusion binder mode, AF2-Multimer, sequence-conservation analysis, `filtering_pipeline.py`.
**Data:** RBD–ACE2 complex (candidate: 6M0J, verify) + a panel of variant RBD sequences/structures for breadth analysis.
**6-month tasks:**
- P0–P1: Map conserved RBD epitopes (conservation across sarbecoviruses); target prep. `[core]`
- P2: Binder campaign against the chosen epitope. `[core]`
- P3: Filter; predict cross-reactivity by modeling binder vs multiple variant RBDs (AF2-Multimer pAE across variants). `[core]` Compare conserved- vs variable-epitope targeting. `[extension]`
- P4: Validation + breadth-testing plan (panel of variant RBDs), ACE2-competition assay, controls. `[core]`
- P5: Thesis + pandemic-preparedness report.
**Benchmark/ablation:** conserved vs variable epitope breadth; tool comparison.
**Responsible-research note:** target the *host-receptor-binding/neutralizing* face to *block* the virus; explicitly out-of-scope to enhance viral fitness.
**Key refs:** Cao 2020 (de novo ACE2-mimetic/RBD minibinders); Pacesa 2025.

---

### Project 08 — De Novo Binder vs KRAS (the "Undruggable" Oncotarget)
**Skill refs:** binder-design-ref · **Compute:** A100 recommended.
**Real problem:** KRAS drives ~25% of cancers and was "undruggable" for decades; G12C inhibitors broke that, but most KRAS alleles (e.g., G12D) remain hard. De novo binders to allele-specific surfaces or the switch regions are a frontier.
**Objectives:** (1) Select a KRAS surface/allele (e.g., switch I/II, or a mutant-specific pocket); (2) design binders; (3) reason about specificity vs other RAS isoforms; (4) filter + plan validation.
**Tools:** BindCraft, RFdiffusion binder mode, AF2-Multimer, `filtering_pipeline.py`, structural alignment for isoform specificity.
**Data:** KRAS structures (candidates: WT 4OBE, G12C 6OIM — verify); HRAS/NRAS for specificity comparison.
**6-month tasks:**
- P0–P1: Literature on KRAS druggability; choose epitope/allele; target prep (nucleotide state matters — GDP vs GTP/analog). `[core]`
- P2: Binder campaign at the chosen surface. `[core]`
- P3: Filter; specificity analysis (model binder vs HRAS/NRAS); allele selectivity reasoning. `[core]` Effector-competition framing (block RAF). `[extension]`
- P4: Validation plan with isoform-specificity panel + controls. `[core]` Nucleotide-state dependence test design. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** epitope choice; isoform cross-reactivity.
**Key refs:** KRAS structural biology reviews; Pacesa 2025; Cao 2022.

---

### Project 09 — Macrocycle / Peptide Binder vs MDM2–p53 (or IL-17)
**Skill refs:** binder-design-ref (peptide/macrocycle), validation-ref · **Compute:** Colab T4–Pro.
**Real problem:** Macrocyclic/constrained peptides bridge small molecules and biologics — potential **oral or cell-penetrant** therapeutics. The MDM2–p53 interaction (restore p53 tumor suppression) is a canonical PPI target with known peptide chemistry.
**Objectives:** (1) Design linear + cyclic peptide binders; (2) compare peptide vs mini-protein modalities; (3) assess predicted affinity; (4) plan synthesis/validation appropriate to peptides.
**Tools:** BoltzGen (peptide-anything, macrocycle-anything), EvoBind2, AF2/Boltz-2, RFpeptides concepts.
**Data:** MDM2–p53 peptide complex (candidate: 1YCR — verify) defines the binding cleft; or IL-17A as alternative.
**6-month tasks:**
- P0–P1: PPI + peptide-therapeutic literature; target cleft prep; reproduce a peptide-design mini-run. `[core]`
- P2: Linear + macrocyclic peptide campaigns; vary length/constraint. `[core]`
- P3: Filter (Boltz-2 affinity, AF2 pAE); compare peptide vs mini-binder (run Project 06-style mini-binder as a foil). `[core]` Cyclization-chemistry feasibility notes. `[extension]`
- P4: Validation plan — note peptides need SPP synthesis + protease-stability/permeability assays, not just E. coli. `[core]` D-amino-acid / stapling extension. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** linear vs cyclic; peptide vs protein modality.
**Key refs:** BoltzGen 2025; EvoBind2; macrocycle therapeutic reviews.

---

### Project 10 — De Novo Binder vs an Antimicrobial-Resistance Target (e.g., NDM-1)
**Skill refs:** binder-design-ref · **Compute:** A100 recommended.
**Real problem:** AMR is a top global health threat. Metallo-β-lactamases like **NDM-1** hydrolyze carbapenems (last-resort antibiotics) and lack clinical inhibitors. A designed binder that occludes/inhibits the active site is a defensible, high-impact target.
**Objectives:** (1) Target the NDM-1 active-site rim to block substrate access; (2) design binders; (3) reason about inhibition mechanism; (4) filter + plan an inhibition assay.
**Tools:** BindCraft, RFdiffusion binder mode, LigandMPNN (Zn-aware near active site), AF2-Multimer, `filtering_pipeline.py`.
**Data:** NDM-1 structure with di-zinc site (candidate: 3SPU/4EYL — verify).
**6-month tasks:**
- P0–P1: AMR + metallo-β-lactamase literature; active-site prep (preserve Zn site); choose occluding epitope. `[core]`
- P2: Binder campaign targeting the active-site rim. `[core]`
- P3: Filter; model whether the binder occludes substrate access (pocket geometry); specificity vs human metalloenzymes. `[core]`
- P4: Validation plan — nitrocefin/carbapenem hydrolysis inhibition assay, IC50, controls (off-target metalloenzyme). `[core]` Combine with a β-lactam (adjuvant concept). `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** epitope (active-site rim vs distal); binder length.
**Responsible-research note:** purpose is to *inhibit* a resistance enzyme (restore antibiotic efficacy) — out-of-scope to enhance resistance or pathogen fitness.
**Key refs:** NDM-1 structural papers; Pacesa 2025; LigandMPNN (Dauparas 2024).

---

### Project 11 — Conformation-Specific Binder vs Tau / α-Synuclein
**Skill refs:** binder-design-ref, validation-ref · **Compute:** A100 recommended.
**Real problem:** Alzheimer's (tau) and Parkinson's (α-synuclein) feature pathological aggregates. Binders that recognize a **specific aggregated/fibril conformation** (not the monomer) enable diagnostics (PET tracers, assays) and aggregation modulators.
**Objectives:** (1) Distinguish monomer vs fibril conformations; (2) design binders to a fibril surface; (3) reason about conformational specificity (the hard part); (4) filter + plan a specificity assay.
**Tools:** RFdiffusion binder mode, BindCraft, AF2-Multimer, fibril cryo-EM structures, `filtering_pipeline.py`.
**Data:** cryo-EM fibril structures — tau PHF (candidates: 5O3L/5O3T) and α-syn fibril (candidates: 6CU7/6H6B) — verify; monomer models for the specificity counter-test.
**6-month tasks:**
- P0–P1: Amyloid/fibril structural biology; choose target conformation; prep fibril surface. `[core]`
- P2: Binder campaign to the fibril epitope. `[core]`
- P3: Filter; conformational-specificity test (model binder vs monomer vs fibril; must prefer fibril). `[core]` Cross-amyloid specificity (tau vs α-syn). `[extension]`
- P4: Validation plan — fibril-vs-monomer ELISA/SPR, controls; diagnostic-tracer framing. `[core]`
- P5: Thesis.
**Benchmark/ablation:** conformational selectivity; epitope choice.
**Key refs:** tau/α-syn cryo-EM (Fitzpatrick; Schweighauser); Pacesa 2025.

---

### Project 12 — De Novo Binder → Biosensor (Binder + Split-Reporter Switch)
**Skill refs:** binder-design-ref, backbone-design-ref · **Compute:** A100 recommended.
**Real problem:** Rapid, cheap diagnostics need analyte-responsive sensors. Coupling a de novo binder to a **conformational switch / split-reporter** (LOCKR-style or split-luciferase) turns binding into signal — a real platform for point-of-care assays.
**Objectives:** (1) Design a binder to a chosen analyte (small protein/biomarker); (2) integrate it with a switch/split-reporter concept; (3) reason about the binding→signal transduction; (4) plan a functional readout.
**Tools:** BindCraft/RFdiffusion (binder), RFdiffusion (scaffold/switch), ProteinMPNN, AF2, LOCKR/split-reporter literature.
**Data:** a biomarker target structure (student choice, e.g., a cytokine or cardiac marker — verify accession); split-reporter reference designs.
**6-month tasks:**
- P0–P1: Biosensor architectures (allosteric switches, split systems); pick analyte + readout. `[core]`
- P2: Design the binder module; design/borrow the switch module. `[core]`
- P3: Filter binder; model the integrated construct; reason about ON/OFF states. `[core]` Two-state AF2 modeling of switch. `[extension]`
- P4: Validation plan — luminescence/FRET dose-response, LOD estimate, controls (no-analyte, off-target). `[core]` Multiplexing concept. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** switch architecture; binder affinity vs dynamic range.
**Key refs:** Langan/Baker LOCKR; split-reporter biosensor literature; Pacesa 2025.

---

### Project 13 — Cytokine-Mimetic Receptor Agonist Mini-Protein
**Skill refs:** binder-design-ref, backbone-design-ref · **Compute:** A100 recommended.
**Real problem:** Natural cytokines (e.g., IL-2) are powerful but pleiotropic and unstable. De novo mimetics that engage a **chosen receptor subunit combination** with tuned selectivity (the Neoleukin "Neo-2/15" paradigm) are a real immunotherapy strategy.
**Objectives:** (1) Choose a receptor (sub)unit interface to engage; (2) design an agonist mini-protein hitting the right subunits; (3) reason about receptor selectivity (e.g., βγ vs α); (4) filter + plan a signaling assay.
**Tools:** RFdiffusion binder mode / BindCraft, ProteinMPNN, AF2-Multimer (model binder vs each receptor subunit), `filtering_pipeline.py`.
**Data:** IL-2/IL-2R complex (candidate: 2B5I — verify); reference Neo-2/15 design.
**6-month tasks:**
- P0–P1: Cytokine signaling + de novo mimetic literature; define target subunit engagement + desired selectivity. `[core]`
- P2: Design mini-proteins engaging the chosen receptor surfaces. `[core]`
- P3: Filter; selectivity modeling (engages βγ but not α, or vice versa); stability advantage vs natural cytokine. `[core]`
- P4: Validation plan — receptor-binding SPR per subunit + cell signaling (STAT phosphorylation) assay, controls. `[core]` Thermostability comparison to native cytokine. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** subunit selectivity; comparison to natural cytokine interface.
**Key refs:** Silva 2019 (Neo-2/15); Watson 2023; Pacesa 2025.

---

## TIER C — Antibodies & Nanobodies

### Project 14 — De Novo Nanobody (VHH) vs a Viral Antigen
**Skill refs:** antibody-design-ref, validation-ref · **Compute:** A100 recommended.
**Real problem:** Nanobodies (15 kDa, stable, cheap, deep-tissue) are an ideal pandemic-ready platform. De novo VHH design against conserved viral epitopes (influenza HA stem, RSV F prefusion) is newly feasible with RFantibody. **Neutralizing framing only.**
**Objectives:** (1) Choose a conserved neutralizing epitope; (2) design VHH CDRs with RFantibody (or BoltzGen nanobody mode); (3) filter with antibody-aware metrics; (4) plan a yeast-display screen.
**Tools:** RFantibody (RFdiffusion-Ab + ProteinMPNN), BoltzGen nanobody protocol, AF2-Multimer/IgFold, humanness/developability tools, `filtering_pipeline.py`.
**Data:** HA stem (candidate: 4FQI — verify) or RSV F prefusion (candidate: 5UDE/DS-Cav1 — verify); a VHH framework (e.g., cAbBCII10/humanized).
**6-month tasks:**
- P0–P1: Antibody/CDR structure; choose epitope + framework; reproduce a small RFantibody run. `[core]`
- P2: VHH CDR design campaign (500+ given low hit rate). `[core]`
- P3: Filter — AF2-Multimer pAE, CDR geometry/Ramachandran, aggregation (TAP/CamSol), humanness. `[core]` BoltzGen vs RFantibody comparison. `[extension]`
- P4: Plan a **yeast-display** screen (pool designs → FACS vs labeled antigen → sequence winners → express → SPR); controls. `[core]`
- P5: Thesis.
**Benchmark/ablation:** RFantibody vs BoltzGen; epitope conservation/breadth.
**Responsible-research note:** neutralizing/diagnostic only.
**Key refs:** Bennett 2025 (RFantibody, Nature); BoltzGen 2025; Abanades 2023 (ImmuneBuilder).

---

### Project 15 — Computational Antibody Affinity Maturation + Developability
**Skill refs:** antibody-design-ref, sequence-design-ref · **Compute:** Colab T4–Pro.
**Real problem:** Therapeutic-antibody lead optimization (raise affinity, keep developability) is slow and expensive. Computational maturation that proposes a *small, testable* set of improving mutations is directly industrially relevant.
**Objectives:** (1) Start from a known antibody–antigen complex; (2) propose affinity-improving CDR mutations (ESM-1v/AbLang + ProteinMPNN); (3) check binding pose is maintained; (4) screen for developability liabilities.
**Tools:** ESM-1v, AbLang/AbLang2, ProteinMPNN (CDR redesign, framework fixed), AF2-Multimer, developability filters (TAP, CamSol; deamidation/oxidation hotspot scan).
**Data:** an antibody–antigen complex from SAbDab (student-chosen, verify accession) with a measured KD in literature.
**6-month tasks:**
- P0–P1: Affinity-maturation + developability literature; identify CDR contact residues; reproduce ESM-1v scoring. `[core]`
- P2: Score single mutations (ESM-1v/AbLang); ProteinMPNN CDR redesigns; assemble a candidate mutation set. `[core]`
- P3: AF2-Multimer pose maintenance; rank; developability liability scan (avoid NG/DG/Met in CDRs). `[core]` Epistasis/combination reasoning. `[extension]`
- P4: Validation plan — express variants, SPR kinetics, DSF stability, specificity panel; controls (WT + a destabilizing decoy). `[core]`
- P5: Thesis.
**Benchmark/ablation:** ESM-1v vs AbLang vs ProteinMPNN agreement; single vs combined mutations.
**Key refs:** antibody-design-ref affinity-maturation workflow; AbLang; ESM-1v (Meier 2021).

---

### Project 16 — Antibody Humanization Pipeline with Humanness Scoring
**Skill refs:** antibody-design-ref · **Compute:** Colab T4.
**Real problem:** Non-human antibodies trigger anti-drug-antibody responses; humanization is a regulatory necessity. A reproducible computational humanization + humanness-scoring pipeline (predicting stability cost) is a clean, high-value capstone.
**Objectives:** (1) Take a non-human antibody; (2) graft CDRs onto human germline frameworks; (3) score humanness (OASis/T20); (4) predict and mitigate stability/affinity loss.
**Tools:** AbLang, OASis/Hu-mAb/T20 humanness scoring, ProteinMPNN (framework optimization), AF2/IgFold (structure), FoldX/Rosetta ΔΔG (stability proxy).
**Data:** a non-human therapeutic antibody sequence + human germline framework database (IMGT/OAS).
**6-month tasks:**
- P0–P1: Humanization strategies (CDR grafting, resurfacing, germline content) literature; pick antibody + frameworks. `[core]`
- P2: Graft CDRs onto candidate human frameworks; generate variants. `[core]`
- P3: Humanness scoring; structure prediction; ΔΔG stability prediction; identify back-mutations needed (Vernier zone). `[core]` Compare grafting vs resurfacing. `[extension]`
- P4: Validation plan — express humanized variants, ELISA/SPR (retained binding?), DSF, immunogenicity-risk summary; controls (parental + over-humanized decoy). `[core]`
- P5: Thesis.
**Benchmark/ablation:** framework choice; grafting vs resurfacing; humanness vs stability trade-off.
**Key refs:** OASis/Hu-mAb; AbLang; antibody-design-ref humanization section.

---

### Project 17 — Nanobody vs a Tumor-Associated Antigen (HER2/EGFR/Mesothelin)
**Skill refs:** antibody-design-ref · **Compute:** A100 recommended.
**Real problem:** Nanobodies against tumor antigens power imaging agents and CAR constructs. De novo VHH design to a defined, validated tumor antigen epitope is a real translational pipeline.
**Objectives:** (1) Choose a TAA + epitope (avoid the natural-ligand site or target it deliberately); (2) design VHH; (3) filter + assess specificity; (4) plan a screen + a downstream format (imaging or CAR).
**Tools:** RFantibody / BoltzGen nanobody mode, AF2-Multimer, developability filters, `filtering_pipeline.py`.
**Data:** TAA structure — HER2 (candidate: 1N8Z trastuzumab–HER2, verify), EGFR (candidate: 1IVO), or mesothelin model.
**6-month tasks:**
- P0–P1: TAA biology + nanobody therapeutics; choose epitope (overlapping vs non-overlapping with approved mAbs). `[core]`
- P2: VHH design campaign. `[core]`
- P3: Filter; specificity vs related receptors (e.g., HER family); epitope-binning reasoning. `[core]`
- P4: Plan a display screen + a downstream construct (e.g., VHH-Fc for imaging, or CAR scFv-equivalent); controls. `[core]` Bispecific/biparatopic concept. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** epitope choice; specificity within receptor family.
**Responsible-research note:** therapeutic/diagnostic only.
**Key refs:** Bennett 2025; nanobody-CAR / imaging literature.

---

## TIER D — Enzymes & Catalysis

### Project 18 — De Novo Kemp Eliminase (the Field Benchmark)
**Skill refs:** enzyme-design-ref, validation-ref · **Compute:** A100 recommended for scaffolding.
**Real problem:** The Kemp elimination is the model reaction for de novo enzyme design (no natural counterpart, simple readout). Recent methods (Riff-Diff, RFdiffusion2) reach near-natural rates *without* directed evolution — a perfect teaching benchmark and a genuine methods test.
**Objectives:** (1) Build a Kemp-eliminase theozyme; (2) scaffold it (RFdiffusion2 / Riff-Diff / motif scaffolding); (3) sequence-design with LigandMPNN preserving catalytic residues; (4) validate active-site geometry + plan a kinetic assay.
**Tools:** theozyme construction (catalytic base + π-stack + H-bond donor), RFdiffusion2 / Riff-Diff / RFdiffusion motif scaffolding, LigandMPNN, AF2 (catalytic-residue geometry), AutoDock Vina (substrate fit), OpenMM (active-site stability).
**Data:** 5-nitrobenzisoxazole substrate + TS geometry (from literature/QM); reference designed Kemp eliminases.
**6-month tasks:**
- P0–P1: Enzyme-design + Kemp literature; construct the theozyme (define functional-group positions). `[core]`
- P2: Scaffold (1000s of backbones); LigandMPNN sequence design fixing catalytic residues. `[core]`
- P3: Filter — global + catalytic-residue pLDDT, catalytic geometry RMSD <0.5 Å vs theozyme, substrate docking, short MD of active-site stability. `[core]` Method comparison (RFdiffusion2 vs Riff-Diff vs motif). `[extension]`
- P4: Plan the kinetic assay (UV absorbance of product; kcat/KM, controls: natural reference, heat-killed, empty vector); select <96 for synthesis. `[core]` Directed-evolution plan for hits. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** scaffolding-method comparison; catalytic-geometry preservation rate.
**Key refs:** Schnettler 2025 (Riff-Diff, Nature); Dauparas 2025 (RFdiffusion2); Rothlisberger 2008 (first Kemp).

---

### Project 19 — Plastic-Degrading Active-Site Design (PETase-like)
**Skill refs:** enzyme-design-ref, validation-ref · **Compute:** A100 recommended.
**Real problem:** Plastic pollution and circular-chemistry needs drive enzyme engineering for PET hydrolysis. Designing/grafting a PET-hydrolase-like Ser-His-Asp active site into a stable scaffold (thermostability is the real bottleneck) is high-impact.
**Objectives:** (1) Define the serine-hydrolase catalytic triad + oxyanion hole for an ester substrate; (2) scaffold into a thermostable fold; (3) design sequence; (4) emphasize MD-based thermostability + plan an activity assay.
**Tools:** theozyme (Ser-His-Asp triad), RFdiffusion2 / Riff-Diff, LigandMPNN, AF2, OpenMM/GROMACS (thermostability MD), docking (PET-mimic substrate).
**Data:** IsPETase / cutinase structures (candidates: 6EQE/5XJH — verify) as references; ester/PET-mimic substrate model.
**6-month tasks:**
- P0–P1: PETase mechanism + thermostability-engineering literature; define triad geometry. `[core]`
- P2: Scaffold the triad into stable folds; sequence design. `[core]`
- P3: Filter + **MD-based thermostability ranking** (RMSF, melting-proxy); substrate-pocket accessibility (docking). `[core]` Compare engineered-natural vs fully de novo scaffolds. `[extension]`
- P4: Plan activity assay (pNP-ester colorimetric or PET-film/HPLC), thermostability (DSF), controls. `[core]` Surface-residue redesign for solubility. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** scaffold thermostability vs activity trade-off.
**Key refs:** PETase structural/engineering papers; Lauko 2025 (serine hydrolases, Science); enzyme-design-ref.

---

### Project 20 — CO₂-Fixing Metalloenzyme (Carbonic-Anhydrase-Style)
**Skill refs:** enzyme-design-ref, sequence-design-ref (LigandMPNN) · **Compute:** A100 recommended.
**Real problem:** Carbon capture motivates robust, fast CO₂-hydration catalysts. Carbonic anhydrase is the model; designing a **de novo Zn-metalloenzyme** active site (the GRACE paradigm produced functional carbonic-anhydrase designs) tests metal-aware design end-to-end.
**Objectives:** (1) Define a Zn-coordinating active site (3-His + hydroxide); (2) scaffold + design with **LigandMPNN** (metal-aware); (3) validate metal-site geometry; (4) plan an activity + metal-incorporation assay.
**Tools:** theozyme with metal site, RFdiffusion / RFdiffusion2, **LigandMPNN** (Zn), AF2, MD (metal-site stability — note classical FF limits), GRACE-style pipeline (CLEAN classification, solubility).
**Data:** carbonic anhydrase II (candidate: 2CAB/3KS3 — verify) as reference; Zn site geometry.
**6-month tasks:**
- P0–P1: Metalloenzyme design + GRACE literature; define Zn-His₃-OH site. `[core]`
- P2: Scaffold; **LigandMPNN** sequence design preserving metal ligands; large pool (GRACE used ~10k). `[core]`
- P3: Filter — metal-ligand geometry, pLDDT at site, solubility, CLEAN-style functional classification; MD caveats for metals. `[core]`
- P4: Plan assay — esterase-proxy (pNPA) and/or CO₂-hydration (Wilbur-Anderson units), ICP/metal-incorporation check, controls (apo, natural CA). `[core]` Alternative metal (Co) substitution test. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** LigandMPNN vs ProteinMPNN at the metal site; pool-size vs hit-rate.
**Key refs:** Hu 2024 (GRACE); Dauparas 2024 (LigandMPNN); enzyme-design-ref.

---

### Project 21 — De Novo Serine Hydrolase / Esterase (Green Chemistry)
**Skill refs:** enzyme-design-ref · **Compute:** A100 recommended.
**Real problem:** Serine hydrolases/esterases are industrial workhorses (synthesis, biocatalysis, detergents). The 2025 Science serine-hydrolase work showed de novo design of efficient hydrolases — a tractable, validated target reproducing a frontier result.
**Objectives:** (1) Build the Ser-His-Asp triad + oxyanion hole theozyme; (2) scaffold; (3) sequence-design preserving the triad; (4) validate geometry + plan kinetics on a chromogenic ester.
**Tools:** theozyme, RFdiffusion2 / Riff-Diff, LigandMPNN/ProteinMPNN, AF2, docking, MD.
**Data:** reference serine hydrolases; pNP-acetate / fluorogenic ester substrate.
**6-month tasks:**
- P0–P1: Serine-hydrolase mechanism + de novo design literature; build theozyme. `[core]`
- P2: Scaffold + sequence design. `[core]`
- P3: Filter (catalytic geometry, MD stability, pocket accessibility); rank. `[core]` Substrate-scope reasoning (acyl-chain length). `[extension]`
- P4: Plan kinetic assay (pNP-ester, steady-state kinetics), controls (catalytic-Ser→Ala "dead" mutant is a perfect negative), DSF. `[core]` Enantioselectivity concept. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** scaffolding method; Ser→Ala dead-mutant control logic.
**Key refs:** Lauko 2025 (Science); Schnettler 2025; enzyme-design-ref.

---

## TIER E — Frontier & Integration

### Project 22 — Conformational-Switch / Multi-State Protein
**Skill refs:** sequence-design-ref (multi-state), backbone-design-ref · **Compute:** A100 recommended.
**Real problem:** Proteins that change conformation/function on a stimulus (pH, ligand, light) underpin smart biomaterials, allosteric sensors, and logic gates. Multi-state design is a genuine frontier.
**Objectives:** (1) Define two target states + the trigger; (2) multi-state sequence design (sequence compatible with both backbones); (3) validate both states + the switch; (4) plan a state-reporting assay.
**Tools:** RFdiffusion (two backbones), ProteinMPNN multi-state (ensemble), AF2 (predict both states), MD (transition plausibility), LOCKR concepts.
**Data:** reference switch designs (LOCKR, hinge proteins); two-state backbone definitions.
**6-month tasks:**
- P0–P1: Allostery + multi-state design literature; define states + trigger. `[core]`
- P2: Generate the two states; multi-state ProteinMPNN to find a shared sequence. `[core]`
- P3: AF2 predict both states from one sequence; energy-gap reasoning; filter. `[core]` MD of the transition. `[extension]`
- P4: Plan a readout for state change (FRET/protease accessibility/SAXS), controls. `[core]` Light-switch (LOV domain) integration. `[stretch]`
- P5: Thesis.
**Benchmark/ablation:** single- vs multi-state design; state energy gap.
**Key refs:** Langan/Baker LOCKR; sequence-design-ref multi-state; allosteric design reviews.

---

### Project 23 — Protein–Nucleic-Acid Binder (DNA/RNA-Binding Mini-Protein)
**Skill refs:** sequence-design-ref (LigandMPNN), binder-design-ref · **Compute:** A100 recommended.
**Real problem:** Designed nucleic-acid-binding proteins enable gene-editing modulators, RNA-targeting therapeutics, and synthetic transcription factors. **LigandMPNN** explicitly supports nucleic acids, making this newly tractable.
**Objectives:** (1) Choose a DNA/RNA target (sequence/structure motif); (2) design a binding mini-protein with LigandMPNN; (3) reason about specificity; (4) plan an EMSA/binding assay.
**Tools:** RFdiffusion (scaffold near nucleic acid), **LigandMPNN** (nucleic-acid-aware), AF3-style/AF2 complex modeling or Boltz (protein–NA), `filtering_pipeline.py`.
**Data:** a protein–DNA/RNA complex as a starting template (verify accession); target motif.
**6-month tasks:**
- P0–P1: Protein–NA recognition + LigandMPNN-NA literature; choose target motif. `[core]`
- P2: Scaffold + LigandMPNN design around the nucleic acid. `[core]`
- P3: Filter; specificity vs scrambled motif; complex modeling. `[core]` CRISPR-modulator framing (bind a Cas surface). `[extension]`
- P4: Plan EMSA / fluorescence-anisotropy binding + specificity controls (scrambled NA). `[core]`
- P5: Thesis.
**Benchmark/ablation:** sequence specificity; ProteinMPNN vs LigandMPNN at the interface.
**Key refs:** Dauparas 2024 (LigandMPNN); protein–NA design literature.

---

### Project 24 — Metalloprotein / Cofactor-Binding De Novo Protein (Heme/FeS/Zn)
**Skill refs:** sequence-design-ref (LigandMPNN), backbone-design-ref · **Compute:** A100 recommended.
**Real problem:** De novo metalloproteins and cofactor-binders are the basis of artificial electron-transfer proteins, synthetic oxygen carriers, and artificial metalloenzymes — a long-standing grand challenge now tractable with ML.
**Objectives:** (1) Choose a cofactor (heme, [4Fe-4S], or Zn) + coordination scheme; (2) scaffold a binding pocket; (3) design with LigandMPNN (cofactor-aware); (4) validate coordination geometry + plan a spectroscopic assay.
**Tools:** RFdiffusion / RFdiffusion2, **LigandMPNN** (ligand/metal-aware), AF2, MD (with metal-FF caveats), docking of cofactor.
**Data:** reference cofactor-binding proteins (heme: cytochrome/myoglobin; FeS: ferredoxin); cofactor geometry.
**6-month tasks:**
- P0–P1: De novo metalloprotein literature (e.g., designed heme proteins); choose cofactor + ligands. `[core]`
- P2: Scaffold the pocket; LigandMPNN design preserving coordinating residues. `[core]`
- P3: Filter — coordination geometry, pocket fit (docking), pLDDT at site, solubility. `[core]` Redox-tuning reasoning. `[extension]`
- P4: Plan assay — UV-vis/Soret band for heme (or EPR for FeS), metal/cofactor titration, controls (apo, ligand→Ala mutant). `[core]`
- P5: Thesis.
**Benchmark/ablation:** cofactor choice; coordination-residue preservation.
**Key refs:** designed metalloprotein literature (DeGrado, Baker); Dauparas 2024 (LigandMPNN).

---

### Project 25 — Capstone Integrated DBTL Campaign + ML Success Predictor
**Skill refs:** ALL · **Compute:** A100 recommended; aggregates cohort compute.
**Real problem:** The field's central bottleneck is the **gap between in-silico scores and experimental success** — "no metric perfectly separates true binders from false." Closing the loop requires (a) a complete, controlled campaign and (b) learning from accumulated data which features actually predict success.
**Objectives:** (1) Run a *complete* DBTL campaign on a **student-chosen, advisor-approved real target** (any tier); (2) execute or fully plan experimental validation; (3) **train an ML model** on cohort-wide design data (features → in-silico/experimental outcome) to improve the shared filter; (4) deliver an honest hit-rate analysis.
**Tools:** the full stack (RFdiffusion/RFdiffusion2/BindCraft/RFantibody as appropriate), `filtering_pipeline.py`, scikit-learn/XGBoost (success predictor), all validation tools.
**Data:** student's chosen target + the **aggregated design–outcome dataset** assembled across Projects 1–24 in the cohort (sequences, in-silico metrics, and any experimental labels).
**6-month tasks:**
- P0–P1: Choose + justify target (responsible-research check); define success criteria + controls upfront. `[core]`
- P2: Full design campaign on the target. `[core]`
- P3: Apply the shared filter; **build the cohort feature table**; train + cross-validate an ML success predictor; report feature importance. `[core]` Compare to the field's standard cutoffs. `[extension]`
- P4: Execute (if lab capacity) or fully plan validation; integrate any experimental labels into the model; honest hit-rate + failure forensics. `[core]` Active-learning loop design (which design to test next). `[stretch]`
- P5: Thesis + the improved success-predictor module + a cohort-wide "lessons learned" synthesis.
**Benchmark/ablation:** ML predictor vs single-metric cutoffs (enrichment); feature importance; cross-target generalization.
**Responsible-research note:** advisor must approve the chosen target against the §7 policy before P2.
**Key refs:** all prior; BindCraft discrimination caveat; ML-for-design-filtering literature.

---

## Cross-project dependency map (suggested sequencing for a cohort)

- **Projects 01, 02, 03, 05** produce infrastructure (validation harness, MPNN settings, backbone pool, filtering engine) that **all later projects reuse**. Run at least one of each early in the cohort, or assign them to the first wave of students.
- **Project 25** consumes the **design–outcome data** generated by Projects 01–24 — schedule it last in a cohort cycle.
- Binder projects (06–13) share the BindCraft/RFdiffusion-binder + filtering workflow; antibody projects (14–17) share RFantibody + developability; enzyme projects (18–21) share theozyme + RFdiffusion2/Riff-Diff + LigandMPNN. Generating one project per family first gives you a within-family template.
