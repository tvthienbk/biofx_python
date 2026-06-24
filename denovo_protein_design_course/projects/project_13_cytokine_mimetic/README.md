# Project 13 — Cytokine-Mimetic Receptor Agonist Mini-Protein

> **De Novo Protein Design Capstone · ~6 months (24 weeks) · Final-year / early-MSc**
> **Primary paradigm:** Target-directed (receptor-subunit-selective) agonist mini-protein design · **Compute tier:** Colab **Pro (A100)** or local A100 (free-tier T4 = small fallback campaign only)

## The problem (and why it matters now)
Natural cytokines are powerful immune signals but lousy drugs: **IL-2**, for example, drives both the
anti-tumor effector T/NK response *and* the immunosuppressive regulatory-T-cell (Treg) response, has a
short half-life, and is unstable — its therapeutic window is narrow and toxic. The receptor explains
the pleiotropy: IL-2 engages a heterotrimeric receptor (IL-2Rα/CD25, IL-2Rβ/CD122, γc/CD132), and
which **subunit combination** is engaged decides which cells respond. De novo **cytokine mimetics**
that engage a **chosen receptor-subunit combination** with tuned selectivity — the Neoleukin
**"Neo-2/15"** paradigm (Silva et al. 2019), a hyperstable de novo mini-protein that signals through
IL-2Rβ/γc but **not** IL-2Rα — are a real, validated immunotherapy strategy: keep the useful signaling,
drop the toxic arm, and gain stability. This project designs such a mini-protein computationally and
reasons explicitly about **subunit selectivity**. **This is a therapeutic immunotherapy project; the
explicit goal is to *reduce* the toxicity of a natural cytokine, framing is therapeutic-only.**

## What you will do
By the end you will have run an end-to-end de novo agonist mini-protein campaign against a chosen
IL-2-receptor surface (e.g., the **IL-2Rβ/γc interface**), modeled each candidate against **each
receptor subunit separately** with AF2-Multimer, triaged the pool with the shared multi-layer in-silico
filter (`design_type="binder"`), built a **subunit-selectivity profile** (engages βγ but **not** α),
compared stability against the native cytokine, and produced a costed validation plan — **per-subunit
SPR + a cell-based STAT-phosphorylation signaling assay with controls** — all reproducibly, degrading
gracefully when only a free T4 is available.

## Learning objectives
1. Choose a receptor-subunit interface to engage (e.g., IL-2Rβ/γc) and justify the **desired selectivity** (βγ-biased agonist that spares α/CD25 → spares Tregs / vascular leak).
2. Run RFdiffusion binder mode (or BindCraft) + ProteinMPNN to design agonist mini-proteins steered onto the chosen subunit surfaces, and re-score with AF2-Multimer.
3. Apply the shared 4-layer filter with binder cutoffs (`pae_interaction` is the key metric) and build a **per-subunit selectivity profile** (model the binder vs IL-2Rα, IL-2Rβ, and γc separately).
4. Reason about why **binding ≠ signaling** and design a controlled validation plan (per-subunit SPR + a STAT-phosphorylation cell assay), with a thermostability comparison to the native cytokine.

## Quickstart
1. Open `notebooks/00_setup.ipynb` in Google Colab → Runtime → Change runtime type → GPU.
2. Run it top to bottom (it checks your GPU and installs the light core; it degrades gracefully on a free T4).
3. Read `INSTRUCTIONS.md` (your week-by-week guide) and `MANUAL.md` (the technical reference).
4. Fetch inputs: `python data/download_data.py` (records provenance; verify accessions in Week 1).
5. Work through notebooks `01 → 05` following `TIMELINE.md`. Every notebook runs end-to-end on a deterministic `mock` backend with no GPU; switch to the real backends on Colab Pro / A100.

## Tools
RFdiffusion **binder mode** + ProteinMPNN (diffuse a mini-protein backbone against the chosen receptor
surface, then design a sequence) and/or BindCraft (one-shot hallucination, AF2-Multimer in the loop)
for the agonist mini-proteins; AF2-Multimer (ColabFold) to model the binder **against each receptor
subunit separately** (`pae_interaction` per subunit → the selectivity profile); the shared
`filtering_pipeline.py` (`design_type="binder"`); Biopython, py3Dmol. Optional stretch: Boltz-2 affinity
on top hits (scaffold only — never a fabricated K_D) and a thermostability proxy vs the native cytokine.

