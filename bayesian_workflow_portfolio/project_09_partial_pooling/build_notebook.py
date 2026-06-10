"""Emit notebook.ipynb (clean workflow) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py

The clean notebook fits the **non-centered** hierarchical Normal model and shows
~0 divergences. The broken notebook fits the **centered** parameterization with a
small target_accept so the funnel produces divergences; it shows the divergence
count, an energy plot, and the funnel pairs plot, then the non-centered fix.
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
    nb = NotebookBuilder(title="Project 09 — Partial Pooling")

    nb.md(
        "# Project 09 — Partial Pooling (Hierarchical Means)",
        "**Scenario.** A continuous assay readout is measured on many "
        "plates/labs/batches, with only a *few* observations per group. We want "
        "each group's mean **and** the population they come from — without either "
        "pretending the groups are identical (complete pooling) or treating each "
        "in isolation (no pooling).",
        "**New skill:** *partial pooling* — shrinkage of each group toward the "
        "grand mean, with the amount of shrinkage learned from the data. "
        "**Key pitfall:** the natural *centered* parameterization creates **Neal's "
        "funnel** and produces divergences when the between-group SD $\\tau$ is "
        "small. The fix is a *non-centered* parameterization.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "We assume groups are **exchangeable**: their latent means $\\theta_j$ are "
        "draws from a common population $\\text{Normal}(\\mu, \\tau)$, and within a "
        "group observations are $\\text{Normal}(\\theta_j, \\sigma)$.",
        "$$\\theta_j \\sim \\text{Normal}(\\mu, \\tau), \\qquad "
        "y_{ij} \\sim \\text{Normal}(\\theta_j, \\sigma).$$",
        "**Assumptions made explicit:** (a) groups are exchangeable (no group is "
        "special a priori), (b) the population of group means is Normal, (c) "
        "within-group noise $\\sigma$ is common across groups. We synthesize from "
        "known truth ($\\mu=5,\\ \\tau=0.8,\\ \\sigma=1$) with **few** obs per group "
        "so shrinkage is visible and the funnel can bite.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, group, J = data['y'], data['group'], data['J']\n"
        "print(f\"{J} groups x {data['n_per']} obs = {len(y)} observations\")\n"
        "print(f\"true mu={data['truth']['mu']}, tau={data['truth']['tau']}, \"\n"
        "      f\"sigma={data['truth']['sigma']}\")\n"
        "emp = np.array([y[group==j].mean() for j in range(J)])\n"
        "print('per-group empirical means:', np.round(emp, 2))"
    )

    nb.md(
        "## Step 2 — Model specification (with justified priors)",
        "Hyperpriors: $\\mu \\sim \\text{Normal}(5, 5)$ (weakly informative, centred "
        "near the plausible scale), $\\tau \\sim \\text{HalfNormal}(2)$ and "
        "$\\sigma \\sim \\text{HalfNormal}(2)$ (positive scales, gently shrunk).",
        "**Centered vs non-centered.** The centered form $\\theta_j \\sim "
        "\\text{Normal}(\\mu, \\tau)$ couples each $\\theta_j$ to $\\tau$; when "
        "$\\tau \\to 0$ the joint density narrows into a sharp funnel neck that NUTS "
        "cannot traverse at a fixed step size $\\Rightarrow$ **divergences**. The "
        "non-centered form writes $\\theta_j = \\mu + \\tau\\, z_j$ with "
        "$z_j \\sim \\text{Normal}(0,1)$, decoupling the geometry. We fit "
        "**non-centered** here and revisit the centered failure in the broken "
        "notebook.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data, parameterization='noncentered')\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate datasets implied by the prior and check that the implied "
        "observations cover the scale of the real data without absurd extremes. A "
        "HalfNormal(2) on $\\tau$ admits both near-complete-pooling ($\\tau\\approx0$) "
        "and substantial spread, which is the flexibility we want the data to "
        "resolve.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=400, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(pp, bins=40, color='#55A868', edgecolor='white', density=True)\n"
        "ax.axvline(y.mean(), color='red', lw=1.5, label='observed mean')\n"
        "ax.set(xlabel='y implied by prior', ylabel='density',\n"
        "       title='Prior predictive — covers the data scale')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS, non-centered)",
        "Settings: `draws=800, tune=1000, chains=4, target_accept=0.9`. Four chains "
        "give reliable split-$\\hat R$; `target_accept=0.9` is a mild safeguard for "
        "hierarchical geometry. The non-centered parameterization should sample "
        "cleanly with ~0 divergences.",
    )
    nb.code(
        "idata = fit(data, parameterization='noncentered', draws=800, tune=1000,\n"
        "            chains=4, target_accept=0.9, seed=101)"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R \\approx 1.00$, healthy ESS, and **divergences = 0**. For "
        "hierarchical models the **energy plot** (`az.plot_energy`) is essential: a "
        "marginal energy distribution that matches the energy-transition "
        "distribution indicates NUTS can move through the funnel; a large mismatch "
        "(BFMI low) warns of trouble even when $\\hat R$ looks fine.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu', 'tau', 'sigma']))\n"
        "n_div = int(idata.sample_stats['diverging'].sum())\n"
        "print(f'divergences: {n_div}')"
    )
    nb.code("az.plot_energy(idata); plt.tight_layout()")
    nb.code(
        "az.plot_trace(idata, var_names=['mu', 'tau', 'sigma']); plt.tight_layout()"
    )

    nb.md(
        "**The funnel, visualized.** Plot $\\log\\tau$ against a single group offset "
        "$z_0$. In the *non-centered* space this is a clean, roughly round cloud — "
        "no neck — which is exactly why the sampler succeeds. (The broken notebook "
        "shows the centered version, where this same pair forms the divergent "
        "funnel.)",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['tau', 'z'], coords={'group':[0]},\n"
        "             divergences=True)\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Does the fitted model reproduce the observed spread of the data? We overlay "
        "posterior-predictive datasets on the observed distribution; a good fit "
        "envelopes the data without systematic gaps.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Shrinkage: the heart of partial pooling",
        "Compare each group's **no-pooling** empirical mean to its **partial-pooling** "
        "posterior mean. Partial pooling pulls every group toward the grand mean "
        "$\\hat\\mu$, and pulls *small/noisy* groups more. This is the bias–variance "
        "trade made explicit: a little bias toward the population buys a large "
        "variance reduction, which is why partial pooling beats both extremes when "
        "groups have few observations.",
    )
    nb.code(
        "theta_post = idata.posterior['theta'].mean(dim=('chain','draw')).values\n"
        "mu_hat = float(idata.posterior['mu'].mean())\n"
        "fig, ax = plt.subplots(figsize=(6,4))\n"
        "for j in range(J):\n"
        "    ax.plot([0,1], [emp[j], theta_post[j]], color='grey', alpha=0.6)\n"
        "ax.scatter(np.zeros(J), emp, color='#C44E52', label='no pooling (empirical)')\n"
        "ax.scatter(np.ones(J), theta_post, color='#4C72B0', label='partial pooling')\n"
        "ax.axhline(mu_hat, color='k', ls='--', lw=1, label='grand mean (mu_hat)')\n"
        "ax.set(xticks=[0,1], xticklabels=['no pool','partial'],\n"
        "       ylabel='group mean', title='Shrinkage toward the grand mean')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Report the population parameters with uncertainty and a recovery check "
        "against the known truth. For a collaborator, the headline is the grand mean "
        "$\\mu$ and the between-group SD $\\tau$ (how much plates genuinely differ).",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "for res in check_recovery(idata, data['truth']):\n"
        "    print(res)"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The population mean readout is ~5.0 "
        "with a tight interval; plates differ from one another with a between-plate "
        "SD $\\tau\\approx0.8$ — real but modest variation. Per-plate estimates "
        "should be the *shrunken* partial-pooling means, not the raw averages, "
        "especially for plates with few wells. See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """The debugging exercise: centered parameterization -> funnel -> divergences."""
    nb = NotebookBuilder(title="Project 09 — BROKEN debugging exercise")
    nb.md(
        "# Project 09 — BROKEN notebook (debugging exercise)",
        "This notebook fits the **centered** parameterization with a deliberately "
        "low `target_accept`, so the funnel produces divergences. Your job: run it, "
        "read the divergence count, the **energy plot**, and the **funnel pairs "
        "plot**, then apply the non-centered fix. Answer key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, group, J = data['y'], data['group'], data['J']"
    )

    nb.md(
        "### BUG 1 — centered parameterization (the funnel).",
        "Here $\\theta_j \\sim \\text{Normal}(\\mu, \\tau)$ directly. When $\\tau$ is "
        "small this couples $\\theta_j$ and $\\tau$ into a sharp neck.",
    )
    nb.code(
        "with pm.Model(coords={'group': np.arange(J)}) as model:\n"
        "    mu = pm.Normal('mu', 5.0, 5.0)\n"
        "    tau = pm.HalfNormal('tau', 2.0)\n"
        "    sigma = pm.HalfNormal('sigma', 2.0)\n"
        "    # BUG 1: centered -> Neal's funnel\n"
        "    theta = pm.Normal('theta', mu=mu, sigma=tau, dims='group')\n"
        "    pm.Normal('y', mu=theta[group], sigma=sigma, observed=y)\n"
        "    # BUG 2: target_accept too low for this geometry\n"
        "    idata = pm.sample(draws=800, tune=1000, chains=4, target_accept=0.8,\n"
        "                      random_seed=RNG, progressbar=False)"
    )

    nb.md("### Symptom — count the divergences and read the diagnostics.")
    nb.code(
        "n_div = int(idata.sample_stats['diverging'].sum())\n"
        "print('divergences:', n_div)\n"
        "print(az.summary(idata, var_names=['mu','tau','sigma']))"
    )

    nb.md(
        "### Diagnostic 1 — energy plot.",
        "A mismatch between the marginal-energy and energy-transition distributions "
        "(low BFMI) is the hierarchical-model fingerprint of the funnel.",
    )
    nb.code("az.plot_energy(idata); plt.tight_layout()")

    nb.md(
        "### Diagnostic 2 — the funnel pairs plot.",
        "Plot $\\tau$ against a group's $\\theta_0$ with divergences highlighted. The "
        "red divergent points cluster in the **narrow neck** where $\\tau$ is small "
        "— the sampler cannot resolve that region.",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['tau','theta'], coords={'group':[0]},\n"
        "             divergences=True)\n"
        "plt.tight_layout()"
    )

    nb.md(
        "### The fix — non-centered parameterization.",
        "Re-express $\\theta_j = \\mu + \\tau\\, z_j$, $z_j \\sim \\text{Normal}(0,1)$, "
        "and raise `target_accept`. The neck disappears and divergences drop to ~0.",
    )
    nb.code(
        "with pm.Model(coords={'group': np.arange(J)}) as model_fixed:\n"
        "    mu = pm.Normal('mu', 5.0, 5.0)\n"
        "    tau = pm.HalfNormal('tau', 2.0)\n"
        "    sigma = pm.HalfNormal('sigma', 2.0)\n"
        "    z = pm.Normal('z', 0.0, 1.0, dims='group')\n"
        "    theta = pm.Deterministic('theta', mu + tau * z, dims='group')\n"
        "    pm.Normal('y', mu=theta[group], sigma=sigma, observed=y)\n"
        "    idata_fixed = pm.sample(draws=800, tune=1000, chains=4,\n"
        "                            target_accept=0.95, random_seed=RNG,\n"
        "                            progressbar=False)\n"
        "print('divergences after fix:', int(idata_fixed.sample_stats['diverging'].sum()))"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
