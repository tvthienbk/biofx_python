# Project 25 — Capstone: Integrated DBTL Campaign + ML Success Predictor

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Integrative capstone (full DBTL campaign + data-driven filtering) · **Compute tier:** **A100 recommended** for the campaign (it aggregates a cohort's compute); the **ML part is light / CPU-OK**

## The problem (and why it matters now)
The field's central bottleneck is the **gap between in-silico scores and experimental success** —
*no single metric perfectly separates true binders (or enzymes) from false*. A low `pae_interaction`
or `scrmsd` is *confidence*, not a measured K_D or kcat, and most designs that pass the standard
filters still fail at the bench. Closing that loop needs two things at once: (a) a **complete,
controlled DBTL campaign** on a real target, and (b) **learning from accumulated cohort data** which
features actually predict success — so the shared filter gets better with every campaign the cohort
runs. This capstone does both and reports an **honest hit-rate analysis**, not a cherry-picked design.

## What you will do
You will run an end-to-end de novo design campaign on a **student-chosen, advisor-approved real
target** (any tier; the notebooks use a **binder** as the worked example, but your `design_type` is
whatever you and your advisor pick), triage it with the shared multi-layer in-silico filter, then
**train an ML success predictor** on the cohort-wide design→outcome dataset (Projects 01–24), report
**feature importance** and its **enrichment vs the field's single-metric cutoffs**, integrate any
experimental labels, and deliver an honest hit-rate + failure-forensics synthesis — all reproducibly,
on a deterministic `EXAMPLE_DATA` path that runs anywhere.

## Learning objectives
1. Run a *complete* DBTL campaign on a real, advisor-approved target and triage it with the shared filter.
2. Assemble the cohort design→outcome feature table and **train + cross-validate** an ML success predictor.
3. Benchmark the learned predictor against single-metric cutoffs (enrichment, recall, feature importance) — honestly, with N and CV-AUC.
4. Deliver an honest hit-rate + failure-forensics analysis, a cohort-wide "lessons learned" synthesis, and an active-learning loop design.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs everything; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` / `EXAMPLE_DATA` path with no GPU; switch to the real backends on Colab (A100) for the campaign. The ML notebook (04) is light / CPU-OK.

## Tools
The **full stack** as appropriate to your chosen target — RFdiffusion / RFdiffusion2 / BindCraft /
RFantibody for generation, ProteinMPNN / LigandMPNN for sequences, AF2(-Multimer) / ESMFold / Boltz-2
for prediction — plus the shared `filtering_pipeline.py` (`design_type` = your type) and
**scikit-learn / XGBoost** for the success predictor (`scripts/ml_predictor.py`). XGBoost is optional;
the sklearn path runs anywhere.

## Data
Two things: (1) **your chosen target** (structure/sequence from RCSB/UniProt — verify in Week 1), and
(2) the **aggregated design→outcome dataset** assembled across Projects 01–24 (sequences, in-silico
metrics, any experimental labels). For teaching with no real cohort yet, `scripts/ml_predictor.py`
generates a clearly-labeled **`EXAMPLE_DATA`** synthetic cohort (deterministic seed) with a planted,
imperfect feature→outcome structure so the ML notebook runs anywhere — exact accessions and licenses
are in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + **advisor-approved target** + success criteria + controls + reproduced mock mini-run |
| D1 | P1 (3–6)   | Working minimal pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Full design campaign pool + **cohort feature table** + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + **trained success predictor (CV-AUC, feature importance, enrichment vs cutoffs)** + filtering report |
| D4 | P4 (19–22) | Validation report + costed experimental plan + integrated labels + honest hit-rate + failure forensics |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** the improved **success-predictor module** (feature importance, CV-AUC vs single-metric cutoffs) + honest hit-rate + failure-forensics analysis + cohort-wide "lessons learned" synthesis + active-learning loop design `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
This capstone's deliverable is an **honest hit-rate analysis** and an ML predictor that **beats
single-metric cutoffs by some margin** on the cohort data — *or honestly reports that it doesn't*,
given the N. It is **not** a perfect classifier: the cohort is a small, biased, multi-target dataset,
so report **CV-AUC (mean ± std) and N**, expect modest enrichment, and own the overfitting risk. In-
silico design hit rates vary enormously (binder ~1–100% by tool/target; de novo enzyme < 5%), and a
passing design is a **hypothesis** until measured. **You are graded on rigor, reasoning, and
reproducibility — not on whether the protein works.** A meticulous campaign with a low hit rate and
sharp failure analysis is an excellent capstone. All example numbers are labeled `EXAMPLE_DATA` /
`SYNTHETIC` and must never be reported as real.

## Responsible research
**Your advisor MUST approve your chosen target against `MASTER_BLUEPRINT.md §7` BEFORE the design
campaign (P2).** This project is framed for **neutralizing / diagnostic / inhibitory / industrial**
purposes; default any ambiguous target to that framing. Out of scope: enhancing pathogen
transmissibility/virulence, toxins, evasion of biosecurity screening, or any design intended to cause
harm — targeting a pathogen protein to *neutralize* it is fine, engineering one to be *more dangerous*
is not. Real gene-synthesis orders must go through a biosecurity-screening provider (IGSC member);
wet-lab work requires institutional biosafety/ethics approval. Never overstate results or imply
experimental validation that was not done — a design is a hypothesis, and no experimental label here
is fabricated.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This is the **integrative capstone** — it reuses the
shared campaign workflow (e.g. `project_06_pdl1_binder/`) and the shared `filtering_pipeline.py`, and
its D★ output (the learned success predictor) is **pull-requested back into `shared/`** so the whole
cohort's filter improves.
