# Project 05 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
A design campaign produces a **pool** of candidate sequences, each annotated with in-silico metrics.
The triage problem is: *given the pool, return a small, ranked, defensible short-list to synthesize.*
This project builds that triage as a **4-layer filter** — clean Python functions that score, filter,
rank, and report — and it becomes `shared/filtering_pipeline.py` for the cohort.

The four layers, cheap → expensive, are applied in order (a design must pass a layer to reach the next):

- **Layer 1 — self-consistency** (`self_consistency`): does the sequence fold back to the shape it
  was designed for? Measured by **scRMSD** (design → predict its structure → Cα-RMSD), **pLDDT**
  (local confidence; **NOT** stability), and, for complexes, **pAE** (interface confidence). This is
  the single most important, cheapest, mandatory layer.
- **Layer 2 — orthogonal agreement** (`orthogonal_check`): a *second*, independent predictor
  (ESMFold or Boltz, different inductive bias than AF2) must also reproduce the design
  (`scrmsd_orthogonal`). This catches predictor-specific overconfidence — a design AF2 loves but
  ESMFold rejects is suspect.
- **Layer 3 — physics** (`physics_filter`): solubility/aggregation (a CamSol-style score) and, for
  binders, interface energy (`rosetta_dG`, REU) + shape complementarity. A self-consistent fold that
  will aggregate or has a weak interface is still a bad candidate.
- **Layer 4 — dynamics** (`dynamics_filter`, optional/expensive): a short MD run; the structure
  should not drift far from the design (`md_rmsd`). Catches "folds-but-melts" designs the static
  metrics miss. Rarely worth its cost at scale — use it only on a short-list.

Then `rank_designs()` assigns a composite score (higher = better; rewards low scRMSD/pAE, high pLDDT,
negative `rosetta_dG`, and layers passed), `run_pipeline()` orchestrates and records survival counts,
and `report()` prints the hit-rate accounting + the survival figure and writes the ranked CSV.

**Why this is hard and what realistic success looks like.** Predictors are trained on natural
proteins and can be overconfident on de novo sequences; physics scores are approximate; MD is short.
The result: **no single metric — and no single layer — perfectly separates true hits from false
ones.** Each layer *enriches* the pool (raises the fraction of true-good among survivors) but also
*discards some true hits* (false negatives) and *passes some duds* (false positives). A realistic,
gradeable outcome for this project is therefore a clean, tested engine plus an **honest
discrimination-problem analysis**: the enrichment each layer buys, where it fails, and how sensitive
the ranking is to cutoff choices. Success = reproducible, tested, honestly characterized — not "a
perfect classifier." Realistic downstream hit rates the filter cannot fix: binder campaigns ~1–100%
by tool/target; de novo enzymes < 5%. The filter raises the *odds*; it does not manufacture hits.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)
The **engine itself** needs only pandas/numpy/matplotlib + Biopython — no GPU. The tools below are
the *upstream sources of the metrics* the engine scores; they sit **behind clean function
boundaries**, so the filter, its tests, and its analysis all run on a free T4 (or CPU) with the
labeled `EXAMPLE_DATA` pool. Pin upstreams in a comment and **verify they still exist** (version-verify
cell in `00_setup` / `02`); these change.

### pandas / numpy / matplotlib + Biopython (the engine)
- **What it does / where it fits:** all scoring, filtering, ranking, reporting, and the Cα-RMSD
  geometry helper (`ca_rmsd`, Biopython `Superimposer`). This is the whole deliverable.
- **Install:** pinned in `env/requirements.txt`; installed by `00_setup`.
- **Key parameters that matter:** `DEFAULT_CUTOFFS` per design type; `use_layers` in `run_pipeline`.
- **Compute:** **free T4 — and in fact CPU-only is fine.** This is pure-Python scoring.
- **Typical call:**
  ```python
  import filtering_pipeline as fp
  df = fp.run_pipeline(designs, design_type="binder", use_layers=(1,2,3))
  fp.report(df, top_n=20, save_prefix="results/p05")
  ```

### ColabFold (AlphaFold2) + ESMFold — upstream of Layers 1 & 2
- **What it does / where it fits:** AF2 (MSA-based) gives the primary scRMSD/pLDDT/pAE; ESMFold
  (single-sequence, MSA-free) is the **orthogonal** opinion for Layer 2. The engine consumes the
  *numbers*; it does not run these models.
- **Install (pin & verify):** ColabFold `https://github.com/sokrypton/ColabFold` (pin the commit;
  changes often); ESMFold via HuggingFace `transformers` (`EsmForProteinFolding`).
