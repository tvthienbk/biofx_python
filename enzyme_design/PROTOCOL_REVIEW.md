# Correctness review of the source protocol

You asked me to check the protocol carefully for content/correctness/bugs while
building the deliverables. The document is technically sound and reflects the
current (2023–2025) state of the art. Below are the issues I found, graded, plus
where the toolkit turns a documented pitfall into an enforced check.

## A. Technical inaccuracies (worth fixing in the text)

1. **Expression vector tag description (Materials → Wet-lab reagents).**
   The protocol writes *“pET-29b(+) with C-/N-terminal His₆.”* pET-29b(+)
   actually provides an **N-terminal S-tag and a C-terminal His₆-tag** — it has
   **no N-terminal His₆**. If an N-terminal His₆ is wanted, **pET-28a(+)**
   (N-terminal His₆ + thrombin site, plus C-terminal His₆) is the conventional
   choice. *Severity: low (reagent selection).*

2. **`inference.deterministic=True` together with `inference.num_designs=1000`
   (Stage 3, step 7).** `deterministic=True` fixes the RNG; it is meant for
   reproducing a *single* trajectory. Pairing it with 1000 designs is
   contradictory unless the per-design seed is incremented (the protocol relies
   on that behaviour implicitly). For a large diversity-seeking batch you
   normally leave it `False` (or sweep `inference.seed`). The protocol elsewhere
   (step 7 CRITICAL STEP) correctly stresses generating *hundreds–thousands* of
   diverse backbones, which is in mild tension with a globally deterministic run.
   *Severity: low–medium (reproducibility vs. diversity).*

3. **Ligand-RMSD threshold “< 5 Å” (Stage 5a, step 11).** This is fine as a
   *pose-sanity* gate but is far too loose to certify catalytic placement; the
   document is internally consistent in saying the **motif Cα-RMSD ≲ 1.0–1.5 Å**
   is the strict criterion. Readers should not treat ligand-RMSD < 5 Å as
   evidence of a competent active site. *Severity: low (clarification).*

## B. Things that are correct and worth emphasising (not bugs)

- The **catalytic-knockout control** logic (step 26) is exactly right and is the
  single most important activity control: activity surviving the nucleophile
  knockout is an artifact, not designed catalysis.
- The **worst-step preorganization** thesis (step 12) matches the published
  serine-hydrolase result and is the correct ranking quantity (not the mean).
- The contig guidance in step 6 (*always ranges, never bare integers; keep total
  length consistent with `contigmap.length`*) is a real, common failure mode.
- Citations check out: RFdiffusion (*Nature* 620, 2023), RoseTTAFold All-Atom
  (*Science* 2024), LigandMPNN (*Nature Methods* 2025), serine-hydrolase design
  (*Science* 2025), AlphaFold (*Nature* 596, 2021).
- The example contig `['10-120,A84-87,10-120']` with `length='150-150'` is
  internally consistent: the segments span 24–244 residues, so 150 is reachable.

## C. Pitfalls the toolkit now *enforces* (so they can’t silently happen)

| Protocol warning | Enforced by |
|---|---|
| Bare integer instead of a range in a contig | `contig.parse_contig` raises `ContigError` |
| `contigmap.length` impossible for the segments | `Contig.validate()` reports it; `build_contig` raises |
| Catalytic residues not held fixed in LigandMPNN | `LigandMPNNJob.validate(motif_residues=…)` blocks the command |
| Ligand present but a ligand-blind MPNN model chosen | `pipeline.consistency_check` flags it |
| Theozyme block missing the primary `distanceAB` | `Theozyme.validate()` reports it |
| Judging a design with no RMSD measured | `SelfConsistency.evaluate` refuses (returns fail + reason) |
| Ranking by average preorganization | `selection.rank_designs` uses `worst_score()` |
| Free surface Cys / internal restriction site before ordering | `DesignRecord.pre_synthesis_warnings` |

## D. Out of scope (correctly left to the real tools)

QM transition-state optimization, the diffusion/sequence/structure networks
themselves, PLACER/ChemNet ensemble *generation* (we score the ensembles, we do
not generate them), MD, and all wet-lab stages (7–12). The toolkit produces the
validated inputs and consumes mock/real outputs at each interface.

## E. Reproducibility (per the protocol’s own checklist)

`environment.yml` pins the installable analysis layer. The generative models are
**not** pip packages — record, next to the env file: each repo’s **commit hash**,
the **weight filenames** (e.g. `RFDiffusionAA_paper_weights.pt`), every **command
line + config + random seed**, and the **full metric table for all designs
(the denominator), not only the hits** — exactly as the protocol’s
Reproducibility checklist demands.
