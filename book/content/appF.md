# Appendix F · Glossary

Consolidated definitions of the key terms used across the book, in alphabetical
order. Terms span catalytic chemistry, computational design, and experimental
characterization. Where a term has a precise quantitative meaning, the definition
states it.

**Activation energy (Eₐ)** — The energy barrier a reaction must surmount to
proceed; in transition-state language the closely related quantity is ΔG‡.

**Active site** — The pocket of an enzyme where substrate binds and catalysis
occurs; in design, the region shaped around the theozyme.

**All-atom diffusion** — A generative diffusion approach that places all atoms
(including side chains and ligand atoms) rather than only backbone frames,
enabling direct reasoning about catalytic geometry (RFdiffusion3-class methods).

**AlphaFold3 (AF3)** — A 2024 structure-prediction model (Abramson et al.) that
predicts proteins together with ligands, nucleic acids, and ions; used in design
as a folding-based filter.

**Boltz-2** — A 2025 open-weights structure-prediction model in the AF3 family,
widely used as a free alternative for the folding filter.

**Catalytic triad** — A set of three cooperating residues (classically
Ser–His–Asp) that together perform nucleophilic catalysis, as in serine
hydrolases.

**CD (circular dichroism)** — A spectroscopic method that reports protein
secondary-structure content and, via thermal melts, fold stability.

**Dead mutant** — A designed enzyme with a catalytic residue mutated to alanine
(or similar) to abolish activity; the essential control proving observed activity
is catalytic rather than artifactual.

**De novo design** — Building a protein from a specification of desired function
rather than from a natural template; operationally, low structural and sequence
similarity to known proteins.

**Diffusion model** — A generative model that learns to reverse a gradual noising
process, sampling new structures by denoising from random noise (see Appendix C).

**Directed evolution** — Iterative mutation and selection/screening of a starting
protein to improve a property; a local optimizer, complementary to design.

**DBTL cycle** — Design–Build–Test–Learn, the iterative engineering loop that
organizes this book.

**ΔG‡ (Gibbs free energy of activation)** — The free-energy difference between the
ground state and the transition state; sets the reaction rate via Eyring's
equation. Lowering ΔG‡ is the essence of catalysis.

**EnzyGen2** — A 2026 generative model for enzyme sequence/structure design
co-conditioned on function.

**Equivariance** — A symmetry property: transforming a model's input (e.g.,
rotating a structure) transforms its output the same way; SE(3)-equivariance is
key to structure networks (see Appendix C).

**Eyring equation** — k = (k_B·T / h)·e^(−ΔG‡/RT), relating a rate constant to the
activation free energy.

**FASTA** — A plain-text format for sequences; the standard output of
inverse-folding tools and input for gene synthesis.

**Foldseek** — An ultrafast structure-search tool used to assess fold novelty
against the PDB/AlphaFold database.

**Functional-group conditioning** — Constraining a generative model to place
specified chemical groups (e.g., a nucleophile and a base) at defined relative
geometry, central to atom-level catalytic design.

**Hit rate** — The fraction of experimentally tested designs showing the intended
activity above background; typically 1–5% in de novo campaigns.

**IMAC (immobilized-metal affinity chromatography)** — A purification method using
a His-tag bound to a metal-charged resin; the first purification step for most
designs.

**Inverse folding** — Predicting a sequence that will fold to a given backbone;
the task solved by ProteinMPNN/LigandMPNN.

**k_cat (turnover number)** — The maximum number of substrate molecules converted
per active site per unit time at saturation (units s⁻¹).

**k_cat/K_M (catalytic efficiency)** — The second-order rate constant governing
catalysis at low substrate; the primary figure of merit for comparing enzymes
(units M⁻¹s⁻¹).

**K_M (Michaelis constant)** — The substrate concentration giving half-maximal
rate; an apparent measure of substrate affinity (units M).

**Kabsch algorithm** — The SVD-based method for the optimal rigid superposition of
two coordinate sets, used in RMSD computation.

**Kemp elimination** — A benchmark reaction (proton abstraction from a
benzisoxazole by a general base) widely used to test designed catalysts.

**LigandMPNN** — A ligand-aware extension of ProteinMPNN that designs sequences
accounting for a bound small molecule or cofactor.

