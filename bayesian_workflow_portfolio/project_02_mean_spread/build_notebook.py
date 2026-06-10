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
    nb = NotebookBuilder(title="Project 02 — Estimating a Mean & Spread")

    nb.md(
        "# Project 02 — Estimating a Mean & Spread (Normal $\\mu,\\sigma$)",
        "**Scenario.** A concentration is measured $N$ times on the same sample. "
        "Each replicate is the true concentration $\\mu$ plus Gaussian noise of "
        "unknown SD $\\sigma$. We want the **joint** posterior for $(\\mu,\\sigma)$.",
        "**New skill:** jointly inferring a *scale* $\\sigma$ alongside a location "
        "$\\mu$, with priors on both. **Key pitfall:** improper/uninformative scale "
        "priors — a flat prior on $\\sigma$ is *not* harmless.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240602"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "We assume each measurement is independent and Normally distributed around a "
        "common true concentration $\\mu$ with constant noise SD $\\sigma$. "
        "**Assumptions made explicit:** (a) measurements independent, (b) $\\mu$ and "
        "$\\sigma$ constant across replicates (no drift/heteroscedasticity), "
        "(c) noise is symmetric/Gaussian (no heavy tails or outliers). We synthesize "
        "from known $\\mu_\\text{true}=5.0$, $\\sigma_\\text{true}=1.2$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']\n"
        "print(f\"n={data['n']}, empirical mean={y.mean():.3f}, \"\n"
        "      f\"empirical sd={y.std(ddof=1):.3f}\")\n"
        "print('true:', data['truth'])"
    )

    nb.md(
        "## Step 2 — Model specification (likelihood + justified priors)",
        "$$y_i \\sim \\text{Normal}(\\mu, \\sigma), \\quad \\mu \\sim \\text{Normal}(5, 10), "
        "\\quad \\sigma \\sim \\text{HalfNormal}(5).$$",
        "**Why these priors?** The location prior $\\text{Normal}(5,10)$ is *broad* "
        "(2 SD spans roughly $-15$ to $25$) — weakly-informative on the data's scale. "
        "The scale prior is where care matters: $\\sigma$ must be positive, so we use a "
        "**proper** $\\text{HalfNormal}(5)$, which concentrates mass on plausible noise "
        "levels and has a finite integral. A 'flat' improper prior on $\\sigma$ "
        "(uniform on $(0,\\infty)$) is **not** uninformative — it puts unbounded mass on "
        "absurdly large variances and can destabilize sampling. That is the seeded bug "
        "in the broken notebook.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate datasets implied by the prior. With $\\mu\\sim N(5,10)$ and "
        "$\\sigma\\sim\\text{HalfNormal}(5)$ the implied measurements should span a "
        "wide-but-not-insane range. If a flat $\\sigma$ prior were used, the prior "
        "predictive would contain datasets with astronomically large spread — the "
        "visual tell of an improper scale prior.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=500, random_seed=RNG)\n"
        "obs_dim = [d for d in prior.prior_predictive['y'].dims if d not in ('chain','draw')][0]\n"
        "pp_means = prior.prior_predictive['y'].mean(dim=obs_dim).values.ravel()\n"
        "pp_sds = prior.prior_predictive['y'].std(dim=obs_dim).values.ravel()\n"
        "fig, axes = plt.subplots(1, 2, figsize=(9,3.5))\n"
        "axes[0].hist(pp_means, bins=30, color='#55A868', edgecolor='white')\n"
        "axes[0].set(xlabel='dataset mean implied by prior', ylabel='count', title='prior predictive means')\n"
        "axes[1].hist(pp_sds, bins=30, color='#C44E52', edgecolor='white')\n"
        "axes[1].set(xlabel='dataset sd implied by prior', ylabel='count', title='prior predictive spreads')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "We sample with `draws=1000, tune=1000, chains=4`. Four chains give reliable "
        "split-$\\hat R$; ample tuning lets NUTS adapt its step size and mass matrix to "
        "the joint $(\\mu,\\sigma)$ geometry. The seed is fixed for reproducibility.",
    )
    nb.code("idata = fit(data, draws=1000, tune=1000, chains=4, seed=202)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "We check $\\hat R\\approx 1.00$, bulk/tail ESS $\\gtrsim 400$ for **both** "
        "parameters, and 0 divergences. The trace should show well-mixed caterpillars. "
        "Scale parameters can be harder to sample than locations, so watch $\\sigma$'s "
        "ESS in particular.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu', 'sigma']))\n"
        "n_div = int(idata.sample_stats['diverging'].sum())\n"
        "print(f'divergences: {n_div}')"
    )
    nb.code("az.plot_trace(idata, var_names=['mu', 'sigma']); plt.tight_layout()")

    nb.md(
        "**What if diagnostics fail?** Low ESS on $\\sigma$ or divergences usually "
        "signal a bad scale prior or a sampler starved of tuning. Remedies: raise "
        "`target_accept`, increase `tune`, and — crucially — use a *proper* scale prior. "
        "An improper flat $\\sigma$ prior often manifests as poor mixing and a posterior "
        "with a heavy right tail that never settles.",
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "We overlay replicated datasets from the posterior on the observed data. If the "
        "Normal model is adequate, the observed histogram/density sits inside the "
        "posterior-predictive band. This is also where non-Gaussian features (outliers, "
        "skew) would betray themselves — motivation for the robust models later.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")
    nb.code(
        "pp = idata.posterior_predictive['y']\n"
        "obs_dim = [d for d in pp.dims if d not in ('chain','draw')][0]\n"
        "pp_sd = pp.std(dim=obs_dim).values.ravel()\n"
        "obs_sd = y.std(ddof=1)\n"
        "p_value = float(np.mean(pp_sd >= obs_sd))\n"
        "print(f'observed sd={obs_sd:.3f}; posterior-predictive p-value for sd={p_value:.3f} "
        "(near 0.5 = good fit)')"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison",
        "With a single model there is no LOO/WAIC comparison yet, but we criticize the "
        "fit two ways: (1) confirm the posterior for $(\\mu,\\sigma)$ brackets the known "
        "truth, and (2) inspect the joint posterior for the classic mild correlation "
        "between $\\mu$ and $\\sigma$ when $N$ is modest.",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['mu', 'sigma'], kind='kde',\n"
        "             marginals=True, figsize=(6,5))\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Translate the joint posterior into reportable quantities: the estimated "
        "concentration with a credible interval, and the estimated measurement noise.",
    )
    nb.code(
        "mu_post = idata.posterior['mu'].values.ravel()\n"
        "sigma_post = idata.posterior['sigma'].values.ravel()\n"
        "mu_lo, mu_hi = np.percentile(mu_post, [3, 97])\n"
        "sig_lo, sig_hi = np.percentile(sigma_post, [3, 97])\n"
        "print(f'Concentration mu = {mu_post.mean():.3f} mg/mL, 94% CI [{mu_lo:.3f}, {mu_hi:.3f}]')\n"
        "print(f'Measurement noise sigma = {sigma_post.mean():.3f} mg/mL, 94% CI [{sig_lo:.3f}, {sig_hi:.3f}]')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The sample's concentration is about "
        "5.0 mg/mL (94% CI roughly [4.6, 5.4]) and the assay's replicate noise is about "
        "1.2 mg/mL. Reporting $\\sigma$ matters as much as $\\mu$: it tells the "
        "collaborator how reproducible a single future measurement will be.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """A deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 02 — BROKEN debugging exercise")
    nb.md(
        "# Project 02 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs** centred on the project's pitfall: "
        "scale priors. Run it, read the diagnostics, find each bug, and fix it. The "
        "clean reference is `notebook.ipynb`; the answer key is `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240602"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y = data['y']"
    )
    nb.md(
        "### Model — an improper flat scale prior, and a variance/SD confusion.")
    nb.code(
        "# BUG 1: improper 'flat' prior on sigma via a huge Uniform(0, 1e6).\n"
        "#         This is NOT uninformative; it puts vast mass on absurd spreads.\n"
        "# BUG 2: passing a VARIANCE where pm.Normal expects a standard deviation.\n"
        "with pm.Model() as model:\n"
        "    mu = pm.Normal('mu', mu=5.0, sigma=10.0)\n"
        "    sigma = pm.Uniform('sigma', lower=0.0, upper=1e6)   # BUG 1\n"
        "    variance = sigma ** 2\n"
        "    pm.Normal('y', mu=mu, sigma=variance, observed=y)   # BUG 2: variance, not sd\n"
        "    idata = pm.sample(draws=800, tune=800, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['mu', 'sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.md(
        "### Posterior predictive — BUG 3: reducing over the wrong axis for the spread.")
    nb.code(
        "with model:\n"
        "    idata.extend(pm.sample_posterior_predictive(idata, random_seed=RNG,\n"
        "                                                progressbar=False))\n"
        "pp = idata.posterior_predictive['y']\n"
        "# BUG 3: std over 'draw' collapses across posterior samples, not observations\n"
        "pp_sd = pp.std(dim='draw').values.ravel()\n"
        "print('observed sd =', y.std(ddof=1), 'predicted sd mean =', pp_sd.mean())"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
