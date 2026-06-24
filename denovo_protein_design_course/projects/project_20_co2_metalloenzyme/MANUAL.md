# Project 20 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** Carbonic anhydrase (CA) hydrates CO₂ (CO₂ + H₂O ⇌ HCO₃⁻ + H⁺)
near the diffusion limit using a single **Zn(II)** ion. The catalytic centre is a **Zn-His₃-OH** site:
three histidine imidazole nitrogens hold the Zn in a tetrahedral cage, and the fourth coordination
position carries a **Zn-bound hydroxide** whose pKa the metal lowers to ~7, making it a potent
nucleophile that attacks the CO₂ carbon; a proton-shuttle His then relays the proton to bulk solvent.
Designing this **de novo** means building the metal centre as a *theozyme* (the catalytic motif +
geometry around the transition state), scaffolding backbones that present it, designing a sequence
that folds **with the metal in context** while keeping the His ligands, and checking the predicted
site still holds the **metal-coordination geometry**. This is the **enzyme-family template** (Project
18) specialised to a metal site.

**Key concepts a student must understand.**
- **Metal-site theozyme** — the metalloenzyme's catalytic motif: the **Zn ion**, its **three His
  ligands** (imidazole N), and the **Zn-hydroxide** nucleophile, placed around the **CO₂-hydration TS**
  (`data/inputs/metal_site_def.txt`). Place groups around the **TS**, not the resting state.
- **Metal-aware sequence design** — **LigandMPNN** fixes the three His ligands **and** is given the
  **Zn as atom/ligand context**, so it designs the rest of the protein to accommodate the charged
  metal centre. This is exactly why LigandMPNN (not vanilla **ProteinMPNN**, which is metal-blind) is
  used — and exactly what the notebook-04 benchmark measures.
- **Metal-ligand geometry** — atom-level geometry of the predicted coordinating atoms vs the target:
  the three **Zn-N(His) distances** (~2.0–2.2 Å), the **N-Zn-N angles** (~109.5° tetrahedral), and an
  **RMSD** vs the target Zn-His₃ placement. **This is the key metric** (it fills `catalytic_geom_rmsd`
  in the shared filter; pass < 0.5 Å). A design can fold well (high pLDDT) yet present the His
  nitrogens at the wrong distances/angles to make a clean cage — only this metric catches that.
- **Active-site pLDDT** — local AF2 confidence *at the His ligand residues* (target ≥ 90), stricter
  than global pLDDT. **Note: AF2 does not place the metal** — you add the Zn from the His₃ geometry
  (or use a metal-aware predictor) before scoring the coordination.
- **CLEAN-style functional classification** — a GRACE-style triage step: an ML EC/function classifier
  (CLEAN) flags whether a designed sequence reads as the intended enzyme class; pair with a solubility
  score to prune the large pool before expensive checks.

**Why this is hard and what realistic success looks like.** De novo **metalloenzyme** design is hard
and **hit rates are low** — GRACE reached functional CA-style designs only by generating a **large
pool (~10k)** and screening. Three caveats stack: **(1)** preserving the metal geometry in silico does
**not** guarantee activity; **(2)** **metal incorporation is uncertain** — geometry on paper ≠ Zn
actually bound in the expressed protein (measure it by ICP/PAR); **(3)** **classical MD cannot model
the metal site well** (fixed charges, no charge transfer/polarisation/hydroxide-pKa), so MD is a weak,
caveated proxy. Success for this capstone = a rigorous, honestly-reported campaign with a
metal-geometry-filtered set, the two benchmarks, and a sound activity + metal-incorporation assay
plan — **not** a working enzyme.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion2 / Riff-Diff (scaffolding — the A100 step, large pool)
- **What it does / where it fits:** generates backbones presenting the Zn-His₃ metal motif (P2 core).
  Riff-Diff (Schnettler 2025, *Nature*) is theozyme→enzyme scaffolding; RFdiffusion2 (Dauparas 2025)
  is all-atom motif/active-site scaffolding and can place the **metal + His ligands** as an all-atom
  motif. GRACE used a **large (~10k)** pool — diversity before filtering.
- **Install:** **VERIFY the current public release/repo at generation time** — these are new and move
  fast. Pin the commit/tag you actually use and log it.
