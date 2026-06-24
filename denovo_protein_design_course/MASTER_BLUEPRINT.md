# MASTER BLUEPRINT — Standards for All 25 Projects

This document defines the **invariant standards** every generated project must satisfy. Claude Code must load this on every generation. The `PROJECT_CATALOG.md` entry supplies the project-specific content; this file supplies the *shape*.

---

## 0. Guiding principles (the DBTL spine)

Every project is one turn of the **Design–Build–Test–Learn** cycle, even when "Build/Test" is a *plan* rather than executed wet-lab work:

```
DEFINE  → What function? What constraints? What does success look like? What are the controls?
DESIGN  → Generate backbone → design sequence → filter in silico (this is the bulk of the compute)
BUILD   → Gene-synthesis / cloning / expression strategy (planned; executed only if lab capacity exists)
TEST    → Biophysical + functional characterization plan (SEC, CD, DSF, SPR/BLI, activity)
LEARN   → Failure analysis, iteration, honest reporting of hit rate
```

**Non-negotiable teaching messages, embedded in every project:**
1. *A computational design is a hypothesis, not a result.* pLDDT is **not** stability; low scRMSD is **not** binding; expression is **not** function.
2. *Diversity before filtering.* Generate many (100s–1000s), filter aggressively, never polish a single design endlessly.
3. *Controls are mandatory* — even in the experimental *plan* (positive control, scrambled-interface negative, unrelated-protein negative).
4. *Report the hit rate*, not the cherry. Include failures.

---

## 1. Standard project anatomy (file structure)

Every project folder is `projects/project_NN_shortname/` and MUST contain exactly this structure:

```
project_NN_shortname/
├── README.md               # Landing page: problem, objectives, quickstart, deliverables (from README_TEMPLATE.md)
├── INSTRUCTIONS.md         # Week-by-week student guide, 24 weeks (from INSTRUCTIONS_TEMPLATE.md)
├── MANUAL.md               # Technical reference: theory, tools, commands, parameters, troubleshooting (from MANUAL_TEMPLATE.md)
├── TIMELINE.md             # Gantt-style 6-month milestone table + deliverable-to-assessment mapping
├── ASSESSMENT.md           # Rubric, deliverable specs, weighting (instantiated from the shared rubric in §5)
├── notebooks/
│   ├── 00_setup.ipynb              # Colab env check + installs (adapted from templates/setup_colab.ipynb)
│   ├── 01_define_and_explore.ipynb # Target/problem exploration, structure prep, baseline prediction
│   ├── 02_design_campaign.ipynb    # Backbone generation + sequence design (the core)
│   ├── 03_filter_and_rank.ipynb    # Multi-layer filtering (imports shared/filtering_pipeline.py)
│   ├── 04_analysis_and_figures.ipynb # Benchmarks, ablations, publication-quality figures
│   └── 05_validation_plan.ipynb    # Docking/MD as relevant + experimental-plan generator
├── data/
│   ├── README.md           # Data provenance, exact accessions, licenses, sizes
│   ├── download_data.py     # Reproducible fetcher (adapted from templates/download_data.py)
│   └── inputs/             # Small seed files only (target PDBs, configs, theozyme defs); large data fetched, never committed
├── scripts/
│   └── (project-specific .py helpers; common logic imported from shared/)
├── results/
│   └── .gitkeep            # Empty; students write outputs here (git-ignored)
├── references/
│   └── reading_list.md     # 8–12 papers, tiered (intro / method / frontier), with 1-line "why read this"
└── env/
    └── requirements.txt    # Pinned, Colab-compatible
```

**Rules:**
- Notebooks must be **valid `.ipynb` JSON** (nbformat 4), each with a first cell that `!pip`-installs only what that notebook needs and a GPU check.
- **Never commit large data** (PDB dumps, AlphaFold DB, model weights). Provide `download_data.py` and document sizes.
- Every notebook runs **top-to-bottom on Colab** with no hidden state. Set seeds. Print versions.
- Cross-project shared code lives in `templates/filtering_pipeline.py` etc.; projects copy or import it, never silently fork it.

---

## 2. The shared 6-month (24-week) timeline template

Every project instantiates these six phases. The catalog gives *project-specific tasks* for each phase; the phase structure, milestones, and deliverables are fixed so cohorts stay synchronized and grading is comparable.

