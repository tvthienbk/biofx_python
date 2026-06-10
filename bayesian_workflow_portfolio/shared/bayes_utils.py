"""Shared utilities reused across all 20 projects.

Keeping these in one module means each project's ``model.py`` and notebook focus
on *what is new* in that project rather than re-deriving boilerplate. Everything
here is deliberately dependency-light (numpy + optional arviz) so the helpers
import even in environments where PyMC is not installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

DEFAULT_SEED = 20240601


def rng(seed: int = DEFAULT_SEED) -> np.random.Generator:
    """A single, explicit source of randomness. Pass a seed for reproducibility."""
    return np.random.default_rng(seed)


@dataclass
class RecoveryResult:
    name: str
    truth: float
    mean: float
    sd: float
    lower: float
    upper: float

    @property
    def covered(self) -> bool:
        """Does the 94% credible interval contain the known true value?"""
        return self.lower <= self.truth <= self.upper

    @property
    def z(self) -> float:
        """Posterior z-score of the truth: (mean - truth) / sd. |z| < ~2 is healthy."""
        return float((self.mean - self.truth) / self.sd) if self.sd > 0 else np.inf

    def __str__(self) -> str:
        flag = "OK " if self.covered else "MISS"
        return (
            f"[{flag}] {self.name:>12}: true={self.truth:+.3f} "
            f"post={self.mean:+.3f}±{self.sd:.3f} "
            f"94%=[{self.lower:+.3f}, {self.upper:+.3f}] z={self.z:+.2f}"
        )


def check_recovery(idata, truths: Mapping[str, float], hdi_prob: float = 0.94):
    """Compare posterior summaries against known true parameters.

    Returns a list of :class:`RecoveryResult`. Used by every project's
    ``test_recovery.py`` to assert inference recovers the data-generating
    parameters within a stated tolerance.
    """
    import arviz as az

    post = idata.posterior
    summary = az.summary(idata, var_names=list(truths.keys()), hdi_prob=hdi_prob)
    results = []
    for name, truth in truths.items():
        # az.summary names HDI columns by the probability, e.g. hdi_3% / hdi_97%.
        lo_col = [c for c in summary.columns if c.startswith("hdi_") and c.endswith("%")][0]
        hi_col = [c for c in summary.columns if c.startswith("hdi_") and c.endswith("%")][-1]
        row = summary.loc[name]
        results.append(
            RecoveryResult(
                name=name,
                truth=float(truth),
                mean=float(row["mean"]),
                sd=float(row["sd"]),
                lower=float(row[lo_col]),
                upper=float(row[hi_col]),
            )
        )
    return results


def sbc_rank(prior_draw: float, posterior_draws: np.ndarray) -> int:
    """Rank statistic for Simulation-Based Calibration.

    The rank of the prior draw among ``L`` posterior draws should be uniform on
    {0, ..., L} if inference is calibrated. Aggregate these ranks across many
    simulations and check uniformity (histogram / ECDF).
    """
    return int(np.sum(np.asarray(posterior_draws) < prior_draw))


def assert_calibrated(ranks: np.ndarray, n_bins: int = 20, alpha: float = 0.01) -> dict:
    """Chi-square test that SBC ranks are uniform. Returns a small report dict."""
    from scipy import stats

    ranks = np.asarray(ranks)
    counts, _ = np.histogram(ranks, bins=n_bins, range=(ranks.min(), ranks.max() + 1e-9))
    expected = len(ranks) / n_bins
    chi2 = float(np.sum((counts - expected) ** 2 / expected))
    dof = n_bins - 1
    pval = float(stats.chi2.sf(chi2, dof))
    return {"chi2": chi2, "dof": dof, "pvalue": pval, "uniform": pval > alpha}
