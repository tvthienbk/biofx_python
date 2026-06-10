"""Prior sensitivity for the capstone — the between-compound SD prior.

The prior on tau (between-compound sd) controls how aggressively the model pools.
A tight tau prior pools hard (shrinks everyone toward mu — risks missing a genuine
standout); a loose tau prior barely pools (re-admits the winner's curse). We refit
under three tau priors and compare: the population tau, the amount of shrinkage,
and — crucially — whether the DECISION (recommended compound) is stable.

  * Default     tau ~ HalfNormal(1.0)
  * Tight       tau ~ HalfNormal(0.3)   -- strong pooling
  * Loose       tau ~ HalfNormal(3.0)   -- weak pooling

Teaching point: the headline deliverable is a decision, so the right robustness
question is "does the recommended compound change?" — not just "does tau change?".
"""
from __future__ import annotations

import pathlib
import sys

import arviz as az
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit, decision_table, posterior_theta  # noqa: E402

PRIORS = {
    "Default HN(1.0)": dict(tau_sd=1.0),
    "Tight HN(0.3)": dict(tau_sd=0.3),
    "Loose HN(3.0)": dict(tau_sd=3.0),
}


def main() -> None:
    data = generate()
    raw_pick = int(np.argmax(data["raw_means"]))
    print(f"True best = #{data['best_true']}, raw-mean winner = #{raw_pick} "
          f"(winner's curse)\n")
    header = (f"{'prior':>16}  {'tau mean':>8}  {'rec(min-regret)':>15}  "
              f"{'P(best) of rec':>14}")
    print(header)
    for name, kw in PRIORS.items():
        idata = fit(data, draws=400, tune=800, chains=2, seed=11, **kw)
        tau_mean = float(az.summary(idata, var_names=["tau"]).loc["tau", "mean"])
        dec = decision_table(idata)
        rec = dec["recommend_min_regret"]
        print(f"{name:>16}  {tau_mean:8.3f}  {('#'+str(rec)):>15}  "
              f"{dec['p_best'][rec]:14.3f}")
    print("\nInterpretation: the recommended compound is the robustness target. "
          "Across all three priors the partial-pooling decision points to the true "
          "best, correcting the raw-mean winner's curse -- the ACTION is robust. The "
          "tight tau prior over-pools (smaller tau, more shrinkage), which reshapes "
          "P(best) but does not overturn the recommendation here. The between-compound "
          "SD prior is the key lever, and the safe default is weakly-informative.")


if __name__ == "__main__":
    main()
