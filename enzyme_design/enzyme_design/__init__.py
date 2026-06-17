"""enzyme_design — a tested toolkit for the computational stages (1-6) of the
deep-learning de novo enzyme-design protocol.

The heavy GPU models (RFdiffusion(AA/2/3), LigandMPNN, AlphaFold/ColabFold,
PLACER/ChemNet) are *not* run here; instead this package provides the
reproducible, validated glue around them:

* :mod:`theozyme`  — build/parse Rosetta enzdes ``.cst`` constraint files
* :mod:`contig`    — parse/build/validate RFdiffusion contig strings
* :mod:`pipeline`  — emit validated RFdiffusionAA/LigandMPNN/ColabFold commands
* :mod:`geometry`  — PDB parsing + Kabsch motif Cα-RMSD / ligand RMSD
* :mod:`metrics`   — Stage 5a self-consistency metrics + thresholds
* :mod:`preorg`    — Stage 5b whole-reaction-coordinate (worst-step) scoring
* :mod:`selection` — aggregate ranking + diverse panel selection
* :mod:`registry`  — Stage 6 construct registry + pre-synthesis checks
"""

from . import contig, geometry, metrics, pipeline, preorg, registry, selection, theozyme

__all__ = [
    "contig",
    "geometry",
    "metrics",
    "pipeline",
    "preorg",
    "registry",
    "selection",
    "theozyme",
]

__version__ = "0.1.0"
