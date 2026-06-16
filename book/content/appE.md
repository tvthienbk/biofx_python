# Appendix E · Master Capstone Project

This appendix specifies a complete, gradeable de novo enzyme design campaign that
exercises the entire book. A student (or small team) takes a target reaction from
a written specification through to a defensible 96-design order list and an
experimental plan with controls and budget. The project is organized into eight
phases mapped to the book's chapters, each with concrete deliverables and a
**go/no-go gate** that mirrors how a real campaign decides whether to continue or
redesign. A grading rubric follows in §E.3. The capstone is designed to be run as
the *design* (in-silico) campaign in full; the wet-lab phases are delivered as a
plan unless the course has bench access.

## E.1 Project Overview and Target

Choose one reaction from the approved list (or propose one, instructor approval
required): an **ester hydrolysis** (serine-hydrolase-style triad; the best-trodden
path and recommended default), a **Kemp elimination** (single general base;
classic benchmark), or a **metal-dependent hydrolysis** (a divalent-metal site;
ambitious). Each implies a different theozyme and a different control suite, which
is the point: the campaign's downstream choices must follow from the chemistry
chosen at the start.

The deliverable of the whole project is a campaign dossier: the signed spec, the
theozyme, the generated and filtered designs, the MD evidence, the final 96-design
order list with a diversity justification, and a costed experimental plan. It must
be reproducible — anyone with the repository and the manifest should be able to
re-derive the shortlist.

## E.2 Phases, Deliverables, and Gates

::: {.method data-title="Method E.1 · The eight-phase campaign"}
Run the phases in order. Do not begin a phase until the prior gate is passed, and
record every gate decision (and its evidence) in the design notebook.
:::

