"""Generate the demo/test notebooks for the enzyme_design toolkit.

Run from the ``notebooks/`` directory:  python _build_notebooks.py
This keeps the notebooks reproducible and version-controllable as source.
"""

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

# Every notebook starts by putting the package import root on sys.path so the
# notebook runs whether launched from notebooks/ or the project root.
BOOTSTRAP = """\
import sys, os
# make the package importable from the notebooks/ directory
ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
EXAMPLES = os.path.join(ROOT, "examples")
print("project root:", ROOT)
"""


def md(*lines):
    return new_markdown_cell("\n".join(lines))


def code(src):
    return new_code_cell(src)


def save(nb, name):
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python", "version": "3.11"}
    with open(name, "w") as fh:
        nbf.write(nb, fh)
    print("wrote", name)


# ---------------------------------------------------------------------------
# 00 — end-to-end overview
# ---------------------------------------------------------------------------
def nb_overview():
    nb = new_notebook()
    nb.cells = [
        md(
            "# 00 · End-to-end overview",
            "",
            "This notebook walks Stages **1–6** (the computational half) of the",
            "*de novo* enzyme-design protocol using the `enzyme_design` toolkit.",
            "The heavy GPU models (RFdiffusion, LigandMPNN, AlphaFold, PLACER) are",
            "**not** executed here — instead we build their validated inputs and",
            "process mock outputs, so the whole logic chain is testable on a laptop.",
        ),
        code(BOOTSTRAP),
        md("## Stage 1 — Theozyme (catalytic constraints)"),
        code(
            "from enzyme_design.theozyme import parse_cst\n"
            "theo = parse_cst(open(os.path.join(EXAMPLES, 'theozyme.cst')).read())\n"
            "print('blocks:', len(theo.blocks))\n"
            "print('catalytic residues:', theo.catalytic_residues())\n"
            "print('validation problems:', theo.validate())"
        ),
        md("## Stage 2 — Contig (what is fixed vs generated)"),
        code(
            "from enzyme_design.contig import build_contig\n"
            "contig = build_contig([('A', 84, 87)], flank=(10, 120), total_length=(150, 150))\n"
            "print('contigs   :', contig.to_contigs_string())\n"
            "print('motif res :', contig.motif_residues())\n"
            "print('length    :', contig.length_range(), '-> valid?', contig.validate() == [])"
        ),
        md("## Stage 3 — RFdiffusionAA command (backbone generation)"),
        code(
            "from enzyme_design.pipeline import RFdiffusionAAJob\n"
            "rfd = RFdiffusionAAJob(input_pdb=os.path.join(EXAMPLES, 'active_site.pdb'),\n"
            "                       contig=contig, ligand='LIG', num_designs=1000)\n"
            "print(rfd.to_shell())"
        ),
        md("## Stage 4 — LigandMPNN command (sequence design, catalytic residues fixed)"),
        code(
            "from enzyme_design.pipeline import LigandMPNNJob, consistency_check\n"
            "mpnn = LigandMPNNJob(pdb_path='output/run1/sample_0.pdb',\n"
            "                     fixed_residues=contig.motif_residues(),\n"
            "                     number_of_batches=8, pack_side_chains=True)\n"
            "print(mpnn.to_shell(motif_residues=contig.motif_residues()))\n"
            "print('cross-check problems:', consistency_check(rfd, mpnn))"
        ),
        md(
            "## Stage 5 — Filtering",
            "(a) self-consistency, (b) whole-reaction-coordinate preorganization,",
            "then a combined ranking.",
        ),
        code(
            "import json\n"
            "from enzyme_design.metrics import read_metrics_csv\n"
            "from enzyme_design.preorg import preorg_from_rmsd_samples\n"
            "from enzyme_design.selection import rank_designs, select_diverse\n"
            "\n"
            "rows = read_metrics_csv(os.path.join(EXAMPLES, 'af2_metrics.csv'))\n"
            "data = json.load(open(os.path.join(EXAMPLES, 'preorg_ensembles.json')))\n"
            "profiles = {d: preorg_from_rmsd_samples(d, v['rmsd_samples'], v.get('contacts'))\n"
            "            for d, v in data['designs'].items()}\n"
            "clusters = {'design_0001':'A','design_0006':'A','design_0004':'A',\n"
            "            'design_0002':'B','design_0005':'B','design_0008':'B',\n"
            "            'design_0003':'C','design_0007':'C'}\n"
            "ranked = rank_designs(rows, profiles, clusters)\n"
            "for r in ranked:\n"
            "    flag = 'PASS' if r.passes_filters else 'fail'\n"
            "    print(f'{r.design_id}  [{flag}]  score={r.score:.3f}  cluster={r.cluster}')"
        ),
        md("### Stage 6 — Select a diverse experimental panel and register it"),
        code(
            "from enzyme_design.registry import ConstructRegistry, DesignRecord\n"
            "panel = select_diverse(ranked, n=3, per_cluster=1)\n"
            "print('panel:', [p.design_id for p in panel])\n"
            "\n"
            "reg = ConstructRegistry()\n"
            "seqs = {r.design_id: 'MAGYSTVKDEFHIKLNPQRWG' for r in panel}  # placeholder seqs\n"
            "for p in panel:\n"
            "    reg.add(DesignRecord(p.design_id, protein_seq=seqs[p.design_id],\n"
            "                         catalytic_residues=contig.motif_residues(),\n"
            "                         cluster=p.cluster, score=p.score))\n"
            "print('registry size:', len(reg))\n"
            "for rec in reg:\n"
            "    print(rec.design_id, 'warnings:', rec.pre_synthesis_warnings())"
        ),
        md(
            "**Done.** From one active-site specification we produced validated",
            "generation/design commands and a filtered, diversity-aware panel — the",
            "exact hand-off to gene synthesis (Stage 6 → 7).",
        ),
    ]
    return nb