- **Key parameters:** AF2 `num_recycles`, `msa_mode`; ESMFold sequence-length limit on T4 (~400 aa).
- **Compute:** both free-T4-OK for triage-sized monomers; long sequences/deep MSAs approach the T4 ceiling.
- **Typical call:** produced upstream (Projects 01/03); here you ingest the parsed metrics into `Design`.

### Boltz-2 — upstream of Layer 2 (third opinion) / affinity
- **What it does / where it fits:** open all-atom structure + affinity predictor; a third orthogonal
  agreement signal and (for binders) a predicted-affinity input to the physics reasoning.
- **Install (pin & verify):** Boltz `https://github.com/jwohlwend/boltz` (`pip install boltz`; pin the version; verify weights download).
- **Key parameters:** `--recycling_steps`, `--diffusion_samples`; affinity mode for complexes.
- **Compute:** heavier than ESMFold; small monomers OK on T4, complexes/affinity prefer A100.

### PyRosetta / FreeBindCraft relax + CamSol — upstream of Layer 3 (physics)
- **What it does / where it fits:** PyRosetta (or a FreeBindCraft relax) produces interface energy
  (`rosetta_dG`, REU) and shape complementarity; a CamSol-style predictor gives the solubility score.
  The engine just thresholds these.
- **Install (pin & verify):** PyRosetta `https://www.pyrosetta.org` (academic license required; pin
  the release). FreeBindCraft / CamSol per their sites — verify availability at generation time.
- **Key parameters:** relax protocol / score function (`ref2015`); `rosetta_dG` and `sc` cutoffs in `DEFAULT_CUTOFFS`.
- **Compute:** CPU-feasible for relax on small complexes; budget time, not GPU.

### OpenMM short MD — upstream of Layer 4 (dynamics, optional)
- **What it does / where it fits:** a short (10–50 ns) MD run; the mean backbone RMSD over the
  trajectory (`md_rmsd`) flags designs that drift. Optional and expensive.
- **Install (pin & verify):** OpenMM (conda/pip). **Compute:** feasible on T4 for small systems; long MD → HPC.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback) + version-verify cell
01_define_explore   → spec the API (Design + layer signatures); implement/verify Layer 1 with inline asserts on planted designs
02_generate         → "nothing to generate": build the labeled EXAMPLE_DATA pool (make_example_pool.py); implement/verify Layers 2 + 3 + unit tests
03_filter_and_rank  → import shared/filtering_pipeline.py; run_pipeline(pool) + report(); survival-at-each-layer → ranked CSV + figure
04_validate         → the discrimination-problem analysis: enrichment per layer (labeled pool), cutoff-sensitivity sweep, where no metric separates true/false
05_validation_plan  → optional Layer 4 (short MD) hook; package as pip module [stretch]; cohort-adoption-via-PR guide
```
For Project 05 the standard notebook slots map to: *02 = pool assembly* (instead of generative
design — there is nothing to generate), *04 = the discrimination-problem analysis*, *05 = the
dynamics hook + packaging + adoption plan* (instead of a wet-lab plan — this project ships software).

## 4. Filtering cutoffs for this design type
The engine handles **all** design types; cutoffs live in `DEFAULT_CUTOFFS` and are justified below.
These are starting points from the validation-ref lineage — **justify and, where your labeled
analysis supports it, propose changes via PR** (with enrichment + N behind each).
| Metric | Cutoff (by type) | Why |
|--------|------------------|-----|
| scRMSD | < 2.0 Å (monomer/enzyme), < 2.5 Å (binder/oligomer), < 3.0 Å (antibody) | self-consistency (designed vs predicted backbone) |
| pLDDT (mean) | > 85 (monomer/enzyme), > 80 (binder/oligomer), > 70 (antibody) | local confidence (**NOT** stability) |
| pae_interaction (complexes) | < 10 Å (binder/oligomer), < 12 Å (antibody) | interface confidence |
| plddt_catalytic / catalytic_geom_rmsd (enzyme) | > 90 / < 0.5 Å | active-site confidence + theozyme geometry |
| scrmsd_orthogonal (Layer 2) | < 2.5 Å | a second predictor must agree |
| solubility (Layer 3) | ≥ -1.0 (CamSol-style) | aggregation risk |
| rosetta_dG / shape_complementarity (binder, Layer 3) | ≤ -30 REU / ≥ 0.6 | interface energy + packing |
| md_rmsd (Layer 4, optional) | ≤ 3.0 Å | structure should not drift over a short MD |

> Reminder: **no in-silico metric perfectly separates true from false hits.** Filters enrich; they
> do not guarantee. Expect false positives among survivors and true hits among the cut — and report
> both. Every enrichment number you show from the teaching pool is `EXAMPLE_DATA`, never a real result.

## 5. Interpreting results
- A *good* design: low scRMSD, high mean pLDDT, low pAE, the orthogonal predictor agrees, soluble,
  (for binders) negative `rosetta_dG` + good shape complementarity, stable under short MD.
- A *suspicious* one: high pLDDT but high scRMSD (confident about the wrong fold); AF2 happy but
  ESMFold/Boltz disagree (predictor-specific overconfidence — flag it); self-consistent but
  aggregation-prone or weak interface (passes L1, fails L3).
- **Survival-at-each-layer plot** (`report()`): a bar per layer showing how many designs survive.
  Read it as a funnel — steep drops tell you which layer is doing the discriminating; a layer that
  cuts *nothing* is either too lenient or redundant.
- **Enrichment vs survival:** survival counts alone are not success. On the *labeled* pool, also
  report **precision** (fraction of survivors that are truly good) and **recall** (fraction of truly
  good designs retained). A good layer raises precision; watch the recall you pay for it.
- **Hit rate:** N pass / N total, per layer, with the false-positive / false-negative breakdown.
  Report the rate, not the cherry.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ImportError: filtering_pipeline` in notebook 03 | `shared/` not on `sys.path` | run the "Setup paths" cell (`sys.path.insert(0, "../../../shared")`); check cwd is `notebooks/` |
