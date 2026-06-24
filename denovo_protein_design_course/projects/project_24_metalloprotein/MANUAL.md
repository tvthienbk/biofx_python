# Project 24 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem in one paragraph.** A cofactor-binding metalloprotein holds a **redox/O₂
cofactor** — a **heme** (Fe-protoporphyrin IX), a **[4Fe-4S]** cluster, or a **Zn** — in a protein
pocket via **coordinating residues** so the cofactor can do its job (electron transfer, O₂ transport,
or catalysis). For a **bis-His heme** (this project's default, a b-type-cytochrome electron-transfer
motif) the iron is held by the four porphyrin nitrogens **plus two axial histidines** the protein
supplies (Fe–Nε2 ~2.0–2.2 Å, His–Fe–His ~180°). Designing this **de novo** proceeds **cofactor-site
spec → scaffold pocket → cofactor-aware sequence → coordination check**: you first define the
**cofactor site** (the cofactor + its coordinating ligands + the geometry they must hold), then build
backbones that present that motif, then design a sequence that folds to the backbone while keeping the
coordinating residues *and lets the designer "see" the cofactor*, then check the predicted site still
holds the coordination geometry. The function is then confirmed by **spectroscopy**, not a catalytic
assay.

**Key concepts a student must understand.**
- **Cofactor-site spec** — the minimal coordination motif + geometry. For bis-His heme: heme b + two
  **axial His** (imidazole N) at the right Fe distance/angle. Other schemes: **His/Met** heme (c-type),
  **proximal-His + open distal** heme (O₂ binding, myoglobin-like), **[4Fe-4S]-4Cys** (ferredoxin),
  **Cys2His2** (structural Zn). Place the ligands around the **cofactor**, with the right oxidation/spin
  state in mind (it changes the geometry).
- **Motif scaffolding** — generating backbones that hold the coordinating residues in the right relative
  geometry (RFdiffusion2 / Riff-Diff / RFdiffusion motif mode), treating the cofactor as an all-atom
  motif / external ligand.
- **Cofactor-aware sequence design** — LigandMPNN redesigns the protein but **keeps the coordinating
  residues fixed** *and passes the cofactor as atom context*, which is exactly why it (not vanilla
  ProteinMPNN, which is cofactor-blind) is used. **This is the central tool of the project.**
- **Coordination-geometry RMSD** — atom-level deviation (metal-ligand distances + ligand-metal-ligand
  angles) of the predicted coordinating atoms vs the target scheme. **This is the key metric:** < 0.5 Å
  is the pass bar. It populates `catalytic_geom_rmsd`/`cat_geom` in the shared filter — for **this**
  project `cat_geom` is the **coordination**-geometry RMSD. Self-consistency (scRMSD) and pLDDT can look
  great while the coordinating atoms are misplaced — only this metric catches that.
- **Site pLDDT** — local AF2 confidence *at the coordinating residues* (target ≥ 90), stricter than the
  global pLDDT bar. It populates `plddt_catalytic`/`plddt_cat`. **AF2 does not place the metal/cofactor**
  — it predicts the apo backbone; dock/model the cofactor separately to place the metal.

**Why this is hard and what realistic success looks like.** De novo **metalloprotein** design is a
long-standing grand challenge and **hit rates are low**. Three caveats stack: **(1) coordination
geometry ≠ cofactor incorporation ≠ function** — a perfect bis-His geometry on paper does not mean heme
actually loads into the expressed protein (check by UV-vis), and loading does not mean the designed
redox/O₂ behaviour; **(2)** AF2 predicts the **apo** backbone, so the metal/cofactor must be placed
separately; **(3)** classical MD models a coordinated metal / heme Fe **poorly** (fixed charges, no
charge transfer / polarisation / spin), so MD here is a **weak, caveated** stability proxy, not ground
truth. Success for this capstone = a rigorous, honestly-reported campaign with a coordination-geometry-
filtered set and a sound **spectroscopic** assay plan — **not** a confirmed functional metalloprotein.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion2 / Riff-Diff (scaffolding — the A100 step)
- **What it does / where it fits:** generates backbones that present the coordination motif (P2 core),
  with the cofactor as an all-atom motif / external ligand. Riff-Diff (Schnettler 2025, *Nature*) is
  motif→protein scaffolding; RFdiffusion2 (Dauparas 2025) is all-atom motif/active-site scaffolding.
