"""Emit notebook.ipynb (clean workflow) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py
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
    nb = NotebookBuilder(title="Project 16 — Detecting a shift (change-point)")

    nb.md(
        "# Project 16 — Detecting a shift (single change-point)",
        "**Scenario.** A reaction-kinetics time series of **counts** undergoes a "
        "**regime shift** at an unknown time $\\tau$ — a catalyst is added, a pathway "
        "switches on — after which the underlying Poisson rate changes. We want to "
        "locate the shift and quantify the before/after rates.",
        "**New skill.** Discrete *structural* change. **Key pitfall.** A **multimodal "
        "posterior over $\\tau$** — if more than one time looks like a plausible shift, "
        "the $\\tau$ posterior has multiple peaks and its *mean* is meaningless. We show "
        "two implementations (discrete $\\tau$ and a marginalized $\\tau$) and how to "
        "summarize a multimodal $\\tau$.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "$\\text{rate}_t=\\lambda_0$ if $t<\\tau$ else $\\lambda_1$; "
        "$y_t\\sim\\text{Poisson}(\\text{rate}_t)$. **Index convention:** $\\tau$ is the "
        "**first post-shift index**, so $0..\\tau{-}1$ use $\\lambda_0$ and "
        "$\\tau..T{-}1$ use $\\lambda_1$. **Assumptions:** (a) exactly one shift, (b) "
        "abrupt (not gradual) change, (c) constant rate within each regime, (d) Poisson "
        "counts (mean = variance). Truth: $\\tau=70, \\lambda_0=4, \\lambda_1=11, T=120$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); y = data['y']; t = data['truth']\n"
        "print(f\"T={data['T']}, true tau={t['tau']}, lam0={t['lam0']}, lam1={t['lam1']}\")"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(8,3))\n"
        "ax.bar(range(len(y)), y, color='#4C72B0', width=1.0)\n"
        "ax.axvline(t['tau']-0.5, color='red', ls='--', label='true tau')\n"
        "ax.set(xlabel='time t', ylabel='count y_t', title='Count series with a regime shift')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model: discrete tau (the classic switch model)",
        "$$\\tau\\sim\\text{DiscreteUniform}(1, T{-}1),\\quad "
        "\\lambda_0,\\lambda_1\\sim\\text{Exponential}(1/5),\\quad "
        "\\text{rate}_t=\\text{switch}(\\tau>t,\\ \\lambda_0,\\ \\lambda_1).$$",
        "PyMC samples $\\lambda$ with NUTS and the integer $\\tau$ with Metropolis. The "
        "`switch(tau > t, lam0, lam1)` direction is the easy place to introduce an "
        "off-by-one or sign error (see the broken notebook).",
    )
    nb.code(
        "from model import build_model, fit, build_marginal_model, fit_marginal, "
        "tau_posterior_from_marginal\n"
        "model = build_model(data); model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "The prior on the rates is Exponential(1/5) (mean 5). Prior-predictive count "
        "series should span a plausible range of levels and shift locations — not, say, "
        "rates in the thousands. We check the implied count magnitudes are sane.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=300, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.reshape(-1, len(y))\n"
        "print('prior-predictive count range:', int(pp.min()), 'to', int(pp.max()),\n"
        "      '| median per-series mean:', round(float(np.median(pp.mean(1))),2))"
    )

    nb.md(
        "## Step 4 — Inference (NUTS + Metropolis)",
        "`draws=1000, tune=1000, chains=4`. Four chains help confirm the $\\tau$ "
        "posterior is the same mode across chains (a multimodal $\\tau$ would show "
        "chains favouring different peaks).",
    )
    nb.code("idata = fit(data, draws=1000, tune=1000, chains=4, seed=16)")

    nb.md(
        "## Step 5 — Diagnostics & the tau posterior",
        "Check R-hat/ESS for the rates. For $\\tau$, **do not summarize by the mean** — "
        "inspect the full discrete posterior. Here the shift is sharp so $\\tau$ "
        "concentrates on one value; we still plot the distribution and report the "
        "**mode** and a credible set.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['lam0','lam1']))\n"
        "tau_draws = idata.posterior['tau'].values.ravel().astype(int)\n"
        "vals, counts = np.unique(tau_draws, return_counts=True)\n"
        "mode = vals[counts.argmax()]\n"
        "print(f'tau MODE = {mode} (true {t[\"tau\"]}); tau MEAN = {tau_draws.mean():.2f} '\n"
        "      f'(mean can mislead if multimodal)')"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(7,3))\n"
        "ax.bar(vals, counts/counts.sum(), color='#55A868', width=1.0)\n"
        "ax.axvline(t['tau'], color='red', ls='--', label='true tau')\n"
        "ax.set(xlabel='tau', ylabel='P(tau | y)', title='Posterior over the change-point')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Compare observed counts to posterior-predictive counts; the two-level "
        "structure (low before, high after) should be reproduced.",
    )
    nb.code("ax = az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — A second implementation: marginalize tau",
        "We can sum the likelihood over all $T{-}1$ candidate $\\tau$ analytically, "
        "leaving only $\\lambda_0,\\lambda_1$ to sample (pure NUTS, no discrete step). "
        "The full $P(\\tau\\mid y)$ is then reconstructed from the per-$\\tau$ weights. "
        "The two implementations should agree — a strong cross-check.",
    )
    nb.code(
        "idm = fit_marginal(data, draws=1000, tune=1000, chains=2, seed=16)\n"
        "print(az.summary(idm, var_names=['lam0','lam1']))\n"
        "probs = tau_posterior_from_marginal(idm, data)\n"
        "print('marginal-model tau MODE =', int(np.argmax(probs))+1, '(true', t['tau'], ')')"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(7,3))\n"
        "ax.bar(np.arange(1, data['T']), probs, color='#8172B3', width=1.0)\n"
        "ax.axvline(t['tau'], color='red', ls='--', label='true tau')\n"
        "ax.set(xlabel='tau', ylabel='P(tau | y)', title='Marginalized model: P(tau | y)')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "For a collaborator: 'The rate jumps from ~4 to ~11 counts/bin at about bin 70 "
        "(94% credible set [68, 71]).' Report the **mode/credible set** of $\\tau$, the "
        "two rates, and the **fold-change** $\\lambda_1/\\lambda_0$. See "
        "`summary_onepager.md`.",
    )
    nb.code(
        "l0 = idata.posterior['lam0'].values.ravel(); l1 = idata.posterior['lam1'].values.ravel()\n"
        "fold = l1 / l0\n"
        "print(f'rate before = {l0.mean():.2f}, after = {l1.mean():.2f}')\n"
        "print(f'fold-change = {fold.mean():.2f} (94% [{np.percentile(fold,3):.2f}, "
        "{np.percentile(fold,97):.2f}])')"
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Broken version: wrong switch direction + tau summarized by mean. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 16 — BROKEN debugging exercise")
    nb.md(
        "# Project 16 — BROKEN notebook (change-point pitfalls)",
        "Seeded bugs: a wrong-direction switch and treating a (potentially multimodal) "
        "tau posterior by its mean. Run it, read the diagnostics, fix each. Clean "
        "reference: `notebook.ipynb`; answer key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); y = data['y']; t = data['truth']; T = data['T']\n"
        "idx = np.arange(T)"
    )
    nb.md(
        "### BUG 1 — wrong switch direction (rates swapped before/after tau).",
        "`switch(tau < idx, ...)` (or swapping lam0/lam1) assigns the pre-shift rate to "
        "the post-shift region. The model still runs but fits a mirror-image change.",
    )
    nb.code(
        "with pm.Model() as model:\n"
        "    tau = pm.DiscreteUniform('tau', lower=1, upper=T-1)\n"
        "    lam0 = pm.Exponential('lam0', 1/5.)\n"
        "    lam1 = pm.Exponential('lam1', 1/5.)\n"
        "    # BUG 1: should be switch(tau > idx, lam0, lam1)\n"
        "    rate = pm.math.switch(tau < idx, lam0, lam1)\n"
        "    pm.Poisson('y', mu=rate, observed=y)\n"
        "    # BUG 2: too few tune steps for the discrete+continuous geometry\n"
        "    idata = pm.sample(draws=800, tune=100, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['tau','lam0','lam1']))\n"
        "print('true tau,lam0,lam1 =', t['tau'], t['lam0'], t['lam1'])\n"
        "# Symptom: lam0/lam1 come out swapped relative to truth."
    )
    nb.md(
        "### BUG 3 — summarizing tau by its mean.",
        "If the tau posterior is multimodal (or just skewed), the **mean** falls between "
        "peaks and points at a time the data do not support.",
    )
    nb.code(
        "tau_draws = idata.posterior['tau'].values.ravel()\n"
        "# BUG 3: reporting the mean of a discrete (possibly multimodal) tau\n"
        "print('reported tau =', tau_draws.mean())\n"
        "fig, ax = plt.subplots(figsize=(7,3))\n"
        "ax.hist(tau_draws, bins=np.arange(0, T+1)-0.5, color='#C44E52')\n"
        "ax.axvline(tau_draws.mean(), color='k', label='reported mean (misleading)')\n"
        "ax.legend(); ax.set_title('Summarize a discrete tau by its MODE, not its mean')\n"
        "plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