- **Key parameters:** the motif/constraint spec (your Zn + 3 His as contigs + external ligand /
  all-atom motif), number of backbones (1000s–10k for the real campaign), diffusion steps/noise.
  Export the metal site from `enzyme_tools.scaffold_motif`.
- **Compute:** **A100 recommended** (Colab Pro+ or HPC) for the large pool. Free-tier fallback = a
  small **RFdiffusion** (classic) metal-motif demo of tens of backbones.
- **Typical call:** *(verify against the current release)*
  ```bash
  # Conceptual — confirm the real CLI for the release you pinned:
  # riffdiff scaffold --motif metal_site.json --num 5000 --out scaffolds/
  # rfdiffusion2 ...   (all-atom motif scaffolding with the Zn + His3 ligands; see the verified repo)
  ```

### RFdiffusion (classic motif scaffolding — free-tier demo)
- **What it does / where it fits:** the P1 hello-world / free-tier path; tens of backbones on a T4.
  Present the His ligands as the motif and treat the Zn as an external ligand.
- **Install:** `https://github.com/RosettaCommons/RFdiffusion` (pin the commit). Verify it still exists.
- **Key parameters:** `contigmap.contigs` (His-ligand motif + built segments), `inference.num_designs`.
- **Compute:** ⚠️ small campaigns on T4; the large pool → A100/HPC.

### LigandMPNN (metal-aware sequence design — the CENTRAL tool)
- **What it does / where it fits:** designs a sequence for each backbone while **fixing the three His
  ligands** and **accounting for the Zn** (atom context). CPU-fast. This metal-awareness is the whole
  point — vanilla ProteinMPNN cannot see the metal.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the version).
- **Key parameters:** the **fixed-positions** list (all three His ligands), `--ligand_mpnn_use_atom_context 1`
  with the Zn in the context PDB, the metal-conditioned checkpoint, `temperature` (try 0.1–0.3),
  sequences-per-backbone. **Confirm the model/flag names against the current repo.**
- **Compute:** CPU-fine; trivial vs scaffolding.
- **Typical call:** *(verify flags against the repo)*
  ```bash
  python run.py --pdb_path bb_with_zn.pdb --fixed_residues "A64 A92 A118" \
                --ligand_mpnn_use_atom_context 1 --out_folder seqs/ --temperature 0.2
  ```

### ProteinMPNN (metal-BLIND baseline — for the benchmark)
- **What it does / where it fits:** the control arm of the **LigandMPNN-vs-ProteinMPNN** benchmark
  (P3). Fix the His positions but pass **no** metal/atom context, so the pocket around the charged
  metal is designed blind. `https://github.com/dauparas/ProteinMPNN` (pin the version). CPU-fast.

### AlphaFold2 (active-site geometry; does NOT place the metal)
- **What it does / where it fits:** predicts each designed sequence; you read **per-residue pLDDT at
  the His ligands** and extract the **His₃ geometry** (P3 core). ESMFold for fast triage.
- **Install:** official ColabFold notebook (pin the commit); ESMFold via `transformers` for triage.
- **Key parameters:** `num_recycles`, `msa_mode` (single-sequence is realistic for de novo seqs).
- **Compute:** free T4 OK for these sizes; ESMFold is fastest. **AF2 will not model the Zn** — add it
  from the His₃ geometry (or use a metal-aware predictor) before computing the metal-ligand geometry.

### CLEAN (functional classification) · AutoDock Vina (substrate fit) · OpenMM (metal-site MD)
- **CLEAN** (mark "verify the current release/repo"): a GRACE-style ML EC/function classifier — does
  a designed sequence read as the intended enzyme class? Pair with a solubility score to prune the pool.
- **Vina** (`https://github.com/ccsb-scripps/AutoDock-Vina`, pin version): dock CO₂ / the pNPA proxy
  toward the **Zn-OH** — a **fit/orientation** check, NOT affinity or activity. CO₂ is tiny/weak, so
  treat its docking as coarse; the pNPA proxy is easier to pose.
