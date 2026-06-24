# Project 22 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase. This is
the most expensive and most frontier project in the course: you are searching for **one sequence
that folds to TWO defined backbones** and toggles between them on a trigger. Almost everything below
exists to keep that hard problem honest.

## 1. Background theory
A conformational switch is **one amino-acid sequence compatible with two distinct backbones** —
state A and state B — that interconverts when a stimulus (pH, ligand, light, temperature) fires.
Natural switches are everywhere (adenylate kinase open/closed, calmodulin, kinases); de novo ones
are rare. The Baker lab's **LOCKR** (Langan 2019) showed switchable de novo proteins are possible,
but a sequence that fits state A well usually fits state B badly, and our structure predictors may
only ever return *one* of the two states. The metrics you live and die by:

- **Per-state scRMSD** (Å): for EACH state, predict the shared sequence and measure Cα-RMSD to that
  state's *designed* backbone. **< 2 Å for BOTH A and B** is the self-consistency bar for a switch.
  What it means: the sequence is *foldable* to that geometry. What it does **not** mean: that the
  protein actually toggles, that state B is populated, or that the trigger works.
- **Per-state pLDDT** (0–100): local confidence of each refold. High pLDDT ≠ stability, and ≠ "this
  state exists" — it is the predictor's confidence in *local* geometry of the one model it returned.
- **State energy gap** (relative units — **NOT kcal/mol**): a teaching-grade proxy for how far apart
  the two states sit in relative energy. Computed from per-state fit (lower scRMSD + higher pLDDT ⇒
  lower relative energy; `multistate_tools.energy_gap`). A switch needs the gap **inside a band**
  (`SWITCH_GAP_MIN`..`SWITCH_GAP_MAX`): too LARGE and the high-energy state is never populated (no
  switch); too SMALL and the two states are indistinct (no defined OFF/ON). What it does **not**
  mean: a real ΔΔG. For that you need physics (FoldX/Rosetta) or MD free-energy methods.
- **Per-state MPNN score**: multi-state ProteinMPNN's own confidence that the shared sequence fits
  each backbone (lower = better). A good switch fits **both**; record A and B separately to see the
  trade-off.

Why this is hard and what realistic success looks like: **multi-state design is VERY hard.** A
single sequence rarely satisfies two states well; one state usually folds better than the other; and
**AF2 typically returns a single dominant state, so confirming the switch in silico is genuinely
difficult.** A realistic outcome is a *low hit rate* (a few percent pass both states; fewer still
land inside the switchable band) plus a sharp account of *why*. Success = a rigorously characterized
switch **hypothesis** with a real validation plan — **not** a guaranteed working switch. You are
graded on rigor, reasoning, and reproducibility, not on whether the protein works.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion (via ColabDesign) — the TWO state backbones
- **What it does / where it fits:** generative backbone design. You run it **twice** to produce two
  related-but-distinct backbones (state A and state B) that one sequence must adopt. Two routes:
  (a) generate A, then generate B as a conformational variant of A (partial diffusion / hinge
  re-fold), or (b) build de novo backbones matching a known two-state template pair (LOCKR
  latch/cage, an open/closed hinge).
- **Install / pin:** `RosettaCommons/RFdiffusion` + `sokrypton/ColabDesign`. **Pin the commit** and
  verify it with the version-verify cell in `02_generate`.
- **Key parameters:** `contigmap.contigs` (length per state), `inference.num_designs`,
  `diffuser.T ~ 50`, `inference.output_prefix=results/two_state/state_{A,B}`, partial-diffusion
  noise for state B.
- **Compute:** **two** backbone-generation runs. A100/HPC for the campaign; a T4 runs only a tiny
  fallback (short backbones, few designs).

### ProteinMPNN in multi-state / tied mode — the shared sequence
- **What it does / where it fits:** sequence design. In **multi-state (tied) mode** the SAME residue
  identities are tied across both backbones and one sequence is optimized for the (e.g. averaged)
  likelihood under BOTH states at once. This is the heart of the project.