- **Install:** **VERIFY the current public release/repo at generation time** — these are new and move
  fast; do not assume a repo URL. Pin the commit/tag you actually use and log it.
- **Key parameters:** the motif/constraint spec (your cofactor site as contigs + the cofactor ligand +
  the coordinating ligand atoms), number of backbones (1000s for the real campaign), diffusion
  steps/noise. Export from `cofactor_tools.scaffold_cofactor_pocket`.
- **Compute:** **A100 recommended** (Colab Pro+ or HPC). Free-tier fallback = a small **RFdiffusion**
  (classic) motif-scaffolding demo of tens of backbones.
- **Typical call:** *(verify against the current release)*
  ```bash
  # Conceptual — confirm the real CLI for the release you pinned:
  # riffdiff scaffold --motif cofactor_site.json --num 2000 --out scaffolds/
  # rfdiffusion2 ...   (all-atom motif scaffolding with the cofactor as an external ligand)
  ```

### RFdiffusion (classic motif scaffolding — free-tier demo)
- **What it does / where it fits:** the P1 hello-world / free-tier demo path; tens of backbones on a T4,
  presenting the coordinating residues as a motif (cofactor as external ligand).
- **Install:** `https://github.com/RosettaCommons/RFdiffusion` (pin the commit). Verify it still exists.
- **Key parameters:** `contigmap.contigs` (motif + built segments), `inference.num_designs`.
- **Compute:** ⚠️ small campaigns on T4; large campaigns → A100/HPC.

### LigandMPNN (cofactor-aware sequence design — THE CENTRAL TOOL)
- **What it does / where it fits:** designs a sequence for each backbone while **fixing the coordinating
  residues** *and passing the cofactor (heme / cluster / metal) as atom context* (P2 core). CPU-fast.
  This ligand-awareness is exactly why LigandMPNN, not vanilla ProteinMPNN, is the right tool.
- **Install:** `https://github.com/dauparas/LigandMPNN` (pin the version).
- **Key parameters:** the **fixed-positions** list (every coordinating residue), the cofactor as atom
  context (`--ligand_mpnn_use_atom_context 1`), `temperature` (try 0.1–0.3), sequences-per-backbone.
- **Compute:** CPU-fine; trivial vs scaffolding.
- **Typical call:**
  ```bash
  python run.py --pdb_path bb_with_heme.pdb --fixed_residues "A34 A88" \
                --ligand_mpnn_use_atom_context 1 --out_folder seqs/ --temperature 0.2
  ```

### AlphaFold2 (site geometry + site pLDDT)
- **What it does / where it fits:** predicts each designed sequence; you read **per-residue pLDDT at the
  coordinating residues** and compute **coordination-geometry RMSD** vs the target (P3 core). ESMFold
  for fast triage. **AF2 predicts the apo backbone — it does NOT place the metal/cofactor**; place it by
  docking/superposition before scoring the coordination.
- **Install:** official ColabFold notebook (pin the commit); ESMFold via `transformers` for triage.
- **Key parameters:** `num_recycles`, `msa_mode` (single-sequence is realistic for de novo seqs).
- **Compute:** free T4 OK for these sizes; ESMFold is fastest (no MSA).

### AutoDock Vina (cofactor fit) · OpenMM (pocket MD — metal-FF caveat)
- **Vina** (`https://github.com/ccsb-scripps/AutoDock-Vina`, pin version): dock the cofactor (heme
  macrocycle / cluster) into the designed pocket — a **fit/orientation** check (does the metal sit
  between the ligands?), NOT an affinity, incorporation, or function measurement; metal-cofactor docking
  is approximate. **OpenMM** (`https://github.com/openmm/openmm`, pin version): short pocket MD →
  coordinating-atom RMSF / backbone RMSD. **Classical metal/heme force fields are approximate (fixed
  charges, no charge transfer / polarisation / spin)** — treat this MD as a weak, caveated proxy, and
  say so wherever you report it; for the metal centre itself, **spectroscopy** is the real test.

