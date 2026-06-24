# Project 14 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
A nanobody (VHH) is the single variable domain of a camelid heavy-chain antibody: a stable ~15 kDa
scaffold with three CDR loops (CDR3 dominates the paratope). De novo VHH design fixes a **framework**
and a target **epitope**, then designs the CDR loops to bind. Here the epitope is a **conserved
neutralizing** site (influenza HA stem / RSV F prefusion) — a VHH that binds it **blocks** the virus.
**RFantibody** = RFdiffusion-Ab (diffuse CDR loops onto the framework against the epitope) +
ProteinMPNN (design the loop sequence); **BoltzGen** nanobody mode is an alternative generator.

Key metrics: AF2-Multimer **`pae_interaction`** (interface confidence; antibody cutoff ≤ 12),
interface pLDDT, self-consistency scRMSD, **CDR-loop geometry** (Ramachandran sanity vs an
IgFold/NanoBodyBuilder2 model), and **developability** (aggregation/TAP, solubility/CamSol, humanness).
The project-specific hard problem is **breadth**: a VHH to a conserved epitope should recognize the
antigen across **strains** — quantify it by modeling each VHH against a strain panel and reporting the
**worst-case** `pae_interaction`.

Why this is hard and what realistic success looks like: de novo antibody hit rates are **LOW**, so the
campaign feeds a **display screen**, not a finished binder. A realistic outcome is a small,
developability-filtered, breadth-profiled set of conserved-epitope VHHs and a controlled plan to screen
them — not a guaranteed neutralizer.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFantibody (RFdiffusion-Ab + ProteinMPNN)
- **What/where:** diffuse CDR loops onto a fixed VHH framework against the epitope, then design the loop sequence.
- **Install:** `https://github.com/RosettaCommons/RFantibody` (pin a commit). **Verify it still exists.**
- **Key params:** `target_pdb`, hotspot/epitope residues, framework, `num_designs` (aim 500+).
- **Compute:** A100 strongly recommended; free T4 → a tiny demo only.

### BoltzGen (nanobody mode) `[extension]`
- **What/where:** an alternative de novo nanobody generator for the head-to-head.
- **Install:** **verify the current public release at course start** and pin it (the API is newer/changing).

### AF2-Multimer (ColabFold) + IgFold / ImmuneBuilder
- AF2-Multimer (`https://github.com/sokrypton/ColabFold`) for `pae_interaction`/interface pLDDT/scRMSD; IgFold / ImmuneBuilder (`https://github.com/oxpig/ImmuneBuilder`) for fast antibody-aware CDR geometry. Pin commits.

### Developability heuristics (teaching only)
- `antibody_tools.developability()` returns TAP-like / CamSol-like / humanness **proxies** — CLEARLY-LABELED teaching heuristics, NOT the validated tools (TAP/CamSol/Hu-mAb). Swap in the real tools before any developability conclusion.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → epitope + framework choice, CDR/metrics table, mock hello-world, conservation concept
02_generate         → RFantibody CDR design campaign (500+) → AF2-Multimer + IgFold + developability
03_filter_and_rank  → shared/filtering_pipeline.py (design_type="antibody") → ranked CSV + survival figure
04_validate         → cross-strain BREADTH + developability/humanness gate + RFantibody-vs-BoltzGen
05_validation_plan  → yeast-display screen plan + neutralization/breadth plan (controls + IBC)
```

## 4. Filtering cutoffs for this design type (antibody)
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | < 3.0 Å | self-consistency (antibody loops are flexible — looser than monomers) |
| pLDDT | > 70 | confidence (NOT affinity) |
| pae_interaction | < 12 Å | interface confidence — the key complex metric |
| CDR geometry RMSD | low | Ramachandran/loop sanity vs IgFold/NanoBodyBuilder2 |
| developability (TAP/CamSol/humanness) | gate | aggregation/solubility/immunogenicity proxies (use real tools) |
| **worst-case breadth pae** | report it | a broad neutralizer keeps low pae across ALL strains |

> Reminder: **no in-silico metric perfectly separates true from false binders**, and de novo antibody
> hit rates are low. Filters enrich; the **display screen** is what finds real binders.

## 5. Interpreting results
- A *promising* VHH: low `pae_interaction` + low scRMSD + clean CDR geometry + good developability + **low pae across the strain panel**.
- A *suspicious* one: great on the design strain, poor on others (narrow), or long CDR3 with deamidation/oxidation liabilities.
- **Hit rate:** report N pass / N generated at each layer, per generator — the honest accounting; survivors are screening inputs.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / dies | campaign too large for T4 | tiny demo on T4; move to A100; batch |
| RFantibody install fails | repo changed | pinned commit; update install cell; log it |
| All designs fail self-consistency | bad target prep / framework mismatch | re-clean antigen; check epitope numbering; verify framework |
| Great on one strain, bad on others | epitope not conserved enough | re-map to a more conserved site; re-run breadth |
| pae_interaction looks random | AF2-Multimer parsing error | confirm multimer model; parse inter-chain PAE correctly |

## 7. Experimental validation reference (for the D4 plan)
- **Yeast/phage display** is the workhorse: pool the designs → FACS against labeled antigen → sequence winners → express → SPR/BLI → neutralization.
- Neutralization: **pseudovirus surrogate (standard BSL-2)** across the strain panel, **with IBC approval**. Authentic-virus work is higher-containment and out of scope for most courses.
- **Controls:** positive (a known neutralizing nanobody), negative (scrambled-CDR), irrelevant-antigen negative. Report breadth as worst-case across strains.

## 8. Responsible research
**Defensive / neutralizing only.** In scope: blocking the virus by binding a conserved neutralizing
epitope (antiviral/diagnostic). Out of scope: enhancing transmissibility, virulence, affinity, immune
escape, or any pathogen gain-of-function. See `MASTER_BLUEPRINT.md §7`. Synthesis screening + IBC
approval required for any wet-lab work. Never overstate results.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used.
