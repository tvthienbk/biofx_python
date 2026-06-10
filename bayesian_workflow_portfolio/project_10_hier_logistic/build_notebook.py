"""Emit notebook.ipynb (clean) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py

Clean notebook: non-centered hierarchical logistic, ~0 divergences, shows
varying intercepts and shrinkage. Broken notebook: centered parameterization +
over-tight tau prior -> excessive pooling of family intercepts (the shrinkage
pathology) plus divergences; then the non-centered, sensible-prior fix.
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
    nb = NotebookBuilder(title="Project 10 — Varying Intercepts (Hierarchical Logistic)")

    nb.md(
        "# Project 10 — Varying Intercepts (Hierarchical Logistic)",
        "**Scenario.** A binary binding assay is run across many protein "
        "*families*. Each family has its own baseline binding propensity (a "
        "group-varying intercept on the log-odds scale), and a global covariate "
        "$x$ shifts the log-odds for every observation.",
        "**New skill:** group-level structure inside a **GLM** — a hierarchical "
        "logistic regression with varying intercepts. **Key pitfall:** with few "
        "groups it is easy to **pool too aggressively**, collapsing real "
        "family-to-family differences toward a single intercept. The amount of "
        "pooling is governed by the between-family SD $\\tau$ and its prior.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Families are **exchangeable**: their intercepts $\\alpha_g$ are draws from "
        "a common population $\\text{Normal}(\\mu, \\tau)$.",
        "$$\\alpha_g \\sim \\text{Normal}(\\mu, \\tau), \\quad "
        "\\text{logit}(p_i) = \\alpha_{g[i]} + \\beta x_i, \\quad "
        "y_i \\sim \\text{Bernoulli}(p_i).$$",
        "**Assumptions:** (a) families exchangeable, (b) Normal population of "
        "intercepts, (c) a single global slope $\\beta$ shared across families, "
        "(d) Bernoulli outcomes. Truth: $\\mu=-0.3,\\ \\tau=0.9,\\ \\beta=1.2$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, x, group, G = data['y'], data['x'], data['group'], data['G']\n"
        "print(f\"{G} families x {data['n_per']} obs = {len(y)} observations\")\n"
        "rates = np.array([y[group==g].mean() for g in range(G)])\n"
        "print('per-family empirical binding rates:', np.round(rates, 2))"
    )

    nb.md(
        "## Step 2 — Model specification with justified priors",
        "Hyperpriors: $\\mu \\sim \\text{Normal}(0, 1.5)$ and $\\beta \\sim "
        "\\text{Normal}(0, 1.5)$ are weakly informative on the **log-odds** scale "
        "(an SD of 1.5 already spans binding probabilities from ~0.05 to ~0.95). "
        "$\\tau \\sim \\text{HalfNormal}(1)$ is a weakly-informative positive scale "
        "prior; it must not be so tight that it forces all families to share one "
        "intercept (over-pooling), nor so vague it lets a 10-family dataset invent "
        "spurious spread.",
        "**Non-centered** as in Project 09: $\\alpha_g = \\mu + \\tau z_g$, "
        "$z_g \\sim \\text{Normal}(0,1)$ — the funnel hazard is identical in a GLM.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data, parameterization='noncentered')\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "On the log-odds scale a careless prior can push every implied probability "
        "to 0 or 1. We simulate from the prior and check the implied binding rates "
        "spread sensibly across $[0,1]$ rather than piling at the extremes.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=400, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.reshape(-1, len(y)).mean(axis=1)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(pp, bins=30, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='dataset binding rate implied by prior', ylabel='count',\n"
        "       title='Prior predictive — sensible spread, not piled at 0/1')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS, non-centered)",
        "`draws=800, tune=1000, chains=4, target_accept=0.9`. Four chains for "
        "$\\hat R$, a mild `target_accept` bump for the hierarchical geometry.",
    )
    nb.code(
        "idata = fit(data, parameterization='noncentered', draws=800, tune=1000,\n"
        "            chains=4, target_accept=0.9, seed=101)"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R$, ESS, **divergences = 0**, and the **energy plot**. The "
        "energy plot is the hierarchical canary: a marginal/transition mismatch "
        "signals the funnel even if $\\hat R$ looks fine.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu','tau','beta']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_energy(idata); plt.tight_layout()")
    nb.code("az.plot_trace(idata, var_names=['mu','tau','beta']); plt.tight_layout()")

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Compare observed per-family binding counts to the posterior-predictive "
        "distribution. A good fit reproduces the spread of family rates.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Varying intercepts & shrinkage",
        "Plot each family's no-pooling empirical log-odds against its "
        "partial-pooling posterior intercept $\\alpha_g$. Families are pulled "
        "toward the population mean $\\hat\\mu$, and the noisiest (most extreme) "
        "are pulled most. This is the GLM version of Project 09's shrinkage. "
        "**The pitfall** is letting $\\tau$ (via its prior) shrink so hard that all "
        "$\\alpha_g$ collapse to $\\hat\\mu$ — see the broken notebook.",
    )
    nb.code(
        "eps = 0.5\n"
        "emp_logodds = np.log((rates*data['n_per']+eps)/((1-rates)*data['n_per']+eps))\n"
        "alpha_post = idata.posterior['alpha'].mean(dim=('chain','draw')).values\n"
        "mu_hat = float(idata.posterior['mu'].mean())\n"
        "fig, ax = plt.subplots(figsize=(6,4))\n"
        "for g in range(G):\n"
        "    ax.plot([0,1], [emp_logodds[g], alpha_post[g]], color='grey', alpha=0.6)\n"
        "ax.scatter(np.zeros(G), emp_logodds, color='#C44E52', label='no pooling')\n"
        "ax.scatter(np.ones(G), alpha_post, color='#4C72B0', label='partial pooling')\n"
        "ax.axhline(mu_hat, color='k', ls='--', lw=1, label='mu_hat')\n"
        "ax.set(xticks=[0,1], xticklabels=['no pool','partial'],\n"
        "       ylabel='family intercept (log-odds)', title='Shrinkage of intercepts')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Recover the population parameters and the global slope, then verify against "
        "known truth.",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "for res in check_recovery(idata, data['truth']):\n"
        "    print(res)"
    )
    nb.md(
        "**Conclusion (for a collaborator).** Higher physicochemical score $x$ "
        "raises binding odds ($\\beta>0$, robustly). Families do differ in baseline "
        "propensity ($\\tau\\approx0.9$), but with only ~12 assays each, report the "
        "**shrunken** per-family intercepts, not the raw rates. See "
        "`summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Debug exercise: centered + over-tight tau prior -> over-pooling pathology."""
    nb = NotebookBuilder(title="Project 10 — BROKEN debugging exercise")
    nb.md(
        "# Project 10 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs** that make the model pool the family "
        "intercepts too aggressively and sample badly. Run it, read the diagnostics "
        "and the shrinkage plot, then fix it. Answer key: `BROKEN_BUGS.md`.",
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
        "rates = np.array([y[group==g].mean() for g in range(G)])"
    )

    nb.md(
        "### BUGS — centered parameterization AND an over-tight tau prior.",
        "BUG 1: `tau ~ HalfNormal(0.05)` is far too tight — it forces every family "
        "intercept toward a single value (over-pooling). BUG 2: the **centered** "
        "form re-introduces the funnel, worst exactly where the tight prior pushes "
        "$\\tau$ (near 0).",
    )
    nb.code(
        "with pm.Model(coords={'group': np.arange(G)}) as model:\n"
        "    mu = pm.Normal('mu', 0.0, 1.5)\n"
        "    # BUG 1: over-tight tau prior -> excessive pooling\n"
        "    tau = pm.HalfNormal('tau', 0.05)\n"
        "    beta = pm.Normal('beta', 0.0, 1.5)\n"
        "    # BUG 2: centered parameterization -> funnel\n"
        "    alpha = pm.Normal('alpha', mu=mu, sigma=tau, dims='group')\n"
        "    eta = alpha[group] + beta * x\n"
        "    pm.Bernoulli('y', logit_p=eta, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=1000, chains=4, target_accept=0.9,\n"
        "                      random_seed=RNG, progressbar=False)"
    )

    nb.md("### Symptom — divergences and a near-zero tau.")
    nb.code(
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print(az.summary(idata, var_names=['mu','tau','beta']))"
    )

    nb.md("### Diagnostic 1 — energy plot (funnel fingerprint).")
    nb.code("az.plot_energy(idata); plt.tight_layout()")

    nb.md(
        "### Diagnostic 2 — the shrinkage pathology.",
        "Plot the recovered family intercepts. Under the over-tight prior they "
        "**collapse onto $\\hat\\mu$** — the model has erased real family "
        "differences. Compare to the clean notebook's spread of intercepts.",
    )
    nb.code(
        "alpha_post = idata.posterior['alpha'].mean(dim=('chain','draw')).values\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.scatter(range(G), alpha_post, color='#C44E52', label='posterior alpha_g')\n"
        "ax.axhline(float(idata.posterior['mu'].mean()), color='k', ls='--',\n"
        "           label='mu_hat')\n"
        "ax.set(xlabel='family', ylabel='intercept (log-odds)',\n"
        "       title='Over-pooling: intercepts collapse to the grand mean')\n"
        "ax.legend(); plt.tight_layout()\n"
        "print('intercept spread (max-min):', float(alpha_post.max()-alpha_post.min()))"
    )

    nb.md(
        "### The fix — non-centered + a sensible tau prior.",
        "Use `tau ~ HalfNormal(1)` (lets the data express real spread) and the "
        "non-centered $\\alpha_g = \\mu + \\tau z_g$. Divergences drop to ~0 and the "
        "family intercepts regain their genuine spread.",
    )
    nb.code(
        "with pm.Model(coords={'group': np.arange(G)}) as fixed:\n"
        "    mu = pm.Normal('mu', 0.0, 1.5)\n"
        "    tau = pm.HalfNormal('tau', 1.0)\n"
        "    beta = pm.Normal('beta', 0.0, 1.5)\n"
        "    z = pm.Normal('z', 0.0, 1.0, dims='group')\n"
        "    alpha = pm.Deterministic('alpha', mu + tau * z, dims='group')\n"
        "    pm.Bernoulli('y', logit_p=alpha[group] + beta * x, observed=y)\n"
        "    idata_fixed = pm.sample(draws=800, tune=1000, chains=4,\n"
        "                            target_accept=0.95, random_seed=RNG,\n"
        "                            progressbar=False)\n"
        "a2 = idata_fixed.posterior['alpha'].mean(dim=('chain','draw')).values\n"
        "print('divergences after fix:', int(idata_fixed.sample_stats['diverging'].sum()))\n"
        "print('intercept spread after fix:', float(a2.max()-a2.min()))"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
