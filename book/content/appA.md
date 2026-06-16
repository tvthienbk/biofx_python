# Appendix A · Compute Environment Setup

This appendix is the practical foundation for every Hands-On Lab in the book. De
novo enzyme design is GPU-bound: the structure-generation and folding steps run
deep neural networks that expect an NVIDIA GPU with substantial VRAM, while the
sequence-design and molecular-dynamics steps are comparatively light. The goal
here is to get you a working environment regardless of budget — from a fully free
Colab-and-web-server path that needs no local GPU, through a departmental HPC
cluster, to rented cloud GPUs. Read §A.1 to choose a path, §A.2–A.3 to build a
local stack, §A.4 for cluster submission, and §A.5 if you have no GPU at all.

## A.1 Choosing a Path

Three questions decide your setup:

1. **Do you have access to an NVIDIA GPU with ≥ 24 GB VRAM?** If yes, build the
   local/HPC stack (§A.2). If no, use the web-server and Colab path (§A.5).
2. **Is your work bursty (a few campaigns per term) or sustained?** Bursty work
   favors pay-per-use cloud or free web servers; sustained work justifies a
   cluster allocation or a reserved cloud instance.
3. **Are your inputs confidential?** Unpublished sequences and proprietary
   substrates should not be uploaded to free public web servers; keep those on
   institutional HPC or a private cloud account.

The single most common mistake is over-provisioning. The generative steps that
gate a campaign (RFdiffusion backbone generation, AlphaFold3/Boltz folding) are
*throughput* problems, not *latency* problems: you submit hundreds of jobs and
collect results hours later. A single 24–48 GB GPU run as a queue is sufficient
for an entire course. You do not need a multi-GPU node to learn this material.

## A.2 A Conda Environment for the Design Stack

The reference environment below covers ProteinMPNN/LigandMPNN, OpenMM, and the
PyTorch-based tooling shared across labs. RFdiffusion and AlphaFold3 are
installed into *separate* environments (their dependency pins conflict), a point
emphasized in the Tool Box. Use Miniforge/`mamba` — it resolves these
PyTorch+CUDA solves far faster than stock `conda`.

```bash
# Install Miniforge first (provides mamba). Then:
mamba create -n design python=3.10 -y
mamba activate design

# PyTorch with CUDA 12.1 (match your driver: nvidia-smi shows the max CUDA)
mamba install -y pytorch=2.3 pytorch-cuda=12.1 -c pytorch -c nvidia

# Structure/IO + analysis stack
mamba install -y -c conda-forge \
    numpy=1.26 scipy pandas matplotlib \
    biopython=1.83 biotite mdanalysis \
    openmm=8.1 pdbfixer openff-toolkit \
    foldseek freesasa
pip install ligandmpnn  # ProteinMPNN/LigandMPNN reference impl
```

```yaml
# environment.yml — pin this and commit it with your campaign
name: design
channels: [pytorch, nvidia, conda-forge]
dependencies:
  - python=3.10
  - pytorch=2.3
  - pytorch-cuda=12.1
  - numpy=1.26
  - scipy
  - biopython=1.83
  - openmm=8.1
  - pdbfixer
  - foldseek
  - pip
  - pip: [ligandmpnn]
```

Verify the GPU is visible from PyTorch before running anything expensive:

```python
import torch
print(torch.__version__, torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
```

::: {.reality data-title="Reality Check A.1 · One environment will not hold everything"}
Do not try to install RFdiffusion, ProteinMPNN, and AlphaFold3 into a single
conda environment. AF3 pins JAX/CUDA versions that fight RFdiffusion's PyTorch
pins, and LigandMPNN's torch build can diverge from both. Maintain three named
environments (`rfd`, `design`, `af3`) and orchestrate them from a shell script.
This is normal practice, not a workaround.
:::

## A.3 GPU Memory Guidance Per Tool

VRAM, not FLOPs, is the limiting resource. The values below are practical
working points for typical enzyme-design sizes (single chains of ~100–300
residues plus a small-molecule ligand); requirements scale with sequence length
roughly linearly for MPNN and super-linearly for the folding models.

| Tool | Typical VRAM | Notes |
|---|---|---|
| RFdiffusion / RFdiffusion2 | 8–16 GB | Backbone gen scales with length; 300 aa fits in 16 GB. Runs on a 12 GB card for small motifs. |
| RFdiffusion3 (all-atom) | 16–24 GB | Atomized ligand context raises memory vs. RFD1. |
| ProteinMPNN | 2–4 GB | Very light; even runs on CPU (slowly). Batch many designs per call. |
| LigandMPNN | 4–8 GB | Ligand context adds modest memory over ProteinMPNN. |
| AlphaFold3 (inference) | 24–40 GB | Monomer + ligand commonly fits 24 GB; large complexes need 40–80 GB. |
| Boltz-2 | 16–24 GB | Lighter than AF3 at equal size; good free-weights alternative. |
| OpenMM (explicit-solvent MD) | 4–8 GB | A ~30k-atom solvated system runs comfortably on any modern GPU. |

