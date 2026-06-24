# Project 16 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
**The design problem.** You are **humanizing** an existing **non-human (murine / chimeric) therapeutic
antibody**: rewriting its **framework** regions to look like a **human germline** antibody (to reduce
anti-drug-antibody / ADA immunogenicity) while keeping its **CDR loops** (which confer binding). The CDRs
are FIXED; the framework is the design variable. The classic move is **CDR grafting**: transplant the
non-human CDR1/CDR2/CDR3 onto a human germline framework (FR1..FR4). Two alternatives: **resurfacing**
(mutate only surface-exposed framework residues to human identity) and **germline-content optimization**
(push toward the nearest human germline, scored by humanness tools).

**Key concepts you must understand:**
- **VH/VL & CDR structure** — each variable domain is FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4. The CDRs form the
  paratope; the frameworks are the scaffold. Humanize a Fab by humanizing **both** VH and VL.
- **Humanness** — how closely the sequence resembles human-antibody repertoires. Scored by **OASis**
  (9-mer peptides vs the Observed Antibody Space), **Hu-mAb** (germline-content ML classifier), **T20**
  (curated human-antibody DB), and **AbLang** (antibody language model; also proposes residue
  restorations). Higher humanness ⇒ lower expected ADA — **a correlate, not a guarantee.**
- **The Vernier zone** — framework residues that pack against and *position* the CDR loops (Foote & Winter
  1992). A graft that replaces a Vernier residue with the human one can shift the loop ⇒ lost
  affinity/stability. These are the prime **back-mutation** candidates: restore the parental residue.
- **The humanness ↔ stability trade-off (the heart of this project)** — more framework humanization ⇒ more
  mutations ⇒ usually higher destabilization (**ΔΔG > 0**). Resurfacing changes fewer residues (lower ΔΔG,
  less human); grafting changes the whole framework (more human, higher ΔΔG, needs back-mutations).
- **ΔΔG (stability cost)** — the predicted change in folding free energy of the variant vs the parental.
  Computed by **FoldX** (BuildModel / PositionScan) or **Rosetta** (cartesian_ddg) on a 3-D **Fv model**
  (from IgFold / ImmuneBuilder). Convention: **ΔΔG > 0 = destabilizing.** It is **not** a measured Tm.
- **Self-consistency (scRMSD) & pLDDT** — fold an Fv model of the variant, measure designed-vs-predicted
  backbone RMSD and confidence. The antibody bar is more lenient (≤ 3.0 Å) because CDR loops are flexible.

**Why this is hard / realistic success.** Humanization is a **trade-off, not a free lunch.** Grafting
commonly loses some affinity/stability; the campaign's job is to *quantify* that and to find the
**Vernier back-mutations** (and/or resurfacing) that recover it at minimal humanness cost. Success = a
rigorous, honestly-reported trade-off analysis + a sound validation plan — **not** "a humanized antibody".
A humanness score is a hypothesis until ELISA/SPR/DSF confirm retained binding and stability.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### AbLang (antibody language model)
- **What it does / where it fits:** scores per-residue "humanness" and can **restore** non-human framework
  residues toward human ones — used in `02_generate` for humanness-aware grafting and back-mutation.
- **Install:** `https://github.com/oxpig/AbLang` (pip / repo). **Verify it still exists and pin the
  commit** before the course starts.
- **Key parameters:** chain (heavy/light), restoration threshold.
- **Compute:** light — **T4 fine** (CPU often fine).
- **Typical call (schematic):**
  ```python
  import ablang
  heavy = ablang.pretrained("heavy"); heavy.freeze()
  # score / restore framework residues toward human (see the repo README; pin the commit)
  ```

### OASis / Hu-mAb (humanness) — via BioPhi (VERIFY the current public release/host)
- **What they do / where they fit:** the **reportable** humanness scores. OASis scores 9-mer peptides vs
  the OAS human repertoires; Hu-mAb is a germline-content classifier. Used in `02`/`04` for the real
  humanness axis of the trade-off.
- **Install:** BioPhi `https://github.com/Merck/BioPhi` bundles OASis/Hu-mAb. **VERIFY the current public
  release/host** at course start (web app vs package) and pin it.
- **Compute:** light — **T4 / CPU fine.**