> All of the above are wrapped behind clean functions in `scripts/cofactor_tools.py` with a
> deterministic **mock** backend (no GPU) so the plumbing runs anywhere; the real backends are marked
> TODO. **Every mock number is SYNTHETIC — never report it as a real result, and never fabricate a
> spectrum.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → metalloprotein theory + cofactor/scheme choice; build_cofactor_spec() → coordinating-group spec; mock scaffold (D0)
02_generate         → cofactor site → scaffold (RFdiffusion2/Riff-Diff; A100) → cofactor-aware LigandMPNN (coordinating residues FIXED) → results CSV (D2)
03_filter_and_rank  → import filtering_pipeline as fp; build enzyme Designs; fp.run_pipeline(design_type="enzyme") + fp.report (D3 pt1)
04_validate         → coordination-geometry preservation rate + cofactor/scheme comparison + docking/site-pLDDT/MD figures + redox-tuning (D3 pt2)
05_validation_plan  → UV-vis Soret / EPR spectroscopic assay + cofactor titration + controls (apo, coordinating-residue→Ala) (D4/D5)
```

## 4. Filtering cutoffs for this design type (`design_type="enzyme"`)
From `shared/filtering_pipeline.py` `DEFAULT_CUTOFFS["enzyme"]` — reused for the cofactor site, where
`cat_geom` maps to **coordination**-geometry and `plddt_cat` to **site** confidence:
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 2.0 Å | self-consistency (designed vs predicted backbone) |
| pLDDT (global) | ≥ 85 | overall local confidence (NOT stability) |
| pLDDT (site) | ≥ 90 | stricter confidence *at the coordinating residues* — the part that matters |
| **coordination_geom_rmsd** (`cat_geom`) | **< 0.5 Å** | **the key metric:** predicted coordinating atoms vs the target scheme |

> Reminder: **no in-silico metric perfectly separates true from false hits** — and for a metalloprotein,
> *passing all four does not mean the cofactor is incorporated or functional.* Filters enrich; they do
> not guarantee. Report false positives and the hit rate honestly; **spectroscopy** is the real test.

## 5. Interpreting results
- A *promising* design: scRMSD ≤ 2 Å, global pLDDT ≥ 85, **site pLDDT ≥ 90, coordination-geometry RMSD
  < 0.5 Å**, the cofactor docks with the metal between the ligands, the pocket is MD-stable (caveated).
- A *suspicious* one: great global pLDDT but **high coordination-geometry RMSD** (folds well, ligands
  misplaced — the classic trap); or a pocket the cofactor won't fit; or LigandMPNN that quietly
  redesigned a coordinating residue (check the fixed-positions list).
- **Survival-at-each-layer** (from `fp.report`): read it as a funnel — N generated → N self-consistent →
  N with good coordination geometry → N MD-stable. The drop at the geometry layer is usually steepest.
- **Hit rate:** report N(pass all layers) / N(generated), per cofactor/scheme. Expect it to be low —
  that is the honest, expected outcome.
- **Coordination-geometry preservation rate:** the headline benchmark — fraction holding the motif < 0.5 Å.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies during scaffolding | T4 too small for 1000s of backbones | Reduce batch; run the small RFdiffusion demo on T4; move the real campaign to A100/HPC |
| RFdiffusion2 / Riff-Diff install fails | new tool, repo/release moved | **Verify the current public release** and pin a commit; log the URL; fall back to classic RFdiffusion motif mode |
| LigandMPNN redesigns a coordinating residue | fixed-positions list wrong/empty, or cofactor context not passed | Pass every coordinating residue in `--fixed_residues`; set `--ligand_mpnn_use_atom_context 1`; confirm numbering matches the backbone PDB |
| All designs fail coordination-geometry RMSD | motif not actually held by the scaffold, wrong atom mapping, or metal not placed | Re-check the cofactor-site export to the scaffolder; verify you compare the *same* coordinating atoms; place the metal/cofactor before scoring; loosen motif placement and regenerate |
| High global pLDDT but bad site | folds well but coordinating residues misplaced | Trust the **site** pLDDT + coordination-geometry RMSD, not the global pLDDT; filter on the site metrics |
| AF2 structure has no metal/cofactor | AF2 predicts the apo backbone | Expected — dock/superpose the cofactor to place the metal before measuring coordination geometry |
| Cofactor won't dock in the pocket | pocket too closed / wrong box / heme too big | Re-define the Vina box at the coordination site; check the pocket admits the macrocycle; revisit scaffold selection |
| MD blows up / metal drifts | classical metal/heme FF is approximate | Treat MD as a weak proxy only; note the caveat; don't over-interpret — spectroscopy decides |
| Mock numbers look like results | using the no-GPU demo path | They are **SYNTHETIC** by construction — switch to the real backends before reporting anything; never fabricate a spectrum |

## 7. Experimental validation reference (for the D4 plan)
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight; His-tag + IMAC; SEC polish. For
  heme, you may co-express/supplement the cofactor or reconstitute the apo protein with hemin in vitro;
  for [4Fe-4S], cluster assembly is **air-sensitive** (anaerobic reconstitution, e.g. an *isc/suf*
  system or chemical reconstitution under inert atmosphere).
- **Assay — SPECTROSCOPY (the readout that confirms incorporation + coordination):**
  - **Heme → UV-vis Soret band:** the intense Soret absorption (and Q-bands) report heme binding,
    coordination, and oxidation/spin state; run a **heme/cofactor titration** (add sub-stoichiometric to
    stoichiometric cofactor, follow the Soret to an endpoint) to confirm 1:1 binding. (Report
    positions/shifts qualitatively — **do not fabricate a wavelength**.)
  - **[4Fe-4S] / high-spin heme → EPR:** the EPR signature reports the cluster/metal oxidation and spin
    state; combine with a redox titration if you study electron transfer.
  - **Metal/cofactor quantification:** confirm stoichiometry (e.g. pyridine-hemochrome for heme, or
    ICP/colorimetric metal assays) — incorporation is uncertain and must be measured, not assumed.
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC → a UV-vis scan) → basic (Soret
  titration / EPR, DSF stability) → deep (redox potentiometry; crystal/cryo-EM of the holo site).
- **Controls (mandatory):**
  - **Positive:** a **natural reference** cofactor protein (e.g. a cytochrome / ferredoxin) — confirms
    the assay and the expected spectroscopic signature.
  - **Negative — coordinating-residue→Ala mutant:** mutate a coordinating ligand (e.g. an axial His →
    Ala); the cleanest negative — loss of the coordinated spectroscopic signature pins binding to that
    residue.
  - **Negative — apo protein:** the same protein with **no cofactor added** — the baseline spectrum to
    subtract; distinguishes specific coordination from non-specific cofactor sticking.
- **Redox-tuning / function-engineering (`[extension]`/`[stretch]`):** for a coordinating design, reason
  about (and plan to test) how the **axial-ligand identity** (His vs Met), **second-shell** residues,
  and **pocket polarity/hydrophobicity** shift the redox midpoint potential / O₂ affinity — the hard,
  valuable problem after coordination; use the same spectroscopic readout as the screen.

## 8. Responsible research
This is a **basic-science / industrial** metalloprotein with **low dual-use** risk: artificial
electron-transfer proteins, synthetic O₂ carriers, and artificial metalloenzymes have no toxin/pathogen
connection. See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: building and benchmarking de novo
cofactor-aware metalloprotein-design methodology. Out of scope: toxins, pathogen-enhancing functions,
or any design intended to cause harm. Synthesis screening (IGSC-member provider) + institutional
biosafety/ethics approval are required for any wet-lab work. If you adapt this template to a different
cofactor or function, re-check the new target against §7 with your advisor first.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: a designed-
metalloprotein paper (DeGrado/Baker), Dauparas 2024 (LigandMPNN), a cytochrome/ferredoxin reference,
Watson 2023 (RFdiffusion), Jumper 2021 (AF2), Trott & Olson 2010 (Vina), Eastman 2017 (OpenMM), plus a
coordination-chemistry reference and a UV-vis/EPR spectroscopy methods reference.
