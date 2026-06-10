"""Emit notebook.ipynb (clean capstone workflow) and notebook_broken.ipynb.

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
    nb = NotebookBuilder(title="Project 20 — Capstone: Decision Under Uncertainty")

    nb.md(
        "# Project 20 — Capstone: Compound Prioritization & Decision Under Uncertainty",
        "**Scenario.** We screened $J$ compounds in a noisy assay with **unequal "
        "replication**. We must pick the single best compound to advance. This capstone "
        "integrates the whole workflow — a **hierarchical** model with partial pooling, "
        "full diagnostics + PPC, a **LOO** model comparison — and then crosses the "
        "finish line the other projects stop short of: it turns the posterior into an "
        "**explicit decision** via a cost-loss / expected-utility calculation.",
        "**Key pitfall.** *Stopping at the posterior.* And, in the broken version, "
        "ranking by **raw (unpooled) means** — which falls for the small-sample "
        "**winner's curse**.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Each compound $j$ has a true effect $\\theta_j$; we observe replicate assay "
        "readings $y_{j,i}\\sim N(\\theta_j,\\sigma)$. The compounds are exchangeable "
        "draws $\\theta_j\\sim N(\\mu,\\tau)$. **Replication is unequal** — a few "
        "compounds have many replicates, several have only 2-3 — which is exactly what "
        "lets a noisy compound post a lucky-high raw mean. We know the truths and the "
        "TRUE best compound.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "raw_pick = int(np.argmax(data['raw_means']))\n"
        "print(f\"J={data['j']} compounds; replicates={data['n_reps']}\")\n"
        "print(f\"TRUE best = #{data['best_true']} (theta={data['theta_true'][data['best_true']]:.2f})\")\n"
        "print(f\"RAW-mean winner = #{raw_pick} (raw={data['raw_means'][raw_pick]:.2f}, \"\n"
        "      f\"n={data['n_reps'][raw_pick]}) <- the winner's-curse trap\")"
    )

    nb.md(
        "## Step 2 — Model specification (hierarchical, non-centred)",
        "$$\\mu\\sim N(0,2),\\;\\tau\\sim\\text{HalfNormal}(1),\\;"
        "\\theta_j=\\mu+\\tau z_j,\\;z_j\\sim N(0,1),\\;\\sigma\\sim\\text{HalfNormal}(1),\\;"
        "y_{j,i}\\sim N(\\theta_j,\\sigma).$$",
        "**Partial pooling** is the engine: compounds with few replicates are shrunk "
        "toward $\\mu$ (their lucky-high raw means are pulled back), while "
        "well-replicated compounds barely move. We use the **non-centred** form "
        "($\\theta_j=\\mu+\\tau z_j$) to avoid the hierarchical funnel.",
    )
    nb.code(
        "from model import build_model, fit, fit_pooled, decision_table, posterior_theta\n"
        "model = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate compound screens from the priors. We want plausible spreads of "
        "effects — not all compounds identical (tau prior too tight) nor implausibly "
        "extreme (too loose).",
    )
    nb.code(
        "rng = np.random.default_rng(RNG)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "for _ in range(200):\n"
        "    mu = rng.normal(0,2); tau = abs(rng.normal(0,1))\n"
        "    ax.plot(rng.normal(mu, tau, size=data['j']), color='#4C72B0', alpha=0.05)\n"
        "ax.set(xlabel='compound index', ylabel='theta drawn from prior',\n"
        "       title='Prior predictive compound effects')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=600, tune=1000, chains=2, target_accept=0.95, cores=1`. The "
        "non-centred parameterisation plus a high `target_accept` keep the hierarchical "
        "geometry divergence-free.",
    )
    nb.code("idata = fit(data, draws=600, tune=1000, chains=2, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R$, ESS, and divergences (want 0 — the funnel is the usual culprit, "
        "tamed by non-centring). We also visualise the **shrinkage**: posterior "
        "$\\theta_j$ means vs raw means; few-replicate compounds should be pulled "
        "toward $\\mu$.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu','tau','sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code(
        "th = posterior_theta(idata)\n"
        "post_means = th.mean(axis=0)\n"
        "fig, ax = plt.subplots(figsize=(6,3.8))\n"
        "ax.scatter(data['raw_means'], post_means, c=data['n_reps'], cmap='viridis', zorder=3)\n"
        "lims=[min(data['raw_means'].min(),post_means.min())-0.3,\n"
        "      max(data['raw_means'].max(),post_means.max())+0.3]\n"
        "ax.plot(lims, lims, 'k--', alpha=0.5, label='no shrinkage')\n"
        "ax.set(xlabel='raw mean', ylabel='posterior theta mean',\n"
        "       title='Shrinkage (colour = #replicates)')\n"
        "ax.legend(); plt.colorbar(ax.collections[0], ax=ax, label='n_reps')"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "We confirm the model reproduces the spread of the observed replicate data "
        "(`az.plot_ppc`). A good hierarchical fit captures both within- and "
        "between-compound variation.",
    )
    nb.code("ax = az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Model comparison (hierarchical vs complete pooling) via LOO",
        "Is the hierarchical structure earning its keep? We compare against a "
        "**complete-pooling** model (one shared effect) using LOO. When compounds "
        "genuinely differ, the hierarchical model should win (higher `elpd_loo`).",
    )
    nb.code(
        "idata_pooled = fit_pooled(data, draws=600, tune=1000, chains=2, seed=101)\n"
        "cmp = az.compare({'hierarchical': idata, 'complete_pool': idata_pooled}, ic='loo')\n"
        "print(cmp[['rank','elpd_loo','p_loo','dse']])"
    )

    nb.md(
        "## Step 8 — DECISION (the point of the capstone)",
        "A posterior is not a decision. We define a **utility**: advancing compound $j$ "
        "yields $U_j=\\theta_j-\\text{cost}$. From the posterior we compute, per "
        "compound, the **expected utility**, the **probability of being best**, and the "
        "**expected regret** $E[\\max_k\\theta_k-\\theta_j]$. We recommend the compound "
        "that **minimises expected regret**. Watch how this can differ from picking the "
        "highest posterior mean — and how it overturns the raw-mean winner's curse.",
    )
    nb.code(
        "dec = decision_table(idata, cost=0.0)\n"
        "import pandas as pd\n"
        "tab = pd.DataFrame({'n_reps': data['n_reps'], 'raw_mean': data['raw_means'],\n"
        "                    'exp_util': dec['exp_util'], 'P_best': dec['p_best'],\n"
        "                    'exp_regret': dec['exp_regret']})\n"
        "print(tab.round(3))\n"
        "print()\n"
        "print(f\"true best          = #{data['best_true']}\")\n"
        "print(f\"raw-mean winner    = #{int(np.argmax(data['raw_means']))} (winner's curse)\")\n"
        "print(f\"posterior-mean pick= #{dec['argmax_posterior_mean']}\")\n"
        "print(f\"MIN-REGRET pick    = #{dec['recommend_min_regret']}  <-- recommendation\")"
    )
    nb.md(
        "**Reading the table.** `P_best` spreads probability across several plausible "
        "winners — honesty the raw maximum hides. The min-expected-regret choice "
        "balances *being good* against *uncertainty about being best*. It corrects the "
        "winner's curse: the lucky low-$n$ raw winner is shrunk away, and a "
        "well-supported compound is advanced.",
    )

    nb.md(
        "## Communication",
        "We recommend advancing the min-expected-regret compound, and we report its "
        "probability of being best and the runner-up — so the team knows whether to "
        "advance one compound or carry two. See `summary_onepager.md` for the "
        "non-technical version. **This is the capstone lesson: the workflow ends in a "
        "decision, not a posterior.**",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Seeded bugs: rank by raw means (winner's curse) + stop at the posterior."""
    nb = NotebookBuilder(title="Project 20 — BROKEN debugging exercise")
    nb.md(
        "# Project 20 — BROKEN notebook (debugging exercise)",
        "Seeded bugs centred on the capstone pitfalls: **ranking by raw (unpooled) "
        "means** (the winner's curse) and **stopping at the posterior** without a loss "
        "function. Run it, see the wrong recommendation, find each bug, fix it. Answer "
        "key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()"
    )
    nb.md(
        "### BUG 1 — rank compounds by their RAW means (no pooling).",
        "This ignores that low-replicate compounds have noisy means; the 'winner' is "
        "often a small-$n$ fluke.",
    )
    nb.code(
        "# BUG 1: pick the compound with the largest raw mean.\n"
        "raw_pick = int(np.argmax(data['raw_means']))\n"
        "print(f\"raw-mean recommendation = #{raw_pick} \"\n"
        "      f\"(n={data['n_reps'][raw_pick]}, raw={data['raw_means'][raw_pick]:.2f})\")\n"
        "print(f\"but the TRUE best is #{data['best_true']} \"\n"
        "      f\"(theta={data['theta_true'][data['best_true']]:.2f})\")"
    )
    nb.md(
        "### BUG 2 — fit a model but STOP at the posterior mean.",
        "Even a correct hierarchical fit is not a decision. Ranking by posterior mean "
        "ignores uncertainty (probability-of-best, expected regret). And here a second "
        "seeded modelling bug lurks: a CENTRED hierarchy that may diverge.",
    )
    nb.code(
        "# BUG 3: CENTRED hierarchy -> funnel / divergences at small tau.\n"
        "comp_idx = data['comp_idx']; y = data['y']; J = data['j']\n"
        "with pm.Model() as model:\n"
        "    mu = pm.Normal('mu', 0, 2)\n"
        "    tau = pm.HalfNormal('tau', 1)\n"
        "    theta = pm.Normal('theta', mu=mu, sigma=tau, shape=J)  # CENTRED\n"
        "    sigma = pm.HalfNormal('sigma', 1)\n"
        "    pm.Normal('y_obs', mu=theta[comp_idx], sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=500, tune=800, chains=2, cores=1,\n"
        "                      target_accept=0.9, random_seed=RNG, progressbar=False)\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code(
        "# BUG 2 continued: stopping at the posterior mean, no loss function.\n"
        "pm_pick = int(idata.posterior['theta'].mean(dim=('chain','draw')).argmax())\n"
        "print(f\"posterior-mean recommendation = #{pm_pick} (no decision-theoretic step)\")\n"
        "# The fix: compute expected utility / expected regret / P(best) and recommend\n"
        "# the min-regret compound -- see model.decision_table and the clean notebook."
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
