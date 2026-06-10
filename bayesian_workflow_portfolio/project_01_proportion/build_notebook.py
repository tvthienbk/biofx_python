"""Emit notebook.ipynb (clean workflow) and notebook_broken.ipynb (debug exercise).

Run:  python build_notebook.py
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
    nb = NotebookBuilder(title="Project 01 — Estimating a Proportion")

    nb.md(
        "# Project 01 — Estimating a Proportion (Beta–Binomial)",
        "**Scenario.** A biochemical binary assay is run many times; each run "
        "succeeds with an unknown probability $\\theta$. We want the full posterior "
        "for $\\theta$, not just a point estimate.",
        "This is the simplest Bayesian problem — one parameter — so we use it to "
        "learn the **entire workflow**: data story → model → prior predictive → "
        "inference → diagnostics → posterior predictive → criticism → decision.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "from scipy.stats import beta as beta_dist\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "We assume each assay run is an independent Bernoulli trial with a common "
        "success probability $\\theta$. **Assumptions made explicit:** (a) runs are "
        "independent, (b) $\\theta$ is constant across runs (no drift/batch effects), "
        "(c) outcomes are truly binary. We synthesize data from a known "
        "$\\theta_\\text{true}=0.62$ so we can later check recovery.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']\n"
        "print(f\"n={data['n']} runs, k={data['k']} successes, \"\n"
        "      f\"empirical rate={data['k']/data['n']:.3f}, true theta={data['truth']['theta']}\")"
    )

    nb.md(
        "## Step 2 — Model specification (likelihood + justified priors)",
        "$$y_i \\sim \\text{Bernoulli}(\\theta), \\qquad \\theta \\sim \\text{Beta}(2,2).$$",
        "**Why Beta(2,2) and not Beta(1,1)?** A 'flat' Beta(1,1) places as much mass "
        "on $\\theta=0.999$ as on $\\theta=0.5$, which is *not* an innocent default for "
        "an assay — it over-trusts extreme rates when data are scarce. Beta(2,2) is "
        "mild, unimodal, centred at 0.5, and pulls gently away from the degenerate "
        "edges. It is **weakly informative**, the recommended posture.",
    )
    nb.code(
        "from model import build_model, fit, analytic_posterior\n"
        "model = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "Before touching the data we simulate datasets *implied by the prior*. If the "
        "prior implied, say, that 95% of assays succeed essentially never or always, "
        "we'd fix the prior now. We look at the distribution of the success **count** "
        "$k$ under the prior; Beta(2,2) should spread mass across the whole 0–n range, "
        "concentrated mildly toward the middle.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=1000, random_seed=RNG)\n"
        "prior_k = prior.prior_predictive['y'].sum(dim='y_dim_2' if 'y_dim_2' in "
        "prior.prior_predictive['y'].dims else prior.prior_predictive['y'].dims[-1]).values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(prior_k, bins=np.arange(0, data['n']+2)-0.5, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='successes k implied by prior', ylabel='count',\n"
        "       title='Prior predictive — sensible spread, no pathology')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Even though this model has a closed-form conjugate posterior, we sample with "
        "**NUTS** to learn the machinery. Settings: `draws=1000, tune=1000, chains=4`. "
        "Four chains let us compute split-$\\hat R$ reliably; 1000 tuning steps let NUTS "
        "adapt its step size and mass matrix. We fix `random_seed` for reproducibility.",
    )
    nb.code("idata = fit(data, draws=1000, tune=1000, chains=4, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "We check: **$\\hat R$** (should be ≈ 1.00; > 1.01 signals chains disagree), "
        "**ESS** (bulk/tail effective sample size; want ≳ 400), and **divergences** "
        "(should be 0 for this easy geometry). The trace should look like 'fuzzy "
        "caterpillars' with well-mixed chains.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['theta']))\n"
        "n_div = int(idata.sample_stats['diverging'].sum())\n"
        "print(f'divergences: {n_div}')"
    )
    nb.code("az.plot_trace(idata, var_names=['theta']); plt.tight_layout()")

    nb.md(
        "**What if diagnostics fail?** For this model they won't, but the general "
        "remedies are: raise `target_accept` (e.g. 0.95) to shrink step size and clear "
        "divergences; increase `tune`/`draws` for low ESS; and if $\\hat R$ stays high, "
        "suspect a multimodal or non-identified model (we'll meet those in later projects).",
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "We compare the observed number of successes to the distribution of successes "
        "in datasets simulated from the *posterior*. If the model is adequate, the "
        "observed value sits comfortably inside the posterior-predictive spread.",
    )
    nb.code(
        "ax = az.plot_ppc(idata, num_pp_samples=200)\n"
        "plt.tight_layout()"
    )
    nb.code(
        "pp = idata.posterior_predictive['y']\n"
        "pp_k = pp.sum(dim=pp.dims[-1]).values.ravel()\n"
        "p_value = float(np.mean(pp_k >= data['k']))\n"
        "print(f'observed k={data[\"k\"]}; posterior-predictive p-value={p_value:.3f} "
        "(near 0.5 = good fit)')"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison",
        "Sanity check against the **exact conjugate posterior** Beta$(2+k,\\,2+n-k)$ — "
        "MCMC should match it closely. (With a single parameter and one model there is "
        "no LOO/WAIC comparison to make; later projects introduce competing models.)",
    )
    nb.code(
        "a_post, b_post = analytic_posterior(data)\n"
        "grid = np.linspace(0, 1, 400)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "az.plot_dist(idata.posterior['theta'].values.ravel(), ax=ax, color='#4C72B0',\n"
        "             label='MCMC posterior')\n"
        "ax.plot(grid, beta_dist.pdf(grid, a_post, b_post), 'k--', label='analytic Beta')\n"
        "ax.axvline(data['truth']['theta'], color='red', lw=1, label='true theta')\n"
        "ax.set(xlabel='theta', ylabel='density', title='MCMC vs analytic posterior')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Translate the posterior into something a collaborator can use: a point "
        "estimate with a credible interval, and the probability the assay beats a "
        "decision threshold (say 0.5).",
    )
    nb.code(
        "post = idata.posterior['theta'].values.ravel()\n"
        "mean = post.mean(); lo, hi = np.percentile(post, [3, 97])\n"
        "p_above = float(np.mean(post > 0.5))\n"
        "print(f'Posterior mean theta = {mean:.3f}')\n"
        "print(f'94% credible interval = [{lo:.3f}, {hi:.3f}]')\n"
        "print(f'P(theta > 0.5 | data) = {p_above:.3f}')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The assay's true success rate is most "
        "plausibly around 0.59 with a 94% credible interval of roughly [0.49, 0.69]. "
        "We are ~92% sure the rate exceeds one-half. The next step is the decision "
        "(see `summary_onepager.md`), not the posterior itself.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """A deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 01 — BROKEN debugging exercise")
    nb.md(
        "# Project 01 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs**. Your job: run it, read the "
        "diagnostics, find each bug, and fix it. The clean reference is `notebook.ipynb`; "
        "the answer key is `BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']"
    )
    nb.md("### Model — something here over-trusts extreme rates, and the sampler is starved.")
    nb.code(
        "# BUG 1: a 'flat' prior that is not as innocent as it looks.\n"
        "# BUG 2: far too few tuning steps + 1 chain -> unreliable diagnostics.\n"
        "with pm.Model() as model:\n"
        "    theta = pm.Beta('theta', alpha=1.0, beta=1.0)\n"
        "    pm.Bernoulli('y', p=theta, observed=y)\n"
        "    idata = pm.sample(draws=1000, tune=5, chains=1, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code("print(az.summary(idata, var_names=['theta']))")
    nb.md(
        "### Posterior predictive — BUG 3: a wrong reduction axis makes the PPC nonsensical.")
    nb.code(
        "with model:\n"
        "    idata.extend(pm.sample_posterior_predictive(idata, random_seed=RNG,\n"
        "                                                progressbar=False))\n"
        "pp = idata.posterior_predictive['y']\n"
        "# BUG 3: summing over the wrong dimension (chain/draw instead of observations)\n"
        "pp_k = pp.sum(dim='draw').values.ravel()\n"
        "print('observed k =', data['k'], 'predicted k mean =', pp_k.mean())"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
