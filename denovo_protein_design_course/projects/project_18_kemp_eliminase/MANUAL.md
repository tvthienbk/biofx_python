# Project 18 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** A Kemp eliminase catalyses the base-promoted ring opening
of a benzisoxazole: a catalytic base abstracts the C3 proton while, concertedly, the N–O bond breaks,
opening the ring to a 2-hydroxy-arylnitrile. There is **no natural enzyme** for this reaction, so any
activity you design is genuinely *de novo*; the substrate (5-nitrobenzisoxazole) is **chromogenic**,
so kinetics are a simple UV-vis readout. De novo enzyme design proceeds **theozyme → scaffold →
sequence → geometry check**: you first define a *theozyme* (the "theoretical enzyme" — the catalytic
functional groups placed around the **transition state**), then build protein backbones that present
that motif, then design a sequence that folds to the backbone while keeping the catalytic residues,
then check the predicted active site still holds the theozyme geometry.

**Key concepts a student must understand.**
- **Theozyme** — the minimal catalytic motif + TS geometry. For Kemp: a **catalytic base** (Asp/Glu
  carboxylate) to abstract C3-H; an **aromatic π-stack** (Trp/Tyr/Phe) to bind/orient the planar
  substrate and help delocalise developing charge; an **H-bond donor** (Ser/Thr/backbone amide) to
  stabilise the developing phenolate/nitro oxygen. Place groups around the **TS**, not the ground state.
- **Motif scaffolding** — generating backbones that hold those functional groups in the right relative
  geometry (RFdiffusion2 / Riff-Diff / RFdiffusion motif mode).
- **Catalytic-residue-fixed sequence design** — LigandMPNN redesigns the protein but **keeps the
  catalytic residues fixed** (and is ligand/TS-aware), which is exactly why it (not vanilla
  ProteinMPNN) is used for enzymes.
- **Catalytic-geometry RMSD** — atom-level RMSD of the predicted catalytic atoms vs the theozyme
  target placement. **This is the key metric:** < 0.5 Å is the pass bar. Self-consistency (scRMSD)
  and pLDDT can look great while the catalytic atoms are misplaced — only this metric catches that.
- **Active-site pLDDT** — local AF2 confidence *at the catalytic residues* (target ≥ 90), stricter
  than the global pLDDT bar.

**Why this is hard and what realistic success looks like.** De novo enzyme **hit rates are low** —
historically **<1% active without directed evolution**, and even the recent methods that reach
near-natural rates **still require screening**. Most importantly: **preserving the catalytic geometry
in silico does NOT guarantee catalysis.** A design can hold a perfect geometry and be dead (dynamics,
desolvation, pKa, second-shell effects all matter). Success for this capstone = a rigorous,
honestly-reported campaign with a catalytic-geometry-filtered set and a sound kinetic-assay plan —
**not** a working enzyme.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion2 / Riff-Diff (scaffolding — the A100 step)
- **What it does / where it fits:** generates backbones that present the theozyme motif (P2 core).
  Riff-Diff (Schnettler 2025, *Nature*) is theozyme→enzyme scaffolding; RFdiffusion2 (Dauparas 2025)
  is all-atom motif/active-site scaffolding. Both reach near-natural Kemp rates *without* evolution.
- **Install:** **VERIFY the current public release/repo at generation time** — these are new and
  move fast; do not assume a repo URL. Pin the commit/tag you actually use and log it.
- **Key parameters:** the motif/constraint spec (your theozyme as contigs + ligand/TS), number of
  backbones (1000s for the real campaign), diffusion steps/noise. Export the theozyme to the tool's
  format from `enzyme_tools.scaffold_motif`.
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

### LigandMPNN (sequence design, catalytic residues fixed)
- **What it does / where it fits:** designs a sequence for each backbone while **fixing the catalytic
  residues** and accounting for the ligand/TS context (P2 core). CPU-fast.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the version).
- **Key parameters:** the **fixed-positions** list (every catalytic residue), the ligand/TS context
  PDB, `temperature` (try 0.1–0.3), sequences-per-backbone.
- **Compute:** CPU-fine; trivial vs scaffolding.
- **Typical call:**
  ```bash
  python run.py --pdb_path bb.pdb --fixed_residues "A12 A45 A78" \
                --ligand_mpnn_use_atom_context 1 --out_folder seqs/ --temperature 0.2
  ```

### AlphaFold2 (catalytic-residue geometry)
- **What it does / where it fits:** predicts each designed sequence; you read **per-residue pLDDT at
  the active site** and compute **catalytic-geometry RMSD** vs the theozyme (P3 core). ESMFold for fast triage.
- **Install:** official ColabFold notebook (pin the commit); ESMFold via `transformers` for triage.
- **Key parameters:** `num_recycles`, `msa_mode` (single-sequence is realistic for de novo seqs).
- **Compute:** free T4 OK for these sizes; ESMFold is fastest (no MSA).

### AutoDock Vina (substrate fit) · OpenMM (active-site MD)
- **Vina** (`https://github.com/ccsb-scripps/AutoDock-Vina`, pin version): dock 5-nitrobenzisoxazole
  into the designed pocket — a **fit/orientation** check (does it sit oriented toward the base?), NOT
  an affinity or activity measurement. **OpenMM** (`https://github.com/openmm/openmm`, pin version):
  short active-site MD (10–50 ns on small systems is T4-feasible) → catalytic-atom RMSF / backbone RMSD.

