# Project 17 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track. Cite the
exact versions of any tool you actually run, and the source of any structure/sequence you use.

## Tier 1 — essential (read before Week 3)
- **Bennett et al. 2025, *Nature*** — RFantibody (RFdiffusion-Ab + ProteinMPNN). Read for: the de novo
  antibody/nanobody design protocol you run, and the **honest, LOW hit rates** that make display
  screening essential.
- **Abanades et al. 2023, *Communications Biology*** — ImmuneBuilder (incl. NanoBodyBuilder2). Read for:
  fast, antibody-aware VHH structure prediction and CDR-loop geometry (your `cdr_geom` check).
- **HER2/EGFR structural biology** — the trastuzumab–HER2 complex (Cho et al. 2003, *Nature*, PDB 1N8Z)
  and the EGFR ectodomain (Ogiso et al. 2002, *Cell*, PDB 1IVO). Read for: where the epitopes are, and
  what "overlapping vs non-overlapping with an approved mAb" means structurally.

## Tier 2 — build-time references
- **BoltzGen 2025** — nanobody/antibody generation. *VERIFY the current public release/preprint at
  generation time and pin it.* Read for: the `[extension]` head-to-head with RFantibody.
- **Raybould et al. 2019, *PNAS*** — Therapeutic Antibody Profiler (**TAP**). Read for: the five
  structure-based developability flags your `tap_score` heuristic imitates — and why you must use the
  real tool for any reportable developability claim.
- **Dauparas et al. 2022, *Science*** — ProteinMPNN. Read for: the sequence-design step inside
  RFantibody and the self-consistency idea behind scRMSD.
- **Evans et al. 2021 (AlphaFold-Multimer)** — Read for: `pae_interaction` as the key complex metric,
  and the limits of predicted interfaces (confidence ≠ binding).
- **Nanobody therapeutics review** — a nanobody-CAR or nanobody-**imaging** review (e.g., caplacizumab
  as the first approved nanobody; ⁶⁸Ga/⁸⁹Zr anti-HER2 VHH PET imaging). Read for: the downstream
  formats (VHH-Fc imaging, CAR binder) your D4 plan targets.

## Tier 3 — depth / frontier
- **CamSol (Sormanni et al. 2015, *JMB*)** and **humanness scoring (Hu-mAb / OASis / AbLang)** — the
  real solubility + humanness tools behind your `camsol_like` / `humanness` heuristics.
- **1–2 frontier de novo antibody papers** — recent work pushing de novo CDR/epitope-targeted design
  (e.g., follow-ups to RFantibody/BoltzGen, and de novo VHH or scFv binders to defined epitopes). Read
  for: where the field's hit rates and developability stand, and how display screening closes the loop.
- **Yeast/phage display methodology** — a single-domain-antibody display-selection reference. Read for:
  designing the pooled screen (FACS gating, stringency rounds, NGS enrichment) that turns a designed
  pool into real binders.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (RFantibody/BoltzGen, ImmuneBuilder,
  ColabFold), and the source of every structure/framework.
- Results/Discussion: compare your survival/hit rate to the literature's de novo antibody rates; be
  explicit that designs are **screening inputs**, and that developability heuristics ≠ validated tools.
- Data: cite the deposition for 1N8Z / 1IVO (and AFDB + UniProt for any model/sequence) with license.
