# Project 24 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. De novo **cofactor-binding metalloprotein**
design is a long-standing grand challenge — these papers span the design lineage (maquettes → ML),
the central tool (LigandMPNN), the reference cofactor proteins, and the spectroscopy you will plan.

## Tier 1 — essential (read before Week 3)
- **A designed metalloprotein / de novo heme-protein paper (DeGrado lab "maquettes" or a Baker-lab
  de novo cofactor-binder).**
  *Why read this:* it defines the problem — building a coordination pocket for heme/metal from
  scratch (e.g. bis-His heme in a four-helix bundle) — and sets the honest baseline: coordination is
  achievable, but tuning function (redox potential, O₂ affinity) is the hard part.
- **Dauparas et al. 2024 — LigandMPNN** — ligand/metal-aware sequence design.
  *Why read this:* it is *why* you can fix the coordinating residues while redesigning the rest **and**
  let the model "see" the cofactor — the core of your P2 sequence-design step. Vanilla ProteinMPNN is
  cofactor-blind; this is the central tool of the project.
- **A cytochrome / ferredoxin reference (a b-type cytochrome or a ferredoxin structure paper).**
  *Why read this:* the natural template you read the **target coordination geometry** off — the
  bis-His heme of a b-type cytochrome, or the 4-Cys [4Fe-4S] cubane of a ferredoxin — and your
  positive control. *Verify the exact PDB entry on RCSB (see `data/README.md`).*

## Tier 2 — build-time references
- **Watson et al. 2023, *Nature* — RFdiffusion.**
  *Why read this:* the backbone-generation method (and the basis of RFdiffusion2 / motif scaffolding)
  you use to build pockets that present the coordination motif — your P2 scaffolding step. *Verify the
  current RFdiffusion2/Riff-Diff release at generation time.*
- **Jumper et al. 2021, *Nature* — AlphaFold2.**
  *Why read this:* you use AF2 to check the **coordinating-residue geometry** and per-residue pLDDT at
  the site; read it for what pLDDT/PAE do — and do **not** — mean, and note that **AF2 does not place
  the metal/cofactor** (it predicts the apo backbone).
- **A cofactor / coordination-chemistry reference (a bioinorganic-chemistry text or review on metal
  coordination in proteins).**
  *Why read this:* the recipe for the coordination geometry you encode — metal-ligand distances,
  coordination number/polyhedron, oxidation/spin state and how it changes the geometry — exactly what
  `data/inputs/cofactor_site_def.txt` asks you to construct.
- **A UV-vis / EPR spectroscopy methods reference (a heme UV-vis or an EPR-of-metalloproteins methods
  paper/chapter).**
  *Why read this:* the readout for your D★ assay plan — the **Soret band** (heme UV-vis) and **EPR**
  (Fe-S clusters / high-spin heme), and a cofactor/metal **titration** — read it for what each
  signature reports about coordination and oxidation/spin state, and its controls.

## Tier 3 — depth / MSc track
- **A frontier ML-metalloprotein-design paper (e.g. a recent de novo metal/cofactor-binder or a
  metal-conditioned generative-design paper).**
  *Why read this:* the current frontier your project tests — generating coordination pockets with ML
  and the honest gap between *coordination geometry* and *confirmed function*.
- **An artificial-metalloenzyme / electron-transfer-protein review (the broader design landscape).**
  *Why read this:* frames the real-world payoff — artificial electron-transfer proteins, synthetic O₂
  carriers, artificial metalloenzymes — and why **redox-tuning** (the `[extension]`) is the hard,
  valuable problem after you achieve coordination.
- **Trott & Olson 2010 — AutoDock Vina** *and* **Eastman et al. 2017 — OpenMM.**
  *Why read this:* your cofactor-fit check (Vina; read it for what a docking score is — a fit/
  orientation sanity check — and is **not**) and your short pocket-stability MD (OpenMM; read it for
  system setup and the **classical-metal-FF limits**, which are a real caveat for a metalloprotein).

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion2/Riff-Diff/LigandMPNN/AF2/
  Vina/OpenMM), and the source structure for every coordination-geometry value.
- Results/Discussion: compare your **coordination-geometry preservation rate** and scheme/cofactor
  results to what the design papers claim, and be explicit that in-silico geometry **≠ cofactor
  incorporation ≠ function** — **spectroscopy** is required (cite realistic, low hit rates).
- Data: cite the source paper + table/PDB + license for every reference item you use as a control.
