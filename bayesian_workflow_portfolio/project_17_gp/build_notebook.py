"""Emit notebook.ipynb (clean GP workflow) and notebook_broken.ipynb.

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
    nb = NotebookBuilder(title="Project 17 — Nonparametric Curves (Gaussian Process)")

    nb.md(
        "# Project 17 — Nonparametric Curves with a Gaussian Process",
        "**Scenario.** A thermal-melt / dose-response experiment yields a smooth "
        "response $y$ at inputs $x$ (temperature or log-dose). We do **not** want to "
        "commit to a parametric shape (logistic, polynomial). A **Gaussian process** "
        "(GP) lets the data choose the curve while quantifying uncertainty.",
        "**New skill.** Kernels, hyperpriors, and *flexibility control*. "
        "**Key pitfall.** The length-scale $\\ell$ and the marginal variance $\\eta^2$ "
        "trade off against each other (and against the noise $\\sigma$). A vague "
        "length-scale prior makes the model non-identifiable and the sampler unhappy. "
        "The cure is an **informative length-scale prior**.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Each observation is $y_i = f(x_i) + \\varepsilon_i$ with $\\varepsilon_i \\sim "
        "\\mathcal{N}(0,\\sigma^2)$ and $f$ a smooth latent function. **Assumptions made "
        "explicit:** (a) $f$ is smooth (the ExpQuad kernel encodes infinite "
        "differentiability), (b) noise is homoscedastic Gaussian, (c) inputs are "
        "noise-free. We synthesize from a known curve and a known $\\sigma=0.18$ so we "
        "can check recovery of both the curve and the noise.",
    )
    nb.code(
        "from data.generate_data import generate, f_true\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']\n"
        "print(f\"n={data['n']}, true sigma={data['truth']['sigma']}\")\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.plot(x, data['f_true'], 'k--', label='true f(x)')\n"
        "ax.scatter(x, y, s=18, color='#4C72B0', label='noisy data')\n"
        "ax.set(xlabel='x (e.g. temperature)', ylabel='response', title='Data and latent curve')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (kernel + justified hyperpriors)",
        "$$f \\sim \\mathcal{GP}(0,\\; k),\\quad k(x,x') = \\eta^2\\exp\\!\\Big(-\\tfrac{(x-x')^2}{2\\ell^2}\\Big),"
        "\\quad y \\sim \\mathcal{N}(f(x),\\sigma).$$",
        "**Hyperpriors.** $\\ell \\sim \\text{InverseGamma}(6,12)$ is the load-bearing "
        "choice: its mass sits near $\\ell\\approx 2$ (about a fifth of the input range), "
        "with little mass below 1 or above 5. This **informative** prior prevents the "
        "$\\ell$/$\\eta$ trade-off. $\\eta \\sim \\text{HalfNormal}(2)$ controls amplitude; "
        "$\\sigma \\sim \\text{HalfNormal}(0.5)$ is the noise. We use `pm.gp.Marginal`, "
        "which integrates $f$ out analytically — cheap and stable.",
    )
    nb.code(
        "from model import build_model, fit, predict_curve\n"
        "model, gp = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We draw curves implied by the prior. We want functions that are wiggly on the "
        "scale of the data — not flat lines (length-scale too large) nor white noise "
        "(length-scale too small). The InverseGamma length-scale prior should yield "
        "smooth-but-non-trivial curves spanning a plausible response range.",
    )
    nb.code(
        "rng = np.random.default_rng(RNG)\n"
        "xx = np.linspace(0, 10, 80)\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "for _ in range(8):\n"
        "    ell = 1.0/rng.gamma(6.0, 1.0/12.0)\n"
        "    eta = abs(rng.normal(0, 2.0))\n"
        "    d2 = (xx[:,None]-xx[None,:])**2\n"
        "    K = eta**2*np.exp(-0.5*d2/ell**2) + 1e-8*np.eye(len(xx))\n"
        "    f = rng.multivariate_normal(np.zeros(len(xx)), K)\n"
        "    ax.plot(xx, f, lw=1)\n"
        "ax.set(xlabel='x', ylabel='f(x)', title='Prior predictive draws — smooth, plausible')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "We sample the **hyperposterior** over $(\\ell,\\eta,\\sigma)$ with NUTS. "
        "Settings: `draws=500, tune=1000, chains=2, target_accept=0.95`. GP "
        "hyperposteriors have mildly curved geometry, so a higher `target_accept` "
        "keeps divergences away. (Compute note: GP sampling is the heaviest in the "
        "portfolio; we keep $N$ small.)",
    )
    nb.code("idata = fit(data, draws=500, tune=1000, chains=2, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R \\approx 1.00$, healthy ESS, and **zero divergences**. With the "
        "informative length-scale prior the pair plot of $(\\ell,\\eta)$ should be a "
        "compact blob, not a diagonal ridge. A ridge would signal the trade-off "
        "pathology (see the broken notebook).",
    )
    nb.code(
        "print(az.summary(idata, var_names=['ell','eta','sigma']))\n"
        "n_div = int(idata.sample_stats['diverging'].sum())\n"
        "print(f'divergences: {n_div}')"
    )
    nb.code("az.plot_trace(idata, var_names=['ell','eta','sigma']); plt.tight_layout()")
    nb.code(
        "az.plot_pair(idata, var_names=['ell','eta'], kind='scatter',\n"
        "             scatter_kwargs={'alpha':0.3}); plt.tight_layout()"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks (the fitted curve)",
        "We reconstruct the latent function on a dense grid via the GP conditional mean "
        "$\\mu_* = K(x_*,x)\\,[K(x,x)+\\sigma^2 I]^{-1}y$ (evaluated in pure numpy over "
        "posterior hyperparameter draws — faster than `gp.predict` in a loop), and plot "
        "the posterior mean with a 94% credible band. A good fit: the band hugs the data, "
        "contains the **true** curve, and widens where data are sparse.",
    )
    nb.code(
        "pred = predict_curve(data, idata, n_pred=80, seed=3)\n"
        "fig, ax = plt.subplots(figsize=(6.5,3.8))\n"
        "ax.fill_between(pred['x_new'], pred['lower'], pred['upper'], color='#4C72B0',\n"
        "                alpha=0.25, label='94% band')\n"
        "ax.plot(pred['x_new'], pred['mean'], color='#4C72B0', label='GP mean')\n"
        "ax.plot(data['x'], data['f_true'], 'k--', label='true f(x)')\n"
        "ax.scatter(data['x'], data['y'], s=14, color='black', alpha=0.5, label='data')\n"
        "ax.set(xlabel='x', ylabel='response', title='GP fit vs truth')\n"
        "ax.legend(); plt.tight_layout()"
    )
    nb.code(
        "mae = float(np.mean(np.abs(predict_curve(data, idata, x_new=data['x'], seed=3)['mean']\n"
        "                          - data['f_true'])))\n"
        "print(f'curve recovery MAE at training inputs = {mae:.3f} (want < 0.25)')"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison",
        "We criticise the fit by (a) confirming $\\sigma$ recovers the truth and (b) "
        "checking residuals look like white noise of the inferred scale. A GP is a "
        "single flexible model; comparison against, say, a parametric logistic could be "
        "done with LOO, but the GP's value is precisely that it avoids that commitment.",
    )
    nb.code(
        "resid = data['y'] - predict_curve(data, idata, x_new=data['x'], seed=3)['mean']\n"
        "print(f\"residual sd = {resid.std():.3f}  vs  true sigma = {data['truth']['sigma']}\")\n"
        "post_sigma = idata.posterior['sigma'].values.ravel()\n"
        "print(f\"posterior sigma mean = {post_sigma.mean():.3f}, \"\n"
        "      f\"94% = [{np.percentile(post_sigma,3):.3f}, {np.percentile(post_sigma,97):.3f}]\")"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Turn the curve into something actionable: e.g. the input $x$ at which the "
        "response crosses a threshold (a melt midpoint / an EC50-like quantity), with "
        "uncertainty. Here we report the posterior over the input where the mean curve "
        "first exceeds 1.0.",
    )
    nb.code(
        "xx = np.linspace(0, 10, 200)\n"
        "p = predict_curve(data, idata, x_new=xx, seed=9)\n"
        "cross = xx[np.argmax(p['mean'] > 1.0)]\n"
        "print(f'Estimated input where response crosses 1.0: x = {cross:.2f}')\n"
        "print('Communicate: report this crossing point WITH the credible band width '\n"
        "      'there, not as a bare number.')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The response rises smoothly with a clear "
        "transition; the GP recovers the latent curve to within MAE < 0.25 and the noise "
        "scale within tolerance. The length-scale prior — not the kernel choice — is "
        "what made this stable; see `PRIOR_SENSITIVITY.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Seeded bugs: vague length-scale prior -> ell/eta non-identifiability."""
    nb = NotebookBuilder(title="Project 17 — BROKEN debugging exercise")
    nb.md(
        "# Project 17 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs** centred on the GP's signature "
        "pathology: a vague length-scale prior that makes $\\ell$ and $\\eta$ trade off. "
        "Run it, read the diagnostics (pair plot, divergences, $\\hat R$), find each bug, "
        "and fix it. Answer key: `BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']"
    )
    nb.md(
        "### Model — a vague length-scale prior and a starved sampler.",
        "Two seeded bugs hide here. Watch the $(\\ell,\\eta)$ pair plot.",
    )
    nb.code(
        "# BUG 1: a vague, heavy-tailed length-scale prior (HalfFlat) lets ell wander\n"
        "#         all the way out, re-opening the ell <-> eta trade-off.\n"
        "# BUG 2: low target_accept (0.8) on this curved geometry -> divergences.\n"
        "with pm.Model() as model:\n"
        "    ell = pm.HalfFlat('ell')\n"
        "    eta = pm.HalfNormal('eta', sigma=2.0)\n"
        "    sigma = pm.HalfNormal('sigma', sigma=0.5)\n"
        "    cov = eta**2 * pm.gp.cov.ExpQuad(input_dim=1, ls=ell)\n"
        "    gp = pm.gp.Marginal(cov_func=cov)\n"
        "    gp.marginal_likelihood('y_obs', X=x[:,None], y=y, sigma=sigma)\n"
        "    idata = pm.sample(draws=400, tune=400, chains=2, target_accept=0.8,\n"
        "                      random_seed=RNG, progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['ell','eta','sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.md(
        "### The smoking gun — BUG 3: the pair plot reveals the ridge.",
        "With a vague length-scale prior, $\\ell$ and $\\eta$ are correlated along a "
        "diagonal ridge (large $\\ell$ + large $\\eta$ explains the data as well as "
        "small $\\ell$ + small $\\eta$). The fix is the informative `InverseGamma` "
        "length-scale prior from `model.py`.",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['ell','eta'], kind='scatter',\n"
        "             scatter_kwargs={'alpha':0.3}); plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
