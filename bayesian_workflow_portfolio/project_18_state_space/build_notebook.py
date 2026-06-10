"""Emit notebook.ipynb (clean state-space workflow) and notebook_broken.ipynb.

Run:  python build_notebook.py
Authored via shared.nbbuild.NotebookBuilder so the JSON is valid by construction.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.nbbuild import NotebookBuilder  # noqa: E402

PATH_PREAMBLE = (
    "import sys, pathlib\n"
    f"sys.path.insert(0, r'{ROOT}')\n"
    "sys.path.insert(0, str(pathlib.Path.cwd()))\n"
    "import warnings; warnings.filterwarnings('ignore')"
)


def clean_notebook() -> NotebookBuilder:
    nb = NotebookBuilder(title="Project 18 — Dynamics & Drift (State-Space)")

    nb.md(
        "# Project 18 — Dynamics & Drift (Local-Level State-Space Model)",
        "**Scenario.** A sensor / growth-curve time series whose *true level drifts* "
        "over time. We observe the level through measurement noise. We want the latent "
        "trajectory **and** an honest split of the two noise sources.",
        "**New skill.** Temporal dependence and latent states. "
        "**Key pitfall.** The **process** noise (how much the level wanders) and the "
        "**observation** noise (measurement error) are *confounded* — both make the "
        "observed series wiggly. Separating them needs informative priors and enough "
        "data.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Local-level model: the latent level follows a Gaussian random walk, and each "
        "observation is the level plus noise.\n\n"
        "$$\\text{level}_t = \\text{level}_{t-1} + w_t,\\; w_t\\sim N(0,\\sigma_\\text{lvl}),"
        "\\qquad y_t = \\text{level}_t + e_t,\\; e_t\\sim N(0,\\sigma_\\text{obs}).$$\n\n"
        "**Assumptions:** (a) the level evolves as a random walk (no mean reversion); "
        "(b) both noises are Gaussian and constant; (c) observations are conditionally "
        "independent given the level. We know the truths "
        "$\\sigma_\\text{lvl}=0.30$, $\\sigma_\\text{obs}=0.60$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']\n"
        "print(f\"T={data['t']}, true sigma_level={data['truth']['sigma_level']}, \"\n"
        "      f\"true sigma_obs={data['truth']['sigma_obs']}\")\n"
        "fig, ax = plt.subplots(figsize=(7,3.5))\n"
        "ax.plot(data['level_true'], 'k--', lw=1.5, label='true latent level')\n"
        "ax.plot(y, '.', color='#4C72B0', alpha=0.7, label='observed y')\n"
        "ax.set(xlabel='time', ylabel='value', title='Latent level vs noisy observations')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (non-centred random walk + justified priors)",
        "We build the random walk **non-centred**: standardised innovations $z_t\\sim "
        "N(0,1)$ scaled by $\\sigma_\\text{lvl}$ and cumulatively summed. This avoids the "
        "funnel that a centred random walk develops as $\\sigma_\\text{lvl}\\to 0$.\n\n"
        "**Priors.** $\\sigma_\\text{lvl}\\sim\\text{HalfNormal}(0.5)$ (expect modest drift), "
        "$\\sigma_\\text{obs}\\sim\\text{HalfNormal}(1.0)$ (measurement error can be larger). "
        "These are deliberately *not* both vague — vague priors let the two variances "
        "trade off freely (see the broken notebook).",
    )
    nb.code(
        "from model import build_model, fit, build_ar1_model, fit_ar1\n"
        "model = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate series implied by the priors. We want plausible drifting series "
        "of the right rough magnitude — not explosive random walks (process prior too "
        "wide) nor flat lines (too tight).",
    )
    nb.code(
        "rng = np.random.default_rng(RNG)\n"
        "fig, ax = plt.subplots(figsize=(7,3.5))\n"
        "for _ in range(6):\n"
        "    sl = abs(rng.normal(0,0.5)); so = abs(rng.normal(0,1.0))\n"
        "    lvl = 5 + np.cumsum(rng.normal(0, sl, size=data['t']))\n"
        "    ax.plot(lvl + rng.normal(0, so, size=data['t']), lw=1)\n"
        "ax.set(xlabel='time', ylabel='y', title='Prior predictive series — plausible drift')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=600, tune=1000, chains=2, target_accept=0.95, cores=1`. The "
        "non-centred parameterisation plus a raised `target_accept` keep the random-walk "
        "geometry divergence-free. (`cores=1` because multiprocess sampling can hang "
        "without a linked BLAS.)",
    )
    nb.code("idata = fit(data, draws=600, tune=1000, chains=2, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R\\approx 1.00$, ESS, and divergences (want 0). Look at the **joint** "
        "posterior of $(\\sigma_\\text{lvl}, \\sigma_\\text{obs})$: a strong negative "
        "correlation is the signature of the variance confounding — with our priors and "
        "T=100 it should be present but mild, and both should bracket their truths.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['sigma_level','sigma_obs','level0']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code(
        "az.plot_trace(idata, var_names=['sigma_level','sigma_obs']); plt.tight_layout()"
    )
    nb.code(
        "az.plot_pair(idata, var_names=['sigma_level','sigma_obs'], kind='scatter',\n"
        "             scatter_kwargs={'alpha':0.2}); plt.tight_layout()"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks & latent trajectory",
        "Overlay the inferred latent level (posterior mean + band) on the truth and the "
        "data. A good fit tracks the true level inside a band that is tighter than the "
        "observation scatter (the model 'sees through' the noise).",
    )
    nb.code(
        "lvl = idata.posterior['level']\n"
        "lvl_mean = lvl.mean(dim=('chain','draw')).values\n"
        "lvl_lo = lvl.quantile(0.03, dim=('chain','draw')).values\n"
        "lvl_hi = lvl.quantile(0.97, dim=('chain','draw')).values\n"
        "fig, ax = plt.subplots(figsize=(7,3.8))\n"
        "ax.fill_between(np.arange(data['t']), lvl_lo, lvl_hi, color='#4C72B0', alpha=0.25,\n"
        "                label='94% level band')\n"
        "ax.plot(lvl_mean, color='#4C72B0', label='inferred level')\n"
        "ax.plot(data['level_true'], 'k--', label='true level')\n"
        "ax.plot(data['y'], '.', color='gray', alpha=0.5, label='data')\n"
        "ax.set(xlabel='time', ylabel='value', title='Latent level recovery')\n"
        "ax.legend(); plt.tight_layout()"
    )
    nb.code(
        "mae = float(np.mean(np.abs(lvl_mean - data['level_true'])))\n"
        "print(f'latent-level recovery MAE = {mae:.3f}')"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison (AR(1) alternative)",
        "Is a persistent random-walk drift even needed? We compare against a stationary "
        "**AR(1)** model via LOO. The local-level model should be competitive or better "
        "when the level genuinely drifts; AR(1) assumes mean reversion. We use "
        "`az.compare` on the two `InferenceData` objects (both carry log-likelihood).",
    )
    nb.code(
        "idata_ar1 = fit_ar1(data, draws=600, tune=1000, chains=2, seed=101)\n"
        "cmp = az.compare({'local_level': idata, 'ar1': idata_ar1}, ic='loo')\n"
        "print(cmp[['rank','elpd_loo','p_loo','dse']])"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Translate into a decision: e.g. the current level estimate (last time point) "
        "with its credible interval, and the probability the level is trending up over "
        "the final stretch — the kind of statement a process engineer acts on.",
    )
    nb.code(
        "last = idata.posterior['level'].isel(level_dim_0=-1).values.ravel()\n"
        "slope = (idata.posterior['level'].isel(level_dim_0=-1).values\n"
        "         - idata.posterior['level'].isel(level_dim_0=-11).values).ravel()\n"
        "print(f'current level = {last.mean():.2f} '\n"
        "      f'(94% [{np.percentile(last,3):.2f}, {np.percentile(last,97):.2f}])')\n"
        "print(f'P(level rose over last 10 steps) = {np.mean(slope>0):.2f}')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** We separated genuine drift from "
        "measurement noise: the latent level is recovered within MAE < 0.5, and both "
        "noise scales bracket their true values. Report the *level* and its trend, not "
        "the raw noisy readings. See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Seeded bugs: vague priors that let process/obs noise trade off freely."""
    nb = NotebookBuilder(title="Project 18 — BROKEN debugging exercise")
    nb.md(
        "# Project 18 — BROKEN notebook (debugging exercise)",
        "Seeded bugs centred on the state-space pitfall: **process vs observation "
        "noise confounding**. With vague priors the level either overfits the noise or "
        "oversmooths it. Run it, read the diagnostics, find each bug, fix it. Answer "
        "key: `BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nimport pytensor.tensor as pt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']; T = data['t']"
    )
    nb.md(
        "### Model — vague variance priors and a centred random walk.",
        "Watch the $(\\sigma_\\text{lvl}, \\sigma_\\text{obs})$ pair plot and the divergences.",
    )
    nb.code(
        "# BUG 1: both variance priors are vague (HalfNormal sigma=10) -> the two\n"
        "#         noises trade off freely; their posteriors blow up / anti-correlate.\n"
        "# BUG 2: CENTRED random walk via pm.GaussianRandomWalk -> funnel geometry,\n"
        "#         divergences when sigma_level is small.\n"
        "with pm.Model() as model:\n"
        "    sigma_level = pm.HalfNormal('sigma_level', sigma=10.0)\n"
        "    sigma_obs = pm.HalfNormal('sigma_obs', sigma=10.0)\n"
        "    level = pm.GaussianRandomWalk('level', sigma=sigma_level, shape=T,\n"
        "                                  init_dist=pm.Normal.dist(y.mean(), 5.0))\n"
        "    pm.Normal('y_obs', mu=level, sigma=sigma_obs, observed=y)\n"
        "    idata = pm.sample(draws=500, tune=500, chains=2, cores=1,\n"
        "                      target_accept=0.9, random_seed=RNG, progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['sigma_level','sigma_obs']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.md(
        "### The smoking gun — BUG 3: the two variances anti-correlate.",
        "With vague priors the pair plot of $(\\sigma_\\text{lvl}, \\sigma_\\text{obs})$ shows "
        "a strong negative-correlation banana: the model cannot decide whether the "
        "wiggle is drift or noise. Symptom in the fit: the level either chases every "
        "point (overfit) or flattens out (oversmooth). Fixes: (1) informative priors "
        "like `HalfNormal(0.5)` / `HalfNormal(1.0)`; (2) the **non-centred** random "
        "walk from `model.py`.",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['sigma_level','sigma_obs'], kind='scatter',\n"
        "             scatter_kwargs={'alpha':0.2}); plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
