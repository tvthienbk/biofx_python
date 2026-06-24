# Project 21 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** A serine hydrolase cleaves an ester (or amide) bond by the
**Ser-His-Asp charge-relay** mechanism: the catalytic His, oriented and polarised by the Asp/Glu,
deprotonates the Ser hydroxyl so that **Ser-OG attacks the ester carbonyl carbon**, forming a
**tetrahedral intermediate** whose developing oxyanion is stabilised by the **oxyanion hole** (usually
two backbone amide NHs). The intermediate collapses to an acyl-enzyme, which a His-activated water then
hydrolyses to release the acid product and regenerate the free serine. This is the chemistry of
esterases, lipases, and proteases — the **industrial workhorse** of biocatalysis (synthesis, kinetic
resolution, detergents). De novo enzyme design proceeds **theozyme → scaffold → sequence → geometry
check**: you first define a *theozyme* (the catalytic functional groups placed around the **tetrahedral
intermediate**), build protein backbones that present that motif, design a sequence that folds to the
backbone while keeping the catalytic residues, and check the predicted active site still holds the
theozyme geometry. The **2025 Science** work (Lauko et al.) showed this can produce *efficient*
hydrolases from scratch — the result this project reproduces on a general esterase.

**Key concepts a student must understand.**
- **Theozyme** — the minimal catalytic motif + TS geometry. For ester hydrolysis: the **Ser-His-Asp
  triad** (Ser-OG nucleophile; His-NE2 general base; Asp/Glu charge-relay) **plus the oxyanion hole**
  (two H-bond donors stabilising the tetrahedral-intermediate oxyanion). Place groups around the
  **tetrahedral intermediate / TS**, not the ground-state ester. *Do not forget the oxyanion hole* — it
  is easy to omit and decisive for catalysis.
- **Motif scaffolding** — generating backbones that hold those functional groups in the right relative
  geometry (RFdiffusion2 / Riff-Diff / RFdiffusion motif mode), biased toward an **open, accessible
  pocket** (a buried triad cannot turn over substrate).
- **Catalytic-residue-fixed sequence design** — LigandMPNN redesigns the protein but **keeps the triad
  AND the oxyanion-hole donors fixed** (and is ligand/TS-aware), which is exactly why it (not vanilla
  ProteinMPNN) is used for enzymes.
- **Catalytic-geometry RMSD** — atom-level RMSD of the predicted catalytic atoms (Ser-OG, His-NE2,
  Asp-OD + the oxyanion-hole N/OG atoms) vs the theozyme target placement. **This is the key metric:**
  < 0.5 Å is the pass bar. Self-consistency (scRMSD) and pLDDT can look great while the catalytic atoms
  are misplaced — only this metric catches that.
- **Active-site pLDDT** — local AF2 confidence *at the catalytic residues* (target ≥ 90), stricter than
  the global pLDDT bar.
- **Pocket accessibility & substrate scope** — beyond geometry, the pNP-ester must physically fit the
  pocket and orient its carbonyl toward Ser-OG (docking), and the **acyl-chain length** the pocket
  accepts sets esterase- (short acyl, C2 acetate) vs lipase-like (longer acyl, C4–C8) preference.

**Why this is hard and what realistic success looks like.** De novo enzyme **hit rates are low** —
often **<5% active without directed evolution**, and even the recent methods that reach efficient rates
**still require screening**. Most importantly: **preserving the catalytic geometry in silico does NOT
guarantee catalysis.** A design can hold a perfect triad geometry and be dead (dynamics, desolvation,
His pKa, oxyanion-hole H-bond subtleties, second-shell effects all matter). Success for this capstone =
a rigorous, honestly-reported campaign with a catalytic-geometry-filtered set and a sound pNP-ester
kinetic-assay plan whose **catalytic-Ser→Ala dead mutant** proves any rate is real — **not** a working
enzyme.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion2 / Riff-Diff (scaffolding — the A100 step)
- **What it does / where it fits:** generates backbones that present the triad + oxyanion-hole motif
  (P2 core). Riff-Diff (Schnettler 2025, *Nature*) is theozyme→enzyme scaffolding; RFdiffusion2
  (Dauparas 2025) is all-atom motif/active-site scaffolding.
- **Install:** **VERIFY the current public release/repo at generation time** — these are new and move
  fast; do not assume a repo URL. Pin the commit/tag you actually use and log it.
- **Key parameters:** the motif/constraint spec (your triad + oxyanion hole as contigs + ligand/ester
  TS), number of backbones (1000s for the real campaign), diffusion steps/noise; bias toward an open
  pocket. Export the theozyme to the tool's format from `enzyme_tools.scaffold_motif`.
