# GENERATION LOG — De Novo Protein Design Capstones

Record of how the 25 project folders under `projects/` were generated from `MASTER_BLUEPRINT.md`,
`PROJECT_CATALOG.md`, and the `templates/`. Keep this updated when tools change and projects are
regenerated (see `CLAUDE_CODE_PROMPTS.md` → Tips).

- **Date:** 2026-06-24
- **Model:** Claude Code (Opus 4.x)
- **Method:** one project per generator, built against `MASTER_BLUEPRINT.md` §1 anatomy + the worked
  example (`project_01_validation_harness`) as the quality bar. Notebooks emitted as strict nbformat-4.5
  JSON via a shared builder; every notebook verified to run top-to-bottom on a no-GPU **mock /
  `EXAMPLE_DATA`** path. Each project's `03_filter_and_rank.ipynb` imports `shared/filtering_pipeline.py`.
- **Generation order:** infrastructure/worked example (01) + tooling (02, 03, 04, 05) first; then the
  three **family templates** (06 binder, 17 antibody, 18 enzyme); then the rest of each family
  referencing its template; **25 last** (it consumes cohort data from 01–24).

## Status: 25 / 25 complete

| # | Slug | Tier | `design_type` | Compute | Notes |
|---|------|------|---------------|---------|-------|
| 01 | project_01_validation_harness | A | — | free T4 | AF2/ESMFold/Boltz validation harness (provided worked example / quality bar) |
| 02 | project_02_mpnn_optimization | A | monomer | free T4 | ProteinMPNN settings sweep → expression/foldability Pareto map |
| 03 | project_03_rfdiffusion_monomer | A | monomer | T4 small / **A100** full | novelty–foldability frontier; novelty-budget guideline |
| 04 | project_04_symmetric_nanocage | A | oligomer | **A100** | symmetric C3/C4/D2 nanocages; vaccine antigen display |
| 05 | project_05_triage_pipeline | A | all | free T4 | builds the shared 4-layer filter engine; discrimination-problem analysis |
| 06 | project_06_pdl1_binder | B | binder | **A100** | PD-L1 checkpoint blockade — **binder-family template** |
| 07 | project_07_rbd_binder | B | binder | **A100** | SARS-CoV-2 / sarbecovirus RBD — **DEFENSIVE/neutralizing**; authored in main session |
| 08 | project_08_kras_binder | B | binder | **A100** | KRAS oncotarget; isoform/allele specificity |
| 09 | project_09_macrocycle_mdm2 | B | binder | T4–Pro | MDM2–p53 peptide/macrocycle modality comparison |
| 10 | project_10_ndm1_binder | B | binder | **A100** | NDM-1 AMR — **DEFENSIVE inhibition** (restore antibiotic efficacy) |
| 11 | project_11_fibril_binder | B | binder | **A100** | tau/α-synuclein conformation-specific (fibril vs monomer) |
| 12 | project_12_biosensor | B | binder | **A100** | binder + split-reporter switch (point-of-care diagnostic) |
| 13 | project_13_cytokine_mimetic | B | binder | **A100** | IL-2 mimetic; receptor-subunit selectivity (Neo-2/15 paradigm) |
| 14 | project_14_nanobody_viral | C | antibody | **A100** | viral neutralizing VHH — **DEFENSIVE/neutralizing**; authored in main session |
| 15 | project_15_affinity_maturation | C | antibody | T4–Pro | computational affinity maturation + developability |
| 16 | project_16_humanization | C | antibody | free T4 | humanization + humanness/stability trade-off |
| 17 | project_17_nanobody_taa | C | antibody | **A100** | tumor-antigen nanobody — **antibody-family template** |
| 18 | project_18_kemp_eliminase | D | enzyme | **A100** | Kemp eliminase benchmark — **enzyme-family template** |
| 19 | project_19_petase | D | enzyme | **A100** | PETase-like; thermostability-MD ranking |
| 20 | project_20_co2_metalloenzyme | D | enzyme | **A100** | carbonic-anhydrase-style Zn metalloenzyme (GRACE) |
| 21 | project_21_serine_hydrolase | D | enzyme | **A100** | serine hydrolase; Ser→Ala dead-mutant control |
| 22 | project_22_conformational_switch | E | monomer (multi-state) | **A100** | one sequence, two states; energy-gap caveats |
| 23 | project_23_protein_na_binder | E | binder | **A100** | DNA/RNA-binding mini-protein (LigandMPNN-NA) |
| 24 | project_24_metalloprotein | E | enzyme | **A100** | heme/FeS/Zn cofactor-binding; spectroscopic validation |
| 25 | project_25_capstone_dbtl | E | varies | **A100** | integrated DBTL + ML success predictor (generated last) |

Each project also ships `notebooks/ALL_IN_ONE.ipynb` — the six standalone notebooks (00→05)
concatenated with section dividers, to run the whole project in one Colab session.

## Generation notes / deviations
- **Notebook names** follow the worked example (`02_generate`, `04_validate`) rather than the §1
  prose names (`02_design_campaign`, `04_analysis_and_figures`); the worked example is the quality bar.
- **Pathogen-target projects (07, 14)** were authored directly (not via subagents) with an explicit
  **defensive / neutralizing** framing throughout: block the host-receptor / conserved neutralizing
  face; pseudovirus-surrogate validation under institutional biosafety (IBC) oversight; explicitly
  out-of-scope = any enhancement of pathogen transmissibility, virulence, affinity, escape, or fitness
  (`MASTER_BLUEPRINT.md §7`). Give these an extra review pass.
- **Synthetic data** in every notebook is labeled `EXAMPLE_DATA` / `SYNTHETIC`; no KD/kcat/IC50/spectra
  are fabricated. Heavy backends (BindCraft, RFdiffusion, RFantibody, LigandMPNN, AF2-Multimer, OpenMM)
  sit behind documented TODOs with A100 notes; a deterministic `mock` path runs anywhere.

## Standing human-review TODOs (before handing a project to a student)
1. **Verify every accession** on RCSB/UniProt in Week 1 (all flagged "candidate — verify"). Projects
   04, 15, 25 intentionally ship empty/placeholder accession lists for the student to fill.
2. **Pin exact upstream commits/tags** (BindCraft, RFdiffusion/RFdiffusion2, Riff-Diff, RFantibody,
   LigandMPNN, ColabFold, BoltzGen, FreeBindCraft, scikit-learn/XGBoost). The version-verify cell in
   `02` HTTP-checks the URLs but the pins are placeholders. RFdiffusion2/Riff-Diff/BoltzGen are marked
   "verify current public release."
3. **Compute:** binder/antibody/enzyme/large-diffusion campaigns need an A100; only 02, 05, 16, and the
   ML half of 25 are genuinely free-tier. Confirm cohort GPU access.
4. **Run `00_setup.ipynb` on real Colab** once per project to confirm the upstream installs still resolve.
5. **Teaching heuristics** (developability/CamSol/TAP/humanness in 14/15/16/17; theozyme geometry in
   18/19/20/21/24) are clearly-labeled placeholders — swap in the real tools / literature-QM values
   before any reportable conclusion.

## Reproduce / regenerate
- Standards: `MASTER_BLUEPRINT.md`. Per-project spec: `PROJECT_CATALOG.md`. Driver prompts:
  `CLAUDE_CODE_PROMPTS.md`. Shared filter: `shared/filtering_pipeline.py`. Templates: `templates/`.