**Michaelis–Menten kinetics** — The standard model v = V_max·[S]/(K_M + [S])
describing single-substrate enzyme rates.

**Motif scaffolding** — Generating a protein backbone that holds a fixed
functional motif (e.g., a theozyme) in place; a core RFdiffusion capability.

**nanoDSF** — Nano differential scanning fluorimetry; measures thermal unfolding
(T_m) from intrinsic tryptophan fluorescence with little sample.

**Novelty threshold** — An operational cutoff for calling a design novel,
commonly TM-score < 0.5 to every PDB entry plus low sequence identity.

**OpenMM** — A GPU-accelerated molecular-dynamics engine used to test
active-site/backbone stability of designs.

**Oxyanion hole** — A pocket of backbone amides or side chains that stabilizes the
developing negative charge of a tetrahedral oxyanion intermediate; essential to
hydrolase catalysis.

**PAE (predicted aligned error)** — A pairwise confidence metric from
AlphaFold-class models reporting expected positional error between residue pairs;
low inter-domain PAE indicates confident relative placement.

**pLDDT** — A per-residue confidence score (0–100) from AlphaFold-class models;
> 90 is very high confidence, < 50 likely disordered.

**Preorganization** — The principle (Warshel) that enzymes accelerate reactions
largely by pre-arranging a polar environment complementary to the transition
state, minimizing reorganization energy.

**Proficiency** — A measure of catalytic power, the rate enhancement relative to
the uncatalyzed reaction divided by K_M (effectively (k_cat/K_M)/k_uncat); some
enzymes exceed 10²³.

**ProteinMPNN** — A 2022 message-passing neural network (Dauparas et al.) for
inverse folding; the standard sequence-design tool.

**pTM (predicted TM-score)** — A global confidence metric estimating the TM-score
between the predicted and true structure; complements per-residue pLDDT.

**RFdiffusion** — A 2023 diffusion model (Watson et al.) generating protein
backbones, with motif-scaffolding conditioning.

**RFdiffusion2** — A 2026 successor (Ahern et al.) supporting atomized catalytic
motifs for enzyme design.

**RFdiffusion3** — A 2025 all-atom generative model (Butcher et al.) designing
backbone, side chains, and ligand context together.

**Riff-Diff** — A 2025 pipeline (Schnettler et al.) for building catalytic-motif
scaffolds, easing theozyme-to-backbone construction.

**RMSD (root-mean-square deviation)** — The root-mean-square distance between
matched atoms of two superposed structures; a measure of structural agreement
(see Appendix C).

**Rosetta** — The earlier physics-and-statistics protein-design suite behind the
first generation of designed enzymes.

**scRMSD (self-consistency RMSD)** — The Cα RMSD between a designed backbone and
the independently folded prediction of its designed sequence; the key in-silico
self-consistency filter (commonly pass < 2 Å).

**SE(3)** — The group of rigid motions in 3D (rotations SO(3) plus translations);
the symmetry respected by structure models.

**SEC (size-exclusion chromatography)** — Separates proteins by size; reports
oligomeric state and monodispersity.

**SEC-MALS** — SEC coupled to multi-angle light scattering; gives absolute molar
mass, confirming oligomeric state independent of shape.

**Self-consistency** — The agreement between a design's intended structure and the
structure predicted from its sequence; the basis of the scRMSD filter.

**Serine hydrolase** — An enzyme class using a serine nucleophile (typically in a
triad) to hydrolyze esters/amides; the model chemistry for much of this book.

**Theozyme** — A quantum-chemically idealized arrangement of catalytic functional
groups around a transition state; the chemical blueprint that design builds a
protein around.

**T_m (melting temperature)** — The temperature at which half a protein population
is unfolded; a primary stability metric from CD or nanoDSF.

**TM-score** — A length-normalized (0–1) measure of fold similarity; < 0.5
indicates different folds, used for novelty assessment.

**Transition state** — The highest-energy configuration along a reaction
coordinate; enzymes catalyze by binding it preferentially (Pauling).

**Transition-state analog** — A stable molecule mimicking the transition state's
geometry/charge; binds tightly and is used to probe and design active sites.
