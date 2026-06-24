# Project 04 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
A **symmetric assembly** is built from identical subunits related by a point-group symmetry. We
target two families here: **cyclic Cn** (n subunits arranged in a single ring around one axis — C3 is
a trimer, C4 a tetramer) and **dihedral Dn** (a Cn ring plus a perpendicular two-fold — **D2** is a
tetramer built from two C2 dimers). De novo symmetric design generates one **asymmetric unit** (the
subunit) and lets the symmetry operators replicate it; the whole campaign hinges on designing a
subunit whose interfaces drive assembly into the *intended* point group.

Key concepts you must understand:
- **Symmetric contig:** the per-subunit shape specification given to RFdiffusion's symmetric mode.
  The contig describes one subunit; the chosen point group (`inference.symmetry=C3` etc.) replicates
  it under the symmetry operations. (See `data/inputs/symmetry_defs.txt` for the teaching scaffold.)
- **Tied positions:** in ProteinMPNN, residues that must decode to the **same amino acid** across all
  symmetry-related subunits. Tying makes the assembly symmetric in *sequence*, not just backbone —
  without it the "symmetric" design is a fiction. `scripts/sym_tools.tied_positions()` builds the
  groups.
- **Subunit scRMSD** (self-consistency): design backbone → tied sequence → predict → Cα-RMSD of **one
  subunit** designed-vs-predicted. < ~2.5 Å is the self-consistent bar for a subunit. It says the
  *fold* is recapitulated; it says **nothing** about whether the assembly forms.
- **Interface pAE** (from AF2-Multimer): the predicted aligned error **between** chains at the
  interface. Low inter-chain pAE (**< 10 Å**) signals a confident relative arrangement of subunits.
  It is **necessary but not sufficient** — a confident interface can still be the wrong oligomer.
- **Symmetry RMSD:** does the predicted assembly actually **close into the intended point group**?
  Superpose the predicted assembly onto ideal symmetry axes and measure the deviation. A design can
  have great per-subunit scRMSD and good interface pAE yet fail to close — this is the metric that
  catches it.
- **Oligomeric-state error (wrong-oligomer):** the central failure mode. A subunit designed for C3 may
  prefer a dimer or tetramer. The in-silico tell is when the sequence *also* scores well as the wrong
  order (notebook 04 models alternative states explicitly).

**Why this is hard and what realistic success looks like:** correct-symmetry assembly is genuinely
difficult and **wrong-oligomer outcomes are common.** Interface pAE is a necessary-not-sufficient
filter; AF2-Multimer can be confidently wrong about the global state. Only **nsEM, SEC-MALS, and
native-MS** confirm the true oligomeric state experimentally. A realistic outcome is a **modest
assembly-success rate** with a clear, honest map of which designs are symmetry-clean and which are
ambiguous. **Never claim a cage "will assemble."** Success here = a rigorously filtered, honestly
reported ranked candidate set with a sound validation plan.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### RFdiffusion (symmetric mode)
- **What it does / where it fits:** generates the symmetric backbone — one subunit replicated under
  the chosen point group. This is the generative core (notebook 02).
- **Install:** upstream repo `https://github.com/RosettaCommons/RFdiffusion` — **pin a commit/tag**
  (symmetric-mode flags have changed across versions). The ColabDesign wrappers
  `https://github.com/sokrypton/ColabDesign` are the easiest Colab route. *Verify both still exist
  and pin them with the version-verify cell in `00`/`02`.*
- **Key parameters:** `inference.symmetry` (`C3`/`C4`/`D2`/…), `contigmap.contigs` (per-subunit
  length), `inference.num_designs`, `inference.output_prefix`; potential symmetry/contact potentials
  to encourage closure. **Verify the exact flag names against your pinned release.**
- **Compute:** **A100 recommended.** A full C3/C4/D2 campaign (hundreds of designs) wants an A100/HPC;
  a free **T4 realistically handles only a small C3 demo**.
- **Typical call:**
  ```bash
  # VERIFY flags against the pinned RFdiffusion release before running.
  ./scripts/run_inference.py \
    inference.symmetry=C3 \
    'contigmap.contigs=[60-60]' \
    inference.num_designs=50 \
    inference.output_prefix=results/backbones/C3
  ```