> All of the above are wrapped behind clean functions in `scripts/enzyme_tools.py` with a
> deterministic **mock** backend (no GPU) so the plumbing runs anywhere; the real backends are
> marked TODO. **Every mock number is SYNTHETIC — never report it as a real result.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → enzyme-design + Kemp theory; build_theozyme() → functional-group spec; mock scaffold (D0)
02_generate         → theozyme → scaffold (RFdiffusion2/Riff-Diff; A100) → LigandMPNN (catalytic residues FIXED) → results CSV (D2)
03_filter_and_rank  → import filtering_pipeline as fp; build enzyme Designs; fp.run_pipeline(design_type="enzyme") + fp.report (D3 pt1)
04_validate         → catalytic-geometry preservation rate + scaffolding-method comparison + docking/MD figures (D3 pt2)
05_validation_plan  → kinetic-assay plan + controls (incl. catalytic-dead Ala mutant) + directed-evolution stretch (D4/D5)
```

## 4. Filtering cutoffs for this design type (`design_type="enzyme"`)
From `shared/filtering_pipeline.py` `DEFAULT_CUTOFFS["enzyme"]`:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT (global) | ≥ 85 | overall local confidence (NOT stability) |
| pLDDT (catalytic) | ≥ 90 | stricter confidence *at the active site* — the part that matters |
| **catalytic_geom_rmsd** | **< 0.5 Å** | **the key metric:** predicted catalytic atoms vs the theozyme |

> Reminder: **no in-silico metric perfectly separates true from false hits** — and for enzymes,
> *passing all four does not mean the design is catalytically active.* Filters enrich; they do not
> guarantee. Report false positives and the hit rate honestly; a kinetic assay is the real test.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 2 Å, global pLDDT ≥ 85, **active-site pLDDT ≥ 90, catalytic-geometry
  RMSD < 0.5 Å**, substrate docks oriented toward the base, active site MD-stable.
- A *suspicious* one: great global pLDDT but **high catalytic-geometry RMSD** (folds well, active
  site misplaced) — the classic enzyme-design trap; or the pocket that won't admit the substrate.
- **Survival-at-each-layer** (from `fp.report`): read it as a funnel — N generated → N self-consistent
  → N with good geometry → N MD-stable. The drop at the geometry layer is usually the steepest.
- **Hit rate:** report N(pass all layers) / N(generated), per scaffolding method. Expect it to be
  low — that is the honest, expected outcome, not a failure of your work.
- **Catalytic-geometry preservation rate:** the headline benchmark — fraction holding the motif < 0.5 Å.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies during scaffolding | T4 too small for 1000s of backbones | Reduce batch; run the small RFdiffusion demo on T4; move the real campaign to A100/HPC |
| RFdiffusion2 / Riff-Diff install fails | new tool, repo/release moved | **Verify the current public release** and pin a commit; log the URL; fall back to classic RFdiffusion motif mode |
| LigandMPNN redesigns a catalytic residue | fixed-positions list wrong/empty | Pass every catalytic residue in `--fixed_residues`; confirm numbering matches the backbone PDB |
| All designs fail catalytic-geometry RMSD | motif not actually held by the scaffold, or wrong atom mapping | Re-check the theozyme export to the scaffolder; verify you compare the *same* catalytic atoms; loosen motif placement and regenerate |
| High global pLDDT but bad active site | folds well but active site misplaced | Trust the **catalytic** pLDDT + geometry RMSD, not the global pLDDT; filter on the active-site metrics |
| Substrate won't dock in the pocket | pocket too closed / wrong box | Re-define the Vina box at the active site; check the pocket is open; revisit scaffold selection |
| Mock numbers look like results | using the no-GPU demo path | They are **SYNTHETIC** by construction — switch to the real backends before reporting anything |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight; His-tag + IMAC; SEC polish.
- **Assay:** the **Kemp UV assay** — follow product (2-hydroxy-5-nitrobenzonitrile / nitrophenolate)
  formation by absorbance at its λmax in a plate reader; fit steady-state **kcat/KM** from initial rates.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF stability, the UV
  kinetic assay) → deep (crystal/cryo-EM of the active site; substrate-bound structure).
- **Controls (mandatory):**
  - **Positive:** a natural/reference Kemp eliminase (e.g. a verified KE/HG-series enzyme).
  - **Negative — catalytic-dead mutant:** mutate the **catalytic base → Ala** (same protein, no base);
    the cleanest negative, since loss of activity pins catalysis to that residue.
  - **Negative — heat-killed** enzyme and **empty-vector** lysate (rule out background/contaminant rates).
- **Directed evolution (`[stretch]`):** for any hit, build libraries around the active site / second
  shell and screen with the **same UV assay** as the selection readout (cite the HG3.17 / Arnold context).

## 8. Responsible research
This is an **industrial / green-chemistry / basic-science** enzyme with **low dual-use** risk: the
Kemp elimination has no natural counterpart and no toxin/pathogen connection. See `MASTER_BLUEPRINT.md
§7`. In-scope purpose here: building and benchmarking de novo enzyme-design methodology. Out of scope:
toxins, pathogen-enhancing functions, or any design intended to cause harm. Synthesis screening
(IGSC-member provider) + institutional biosafety/ethics approval are required for any wet-lab work.
If you adapt this template to a different reaction (Projects 19–21, 24), re-check the new target
against §7 with your advisor first.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Röthlisberger 2008 (first Kemp), Schnettler 2025 (Riff-Diff), Dauparas 2025 (RFdiffusion2),
Dauparas 2024 (LigandMPNN), Jumper 2021 (AF2), Trott & Olson 2010 (Vina), Eastman 2017 (OpenMM),
plus the theozyme/QM-TS reference and the directed-evolution context.