- **Compute:** **A100 recommended** (Colab Pro+ or HPC) for 1000s of backbones. Free-tier fallback = a
  small **RFdiffusion** (classic) motif-scaffolding demo of tens of backbones.
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
  triad AND the oxyanion-hole donors** and accounting for the ligand/TS context (P2 core). CPU-fast.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the version).
- **Key parameters:** the **fixed-positions** list (every catalytic residue: Ser, His, Asp + oxyanion
  donors), the ligand/ester-TS context PDB, `temperature` (try 0.1–0.3), sequences-per-backbone.
- **Compute:** CPU-fine; trivial vs scaffolding.
- **Typical call:**
  ```bash
  python run.py --pdb_path bb.pdb --fixed_residues "A105 A187 A132 A57 A58" \
                --ligand_mpnn_use_atom_context 1 --out_folder seqs/ --temperature 0.2
  ```

### AlphaFold2 (catalytic-triad geometry)
- **What it does / where it fits:** predicts each designed sequence; you read **per-residue pLDDT at
  the active site** and compute **catalytic-geometry RMSD** vs the theozyme (P3 core). ESMFold for fast triage.
- **Install:** official ColabFold notebook (pin the commit); ESMFold via `transformers` for triage.
- **Key parameters:** `num_recycles`, `msa_mode` (single-sequence is realistic for de novo seqs).
- **Compute:** free T4 OK for these sizes; ESMFold is fastest (no MSA).

### AutoDock Vina (pocket accessibility + substrate scope) · OpenMM (active-site MD)
- **Vina** (`https://github.com/ccsb-scripps/AutoDock-Vina`, pin version): dock the pNP-ester into the
  designed pocket — a **fit/orientation** check (does it sit oriented with the carbonyl C toward
  Ser-OG?), NOT an affinity or activity measurement. Re-run across the **acyl-chain series** (C2/C4/C6/C8)
  for substrate-scope reasoning (`enzyme_tools.substrate_scope_scan`). **OpenMM**
  (`https://github.com/openmm/openmm`, pin version): short active-site MD (10–50 ns on small systems is
  T4-feasible) → catalytic-atom RMSF / backbone RMSD.