If you see `CUDA out of memory`, the first remedies are: reduce batch size to 1,
shorten the design length, enable the tool's chunked/low-memory attention flag
if present, or move folding to a higher-VRAM node and keep MPNN on the small one.

## A.4 A SLURM Batch Script

Most academic HPC clusters use SLURM. The script below requests one GPU, loads a
CUDA module, activates the conda environment, and runs ProteinMPNN over a
directory of backbones. Adjust `--partition`, `--gres`, and module names to your
site (run `sinfo` and `module avail cuda` to discover them).

```bash
#!/bin/bash
#SBATCH --job-name=mpnn
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1            # 1 GPU; ProteinMPNN needs little VRAM
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --array=0-9             # 10 backbones, one task each
#SBATCH --output=logs/mpnn_%A_%a.out

module load cuda/12.1
source ~/miniforge3/etc/profile.d/conda.sh
conda activate design

BACKBONES=(backbones/*.pdb)
PDB=${BACKBONES[$SLURM_ARRAY_TASK_ID]}

python run_ligandmpnn.py \
    --pdb_path "$PDB" \
    --out_folder designs/ \
    --num_seq_per_target 8 \
    --sampling_temp 0.1 \
    --ligand_mpnn_use_side_chain_context 1
```

Submit and monitor:

```bash
mkdir -p logs designs
sbatch run_mpnn.slurm
squeue --me            # watch your jobs
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS   # post-mortem usage
```

::: {.method data-title="Method A.1 · Chaining the pipeline across environments"}
1. **Generate** backbones in `rfd` (GPU array job), output to `backbones/`.
2. **Design** sequences in `design` (this script), output FASTA + PDBs.
3. **Fold** the top sequences in `af3` (separate GPU job), compute pLDDT/PAE.
4. **Filter** on CPU (scRMSD, active-site geometry) — no GPU needed.
5. **Simulate** survivors with OpenMM in `design` (short GPU job).
Drive steps 1–5 from one wrapper script that activates the right environment per
stage and writes a manifest CSV so the campaign is reproducible.
:::

## A.5 Free and Web-Server Paths (No Local GPU)

A complete campaign is possible without owning a GPU. This is the recommended
path for resource-limited labs and for coursework.

- **Google Colab.** The free tier provides a T4 (16 GB) suitable for
  ProteinMPNN/LigandMPNN and small RFdiffusion runs; Colab Pro/Pro+ rents L4 or
  A100 GPUs by the hour. Community notebooks (e.g., the ColabDesign and
  ColabFold families) wrap RFdiffusion, ProteinMPNN, and AlphaFold2/3-class
  folding behind a few cells. Sessions are ephemeral — mount Google Drive and
  save outputs immediately.
- **Web design servers.** Several platforms run the full stack as a hosted
  service with a browser UI and queue, removing all installation:

| Platform | Free tier | Backend GPU | Best for |
|---|---|---|---|
| Google Colab (free) | Yes (T4, time-limited) | T4 16 GB | Learning, small RFdiffusion + MPNN runs |
| Colab Pro/Pro+ | Paid (credits) | L4 / A100 | Folding, longer jobs, faster queues |
| Tamarind Bio | Limited free credits | A100 / H100 | One-stop hosted RFdiffusion → MPNN → AF3 pipelines |
| Neurosnap | Limited free credits | A100-class | Menu of design/folding tools, no-code UI |
| Ariax | Trial credits | A100/H100-class | Campaign orchestration and batch design runs |
| Cloud IaaS (AWS/GCP/LambdaLabs) | No (pay-per-use) | T4 → H100 | Sustained, confidential, full control |

For confidential inputs, prefer Colab with a private Drive or a rented cloud
instance over public design servers, and check each platform's data-handling
terms before uploading unpublished sequences.

::: {.toolbox data-title="Tool Box A.1 · Platform and tool versions (as of 2026)"}
**RFdiffusion** (2023, Watson et al.) · **RFdiffusion2** (Ahern et al., 2026, atomized motifs) · **RFdiffusion3** (Butcher et al., 2025).
**ProteinMPNN** (Dauparas et al., 2022) · **LigandMPNN** (2023, ligand-aware).
**AlphaFold3** (Abramson et al., 2024; non-commercial weights) · **Boltz-2** (2025, open weights).
**OpenMM** 8.1 · **PDBFixer** · **Foldseek** v9.
**PyTorch** 2.3 + CUDA 12.1 · **Miniforge/mamba** for environment solves.
**Hosted:** Colab, Tamarind Bio, Neurosnap, Ariax (check each for current tool versions and queue policies).
:::

::: {.reality data-title="Reality Check A.2 · What a course actually needs"}
A full semester of this book runs on one rented A100 (≈ US$1–2/GPU-hour
spot/preemptible) used a few hours per lab, or entirely on free Colab plus a
hosted server's free credits for the folding steps. Budget compute the way you
budget reagents: estimate GPU-hours per lab, request a small block, and queue
jobs rather than buying hardware.
:::
