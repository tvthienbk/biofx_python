# De Novo Protein Design — 25 Capstone Projects (Generation Package)

**Audience:** Final-year undergraduate / early MSc students. Each project is a **~6-month (24-week) capstone**.
**Platform:** Google Colab (free T4 / Colab Pro A100) + GitHub. No local install required to run.
**Purpose of this folder:** This is **not** 25 finished projects. It is the **blueprint and generation system** that *you* (the instructor) feed to **Claude Code** to generate each of the 25 self-contained project folders — consistently, one command at a time.

---

## What's in this folder

| File | What it is | Who reads it |
|------|-----------|--------------|
| `README.md` | This file — map + workflow | You |
| `MASTER_BLUEPRINT.md` | The **standards**: project anatomy, the shared 6-month timeline, Colab compute reality, assessment, data policy, biosecurity/ethics | You + Claude Code (always loaded) |
| `PROJECT_CATALOG.md` | All **25 projects fully specified** (problem, tools, data, 6-month task breakdown, deliverables, references) | You + Claude Code (one entry per generation) |
| `CLAUDE_CODE_PROMPTS.md` | **Copy-paste prompts** to generate any project 1–25 (plus a "generate everything" driver) | You |
| `templates/README_TEMPLATE.md` | Per-project landing page template | Claude Code |
| `templates/INSTRUCTIONS_TEMPLATE.md` | Week-by-week student instructions template | Claude Code |
| `templates/MANUAL_TEMPLATE.md` | Technical reference manual template | Claude Code |
| `templates/setup_colab.ipynb` | Shared Colab environment-setup notebook (real, runnable skeleton) | Students |
| `templates/filtering_pipeline.py` | Shared 4-layer in-silico filtering script (real skeleton) | Students |
| `templates/download_data.py` | Shared data-fetcher (PDB / AlphaFold DB) | Students |
| `projects/project_01_validation_harness/` | **One fully worked example project** — the target quality bar | You + students |

> **Read order:** `MASTER_BLUEPRINT.md` → skim `PROJECT_CATALOG.md` → open the worked example in `projects/project_01_validation_harness/` → then use `CLAUDE_CODE_PROMPTS.md` to generate projects 2–25.

---

## The 25 projects at a glance

Difficulty rises roughly 1 → 25. Every project is anchored to a **real, current (2025–2026) problem** and is runnable on Colab.

### Tier A — Foundations & reusable tooling (1–5)
1. **AF2/ESMFold/Boltz validation harness & confidence calibration** — when can you trust a prediction as a design filter?
2. **ProteinMPNN optimization & expression-success prediction** — which settings give foldable, soluble, expressible sequences?
3. **RFdiffusion monomer design: the novelty–foldability frontier** — how novel can a fold be and still self-consistently fold?
4. **Symmetric protein nanocage / oligomer design** — scaffolds for vaccine antigen display & delivery.
5. **Automated multi-layer design-triage pipeline** — the shared filtering engine reused by later projects.

### Tier B — Binders & therapeutics (6–13)
6. **De novo mini-binder vs PD-L1** (checkpoint blockade without antibodies).
7. **De novo binder vs SARS-CoV-2 / pan-sarbecovirus spike RBD** (pandemic preparedness).
8. **De novo binder vs KRAS** (G12C/G12D — the classic "undruggable" oncotarget).
9. **Macrocycle / peptide binder vs MDM2–p53 or IL-17** (oral-modality therapeutics).
10. **De novo binder vs an antimicrobial-resistance target** (e.g., NDM-1 metallo-β-lactamase).
11. **Conformation-specific binder vs tau / α-synuclein** (neurodegeneration diagnostics & therapeutics).
12. **De novo binder → biosensor** (binder + split-reporter switch for diagnostics).
13. **Cytokine-mimetic receptor agonist** (IL-2-mimic-style immunotherapeutic mini-protein).

### Tier C — Antibodies & nanobodies (14–17)
14. **De novo nanobody (VHH) vs a viral antigen** (influenza HA stem / RSV F).
15. **Computational antibody affinity maturation + developability** (lead optimization).
16. **Antibody humanization pipeline with humanness scoring** (immunogenicity reduction).
17. **Nanobody vs a tumor-associated antigen** (HER2/EGFR/mesothelin — imaging & CAR).

### Tier D — Enzymes & catalysis (18–21)
18. **De novo Kemp eliminase** (the field's benchmark reaction; theozyme → scaffold → kinetics plan).
19. **Plastic-degrading active-site design (PETase-like)** (pollution / circular chemistry).
20. **CO₂-fixing metalloenzyme (carbonic-anhydrase-style)** (carbon capture; LigandMPNN + metal site).
21. **De novo serine hydrolase / esterase** (green chemistry; catalytic triad scaffolding).

### Tier E — Frontier & integration (22–25)
22. **Conformational-switch / multi-state protein** (pH- or ligand-gated; smart biomaterials, allostery).
23. **Protein–nucleic-acid binder** (DNA/RNA-binding mini-protein; CRISPR modulator; RNA therapeutics).
24. **Metalloprotein / cofactor-binding de novo protein** (heme / FeS / Zn; artificial metalloenzymes).
25. **Capstone integrated DBTL campaign + ML success predictor** (student-chosen real target; trains a filter on cohort data).

Full specifications for each are in **`PROJECT_CATALOG.md`**.

---

## How to generate the projects with Claude Code

1. **Put this whole folder in a git repo** and open it in Claude Code (`claude` in the repo root).
2. **Open `CLAUDE_CODE_PROMPTS.md`.** It contains:
   - A **standing instruction** (paste once per session) telling Claude Code the rules, the file anatomy, and to always honor `MASTER_BLUEPRINT.md`.
   - A **per-project prompt** (`Generate Project N`) that points Claude Code at the catalog entry and templates.
3. **Generate one project at a time**, e.g. "Generate Project 6." Review the output, run the setup notebook on Colab, then move on. Generating one at a time keeps quality high and lets you correct drift early.
4. **After generation**, each project lives in `projects/project_NN_shortname/` with its own README, instructions, manual, notebooks, data scripts, and timeline — ready to hand to a student.

> Generating all 25 in a single pass is possible (a driver prompt is provided) but **review-as-you-go is strongly recommended** — tool APIs and Colab notebooks change, and the worked example sets the bar you want every project to clear.

---

## Honest compute & scope notes (read before promising students anything)

- **Free Colab (T4, ~16 GB)** comfortably runs: ColabFold/AF2, ESMFold, ProteinMPNN, LigandMPNN, Boltz-1/Boltz-2 (small jobs), and **RFdiffusion** for modest campaigns.
- **BindCraft** and large **RFdiffusion**/**RFantibody** campaigns realistically want **Colab Pro (A100)** or an institutional GPU; on free Colab they run with strict size/time limits. Every binder/antibody/enzyme project flags this and gives a free-tier fallback (smaller campaign, or cloud platforms: Tamarind, Neurosnap, Ariax).
- **Wet-lab validation is a *plan*, not a requirement.** These are computational capstones; the experimental campaign (expression, SEC, SPR/BLI, activity assay) is designed and costed by the student, and only executed if your lab has the capacity. This is standard and pedagogically correct: *a computational design is a hypothesis until tested.*
- **Designs are hypotheses.** Realistic success rates are built into every project (binder ~1–100% depending on tool/target; de novo enzyme <5%). Students are graded on rigor and analysis, **not** on getting a working protein.

See `MASTER_BLUEPRINT.md` for the full compute table and the **biosecurity & responsible-research policy** that every project must include.