### T20 humanness (Gao 2013)
- **What it does:** scores against a curated human-antibody database (a separate web server).
- **Install:** **VERIFY the T20 server is still public** at course start; record the URL + access date.
- **Compute:** server-side.

### IgFold / ImmuneBuilder (Fv structure for ΔΔG)
- **What it does / where it fits:** fast, antibody-aware **Fv structure prediction** (no MSA) — the 3-D
  model FoldX/Rosetta need to compute ΔΔG, and a cheap self-consistency check.
- **Install:** `https://github.com/oxpig/ImmuneBuilder` (pin the commit).
- **Compute:** cheap — **T4 fine.**

### FoldX / Rosetta (ΔΔG stability proxy)
- **What they do / where they fit:** compute the **ΔΔG** of each framework mutation on the Fv model — the
  stability cost of humanization (the y-axis of the trade-off).
- **Install:** FoldX (academic license — register) or Rosetta (`cartesian_ddg`; academic license). **These
  are licensed; document which you used.** The in-repo `ddg_predict` is a **teaching heuristic**, not these.
- **Compute:** FoldX BuildModel is fast (CPU); Rosetta cartesian_ddg is heavier but T4/CPU feasible at this
  scale.

### ProteinMPNN (framework optimization) `[extension]`
- **What it does / where it fits:** redesign/optimize **framework** positions (CDRs fixed) toward stability
  while staying human — the germline-content `[extension]`.
- **Install:** `https://github.com/dauparas/ProteinMPNN` (pin the commit). **CPU / T4 fine.**

