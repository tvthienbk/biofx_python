# Project 09 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. (All tool releases and accessions are
*candidates* — verify they still exist / are current at project start.)

## Tier 1 — essential (read before Week 3)
- **BoltzGen 2025 — peptide/macrocycle "anything" design** (*verify the citation + current public
  release*). *Why read this:* it is the primary generator you run for both linear-peptide and
  macrocycle designs; understand its protocols, inputs, and stated hit-rate caveats — and confirm the
  current public interface, which is moving.
- **Bryant et al. — EvoBind / EvoBind2 (cyclic & linear peptide binder design)**
  (`https://github.com/patrickbryant1/EvoBind`). *Why read this:* the MSA-free, AF2-objective peptide
  binder-design method you run as the second generator; how cyclic constraints enter the design loop.
- **Kussie et al. 1996, *Science* — MDM2–p53 crystal structure (1YCR)**. *Why read this:* the
  authoritative source for the p53-binding cleft and the Phe19/Trp23/Leu26 anchor residues you turn
  into your design cleft — verify the chain and numbering against the actual PDB.
- **A macrocycle / oral-peptide therapeutic review** (cell-penetrant and orally-available
  macrocyclic peptides; the "beyond rule-of-5" space). *Why read this:* to frame *why* a macrocycle
  could be an oral/cell-penetrant alternative to an antibody, and what chemistry (cyclization,
  N-methylation, D-amino acids) buys protease stability and permeability.

## Tier 2 — build-time references
- **Wohlwend et al. 2025 — Boltz-2** (`https://github.com/jwohlwend/boltz`). *Why read this:* where
  the structure prediction and the **affinity** signal come from; understand that the affinity head is
  a *relative ranking* signal for small inputs, **not** a measured K_D.
- **An RFpeptides / cyclic-peptide-design paper** (de novo cyclic peptide binders with backbone
  cyclization). *Why read this:* the structural logic of macrocycle design — ring closure, constrained
  backbones, and why cyclization changes both binding and developability.
- **Lo Conte / interface "hot-spot" review, or an MDM2-inhibitor medicinal-chemistry review**
  (Nutlin / stapled-peptide ATSP-7041 lineage). *Why read this:* the p53-mimetic pharmacophore and
  what "good" MDM2 cleft engagement looks like — context for your cleft-overlap analysis.
- **A solid-phase peptide synthesis (SPPS) + protease-stability/permeability methods reference**.
  *Why read this:* to write a credible, controlled peptide validation plan in D4 (SPPS, serum/protease
  stability, PAMPA/Caco-2 permeability) — peptides are **not** validated like E. coli mini-binders.

## Tier 3 — depth / frontier
- **Verma / Bhardwaj — de novo macrocycle / hyperstable cyclic-peptide design (Baker lab)**.
  *Why read this:* the foundational computational case that constrained macrocycles can be designed to
  be hyperstable — the structural ambition behind your cyclic arm.
- **Pacesa et al. 2025 — BindCraft**. *Why read this:* the mini-protein binder method behind your
  **peptide-vs-protein modality foil**; understand the other modality you compare against and its
  honest hit-rate caveats.
- **A frontier peptide-design paper** (e.g., recent high-throughput experimental validation of de
  novo peptide/macrocycle binders, or a foundation-model peptide-design paper). *Why read this:*
  current state of the art on what fraction of in-silico peptide hits actually bind / are stable, and
  how the field validates.
- **A second frontier paper on stapling / D-amino-acid / N-methylation peptide engineering**.
  *Why read this:* the chemistry for the D-amino-acid / stapling stretch in notebook 05 — how
  modifications trade synthesis complexity for protease stability and permeability.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BoltzGen, EvoBind2, Boltz-2,
  ColabFold/AF2; BindCraft/RFdiffusion if you ran the mini-protein foil).
- Results/Discussion: compare your hit rates and the **linear-vs-cyclic** and **peptide-vs-protein**
  outcomes to what the literature reports, and explain differences (target, cleft, scale, cutoffs,
  chemistry). Discuss that predicted affinity is unreliable for short peptides.
- Data: cite the MDM2–p53 structure paper (Kussie 1996) + PDB accession + access date.
- Always state that a passing design is a **hypothesis** until synthesis + binding + stability assays;
  never imply measured binding, and **never fabricate a K_D** (the Boltz-2 score is a relative rank).