**Phase 1 — Specification (Chapters 1–2, 13).**
Write the design spec: the exact reaction (substrate, product, bond made/broken),
the mechanistic hypothesis, the target operating conditions (pH, temperature,
solvent), and the **predefined success criteria** with numeric go/no-go thresholds
(e.g., "soluble expression, T_m > 45 °C, measurable k_cat/K_M above the
no-enzyme control by ≥ 10×"). Identify the controls now, not later.
*Deliverable:* a signed one-page spec.
*Gate 1:* the reaction has a defensible mechanism and a checkable success metric.
Fail → revise scope.

**Phase 2 — Transition state and theozyme (Chapters 2, 14).**
Build a transition-state model and place the minimal catalytic functional groups
around it (the **theozyme**): for ester hydrolysis, the nucleophile–base–acid
triad plus an oxyanion hole; specify ideal distances and angles with tolerances.
*Deliverable:* theozyme PDB + a geometry table (atom pairs, target distances ±
tolerance).
*Gate 2:* the theozyme's geometry is chemically reasonable and internally
consistent (no clashes; angles within catalytic ranges). Fail → re-place groups.

**Phase 3 — Backbone generation (Chapters 10, 15, 16).**
Scaffold the theozyme into protein backbones with RFdiffusion2/3 (atomized motif
with ligand context for the metal/ligand cases; classic motif scaffolding for the
triad). Generate broadly — hundreds to a few thousand backbones.
*Deliverable:* a backbone set (PDB) + generation parameters.
*Gate 3:* ≥ ~50 backbones place the motif within tolerance and pass a clash check.
Fail → loosen length constraints / regenerate.

**Phase 4 — Sequence design (Chapters 9, 18).**
Design sequences with LigandMPNN (ligand-aware), several sequences per backbone,
sampling temperature tuned for diversity vs. confidence.
*Deliverable:* sequences (FASTA) keyed to backbones in the manifest.
*Gate 4:* sequences generated for all surviving backbones; no obvious pathologies
(e.g., long hydrophobic surface stretches).

**Phase 5 — In-silico filtering (Chapters 8, 17, 19).**
Fold each sequence (AlphaFold3/Boltz-2), compute pLDDT/PAE/pTM and **scRMSD**, and
score active-site geometry conformance against the theozyme. Apply the thresholds
set in the spec. Inspect survivors visually (Appendix B).
*Deliverable:* a ranked filter table with pass/fail per metric.
*Gate 5:* a healthy survivor pool (target ≥ 200 candidates passing folding +
scRMSD < 2 Å + geometry conformance). Fail → return to Phase 3 with adjusted
hotspots.

**Phase 6 — Molecular dynamics triage (Chapter 20).**
Run short explicit-solvent MD (e.g., 10–50 ns) on the top candidates with the
ligand bound; measure active-site RMSF and whether the catalytic geometry
survives solvation and thermal motion.
*Deliverable:* an MD stability report per top candidate.
*Gate 6:* candidates whose catalytic constellation stays within tolerance over the
trajectory. Fail-many → suspect over-fit static geometry; revisit Phase 2/3.

**Phase 7 — Selection of 96 (Chapter 21).**
From survivors, select 96 designs for synthesis. Balance predicted quality with
**diversity** (cluster by backbone topology and sequence; do not pick 96
near-identical winners). Reserve plate positions for controls.
*Deliverable:* the final order list (FASTA + manifest) with a diversity figure and
a one-paragraph selection rationale.
*Gate 7:* 96 designs span ≥ several distinct topologies and include the planned
controls. Fail → rebalance.

**Phase 8 — Experimental plan, controls, and budget (Chapters 19, 22–24).**
Specify the build/test plan: gene synthesis format, expression host and vector,
purification (IMAC → SEC), fold/stability QC (CD, nanoDSF/T_m, SEC-MALS), and the
kinetic assay with its full control suite. Cost it.
*Deliverable:* a costed plan with a control table and a timeline.
*Gate 8 (final):* the plan would convince a skeptical reviewer that a positive
result could not be an artifact (controls present) and is affordable.

### Required controls (Phase 8)

| Control | Purpose |
|---|---|
| No-enzyme (buffer only) | Establishes background (non-enzymatic) rate |
| Catalytically dead mutant | Nucleophile→Ala of each hit; activity must drop to background |
| Known natural enzyme | Positive control / scale reference for the assay |
| Empty-vector lysate | Rules out host-derived background activity |
| Substrate stability | Confirms product signal is enzyme-dependent, not decomposition |

### Indicative budget (96-design campaign)

| Item | Indicative cost |
|---|---|
| Gene synthesis (96 genes, cloning-ready) | US$3,000–9,000 |
| Expression + purification consumables (96, small scale) | US$1,500–3,000 |
| Assay reagents (substrate, buffers, plates) | US$500–1,500 |
| Biophysics (CD/nanoDSF/SEC-MALS time) | US$500–1,500 |
| GPU compute (design + folding + MD) | US$100–400 (cloud) or HPC allocation |
| Structure determination (best hit, optional) | US$2,000–10,000+ |
| **Total (without structure)** | **≈ US$6,000–15,000** |

::: {.reality data-title="Reality Check E.1 · Expect most of the 96 to be silent"}
A favorable chemistry (ester hydrolysis) may yield a handful of active hits among
96; an ambitious one (novel metallohydrolase) may yield zero on the first round
and require a redesign loop. Grade the *process* — spec, theozyme, filtering
discipline, controls — not the hit count, exactly as the field judges a campaign.
:::

## E.3 Grading Rubric

Weights sum to 100. For each criterion, score on a 4/3/2/1 scale mapped to the
descriptors below, then weight.

| Criterion | Weight | Excellent (4) | Adequate (2) | Poor (1) |
|---|---:|---|---|---|
| Specification & success criteria | 10% | Clear reaction + mechanism; numeric, predefined go/no-go thresholds and controls named upfront | Reaction stated; vague or post-hoc success metric | No checkable success criterion |
| Theozyme quality | 15% | Chemically sound geometry with justified distances/angles and tolerances; oxyanion hole/base correct | Plausible but loosely justified geometry | Geometry implausible or clashing |
| Backbone generation | 10% | Broad generation; motif held within tolerance; parameters justified | Some motif drift; thin survivor pool | Motif not recovered; parameters undocumented |
| Sequence design | 10% | Ligand-aware, diverse, sensible temperature choice | Sequences generated but undiscussed | Pathological sequences; ligand ignored |
| In-silico filtering | 20% | Correct metrics (pLDDT/PAE/scRMSD/geometry), thresholds applied as pre-set, visual inspection documented | Metrics computed but thresholds shifted post-hoc | Filters misapplied or misinterpreted |
| MD triage | 10% | Active-site stability assessed over trajectory; failures interpreted | MD run but analysis shallow | No MD or uninterpreted |
| Selection of 96 + diversity | 10% | Quality–diversity balance justified with clustering; controls placed | 96 picked, diversity unaddressed | Near-duplicate picks; no controls |
| Experimental plan & controls | 10% | Complete control suite (incl. dead mutant), realistic budget/timeline | Plan present, gaps in controls | No dead-mutant control; unrealistic |
| Reproducibility & notebook | 5% | Manifest + environment committed; campaign re-derivable | Partial provenance | Not reproducible |

**Suggested grade bands (weighted average of 4/3/2/1 scores):** ≥ 3.5 = A,
3.0–3.49 = B+, 2.5–2.99 = B, 2.0–2.49 = C, < 2.0 = revise and resubmit.

::: {.redflags data-title="Red Flags E.1 · Capstone failure modes that lose points"}
- Choosing filter thresholds *after* seeing which designs pass (Phase 5/Gate 5).
- Reporting a hit "rate" without controls — especially without a dead mutant.
- Selecting 96 near-identical designs and calling it a campaign.
- A theozyme with correct atoms but uncatalytic geometry (right pieces, wrong
  distances/angles).
- A dossier that cannot be re-run from the committed manifest.
:::
