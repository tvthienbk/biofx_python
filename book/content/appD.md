# Appendix D · The Companion Repository (Lab Index)

Every Hands-On Lab in this book has a corresponding Jupyter notebook in the
companion repository. The repository is designed so that a lab can be run end to
end on a free platform (Colab or a hosted design server; see Appendix A) using
only the inputs provided, and so that a campaign's outputs flow into the next
lab's inputs without manual surgery. This appendix indexes the notebooks, lists
the environment files and datasets, and shows the repository layout.

## D.1 Lab-to-Notebook Index

The labs cluster by Part: Part II (representation and prediction), Part III
(generative models), Part IV (the integrated campaign), and Part V
(build/test/characterize). Each notebook is self-contained but consumes the prior
lab's deliverable where indicated.

| Lab | Chapter | Notebook | Platform | Key inputs | Deliverable |
|---|---|---|---|---|---|
| 6 | Ch 6 | `lab06_pdb_featurization.ipynb` | Colab (CPU) | PDB IDs, target enzyme structure | Per-residue feature table; active-site contact map |
| 8 | Ch 8 | `lab08_folding_as_filter.ipynb` | Colab (T4) / hosted | Candidate sequences (FASTA) | pLDDT/PAE/pTM table; pass/fail folding filter |
| 9 | Ch 9 | `lab09_inverse_folding_mpnn.ipynb` | Colab (T4) | Backbone PDB | 8–16 sequences per backbone (FASTA) |
| 10 | Ch 10 | `lab10_rfdiffusion_intro.ipynb` | Colab (T4/L4) / hosted | Length range, optional hotspots | Unconditioned + scaffolded backbones (PDB) |
| 13 | Ch 13 | `lab13_design_spec.ipynb` | Colab (CPU) | Reaction definition, success criteria | Signed design spec + go/no-go thresholds |
| 14 | Ch 14 | `lab14_theozyme.ipynb` | Colab (CPU) / PyMOL | Substrate, transition-state model | Theozyme geometry (residues + constraints) |
| 15 | Ch 15 | `lab15_motif_scaffolding.ipynb` | Colab (L4) / hosted | Theozyme motif (PDB) | Scaffolded backbones hosting the motif |
| 16 | Ch 16 | `lab16_rfd2_atomized_motif.ipynb` | Hosted (A100) | Atomized catalytic motif + ligand | RFdiffusion2 backbones with ligand context |
| 17 | Ch 17 | `lab17_selfconsistency_filter.ipynb` | Colab (T4) | Backbones + designed sequences | scRMSD table; self-consistency pass list |
| 18 | Ch 18 | `lab18_ligandmpnn_design.ipynb` | Colab (T4) | Backbone + ligand (PDB/SDF) | Ligand-aware sequences (FASTA) |
| 19 | Ch 19 | `lab19_activesite_geometry.ipynb` | Colab (CPU) | Folded designs + theozyme | Geometry-conformance scores; ranked shortlist |
| 20 | Ch 20 | `lab20_md_stability.ipynb` | Colab (T4) / GPU | Top designs (PDB), ligand params | Short-MD RMSF/active-site stability report |
| 21 | Ch 21 | `lab21_select96.ipynb` | Colab (CPU) | All filter tables | Final 96-design order list + diversity check |
| 22 | Ch 22 | `lab22_kinetics_fit.ipynb` | Colab (CPU) | Assay rate vs. [S] data (CSV) | k_cat, K_M, k_cat/K_M with error bars |
| 23 | Ch 23 | `lab23_expression_qc.ipynb` | Colab (CPU) | SEC/SDS-PAGE/nanoDSF data | Expression + fold-quality QC summary |
| 24 | Ch 24 | `lab24_structure_validation.ipynb` | Colab (CPU) | Crystal/cryo-EM model vs. design | Design-vs-experiment RMSD; geometry check |
| 25 | Ch 25 | `lab25_failure_diagnosis.ipynb` | Colab (CPU) | Full campaign manifest | Failure-mode classification; redesign plan |

The labs in Part IV (15–21) form a continuous chain: the output manifest of one
becomes the input of the next, so the campaign can be re-run reproducibly from
the spec (Lab 13) to the order list (Lab 21).