- **OpenMM** (`https://github.com/openmm/openmm`, pin version): short metal-site MD with a deliberate
  metal model. **METAL-FF CAVEAT (state it):** classical fixed-charge FFs model a coordinated
  transition metal poorly; use a **bonded** model (explicit Zn-N bonds — stops drift but cannot
  break/reform coordination) or a **cationic-dummy** model, cite the parameter source, and treat the
  result as a weak stability proxy only.

> All of the above are wrapped behind clean functions in `scripts/enzyme_tools.py` with a
> deterministic **mock** backend (no GPU) so the plumbing runs anywhere; the real backends are marked
> TODO. **Every mock number is SYNTHETIC — never report it as a real result.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → metalloenzyme + GRACE theory; build_theozyme("co2_hydration") → Zn-His3-OH spec; mock scaffold (D0)
02_generate         → theozyme → scaffold (RFdiffusion2/Riff-Diff; A100; large pool) → metal-aware LigandMPNN (His3 FIXED, Zn context) + ProteinMPNN baseline → results CSV (D2)
03_filter_and_rank  → import filtering_pipeline as fp; build enzyme Designs; fp.run_pipeline(design_type="enzyme") + fp.report; solubility + CLEAN-style class (D3 pt1)
04_validate         → metal-ligand geometry + LigandMPNN-vs-ProteinMPNN + pool-size-vs-hit-rate + docking/MD figures (D3 pt2)
05_validation_plan  → activity + metal-incorporation assay plan + controls (apo, natural CA) + Co-substitution stretch (D4/D5)
```

## 4. Filtering cutoffs for this design type (`design_type="enzyme"`)
From `shared/filtering_pipeline.py` `DEFAULT_CUTOFFS["enzyme"]`:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT (global) | ≥ 85 | overall local confidence (NOT stability) |
| pLDDT (catalytic) | ≥ 90 | stricter confidence *at the His ligands* — the part that matters |
| **catalytic_geom_rmsd** (= **metal-ligand RMSD**) | **< 0.5 Å** | **the key metric:** predicted Zn-coordinating atoms vs the target Zn-His₃ |

Plus project-specific checks layered on top: a **solubility** score and a **CLEAN-style functional
classification** (GRACE-style triage), and a sanity read of the **Zn-N distances (~2.0–2.2 Å)** and
**N-Zn-N angles (~109.5°)** behind the RMSD.

> Reminder: **no in-silico metric perfectly separates true from false hits** — and for a
> metalloenzyme, passing all of these does **not** mean the design is active, **nor that the metal
> even binds**. Filters enrich; they do not guarantee. Report false positives and the hit rate
> honestly; ICP (metal incorporation) and a kinetic assay are the real tests.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 2 Å, global pLDDT ≥ 85, **active-site pLDDT ≥ 90, metal-ligand RMSD
  < 0.5 Å with clean Zn-N distances/angles**, substrate reaches the Zn-OH, site MD-stable (caveated),
  CLEAN-style classifier agrees.
- A *suspicious* one: great global pLDDT but **high metal-ligand RMSD** (folds well, His₃ cage
  malformed) — the classic metalloenzyme trap; or a cage geometry that is fine but a pocket CO₂/pNPA
  cannot reach.
- **Survival-at-each-layer** (from `fp.report`): read it as a funnel — N generated → N self-consistent
  → N with good metal geometry → N MD-stable. The drop at the **metal-geometry** layer is usually the
  steepest.
- **Hit rate:** report N(pass all layers) / N(generated), per scaffolding method and per design tool.
  Expect it to be low — that is the honest, expected outcome.
- **Headline benchmarks:** the **metal-geometry preservation rate** (fraction holding the cage < 0.5 Å),
  **LigandMPNN vs ProteinMPNN** (does the metal context raise that rate?), and **pool-size vs hit-rate**
  (does scaling toward ~10k pay off?).

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies during scaffolding | T4 too small for a large metal-motif pool | Reduce batch; run the small RFdiffusion demo on T4; move the large pool to A100/HPC |
| RFdiffusion2 / Riff-Diff install fails | new tool, repo/release moved | **Verify the current public release** and pin a commit; log the URL; fall back to classic RFdiffusion motif mode |
| LigandMPNN redesigns a His ligand | fixed-positions list wrong/empty | Pass all three His ligands in `--fixed_residues`; confirm numbering matches the backbone PDB |
| LigandMPNN ignores the metal | atom context off / wrong checkpoint | Set `--ligand_mpnn_use_atom_context 1` with the Zn in the context PDB; use the metal-conditioned model |
| AF2 prediction has no Zn | AF2 does not place metals | Add the Zn from the His₃ geometry (or use a metal-aware predictor) before scoring metal-ligand geometry |
| All designs fail metal-ligand RMSD | His₃ cage not actually held by the scaffold, or wrong atom mapping | Re-check the metal-site export to the scaffolder; verify you compare the *same* coordinating atoms; loosen motif placement and regenerate |
| High global pLDDT but bad metal site | folds well but cage malformed | Trust the **catalytic** pLDDT + metal-ligand geometry, not the global pLDDT |
| MD shows the Zn drifting / "stable" but you don't trust it | classical metal-FF limitation | Use a bonded/cationic-dummy model + cite params; treat MD as a **weak proxy**, never as evidence of catalysis |
| Mock numbers look like results | using the no-GPU demo path | They are **SYNTHETIC** by construction — switch to the real backends before reporting anything |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight; His-tag + IMAC; SEC polish.
  Supplement Zn(II) in the growth/buffer to favour metal loading.
- **Metal incorporation (do this first — it gates everything):** measure bound metal by **ICP-MS** (Zn
  per protein) and/or a **PAR / 4-(2-pyridylazo)resorcinol colorimetric** assay after chelator release.
  A design with no bound Zn cannot be a metalloenzyme regardless of geometry.
- **Activity assays:**
  - **Esterase proxy (fast bench readout):** **p-nitrophenyl acetate (pNPA)** hydrolysis → follow
    p-nitrophenolate absorbance (~348–405 nm); a convenient chromogenic kinetic readout (CA has a
    promiscuous esterase activity). Subtract the uncatalysed background.
  - **True CO₂ hydration:** the classic **Wilbur-Anderson** assay — time the pH drop as CO₂ is
    hydrated; report **WA units**. Stopped-flow for fast designs. The esterase proxy and CO₂ activity
    are correlated but **not identical** — state which you measured.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC → ICP metal check) → basic (DSF
  stability, the pNPA / WA assay) → deep (crystal/cryo-EM/XAS of the metal site).
- **Controls (mandatory):**
  - **Positive:** a **natural carbonic anhydrase** (confirms the assay works).
  - **Negative — apo enzyme:** the **same design with the metal stripped** (chelator, e.g. dipicolinate)
    — the metalloenzyme analogue of a catalytic-dead mutant; loss of activity pins it to the metal.
  - **Negative — His→Ala metal-knockout mutant** and **empty-vector** lysate; **buffer-only** blank
    (both CO₂ hydration and pNPA have non-zero uncatalysed rates — subtract them).
- **Alternative metal — Co(II) substitution (`[stretch]`):** reconstitute the apo design with Co(II)
  (active in CA and **spectroscopically visible**, unlike Zn(II)); a UV-vis d-d band + restored
  activity is orthogonal evidence the designed site is a genuine metal site.

## 8. Responsible research
This is an **industrial / carbon-capture / basic-science** enzyme with **low dual-use** risk: CO₂
hydration is a green-chemistry/carbon-capture reaction with no toxin/pathogen connection. See
`MASTER_BLUEPRINT.md §7`. In-scope purpose here: building and benchmarking de novo **metal-aware**
enzyme-design methodology. Out of scope: toxins, pathogen-enhancing functions, or any design intended
to cause harm. Synthesis screening (IGSC-member provider) + institutional biosafety/ethics approval are
required for any wet-lab work. If you adapt this template to a different metal/reaction (Projects 21,
24), re-check the new target against §7 with your advisor first.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used:
Hu 2024 (GRACE), Dauparas 2024 (LigandMPNN), a carbonic-anhydrase mechanism/structure paper, a de novo
metalloprotein review (DeGrado), Schnettler 2025 (Riff-Diff) / Dauparas 2025 (RFdiffusion2),
Lauko 2025 (de novo enzymes), Jumper 2021 (AF2), a metal-FF/MD-limitations reference + Eastman 2017
(OpenMM), Trott & Olson 2010 (Vina), plus the CLEAN classifier and the Co-substitution reference.