# ---------------------------------------------------------------------------
# 01 — theozyme + contig
# ---------------------------------------------------------------------------
def nb_theozyme_contig():
    nb = new_notebook()
    nb.cells = [
        md(
            "# 01 · Theozyme & contig (Stages 1–2)",
            "",
            "Build a catalytic-constraint (`.cst`) theozyme and a validated",
            "RFdiffusion contig, and exercise the guard-rails the protocol calls out.",
        ),
        code(BOOTSTRAP),
        md("## Build a theozyme from catalytic geometry"),
        code(
            "from enzyme_design.theozyme import (Theozyme, ConstraintBlock, AtomMap,\n"
            "                                     GeometricConstraint)\n"
            "block = ConstraintBlock(\n"
            "    res1=AtomMap(1, ['OG','CB','CA'], ['SER']),\n"
            "    res2=AtomMap(2, ['C1','O1','O2'], ['LIG']),\n"
            "    constraints=[\n"
            "        GeometricConstraint('distanceAB', 2.80, 0.20, 100.0),\n"
            "        GeometricConstraint('angle_A', 105.0, 5.0, 50.0, 360.0),\n"
            "    ],\n"
            "    comment='Ser-OG nucleophilic attack on substrate carbonyl')\n"
            "theo = Theozyme([block], title='demo')\n"
            "print(theo.to_cst())"
        ),
        md(
            "## Round-trip: parse the `.cst` back",
            "Serialise → parse must preserve atoms, residue identities, constraints.",
        ),
        code(
            "from enzyme_design.theozyme import parse_cst\n"
            "parsed = parse_cst(theo.to_cst())\n"
            "assert parsed.blocks[0].res1.atoms == ['OG','CB','CA']\n"
            "assert parsed.catalytic_residues() == ['SER']\n"
            "print('round-trip OK; catalytic residues =', parsed.catalytic_residues())"
        ),
        md("## Build & validate a contig"),
        code(
            "from enzyme_design.contig import build_contig, parse_contig\n"
            "c = build_contig([('A', 84, 87)], flank=(10, 120), total_length=(150, 150))\n"
            "print('contigs:', c.to_hydra()[0])\n"
            "print('length :', c.to_hydra()[1])\n"
            "print('residue range:', c.length_range(), '  valid:', c.validate() == [])"
        ),
        md(
            "## Guard-rail 1 — bare integers are rejected",
            "The protocol warns: *always give ranges (e.g. `16-16`), never bare",
            "integers.* The parser turns that mistake into a hard error.",
        ),
        code(
            "from enzyme_design.contig import ContigError\n"
            "try:\n"
            "    parse_contig(\"['120,A84-87,10-120']\")\n"
            "except ContigError as e:\n"
            "    print('correctly rejected:', e)"
        ),
        md(
            "## Guard-rail 2 — impossible total length is caught",
            "`contigmap.length` must be reachable from the segment ranges.",
        ),
        code(
            "bad = parse_contig(\"['10-20,A84-87,10-20']\", '150-150')\n"
            "print('problems:', bad.validate())"
        ),
        md("## Multi-island motif (typical real active site)"),
        code(
            "multi = build_contig([('A', 84, 85), ('A', 120, 121)],\n"
            "                     flank=(10, 50), inter_island=(5, 30),\n"
            "                     total_length=(80, 120))\n"
            "print(multi.to_contigs_string())\n"
            "print('motif residues:', multi.motif_residues())"
        ),
    ]
    return nb


