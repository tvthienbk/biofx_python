# Appendix B · Python, PyMOL & ChimeraX Primer for Designers

You do not need to be a software engineer to run the labs in this book, but you
do need to read and adapt short scripts: parse a PDB, measure a distance between
two catalytic atoms, superimpose a design on its target, and render a
publication figure. This appendix is a working minimum — enough Biopython,
NumPy, PyMOL, and ChimeraX to execute every lab and to inspect your own results
critically. Each block is correct and runnable; copy, then change the paths and
selections to your case.

## B.1 Biopython: Parsing and Measuring Structures

Biopython's `Bio.PDB` parses a structure into a nested hierarchy:
Structure → Model → Chain → Residue → Atom. Get an atom's coordinate with
`atom.coord` (a NumPy array of x, y, z in ångströms).

```python
from Bio.PDB import PDBParser
parser = PDBParser(QUIET=True)
structure = parser.get_structure("design", "design.pdb")
model = structure[0]                 # first model
chain = model["A"]                   # chain A
res = chain[57]                      # residue with sequence number 57
print(res.resname, [a.name for a in res])   # e.g. HIS ['N','CA','C','O','CB',...]
```

**Distances and angles.** Atom subtraction returns the interatomic distance
directly; angles use vectors. This is the core of every active-site geometry
check.

```python
import numpy as np
from Bio.PDB import calc_angle, calc_dihedral

his = chain[57]; ser = chain[195]
d = his["NE2"] - ser["OG"]                 # His Nε2 ... Ser Oγ distance (Å)
print(f"His57(NE2)-Ser195(OG): {d:.2f} A")

# Angle (in radians) at the middle atom; convert to degrees
ang = calc_angle(his["NE2"].get_vector(),
                 ser["OG"].get_vector(),
                 ser["CB"].get_vector())
print(f"angle: {np.degrees(ang):.1f} deg")
```

**RMSD by superposition.** Use `Superimposer` to fit one set of atoms onto
another (it solves the optimal rotation/translation, the Kabsch problem) and
report the RMSD. Always superpose *matched* atoms — e.g., Cα atoms of aligned
residues.

```python
from Bio.PDB import Superimposer
ref_atoms = [chainA[i]["CA"] for i in common_resids]
mob_atoms = [chainB[i]["CA"] for i in common_resids]
sup = Superimposer()
sup.set_atoms(ref_atoms, mob_atoms)        # computes optimal fit
print(f"Cα RMSD: {sup.rms:.2f} A")
sup.apply(mobile_structure.get_atoms())    # move the mobile copy onto ref
```

## B.2 A NumPy Snippet: Vectorized RMSD

When you have two coordinate arrays already aligned (same atom order), RMSD is a
one-liner. This is faster than per-atom loops and is how scRMSD is computed over
thousands of designs (see Appendix C and Chapter 17).

```python
import numpy as np

def rmsd(P, Q):
    """RMSD between two (N,3) coordinate arrays, no superposition."""
    diff = P - Q
    return np.sqrt((diff * diff).sum() / P.shape[0])

# Kabsch superposition then RMSD:
def kabsch_rmsd(P, Q):
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    H = Pc.T @ Qc
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T                      # optimal rotation
    return rmsd(Pc @ R.T, Qc)
```

## B.3 Reading and Writing FASTA and PDB

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

# Read a multi-FASTA (e.g., LigandMPNN output)
for rec in SeqIO.parse("designs.fasta", "fasta"):
    print(rec.id, len(rec.seq), str(rec.seq)[:20])

# Write a FASTA for gene synthesis ordering
records = [SeqRecord(Seq(s), id=f"design_{i}", description="")
           for i, s in enumerate(sequences)]
SeqIO.write(records, "to_order.fasta", "fasta")
```

```python
# Write a (possibly modified) structure back to PDB
from Bio.PDB import PDBIO
io = PDBIO()
io.set_structure(structure)
io.save("design_aligned.pdb")
```

::: {.method data-title="Method B.1 · Extract a catalytic-residue subset to PDB"}
1. Parse the structure and list the catalytic residue numbers (e.g., 57, 102, 195).
2. Use a `Select` subclass that returns `True` only for those residues.
3. Save with `io.save("triad.pdb", CatalyticSelect())`.
This isolates the catalytic constellation for quick geometry checks and figures.
:::

```python
from Bio.PDB import Select
class CatalyticSelect(Select):
    def __init__(self, resids): self.resids = set(resids)
    def accept_residue(self, residue):
        return residue.id[1] in self.resids
io.save("triad.pdb", CatalyticSelect([57, 102, 195]))
```

## B.4 PyMOL Scripting Cheat-Sheet

PyMOL runs commands interactively, from a `.pml` script (`pymol -cq script.pml`),
or from Python via `from pymol import cmd`. The command forms below are the ones
you will reuse: load, select catalytic residues, align a design to its target,
measure a distance, and ray-trace a figure.

```python
# A complete PyMOL .pml script: load, align, annotate, render
load target.pdb, target
load design.pdb, design
align design, target            # superpose; prints RMSD to log

bg_color white
hide everything
show cartoon
color grey80, target
color marine, design

# Select and show the catalytic triad on the design
select triad, design and resi 57+102+195
show sticks, triad
color yellow, triad and elem C
label triad and name CA, "%s%s" % (resn, resi)

# Measure the His-Ser hydrogen-bonding distance
distance dHS, design and resi 57 and name NE2, \
              design and resi 195 and name OG

set ray_shadows, 0
set ray_opaque_background, 0
ray 1600, 1200                  # high-res render
png active_site.png, dpi=300
```

Useful one-liners:

```python
# In a PyMOL session
cmd.get_distance("/design//A/57/NE2", "/design//A/195/OG")   # numeric distance
cmd.rms_cur("design and name CA", "target and name CA")      # RMSD, no fitting
cmd.super("design", "target")                                # sequence-independent align
```

## B.5 ChimeraX Equivalents

ChimeraX uses a similar command language; equivalents to the PyMOL block above:

```text
open target.pdb        # model #1
open design.pdb        # model #2
matchmaker #2 to #1    # superpose design onto target (prints RMSD)

set bgColor white
hide atoms
show cartoon
color #1 gray
color #2 cornflowerblue

# Catalytic triad on the design (#2)
select #2:57,102,195
show sel atoms
style sel stick
color sel byhetero          # color by element, keep C in model color

# Distance between His Nε2 and Ser Oγ
distance #2:57@NE2 #2:195@OG

# Publication render
lighting soft
graphics silhouettes true
save active_site.png width 1600 height 1200 supersample 3
```

::: {.toolbox data-title="Tool Box B.1 · Visualization and scripting (versions)"}
**Python** 3.10 · **Biopython** 1.83 · **NumPy** 1.26 · **Biotite** (alternative parser) · **MDAnalysis** (trajectories).
**PyMOL** (open-source 3.x or Schrödinger Incentive) — `pymol -cq` for headless rendering.
**ChimeraX** 1.8+ (UCSF) — `chimerax --nogui script.cxc` for headless runs.
Both PyMOL and ChimeraX read mmCIF and PDB; prefer mmCIF for large complexes.
:::

::: {.reality data-title="Reality Check B.1 · Always eyeball the active site"}
Numeric filters miss things a human catches instantly: a catalytic residue
pointing into solvent, a ligand clashing with the backbone, a "triad" whose
geometry is right but whose side chains are buried. Render every shortlisted
design's active site and look at it. Five minutes of inspection per candidate
saves a wasted gene-synthesis order.
:::