### ProteinMPNN (tied positions)
- **What it does / where it fits:** designs a sequence for the symmetric backbone with **tied
  positions**, so all symmetry-related subunits share one sequence (notebook 02).
- **Install:** bundled with RFdiffusion/ColabDesign, or `https://github.com/dauparas/ProteinMPNN` —
  pin a commit. *Verify the tied-position JSON schema for your version.*
- **Key parameters:** the **tied-positions** specification (the whole point), `--num_seq_per_target`,
  `--sampling_temp` (0.1–0.3 typical), backbone noise. The **tied-vs-untied** benchmark needs both a
  tied and an untied run.
- **Compute:** light — **CPU / T4 fine.** MPNN is not the bottleneck; diffusion + AF2-Multimer are.
- **Typical call:**
  ```bash
  python protein_mpnn_run.py --pdb_path results/backbones/C3_0.pdb \
    --tied_positions_jsonl tied.jsonl --num_seq_per_target 8 \
    --sampling_temp 0.1 --out_folder results/seqs/
  ```

### AF2-Multimer / ColabFold (multimer mode)
- **What it does / where it fits:** predicts the **assembly** (sequence repeated n_subunits times) and
  yields subunit scRMSD, interface pAE, and the structure for the symmetry-RMSD check (notebooks 01–04).
- **Install:** ColabFold (`colabfold`) — pin the commit; use `--model-type alphafold2_multimer_v3`.
  *Verify the multimer model name for your pinned version.*
- **Key parameters:** `--model-type alphafold2_multimer_v3`, `--num-recycle` (3 default; raise for
  hard cases), number of chains = oligomeric order.
- **Compute:** **A100 recommended** for full assemblies; small C3 monomer-sized inputs may run on a
  T4 but are slow.
- **Typical call:**
  ```bash
  colabfold_batch assembly.fasta out/ --model-type alphafold2_multimer_v3 --num-recycle 3
  ```

### SymDesign (concepts), py3Dmol, Biopython
- **SymDesign** (`https://github.com/kylemeador/symdesign`) — a reference for symmetry definitions and
  symmetric docking concepts; conceptual here, not a required install. Pin if you use it.
- **py3Dmol** for in-notebook 3-D visualization of the assembly; **Biopython** for parsing and the
  teaching-grade Cα-RMSD in `shared/filtering_pipeline.py`.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback) + version-verify cell
