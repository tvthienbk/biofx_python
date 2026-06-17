"""Stage 5(c)/14 aggregate ranking and diverse panel selection.

The protocol prescribes *sequential hard filters* (motif-RMSD -> preorganization
-> pAE/pLDDT -> packing -> diversity) and then carrying forward a **diverse** top
set rather than many copies of one topology.  This module combines the
self-consistency metrics and the preorganization worst-score into one ranking
and performs greedy diversity selection over topology clusters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .metrics import SelfConsistency, Thresholds
from .preorg import PreorgProfile

__all__ = ["RankedDesign", "rank_designs", "select_diverse"]


@dataclass
class RankedDesign:
    design_id: str
    cluster: str
    score: float            # combined penalty (lower = better)
    passes_filters: bool
    reasons: List[str]


def _norm(value: float, lo: float, hi: float) -> float:
    """Min-max normalise into [0,1]; degenerate range -> 0."""
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def rank_designs(
    metrics: List[SelfConsistency],
    preorg: Dict[str, PreorgProfile],
    clusters: Optional[Dict[str, str]] = None,
    thresholds: Thresholds = Thresholds(),
    w_motif: float = 0.4,
    w_preorg: float = 0.4,
    w_confidence: float = 0.2,
) -> List[RankedDesign]:
    """Combine self-consistency + preorganization into one ranked list.

    Hard filters first: a design must pass the self-consistency thresholds AND
    its preorganization profile (every step) to be ``passes_filters=True``.  The
    soft ``score`` (lower better) is a weighted blend of motif Cα-RMSD,
    worst-step preorganization, and a confidence term (1 - pLDDT/100), so designs
    are ordered even among those that pass.
    """
    clusters = clusters or {}

    # collect ranges for normalisation
    motif_vals = [m.motif_ca_rmsd for m in metrics if m.motif_ca_rmsd is not None]
    preorg_vals = [p.worst_score() for p in preorg.values()] or [0.0]
    m_lo, m_hi = (min(motif_vals), max(motif_vals)) if motif_vals else (0.0, 1.0)
    p_lo, p_hi = min(preorg_vals), max(preorg_vals)

    ranked: List[RankedDesign] = []
    for m in metrics:
        ok_sc, reasons = m.evaluate(thresholds)
        prof = preorg.get(m.design_id)
        ok_pre = True
        if prof is not None:
            ok_pre = prof.passes()
            if not ok_pre:
                reasons = reasons + [
                    f"preorganization fails at step(s): {prof.failing_steps()}"
                ]
        else:
            reasons = reasons + ["no preorganization profile"]
            ok_pre = False

        motif_term = _norm(m.motif_ca_rmsd, m_lo, m_hi) if m.motif_ca_rmsd is not None else 1.0
        worst = prof.worst_score() if prof is not None else p_hi
        preorg_term = _norm(worst, p_lo, p_hi)
        conf_term = (1.0 - (m.plddt or 0.0) / 100.0)

        score = (
            w_motif * motif_term
            + w_preorg * preorg_term
            + w_confidence * conf_term
        )
        ranked.append(
            RankedDesign(
                design_id=m.design_id,
                cluster=clusters.get(m.design_id, m.design_id),
                score=score,
                passes_filters=ok_sc and ok_pre,
                reasons=reasons,
            )
        )

    ranked.sort(key=lambda r: (not r.passes_filters, r.score))
    return ranked


def select_diverse(
    ranked: List[RankedDesign],
    n: int,
    per_cluster: int = 1,
    passing_only: bool = True,
) -> List[RankedDesign]:
    """Greedily pick the best ``n`` designs spread across topology clusters.

    First pass takes up to ``per_cluster`` from each cluster (best score first);
    if fewer than ``n`` chosen, a second pass fills remaining slots from the
    leftover ranked list.  Set ``passing_only=False`` to allow filtered-out
    designs as fillers.
    """
    if n <= 0:
        return []
    pool = [r for r in ranked if r.passes_filters] if passing_only else list(ranked)
    pool_sorted = sorted(pool, key=lambda r: r.score)

    chosen: List[RankedDesign] = []
    taken_per_cluster: Dict[str, int] = {}
    chosen_ids = set()
    # pass 1: spread across clusters
    for r in pool_sorted:
        if len(chosen) >= n:
            break
        if taken_per_cluster.get(r.cluster, 0) < per_cluster:
            chosen.append(r)
            chosen_ids.add(r.design_id)
            taken_per_cluster[r.cluster] = taken_per_cluster.get(r.cluster, 0) + 1
    # pass 2: fill remaining slots regardless of cluster
    if len(chosen) < n:
        for r in pool_sorted:
            if len(chosen) >= n:
                break
            if r.design_id not in chosen_ids:
                chosen.append(r)
                chosen_ids.add(r.design_id)
    return chosen[:n]