| Phase | Weeks | Theme | Key student tasks | Milestone deliverable |
|-------|-------|-------|-------------------|-----------------------|
| **P0 — Orient** | 1–2 | Problem & literature | Read the tiered reading list; write a 1-page problem statement with explicit, measurable success criteria; reproduce the project's "hello-world" tutorial notebook | **D0:** Problem statement + reproduced tutorial output |
| **P1 — Baseline** | 3–6 | Environment + minimal pipeline | Run `00_setup` + `01_define_and_explore`; prepare target/inputs; produce a *first, small* set of designs end-to-end (even if bad); set up the git repo + lab notebook | **D1:** Working minimal pipeline + 1st design batch + repo |
| **P2 — Campaign** | 7–12 | Core design generation | Scale generation (100s–1000s); sequence design; parameter exploration; manage compute budget; log everything | **D2:** Full design pool + design log + interim report |
| **P3 — Filter & benchmark** | 13–18 | Triage + comparison | Apply the 4-layer filter; rank; run ablations/comparisons specified in the catalog; novelty checks; honest hit-rate accounting | **D3:** Ranked top candidates + benchmark figures + filtering report |
| **P4 — Validate (in silico) + plan (wet-lab)** | 19–22 | Deepen confidence + experimental design | Orthogonal prediction, docking/MD as relevant; write the full experimental validation plan with controls, timeline, and a costed reagent list | **D4:** Validation report + experimental plan + (optional) wet-lab data |
| **P5 — Synthesize** | 23–24 | Thesis + defense | Final written report (thesis chapter format); reproducible repo + archived environment; 15-min presentation | **D5:** Thesis report + talk + reproducible release (tagged) |

**Why this fills 6 months:** P2 + P3 alone are 12 weeks of genuine work — compute is slow, campaigns fail and restart, filtering requires building/validating pipelines, and benchmarking demands careful experimental design. The catalog deliberately specifies *more* sub-tasks than a strong student will finish, so advisors can scope up/down per student.

**Scaling lever (instructor knob):** Each catalog entry tags tasks as `[core]`, `[extension]`, or `[stretch]`. Assign `[core]` to all; `[extension]` to most; `[stretch]` to strong students or to extend toward an MSc thesis.

---

## 3. Compute reality (be honest with students)

| Step | Free Colab (T4) | Notes / fallback |
|------|-----------------|------------------|
| ColabFold / AF2 single prediction | ✅ 2–10 min | Bottleneck at scale; batch overnight or use ESMFold for triage |
| ESMFold | ✅ seconds–min | No MSA; great for fast orthogonal checks |
| ProteinMPNN / LigandMPNN | ✅ seconds | CPU-fine; trivial |
| RFdiffusion (monomer/symmetric/motif) | ⚠️ small campaigns | Official ColabDesign notebook; large campaigns need A100/HPC |
| RFdiffusion2 / Riff-Diff (enzymes) | ⚠️ | Verify current public release at generation time; HPC recommended |
| BindCraft | ⚠️ limited | Realistically Colab **Pro (A100)** or local A100; free-tier = tiny campaign. Fallbacks: FreeBindCraft, Tamarind, Neurosnap, Ariax |
| BoltzGen / Boltz-2 | ✅/⚠️ | Boltz-2 affinity prediction OK on T4 for small inputs |
| RFantibody | ⚠️ | A100 recommended; plan yeast-display screening for hits |
| Short MD (OpenMM, 10–50 ns) | ⚠️ | Feasible on T4 for small systems; long MD → HPC |

**Instructor budget guidance:** a class of 20 on Colab Pro is roughly **\$500–1000/semester**, or use 1 shared institutional GPU (RTX 3090+ / A100) for batch jobs. Every project's `00_setup` notebook prints the detected GPU and **degrades gracefully** (smaller `num_designs`, ESMFold instead of AF2 for triage) when only a T4 is available.

> **Generation-time rule for Claude Code:** Do **not** hard-code "this runs free on Colab" for binder/antibody/enzyme campaigns. State the realistic tier and the fallback. Pin the *upstream repo* in setup and add a cell that verifies the current notebook/version still exists, because these tools change.

---

## 4. Shared infrastructure (build once, reuse 25×)

These live in `templates/` and are copied (or imported) into each project:

- **`setup_colab.ipynb`** — GPU detection, conda/pip bootstrap, version printing, graceful T4 fallback flags.
- **`filtering_pipeline.py`** — the 4-layer filter as importable functions: `self_consistency()`, `orthogonal_check()`, `physics_filter()`, `rank_designs()`, plus a `Design` dataclass and a `report()` that emits a ranked table + figures.
- **`download_data.py`** — fetch PDB by ID, AlphaFold DB by UniProt, with checksum + license logging.

Every project's `03_filter_and_rank.ipynb` imports `filtering_pipeline.py` so students learn **one** filtering API across all 25 projects.

---

## 5. Assessment (shared rubric, instantiated per project)

**Weighting (default; instructor may adjust):**

| Component | Weight | Mapped deliverable |
|-----------|--------|--------------------|
| Problem definition & literature | 10% | D0 |
| Pipeline execution & reproducibility | 20% | D1–D3, repo |
| Design campaign rigor (diversity, controls, logging) | 15% | D2 |
| Filtering, benchmarking & critical analysis | 20% | D3 |
| Validation plan (controls, feasibility, cost) | 15% | D4 |
| Final report & reproducibility release | 10% | D5 |
| Oral defense | 10% | D5 |

