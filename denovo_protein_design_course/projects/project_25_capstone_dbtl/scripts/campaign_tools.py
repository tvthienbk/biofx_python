"""
campaign_tools.py — design-campaign + scoring wrappers for the Project 25 capstone.

The capstone runs a COMPLETE design campaign on a student-chosen, advisor-approved target. The worked
example in the notebooks is a BINDER campaign (the Project 06 pattern), but the integration pattern is
identical for any `design_type` (binder | antibody | enzyme | monomer) — only the real backend you
swap in changes. This module keeps the notebooks thin and runs WITHOUT a GPU via a deterministic
`mock` backend:

    parse_hotspots(spec)                                  -> tuple
    generate_designs(target, hotspots, n, design_type, tool="mock") -> list[CampaignDesign]
    score_designs(designs, tool="mock")                   -> list[CampaignDesign]  (fills metrics)
    pool_to_df(designs)                                   -> pandas.DataFrame
    hotspot_overlap(contacts, hotspots)                   -> float

DESIGN NOTE FOR STUDENTS
------------------------
Real generation (RFdiffusion/BindCraft/RFantibody/RFdiffusion2) and AF2(-Multimer) are heavy and want
an A100 (see MANUAL.md §2). Each real backend is a clearly-marked TODO you complete/verify on Colab;
the heavy import is lazy INSIDE the function. The module imports fine here with no GPU. The `mock`
backend is DETERMINISTIC (seeded by target/hotspots/index) so you can develop the plumbing —
generation, scoring, the cohort-table hand-off, the filter — before spending GPU time. NEVER present
mock numbers as real results: they are SYNTHETIC / EXAMPLE_DATA by construction.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  RFdiffusion   https://github.com/RosettaCommons/RFdiffusion
  BindCraft     https://github.com/martinpacesa/BindCraft
  ColabFold     https://github.com/sokrypton/ColabFold   (AF2 / AF2-Multimer)
  (antibody) RFantibody / (enzyme) RFdiffusion2 / Riff-Diff — see your family template project.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

import pandas as pd

_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction (EXAMPLE_DATA)"


@dataclass
class CampaignDesign:
    """One designed protein from the capstone campaign (any design_type)."""
    design_id: str
    sequence: str
    design_type: str = "binder"          # binder | antibody | enzyme | monomer
    target: str = "EXAMPLE_TARGET"
    hotspots: tuple = ()
    length: Optional[int] = None
    # filled by score_designs():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None
    solubility: Optional[float] = None
    tm_to_pdb: Optional[float] = None
    catalytic_geom_rmsd: Optional[float] = None   # enzymes only
    contact_residues: tuple = ()
    synthetic: bool = False
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


def _hashints(*parts) -> int:
    """Stable integer hash (NOT Python's salted hash) for deterministic mock numbers."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16)


def _mock_sequence(seed_int: int, length: int) -> str:
    seq, x = [], seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple ('A56,A66' or ['A56','A66'] -> ('A56','A66'))."""
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the target hotspots the design actually contacts (epitope-competition proxy)."""
    hs = set(parse_hotspots(hotspots))
    if not hs:
        return 0.0
    contacts = set(parse_hotspots(contact_residues))
    return round(len(hs & contacts) / len(hs), 3)


# --------------------------------------------------------------------------- #
# Generation (mock deterministic; real backends behind TODOs).
# --------------------------------------------------------------------------- #
def generate_designs(target: str, hotspots, n: int = 200, design_type: str = "binder",
                     tool: str = "mock", length_range=(40, 90), **kwargs) -> list[CampaignDesign]:
    """Generate a design pool against `target` at `hotspots`.

    tool="mock" -> deterministic SYNTHETIC designs (no GPU; build the plumbing).
    tool="rfdiffusion"/"bindcraft"/"rfantibody"/"rfdiffusion2" -> real backend (A100; see MANUAL.md §2).
    """
    tool = tool.lower()
    hs = parse_hotspots(hotspots)
    if tool == "mock":
        out = []
        for i in range(n):
            seed = _hashints(design_type, target, hs, i)
            length = length_range[0] + (seed % max(1, (length_range[1] - length_range[0] + 1)))
            seq = _mock_sequence(seed, length)
            n_contact = 1 + (seed % max(1, len(hs))) if hs else 0
            contacts = tuple(hs[:n_contact]) if hs else ()
            out.append(CampaignDesign(
                design_id=f"EXAMPLE_DATA_{design_type}_{i:04d}",
                sequence=seq, design_type=design_type, target=target, hotspots=hs,
                length=length, contact_residues=contacts, synthetic=True, notes=[_MOCK_FLAG]))
        return out
    if tool in ("rfdiffusion", "bindcraft", "freebindcraft", "rfantibody", "rfdiffusion2", "riffdiff"):
        # TODO (Colab, A100): run the chosen generator against the cleaned target at the hotspots,
        #   then ProteinMPNN/LigandMPNN for sequences. See the matching family template project
        #   (06 binders / 17 antibodies / 18 enzymes) and MANUAL.md §2. Pin commits; verify URLs.
        raise NotImplementedError(
            f"Wire up the real {tool!r} backend here (A100). Develop with tool='mock' first; "
            "see MANUAL.md §2 and your design_type's family template project.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion, bindcraft, rfantibody, rfdiffusion2")


# --------------------------------------------------------------------------- #
# Scoring (mock deterministic; AF2 / AF2-Multimer behind a TODO).
# --------------------------------------------------------------------------- #
def score_designs(designs: list[CampaignDesign], tool: str = "mock") -> list[CampaignDesign]:
    """Fill each design's metric fields. tool='mock' => deterministic SYNTHETIC metrics."""
    tool = tool.lower()
    for d in designs:
        if tool == "mock":
            h = _hashints("score", d.target, d.hotspots, d.sequence)
            d.plddt = float(70 + (h % 30))                      # 70-99
            d.pae_interaction = float(4 + (h % 16))             # 4-19 (lower better)
            d.scrmsd = round(0.8 + (h % 350) / 100.0, 3)        # 0.8-4.3 Å
            d.shape_complementarity = round(0.45 + (h % 45) / 100.0, 3)  # 0.45-0.89
            d.rosetta_dG = round(-50.0 + (_hashints("dG", d.design_id) % 48), 2)  # ~ -50..-3 REU
            d.solubility = round(-1.5 + (_hashints("sol", d.design_id) % 30) / 10.0, 3)  # -1.5..1.4
            d.tm_to_pdb = round(0.25 + (_hashints("tm", d.design_id) % 60) / 100.0, 3)   # 0.25-0.84
            if d.design_type == "enzyme":
                d.catalytic_geom_rmsd = round(0.2 + (_hashints("cat", d.design_id) % 130) / 100.0, 3)  # 0.2-1.5 Å
            d.synthetic = True
            if _MOCK_FLAG not in d.notes:
                d.notes.append(_MOCK_FLAG)
        elif tool in ("af2", "colabfold", "af2_multimer", "multimer"):
            # TODO (Colab): run AF2(-Multimer) on each (design[, target]) and parse
            #   plddt / pae_interaction / scrmsd / shape_complementarity. ColabFold; pin a commit.
            raise NotImplementedError(
                "Wire up AF2(-Multimer) scoring here (ColabFold). Develop with tool='mock' first.")
        else:
            raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")
    return designs


def pool_to_df(designs: list[CampaignDesign]) -> pd.DataFrame:
    """Tidy one-row-per-design table with the columns the cohort table + shared filter consume."""
    rows = []
    for d in designs:
        rows.append(dict(
            design_id=d.design_id, design_type=d.design_type, target=d.target,
            length=d.length, sequence=d.sequence,
            scrmsd=d.scrmsd, plddt=d.plddt, pae_interaction=d.pae_interaction,
            solubility=d.solubility, rosetta_dG=d.rosetta_dG,
            shape_complementarity=d.shape_complementarity, tm_to_pdb=d.tm_to_pdb,
            catalytic_geom_rmsd=d.catalytic_geom_rmsd,
            contact_residues=",".join(d.contact_residues),
            hotspot_overlap=hotspot_overlap(d.contact_residues, d.hotspots),
            synthetic=d.synthetic,
        ))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Plumbing smoke test (no GPU, no heavy deps). All numbers are SYNTHETIC / EXAMPLE_DATA.
    HS = parse_hotspots("A56,A66,A115")
    pool = generate_designs("EXAMPLE_TARGET", HS, n=5, design_type="binder", tool="mock")
    score_designs(pool, tool="mock")
    df = pool_to_df(pool)
    print("mock campaign pool:", df.shape)
    print(df[["design_id", "design_type", "scrmsd", "pae_interaction", "plddt", "rosetta_dG", "synthetic"]].to_string(index=False))
    print("\\nREMINDER: every number above is SYNTHETIC (mock / EXAMPLE_DATA) — never report it as a real result.")
