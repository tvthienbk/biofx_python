# Project 19 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. PET hydrolases use the **classic
serine-hydrolase Ser-His-Asp triad + oxyanion hole** — so the interesting problem (and these papers'
spine) is **thermostability for industrial PET degradation**, plus the de novo design machinery.

## Tier 1 — essential (read before Week 3)
- **Austin et al. 2018, *PNAS*** — **IsPETase** structure + engineering.
  *Why read this:* it defines the PET-hydrolase active site you are grafting — the Ser-His-Asp triad
  and the oxyanion hole — and shows that wild-type IsPETase is only modestly stable, motivating the
  whole thermostability emphasis.
- **Tournier et al. 2020, *Nature*** — **engineered, thermostabilised LCC** for PET depolymerisation.
  *Why read this:* the landmark demonstration that **thermostability is the bottleneck** — engineering
  the leaf-branch compost cutinase to work near PET's glass transition (~65-72 °C) is what made
  enzymatic PET recycling industrially viable; it frames your D★ thermostability ranking.
- **Lauko et al. 2025, *Science*** — **de novo serine hydrolases** (efficient designed hydrolases).
  *Why read this:* the current frontier for *designing* (not borrowing) a Ser-His-Asp triad +
  oxyanion hole from scratch — the theozyme→scaffold→LigandMPNN→geometry pattern your campaign runs.

## Tier 2 — build-time references
- **Schnettler et al. 2025, *Nature*** — **Riff-Diff** (theozyme → enzyme scaffolding).
  *Why read this:* the scaffolding method for your P2 step (or RFdiffusion2) — it builds backbones
  that present a defined active-site motif. *Verify the current release/repo at generation time.*
- **Dauparas et al. 2024 — LigandMPNN** — ligand/metal-aware sequence design.
  *Why read this:* it is *why* you can fix the catalytic triad + oxyanion-hole residues while
  redesigning the rest — the core of your P2 sequence-design step; vanilla ProteinMPNN is not
  ligand-aware. (RFdiffusion2, Dauparas 2025, is the other scaffolding option to verify.)
- **Jumper et al. 2021, *Nature*** — AlphaFold2.
  *Why read this:* you use AF2 to check the **catalytic-triad geometry** (and per-residue pLDDT at
  the active site); read it for what pLDDT/PAE do — and do **not** — mean.
- **Eastman et al. 2017 — OpenMM.**
  *Why read this:* the engine for the **MD-based thermostability ranking** (RMSF + melting-proxy) —
  this project's headline metric beyond geometry; read it for system setup and the limits of
  classical force fields (an MD proxy is *not* a measured Tm).
- **A theozyme / QM transition-state design reference (Houk or Baker lab)** — e.g. the
  quantum-mechanics-based active-site (theozyme) design methodology.
  *Why read this:* it is the recipe for placing functional groups around the **transition state /
  tetrahedral intermediate** (not the ground state) — exactly what `data/inputs/theozyme_def.txt`
  asks you to construct, including the easily-forgotten oxyanion hole.
- **Trott & Olson 2010 — AutoDock Vina.**
  *Why read this:* your PET-mimic-ester pocket-accessibility check; read it for what a docking score
  is (a fit/orientation sanity check) and is **not** (an affinity or an activity measurement).

## Tier 3 — depth / MSc track
- **A protein-thermostabilisation reference (e.g. the DuraPETase / thermostable-IsPETase engineering
  work, or a FoldX/Rosetta ΔΔG / consensus-design stabilisation review).**
  *Why read this:* the toolkit and the honest limits of *predicting* thermostability — directly
  informs your MD melting-proxy ranking and the surface-redesign-for-solubility `[stretch]`, and the
  thermostability↔activity trade-off.
- **A PET-hydrolase mechanism / depolymerisation-assay reference (Yoshida et al. 2016, *Science*,
  the IsPETase discovery; or a PET-film/HPLC depolymerisation-kinetics paper).**
  *Why read this:* the biology of PET hydrolysis (MHET/TPA products) and how depolymerisation is
  actually measured (PET-film/HPLC vs the pNP-ester proxy) — the backbone of your D4 activity plan.
- **A broader de-novo-enzyme / directed-evolution reference (e.g. Arnold's directed-evolution context,
  or a designed-then-evolved hydrolase lineage).**
  *Why read this:* frames why a kinetic screen + (often) an evolution loop are required after
  computational design — the honest "geometry ≠ activity" message and the surface/DE `[stretch]`.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion2/Riff-Diff/LigandMPNN/
  AF2/Vina/OpenMM), and the source of every theozyme geometry value.
- Results/Discussion: compare your **catalytic-geometry preservation rate** and **thermostability
  ranking** to what the frontier papers claim, contrast the **engineered-natural vs fully de novo**
  tracks, and be explicit that in-silico geometry + an MD proxy ≠ measured activity or Tm — activity
  (pNP-ester / PET-film) and DSF assays are required (cite the realistic, low hit rates).
- Data: cite the source paper + table/PDB + license for every reference item you use as a control.