## Data
The **IL-2 / IL-2R quaternary complex** to define the receptor surfaces and read off the subunit
contacts — candidate accession **2B5I** (**candidate — verify on RCSB**), plus the individual receptor
subunits (IL-2Rα/CD25, IL-2Rβ/CD122, γc/CD132) you isolate for the per-subunit selectivity modeling,
and the **Neo-2/15** de novo design as a reference. Exact accessions, sizes, and licenses are in
`data/README.md`. **Verify every accession on RCSB/UniProt in Week 1; entries get superseded.**

## Deliverables (mapped to the 6-month timeline)
| ID | Phase / weeks | Deliverable |
|----|---------------|-------------|
| D0 | P0 (1–2)   | Problem statement + target-subunit/selectivity choice + reproduced mini-run |
| D1 | P1 (3–6)   | Working minimal agonist pipeline + first design batch + repo |
| D2 | P2 (7–12)  | Agonist mini-protein design pool (engaging the chosen surfaces) + design log + interim report |
| D3 | P3 (13–18) | Ranked top candidates + **per-subunit selectivity profile** + stability-vs-native figures + filtering report |
| D4 | P4 (19–22) | Validation report + costed per-subunit SPR + cell-signaling (STAT) plan with controls |
| D5 | P5 (23–24) | Thesis report + 15-min talk + tagged reproducible release |
| D★ | — | **Project-specific:** a **subunit-selective agonist design** + a **selectivity profile** (engages βγ but not α, or vice versa) + a validation plan (per-subunit SPR + a cell STAT-phosphorylation assay with controls) + a **thermostability comparison to the native cytokine** `[stretch]` |

See `ASSESSMENT.md` for the rubric and weighting.

## Realistic expectations
De novo **agonist** design with **clean subunit selectivity is hard** — harder than a plain binder.
In-silico binder "hit rates" vary **enormously** by target and tool, and the **great majority of
in-silico hits still fail experimentally**. Worse, **binding is not signaling**: a mini-protein can
engage IL-2Rβ/γc in a model and still fail to trigger STAT5 phosphorylation, because agonism depends on
correctly *geometrically dimerizing* the receptor chains — a cell-based signaling assay is therefore
**mandatory**, not optional. A designed mimetic that passes every filter is a **hypothesis**, not a
drug: `pae_interaction` low does **not** mean it binds, and binding does **not** mean it signals. **You
are graded on rigor, reasoning, and reproducibility — not on whether the mimetic works.** A meticulous
campaign with a low hit rate and a sharp selectivity/signaling analysis is an excellent capstone. Any
example numbers in the notebooks are labeled `EXAMPLE_DATA` / `SYNTHETIC` and must never be reported as
real (no fabricated EC50/K_D).

## Responsible research
This project designs a **receptor-selective agonist mini-protein** that mimics a human cytokine for
**cancer immunotherapy / immune modulation** — a defensible, in-scope therapeutic purpose. Its explicit
design intent is to **reduce the toxicity** of a natural cytokine (a βγ-biased IL-2 mimetic spares
CD25-high Tregs and the vascular-leak toxicity associated with high-affinity α engagement), so its
**dual-use risk is low**: a tuned-selectivity agonist is *safer* than the native cytokine it mimics.
Out of scope: any design intended to *over-activate* the immune system to cause harm, to enhance
pathogen fitness, toxins, or immune-evasion tools. Real gene-synthesis orders must go through a
biosecurity-screening provider (IGSC member); wet-lab work (including any cell-based immune assay)
requires institutional biosafety/ethics approval. If your chosen target or selectivity goal raises
dual-use concern, discuss a defensible therapeutic framing with your advisor before proceeding.

## Repository layout
See `MASTER_BLUEPRINT.md §1`. Keep `results/` and large data out of git; pin `env/requirements.txt`;
tag a `v1.0` release with your final report. This project follows the **binder-family template**
(Project 06); its twist is **receptor-subunit selectivity** — model the binder against *each* subunit
and report the selectivity profile, don't just report one interface.