> **Teaching heuristics vs real tools.** `scripts/humanization_tools.py` provides `humanness_score()` and
> `ddg_predict()` as **clearly-labelled teaching heuristics** so the pipeline runs with no installs and no
> GPU. They teach the *axes* (what humanness and ΔΔG measure), **not the verdict.** Swap in the real tools
> above for any reportable humanness or ΔΔG claim. **NEVER report a heuristic number as a real result.**

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback; T4 is all this project needs)
01_define_explore   → humanization strategies; pick antibody + germline frameworks; metrics table; mock hello-world (graft + Vernier back-mutations)
02_generate         → graft CDRs onto candidate human frameworks (+ resurfacing + controls) → results/campaign.csv (+ version-verify cell)
03_filter_and_rank  → fp.Design objects → fp.run_pipeline(design_type="antibody") + a humanness floor → fp.report() → ranked CSV + survival figure
04_validate         → humanness↔stability (ΔΔG) trade-off; Vernier back-mutation ladder; grafting-vs-resurfacing; immunogenicity-risk summary
05_validation_plan  → ELISA/SPR/DSF plan (retained binding + Tm) + immunogenicity-risk summary + controls (parental + over-humanized decoy)
```
The mock backend in `scripts/humanization_tools.py` lets every notebook run with no GPU; switch each
`tool="mock"` to `"ablang"` / a real humanness backend / `"proteinmpnn"` on Colab. All mock numbers are
**SYNTHETIC**.

## 4. Filtering cutoffs for this design type
From `shared/filtering_pipeline.DEFAULT_CUTOFFS["antibody"]`, plus the project-specific humanness/ΔΔG bars.
Start here; justify any change.
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | ≤ 3.0 Å | self-consistency of the Fv (more lenient than monomers — CDR loops are flexible) |
| pLDDT | ≥ 70 (mean) | local confidence of the Fv model (NOT stability/affinity) |
| pae_interaction | ≤ 12 Å | VH–VL / paratope arrangement confidence (when scoring a complex) |
| humanness (OASis/Hu-mAb) | ≥ your floor (e.g. proxy 0.6) | human-likeness — set against REAL tool distributions for your antibody |
| ΔΔG (FoldX/Rosetta) | ≤ your ceiling (e.g. ≤ +2–3 kcal/mol) | stability cost vs parental (**use the real tool**; proxy units are arbitrary) |
| residual non-human FR residues | fewer = better | immunogenicity-risk proxy (pair with a T-cell-epitope predictor) |

> Reminder: **no in-silico metric perfectly separates a good from a bad humanization.** Filters enrich;
> they do not guarantee. Humanness ≠ low ADA; a ΔΔG proxy ≠ a measured Tm. Report the trade-off, not a
> single "best" variant.

## 5. Interpreting results
- A *promising* variant: high humanness, ΔΔG within your ceiling, retained binding predicted, few residual
  non-human exposed framework residues, clean Fv self-consistency.
- A *suspicious* one: maximal humanness but large positive ΔΔG (over-humanized — likely lost stability), or
  many Vernier back-mutations re-introducing non-human residues at exposed positions (humanness regained on
  paper but ADA risk back).
- **Survival-at-each-layer** (`fp.report`): how many variants pass each layer — your honest accounting.
  Expect the **over-humanized decoy** to fail self-consistency and the **parental** to fail the humanness
  floor (it is non-human by definition) — both are the filter behaving correctly.
- **The trade-off curve:** humanness (x) vs ΔΔG (y, lower = more stable). You want the lower-right frontier;
  Vernier back-mutations move a point down-left (more stable, slightly less human).

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | unlikely here (project is light) — large batch of FoldX/Rosetta jobs | This project is T4-friendly; reduce the variant batch or run ΔΔG jobs sequentially |
| AbLang / BioPhi install fails | repo/host changed | Use the pinned commit; **verify the current OASis/Hu-mAb host** (web app vs package); log it |
| T20 server unreachable | server moved / retired | Verify the current public URL; if gone, use OASis/Hu-mAb/AbLang and note it in `LOG.md` |
| FoldX/Rosetta licence error | no academic licence | Register for the academic licence; document which tool you used; do not report the heuristic proxy as ΔΔG |
| Graft loses all binding | Vernier residues not restored | Add Vernier back-mutations (`vernier_backmutations()`); restore the key CDR-support residues |
| Over-humanized decoy still "binds" well | weak assay / wrong Vernier set | Re-check the Vernier positions on YOUR numbered sequence (ANARCI); strengthen the binding assay |
| Every variant "passes" on mock | you're on the deterministic mock backend | Mock numbers are SYNTHETIC — switch to real AbLang/OASis + FoldX/Rosetta for real metrics |
| Humanness looks perfect | you used the heuristic, not the real tool | Re-run with real OASis/Hu-mAb/T20/AbLang before claiming humanness |

## 7. Experimental validation reference (for the D4 plan)
The realistic path is **express each variant + controls and test retained binding and stability** — a
humanized sequence is a hypothesis until measured.
- **Expression:** mammalian (ExpiCHO / HEK293) for Fab/IgG (binding + DSF); scFv/Fab in *E. coli*
  periplasm acceptable for early ELISA triage. Express every variant + both controls under identical
  conditions.
- **Characterization tiers:** go/no-go (ELISA: retained binding yes/no) → basic (SPR/BLI K_D vs parental;
  DSF Tm vs parental) → deep (epitope mapping, structure, in-vivo immunogenicity assessment).
- **Controls (mandatory):** positive = the **parental** non-human antibody (defines retained binding +
  the stability ceiling); negative = an **over-humanized decoy** (humanized including the Vernier zone, no
  rescue — must lose binding and/or Tm, proving the assay detects over-humanization); plus an **isotype**
  control for non-specific binding.
- **Immunogenicity:** humanness scores + (real run) a T-cell-epitope predictor give a *risk* summary;
  definitive ADA risk requires a clinical immunogenicity assessment. Do not overstate.

## 8. Responsible research
This is a **therapeutic antibody** project — **reducing the immunogenicity (ADA risk)** of a non-human
therapeutic antibody so it is safer/more effective in patients; a defensive, **low-dual-use** aim. See
`MASTER_BLUEPRINT.md §7`. In-scope purpose here: humanizing therapeutic/diagnostic antibodies. Out of
scope: enhancing pathogen transmissibility/virulence, toxins, or any design intended to cause harm. Real
gene-synthesis orders go through a biosecurity-screening provider (IGSC member); wet-lab work requires
institutional biosafety/ethics approval. Do not overstate a humanness score as a proven low-ADA outcome.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions/commits you actually used:
Prihoda 2022 (Hu-mAb / BioPhi / OASis), Olsen 2022 (AbLang), Gao 2013 (T20), Ruffolo 2023 (IgFold),
Abanades 2023 (ImmuneBuilder), Dauparas 2022 (ProteinMPNN), a FoldX/Rosetta ΔΔG reference, plus the
publication for your chosen non-human antibody and the IMGT/OAS germline source.