**Rubric (apply to the final report; the same six criteria the field uses):**

| Criterion | Excellent (A) | Good (B) | Adequate (C) | Poor (D/F) |
|-----------|---------------|----------|--------------|-----------|
| Problem definition | Specific, motivated, measurable success criteria | Clear but generic | Vague | Absent |
| Tool selection & justification | Reasoned vs alternatives | Correct, thin justification | No rationale | Wrong tools |
| Computational execution | Complete, multi-layer filter, error analysis, reproducible | Complete, basic filtering | Incomplete | Non-working |
| Critical analysis | Honest limitations + failure forensics + hit-rate accounting | Some limitations noted | Superficial | None |
| Experimental plan | Detailed, controlled, costed, timed | Reasonable, gaps | Vague | Absent |
| Communication | Clear prose, professional figures, logical flow | Mostly clear | Disorganized | Poor |

> **Grading philosophy (state to students explicitly):** You are graded on **rigor, reasoning, and reproducibility — not on whether the protein works.** A meticulously analyzed campaign with a 0% hit rate and sharp failure forensics earns an A; a lucky-looking single design with no controls and no hit-rate accounting does not.

---

## 6. Data policy & canonical sources

- **Structures:** RCSB PDB (`https://www.rcsb.org`), AlphaFold DB (`https://alphafold.ebi.ac.uk`). Always record the **exact accession** and access date.
- **Sequences/antibodies:** UniProt; OAS (Observed Antibody Space) for antibody projects; SAbDab for antibody–antigen complexes.
- **Benchmarks:** project-specific curated sets (defined in the catalog), built from published design papers' supplementary data where licensing allows.
- **Licensing:** `data/README.md` records the license/terms for every source. Do **not** redistribute restricted weights or datasets; link + script the download instead.
- **Reproducibility:** seeds fixed; environments pinned; a `results/` manifest lists every produced file with the command that made it.

---

## 7. Biosecurity & responsible-research policy (MANDATORY in every project)

De novo design of binders, antibodies, and enzymes is **dual-use**. Every generated project MUST include a short "Responsible Research" section stating:

- **In scope:** therapeutic, diagnostic, industrial, and basic-science targets — checkpoint proteins, oncotargets, host receptors, AMR enzymes (to *inhibit*), aggregation proteins, industrial/green-chemistry enzymes, cofactor-binding proteins.
- **Out of scope (do not design, and refuse student proposals for):** anything intended to **enhance pathogen transmissibility or virulence**, **toxins or toxin-delivery**, evasion of biosecurity screening, or binders/enzymes whose primary purpose is to cause harm. Targeting a pathogen protein to *neutralize* it is fine; engineering a pathogen to be *more dangerous* is not.
- **Synthesis screening:** any real gene-synthesis order must go through a provider that performs biosecurity screening (IGSC members); document this in the experimental plan.
- **Institutional oversight:** wet-lab execution requires biosafety/ethics approval; the plan must name the relevant committee.
- **Honesty about capability:** students must not overstate results or imply experimental validation that wasn't done.

If a student's chosen target (especially in Projects 7, 10, 14, 25) raises dual-use concern, the advisor redirects to a defensible neutralizing/diagnostic framing or a different target.

---

## 8. Reproducibility & writing standards

- **Repo hygiene:** `.gitignore` excludes `results/`, weights, and large data; `env/requirements.txt` is pinned; a tagged release (`v1.0`) accompanies D5.
- **Lab notebook:** a running `LOG.md` (date, command, GPU, outcome) — graded as part of reproducibility.
- **Figures:** consistent style; every figure has a caption stating what metric, what cutoff, and N.
- **Report format:** thesis-chapter style — Abstract, Introduction (problem + state of field), Methods (exact tools/versions/params), Results (with hit rates and distributions, not just bests), Discussion (limitations + failure forensics), Experimental Plan, References, Reproducibility Statement.
- **Citations:** use the tiered reading list as the starting bibliography; add the specific tool papers actually used.

---

## 9. What Claude Code must NOT do at generation time

- Do not invent fake data, fake experimental results, or fake KD/kcat values. Notebooks may include **synthetic example data clearly labeled `EXAMPLE_DATA`** for teaching a plotting/analysis step, never presented as real results.
- Do not promise that any campaign "will produce a binder/enzyme." State realistic hit rates.
- Do not hard-code tool versions as eternal truth; pin + verify upstream.
- Do not include any out-of-scope (harmful/dual-use-misuse) target, even if a catalog wording is ambiguous — default to the neutralizing/diagnostic framing.
- Do not omit the Responsible Research section.