- **Install / pin:** `dauparas/ProteinMPNN` (or via ColabDesign). Pin the commit.
- **Key parameters:** `tied_positions` spanning the two states, `--num_seq_per_target ~8–many`,
  `--sampling_temp 0.1–0.2`. Record the **per-state score** for A and B separately.
- **Compute:** modest vs RFdiffusion/AF2, but you sample many sequences — batch it.

### ColabFold (AlphaFold2) / ESMFold — predict BOTH states from one sequence
- **What it does / where it fits:** predict the shared sequence and compare to EACH state's backbone
  (`scrmsd_to_state`). ESMFold (MSA-free) for fast triage; AF2 for trusted picks. **Where possible,
  bias prediction toward each state** (templates / initial guess) to test whether both states are
  genuinely accessible to one sequence.
- **Key parameters:** `num_recycles` (raise for hard cases); AF2 template/initial-guess to bias
  toward a state; ESMFold `chunk_size` for memory.
- **CAVEAT (central):** AF2 predicts a single dominant state and **may not capture both** — this is
  the honest limitation of in-silico multi-state validation. Report the unbiased prediction *and*
  the state-biased ones, and never claim a switch from a single unbiased model.
- **Compute:** ESMFold triage on a T4; AF2 ×2-per-design prefers A100.

### OpenMM — transition-plausibility MD `[extension]`
- **What it does / where it fits:** a short MD (10–50 ns) on a top pick to check the predicted states
  stay put and whether A↔B is even plausible. **Not** a free-energy calculation; a sanity probe.
- **Install / pin:** `openmm/openmm` (pin a release) + a recent force field. Verify with the
  version-verify cell.
- **Compute:** GPU strongly preferred; keep runs short. This is an extension, not a core requirement.

### Geometry + viz
TM-align / Foldseek for inter-state RMSD and novelty; Biopython for Cα-RMSD and parsing; py3Dmol to
eyeball both states side by side; pandas/matplotlib for the results table and figures.