# ---------------------------------------------------------------------------
# 02 — pipeline commands
# ---------------------------------------------------------------------------
def nb_pipeline():
    nb = new_notebook()
    nb.cells = [
        md(
            "# 02 · Pipeline commands (Stages 3–5a)",
            "",
            "Turn a typed config into the exact, validated command lines for",
            "RFdiffusionAA, LigandMPNN and ColabFold — and catch the mistakes the",
            "protocol flags before a GPU job ever starts.",
        ),
        code(BOOTSTRAP),
        code(
            "from enzyme_design.contig import build_contig\n"
            "from enzyme_design.pipeline import (RFdiffusionAAJob, LigandMPNNJob,\n"
            "                                     ColabFoldJob, consistency_check,\n"
            "                                     PipelineError)\n"
            "contig = build_contig([('A', 84, 87)], flank=(10, 120), total_length=(150, 150))"
        ),
        md("## Stage 3 — RFdiffusionAA"),
        code(
            "rfd = RFdiffusionAAJob(input_pdb='input/active_site.pdb', contig=contig,\n"
            "                       ligand='LIG', num_designs=1000, diffuser_T=200,\n"
            "                       guide_scale=1.0)\n"
            "print(rfd.to_shell())"
        ),
        md("## Stage 4 — LigandMPNN (catalytic residues fixed)"),
        code(
            "mpnn = LigandMPNNJob(pdb_path='output/run1/sample_0.pdb',\n"
            "                     fixed_residues=contig.motif_residues(),\n"
            "                     number_of_batches=8, pack_side_chains=True)\n"
            "print(mpnn.to_shell(motif_residues=contig.motif_residues()))"
        ),
        md(
            "### The CRITICAL STEP, enforced",
            "If a catalytic residue is *not* held fixed, the command builder refuses.",
        ),
        code(
            "leaky = LigandMPNNJob(pdb_path='s.pdb', fixed_residues=['A84','A85'])  # missing 86,87\n"
            "try:\n"
            "    leaky.to_argv(motif_residues=contig.motif_residues())\n"
            "except PipelineError as e:\n"
            "    print('blocked:', e)"
        ),
        md("## Stage 5a — ColabFold single-sequence reprediction"),
        code(
            "af = ColabFoldJob(input_fasta='designs.fasta', out_dir='af2/run1/',\n"
            "                  num_models=5, msa_mode='single_sequence')\n"
            "print(af.to_shell())"
        ),
        md("## Whole-pipeline cross-check"),
        code(
            "problems = consistency_check(rfd, mpnn)\n"
            "print('consistency problems:', problems or 'none — diffusion & design agree')"
        ),
    ]
    return nb


