# Project 16 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track. Cite the
exact versions of any tool you actually run, and the source of any antibody/germline sequence you use.

## Tier 1 — essential (read before Week 3)
- **Prihoda et al. 2022, *mAbs*** — **BioPhi / Hu-mAb / OASis** (deep-learning humanization + OASis
  humanness). Read for: the humanness scoring (OASis) and automated humanization you build the campaign
  around, and the modern benchmark for humanness↔stability.
- **Olsen et al. 2022, *Bioinformatics/Protein Science*** — **AbLang** (antibody language model). Read for:
  per-residue humanness and **restoration** of framework residues — your humanness-aware grafting helper.
- **Gao et al. 2013, *Immunome Research*** — **T20** humanness score. Read for: the curated-human-database
  approach to humanness and how to interpret a humanness number (and its limits).
- **A CDR-grafting / resurfacing humanization review** (e.g., Safdari 2013, *Biotechnol. Genet. Eng. Rev.*,
  or Almagro & Fransson 2008). Read for: the strategies (CDR grafting vs resurfacing vs germline-content),
  the **Vernier zone**, and why grafting needs **back-mutations**.

## Tier 2 — build-time references
- **Ruffolo et al. 2023, *Nature Communications*** — **IgFold**. Read for: fast, antibody-aware Fv
  structure prediction — the 3-D model your ΔΔG (FoldX/Rosetta) runs on.
- **Abanades et al. 2023, *Communications Biology*** — **ImmuneBuilder** (Fv / NanoBodyBuilder2). Read for:
  an alternative Fv modeller and a cheap self-consistency check.
- **Dauparas et al. 2022, *Science*** — **ProteinMPNN**. Read for: the `[extension]` framework-position
  optimization (CDRs fixed) and the self-consistency idea behind scRMSD.
- **A FoldX or Rosetta ΔΔG reference** — Schymkowitz et al. 2005 (*Nucleic Acids Res.*, FoldX) **or** Park
  et al. 2016 (*JCTC*, Rosetta cartesian_ddg). Read for: how ΔΔG is computed, its error bars, and why your
  in-repo `ddg_predict` is only a teaching proxy.
- **Foote & Winter 1992, *J. Mol. Biol.*** — the **Vernier zone**. Read for: which framework residues
  support the CDR loops and are the prime back-mutation candidates.

## Tier 3 — depth / frontier
- **Marks et al. 2021, *Bioinformatics* (Hu-mAb)** and **Olsen et al. 2022 (OAS / Observed Antibody
  Space)** — the human-repertoire resources behind humanness scoring. Read for: how "humanness" is defined
  against real human antibody repertoires, and the germline-content view.
- **1–2 frontier antibody-humanization-ML papers** — recent deep-learning humanization (e.g., BioPhi
  follow-ups, Sapiens, or generative/germline-content humanization that jointly optimizes humanness and
  stability/affinity). Read for: where the field's humanness↔stability trade-off stands and how ML closes
  the loop.
- **An immunogenicity / ADA review** (e.g., a clinical-immunogenicity or T-cell-epitope-prediction review).
  Read for: why humanness is a *correlate, not a guarantee* of low ADA — the honesty your report needs.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits/hosts you ran** (AbLang, OASis/Hu-mAb via
  BioPhi, T20 server, IgFold/ImmuneBuilder, FoldX/Rosetta), and the source of your antibody + germline FRs.
- Results/Discussion: report the **humanness↔stability trade-off** with real tools; be explicit that a
  humanness score is a **hypothesis** for low ADA (not a proof), that grafting commonly loses
  affinity/stability, and that the ΔΔG proxy in the repo is **not** a measured Tm.
- Data: cite the publication for your non-human antibody (with license) and the IMGT/OAS germline source
  (Lefranc et al. for IMGT; Olsen et al. for OAS), and record the terms.