> **LOCKR is the conceptual reference, not a tool you install.** Use it to reason about how a latch
> and cage encode two states in one chain.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback) + version-verify
01_define_explore   → multi-state theory; define states+trigger; metrics table; mock hello-world (one seq → two states + gap)  (D0)
02_generate         → generate TWO backbones (RFdiffusion ×2) + multi-state MPNN shared sequence → results/multistate_designs.csv  (mock; version-verify)  (D2)
03_filter_and_rank  → shared filtering_pipeline on BOTH states (two fp.Design per design, design_type="monomer")  (D3 pt1)
04_validate         → AF2 predicts BOTH states from one sequence + energy-gap + single- vs multi-state benchmark + transition figures  (D3 pt2)
05_validation_plan  → state-change read-out plan (FRET/protease/SAXS) + paired controls + LOV light-switch stretch  (D4/D5)
```
For Project 22 the standard slots map to: *02 = the multi-state design campaign* (two backbones +
shared sequence), *04 = the two-state validation + energy-gap study*, *05 = the wet-lab read-out plan*.

## 4. Filtering cutoffs for this design type
A switch must pass the **monomer foldability bar for A AND B** *and* land inside the energy-gap band.
Apply `filtering_pipeline` with `design_type="monomer"` **twice** — once per state — and intersect.

| Metric | Starting cutoff | Applied to | Why |
|--------|-----------------|------------|-----|
| per-state scRMSD | < 2.0 Å | A **and** B | self-consistency of each state (designed vs predicted) |
| per-state pLDDT | > 85 (mean) | A **and** B | local confidence (NOT stability) |
| energy gap | within `[SWITCH_GAP_MIN, SWITCH_GAP_MAX]` | the pair | close enough to switch, distinct enough for OFF/ON |
| inter-state RMSD (TM-align) | states must be *distinct* | A vs B | if A≈B there is no switch |

> Reminder: passing the per-state bars proves **foldability of two shapes**, not that the protein
> toggles. The energy gap is a teaching proxy, **not** a ΔΔG. Filters enrich; they do not guarantee.
> Report N(passes A) / N(passes B) / N(passes BOTH) / N(switchable) — the honest hit-rate ladder.

## 5. Interpreting results
- A *promising* switch candidate: scRMSD < 2 Å for **both** states, high per-state pLDDT, states
  geometrically distinct, gap inside the band, **and** the two states reproduce when prediction is
  biased toward each. That last clause is what separates a real candidate from an AF2 artifact.
- *Suspicious:* one state passes and the other fails (common — that is the multi-state difficulty);
  high pLDDT but the predictor only ever returns state A regardless of bias (state B may not exist);
  a gap that looks switchable only because AF2 never modeled state B.
- **Single- vs multi-state benchmark (the result):** design each backbone alone with normal MPNN,
  then show those single-state sequences **fail the other state**. The contrast — multi-state
  sequences fit both, single-state ones don't — is your headline finding.
- **Energy-gap caveat (say it explicitly):** the gap is a relative-units proxy from prediction fit,
  not a free energy. A "switchable" flag is a hypothesis to test in the wet lab, not a measurement.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Two RFdiffusion runs blow the T4 budget | two-backbone generation is heavy | move to A100/HPC; on T4 use short backbones + few designs (fallback only); log the GPU |
| Multi-state MPNN yields nothing fitting both | the states are too different / tying too strict | relax `tied_positions`, raise temp slightly, or make states more similar; expect low yield regardless |
| One state always passes, the other always fails | the sequence is fitting the easier (designed-for) state | this is the core difficulty — report it; try seeding MPNN from both states symmetrically |
| AF2 returns the same state for both predictions | AF2 collapses to one dominant state | bias toward each state (templates/initial guess); report that B may be inaccessible — do NOT claim a switch |
| Energy gap looks "switchable" but B never modeled | gap proxy fed by a state AF2 didn't actually produce | invalidate the candidate; the gap is meaningless without two real predictions |
| scRMSD looks random | residue numbering / chain mismatch in Cα-RMSD | align by sequence first; check chain IDs; use Biopython Superimposer correctly |
| ColabDesign/ProteinMPNN install fails | upstream repo moved | use the pinned commit; rerun the version-verify cell; log it |
| OpenMM transition MD explodes | bad starting geometry / missing FF terms | minimize + equilibrate first; check protonation at the trigger pH; keep the run short |

## 7. Experimental validation reference (for the D4 read-out plan)
The deliverable is a **state-change read-out** that actually proves a switch, with paired controls:
- **FRET** — donor/acceptor pair reporting the A↔B distance change on trigger.
- **Protease accessibility** — a site exposed in one state, buried in the other (limited proteolysis).
- **SAXS** — solution shape change on trigger (Rg / pair-distribution shift).
- Expression: typically *E. coli* BL21(DE3), 16–18 °C overnight; purify (IMAC → SEC).
- **Controls (mandatory):** a positive (a design/natural protein known to switch), a single-state
  **"locked" negative** (a sequence that should NOT switch — your always-OFF/always-ON control), and
  an unrelated control. Specify the trigger titration (pH series / ligand dose / dark-vs-lit for LOV),
  a timeline, and a costed reagent list.
- *(Stretch)* LOV-domain integration so the trigger is light; add dark/lit validation states.

## 8. Responsible research
This project designs **conformational switches for smart biomaterials, allosteric sensors, and
protein logic gates** — basic-science / biomaterials framing with a **low dual-use surface**: the
designs have no targeted binding or toxic function; they change their *own* shape on a stimulus. See
`MASTER_BLUEPRINT.md §7`. Out of scope: enhancing pathogen transmissibility/virulence, toxins, or
any design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening
provider; wet-lab work requires institutional biosafety/ethics approval. **If a switch is later
coupled to a functional payload (a binder, an enzyme, a delivery module), re-evaluate it under
`MASTER_BLUEPRINT.md §7` before proceeding** — the dual-use surface changes the moment a switch gates
a function.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool versions you actually run: Langan 2019 (LOCKR),
a hinge/two-state design paper (e.g. Praetorius 2023), a multi-state ProteinMPNN/ensemble reference,
Watson 2023 (RFdiffusion), Jumper 2021 (AF2), an allosteric-design review, Eastman 2017 (OpenMM),
plus the source paper for every reference structure in `data/README.md`.
