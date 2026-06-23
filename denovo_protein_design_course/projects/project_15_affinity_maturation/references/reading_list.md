# Project 15 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track. Cite the
exact versions of any tool you actually run, and the source of the structure + the KD you use.

## Tier 1 — essential (read before Week 3)
- **Meier et al. 2021, *NeurIPS*** — **ESM-1v** (language models enable zero-shot prediction of mutation
  effects). Read for: the masked-marginal Δ-log-likelihood you use to **rank** single CDR mutations, and
  why a single-sequence PLM score is a ranking signal — **not** an affinity or a ΔΔG.
- **Olsen et al. 2022, *Bioinformatics Advances*** — **AbLang** (antibody-specific language model). Read
  for: why an antibody-trained LM captures "natural-looking" CDR sequences better than a general PLM,
  and how to use it as a developability/expressibility prior. *VERIFY whether AbLang2 is the current
  release and pin it.*
- **Dunbar et al. 2014, *Nucleic Acids Research*** — **SAbDab** (the Structural Antibody Database). Read
  for: how to find an antibody-antigen complex **with a measured KD** linked to the literature, and how
  to verify the structure + the affinity before you build on them.

## Tier 2 — build-time references
- **Dauparas et al. 2022, *Science*** — **ProteinMPNN**. Read for: the CDR-redesign step (framework
  FIXED via a design mask) and the self-consistency idea behind scRMSD/pose maintenance.
- **Raybould et al. 2019, *PNAS*** — **Therapeutic Antibody Profiler (TAP)**. Read for: the five
  structure-based developability flags your liability scan imitates, the chemical liabilities (NG/DG,
  Met-ox, free Cys) you must avoid introducing into CDRs — and why you must use the real tool for any
  reportable developability claim.
- **Evans et al. 2021 (AlphaFold-Multimer)** — Read for: `pae_interaction` as the interface-pose metric,
  and the limits of predicted interfaces (pose confidence ≠ binding ≠ affinity).
- **An antibody affinity-maturation review** — a review of computational + experimental antibody affinity
  maturation / lead optimization (e.g., in-silico mutation scanning, deep mutational scanning, the role
  of display + SPR). Read for: where computational maturation sits, and the honest expectation that
  **most predicted improvers do not validate.**

## Tier 3 — depth / frontier
- **CamSol (Sormanni et al. 2015, *JMB*)** and **deamidation/isomerization prediction** — the real
  solubility + chemical-liability tools behind your developability heuristics. Read for: what a *real*
  developability call requires (structure-aware, not just sequence motifs).
- **1–2 frontier antibody-ML papers** — recent work on ML-guided antibody optimization (e.g., language-
  model-guided affinity maturation, structure-based ΔΔG predictors for antibodies, or generative CDR
  design as a maturation prior). Read for: where the field's success rates stand and how computational
  ranking is combined with experimental screening to close the loop.
- **SPR/BLI kinetics methodology + DSF for antibodies** — a kinetics/stability methods reference. Read
  for: designing the SPR plan (monovalent Fab to avoid avidity artifacts, concentration series, 1:1 fit)
  and the DSF stability read-out that pairs with it.

## How to use these in your report
- Methods: cite the tool papers **and the versions/commits you ran** (ESM-1v, AbLang/AbLang2, ProteinMPNN,
  ColabFold), and the source of the structure **and the measured KD** for your complex.
- Results/Discussion: be explicit that ESM-1v/AbLang are **ranking** signals (not affinity), that the
  filter enforces **pose maintenance** (not tighter binding), and that **most predicted improvers won't
  validate** — report the expected hit rate, not a cherry. Developability heuristics ≠ validated tools.
- Data: cite the deposition for your complex (and Dunbar 2014 for SAbDab) plus the primary paper that
  reports the KD, with license.
