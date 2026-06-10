"""Emit notebook.ipynb (clean) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py

Clean: correlated random effects via LKJCholeskyCov, non-centered, recovers the
intercept-slope correlation. Broken: (a) models intercept and slope as INDEPENDENT
(diagonal covariance, no LKJ) and shows the misfit / missed correlation, and (b) a
centered-vs-non-centered divergence demonstration.
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
    nb = NotebookBuilder(title="Project 11 — Varying Slopes (Hierarchical with LKJ)")

    nb.md(
        "# Project 11 — Varying Slopes (Correlated Random Effects, LKJ)",
        "**Scenario.** A dose-response readout $y$ depends on a standardized dose "
        "$x$, but both the **baseline** (intercept) and the **dose sensitivity** "
        "(slope) differ by **cell line** — and they are *correlated*: lines with a "
        "higher baseline also tend to respond more steeply.",
        "**New skill:** correlated random effects — varying intercepts AND slopes "
        "with an **LKJ** prior on their correlation (`pm.LKJCholeskyCov`). "
        "**Key pitfall:** ignoring the intercept-slope correlation (modeling them as "
        "independent) mis-fits the data and mis-estimates the population.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Each cell line $g$ has a pair $(\\alpha_g, \\beta_g)$ drawn from a common "
        "**bivariate** distribution with correlation $\\rho$.",
        "$$\\begin{bmatrix}\\alpha_g\\\\\\beta_g\\end{bmatrix} \\sim "
        "\\text{MVNormal}\\!\\left(\\begin{bmatrix}\\mu_a\\\\\\mu_b\\end{bmatrix}, "
        "\\Sigma\\right), \\quad y_{ij} = \\alpha_g + \\beta_g x_{ij} + "
        "\\varepsilon.$$",
        "**Assumptions:** (a) cell lines exchangeable, (b) the effect pair is "
        "bivariate Normal, (c) common observation noise $\\sigma$. Truth: "
        "$\\mu_a=2,\\ \\mu_b=1,\\ \\text{sd}_a=0.8,\\ \\text{sd}_b=0.5,\\ "
        "\\rho=0.6,\\ \\sigma=0.5$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, x, group, G = data['y'], data['x'], data['group'], data['G']\n"
        "emp_rho = np.corrcoef(data['alpha'], data['beta'])[0,1]\n"
        "print(f\"{G} lines x {data['n_per']} obs; empirical intercept-slope \"\n"
        "      f\"corr = {emp_rho:.2f}\")"
    )

    nb.md(
        "## Step 2 — Model specification (LKJ, non-centered)",
        "We give the 2x2 covariance an **LKJ** prior on its correlation matrix via "
        "`pm.LKJCholeskyCov(n=2, eta=2, sd_dist=HalfNormal)`, which returns the "
        "Cholesky factor $L$, the correlation, and the SDs. The **non-centered** "
        "form draws standard-normal $z$ (shape $2\\times G$) and sets "
        "$\\text{effects} = \\mu + (L z)^\\top$ — decoupling the funnel exactly as in "
        "the scalar hierarchical models.",
        "**Why LKJ($\\eta=2$)?** $\\eta=1$ is uniform over correlations; $\\eta>1$ "
        "gently favors weaker correlations (a mild regularizer). With only 8 lines "
        "we want a prior that neither forces $\\rho=0$ nor lets it run to $\\pm1$ on "
        "noise.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data, correlated=True, eta=2.0)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We confirm the prior implies dose-response lines on a sensible scale (not "
        "absurdly steep or flat) before fitting.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=300, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(pp, bins=40, color='#55A868', edgecolor='white', density=True)\n"
        "ax.axvline(y.mean(), color='red', lw=1.5, label='observed mean y')\n"
        "ax.set(xlabel='y implied by prior', ylabel='density',\n"
        "       title='Prior predictive — sensible scale')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "`draws=800, tune=1000, chains=4, target_accept=0.9`. The LKJ + "
        "non-centered model needs the mild `target_accept` bump; 4 chains for "
        "$\\hat R$.",
    )
    nb.code(
        "idata = fit(data, correlated=True, eta=2.0, draws=800, tune=1000,\n"
        "            chains=4, target_accept=0.9, seed=101)"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R$, ESS, **divergences ≈ 0**, and the **energy plot**. The "
        "correlation $\\rho$ will have the widest interval — it is the hardest "
        "quantity to identify from only 8 lines.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu_a','mu_b','sd_a','sd_b','rho','sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_energy(idata); plt.tight_layout()")

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Overlay posterior-predictive $y$ on the observed distribution; a good fit "
        "envelopes the data.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Recovering the correlation (the point of the project)",
        "Plot the posterior for $\\rho$ against the true value. Then show the "
        "per-line $(\\alpha_g, \\beta_g)$ posterior means: the positive tilt is the "
        "correlation the LKJ model captures and an independent model would miss.",
    )
    nb.code(
        "fig, axes = plt.subplots(1, 2, figsize=(11,4))\n"
        "az.plot_posterior(idata, var_names=['rho'], ref_val=data['truth']['rho'],\n"
        "                  ax=axes[0])\n"
        "axes[0].set_title('Posterior for intercept-slope correlation rho')\n"
        "eff = idata.posterior['effects'].mean(dim=('chain','draw')).values\n"
        "axes[1].scatter(eff[:,0], eff[:,1], color='#4C72B0')\n"
        "axes[1].set(xlabel='intercept alpha_g', ylabel='slope beta_g',\n"
        "            title='Per-line effects (note the positive tilt)')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Recover the population parameters and verify against truth.",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "truths = {k: data['truth'][k] for k in ['mu_a','mu_b','sd_a','sd_b','rho','sigma']}\n"
        "for res in check_recovery(idata, truths):\n"
        "    print(res)"
    )
    nb.md(
        "**Conclusion (for a collaborator).** On average dose raises the readout "
        "($\\mu_b\\approx1$), but lines differ in both baseline and sensitivity, and "
        "**higher-baseline lines respond more steeply** ($\\rho>0$). Predicting a new "
        "line's dose response must respect that correlation; treating intercept and "
        "slope as independent would bias predictions. See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Debug exercise: independent (diagonal) effects misfit + centered funnel."""
    nb = NotebookBuilder(title="Project 11 — BROKEN debugging exercise")
    nb.md(
        "# Project 11 — BROKEN notebook (debugging exercise)",
        "Two seeded problems: (1) modeling intercept and slope as **independent** "
        "(diagonal covariance, no LKJ), which misses the real correlation, and (2) a "
        "**centered** parameterization that diverges. Run it, compare to truth, then "
        "fix both. Answer key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, x, group, G = data['y'], data['x'], data['group'], data['G']\n"
        "print('true rho =', data['truth']['rho'])"
    )

    nb.md(
        "### BUG 1 — independent intercept and slope (no correlation modeled).",
        "Here $\\alpha_g$ and $\\beta_g$ get separate, independent priors. The model "
        "*cannot* represent the intercept-slope correlation, so it will report "
        "nothing about $\\rho$ and mis-predict new lines.",
    )
    nb.code(
        "with pm.Model(coords={'group': np.arange(G)}) as model:\n"
        "    mu_a = pm.Normal('mu_a', 0, 5)\n"
        "    mu_b = pm.Normal('mu_b', 0, 5)\n"
        "    sd_a = pm.HalfNormal('sd_a', 1)\n"
        "    sd_b = pm.HalfNormal('sd_b', 1)\n"
        "    sigma = pm.HalfNormal('sigma', 1)\n"
        "    # BUG 2: centered parameterization -> funnel\n"
        "    alpha = pm.Normal('alpha', mu_a, sd_a, dims='group')\n"
        "    beta = pm.Normal('beta', mu_b, sd_b, dims='group')\n"
        "    pm.Normal('y', mu=alpha[group] + beta[group]*x, sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=1000, chains=4, target_accept=0.85,\n"
        "                      random_seed=RNG, progressbar=False)"
    )

    nb.md("### Symptom — divergences, and no rho to be found.")
    nb.code(
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print(az.summary(idata, var_names=['mu_a','mu_b','sd_a','sd_b','sigma']))\n"
        "print('NOTE: this model has no rho parameter at all -> correlation ignored.')"
    )

    nb.md("### Diagnostic — energy plot (centered funnel fingerprint).")
    nb.code("az.plot_energy(idata); plt.tight_layout()")

    nb.md(
        "### Diagnostic — the missed correlation.",
        "Scatter the recovered per-line $(\\alpha_g,\\beta_g)$. The points still show "
        "a tilt (the data have it), but the *model* assumed independence, so its "
        "predictive covariance is wrong: it would generate new lines with $\\rho=0$.",
    )
    nb.code(
        "a = idata.posterior['alpha'].mean(dim=('chain','draw')).values\n"
        "b = idata.posterior['beta'].mean(dim=('chain','draw')).values\n"
        "fig, ax = plt.subplots(figsize=(5,4))\n"
        "ax.scatter(a, b, color='#C44E52')\n"
        "ax.set(xlabel='alpha_g', ylabel='beta_g',\n"
        "       title='Independent model assumes rho=0 (it is not)')\n"
        "plt.tight_layout()\n"
        "print('point-estimate corr in data:', np.corrcoef(a, b)[0,1].round(2))"
    )

    nb.md(
        "### The fix — LKJ correlated effects, non-centered.",
        "Model the 2x2 covariance with `pm.LKJCholeskyCov` and use the non-centered "
        "form. Now $\\rho$ is estimated and divergences drop to ~0. See `model.py`.",
    )
    nb.code(
        "from model import fit\n"
        "idata_fixed = fit(data, correlated=True, eta=2.0, draws=800, tune=1000,\n"
        "                  chains=4, target_accept=0.95, seed=RNG)\n"
        "print('divergences after fix:', int(idata_fixed.sample_stats['diverging'].sum()))\n"
        "print(az.summary(idata_fixed, var_names=['rho']))\n"
        "print('true rho =', data['truth']['rho'])"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
