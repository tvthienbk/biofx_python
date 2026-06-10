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
    nb = NotebookBuilder(title="Project 08 — Many Predictors (Horseshoe)")

    nb.md(
        "# Project 08 — Many Predictors, Sparse Truth (Regularized Horseshoe)",
        "**Scenario.** We have ~20 candidate predictors (assay readouts, expression "
        "markers, engineered covariates) and want to know which *few* actually drive "
        "a continuous response. The truth is **sparse**: only 3 of the 20 "
        "coefficients are nonzero; the rest are exactly zero.",
        "**New skill.** *Shrinkage priors and LOO/WAIC comparison.* A wide-Normal "
        "(\"ridge\") prior spreads small spurious effects across all predictors. The "
        "**horseshoe** prior shrinks the noise coefficients hard toward zero while "
        "letting the few real ones escape — recovering sparsity. We compare the two "
        "with LOO and discuss the **double-dipping / selection-bias** trap.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "$$y_i=\\beta_0+\\sum_{j=1}^{P} X_{ij}\\beta_j+\\varepsilon_i,\\quad "
        "\\varepsilon_i\\sim N(0,\\sigma),\\quad \\text{only } K\\ll P \\text{ of the }"
        "\\beta_j\\neq 0.$$",
        "**Assumptions made explicit:** (a) the response is linear in the predictors; "
        "(b) the true coefficient vector is *sparse*; (c) predictor columns are "
        "standardized so coefficient magnitudes are comparable; (d) errors are "
        "Normal and homoscedastic. Truth: nonzero at indices 2, 7, 13 with values "
        "2.5, -1.8, 1.4; all other 17 coefficients are exactly 0.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "X, y = data['X'], data['y']\n"
        "print(f\"n={data['n']}, p={data['p']}, truly nonzero at {data['nonzero_idx']}\")\n"
        "print('truth:', {f'beta[{j}]': round(float(data['beta_true'][j]),2)\n"
        "                 for j in data['nonzero_idx']})"
    )

    nb.md(
        "## Step 2 — Two priors: wide-Normal ridge vs regularized horseshoe",
        "Both share $y=\\beta_0+X\\beta+N(0,\\sigma)$; only the prior on $\\beta$ differs.",
        "**Ridge:** $\\beta_j\\sim N(0,5)$ — every coefficient is equally free; no "
        "sparsity. **Horseshoe:** each $\\beta_j$ has scale $\\tau\\,\\tilde\\lambda_j$, "
        "where the *global* $\\tau$ controls how many coefficients survive and the "
        "*local* $\\lambda_j$ has heavy (half-Cauchy) tails so a coefficient is either "
        "crushed to ~0 or allowed to escape. The **regularized** variant caps the "
        "escaping magnitude via a slab, which stabilizes sampling.",
        "**Crucial implementation detail — non-centered parameterization.** We sample "
        "standardized $z_j\\sim N(0,1)$ and set $\\beta_j=z_j\\,\\tau\\,\\tilde\\lambda_j$. "
        "The *centered* version (sampling $\\beta_j\\sim N(0,\\tau\\lambda_j)$ directly) "
        "creates a pinched funnel and floods the run with divergences — that is the "
        "seeded bug in the broken notebook.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "m_ridge = build_model(data, model='ridge')\n"
        "m_hs = build_model(data, model='horseshoe')\n"
        "m_hs"
    )

    nb.md(
        "## Step 3 — Prior predictive check",
        "We confirm the horseshoe prior implies a sparse-ish coefficient vector: "
        "most prior-drawn coefficients sit near zero with a few heavy-tailed escapes "
        "— exactly the structure we believe in.",
    )
    nb.code(
        "with m_hs:\n"
        "    prior = pm.sample_prior_predictive(draws=400, random_seed=RNG)\n"
        "pb = prior.prior['beta'].values.reshape(-1)\n"
        "pb = pb[np.abs(pb) < np.percentile(np.abs(pb), 98)]\n"
        "fig, ax = plt.subplots(figsize=(6, 3.4))\n"
        "ax.hist(pb, bins=60, color='#4C72B0', edgecolor='white')\n"
        "ax.set(xlabel='prior-drawn coefficient (98th-pct clipped)', ylabel='count',\n"
        "       title='Horseshoe prior — spike near 0 with heavy tails')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS) for both models",
        "Settings: `draws=1000, tune=1000, chains=4, target_accept=0.95`. The high "
        "`target_accept` shrinks the step size, which the horseshoe geometry needs "
        "even when non-centered. We keep both idatas.",
    )
    nb.code(
        "idata_ridge = fit(data, model='ridge', draws=1000, tune=1000, chains=4, seed=101)\n"
        "idata_hs = fit(data, model='horseshoe', draws=1000, tune=1000, chains=4, seed=101)\n"
        "print('ridge divergences    :', int(idata_ridge.sample_stats['diverging'].sum()))\n"
        "print('horseshoe divergences:', int(idata_hs.sample_stats['diverging'].sum()))"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "For the non-centered horseshoe, divergences should be few or zero and "
        "$\\hat R\\approx1$. **If divergences flood in, suspect a centered "
        "parameterization** (the classic horseshoe funnel) — that is the diagnostic "
        "the broken notebook is built around. `az.plot_energy` and the divergence "
        "count are the tools.",
    )
    nb.code(
        "print(az.summary(idata_hs, var_names=['tau', 'sigma']))\n"
        "az.plot_energy(idata_hs); plt.tight_layout()"
    )

    nb.md(
        "## Step 6 — Posterior predictive & sparsity recovery",
        "The headline plot: a forest of the 20 coefficients under each prior. The "
        "ridge leaves the noise coefficients scattered with non-trivial intervals; "
        "the horseshoe collapses them onto zero and cleanly isolates the 3 real "
        "signals.",
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(7, 6))\n"
        "bh = idata_hs.posterior['beta']\n"
        "br = idata_ridge.posterior['beta']\n"
        "idx = np.arange(data['p'])\n"
        "mh = bh.mean(('chain','draw')).values\n"
        "hh = az.hdi(bh, hdi_prob=0.94)['beta'].values\n"
        "mr = br.mean(('chain','draw')).values\n"
        "hr = az.hdi(br, hdi_prob=0.94)['beta'].values\n"
        "ax.errorbar(mr, idx+0.15, xerr=[mr-hr[:,0], hr[:,1]-mr], fmt='o',\n"
        "            color='#C44E52', label='ridge', alpha=0.7)\n"
        "ax.errorbar(mh, idx-0.15, xerr=[mh-hh[:,0], hh[:,1]-mh], fmt='o',\n"
        "            color='#55A868', label='horseshoe')\n"
        "for j in data['nonzero_idx']:\n"
        "    ax.scatter(data['beta_true'][j], j, color='k', marker='|', s=200, zorder=5)\n"
        "ax.axvline(0, color='gray', ls=':')\n"
        "ax.set(xlabel='coefficient', ylabel='predictor index',\n"
        "       title='Horseshoe recovers sparsity; ridge does not (| = truth)')\n"
        "ax.legend(); plt.tight_layout()"
    )
    nb.code("az.plot_ppc(idata_hs, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — Model comparison (LOO) & recovery",
        "We compare the two priors with PSIS-LOO. The horseshoe typically matches or "
        "beats the ridge in expected predictive density while using **far fewer "
        "effective parameters** (`p_loo`) — it pays for the same fit with less "
        "complexity. We then confirm recovery of the nonzero coefficients.",
    )
    nb.code(
        "cmp = az.compare({'ridge': idata_ridge, 'horseshoe': idata_hs}, ic='loo')\n"
        "print(cmp[['rank', 'elpd_loo', 'p_loo', 'elpd_diff', 'dse', 'weight']])"
    )
    nb.code(
        "mh = idata_hs.posterior['beta'].mean(('chain','draw')).values\n"
        "zeros = [j for j in range(data['p']) if j not in data['nonzero_idx']]\n"
        "print('recovered nonzero:', {j: round(float(mh[j]),2) for j in data['nonzero_idx']})\n"
        "print('max |coef| among true-zeros (horseshoe):', round(float(np.max(np.abs(mh[zeros]))),3))\n"
        "mr = idata_ridge.posterior['beta'].mean(('chain','draw')).values\n"
        "print('max |coef| among true-zeros (ridge)    :', round(float(np.max(np.abs(mr[zeros]))),3))"
    )

    nb.md(
        "## Step 8 — Decision, communication & the double-dipping warning",
        "**The selection-bias trap.** A tempting but WRONG workflow: fit the model, "
        "pick the predictor with the largest coefficient, then re-fit *only* that "
        "predictor and report its (now tiny) p-value or (now narrow) interval as "
        "'significance'. This **double-dips** — using the same data to *select* and "
        "to *test* — and grossly overstates confidence. The Bayesian remedy is to "
        "let the **shrinkage prior** do selection *within one joint fit* and report "
        "the full posterior over all coefficients, including the uncertainty about "
        "which are nonzero. We never re-fit on a selected subset.",
    )
    nb.code(
        "# Honest reporting: posterior probability each |coef| exceeds a small threshold.\n"
        "beta = idata_hs.posterior['beta'].values.reshape(-1, data['p'])\n"
        "thr = 0.2\n"
        "p_active = (np.abs(beta) > thr).mean(0)\n"
        "for j in range(data['p']):\n"
        "    flag = '  <-- truly nonzero' if j in data['nonzero_idx'] else ''\n"
        "    if p_active[j] > 0.2 or j in data['nonzero_idx']:\n"
        "        print(f'beta[{j:2d}]: P(|coef|>{thr}) = {p_active[j]:.2f}{flag}')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** Three predictors (indices 2, 7, 13) "
        "drive the response; the other 17 are indistinguishable from zero. We report "
        "this from a single joint fit with a shrinkage prior — we did **not** "
        "cherry-pick a predictor and re-test it. See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 08 — BROKEN debugging exercise")
    nb.md(
        "# Project 08 — BROKEN notebook (debugging exercise)",
        "Two seeded bugs: a **centered horseshoe** that floods the sampler with "
        "divergences, and a **double-dipping** analysis that fakes significance. Run "
        "it, read the divergence diagnostics, find each bug, and fix it. Clean "
        "reference: `notebook.ipynb`; answer key: `BROKEN_BUGS.md` (don't peek).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "X, y = data['X'], data['y']\n"
        "n, p = X.shape"
    )
    nb.md(
        "### Model — BUG 1: a CENTERED horseshoe. The scale funnel will cause "
        "divergences.",
    )
    nb.code(
        "# BUG 1: sampling beta DIRECTLY through tau*lambda (centered). The joint of\n"
        "#        beta and its own scale is a pinched funnel that NUTS cannot explore;\n"
        "#        expect many divergences and unreliable estimates.\n"
        "with pm.Model() as model:\n"
        "    beta0 = pm.Normal('beta0', 0.0, 5.0)\n"
        "    sigma = pm.HalfNormal('sigma', 5.0)\n"
        "    tau = pm.HalfCauchy('tau', beta=0.1)\n"
        "    lam = pm.HalfCauchy('lam', beta=1.0, shape=p)\n"
        "    beta = pm.Normal('beta', 0.0, tau * lam, shape=p)   # BUG 1: centered funnel\n"
        "    mu = beta0 + pm.math.dot(X, beta)\n"
        "    pm.Normal('y', mu=mu, sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=800, chains=2, random_seed=RNG,\n"
        "                      progressbar=False, target_accept=0.9,\n"
        "                      idata_kwargs={'log_likelihood': True})"
    )
    nb.code(
        "# The divergence count is the alarm. Many divergences => the funnel.\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print(az.summary(idata, var_names=['tau']))\n"
        "az.plot_energy(idata); plt.tight_layout()  # mismatched marginal/energy => trouble"
    )
    nb.md(
        "### Interpretation — BUG 2: double-dipping. Selecting the top coefficient "
        "and re-testing it on the SAME data fakes significance.",
    )
    nb.code(
        "# BUG 2: pick the largest-|coef| predictor, then refit a SIMPLE regression\n"
        "#        on ONLY that predictor and brag about its narrow interval / 'p-value'.\n"
        "#        This uses the data twice (to SELECT and to TEST) -> selection bias.\n"
        "bmean = idata.posterior['beta'].mean(('chain','draw')).values\n"
        "j_star = int(np.argmax(np.abs(bmean)))\n"
        "with pm.Model() as cheat:\n"
        "    a = pm.Normal('a', 0, 5); b = pm.Normal('b', 0, 5); s = pm.HalfNormal('s', 5)\n"
        "    pm.Normal('y', mu=a + b * X[:, j_star], sigma=s, observed=y)\n"
        "    idata2 = pm.sample(draws=500, tune=500, chains=2, random_seed=RNG,\n"
        "                       progressbar=False)\n"
        "bb = idata2.posterior['b'].values.ravel()\n"
        "print(f'Selected predictor {j_star}; refit slope 94% interval:',\n"
        "      np.round(np.percentile(bb, [3, 97]), 2),\n"
        "      '<- this narrow interval is MISLEADING (double-dipped).')"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
