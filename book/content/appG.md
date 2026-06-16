# Appendix G · Annotated Reading List

This list is tiered by level. **Foundational** papers build the chemical and
conceptual base — read these before generating anything. **Methods** papers are
the tools the labs use; read the one behind whatever you are running.
**Frontier (2025–2026)** papers are the current edge of catalytic de novo design;
read them to know what is now possible and what remains hard. Each entry has a
one-line annotation. Citations are inline as (Author, Year); consult the
publishers for full bibliographic details.

## G.1 Foundational

- **Pauling, L. (1948).** *Nature of forces between large molecules of biological
  interest.* — Origin of the transition-state-stabilization view of catalysis:
  enzymes bind the transition state more tightly than the substrate. Read first.

- **Wolfenden, R. & Snider, M. J. (2001).** *The depth of chemical time and the
  power of enzymes as catalysts.* — Quantifies how enormous uncatalyzed rate
  enhancements are (up to ~10²³), framing what a catalyst must achieve.

- **Warshel, A. et al. (preorganization, 1990s–2000s).** *Electrostatic basis for
  enzyme catalysis.* — Argues catalysis comes chiefly from a preorganized polar
  environment that lowers reorganization energy; the physical target of theozyme
  design.

- **Hilvert, D. and coworkers (Kemp eliminase evolution, 2000s–2010s).** — Shows
  that computationally designed catalysts, when finished by directed evolution,
  can approach natural efficiency; the canonical "design then evolve" story.

## G.2 Methods

- **Röthlisberger, D. et al. (2008).** *Kemp elimination catalysts by
  computational enzyme design.* **Nature.** — The landmark first wave: Rosetta
  theozyme-based design of active enzymes for a non-natural reaction. The origin
  of the modern pipeline.

- **Jumper, J. et al. (2021).** *Highly accurate protein structure prediction with
  AlphaFold.* **Nature.** — AlphaFold2; turned structure prediction into a
  reliable filter (pLDDT/PAE/pTM) that underpins self-consistency scoring.

- **Dauparas, J. et al. (2022).** *Robust deep learning–based protein sequence
  design using ProteinMPNN.* **Science.** — The standard inverse-folding tool;
  given a backbone, designs sequences that fold to it. Foundation of Labs 9/18.

- **Watson, J. L. et al. (2023).** *De novo design of protein structure and
  function with RFdiffusion.* **Nature.** — The diffusion model for backbone
  generation with motif scaffolding; the generative engine of Part III.

- **Abramson, J. et al. (2024).** *Accurate structure prediction of biomolecular
  interactions with AlphaFold3.* **Nature.** — Extends folding to proteins with
  ligands, ions, and nucleic acids; the modern filter for ligand-bound active
  sites.

- **Lisanza, S. L. et al. (2024).** *Generative models for protein structure and
  function* (and the atom-level design work of the same group). — Bridges
  backbone generation to function-aware, atom-level conditioning; the conceptual
  pivot toward catalysis-ready design.

## G.3 Frontier (2025–2026)

- **Schnettler, J. et al. — Riff-Diff (2025).** — A pipeline that assembles
  catalytic-motif scaffolds, easing the theozyme-to-backbone step for
  multi-residue active sites.

- **Lauko, A. et al. (2025).** *De novo design of serine hydrolases.* — Designed,
  experimentally validated serine hydrolases with genuine ester-hydrolysis
  turnover; a milestone for the book's model chemistry.

- **De novo metallohydrolase (2025), Nature.** — Designed metal-dependent
  hydrolase with a constructed divalent-metal active site; extends de novo design
  to metallochemistry.

- **Ahern, W. et al. — RFdiffusion2 (2026).** — Atomized-motif diffusion built for
  enzyme active sites, generating backbones around all-atom catalytic
  constellations.

- **Butcher, et al. — RFdiffusion3 (2025).** — All-atom generative model designing
  backbone, side chains, and ligand context jointly; the current top tier for
  catalytic geometry.

- **Boltz-2 (2025).** — Open-weights AF3-class structure predictor; the practical
  free folding filter for labs without AF3 access.

- **EnzyGen2 (2026).** — Function-conditioned generative model for enzyme
  sequence and structure, representing the move toward end-to-end functional
  conditioning.

::: {.reality data-title="Reality Check G.1 · The frontier moves faster than the press"}
Tool versions and benchmark numbers in §G.3 will date quickly. Treat these as the
2025–2026 state of the art, and always check the tool's current release notes and
the latest experimental-validation papers before trusting a hit rate quoted from
memory. The Foundational tier, by contrast, does not date — the chemistry is
permanent.
:::
