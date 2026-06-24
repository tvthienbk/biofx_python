# Project 19 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** A PET hydrolase is a **serine hydrolase**: a His-activated
catalytic **Ser** nucleophile attacks the ester carbonyl of the PET backbone, forming a tetrahedral
intermediate (stabilised by the **oxyanion hole**), then an acyl-enzyme, which is hydrolysed to
release the cleaved chain. The catalytic machinery is the canonical **Ser-His-Asp triad + oxyanion
hole** — the same as lipases, esterases, and cutinases — so unlike the Kemp elimination this reaction
*does* have abundant natural counterparts (IsPETase, LCC, cutinases). The hard part is therefore not
inventing chemistry but **putting that triad into a fold that survives industrial conditions**: PET
only becomes accessible to enzymes near its glass transition (~65–70 °C), and wild-type IsPETase
denatures there. So this project's emphasis is **thermostability**: theozyme → scaffold (into a
*stable* fold) → sequence (triad fixed) → catalytic-geometry check → **MD-based thermostability
ranking** → substrate-pocket accessibility.

**Key concepts a student must understand.**
- **Theozyme** — the minimal catalytic motif + TS geometry. For ester hydrolysis: the **catalytic
  triad** (Ser-OG nucleophile, His-NE2 general base, Asp/Glu-OD orienting/protonating His) and the
  **oxyanion hole** (two H-bond donors — typically backbone amide NHs — to the developing
  oxyanion/carbonyl O of the tetrahedral intermediate). Place groups around the **TS / tetrahedral
  intermediate**, not the ground-state ester.
- **Oxyanion hole** — easy to forget and decisive: without it the tetrahedral intermediate is not
  stabilised and there is no catalysis even with a perfect triad. Treat its donor atoms as part of
  the fixed motif during sequence design.
- **Motif scaffolding** — generating backbones that hold the triad + oxyanion-hole atoms in the right
  relative geometry (RFdiffusion2 / Riff-Diff / RFdiffusion motif mode), biased toward **compact,
  thermostable** topologies (α/β-hydrolase-like).
- **Catalytic-residue-fixed sequence design** — LigandMPNN redesigns the protein but **keeps the
  triad + oxyanion-hole residues fixed** (and is ligand/TS-aware), which is exactly why it (not
  vanilla ProteinMPNN) is used for enzymes.
- **Catalytic-geometry RMSD** — atom-level RMSD of the predicted catalytic atoms (Ser-OG, His-NE2,
  Asp-OD + the oxyanion-hole donors) vs the theozyme target placement. **< 0.5 Å is the pass bar.**
  Self-consistency (scRMSD) and pLDDT can look great while the catalytic atoms are misplaced — only
  this metric catches that.
- **Active-site pLDDT** — local AF2 confidence *at the catalytic residues* (target ≥ 90), stricter
  than the global pLDDT bar.
- **Thermostability proxy (MD)** — the project's headline metric beyond geometry: a short MD run
  reports **catalytic-atom / backbone RMSF** and a **melting-proxy** (e.g. backbone-RMSD growth or
  loss of native contacts under elevated-temperature MD). Lower RMSF + a higher melting-proxy ⇒ a more
  thermostable candidate. **This is a proxy, not a Tm** — the real number comes from DSF (notebook 05).

**Why this is hard and what realistic success looks like.** De novo enzyme **hit rates are low** —
historically **<5% active without directed evolution**, and even recent methods that reach
near-natural rates **still require screening**. For PET hydrolases there is a specific tension: the
**thermostability ↔ activity trade-off** — rigidifying a fold to survive 65–70 °C can quench the
active-site dynamics that catalysis needs (and vice versa). Most importantly: **preserving the
catalytic geometry in silico (and passing an MD stability proxy) does NOT guarantee catalysis or real
thermostability.** Success for this capstone = a rigorous, honestly-reported campaign with a
catalytic-geometry-filtered, **thermostability-ranked** set and a sound activity + DSF assay plan —
**not** a working enzyme.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion2 / Riff-Diff (scaffolding — the A100 step)
- **What it does / where it fits:** generates backbones that present the triad + oxyanion-hole motif,
  biased toward thermostable folds (P2 core). Riff-Diff (Schnettler 2025, *Nature*) is theozyme→enzyme
  scaffolding; RFdiffusion2 (Dauparas 2025) is all-atom motif/active-site scaffolding.
