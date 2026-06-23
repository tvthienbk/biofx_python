# Project 18 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. The Kemp elimination is *the* model reaction
for de novo enzyme design — these papers are the field's spine.

## Tier 1 — essential (read before Week 3)
- **Röthlisberger et al. 2008, *Nature*** — the **first computational Kemp eliminases** (KE07 ...).
  *Why read this:* it defines the theozyme idea for this exact reaction and sets the honest
  baseline — modest activity, low hit rate, big improvement only after directed evolution.
- **Schnettler et al. 2025, *Nature*** — **Riff-Diff** (theozyme → enzyme scaffolding).
  *Why read this:* the current frontier for scaffolding a defined active site; your P2 scaffolding
  step is this method (or RFdiffusion2). *Verify the current release/repo at generation time.*
- **Dauparas et al. 2025 — RFdiffusion2** — all-atom motif/active-site scaffolding.
  *Why read this:* the other scaffolding option you benchmark; reaches near-natural rates *without*
  directed evolution — the methods claim your project tests. *Verify the current release at gen time.*

## Tier 2 — build-time references
- **Dauparas et al. 2024 — LigandMPNN** — ligand/metal-aware sequence design.
  *Why read this:* it is *why* you can fix the catalytic residues while redesigning the rest — the
  core of your P2 sequence-design step; vanilla ProteinMPNN is not ligand-aware.
- **Jumper et al. 2021, *Nature*** — AlphaFold2.
  *Why read this:* you use AF2 to check the **catalytic-residue geometry** (and per-residue pLDDT at
  the active site); read it for what pLDDT/PAE do — and do **not** — mean.
- **A theozyme / QM transition-state design reference (Houk or Baker lab)** — e.g. the
  quantum-mechanics-based active-site (theozyme) design methodology.
  *Why read this:* it is the recipe for placing functional groups around the **transition state**
  (not the ground state) — exactly what `data/inputs/theozyme_def.txt` asks you to construct.
- **Trott & Olson 2010 — AutoDock Vina.**
  *Why read this:* your substrate-fit check; read it for what a docking score is (a fit/orientation
  sanity check) and is **not** (an affinity or an activity measurement).
- **Eastman et al. 2017 — OpenMM.**
  *Why read this:* the engine for the short active-site-stability MD; read it for system setup and
  the limits of classical force fields (relevant if you extend to metalloenzymes in Projects 20/24).

## Tier 3 — depth / MSc track
- **HG3 / HG3.17 directed-evolution lineage (Privett/Blomberg et al.; Hong et al.)** — a designed
  Kemp eliminase taken to near-natural efficiency by evolution.
  *Why read this:* the honest gap between *designed* and *efficient* — motivates your D★
  directed-evolution plan and the "geometry ≠ activity" message.
- **Arnold (directed evolution context; e.g. the Nobel lecture / a directed-evolution review).**
  *Why read this:* frames why a kinetic screen + an evolution loop are usually required after
  computational design; informs the `[stretch]` directed-evolution plan.
- **A de novo serine-hydrolase / broader de-novo-enzyme paper (e.g. Lauko et al. 2025, *Science*).**
  *Why read this:* shows the theozyme→scaffold→LigandMPNN→geometry-filter pattern generalising to
  another reaction — the same family template Projects 19/21 reuse.

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion2/Riff-Diff/LigandMPNN/
  AF2/Vina/OpenMM), and the source of every theozyme geometry value.
- Results/Discussion: compare your **catalytic-geometry preservation rate** and scaffolding-method
  results to what the frontier papers claim, and be explicit that in-silico geometry ≠ measured
  activity — a kinetic assay is required (cite the realistic, low hit rates).
- Data: cite the source paper + table/PDB + license for every reference item you use as a control.