> All of the above are wrapped behind clean functions in `scripts/enzyme_tools.py` with a deterministic
> **mock** backend (no GPU) so the plumbing runs anywhere; the real backends are marked TODO. **Every
> mock number is SYNTHETIC — never report it as a real result, and never fabricate a kcat/KM/ee.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → enzyme-design + serine-hydrolase theory; build_theozyme() (triad + oxyanion hole) → spec; dead-mutant demo; mock scaffold (D0)
02_generate         → theozyme → scaffold (RFdiffusion2/Riff-Diff; A100) → LigandMPNN (triad FIXED) → results CSV (D2)
03_filter_and_rank  → import filtering_pipeline as fp; build enzyme Designs; fp.run_pipeline(design_type="enzyme") + fp.report (D3 pt1)
04_validate         → catalytic-geometry preservation + scaffolding-method comparison + pocket-accessibility/substrate-scope + MD figures (D3 pt2)
05_validation_plan  → pNP-ester kinetic-assay + DSF plan + controls (incl. catalytic-Ser→Ala dead mutant) + enantioselectivity stretch (D4/D5)
```

## 4. Filtering cutoffs for this design type (`design_type="enzyme"`)
From `shared/filtering_pipeline.py` `DEFAULT_CUTOFFS["enzyme"]`:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT (global) | ≥ 85 | overall local confidence (NOT stability) |
| pLDDT (catalytic) | ≥ 90 | stricter confidence *at the active site* — the part that matters |
| **catalytic_geom_rmsd** | **< 0.5 Å** | **the key metric:** predicted catalytic atoms (triad + oxyanion hole) vs the theozyme |

Project-specific orthogonal checks (not hard cutoffs in the shared filter, used in `04_validate`):
**pocket accessibility** (the pNP-ester docks and orients toward Ser-OG) and **substrate scope** (which
acyl chains the pocket admits).

> Reminder: **no in-silico metric perfectly separates true from false hits** — and for enzymes,
> *passing all four does not mean the design is catalytically active.* Filters enrich; they do not
> guarantee. Report false positives and the hit rate honestly; a kinetic assay is the real test.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 2 Å, global pLDDT ≥ 85, **active-site pLDDT ≥ 90, catalytic-geometry
  RMSD < 0.5 Å**, the pNP-ester docks oriented toward Ser-OG, active site MD-stable, and a sensible
  acyl-chain preference.
- A *suspicious* one: great global pLDDT but **high catalytic-geometry RMSD** (folds well, triad
  misplaced) — the classic enzyme-design trap; or a triad that is geometrically perfect but **buried**
  so the substrate cannot reach it; or an oxyanion hole that is not actually formed.
- **Survival-at-each-layer** (from `fp.report`): read it as a funnel — N generated → N self-consistent
  → N with good triad geometry → N MD-stable. The drop at the geometry layer is usually the steepest.
- **Hit rate:** report N(pass all layers) / N(generated), per scaffolding method. Expect it to be low —
  that is the honest, expected outcome, not a failure of your work.
- **Catalytic-geometry preservation rate:** the headline benchmark — fraction holding the triad < 0.5 Å.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies during scaffolding | T4 too small for 1000s of backbones | Reduce batch; run the small RFdiffusion demo on T4; move the real campaign to A100/HPC |
| RFdiffusion2 / Riff-Diff install fails | new tool, repo/release moved | **Verify the current public release** and pin a commit; log the URL; fall back to classic RFdiffusion motif mode |
| LigandMPNN redesigns a catalytic residue / the oxyanion hole | fixed-positions list wrong/empty | Pass every catalytic residue **and both oxyanion-hole donors** in `--fixed_residues`; confirm numbering matches the backbone PDB |
| All designs fail catalytic-geometry RMSD | motif not held by the scaffold, or wrong atom mapping | Re-check the theozyme export to the scaffolder; verify you compare the *same* catalytic atoms; loosen motif placement and regenerate |
| High global pLDDT but bad active site | folds well but triad misplaced | Trust the **catalytic** pLDDT + geometry RMSD, not the global pLDDT; filter on the active-site metrics |
| Geometry passes but substrate won't dock | pocket too closed / triad buried / wrong box | Re-define the Vina box at the active site; bias scaffolding toward an open pocket; revisit scaffold selection |
| Substrate scope looks wrong (no acyl chain fits) | pocket lining too tight/loose | Use LigandMPNN to line the acyl pocket for the target chain length; re-scan C2–C8 |
| Mock numbers look like results | using the no-GPU demo path | They are **SYNTHETIC** by construction — switch to the real backends before reporting anything |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight; His-tag + IMAC; SEC polish.
- **Assay:** the **pNP-ester steady-state assay** — follow **p-nitrophenolate** release from
  p-nitrophenyl acetate/butyrate by absorbance at ~405–410 nm in a plate reader; fit steady-state
  **kcat/KM** from initial rates across substrate concentrations. Add **DSF** (thermal shift) for
  fold/stability. Probe **substrate scope** with the acyl-chain series (C2/C4/C6/C8 pNP-esters).
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF, the pNP-ester kinetic
  assay, substrate-scope panel) → deep (crystal/cryo-EM of the active site; acyl-enzyme trapping).
- **Controls (mandatory):**
  - **Positive:** a natural/reference serine hydrolase (e.g. a verified cutinase/lipase) — confirms the assay works.
  - **Negative — catalytic-Ser→Ala "dead" mutant:** mutate the **catalytic serine → Ala** (same protein,
    no nucleophile); the cleanest negative, since loss of activity pins catalysis to that residue.
    Use `enzyme_tools.make_dead_mutant(sequence, ser_index)`.
  - **Negative — empty-vector** lysate and a **blank** (buffer + substrate) for the non-enzymatic
    background pNP-ester hydrolysis rate (it is non-zero — subtract it from every well).
- **Enantioselectivity (`[stretch]`):** for any hit, screen a **chiral pNP-ester** and measure the
  E-value / ee — the green-chemistry kinetic-resolution readout; relate face selectivity to the pocket.

## 8. Responsible research
This is an **industrial / green-chemistry / basic-science** enzyme with **low dual-use** risk:
esterases for synthesis, kinetic resolution, and detergents have no toxin/pathogen connection. See
`MASTER_BLUEPRINT.md §7`. In-scope purpose here: building and benchmarking de novo enzyme-design
methodology for biocatalysis. Out of scope: toxins, pathogen-enhancing functions, or any design
intended to cause harm — and note that the serine-hydrolase fold also underlies **proteases**, so if
you adapt this template toward a protease or a toxin-relevant substrate, re-check the target against
§7 with your advisor first. Synthesis screening (IGSC-member provider) + institutional biosafety/ethics
approval are required for any wet-lab work.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: Lauko 2025
(de novo serine hydrolases, *Science*), Schnettler 2025 (Riff-Diff), Dauparas 2025 (RFdiffusion2),
Dauparas 2024 (LigandMPNN), Jumper 2021 (AF2), Trott & Olson 2010 (Vina), Eastman 2017 (OpenMM), plus
an alpha/beta-hydrolase mechanism reference and the theozyme/QM-TS methodology.
