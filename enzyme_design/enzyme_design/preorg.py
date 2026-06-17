"""Stage 5(b): whole-reaction-coordinate preorganization scoring.

This is the protocol's central thesis: catalytic success correlates with active-
site preorganization across the *entire* reaction coordinate, not a single
transition state.  For each mechanistic state (Michaelis complex, TS1,
intermediate, TS2, product, ...) a conformational-ensemble predictor
(PLACER/ChemNet) produces an ensemble of the active site, from which we score:

* mean catalytic-geometry RMSD to the ideal theozyme at that step (low = good),
* geometric spread / variance across the ensemble (low = preorganized),
* persistence of key catalytic contacts at that step (high = good).

The decisive rule (step 12): rank designs by their **worst step**, not the
average — a design that loses geometry at any single step stalls there.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import pstdev
from typing import Dict, List, Optional, Sequence

__all__ = ["StepEnsemble", "PreorgProfile", "preorg_from_rmsd_samples"]


@dataclass
class StepEnsemble:
    """Preorganization scores for one mechanistic state.

    ``mean_rmsd``: mean catalytic-geometry RMSD to the ideal theozyme (Å).
    ``rmsd_std``:  standard deviation of that RMSD across the ensemble (Å).
    ``contact_fraction``: fraction of key catalytic contacts satisfied (0-1).
    """

    state: str
    mean_rmsd: float
    rmsd_std: float
    contact_fraction: float = 1.0

    def __post_init__(self) -> None:
        if self.mean_rmsd < 0 or self.rmsd_std < 0:
            raise ValueError("RMSD values must be non-negative")
        if not 0.0 <= self.contact_fraction <= 1.0:
            raise ValueError("contact_fraction must be in [0, 1]")

    def score(
        self,
        rmsd_weight: float = 1.0,
        std_weight: float = 1.0,
        contact_weight: float = 1.0,
    ) -> float:
        """A single penalty for this step (lower is better, 0 is ideal).

        Combines geometry error, ensemble spread, and unmet contacts.
        """
        return (
            rmsd_weight * self.mean_rmsd
            + std_weight * self.rmsd_std
            + contact_weight * (1.0 - self.contact_fraction)
        )


@dataclass
class PreorgProfile:
    """Preorganization across all mechanistic states for one design."""

    design_id: str
    steps: List[StepEnsemble] = field(default_factory=list)

    def worst_step(self, **weights: float) -> Optional[StepEnsemble]:
        """The single step with the highest (worst) penalty."""
        if not self.steps:
            return None
        return max(self.steps, key=lambda s: s.score(**weights))

    def worst_score(self, **weights: float) -> float:
        """Worst-step penalty — the protocol's ranking quantity (lower better)."""
        w = self.worst_step(**weights)
        if w is None:
            return float("inf")
        return w.score(**weights)

    def mean_score(self, **weights: float) -> float:
        """Average penalty across steps (reported, but NOT used for ranking)."""
        if not self.steps:
            return float("inf")
        return sum(s.score(**weights) for s in self.steps) / len(self.steps)

    def passes(
        self,
        max_mean_rmsd: float = 1.5,
        max_rmsd_std: float = 1.0,
        min_contact_fraction: float = 0.8,
    ) -> bool:
        """Pass only if *every* step meets the geometry/spread/contact cutoffs."""
        return all(
            s.mean_rmsd <= max_mean_rmsd
            and s.rmsd_std <= max_rmsd_std
            and s.contact_fraction >= min_contact_fraction
            for s in self.steps
        )

    def failing_steps(
        self,
        max_mean_rmsd: float = 1.5,
        max_rmsd_std: float = 1.0,
        min_contact_fraction: float = 0.8,
    ) -> List[str]:
        return [
            s.state
            for s in self.steps
            if not (
                s.mean_rmsd <= max_mean_rmsd
                and s.rmsd_std <= max_rmsd_std
                and s.contact_fraction >= min_contact_fraction
            )
        ]


def preorg_from_rmsd_samples(
    design_id: str,
    samples_by_state: Dict[str, Sequence[float]],
    contacts_by_state: Optional[Dict[str, float]] = None,
) -> PreorgProfile:
    """Build a :class:`PreorgProfile` from raw per-state RMSD ensembles.

    ``samples_by_state`` maps a state name to the list of catalytic-geometry
    RMSDs from the ensemble (e.g. PLACER samples).  ``contacts_by_state`` maps a
    state to its satisfied-contact fraction (defaults to 1.0).
    """
    contacts = contacts_by_state or {}
    steps: List[StepEnsemble] = []
    for state, samples in samples_by_state.items():
        if not samples:
            raise ValueError(f"state {state!r} has no RMSD samples")
        mean = sum(samples) / len(samples)
        std = pstdev(samples) if len(samples) > 1 else 0.0
        steps.append(
            StepEnsemble(
                state=state,
                mean_rmsd=mean,
                rmsd_std=std,
                contact_fraction=contacts.get(state, 1.0),
            )
        )
    return PreorgProfile(design_id=design_id, steps=steps)
