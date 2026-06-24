# Project 20 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. This project designs a **de novo Zn
metalloenzyme** (a carbonic-anhydrase-style CO2-hydration site) — these papers are its spine:
carbonic-anhydrase mechanism, the GRACE de-novo-CA paradigm, metal-aware sequence design, and the
honest limits of modelling a metal site.

## Tier 1 — essential (read before Week 3)
- **Hu et al. 2024 — GRACE (de novo carbonic-anhydrase-style metalloenzymes).**
  *Why read this:* the paradigm this whole project reproduces — defining a Zn active site, generating
  a **large pool (~10k)**, and screening to functional CA-style designs. Sets the honest expectation:
  diversity before filtering, then a real assay. *Verify the exact citation/venue when you cite it.*
- **Dauparas et al. 2024 — LigandMPNN — ligand/metal-aware sequence design.**
  *Why read this:* it is **why** you can fix the three His ligands AND design the rest of the protein
  with the **Zn in context** — the core of your P2 sequence-design step. Vanilla ProteinMPNN is
  metal-blind; this is the difference your notebook-04 benchmark measures.
- **A carbonic-anhydrase structure / mechanism paper** (e.g. a human CA II structural study; read
  alongside the candidate PDBs 2CAB / 3KS3 — verify on RCSB).
  *Why read this:* the recipe for the **Zn-His3-OH** site — the Zn lowering the water pKa to ~7, the
  hydroxide nucleophile attacking CO2, the proton-shuttle His — exactly what `metal_site_def.txt`
  asks you to construct (read the real Zn-N distances / N-Zn-N angles off the structure).

## Tier 2 — build-time references
- **A de novo metalloprotein design review (DeGrado lab).**
  *Why read this:* the long history and the hard parts of designing metal sites de novo — primary vs
  second-shell ligands, geometry vs function, and why **metal incorporation is uncertain**. Frames
  your ICP/PAR metal-incorporation check and the apo control.
- **Schnettler et al. 2025 (Riff-Diff) or Lauko et al. 2025 (Science, de novo enzymes).**
  *Why read this:* the theozyme->scaffold->LigandMPNN->geometry-filter pattern (the enzyme-family
  template Projects 18/19/21 share) and current scaffolding for a defined active site — your P2
  scaffolding step. *Verify the current Riff-Diff / RFdiffusion2 release at generation time.*
- **Jumper et al. 2021, *Nature* — AlphaFold2.**
  *Why read this:* you use AF2 for active-site **pLDDT** and to get the His3 geometry — but **AF2
  does not place the metal**, so read it for what pLDDT/PAE do and do **not** mean, and plan how you
  add/score the Zn for the metal-ligand-geometry metric.
- **A metal-force-field / MD-limitations reference** (bonded vs cationic-dummy metal models; the
  limits of classical fixed-charge FFs for transition metals; OpenMM, Eastman et al. 2017, for the
  engine).
  *Why read this:* your short metal-site MD is only a **weak, caveated** stability proxy — classical
  FFs cannot model charge transfer / polarisation / the hydroxide pKa. Read this so you state the
  caveat correctly and never present MD as evidence of catalysis.

## Tier 3 — depth / MSc track
- **A frontier de novo metalloenzyme / artificial-metalloenzyme paper** (e.g. designed metal sites
  beyond CA: hydrolytic or redox metalloenzymes).
  *Why read this:* shows where metal-aware design is going and what "functional" really requires
  beyond geometry — motivates honest reporting and the assay plan.
- **An alternative-metal / metal-substitution study in carbonic anhydrase** (e.g. Co(II)-substituted
  CA spectroscopy/activity).
  *Why read this:* the basis of the `[stretch]` **Co-substitution** test — Co(II) is active and gives
  a spectroscopic handle the spectroscopically-silent Zn(II) does not.
- **Dauparas et al. 2025 — RFdiffusion2** (all-atom motif/active-site scaffolding).
  *Why read this:* the all-atom scaffolding option you can benchmark against Riff-Diff for placing
  the Zn + His3 motif cleanly. *Verify the current release at generation time.*

## How to use these in your report
- Methods: cite the tool papers **and the versions you ran** (RFdiffusion2/Riff-Diff/LigandMPNN/
  ProteinMPNN/AF2/CLEAN/Vina/OpenMM), the source of every metal-site geometry value, and your
  metal-site MD model (bonded/dummy) with its parameter source.
- Results/Discussion: compare your **metal-ligand-geometry preservation rate**, your
  **LigandMPNN-vs-ProteinMPNN** result, and your **pool-size-vs-hit-rate** curve to what GRACE
  reports — and be explicit that geometry != metal incorporation != activity (only ICP + a kinetic
  assay decide).
- Data: cite the source paper + table/PDB + license for every reference item (CA structures, GRACE
  supplementary) you use as a control.
