"""Emit notebook.ipynb (clean workflow) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py
Notebooks are authored via shared.nbbuild.NotebookBuilder so the JSON is always
valid by construction.
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
    nb = NotebookBuilder(title="Project 13 — Subpopulations (finite mixture)")

    nb.md(
        "# Project 13 — Subpopulations (2-component Gaussian mixture)",
        "**Scenario.** A biophysical readout (single-molecule FRET efficiency, or a "
        "SAXS order parameter) reflects **two conformational states**. Each molecule "
        "is in a 'low' or 'high' state when measured, and the two states emit Gaussian "
        "signals with different means. We observe only the pooled, *unlabelled* signal "
        "— a bimodal histogram — and must infer the per-state means, the shared spread, "
        "and the mixing weights.",
        "**New skill.** Latent component membership: every observation secretly belongs "
        "to a component. **Key pitfall.** *Label switching* — the mixture likelihood is "
        "invariant to permuting the component labels, so chains can swap which label is "
        "'low' vs 'high', corrupting the per-component marginals. We fix it with an "
        "**ordered transform** on the means.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "We assume: (a) exactly two states (we *fix* K=2 — choosing K is itself a "
        "modelling decision), (b) Gaussian emissions with a **shared** spread sigma, "
        "(c) independent draws (no temporal correlation — that is Project 14's HMM). We "
        "synthesize from known truth so we can check recovery: weights (0.35, 0.65), "
        "means (-2.0, 1.5), sigma 0.7, hence separation 3.5.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']\n"
        "t = data['truth']\n"
        "print(f\"N={len(y)}; true means=({t['mu[0]']:.2f},{t['mu[1]']:.2f}), \"\n"
        "      f\"sigma={t['sigma']:.2f}, w_high={t['w[1]']:.2f}, sep={t['separation']:.2f}\")"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(y, bins=40, color='#55A868', edgecolor='white', density=True)\n"
        "ax.set(xlabel='signal', ylabel='density', title='Observed signal — clearly bimodal')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (likelihood + justified priors)",
        "We marginalize the discrete labels analytically using `pm.NormalMixture`:",
        "$$y_i \\sim \\sum_{k} w_k\\,\\mathcal{N}(\\mu_k, \\sigma), \\quad "
        "w \\sim \\text{Dirichlet}(2,2),\\; \\sigma \\sim \\text{HalfNormal}(1).$$",
        "**The crucial prior is on the means.** Plain `mu ~ Normal(0,3, shape=2)` leaves "
        "the labeling symmetry intact. We instead impose an **ordered transform** so "
        "$\\mu_0 < \\mu_1$ always. This pins label 0 to the lower state and label 1 to the "
        "higher state, breaking the symmetry that causes label switching.",
    )
    nb.code(
        "from model import build_model, fit, add_separation\n"
        "model = build_model(data, ordered=True)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "Datasets implied by the prior should look like *plausible bimodal signals* — "
        "varied separations and weights, but not absurd (e.g. means at ±50). We draw "
        "from the prior predictive and overlay a few simulated histograms.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=200, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.reshape(-1, len(y))\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "for i in range(6):\n"
        "    ax.hist(pp[i], bins=30, histtype='step', density=True, alpha=0.7)\n"
        "ax.set(xlabel='signal', ylabel='density',\n"
        "       title='Prior predictive datasets — varied but plausible')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=500, tune=1000, chains=4, target_accept=0.9`. Four chains are "
        "important here precisely so we can *detect* label switching via R-hat if it "
        "occurred. The ordered transform should keep things clean.",
    )
    nb.code("idata = fit(data, draws=500, tune=1000, chains=4, seed=13)\n"
            "add_separation(idata)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "With the ordered transform, R-hat for `mu` should be ≈1.00 and the four chains "
        "should agree. (In the broken notebook, where ordering is removed, the chains "
        "disagree and `mu`'s R-hat blows up — the signature of label switching.)",
    )
    nb.code(
        "print(az.summary(idata, var_names=['w','mu','sigma','separation']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_trace(idata, var_names=['mu','w']); plt.tight_layout()")
    nb.md(
        "**Reading the trace.** Each `mu` component should be a tight, well-mixed band "
        "with the four chains overlapping. If instead you saw two chains parked near "
        "(-2, 1.5) and two near (1.5, -2), that bimodal-per-label trace would be label "
        "switching — fixed by ordering, not by more tuning.",
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Does the fitted mixture reproduce the bimodal shape of the data? We overlay "
        "posterior-predictive densities on the observed histogram.",
    )
    nb.code("ax = az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Model criticism & the identifiability lesson",
        "Even with ordering, the **raw labels** are only meaningful relative to the "
        "constraint. The robustly identifiable quantities are label-invariant: the "
        "**separation** $\\mu_1-\\mu_0$, the shared $\\sigma$, and the weight of the "
        "higher-mean component. We compare those to truth.",
    )
    nb.code(
        "for name, truth in [('separation', t['separation']), ('sigma', t['sigma']),\n"
        "                    ('w[1]', t['w[1]'])]:\n"
        "    if name == 'w[1]':\n"
        "        post = idata.posterior['w'].isel(w_dim_0=1).values.ravel()\n"
        "    else:\n"
        "        post = idata.posterior[name].values.ravel()\n"
        "    lo, hi = np.percentile(post, [3, 97])\n"
        "    print(f'{name:>11}: post mean={post.mean():.3f} 94%=[{lo:.3f},{hi:.3f}] '\n"
        "          f'truth={truth:.3f}')"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "For a collaborator: report the fraction of molecules in the high state and the "
        "gap between states. E.g. 'About 65% of molecules occupy the high-FRET state; "
        "the two states differ by ~3.5 signal units (94% CI), well-resolved.' The "
        "decision (are there really two states? is the minor population real?) follows "
        "from the weight's credible interval and the posterior predictive fit.",
    )
    nb.code(
        "w_high = idata.posterior['w'].isel(w_dim_0=1).values.ravel()\n"
        "print(f'P(high state) posterior mean = {w_high.mean():.3f}')\n"
        "print(f'P(minor population > 10% of molecules) = {np.mean(np.minimum(w_high,1-w_high) > 0.1):.3f}')"
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Deliberately broken version: label switching. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 13 — BROKEN debugging exercise")
    nb.md(
        "# Project 13 — BROKEN notebook (label switching)",
        "This notebook contains **seeded bugs** centred on the mixture's key pitfall. "
        "Run it, read the diagnostics, find each bug, and fix it. Clean reference: "
        "`notebook.ipynb`; answer key: `BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); y = data['y']"
    )
    nb.md(
        "### Model — BUG 1: no ordering constraint on the means.",
        "Without forcing $\\mu_0 < \\mu_1$, the two components are exchangeable and the "
        "chains will label-switch.",
    )
    nb.code(
        "with pm.Model() as model:\n"
        "    w = pm.Dirichlet('w', a=np.array([2.0, 2.0]))\n"
        "    # BUG 1: unordered means -> label-switching symmetry intact\n"
        "    mu = pm.Normal('mu', 0.0, 3.0, shape=2)\n"
        "    sigma = pm.HalfNormal('sigma', 1.0)\n"
        "    pm.NormalMixture('y', w=w, mu=mu, sigma=sigma, observed=y)\n"
        "    # BUG 2: too few tune steps to even adapt around the multimodality\n"
        "    idata = pm.sample(draws=500, tune=150, chains=4, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "# R-hat for mu will be far from 1.0 — the smoking gun.\n"
        "print(az.summary(idata, var_names=['mu','w']))"
    )
    nb.md(
        "### BUG 3: trusting the per-label posterior mean of `mu` as if identified.",
        "Averaging a label-switched marginal collapses both states toward the overall "
        "mean — a meaningless number reported with false confidence.",
    )
    nb.code(
        "mu_post = idata.posterior['mu'].values.reshape(-1, 2)\n"
        "# BUG 3: this 'mean of mu[0]' mixes both true states across chains\n"
        "print('reported mu[0] =', mu_post[:,0].mean(), 'mu[1] =', mu_post[:,1].mean())\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(mu_post[:,0], bins=40, alpha=0.6, label='mu[0] (should be one mode!)')\n"
        "ax.hist(mu_post[:,1], bins=40, alpha=0.6, label='mu[1]')\n"
        "ax.legend(); ax.set_title('Bimodal per-label marginals = label switching')\n"
        "plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
