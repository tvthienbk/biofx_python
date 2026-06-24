# Project 21 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. Serine hydrolases use the **classic Ser-His-Asp
triad + oxyanion hole** — the industrial workhorse chemistry (synthesis, kinetic resolution,
detergents). The headline this project reproduces is the **de novo design of efficient serine
hydrolases** (Lauko 2025), and these papers are its spine.

## Tier 1 — essential (read before Week 3)
- **Lauko et al. 2025, *Science*** — **de novo serine hydrolases** (efficient designed hydrolases).
  *Why read this:* the result this project reproduces — *designing* (not borrowing) a Ser-His-Asp
  triad + oxyanion hole from scratch and getting real, catalytically efficient hydrolases. It defines
  the theozyme→scaffold→LigandMPNN→geometry pattern your whole campaign runs, and sets the honest
  expectation (most designs are inactive; a screen finds the few that work).
- **Schnettler et al. 2025, *Nature*** — **Riff-Diff** (theozyme → enzyme scaffolding).
  *Why read this:* the current frontier for scaffolding a *defined* active-site motif; your P2
  scaffolding step is this method (or RFdiffusion2) — it builds backbones that present your triad +
  oxyanion hole. *Verify the current release/repo at generation time.*
- **A classic alpha/beta-hydrolase mechanism reference** (a lipase / cutinase / acetylcholinesterase
  active-site & mechanism paper or review).
  *Why read this:* the canonical Ser-His-Asp charge-relay + oxyanion-hole mechanism, the tetrahedral
  intermediate, and the acyl-enzyme — exactly the chemistry your theozyme encodes, and the geometry
  `data/inputs/theozyme_def.txt` asks you to construct (including the easily-forgotten oxyanion hole).

## Tier 2 — build-time references
- **Dauparas et al. 2024 — LigandMPNN** — ligand/metal-aware sequence design.
  *Why read this:* it is *why* you can fix the catalytic triad + oxyanion-hole residues while
  redesigning the rest — the core of your P2 sequence-design step; vanilla ProteinMPNN is not
  ligand-aware and would design away your active site.
- **Dauparas et al. 2025 — RFdiffusion2** — all-atom motif/active-site scaffolding.
  *Why read this:* the other scaffolding option you benchmark against Riff-Diff; all-atom motif
  scaffolding that places the catalytic atoms directly. *Verify the current release at generation time.*
- **Jumper et al. 2021, *Nature*** — AlphaFold2.
  *Why read this:* you use AF2 to check the **catalytic-triad geometry** (and per-residue pLDDT at the
  active site); read it for what pLDDT/PAE do — and do **not** — mean (confidence is not stability,
  and a confident fold can still hold the triad in the wrong place).
- **Trott & Olson 2010 — AutoDock Vina.**
  *Why read this:* your **pocket-accessibility** check and the **acyl-chain substrate-scope scan**;
  read it for what a docking score is (a fit/orientation sanity check) and is **not** (an affinity or
  an activity measurement).
- **Eastman et al. 2017 — OpenMM.**
  *Why read this:* the engine for the short **active-site-stability MD** (catalytic-atom RMSF /
  backbone RMSD); read it for system setup and the limits of classical force fields — a triad that
  drifts apart under MD will not catalyse even if the static prediction looks perfect.

## Tier 3 — depth / MSc track
- **A frontier de-novo-enzyme paper beyond hydrolases** (e.g. Yeh et al. 2023 de novo luciferases,
  *Nature*; a RFdiffusion2/Riff-Diff enzyme application; or a designed retro-aldolase / Kemp lineage).
  *Why read this:* shows the same theozyme→scaffold→sequence→geometry-filter machinery generalising
  across reactions — and the recurring, honest "geometry ≠ activity, low hit rate, screening required"
  message that frames your D★ assay plan.
- **A serine-hydrolase enantioselectivity / kinetic-resolution reference** (a lipase/esterase
  enantioselectivity or chiral-ester kinetic-resolution paper).
  *Why read this:* the basis for the **enantioselectivity `[stretch]`** — how an asymmetric pocket
  discriminates the two faces of a chiral ester, and how E-value / ee is measured; informs the
  green-chemistry kinetic-resolution framing.
- **A directed-evolution context reference** (Arnold's directed-evolution review / Nobel lecture, or a
  designed-then-evolved hydrolase lineage).
  *Why read this:* frames why a kinetic screen + (often) an evolution loop are required after
  computational design — the honest hit-rate reality behind your kinetic-assay plan and any hit follow-up.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion2/Riff-Diff/LigandMPNN/AF2/
  Vina/OpenMM), and the source of every theozyme geometry value.
- Results/Discussion: compare your **catalytic-geometry preservation rate**, **pocket-accessibility**,
  and **substrate-scope** results to what Lauko 2025 and the scaffolding papers claim, and be explicit
  that in-silico geometry ≠ measured activity — a pNP-ester kinetic assay with the catalytic-Ser→Ala
  dead-mutant control is required (cite the realistic, low hit rates).
- Data: cite the source paper + table/PDB + license for every reference item you use as a control.