- **Install:** **VERIFY the current public release/repo at generation time** — these are new and
  move fast; do not assume a repo URL. Pin the commit/tag you actually use and log it.
- **Key parameters:** the motif/constraint spec (your theozyme as contigs + ligand/ester TS), number
  of backbones (1000s for the real campaign), diffusion steps/noise, any topology bias toward stable
  folds. Export the theozyme to the tool's format from `enzyme_tools.scaffold_motif`.
- **Compute:** **A100 recommended** (Colab Pro+ or HPC) for 1000s of backbones. Free-tier fallback =
  a small **RFdiffusion** (classic) motif-scaffolding demo of tens of backbones.
- **Typical call:** *(verify against the current release)*
  ```bash
  # Conceptual — confirm the real CLI for the release you pinned:
  # riffdiff scaffold --motif theozyme.json --num 2000 --out scaffolds/
  # rfdiffusion2 ...   (all-atom motif scaffolding; see the verified repo)
  ```

### RFdiffusion (classic motif scaffolding — free-tier demo)
- **What it does / where it fits:** the P1 hello-world / free-tier demo path; tens of backbones on a T4.
- **Install:** `https://github.com/RosettaCommons/RFdiffusion` (pin the commit). Verify it still exists.
- **Key parameters:** `contigmap.contigs` (motif + built segments), `inference.num_designs`.
- **Compute:** ⚠️ small campaigns on T4; large campaigns → A100/HPC.

### LigandMPNN (sequence design, catalytic triad fixed)
- **What it does / where it fits:** designs a sequence for each backbone while **fixing the catalytic
  triad + oxyanion-hole residues** and accounting for the ester/TS context (P2 core). CPU-fast.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the version).
- **Key parameters:** the **fixed-positions** list (Ser, His, Asp **and** the oxyanion-hole residues),
  the ligand/ester-TS context PDB, `temperature` (try 0.1–0.3), sequences-per-backbone. Optionally
  bias toward thermostabilising residues at the surface (see the §1 trade-off; do *not* touch the
  triad).
- **Compute:** CPU-fine; trivial vs scaffolding.
- **Typical call:**
  ```bash
  python run.py --pdb_path bb.pdb --fixed_residues "A130 A177 A206 A87 A88" \
                --ligand_mpnn_use_atom_context 1 --out_folder seqs/ --temperature 0.2
  ```

### AlphaFold2 (catalytic-residue geometry)
- **What it does / where it fits:** predicts each designed sequence; you read **per-residue pLDDT at
  the active site** and compute **catalytic-geometry RMSD** vs the theozyme (P3 core). ESMFold for fast triage.
- **Install:** official ColabFold notebook (pin the commit); ESMFold via `transformers` for triage.
- **Key parameters:** `num_recycles`, `msa_mode` (single-sequence is realistic for de novo seqs).
- **Compute:** free T4 OK for these sizes; ESMFold is fastest (no MSA).

### OpenMM (thermostability MD — the project's emphasis) · AutoDock Vina (PET-mimic substrate fit)
- **OpenMM** (`https://github.com/openmm/openmm`, pin version) — the headline tool here: solvate,
  minimize, equilibrate, then a short production run (and/or an **elevated-temperature** run) to
  derive **RMSF** + a **melting-proxy** (backbone-RMSD growth / native-contact retention). 10–50 ns on
  small systems is T4-feasible; longer/replica or higher-temperature runs → **A100/HPC**. GROMACS is a
  valid alternative engine. **This is a *proxy*, not a Tm — classical force fields don't predict
  melting temperatures; DSF gives the real number.**
- **Vina** (`https://github.com/ccsb-scripps/AutoDock-Vina`, pin version): dock a **PET-mimic ester**
  (e.g. a mono/bis-(hydroxyethyl) terephthalate-like or a model p-nitrophenyl ester) into the designed
  pocket — a **pocket-accessibility / orientation** check (does it sit oriented toward Ser-OG?), NOT
  an affinity or activity measurement.