## D.2 Environment Files

Two dependency files are provided. Use `environment.yml` for a full local/HPC
build (mirrors Appendix A); use `requirements.txt` for Colab, where the base
image already supplies CUDA-enabled PyTorch.

```yaml
# environment.yml (local / HPC)
name: edn-labs
channels: [pytorch, nvidia, conda-forge]
dependencies:
  - python=3.10
  - pytorch=2.3
  - pytorch-cuda=12.1
  - numpy=1.26
  - scipy
  - pandas
  - matplotlib
  - biopython=1.83
  - openmm=8.1
  - pdbfixer
  - foldseek
  - jupyterlab
  - pip
  - pip: [ligandmpnn, py3dmol]
```

```text
# requirements.txt (Colab; PyTorch preinstalled in the runtime)
numpy==1.26.*
scipy
pandas
matplotlib
biopython==1.83
py3dmol
ligandmpnn
# RFdiffusion and AlphaFold3/Boltz are installed per-notebook via their
# own install cells, since their pins conflict with the base stack.
```

## D.3 Datasets Provided

The `data/` directory ships everything a lab needs so no external download is
required for a first pass:

- **Target structures** — curated PDB/mmCIF files for the worked-example enzymes
  used in Chapters 6, 14, and 24 (e.g., a serine hydrolase reference for the
  catalytic-triad theozyme).
- **Ligand definitions** — SDF and parameterized small-molecule files (substrate,
  transition-state analog) for LigandMPNN and OpenMM, plus their force-field
  parameter files.
- **Theozyme templates** — pre-built catalytic-motif PDBs for Labs 14–16 so
  scaffolding can be practiced without first solving the theozyme.
- **Example kinetics data** — CSV files of initial rate vs. substrate
  concentration (with replicates and a no-enzyme control) for the Michaelis–Menten
  fit in Lab 22.
- **A reference campaign manifest** — a completed `manifest.csv` from a model
  campaign, used by Labs 21 and 25 to practice selection and failure diagnosis
  without running every upstream GPU step.

## D.4 Repository Layout

```text
edn-labs/
├── README.md
├── environment.yml          # local / HPC build
├── requirements.txt         # Colab build
├── notebooks/
│   ├── lab06_pdb_featurization.ipynb
│   ├── lab08_folding_as_filter.ipynb
│   ├── lab09_inverse_folding_mpnn.ipynb
│   ├── ...                  # one per lab (see §D.1)
│   └── lab25_failure_diagnosis.ipynb
├── data/
│   ├── targets/             # reference enzyme structures (PDB/mmCIF)
│   ├── ligands/             # SDF + force-field params
│   ├── theozymes/           # prebuilt catalytic motifs
│   ├── kinetics/            # rate-vs-[S] CSVs with controls
│   └── manifest_example.csv # completed reference campaign
├── src/
│   ├── geometry.py          # distances, angles, RMSD, scRMSD helpers
│   ├── filters.py           # pLDDT/PAE/scRMSD thresholds; ranking
│   ├── kinetics.py          # Michaelis–Menten fitting
│   └── pipeline.py          # manifest I/O; chains labs together
├── scripts/
│   ├── run_mpnn.slurm       # SLURM example (Appendix A)
│   └── run_campaign.sh      # orchestrates rfd → design → af3 → filter
└── figures/                 # rendered active-site images per design
```

::: {.method data-title="Method D.1 · Running a lab from a clean state"}
1. Open the lab notebook in Colab (or JupyterLab locally).
2. Run the install cell, then `import` the helpers from `src/`.
3. Point the input paths at `data/` (defaults already do) or at your prior lab's
   output in your Drive.
4. Run top to bottom; each notebook writes its deliverable and appends to
   `manifest.csv` so the next lab can find it.
:::

::: {.toolbox data-title="Tool Box D.1 · Repository conventions"}
**Notebooks** pin tool install commands at the top and print versions in the first
cell. **`manifest.csv`** is the single source of truth linking backbones →
sequences → folds → filters → final picks. **`src/`** is plain Python so the same
helpers run in notebooks, scripts, and tests. Commit your `environment.yml` and
`manifest.csv` with each campaign for reproducibility.
:::
