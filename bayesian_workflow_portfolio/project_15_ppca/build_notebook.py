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
    nb = NotebookBuilder(title="Project 15 — Latent dimensions (probabilistic PCA)")

    nb.md(
        "# Project 15 — Latent dimensions (probabilistic PCA / factor model)",
        "**Scenario.** A panel of $D$ correlated measurements per sample (spectral "
        "channels, or omics features) is driven by a few underlying **latent factors**. "
        "We want to recover that low-dimensional structure.",
        "**New skill.** Latent *continuous* structure (factor scores $z_n$). "
        "**Key pitfall.** *Rotational / sign non-identifiability* — the loadings $W$ and "
        "scores $z$ are identified only up to an orthogonal rotation, so raw $W$ entries "
        "are meaningless. We interpret **rotation-invariant** quantities (the noise "
        "$\\sigma$, the reconstructed covariance $WW^\\top+\\sigma^2 I$) instead.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Probabilistic PCA: $z_n\\sim\\mathcal N(0,I_K)$, "
        "$x_n\\sim\\mathcal N(Wz_n+\\mu,\\sigma^2 I_D)$. **Assumptions:** (a) linear "
        "factor structure, (b) isotropic Gaussian noise (one shared $\\sigma$), (c) a "
        "fixed number of factors $K$ (here the true $K=2$; over-specifying $K$ is the "
        "pitfall). Truth: $D=6, K=2, N=150, \\sigma=0.4$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); X = data['X']; t = data['truth']\n"
        "print(f\"X shape = {X.shape}; true sigma={t['sigma']}, total_var(trace C)={t['total_var']:.2f}\")"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(5,4))\n"
        "im = ax.imshow(np.corrcoef(X.T), cmap='RdBu_r', vmin=-1, vmax=1)\n"
        "ax.set_title('Empirical correlation across the D dims\\n(structure = shared factors)')\n"
        "plt.colorbar(im, ax=ax, shrink=0.8); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (priors)",
        "$$W\\sim\\mathcal N(0,1)^{D\\times K},\\quad \\mu\\sim\\mathcal N(0,1)^D,\\quad "
        "\\sigma\\sim\\text{HalfNormal}(1),\\quad z\\sim\\mathcal N(0,1)^{N\\times K}.$$",
        "**The identifiability caveat up front.** Because $W\\to WR,\\ z\\to R^\\top z$ "
        "(orthogonal $R$) leaves the likelihood unchanged, the posterior over raw $W$ is "
        "**not** unimodal and its R-hat will be large. This is expected and not a bug. "
        "We will only ever interpret rotation-invariant functions of $W$.",
    )
    nb.code(
        "from model import build_model, fit, reconstructed_cov, add_identifiable\n"
        "model = build_model(data, K=2)\nmodel"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "Datasets implied by the prior should have a covariance scale comparable to "
        "(or larger than) what we observe — the $\\mathcal N(0,1)$ loadings give each "
        "dim unit-ish factor variance plus noise. We check the implied total variance "
        "is sensible (not collapsed to noise, not exploding).",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=200, random_seed=RNG)\n"
        "Xp = prior.prior_predictive['X'].values.reshape(-1, *X.shape)\n"
        "tv = [np.trace(np.cov(xx.T)) for xx in Xp[:50]]\n"
        "fig, ax = plt.subplots(figsize=(6,3.2))\n"
        "ax.hist(tv, bins=20, color='#55A868', edgecolor='white')\n"
        "ax.axvline(np.trace(np.cov(X.T)), color='red', label='observed total var')\n"
        "ax.legend(); ax.set(xlabel='prior-implied total variance', title='Prior predictive')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "`draws=500, tune=1000, chains=2, target_accept=0.9`. The $N\\times K$ latent "
        "scores make this a few-hundred-parameter model; it samples in ~30 s. Expect "
        "**clean** sampling for $\\sigma$ and the reconstruction, but **poor** mixing "
        "for raw $W$/$z$ — by design.",
    )
    nb.code("idata = fit(data, K=2, draws=500, tune=1000, chains=2, seed=15)\n"
            "add_identifiable(idata)")

    nb.md(
        "## Step 5 — Diagnostics: read the right R-hat",
        "Look at R-hat for **$\\sigma$** and **total_var** (should be ≈ 1.0–1.05), NOT "
        "for raw $W$ (which will be large — the rotation symmetry, not a convergence "
        "failure). This is the central teaching point: *which* parameters you check "
        "depends on what is identified.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['sigma','total_var']))\n"
        "print('--- raw W R-hat is large ON PURPOSE (rotation non-identifiability): ---')\n"
        "print(az.summary(idata, var_names=['W']).iloc[:4][['mean','r_hat','ess_bulk']])\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Compare the **observed covariance** to posterior-predictive covariances. The "
        "reconstruction $WW^\\top+\\sigma^2 I$ is rotation-invariant, so even though "
        "$W$ wanders, the implied covariance is stable and should match the data.",
    )
    nb.code(
        "C_hat = reconstructed_cov(idata)\n"
        "C_emp = np.cov(X.T)\n"
        "fig, axes = plt.subplots(1, 3, figsize=(11,3.2))\n"
        "for ax, M, ttl in zip(axes, [C_emp, C_hat, data['C_true']],\n"
        "                      ['empirical cov','reconstructed WWᵀ+σ²I','true C']):\n"
        "    im = ax.imshow(M, cmap='viridis'); ax.set_title(ttl); plt.colorbar(im, ax=ax, shrink=0.7)\n"
        "plt.tight_layout()\n"
        "print('reconstruction rel Frobenius error =',\n"
        "      round(np.linalg.norm(C_hat-data['C_true'])/np.linalg.norm(data['C_true']),3))"
    )

    nb.md(
        "## Step 7 — Model criticism: how many factors?",
        "Over-specifying $K$ is the analogue of the mixture's extra components: surplus "
        "factors are non-identified, hurt mixing, and do not improve fit. The robust "
        "check is the reconstruction error and (optionally) LOO across $K$. We compare "
        "the recovered $\\sigma$ / total_var to truth as the identifiable recovery test.",
    )
    nb.code(
        "for name, truth in [('sigma', t['sigma']), ('total_var', t['total_var'])]:\n"
        "    post = idata.posterior[name].values.ravel()\n"
        "    lo, hi = np.percentile(post, [3, 97])\n"
        "    print(f'{name:>10}: post mean={post.mean():.3f} 94%=[{lo:.3f},{hi:.3f}] truth={truth:.3f}')"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "For a collaborator: 'Two latent factors explain the bulk of the variance across "
        "the $D$ channels; the per-channel noise is $\\sigma\\approx0.4$. The factor "
        "*directions* are only defined up to rotation — interpret the reconstructed "
        "covariance and the dimensionality, not individual loading numbers.' See "
        "`summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Broken version: over-specified K + interpreting raw loadings. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 15 — BROKEN debugging exercise")
    nb.md(
        "# Project 15 — BROKEN notebook (over-specification & raw loadings)",
        "Seeded bugs centred on rotational non-identifiability. Run it, read the "
        "diagnostics, fix each bug. Clean reference: `notebook.ipynb`; answer key: "
        "`BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); X = data['X']; t = data['truth']"
    )
    nb.md(
        "### BUG 1 — over-specifying the number of factors (K=5 when truth is 2).",
        "Three surplus factors are non-identified: they soak up rotational freedom and "
        "wreck mixing without improving fit.",
    )
    nb.code(
        "N, D = X.shape\n"
        "K_WRONG = 5   # BUG 1: truth is K=2\n"
        "with pm.Model() as model:\n"
        "    W = pm.Normal('W', 0.0, 1.0, shape=(D, K_WRONG))\n"
        "    mu = pm.Normal('mu', 0.0, 1.0, shape=D)\n"
        "    sigma = pm.HalfNormal('sigma', 1.0)\n"
        "    z = pm.Normal('z', 0.0, 1.0, shape=(N, K_WRONG))\n"
        "    pm.Normal('X', mu=pm.math.dot(z, W.T)+mu, sigma=sigma, observed=X)\n"
        "    # BUG 2: too few tune steps for a poorly-identified geometry\n"
        "    idata = pm.sample(draws=400, tune=200, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.md(
        "### BUG 3 — interpreting a raw loading entry as if it were identified.",
        "Reporting `W[0,0]` as 'the loading of channel 0 on factor 0' is meaningless: "
        "it changes under any rotation of the latent space.",
    )
    nb.code(
        "# BUG 3: this number is not identified and its R-hat is huge.\n"
        "w00 = idata.posterior['W'].values.reshape(-1, D, K_WRONG)[:,0,0]\n"
        "print('reported W[0,0] =', w00.mean(), '+/-', w00.std())\n"
        "print(az.summary(idata, var_names=['W']).iloc[:5][['mean','r_hat','ess_bulk']])\n"
        "fig, ax = plt.subplots(figsize=(6,3.2))\n"
        "ax.hist(w00, bins=40, color='#C44E52'); ax.set_title('W[0,0]: multimodal, non-identified')\n"
        "plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
