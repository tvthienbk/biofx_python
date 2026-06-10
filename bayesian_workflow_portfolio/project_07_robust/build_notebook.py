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
    nb = NotebookBuilder(title="Project 07 — Robust Regression (Student-t)")

    nb.md(
        "# Project 07 — Robust Regression (Student-t vs Normal)",
        "**Scenario.** A calibration experiment relates a known input $x$ to a "
        "measured response $y$ that should be linear, $y=\\alpha+\\beta x+\\text{noise}$. "
        "Most points are clean, but a handful are **gross outliers** (a pipetting "
        "slip, a bubble, a mis-read plate). We want the calibration line without "
        "letting those few points drag it.",
        "**New skill.** *Heavy tails, with $\\nu$ as a parameter.* A Normal "
        "likelihood penalizes far points quadratically, so a single outlier can "
        "dominate the fit. The **Student-t** likelihood has heavy tails controlled "
        "by a degrees-of-freedom parameter $\\nu$; small $\\nu$ lets the model treat "
        "far points as tail events rather than evidence, making the fit robust. We "
        "fit **both** and let LOO confirm the Student-t wins.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Clean points follow $y=\\alpha+\\beta x+\\text{Normal}(0,\\sigma)$; a few are "
        "shifted by a large amount. The **known truth is the clean line** "
        "($\\alpha=1$, $\\beta=2$, $\\sigma=0.6$); a robust fit should recover it.",
        "**Assumptions made explicit:** (a) the underlying relationship is linear; "
        "(b) most measurements are clean, a minority are gross outliers; (c) outliers "
        "are *vertical* (in $y$), not high-leverage corruptions of $x$; (d) inputs "
        "$x$ are known. The outliers here are placed at low-leverage (central $x$) "
        "with balanced signs, so they contaminate scatter without engineering a "
        "slope artefact.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y, out = data['x'], data['y'], data['is_outlier']\n"
        "print(f\"n={data['n']}, outliers={int(out.sum())}, \"\n"
        "      f\"true alpha={data['truth']['alpha']}, beta={data['truth']['beta']}\")"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6, 4))\n"
        "ax.scatter(x[~out], y[~out], color='#4C72B0', label='clean', s=25)\n"
        "ax.scatter(x[out], y[out], color='#C44E52', label='outlier', s=45, marker='X')\n"
        "tx = np.linspace(x.min(), x.max(), 50)\n"
        "ax.plot(tx, data['truth']['alpha'] + data['truth']['beta']*tx, 'k--',\n"
        "        label='true clean line')\n"
        "ax.set(xlabel='x', ylabel='y', title='Calibration data with gross outliers')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Two likelihoods: Normal and Student-t",
        "Both share $\\mu_i=\\alpha+\\beta x_i$. They differ only in the noise model:",
        "$$\\text{Normal: } y_i\\sim N(\\mu_i,\\sigma),\\qquad"
        "\\text{Student-t: } y_i\\sim t_\\nu(\\mu_i,\\sigma).$$",
        "**Priors:** $\\alpha,\\beta\\sim N(0,5)$, $\\sigma\\sim\\text{HalfNormal}(5)$, "
        "and for the robust model $\\nu\\sim\\text{Gamma}(2,0.1)$. The $\\nu$ prior "
        "places real mass on small $\\nu$ (heavy tails) but also lets $\\nu$ grow if "
        "the data are clean — as $\\nu\\to\\infty$ the Student-t becomes Normal, so "
        "the robust model nests the non-robust one.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "m_norm = build_model(data, model='normal')\n"
        "m_t = build_model(data, model='studentt')\n"
        "m_t"
    )

    nb.md(
        "## Step 3 — Prior predictive check",
        "We confirm the Student-t prior implies calibration lines of plausible slope "
        "and noisy-but-not-absurd responses. (The heavy tail means occasional large "
        "$y$ are *expected* under the prior — exactly the flexibility we want.)",
    )
    nb.code(
        "with m_t:\n"
        "    prior = pm.sample_prior_predictive(draws=200, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.ravel()\n"
        "pp = pp[np.abs(pp) < np.percentile(np.abs(pp), 99)]\n"
        "fig, ax = plt.subplots(figsize=(6, 3.4))\n"
        "ax.hist(pp, bins=40, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='prior-implied y (99th-pct clipped)', ylabel='draws',\n"
        "       title='Student-t prior predictive — heavy-tailed but plausible')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS) for both models",
        "Settings: `draws=1000, tune=1000, chains=4`. The Student-t can be slightly "
        "stiffer when $\\nu$ is small, but with standardized $x$ default NUTS is "
        "fine. We keep both idatas for the comparison.",
    )
    nb.code(
        "idata_norm = fit(data, model='normal', draws=1000, tune=1000, chains=4, seed=101)\n"
        "idata_t = fit(data, model='studentt', draws=1000, tune=1000, chains=4, seed=101)\n"
        "print('normal divergences  :', int(idata_norm.sample_stats['diverging'].sum()))\n"
        "print('studentt divergences:', int(idata_t.sample_stats['diverging'].sum()))"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Both should converge ($\\hat R\\approx1$, healthy ESS). As with the Poisson "
        "in Project 06, the Normal model converges fine — it is *adequacy*, not "
        "convergence, that fails. The tell is in the estimates themselves.",
    )
    nb.code(
        "print('--- Normal ---')\n"
        "print(az.summary(idata_norm, var_names=['alpha', 'beta', 'sigma']))\n"
        "print('--- Student-t ---')\n"
        "print(az.summary(idata_t, var_names=['alpha', 'beta', 'sigma', 'nu']))"
    )
    nb.md(
        "**Read it now:** the Normal $\\sigma$ is hugely inflated (~3 vs the clean "
        "0.6 — it must 'explain' the outliers as ordinary noise), and as a direct "
        "consequence its slope/intercept become **far more uncertain** ($\\beta$ has "
        "an SD ~6× the Student-t's). Because these outliers are balanced and "
        "low-leverage by design, the Normal's slope *mean* is not strongly biased — "
        "the damage is to its precision and its noise estimate. The Student-t "
        "recovers $\\alpha\\approx1$, $\\beta\\approx2$ with tight intervals, a small "
        "scale, and a small $\\nu$ (heavy tails) — it has *identified* the outliers "
        "as tail events.",
    )

    nb.md(
        "## Step 6 — Posterior predictive & the fitted lines",
        "Overlay both fitted lines on the data. The Normal fit is far less certain "
        "(a much wider posterior band, driven by its inflated $\\sigma$); the "
        "Student-t line tracks the clean trend tightly. With these balanced, "
        "low-leverage outliers the Normal *mean* line is close to the truth too — "
        "the cost of ignoring robustness shows up as ballooning uncertainty and a "
        "5× inflated noise scale rather than a tilted mean line.",
    )
    nb.code(
        "tx = np.linspace(x.min(), x.max(), 50)\n"
        "def line(idata):\n"
        "    a = idata.posterior['alpha'].values.ravel()\n"
        "    b = idata.posterior['beta'].values.ravel()\n"
        "    yy = a[:, None] + b[:, None] * tx[None, :]\n"
        "    return yy.mean(0), np.percentile(yy, [3, 97], axis=0)\n"
        "fig, ax = plt.subplots(figsize=(6.5, 4.5))\n"
        "ax.scatter(x[~out], y[~out], color='#4C72B0', s=25, label='clean')\n"
        "ax.scatter(x[out], y[out], color='#C44E52', s=45, marker='X', label='outlier')\n"
        "mn, _ = line(idata_norm); mt, _ = line(idata_t)\n"
        "ax.plot(tx, mn, color='#C44E52', lw=2, label='Normal fit (noisy/uncertain)')\n"
        "ax.plot(tx, mt, color='#55A868', lw=2, label='Student-t fit (robust)')\n"
        "ax.plot(tx, data['truth']['alpha']+data['truth']['beta']*tx, 'k--', label='truth')\n"
        "ax.set(xlabel='x', ylabel='y', title='Normal destabilized by outliers; Student-t robust')\n"
        "ax.legend(); plt.tight_layout()"
    )
    nb.code(
        "az.plot_ppc(idata_t, num_pp_samples=100)\n"
        "plt.title('Student-t posterior predictive'); plt.tight_layout()"
    )

    nb.md(
        "## Step 7 — Model comparison (LOO) & recovery",
        "PSIS-LOO should prefer the Student-t decisively: down-weighting outliers "
        "yields better held-out prediction. We then confirm recovery of the clean "
        "line by the robust model.",
    )
    nb.code(
        "cmp = az.compare({'normal': idata_norm, 'studentt': idata_t}, ic='loo')\n"
        "print(cmp[['rank', 'elpd_loo', 'p_loo', 'elpd_diff', 'dse', 'weight']])"
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "line_truth = {k: data['truth'][k] for k in ('alpha', 'beta')}\n"
        "print('Student-t recovery of the clean line:')\n"
        "for res in check_recovery(idata_t, line_truth):\n"
        "    print(res)\n"
        "print('\\nNormal estimate of the slope (for contrast):')\n"
        "print(az.summary(idata_norm, var_names=['beta'])[['mean', 'sd']])"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Report the calibration slope and intercept with intervals, and state that "
        "the robust model was used so the few bad wells did not distort the result.",
    )
    nb.code(
        "b = idata_t.posterior['beta'].values.ravel()\n"
        "a = idata_t.posterior['alpha'].values.ravel()\n"
        "print(f'Robust slope  beta : {b.mean():.3f}  94% [{np.percentile(b,3):.3f}, {np.percentile(b,97):.3f}]')\n"
        "print(f'Robust intercept   : {a.mean():.3f}  94% [{np.percentile(a,3):.3f}, {np.percentile(a,97):.3f}]')\n"
        "nu = idata_t.posterior['nu'].values.ravel()\n"
        "print(f'Estimated nu (tail weight): {nu.mean():.2f} (small => heavy tails => outliers present)')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The calibration line is "
        "$y\\approx 1.0 + 2.0\\,x$, recovered cleanly despite ~10% gross outliers. A "
        "small $\\nu$ tells us the outliers are real and were correctly "
        "down-weighted. A naive least-squares / Normal fit would have reported a "
        "wildly inflated noise level and a much less certain line (here ~6× the "
        "slope SD). See `summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 07 — BROKEN debugging exercise")
    nb.md(
        "# Project 07 — BROKEN notebook (debugging exercise)",
        "This notebook fits a **Normal** likelihood to outlier-contaminated data and "
        "lets a single outlier dominate. Run it, see the dragged line and inflated "
        "sigma, find each bug, and fix it. Clean reference: `notebook.ipynb`; answer "
        "key: `BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y, out = data['x'], data['y'], data['is_outlier']"
    )
    nb.md(
        "### Model — BUG 1: a Normal likelihood lets gross outliers dominate.",
    )
    nb.code(
        "# BUG 1: Normal noise penalizes far points QUADRATICALLY, so a handful of\n"
        "#        outliers dominate the fit. The slope tilts and sigma inflates to\n"
        "#        'explain' the outliers as ordinary noise.\n"
        "with pm.Model() as model:\n"
        "    alpha = pm.Normal('alpha', 0.0, 5.0)\n"
        "    beta = pm.Normal('beta', 0.0, 5.0)\n"
        "    sigma = pm.HalfNormal('sigma', 5.0)\n"
        "    mu = alpha + beta * x\n"
        "    pm.Normal('y', mu=mu, sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=800, chains=2, random_seed=RNG,\n"
        "                      progressbar=False, idata_kwargs={'log_likelihood': True})"
    )
    nb.code(
        "# Converges fine -> the trap. Note the inflated sigma and the off-truth slope.\n"
        "print(az.summary(idata, var_names=['alpha', 'beta', 'sigma']))\n"
        "print('true beta =', data['truth']['beta'], 'true sigma =', data['truth']['sigma'])"
    )
    nb.md(
        "### A 'robust' attempt — BUG 2: nu is fixed FAR too large, so the Student-t "
        "is Normal in disguise and stays non-robust.",
    )
    nb.code(
        "# BUG 2: using a Student-t but PINNING nu=100. At nu=100 the t is\n"
        "#        indistinguishable from a Normal, so this 'robust' model is not\n"
        "#        robust at all. nu must be a free parameter (or set small) to let\n"
        "#        the heavy tail absorb the outliers.\n"
        "with pm.Model() as model_t:\n"
        "    alpha = pm.Normal('alpha', 0.0, 5.0)\n"
        "    beta = pm.Normal('beta', 0.0, 5.0)\n"
        "    sigma = pm.HalfNormal('sigma', 5.0)\n"
        "    mu = alpha + beta * x\n"
        "    pm.StudentT('y', nu=100.0, mu=mu, sigma=sigma, observed=y)  # BUG 2\n"
        "    idata_t = pm.sample(draws=800, tune=800, chains=2, random_seed=RNG,\n"
        "                        progressbar=False)\n"
        "print(az.summary(idata_t, var_names=['alpha', 'beta', 'sigma']))\n"
        "# Still dragged: nu=100 defeats the purpose. Fix: nu = pm.Gamma('nu', 2, 0.1)."
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