> All of the above are wrapped behind clean functions in `scripts/enzyme_tools.py` with a
> deterministic **mock** backend (no GPU) so the plumbing runs anywhere; the real backends are
> marked TODO. **Every mock number is SYNTHETIC — never report it as a real result, and never report
> a fabricated kcat or Tm.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → serine-hydrolase/PETase theory; build_theozyme("ester_hydrolysis") → triad+oxyanion spec; mock scaffold (D0)
02_generate         → theozyme → scaffold (RFdiffusion2/Riff-Diff; A100) → LigandMPNN (triad FIXED) → results CSV (D2)
03_filter_and_rank  → import filtering_pipeline as fp; build enzyme Designs; fp.run_pipeline(design_type="enzyme") + fp.report (D3 pt1)
04_validate         → catalytic-geometry preservation + MD-THERMOSTABILITY ranking + pocket docking + engineered-vs-de-novo (D3 pt2)
05_validation_plan  → activity assay (pNP-ester/PET-film+HPLC) + DSF + controls (catalytic-Ser→Ala dead) + surface-redesign stretch (D4/D5)
```

## 4. Filtering cutoffs for this design type (`design_type="enzyme"`)
From `shared/filtering_pipeline.py` `DEFAULT_CUTOFFS["enzyme"]`:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT (global) | ≥ 85 | overall local confidence (NOT stability) |
| pLDDT (catalytic) | ≥ 90 | stricter confidence *at the triad + oxyanion hole* — the part that matters |
| **catalytic_geom_rmsd** | **< 0.5 Å** | **the key geometry metric:** predicted catalytic atoms vs the theozyme |

> Then, beyond the shared cutoffs, this project **ranks geometry-passing survivors by an MD
> thermostability proxy** (RMSF + melting-proxy) and checks **PET-mimic pocket accessibility**
> (docking). Reminder: **no in-silico metric perfectly separates true from false hits** — and for
> enzymes, *passing geometry + a stability proxy does not mean the design is active or truly
> thermostable.* Filters enrich; they do not guarantee. Report false positives and the hit rate
> honestly; activity + DSF assays are the real tests.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 2 Å, global pLDDT ≥ 85, **active-site pLDDT ≥ 90, catalytic-geometry
  RMSD < 0.5 Å**, **low MD RMSF + a strong melting-proxy** (thermostable), PET-mimic ester docks
  oriented toward Ser-OG, oxyanion hole intact.
- A *suspicious* one: great global pLDDT but **high catalytic-geometry RMSD** (folds well, active
  site misplaced) — the classic enzyme-design trap; or geometry passes but the **MD melts / RMSF is
  high** (won't survive 65–70 °C); or a closed pocket the PET-mimic can't enter.
- **Survival-at-each-layer** (from `fp.report`): read it as a funnel — N generated → N self-consistent
  → N with good geometry → N MD-stable. Then layer the **thermostability ranking** on the survivors.
- **Hit rate:** report N(pass all layers) / N(generated), per scaffolding method **and per track
  (engineered-natural vs fully de novo)**. Expect it to be low — that is the honest, expected outcome.
- **Catalytic-geometry preservation rate** + **thermostability ranking** are the two headline
  benchmarks; the **engineered-natural-vs-de-novo** comparison is the `[extension]` study.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies during scaffolding | T4 too small for 1000s of backbones | Reduce batch; run the small RFdiffusion demo on T4; move the real campaign to A100/HPC |
| RFdiffusion2 / Riff-Diff install fails | new tool, repo/release moved | **Verify the current public release** and pin a commit; log the URL; fall back to classic RFdiffusion motif mode |
| LigandMPNN redesigns a triad / oxyanion residue | fixed-positions list wrong/empty | Pass **every** catalytic residue (Ser, His, Asp **and** oxyanion-hole NHs) in `--fixed_residues`; confirm numbering matches the backbone PDB |
| All designs fail catalytic-geometry RMSD | motif not held, or wrong atom mapping, or oxyanion hole omitted | Re-check the theozyme export to the scaffolder; verify you compare the *same* catalytic atoms; ensure the oxyanion-hole donors are in the motif; loosen placement + regenerate |
| Geometry passes but MD "melts" (high RMSF / melting-proxy fails) | fold not actually thermostable | That is the point of the ranking — down-rank it; prefer compact α/β-hydrolase-like scaffolds; try the engineered-natural track |
| Thermostability MD too slow / won't finish | long/replica/high-T MD on a T4 | Shorten the run for triage; reserve A100/HPC for the production thermostability ranking; report it as a proxy |
| High global pLDDT but bad active site | folds well but active site misplaced | Trust the **catalytic** pLDDT + geometry RMSD, not the global pLDDT; filter on the active-site metrics |
| PET-mimic won't dock in the pocket | pocket too closed / wrong box / wrong ligand model | Re-define the Vina box at the active site; check the pocket is open and large enough for the ester; revisit scaffold selection |
| Mock numbers look like results | using the no-GPU demo path | They are **SYNTHETIC** by construction — switch to the real backends before reporting anything; never report a fabricated kcat/Tm |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** typically *E. coli* BL21(DE3) (or SHuffle for disulfide-containing cutinase-like
  folds), 16–18 °C overnight; His-tag + IMAC; SEC polish.
- **Activity assay:**
  - **Fast screen — pNP-ester colorimetric:** p-nitrophenyl acetate/butyrate; follow released
    **p-nitrophenolate at ~405–410 nm** in a plate reader; fit initial rates. (A soluble-ester proxy
    for throughput — *not* PET itself.)
  - **True substrate — PET-film / amorphous-PET digestion + HPLC:** incubate with amorphous PET film
    or powder, quantify released **MHET / TPA** by HPLC over time and temperature. This is the
    real readout for plastic degradation; run it on hits from the pNP screen.
- **Thermostability — DSF (differential scanning fluorimetry / thermal shift):** report **Tm**;
  compare designs to a natural reference (IsPETase, LCC, or a thermostable cutinase). This is the
  measurement the whole project is optimised for.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF Tm, the pNP-ester
  kinetic assay) → deep (PET-film/HPLC depolymerisation at 30/50/65 °C; crystal/cryo-EM of the active site).
- **Controls (mandatory):**
  - **Positive:** a natural/reference PET hydrolase or cutinase (e.g. a verified IsPETase / LCC / cutinase).
  - **Negative — catalytic-dead mutant:** mutate the **catalytic Ser → Ala** (same protein, no
    nucleophile); the cleanest negative, since loss of activity pins catalysis to that residue.
  - **Negative — heat-killed** enzyme and **empty-vector** lysate (rule out background/contaminant rates).
- **Surface-residue redesign for solubility (`[stretch]`):** if a thermostable hit is poorly soluble,
  redesign only the **surface** residues (LigandMPNN/ProteinMPNN, triad + core fixed) to improve
  solubility/expression; re-check geometry + the thermostability proxy afterwards.

## 8. Responsible research
This is an **industrial / green-chemistry / pollution-remediation** enzyme with **low dual-use**
risk: PET hydrolysis breaks a synthetic polymer into recyclable monomers — no toxin/pathogen
connection. See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: building and benchmarking de novo
enzyme-design methodology for plastic degradation / circular chemistry. Out of scope: toxins,
pathogen-enhancing functions, or any design intended to cause harm. Synthesis screening (IGSC-member
provider) + institutional biosafety/ethics approval are required for any wet-lab work. If you adapt
this template to a different reaction or substrate, re-check the new target against §7 with your
advisor first.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Austin 2018 (IsPETase structure/engineering), Tournier 2020 (engineered LCC, *Nature*), Lauko 2025
(de novo serine hydrolases, *Science*), Schnettler 2025 (Riff-Diff), Dauparas 2024 (LigandMPNN),
Jumper 2021 (AF2), Trott & Olson 2010 (Vina), Eastman 2017 (OpenMM), plus a thermostability-
engineering reference (e.g. the LCC ICCG / DuraPETase work) and the theozyme/QM-TS reference.
