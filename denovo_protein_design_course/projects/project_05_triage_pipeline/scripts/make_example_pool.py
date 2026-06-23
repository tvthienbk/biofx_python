#!/usr/bin/env python3
"""
make_example_pool.py — generate the labeled, SYNTHETIC teaching pool for Project 05.

WHY THIS EXISTS
---------------
The triage engine (shared/filtering_pipeline.py) scores a *design pool*. In production that pool
comes from Projects 01/03 or public design sets (with predictions). For TEACHING and TESTING we need
a pool we can develop the layers against with NO GPU and with KNOWN ANSWERS — so this script emits a
clearly-synthetic pool with *planted* known-good and known-bad designs.

EVERY ROW IS SYNTHETIC. `design_id` is prefixed `EXAMPLE_DATA_`, and a hidden `truth` column
(good/bad) records the planted label so notebook 04 can measure enrichment. NEVER present any number
derived from this pool as a real experimental result.

The pool is MIXED across design types (monomer/binder/enzyme/antibody/oligomer). It contains:
  * PLANTED known-GOOD designs that pass every layer for their type,
  * PLANTED known-BAD designs that each fail a SPECIFIC layer (so layers are individually testable),
  * AMBIGUOUS designs near the cutoffs, so enrichment is imperfect and the discrimination problem is
    visible (some duds survive; some good designs get cut).

The planted-good / planted-bad designs are also exported (via known_designs()) for the unit tests in
scripts/test_filtering.py, so the tests and the pool stay in sync.

Run:  python scripts/make_example_pool.py            # writes results/pool.csv
      python scripts/make_example_pool.py --n 300    # bigger pool
      python scripts/make_example_pool.py --out results/pool.csv
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

SEED = 20240605  # deterministic: the pool is identical every run (reproducibility is graded).

# Columns mirror the fields of filtering_pipeline.Design that this pool populates, plus the hidden
# label and the design type. `truth` is the PLANTED ground truth, NOT a real outcome.
COLUMNS = [
    "design_id", "design_type", "truth",
    "scrmsd", "plddt", "plddt_catalytic", "pae_interaction", "catalytic_geom_rmsd",
    "scrmsd_orthogonal", "solubility", "rosetta_dG", "shape_complementarity", "md_rmsd",
    "note",
]

# Per-type "comfortably passing" centers, chosen to clear DEFAULT_CUTOFFS for that type with margin.
# (See filtering_pipeline.DEFAULT_CUTOFFS; these are EXAMPLE_DATA, not measured values.)
GOOD_CENTERS = {
    "monomer":  dict(scrmsd=1.2, plddt=92, pae=6,  scrmsd_orthogonal=1.4, solubility=0.6,
                     rosetta_dG=None, sc=None, md_rmsd=1.5, plddt_cat=None, cat_geom=None),
    "binder":   dict(scrmsd=1.6, plddt=88, pae=6,  scrmsd_orthogonal=1.8, solubility=0.4,
                     rosetta_dG=-42, sc=0.72, md_rmsd=2.0, plddt_cat=None, cat_geom=None),
    "enzyme":   dict(scrmsd=1.2, plddt=92, pae=6,  scrmsd_orthogonal=1.5, solubility=0.5,
                     rosetta_dG=None, sc=None, md_rmsd=1.6, plddt_cat=95, cat_geom=0.3),
    "antibody": dict(scrmsd=2.2, plddt=80, pae=8,  scrmsd_orthogonal=2.1, solubility=0.3,
                     rosetta_dG=None, sc=None, md_rmsd=2.2, plddt_cat=None, cat_geom=None),
    "oligomer": dict(scrmsd=1.7, plddt=88, pae=6,  scrmsd_orthogonal=1.9, solubility=0.5,
                     rosetta_dG=-38, sc=0.68, md_rmsd=2.0, plddt_cat=None, cat_geom=None),
}

DESIGN_TYPES = list(GOOD_CENTERS)


def _round(d: dict) -> dict:
    """Round floats for a tidy CSV; leave None as None."""
    out = {}
    for k, v in d.items():
        out[k] = round(float(v), 3) if isinstance(v, (int, float)) else v
    return out


def known_designs() -> list[dict]:
    """Return the explicit PLANTED designs (one good + several layer-specific bad per concept).

    These are the ground-truth fixtures the unit tests assert on. Each bad design fails exactly the
    layer named in its note (good static metrics elsewhere), so layers are individually testable.
    Values are EXAMPLE_DATA.
    """
    rows: list[dict] = []

    # --- one clean known-GOOD per design type (passes L1-L4 for that type) ---
    for dt in DESIGN_TYPES:
        c = GOOD_CENTERS[dt]
        rows.append(_round(dict(
            design_id=f"EXAMPLE_DATA_GOOD_{dt}", design_type=dt, truth="good",
            scrmsd=c["scrmsd"], plddt=c["plddt"], plddt_catalytic=c["plddt_cat"],
            pae_interaction=c["pae"], catalytic_geom_rmsd=c["cat_geom"],
            scrmsd_orthogonal=c["scrmsd_orthogonal"], solubility=c["solubility"],
            rosetta_dG=c["rosetta_dG"], shape_complementarity=c["sc"], md_rmsd=c["md_rmsd"],
            note="planted known-good: passes all layers for its type",
        )))

    # --- known-BAD: fails Layer 1 (self-consistency) — high scRMSD despite ok pLDDT (monomer) ---
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L1_scrmsd", design_type="monomer", truth="bad",
        scrmsd=3.4, plddt=90, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=1.5, solubility=0.5, rosetta_dG=None, shape_complementarity=None, md_rmsd=1.5,
        note="planted known-bad: fails L1 (scRMSD 3.4 > 2.0) — confident about the WRONG fold",
    )))
    # known-BAD: fails Layer 1 via low pLDDT (monomer)
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L1_plddt", design_type="monomer", truth="bad",
        scrmsd=1.5, plddt=72, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=1.6, solubility=0.5, rosetta_dG=None, shape_complementarity=None, md_rmsd=1.6,
        note="planted known-bad: fails L1 (pLDDT 72 < 85)",
    )))

    # --- known-BAD: fails Layer 2 (orthogonal) — AF2 likes it, ESMFold/Boltz disagree (monomer) ---
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L2_orthogonal", design_type="monomer", truth="bad",
        scrmsd=1.3, plddt=91, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=3.6, solubility=0.5, rosetta_dG=None, shape_complementarity=None, md_rmsd=1.5,
        note="planted known-bad: passes L1, fails L2 (orthogonal scRMSD 3.6 > 2.5) — predictor-specific overconfidence",
    )))

    # --- known-BAD: fails Layer 3 (physics) — aggregation-prone monomer ---
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L3_solubility", design_type="monomer", truth="bad",
        scrmsd=1.3, plddt=90, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=1.5, solubility=-2.4, rosetta_dG=None, shape_complementarity=None, md_rmsd=1.6,
        note="planted known-bad: passes L1-L2, fails L3 (solubility -2.4 < -1.0) — aggregation-prone",
    )))
    # known-BAD: fails Layer 3 via weak binder interface energy
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L3_interface", design_type="binder", truth="bad",
        scrmsd=1.6, plddt=88, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=1.8, solubility=0.4, rosetta_dG=-12, shape_complementarity=0.45, md_rmsd=2.0,
        note="planted known-bad: passes L1-L2, fails L3 (rosetta_dG -12 > -30, sc 0.45 < 0.6) — weak interface",
    )))

    # --- known-BAD: fails Layer 4 (dynamics) — folds-but-melts (good static metrics, drifts in MD) ---
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L4_dynamics", design_type="monomer", truth="bad",
        scrmsd=1.3, plddt=90, plddt_catalytic=None, pae_interaction=6, catalytic_geom_rmsd=None,
        scrmsd_orthogonal=1.5, solubility=0.5, rosetta_dG=None, shape_complementarity=None, md_rmsd=4.5,
        note="planted known-bad: passes L1-L3, fails L4 (md_rmsd 4.5 > 3.0) — folds-but-melts",
    )))

    # --- known-BAD: enzyme that fails L1 on catalytic geometry (theozyme broken) ---
    rows.append(_round(dict(
        design_id="EXAMPLE_DATA_BAD_L1_enzyme_geom", design_type="enzyme", truth="bad",
        scrmsd=1.2, plddt=92, plddt_catalytic=95, pae_interaction=6, catalytic_geom_rmsd=1.1,
        scrmsd_orthogonal=1.5, solubility=0.5, rosetta_dG=None, shape_complementarity=None, md_rmsd=1.6,
        note="planted known-bad: fails L1 (catalytic_geom_rmsd 1.1 > 0.5) — active-site geometry off",
    )))

    return rows


def _sample_population(rng: np.random.Generator, n: int) -> list[dict]:
    """Sample a noisy background population of mixed types with planted truth + ambiguous cases."""
    rows: list[dict] = []
    for i in range(n):
        dt = rng.choice(DESIGN_TYPES)
        c = GOOD_CENTERS[dt]
        # ~55% are "truly good" (cluster near the good center), ~45% "truly bad" (degraded), with
        # noise that pushes some across cutoffs — that overlap is the discrimination problem.
        is_good = rng.random() < 0.55
        truth = "good" if is_good else "bad"
        # noise scale: good designs tight, bad designs degraded on a RANDOM subset of metrics
        def jitter(center, lo, hi, bad_shift):
            v = center + rng.normal(0, (hi - lo) * 0.06)
            if not is_good and rng.random() < 0.5:
                v = v + bad_shift  # degrade some (not all) metrics → overlap near cutoffs
            return float(np.clip(v, lo, hi))

        scrmsd = jitter(c["scrmsd"], 0.6, 5.0, bad_shift=+1.6)
        plddt = jitter(c["plddt"], 50, 99, bad_shift=-18)
        pae = jitter(c["pae"], 2, 25, bad_shift=+7)
        scr_o = jitter(c["scrmsd_orthogonal"], 0.6, 5.0, bad_shift=+1.6)
        sol = jitter(c["solubility"], -3.0, 1.5, bad_shift=-2.0)
        md = jitter(c["md_rmsd"], 0.8, 6.0, bad_shift=+2.0)
        rdg = None if c["rosetta_dG"] is None else jitter(c["rosetta_dG"], -60, -5, bad_shift=+25)
        sc = None if c["sc"] is None else jitter(c["sc"], 0.3, 0.85, bad_shift=-0.25)
        pc = None if c["plddt_cat"] is None else jitter(c["plddt_cat"], 60, 99, bad_shift=-12)
        cg = None if c["cat_geom"] is None else jitter(c["cat_geom"], 0.1, 1.5, bad_shift=+0.6)

        rows.append(_round(dict(
            design_id=f"EXAMPLE_DATA_{i:04d}", design_type=dt, truth=truth,
            scrmsd=scrmsd, plddt=plddt, plddt_catalytic=pc, pae_interaction=pae,
            catalytic_geom_rmsd=cg, scrmsd_orthogonal=scr_o, solubility=sol,
            rosetta_dG=rdg, shape_complementarity=sc, md_rmsd=md,
            note="EXAMPLE_DATA synthetic background sample",
        )))
    return rows


def make_pool(n: int = 200) -> pd.DataFrame:
    """Build the full labeled EXAMPLE_DATA pool (planted designs + noisy background)."""
    rng = np.random.default_rng(SEED)
    planted = known_designs()
    background = _sample_population(rng, max(0, n - len(planted)))
    df = pd.DataFrame(planted + background, columns=COLUMNS)
    return df


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Generate the labeled synthetic EXAMPLE_DATA design pool.")
    ap.add_argument("--n", type=int, default=200, help="approx total pool size (default: 200)")
    ap.add_argument("--out", default="results/pool.csv", help="output CSV path (default: results/pool.csv)")
    args = ap.parse_args(argv)

    df = make_pool(args.n)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out, index=False)
    n_good = int((df["truth"] == "good").sum())
    print(f"Wrote {args.out}: {len(df)} EXAMPLE_DATA designs "
          f"({n_good} planted-good, {len(df) - n_good} planted-bad).")
    print("ALL ROWS ARE SYNTHETIC (EXAMPLE_DATA). Never present these numbers as real results.")
    print(f"Planted fixtures for the unit tests: {len(known_designs())} explicit known-good/known-bad designs.")


if __name__ == "__main__":
    main(sys.argv[1:])