| A layer passes everything (survival == total) | cutoff too lenient, or the relevant field is `None` for every design | check the field is populated; the layer is skipped when its cutoff is `None` or the value is missing — confirm with a planted known-bad |
| A layer fails everything | metric direction flipped or wrong units (Å vs nm, REU sign) | re-check the cutoff sign/units against `DEFAULT_CUTOFFS`; lower scRMSD/pAE = better, more-negative `rosetta_dG` = better |
| `python scripts/test_filtering.py` fails after editing cutoffs | you changed `shared/filtering_pipeline.py` and broke a planted case | that is the test doing its job; re-justify the cutoff or revert; never weaken a test to make it pass |
| scRMSD looks random | mismatched residue numbering in `ca_rmsd` | the helper truncates to the shorter chain; align by sequence first; check chain IDs |
| Enrichment ≈ baseline (no lift) | label noise in `truth`, or the cutoff is not discriminating on this pool | re-check the planted labels; sweep the cutoff (notebook 04) to find where it separates |
| "It runs but needs a GPU" | you tried to run the *upstream* predictor, not the engine | the engine needs no GPU; ingest pre-computed metrics; only Projects 01/03 run the models |

## 7. Experimental validation reference (for the D4 plan)
This project ships **software**, not a wet-lab campaign, but the engine's output feeds the
experimental plans of *downstream* projects, so document what your short-list implies:
- Expression: downstream projects typically use *E. coli* BL21(DE3), 16–18 °C overnight; mammalian
  expression where the target needs it.
- Characterization tiers: go/no-go (express → SDS-PAGE → SEC) → basic (DSF, CD, binding assay
  SPR/BLI) → deep (structure, SEC-MALS/SAXS).
- **Controls** every downstream project must run on the short-list this engine produces: positive
  control (a known-good design / natural protein), negative control (scrambled-interface for binders
  or catalytic dead-mutant for enzymes), and an unrelated-protein control. The engine's *own*
  "controls" are the **planted known-good / known-bad `EXAMPLE_DATA` designs** its tests assert on.

## 8. Responsible research
This project builds triage *infrastructure* and designs no new functional protein, so its dual-use
surface is low. See `MASTER_BLUEPRINT.md §7`. In-scope purpose here: **safe, reproducible filtering
infrastructure** for the cohort, with any pool it scores defaulting to a neutralizing/diagnostic/
industrial framing. The filter must **not** be used to optimize designs whose primary purpose is
harmful (enhancing pathogen transmissibility/virulence, toxins, biosecurity-screening evasion). If a
pool you are handed raises dual-use concern, decline it and raise it with your advisor. Any wet-lab
follow-up by downstream projects requires gene-synthesis screening + institutional biosafety/ethics
approval.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used: the
4-layer validation-ref lineage, Dauparas 2022 (ProteinMPNN/self-consistency), Jumper 2021 (AF2
confidence), Lin 2023 (ESMFold orthogonal check), Wohlwend 2025 (Boltz-2), Norn 2021 (energy
landscapes), Pacesa 2025 (BindCraft discrimination caveat), plus a testing/reproducibility reference.
