# Project 12 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run. This project has **two** literatures: binder
design (the recognition element) and protein switches / split-reporters (the transduction element).

## Tier 1 — essential (read before Week 3)
- **Langan et al. 2019, *Nature* — LOCKR (de novo protein switches)** — the cage+latch+key switch
  paradigm. *Why read this:* this is the conformational-switch architecture you can borrow/adapt to
  turn binding into a controllable ON/OFF, and the source of the latch/key design logic.
- **Quijano-Rubio et al. 2021, *Nature* — de novo designed protein biosensors** — couples binders to
  LOCKR-style switches with luminescent readouts. *Why read this:* the closest published analog of this
  whole project (binder → switch → signal) and a sober view of dynamic range and what makes a sensor work.
- **Dixon et al. 2016 — NanoBiT split-luciferase** — the LgBiT/SmBiT complementation reporter.
  *Why read this:* the split-reporter readout you may use; how reconstitution → luminescence and the
  background/leak considerations that set dynamic range.
- **Pacesa et al. 2025 — BindCraft** — the primary one-shot binder-design method here. *Why read this:*
  the BindCraft paradigm you run for the recognition element, with its hit-rate caveats.

## Tier 2 — build-time references
- **Watson et al. 2023, *Nature* — RFdiffusion** — the diffusion backbone generator (binder mode +
  scaffold generation). *Why read this:* binder paradigm #2 **and** how to generate a switch scaffold
  to host a split-reporter.
- **Dauparas et al. 2022, *Science* — ProteinMPNN** — sequence design for the diffused backbones and
  for redesigning the switch latch/interface. *Why read this:* the self-consistency idea and the
  temperature/diversity knobs you tune.
- **Evans et al. 2021 — AlphaFold-Multimer** — complex prediction. *Why read this:* where
  `pae_interaction` (your key binder metric) comes from, and the basis for **two-state** modeling of
  the ON/OFF conformations.
- **Cao et al. 2022, *Nature* — target-structure-only mini-binders** — de novo binders from just the
  target surface. *Why read this:* the conceptual foundation for designing a minibinder to your chosen
  analyte epitope, and realistic hit rates.

## Tier 3 — depth / frontier
- **The structural-biology source for your chosen analyte** (the deposition behind the PDB you use).
  *Why read this:* the authoritative source for the epitope residues you turn into hotspots — verify the
  numbering against the actual PDB; pick an epitope that doesn't disrupt the marker's diagnostic utility.
- **A frontier protein-switch / sensor paper** (e.g. a recent allosteric biosensor, a de novo
  signaling switch, or a colocalization-dependent reporter). *Why read this:* current state of the art
  on coupling binding to signal and on tuning dynamic range vs affinity.
- **A second frontier switch/biosensor paper** (e.g. CID/CAR-style or two-component sensors, or a
  point-of-care diagnostic platform). *Why read this:* context for the affinity-vs-dynamic-range
  trade-off, the LOD/assay-noise relationship, and multiplexing.
- **An assay/dose-response methods reference** (luminescence or FRET dose-response + LOD estimation).
  *Why read this:* to write a credible, controlled functional-readout plan in D4 (fit, blank, LOD).

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (BindCraft, RFdiffusion,
  ProteinMPNN, ColabFold/AF2-Multimer) plus the **switch reference** you adapted (Langan 2019 /
  Quijano-Rubio 2021 / NanoBiT).
- Results/Discussion: compare your binder hit rates and your switch-architecture / dynamic-range
  outcomes to what the biosensor literature reports, and explain differences.
- Data: cite the analyte structure paper + PDB accession + access date.
- Always state that a passing binder is a **hypothesis**, a modeled dynamic range is **not** a measured
  signal, and there is **no LOD** until a real dose-response is fit; never imply a working sensor.