01_define_explore   → symmetry concepts + metrics table; stand up sym_tools; small-C3 hello-world (mock)
02_design_campaign  → generate C3/C4/D2 (symmetric contigs) + tied ProteinMPNN → results/assemblies.csv
03_filter_and_rank  → multi-layer filter via shared/filtering_pipeline.py (design_type="oligomer") → ranked CSV + figures
04_analysis_figures → symmetry-order-vs-success + tied-vs-untied + wrong-oligomer alternative-state analysis
05_validation_plan  → nsEM/SEC-MALS/native-MS plan + controls + antigen-display extension (vaccine framing)
```
For Project 04 the standard notebook slots map to: *02 = the symmetric design campaign*, *04 = the
symmetry/tied benchmark + wrong-oligomer analysis*, *05 = the assembly validation plan*. The notebook
files are named `02_generate.ipynb`, `04_validate.ipynb`, `05_validation_plan.ipynb`.

## 4. Filtering cutoffs for this design type
Use the shared filter with `design_type="oligomer"` (`DEFAULT_CUTOFFS["oligomer"]`). Start here;
record the cutoffs you actually used.
| Metric | Cutoff | Why |
|--------|--------|-----|
| subunit scRMSD | < 2.5 Å | subunit self-consistency (designed vs predicted subunit) |
| pLDDT | > 80 (mean) | confidence (NOT stability, NOT assembly) |
| pae_interaction | < 10 Å | interface confidence — **necessary, not sufficient** |
| symmetry RMSD | < ~2 Å (project-specific) | does it close into the intended point group? |
| interface energy | more negative = better | interface-energy proxy (rank, not a hard gate) |

> Reminder: **no in-silico metric perfectly separates true from false assemblies.** A confident
> interface pAE does not prove the cage forms or that it forms the *right* oligomer. Filters enrich;
> they do not guarantee. Report wrong-oligomer cases explicitly.

## 5. Interpreting results
- A *good* design: subunit scRMSD < 2.5 Å, mean pLDDT high, interface pAE < 10, symmetry RMSD small,
  and it does **not** also score well as a different oligomeric order.
- A *suspicious* one: good interface pAE but poor symmetry RMSD (confident interface, wrong global
  arrangement), or a sequence that scores comparably as the wrong order (wrong-oligomer risk).
- **Survival-at-each-layer:** count how many designs pass each layer (per symmetry). This is your
  honest funnel; report N pass / N generated.
- **Assembly-success rate:** the fraction of generated designs passing the full `oligomer` filter,
  **per symmetry**. Expect it to be modest and to differ by symmetry order — report it, don't hide it.
- **Symmetry order vs success / tied vs untied:** the two benchmark axes; report each as a rate with N.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / runtime dies | T4 too small for symmetric diffusion / multimer | Use the small C3 demo on T4; move the full C3/C4/D2 campaign to an A100/HPC; reduce `num_designs`/subunit length |
| RFdiffusion symmetric install/flags fail | Upstream notebook/repo or flag names changed | Use the pinned commit; check `inference.symmetry`/contig syntax for that release; log it |
| "Symmetric" design isn't actually symmetric | Tied positions not applied | Verify the tied-positions JSON (use `sym_tools.tied_positions`); confirm symmetry-mates share residues |
| Good interface pAE but assembly won't close | Symmetry RMSD ignored | Add the symmetry-RMSD screen; superpose predicted assembly onto ideal axes; reject high-deviation designs |
| Design prefers the wrong oligomer | Oligomeric-state error | Model alternative states (nb 04); down-rank designs that also score well as the wrong order |
| AF2-Multimer very slow / fails on large order | Many chains on a T4 | Move to A100; reduce recycles for triage; predict the smallest representative assembly first |

## 7. Experimental validation reference (for the D4 plan)
The in-silico filter only *enriches*; the wet-lab assays below determine the **actual** oligomeric
state. This is the core of the D4 plan.
- **Expression:** typically *E. coli* BL21(DE3), 16–18 °C overnight for many designed assemblies; note
  when mammalian expression is needed (e.g., glycosylated antigen-display constructs).
- **Characterization tiers:** go/no-go (express → SDS-PAGE → SEC) → basic (DSF for stability, CD,
  **SEC-MALS** for absolute molar mass / oligomeric number) → deep (**negative-stain EM** for assembly
  architecture, **native-MS** for stoichiometry, then cryo-EM if it warrants it).
- **Controls:** positive (a known nanocage / a verified natural homo-oligomer of the target symmetry),
  negative (a **scrambled-interface** or **monomeric** variant of your own design — it should *not*
  assemble), and an unrelated-protein control. The scrambled-interface negative is the perfect foil:
  same fold, broken assembly.
- **Antigen-display extension:** if grafting an epitope, the displayed antigen must be **neutralizing
  / benign** (vaccine framing) — confirm display by binding a known neutralizing antibody to the
  particle, and assess immunogenicity in the standard preclinical route. See §8.

## 8. Responsible research
Designed nanocages are **dual-use**. See `MASTER_BLUEPRINT.md §7`. **In-scope purpose here:**
vaccine antigen-display and delivery scaffolds (therapeutic / diagnostic / vaccine) — antigen display
means presenting a **neutralizing or benign** antigen to raise a protective immune response (the
RSV-F / SARS-CoV-2-RBD nanoparticle-vaccine paradigm). **Out of scope, and to be refused:** displaying
anything to **enhance pathogen fitness, transmissibility, or virulence**, toxin display/delivery,
biosecurity-screening evasion, or any assembly whose primary purpose is harm. Real gene-synthesis
orders must go through an IGSC-member provider that performs biosecurity screening; wet-lab execution
requires institutional biosafety/ethics approval. If a chosen antigen raises dual-use concern, agree a
defensible neutralizing/vaccine framing with your advisor before proceeding.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions/commits you actually used:
Watson 2023 (RFdiffusion, symmetric), Dauparas 2022 (ProteinMPNN/tied), Evans 2021 (AF2-Multimer),
Wicky 2022 (symmetric assembly validation), plus the nanocage/vaccine references (King, Bale,
Marcandalli) for context.