# ---------------------------------------------------------------------------
# 03 — filtering & ranking
# ---------------------------------------------------------------------------
def nb_filtering():
    nb = new_notebook()
    nb.cells = [
        md(
            "# 03 · Filtering & ranking (Stage 5)",
            "",
            "The decisive stage. (a) self-consistency, (b) **whole-reaction-coordinate",
            "preorganization** scored by the *worst* mechanistic step, and a combined",
            "diversity-aware ranking.",
        ),
        code(BOOTSTRAP),
        md("## Stage 5a — self-consistency hard filters"),
        code(
            "from enzyme_design.metrics import read_metrics_csv, Thresholds\n"
            "rows = read_metrics_csv(os.path.join(EXAMPLES, 'af2_metrics.csv'))\n"
            "for m in rows:\n"
            "    ok, reasons = m.evaluate()\n"
            "    print(f\"{m.design_id}: {'PASS' if ok else 'FAIL'}\", '' if ok else reasons)"
        ),
        md(
            "## Stage 5b — preorganization across the reaction coordinate",
            "We rank by the **worst step**, not the average. `design_0004` looks fine",
            "on average but collapses at the *intermediate* — exactly the failure mode",
            "the protocol says single-TS filtering would miss.",
        ),
        code(
            "import json\n"
            "from enzyme_design.preorg import preorg_from_rmsd_samples\n"
            "data = json.load(open(os.path.join(EXAMPLES, 'preorg_ensembles.json')))\n"
            "profiles = {d: preorg_from_rmsd_samples(d, v['rmsd_samples'], v.get('contacts'))\n"
            "            for d, v in data['designs'].items()}\n"
            "for did, p in profiles.items():\n"
            "    w = p.worst_step()\n"
            "    print(f'{did}: worst={w.state} (score {p.worst_score():.2f}), '\n"
            "          f'mean {p.mean_score():.2f}, passes={p.passes()}, '\n"
            "          f'failing={p.failing_steps()}')"
        ),
        md("## Combined ranking + diverse selection"),
        code(
            "from enzyme_design.selection import rank_designs, select_diverse\n"
            "clusters = {'design_0001':'A','design_0006':'A','design_0004':'A',\n"
            "            'design_0002':'B','design_0005':'B','design_0008':'B',\n"
            "            'design_0003':'C','design_0007':'C'}\n"
            "ranked = rank_designs(rows, profiles, clusters)\n"
            "print(f\"{'design':14}{'pass':6}{'score':8}{'cluster':8}\")\n"
            "for r in ranked:\n"
            "    print(f'{r.design_id:14}{str(r.passes_filters):6}{r.score:<8.3f}{r.cluster}')\n"
            "print()\n"
            "panel = select_diverse(ranked, n=3, per_cluster=1)\n"
            "print('selected panel (diverse):', [(p.design_id, p.cluster) for p in panel])"
        ),
    ]
    return nb


# ---------------------------------------------------------------------------
# 04 — registry & panel
# ---------------------------------------------------------------------------
def nb_registry():
    nb = new_notebook()
    nb.cells = [
        md(
            "# 04 · Construct registry & gene order (Stage 6)",
            "",
            "Register the chosen panel, run pre-synthesis sequence checks (free",
            "cysteines, internal restriction sites, frame), and archive the full",
            "table to CSV — *including the denominator*, per the reproducibility",
            "checklist.",
        ),
        code(BOOTSTRAP),
        code(
            "from enzyme_design.registry import (ConstructRegistry, DesignRecord,\n"
            "                                     restriction_sites, free_cysteines)\n"
            "reg = ConstructRegistry()\n"
            "reg.add(DesignRecord('design_0006', protein_seq='MAGYSTVKDEFHIKLNPQRWG',\n"
            "                     catalytic_residues=['A84','A85','A86','A87'],\n"
            "                     cluster='A', score=0.05,\n"
            "                     dna_seq='ATGGCTGGTTATAGTACCGTTAAA'))\n"
            "reg.add(DesignRecord('design_0001', protein_seq='MAGCSTVKDEFHIKLNPQRWG',\n"
            "                     catalytic_residues=['A84','A85','A86','A87'],\n"
            "                     cluster='A', score=0.11,\n"
            "                     dna_seq='ATGGCTTGCAGCACCCATATGAAA'))  # has Cys + NdeI\n"
            "print('registry size:', len(reg))"
        ),
        md("## Pre-synthesis warnings"),
        code(
            "for rec in reg:\n"
            "    print(rec.design_id, '->', rec.pre_synthesis_warnings() or 'clean')"
        ),
        md("## Spot-check the helpers"),
        code(
            "print('free cysteines in MAGCSTV...:', free_cysteines('MAGCSTVKDEFHIKLNPQRWG'))\n"
            "print('restriction sites:', restriction_sites('ATGGCTTGCAGCACCCATATGAAA'))"
        ),
        md("## Archive to CSV and reload"),
        code(
            "reg.to_csv('panel_registry.csv')\n"
            "reloaded = ConstructRegistry.from_csv('panel_registry.csv')\n"
            "print('reloaded:', len(reloaded), 'records')\n"
            "r = reloaded.get('design_0006')\n"
            "print('catalytic residues:', r.catalytic_residues, ' score:', r.score)\n"
            "print(open('panel_registry.csv').read())"
        ),
    ]
    return nb


if __name__ == "__main__":
    save(nb_overview(), "00_end_to_end_overview.ipynb")
    save(nb_theozyme_contig(), "01_theozyme_and_contig.ipynb")
    save(nb_pipeline(), "02_pipeline_commands.ipynb")
    save(nb_filtering(), "03_filtering_and_ranking.ipynb")
    save(nb_registry(), "04_registry_and_panel.ipynb")
