# Project 13 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Silva et al. 2019, *Nature* — "De novo design of potent and selective mimics of IL-2 and IL-15"
  (Neo-2/15)** — the landmark of this project. *Why read this:* it *is* the paradigm — a hyperstable de
  novo mini-protein that signals through IL-2Rβ/γc but has **no IL-2Rα site**, giving βγ-biased agonism
  with reduced toxicity. Your selectivity goal and stability framing come from here.
- **Watson et al. 2023, *Nature* — RFdiffusion** — the diffusion backbone generator (binder mode is your
  primary paradigm). *Why read this:* how diffusion-then-sequence design steers a mini-protein onto a
  chosen receptor surface, and how to think about hotspots/contigs across two receptor chains.
- **Pacesa et al. 2025 — BindCraft** — the one-shot binder-design alternative/foil. *Why read this:* the
  AF2-in-the-loop paradigm and its hit-rate caveats, useful as a second campaign route.
- **An IL-2 / IL-2R structural-biology paper** (e.g., the IL-2–IL-2Rαβγc quaternary complex behind 2B5I,
  Wang/Stauber/Garcia). *Why read this:* to read off the per-subunit contact residues that become your
  hotspots, and to understand which chain (α) you must *spare* to be selective.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science* — ProteinMPNN** — sequence design for the RFdiffusion backbones.
  *Why read this:* the self-consistency idea and the temperature/diversity knobs you tune.
- **Evans et al. 2021 — AlphaFold-Multimer** — complex prediction. *Why read this:* where
  `pae_interaction` (your key metric) comes from and how to read interface confidence — here you run it
  **once per subunit** to build the selectivity profile.
- **A cytokine-signaling (JAK/STAT) review** — how βγ receptor dimerization juxtaposes JAK1/JAK3 and
  fires STAT5. *Why read this:* this is *why* binding ≠ signaling, and why a cell pSTAT5 assay (not just
  SPR) is the decisive validation — agonism requires the right dimerizing geometry, not just affinity.
- **An SPR/BLI methods reference** (a surface-plasmon-resonance or bio-layer-interferometry protocol
  review). *Why read this:* to write a credible, controlled **per-subunit** affinity-measurement plan in
  D4 (K_D to IL-2Rα, IL-2Rβ, γc separately).

## Tier 3 — depth / frontier
- **The original IL-2 quaternary-complex structure paper** (the deposition behind 2B5I). *Why read this:*
  the authoritative source for the interface residues you turn into per-subunit hotspots — verify the
  numbering against the actual PDB and confirm which chain is which.
- **A frontier de novo cytokine-mimetic / agonist paper** (e.g., a more recent de novo IL-2/IL-7/IL-15
  partial-agonist or biased-agonist design, or a de novo receptor-agonist from the Baker lab). *Why read
  this:* current state of the art on tuned-selectivity agonists and how the field validates signaling.
- **A second frontier cytokine-engineering paper** (e.g., an engineered IL-2 "muteins"/orthogonal-IL-2
  or partial-agonist study). *Why read this:* context for the selectivity↔potency trade-off and how
  partial vs full agonism is measured (EC50, Emax) — never fabricate these numbers.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (RFdiffusion, ProteinMPNN,
  BindCraft, ColabFold/AF2-Multimer; Boltz-2 if used).
- Results/Discussion: compare your hit rate, **selectivity profile**, and stability comparison to what
  the literature (Neo-2/15 and follow-ups) reports, and explain differences (target, hotspots, scale,
  cutoffs).
- Data: cite the IL-2/IL-2R structure paper + PDB accession + access date for the complex you used.
- Always state that a passing design is a **hypothesis** — selective in silico is **not** a confirmed
  agonist until per-subunit SPR **and** a cell pSTAT5 assay; never imply measured binding or signaling.
