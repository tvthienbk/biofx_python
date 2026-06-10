"""Emit notebook.ipynb (clean) and notebook_broken.ipynb (debug exercise).

Run:  python3 build_notebook.py

Clean: fits BOTH the naive regression (attenuated slope) and the errors-in-variables
model (latent x_true) and shows the EIV model recovers the true slope. Broken: the
naive regression presented as if correct (attenuation bug, seeded), plus a
latent-variable indexing bug; then the fix.
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
    nb = NotebookBuilder(title="Project 12 — Errors-in-Variables")

    nb.md(
        "# Project 12 — Errors-in-Variables (Measurement-Error Model)",
        "**Scenario.** We want the relationship $y = \\alpha + \\beta x^*$, but the "
        "instrument adds noise to **both** variables. We never see the true "
        "predictor $x^*$; we see $x_\\text{obs} = x^* + \\text{noise}$ and a noisy "
        "$y$. Regressing $y$ on $x_\\text{obs}$ — the obvious thing — **attenuates** "
        "the slope toward 0.",
        "**New skill:** model noise in a *predictor* via a **latent true predictor** "
        "$x^*$. **Key pitfall:** attenuation bias if predictor noise is ignored.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "$$x^*_i \\sim \\text{Normal}(\\mu_x, s_x), \\quad "
        "x_{\\text{obs},i} = x^*_i + \\text{Normal}(0, \\tau_x), \\quad "
        "y_i = \\alpha + \\beta x^*_i + \\text{Normal}(0, \\sigma_y).$$",
        "**Assumptions:** (a) the structural relationship is linear in the *true* "
        "$x^*$, (b) predictor noise is additive Gaussian with known SD $\\tau_x$ "
        "(from calibration), (c) the response noise is independent of the predictor "
        "noise. Truth: $\\alpha=1,\\ \\beta=2,\\ \\sigma_y=0.5,\\ \\tau_x=0.6$. The "
        "**attenuation factor** $s_x^2/(s_x^2+\\tau_x^2)\\approx0.74$ predicts how far "
        "the naive slope is pulled toward 0.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x_obs, y = data['x_obs'], data['y']\n"
        "print(f\"n={data['n']}, true beta={data['truth']['beta']}, \"\n"
        "      f\"tau_x={data['tau_x']}, attenuation factor={data['attenuation_factor']:.2f}\")\n"
        "b_ols = np.cov(x_obs, y)[0,1]/np.var(x_obs)\n"
        "print(f'naive OLS slope (y on x_obs) = {b_ols:.3f}  (attenuated!)')"
    )

    nb.md(
        "## Step 2 — Two models",
        "**Naive:** $y_i \\sim \\text{Normal}(\\alpha + \\beta x_{\\text{obs},i}, "
        "\\sigma_y)$ — regress on the noisy predictor (biased).",
        "**Errors-in-variables (EIV):** treat $x^*$ as a **latent** variable with a "
        "population prior, add a measurement model $x_\\text{obs} \\sim "
        "\\text{Normal}(x^*, \\tau_x)$, and write the structural model in terms of "
        "$x^*$. With $\\tau_x$ known, the slope is de-attenuated.",
        "Priors: $\\alpha,\\beta \\sim \\text{Normal}(0,5)$ on the regression "
        "coefficients; $\\mu_x \\sim \\text{Normal}(0,5)$, $s_x \\sim "
        "\\text{HalfNormal}(5)$ for the latent-predictor population.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "build_model(data, model='eiv')"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We confirm the priors imply plausible $y$ ranges before fitting.",
    )
    nb.code(
        "with build_model(data, model='eiv') as m:\n"
        "    prior = pm.sample_prior_predictive(draws=300, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(pp, bins=40, color='#55A868', edgecolor='white', density=True)\n"
        "ax.axvline(y.mean(), color='red', lw=1.5, label='observed mean y')\n"
        "ax.set(xlabel='y implied by prior', ylabel='density', title='Prior predictive')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (both models)",
        "We fit the naive model and the EIV model. The EIV model has 100s of latent "
        "$x^*_i$, so we use `target_accept=0.95` and ample tuning.",
    )
    nb.code(
        "idata_naive = fit(data, model='naive', draws=800, tune=1000, chains=4, seed=101)\n"
        "idata_eiv = fit(data, model='eiv', draws=800, tune=1500, chains=4,\n"
        "                target_accept=0.95, seed=101)"
    )

    nb.md(
        "## Step 5 — Diagnostics",
        "Check $\\hat R$, ESS, and divergences for both. The EIV model is harder to "
        "sample (a high-dimensional latent vector); `sigma_y` is the most weakly "
        "identified parameter (it trades off against the predictor-noise scale), so "
        "expect its ESS to be the lowest — the **slope** $\\beta$, our target, is "
        "well-behaved.",
    )
    nb.code(
        "print('NAIVE'); print(az.summary(idata_naive, var_names=['alpha','beta','sigma_y']))\n"
        "print('\\nEIV'); print(az.summary(idata_eiv, var_names=['alpha','beta','sigma_y']))\n"
        "print('EIV divergences:', int(idata_eiv.sample_stats['diverging'].sum()))"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Both models can fit the *observed* $y$ adequately — a reminder that a good "
        "PPC on $y$ does **not** vindicate the naive model's *slope*. The bias is in "
        "the coefficient, not necessarily the fit to $y$.",
    )
    nb.code("az.plot_ppc(idata_eiv, num_pp_samples=100); plt.tight_layout()")

    nb.md(
        "## Step 7 — The headline: naive vs EIV slope",
        "Overlay the two posterior slopes against the true $\\beta=2$. The naive "
        "posterior sits near the attenuated value ($\\approx \\beta \\times 0.74$); "
        "the EIV posterior covers the truth.",
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6.5,4))\n"
        "az.plot_dist(idata_naive.posterior['beta'].values.ravel(), ax=ax,\n"
        "             color='#C44E52', label='naive (attenuated)')\n"
        "az.plot_dist(idata_eiv.posterior['beta'].values.ravel(), ax=ax,\n"
        "             color='#4C72B0', label='errors-in-variables')\n"
        "ax.axvline(data['truth']['beta'], color='k', ls='--', label='true beta=2')\n"
        "ax.set(xlabel='slope beta', ylabel='density', title='Attenuation and its correction')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Recover $(\\alpha,\\beta)$ of the EIV model and verify against truth.",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "truths = {k: data['truth'][k] for k in ['alpha','beta']}\n"
        "for res in check_recovery(idata_eiv, truths):\n"
        "    print(res)"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The true effect of $x$ on $y$ is "
        "$\\beta\\approx2$, but the naive regression reports only ~1.5 because the "
        "predictor is measured with noise. Quoting the naive slope would understate "
        "the effect by ~25%. The fix requires knowing (calibrating) the predictor's "
        "measurement-error SD $\\tau_x$. See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Debug exercise: naive regression presented as correct + a latent indexing bug."""
    nb = NotebookBuilder(title="Project 12 — BROKEN debugging exercise")
    nb.md(
        "# Project 12 — BROKEN notebook (debugging exercise)",
        "This notebook reports a slope that is **biased** and contains a "
        "latent-variable **indexing bug** in an attempted EIV fix. Run it, compare "
        "the slope to the known truth, find both bugs, and fix them. Answer key: "
        "`BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x_obs, y, n = data['x_obs'], data['y'], data['n']\n"
        "print('true beta =', data['truth']['beta'])"
    )

    nb.md(
        "### BUG 1 — naive regression on the noisy predictor (attenuation).",
        "This regresses $y$ directly on $x_\\text{obs}$, ignoring that the predictor "
        "is measured with noise. The slope will be biased toward 0, but nothing in "
        "this cell warns you.",
    )
    nb.code(
        "with pm.Model() as naive:\n"
        "    alpha = pm.Normal('alpha', 0, 5)\n"
        "    beta = pm.Normal('beta', 0, 5)\n"
        "    sigma_y = pm.HalfNormal('sigma_y', 2)\n"
        "    pm.Normal('y', mu=alpha + beta * x_obs, sigma=sigma_y, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=1000, chains=4, random_seed=RNG,\n"
        "                      progressbar=False)\n"
        "print(az.summary(idata, var_names=['beta']))\n"
        "print('Reported slope is ~1.5 but the TRUTH is 2.0 -> attenuation bias.')"
    )

    nb.md(
        "### BUG 2 — an EIV attempt with a latent-variable indexing bug.",
        "Someone tried to fix it with a latent $x^*$, but mis-indexed the latent "
        "vector against the observations, so the measurement and structural models "
        "no longer line up row-for-row. (Run and read the error / nonsensical fit.)",
    )
    nb.code(
        "tau_x = data['tau_x']\n"
        "with pm.Model(coords={'obs': np.arange(n)}) as eiv_bug:\n"
        "    alpha = pm.Normal('alpha', 0, 5)\n"
        "    beta = pm.Normal('beta', 0, 5)\n"
        "    sigma_y = pm.HalfNormal('sigma_y', 2)\n"
        "    mu_x = pm.Normal('mu_x', 0, 5)\n"
        "    sd_x = pm.HalfNormal('sd_x', 5)\n"
        "    x_true = pm.Normal('x_true', mu_x, sd_x, dims='obs')\n"
        "    pm.Normal('x_obs', mu=x_true, sigma=tau_x, observed=x_obs, dims='obs')\n"
        "    # BUG 2: reversing x_true breaks the row-for-row alignment with y\n"
        "    pm.Normal('y', mu=alpha + beta * x_true[::-1], sigma=sigma_y, observed=y)\n"
        "    idata_bug = pm.sample(draws=600, tune=1000, chains=2, target_accept=0.95,\n"
        "                          random_seed=RNG, progressbar=False)\n"
        "print(az.summary(idata_bug, var_names=['beta']))\n"
        "print('Mis-indexed latent -> slope collapses toward 0 (relationship destroyed).')"
    )

    nb.md(
        "### The fix — correct EIV with aligned latent x_true.",
        "Use the latent $x^*$ **in the same order** as the observations (no "
        "reversal). With $\\tau_x$ known, the slope is recovered near 2. See "
        "`model.py` (`model='eiv'`).",
    )
    nb.code(
        "from model import fit\n"
        "idata_fixed = fit(data, model='eiv', draws=800, tune=1500, chains=4,\n"
        "                  target_accept=0.95, seed=RNG)\n"
        "print(az.summary(idata_fixed, var_names=['alpha','beta']))\n"
        "print('true beta =', data['truth']['beta'])"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
