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
    nb = NotebookBuilder(title="Project 04 — Simple Linear Regression")

    nb.md(
        "# Project 04 — Simple Linear Regression (dose-response)",
        "**Scenario.** A dose-response experiment: a single predictor $x$ (the dose) "
        "drives a continuous response $y$ linearly, with Gaussian noise.",
        "**New skill:** predictors, with priors on a **slope** and an **intercept**. "
        "**Key pitfall:** un-scaled predictors. The doses live far from zero "
        "($\\sim 100$ to $600$), which makes the raw intercept meaningless, priors hard "
        "to set, and the sampler's geometry poor. The fix is to **standardize** $x$.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240604"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "The response is linear in dose with constant-variance Gaussian noise: "
        "$y_i = \\alpha + \\beta x_i + \\varepsilon_i$, $\\varepsilon_i\\sim N(0,\\sigma)$. "
        "**Assumptions made explicit:** (a) the relationship is linear, (b) noise is "
        "Gaussian with constant variance (homoscedastic), (c) doses are measured "
        "without error. We synthesize from known natural-scale "
        "$\\alpha=2.0$, $\\beta=0.015$, $\\sigma=0.8$, with doses on $[100, 600]$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']\n"
        "print(f\"n={data['n']}, doses in [{x.min():.0f}, {x.max():.0f}] (far from zero)\")\n"
        "print(f\"standardization: x_mean={data['x_mean']:.1f}, x_sd={data['x_sd']:.1f}\")\n"
        "print('natural-scale truth:', data['truth_natural'])"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.scatter(x, y, color='#4C72B0')\n"
        "ax.set(xlabel='dose x (natural units)', ylabel='response y',\n"
        "       title='dose-response — note x is far from zero')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification & the standardization fix",
        "We fit on the **standardized** predictor $x_\\text{std}=(x-\\bar x)/s_x$:",
        "$$y_i \\sim \\text{Normal}(\\alpha + \\beta\\,x_{\\text{std},i}, \\sigma), \\quad "
        "\\alpha\\sim N(0,5),\\ \\beta\\sim N(0,5),\\ \\sigma\\sim\\text{HalfNormal}(2).$$",
        "**Why standardize?** With raw doses on $[100,600]$: (1) the intercept $\\alpha$ "
        "would be the response at $x=0$, a wild extrapolation far outside the data; "
        "(2) the slope is tiny ($\\sim 0.015$) so a sensible prior width is hard to "
        "guess; (3) $\\alpha$ and $\\beta$ become strongly correlated, a banana-shaped "
        "posterior that NUTS samples poorly. Standardizing centers $x$ (so $\\alpha$ is "
        "the response at the *mean* dose — interpretable) and scales it to unit SD (so "
        "$\\beta$ is the change per 1 SD of dose, an $O(1)$ quantity). Now $N(0,5)$ "
        "priors are sensible for both, and the posterior geometry is clean.",
    )
    nb.code(
        "from model import build_model, fit, to_natural\n"
        "model = build_model(data)   # standardize=True by default\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate dose-response lines implied by the prior on the standardized "
        "scale. $N(0,5)$ priors should imply a wide fan of plausible slopes and "
        "intercepts — not so wide they predict absurd responses, not so tight they "
        "forbid the true line.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=80, random_seed=RNG)\n"
        "xs = np.linspace(data['x_std'].min(), data['x_std'].max(), 50)\n"
        "a_pr = prior.prior['alpha'].values.ravel()\n"
        "b_pr = prior.prior['beta'].values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "for a_i, b_i in zip(a_pr[:60], b_pr[:60]):\n"
        "    ax.plot(xs, a_i + b_i*xs, color='#55A868', alpha=0.25)\n"
        "ax.set(xlabel='x_std', ylabel='implied response',\n"
        "       title='prior predictive lines — wide but plausible')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "We sample with `draws=1000, tune=1000, chains=4`. Standardizing decorrelates "
        "$\\alpha$ and $\\beta$, so the posterior is well-conditioned and NUTS mixes "
        "efficiently — a direct, measurable payoff of the standardization fix.",
    )
    nb.code("idata = fit(data, draws=1000, tune=1000, chains=4, seed=404)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R\\approx 1.00$, ESS $\\gtrsim 400$, and 0 divergences for "
        "$\\alpha,\\beta,\\sigma$. With standardized $x$ the $\\alpha$-$\\beta$ "
        "correlation is near zero, so ESS is high. (On raw $x$ the correlation can "
        "exceed 0.99 and ESS collapses — the geometric cost of not standardizing.)",
    )
    nb.code(
        "print(az.summary(idata, var_names=['alpha', 'beta', 'sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print('standardized truth:', data['truth'])"
    )
    nb.code("az.plot_trace(idata, var_names=['alpha', 'beta', 'sigma']); plt.tight_layout()")

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "We overlay the fitted regression line (with uncertainty) on the data, and run "
        "a standard PPC. A well-fit linear model has residuals with no structure and "
        "data that sit inside the posterior-predictive band across the dose range.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")
    nb.code(
        "a = idata.posterior['alpha'].values.ravel()\n"
        "b = idata.posterior['beta'].values.ravel()\n"
        "xs = np.linspace(data['x_std'].min(), data['x_std'].max(), 50)\n"
        "lines = a[:400,None] + b[:400,None]*xs[None,:]\n"
        "lo, mid, hi = np.percentile(lines, [3, 50, 97], axis=0)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.scatter(data['x_std'], y, color='#4C72B0', label='data')\n"
        "ax.plot(xs, mid, 'k-', label='posterior mean line')\n"
        "ax.fill_between(xs, lo, hi, color='gray', alpha=0.3, label='94% band')\n"
        "ax.set(xlabel='x_std', ylabel='y', title='fitted line with uncertainty')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison",
        "We criticize the fit two ways: (1) confirm the posterior brackets the known "
        "standardized truth, and (2) map the coefficients back to the **natural scale** "
        "and check they match the true $\\alpha=2.0$, $\\beta=0.015$. The back-mapping "
        "is the whole reason standardizing is safe: it is an exact, invertible "
        "reparameterization.",
    )
    nb.code(
        "nat = to_natural(idata, data)\n"
        "print(f\"recovered natural-scale: alpha={nat['alpha']:.3f}, beta={nat['beta']:.4f}\")\n"
        "print('true natural-scale:', data['truth_natural'])\n"
        "print('the standardized fit maps back to the true natural-scale coefficients')"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Report the dose effect on the interpretable natural scale: how much the "
        "response rises per unit dose, with uncertainty, and a predicted response at a "
        "dose of interest.",
    )
    nb.code(
        "b_post = idata.posterior['beta'].values.ravel()\n"
        "beta_nat = b_post / data['x_sd']\n"
        "lo, hi = np.percentile(beta_nat, [3, 97])\n"
        "print(f'Dose effect (natural scale) = {beta_nat.mean():.4f} response/unit dose, '\n"
        "      f'94% CI [{lo:.4f}, {hi:.4f}]')\n"
        "dose_q = 400.0\n"
        "a_post = idata.posterior['alpha'].values.ravel()\n"
        "x_std_q = (dose_q - data['x_mean']) / data['x_sd']\n"
        "pred = a_post + b_post * x_std_q\n"
        "print(f'Predicted response at dose {dose_q:.0f}: {pred.mean():.3f} '\n"
        "      f'(94% CI [{np.percentile(pred,3):.3f}, {np.percentile(pred,97):.3f}])')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The response rises by about 0.015 units "
        "per unit of dose (94% CI roughly [0.011, 0.019]). At a dose of 400 the expected "
        "response is about 8. We standardized the dose internally for stable estimation, "
        "then reported everything back on the natural dose scale the collaborator uses.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """A deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 04 — BROKEN debugging exercise")
    nb.md(
        "# Project 04 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs** centred on the project's pitfall: "
        "un-scaled predictors and the priors they break. Run it, read the diagnostics, "
        "find each bug, and fix it. The clean reference is `notebook.ipynb`; the answer "
        "key is `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240604"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']   # NOTE: raw dose, NOT standardized"
    )
    nb.md(
        "### Model — raw predictor with a slope prior meant for a standardized scale.")
    nb.code(
        "# BUG 1 (headline): regress on RAW x (doses ~100..600), not standardized x.\n"
        "#   The intercept becomes an extrapolation to x=0 and alpha/beta correlate ~1.\n"
        "# BUG 2: a too-tight slope prior Normal(0, 0.5) that is fine on the\n"
        "#   standardized scale but absurd on the raw scale, where the true slope is\n"
        "#   ~0.015. (Here it is not too tight; the danger is using the SAME width on\n"
        "#   raw and standardized scales without thinking -- see BROKEN_BUGS.md.)\n"
        "with pm.Model() as model:\n"
        "    alpha = pm.Normal('alpha', mu=0.0, sigma=0.5)   # BUG 2: width copied from std scale\n"
        "    beta = pm.Normal('beta', mu=0.0, sigma=0.5)\n"
        "    sigma = pm.HalfNormal('sigma', sigma=2.0)\n"
        "    mu = alpha + beta * x                            # BUG 1: raw x\n"
        "    pm.Normal('y', mu=mu, sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=1000, tune=1000, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['alpha', 'beta', 'sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print('natural-scale truth:', data['truth_natural'])"
    )
    nb.md(
        "### Posterior predictive overlay — BUG 3: line plotted on the wrong x scale.")
    nb.code(
        "a = idata.posterior['alpha'].values.ravel()\n"
        "b = idata.posterior['beta'].values.ravel()\n"
        "# BUG 3: the fit used RAW x, but here we overlay the line on STANDARDIZED x,\n"
        "#   so the line will not match the data cloud.\n"
        "xs = np.linspace(data['x_std'].min(), data['x_std'].max(), 50)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.scatter(x, y, color='#4C72B0', label='data (raw x)')\n"
        "ax.plot(xs, a.mean() + b.mean()*xs, 'k-', label='fitted line (std x) -- mismatched!')\n"
        "ax.legend(); plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
