# Project 10 — De Novo Binder vs an Antimicrobial-Resistance Target (NDM-1)

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed binder design (active-site occlusion) · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
Antimicrobial resistance (AMR) is one of the top global health threats. **NDM-1** (New Delhi
metallo-β-lactamase) is a class B **metallo-β-lactamase** that hydrolyzes carbapenems — our
**last-resort** antibiotics — and, unlike the serine β-lactamases, it has **no clinical inhibitor**.
Its active site holds **two catalytic Zn²⁺ ions** that activate a hydroxide to attack the β-lactam
ring. A small **de novo binder** that docks onto the **active-site rim** and **occludes substrate
access** is a defensible, high-impact way to **inhibit** NDM-1 and **restore carbapenem efficacy**
(a β-lactam *adjuvant*, used alongside the antibiotic). This project designs such binders
computationally, reasons explicitly about the *inhibition mechanism* (occlusion, not just sticking),
and plans the enzyme-kinetics assay that actually tests inhibition.

## What you will do
By the end you will have run an end-to-end de novo binder campaign against the **NDM-1 di-zinc
active-site rim** with **two** paradigms (BindCraft and RFdiffusion-binder + **LigandMPNN**, Zn-aware
near the metal), triaged both pools with the shared multi-layer in-silico filter
(`design_type="binder"`) **plus** an **occlusion** score and an **off-target specificity** check vs
human metalloenzymes, benchmarked them head-to-head, and produced a costed **nitrocefin /
carbapenem-hydrolysis inhibition (IC50)** validation plan with the right controls — all reproducibly,
degrading gracefully when only a free T4 is available.

## Learning objectives
1. Prepare the NDM-1 target **preserving both catalytic Zn²⁺ ions** and select **active-site-rim
   hotspots** that wall the substrate-access channel (the occluding epitope).
2. Run BindCraft (or FreeBindCraft) and RFdiffusion binder mode + **LigandMPNN (Zn-aware)** against
   that rim.
3. Apply the shared 4-layer filter with binder cutoffs (`pae_interaction` is the key binder metric),
   add an **occlusion** score and an **off-target-metalloenzyme specificity** check, and report an
   honest hit rate.
4. Reason about the **inhibition mechanism** (binding ≠ inhibition) and design a controlled
   **enzyme-kinetics inhibition** plan (IC50) with an off-target-metalloenzyme control.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
BindCraft (or FreeBindCraft) for one-shot hallucination-based binders; RFdiffusion **binder mode** +
**LigandMPNN** (Zn-aware sequence design near the di-zinc site) for diffusion-then-sequence binders;
AF2-Multimer (ColabFold) for interface confidence (`pae_interaction`); the shared
`filtering_pipeline.py` (`design_type="binder"`); the project's `occlusion_score` and
`offtarget_specificity` mechanism helpers; Biopython, py3Dmol. Optional stretch: a β-lactam-adjuvant
concept and a Boltz-2/affinity scaffold on top hits (never a fabricated number).

## Data
NDM-1 di-zinc metallo-β-lactamase structures to define the active-site rim and read off occluding
hotspots — candidate accessions **3SPU** and **4EYL** (**candidate — verify on RCSB**). The binder
targets the rim of the substrate-access channel over the di-zinc site; **both Zn²⁺ ions must be
preserved** in target prep (they are part of the epitope). Exact accessions, sizes, and licenses are
in `data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + di-zinc target prep (Zn preserved) + rim hotspots + reproduced mini-run |
| D1 | P1 (3–6)   | Working minimal binder pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Two-paradigm design pool (BindCraft + RFdiffusion→LigandMPNN) + design log + interim report |
| D3 | P3 (13–18) | Ranked top 10–20 each + occlusion + specificity-vs-human-metalloenzymes + benchmark + filtering report |
| D4 | P4 (19–22) | Validation report + costed **nitrocefin/carbapenem inhibition (IC50)** plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** binder design report + **occlusion + off-target-specificity analysis** + top 10–20 each with a **nitrocefin/carbapenem-hydrolysis inhibition (IC50)** plan, off-target-human-metalloenzyme + scrambled-interface controls, β-lactam-adjuvant stretch |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
In-silico binder "hit rates" vary **enormously** by target and tool — anywhere from single-digit to
tens of percent passing the filter, and the **great majority of in-silico hits still fail
experimentally**. Worse here: **binding is not inhibition.** A binder can have a beautiful interface,
sit just off the substrate groove, and never slow the enzyme. A designed binder that passes every
filter is a **hypothesis**, not an inhibitor: `pae_interaction` low and `occlusion` high do **not**
mean it inhibits, and an **enzyme-kinetics IC50 assay is mandatory**. **You are graded on rigor,
reasoning, and reproducibility — not on whether the binder inhibits.** Any example numbers in the
notebooks are labeled `EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as real — there are **no
fabricated IC50 values** anywhere in this project.

## Responsible research
This is a **defensive anti-AMR** project. Its purpose is to **inhibit** a resistance enzyme (NDM-1)
so that a **last-resort antibiotic works again** — a therapeutic/diagnostic, in-scope goal under
`MASTER_BLUEPRINT.md §7` ("AMR enzymes (to *inhibit*)"). The binder is an **inhibitor / β-lactam
adjuvant** that *restores* antibiotic efficacy. It is **explicitly out of scope** to enhance
antimicrobial **resistance**, improve **pathogen fitness/virulence/transmissibility**, protect or
stabilize the enzyme, or otherwise make the bug harder to treat — and student proposals in that
direction must be refused and redirected. Also out of scope: toxins, immune-evasion tools, or any
design intended to cause harm. Real gene-synthesis orders must go through a biosecurity-screening
provider (IGSC member); wet-lab work requires institutional biosafety/ethics approval. If your chosen
target raises dual-use concern, discuss a defensible inhibitory/diagnostic framing with your advisor
before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(Project 06, PD-L1); its scientific twist is the di-zinc active-site target, the occlusion/specificity
mechanism analysis, and the enzyme-kinetics inhibition assay.
