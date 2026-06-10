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
    nb = NotebookBuilder(title="Project 05 — Binary Outcomes (Logistic GLM)")

    nb.md(
        "# Project 05 — Binary Outcomes (Logistic Regression)",
        "**Scenario.** A ligand either binds (1) or does not bind (0) to a receptor "
        "in each of $N$ independent wells. The probability of binding rises with a "
        "continuous covariate $x$ (a standardized concentration / hydrophobicity "
        "score). We want the posterior over the dose–response relationship.",
        "**New skill.** *Link functions.* We never put a prior on a probability "
        "directly. We model a linear predictor $\\eta=\\alpha+\\beta x$ on the "
        "unconstrained log-odds scale and squash it through the logistic sigmoid. "
        "The crucial consequence: priors live on the log-odds scale, and we must "
        "read their implications back **on the probability scale**.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Each well is an independent Bernoulli trial whose success probability is a "
        "logistic function of $x$:",
        "$$\\operatorname{logit}(p_i)=\\alpha+\\beta x_i,\\qquad y_i\\sim\\text{Bernoulli}(p_i).$$",
        "**Assumptions made explicit:** (a) wells are independent; (b) the log-odds "
        "is *linear* in $x$; (c) $x$ is measured without error; (d) no omitted "
        "covariate confounds the relationship. We standardize $x$ so $\\alpha$ is the "
        "log-odds of binding at the mean covariate, which makes priors interpretable. "
        "Truth: $\\alpha=0.3$ ($p\\approx0.57$ at mean $x$), $\\beta=1.4$ "
        "(each $+1$ SD multiplies the odds by $e^{1.4}\\approx4.1$).",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']\n"
        "print(f\"n={data['n']} wells, binding rate={y.mean():.3f}, \"\n"
        "      f\"true alpha={data['truth']['alpha']}, beta={data['truth']['beta']}\")"
    )

    nb.md(
        "## Step 2 — Model specification (likelihood, link, justified priors)",
        "$$y_i\\sim\\text{Bernoulli}(p_i),\\quad p_i=\\operatorname{logit}^{-1}(\\alpha+\\beta x_i),"
        "\\quad \\alpha,\\beta\\sim\\text{Normal}(0,1.5).$$",
        "**Why Normal(0, 1.5) and not the 'non-informative' Normal(0, 10)?** This is "
        "the heart of the project. A prior on the *log-odds* coefficient maps to a "
        "prior on the *probability*. A wide Normal(0, 10) on $\\alpha$ says the "
        "binding probability at mean $x$ is almost certainly either $\\approx 0$ or "
        "$\\approx 1$ — a bimodal U-shape piled at the edges — which is an absurd "
        "belief to hold *before* seeing data. Normal(0, 1.5) spreads the implied "
        "probability sensibly across $(0,1)$. We verify this next.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data, prior_sd=1.5)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive check ON THE PROBABILITY SCALE",
        "We draw coefficients from each candidate prior, push them through the link, "
        "and look at the implied binding probability $p$ at the mean covariate "
        "($x=0$, so $p=\\operatorname{logit}^{-1}(\\alpha)$). A good prior spreads $p$ "
        "across the unit interval; a bad one piles it at the 0/1 edges.",
    )
    nb.code(
        "def sigmoid(z):\n"
        "    return 1.0 / (1.0 + np.exp(-z))\n"
        "rng = np.random.default_rng(RNG)\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)\n"
        "for ax, sd, ttl in [(axes[0], 1.5, 'Normal(0, 1.5) — sensible'),\n"
        "                    (axes[1], 10.0, 'Normal(0, 10) — pathological')]:\n"
        "    a = rng.normal(0, sd, size=20000)\n"
        "    p0 = sigmoid(a)\n"
        "    ax.hist(p0, bins=40, color='#4C72B0', edgecolor='white', density=True)\n"
        "    ax.set(xlabel='implied p at mean x', title=ttl)\n"
        "axes[0].set_ylabel('density')\n"
        "plt.tight_layout()"
    )
    nb.md(
        "Read it: **left** (Normal(0, 1.5)) spreads the implied probability broadly "
        "and unimodally around 0.5 — exactly the agnostic belief we want. **Right** "
        "(Normal(0, 10)) is a U pinned at 0 and 1: the 'vague' prior secretly "
        "asserts the assay is near-deterministic. Wide priors are *not* "
        "uninformative once a nonlinear link is involved.",
    )
    nb.code(
        "# Full prior predictive across all x (not just the mean), default prior.\n"
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=400, random_seed=RNG)\n"
        "pp_p = sigmoid(prior.prior['alpha'].values[..., None]\n"
        "               + prior.prior['beta'].values[..., None] * x[None, None, :])\n"
        "rate = pp_p.mean(axis=-1).ravel()\n"
        "fig, ax = plt.subplots(figsize=(6, 3.4))\n"
        "ax.hist(rate, bins=30, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='prior-implied overall binding rate', ylabel='count',\n"
        "       title='Normal(0,1.5) prior predictive — broad, no edge pile-up')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=1000, tune=1000, chains=4`. Logistic GLMs with "
        "standardized predictors have benign geometry, so default NUTS is plenty. "
        "Four chains give reliable split-$\\hat R$; we fix `random_seed`.",
    )
    nb.code("idata = fit(data, prior_sd=1.5, draws=1000, tune=1000, chains=4, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check **$\\hat R$** ($\\approx1.00$), **ESS** (bulk/tail $\\gtrsim 400$) and "
        "**divergences** (expect 0). The trace should be well-mixed fuzzy "
        "caterpillars. If $\\hat R$ stayed high we would suspect $\\alpha$–$\\beta$ "
        "correlation from un-centered $x$ (cured by standardizing, which we did).",
    )
    nb.code(
        "print(az.summary(idata, var_names=['alpha', 'beta']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_trace(idata, var_names=['alpha', 'beta']); plt.tight_layout()")

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Two views. First the ArviZ PPC of the 0/1 outcomes; then the **calibration** "
        "view that matters for a GLM — bin wells by predicted probability and check "
        "the observed binding fraction tracks the diagonal.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=200); plt.tight_layout()")
    nb.code(
        "p_hat = idata.posterior['p'].mean(('chain', 'draw')).values\n"
        "bins = np.linspace(0, 1, 7)\n"
        "idx = np.digitize(p_hat, bins) - 1\n"
        "xs, ys = [], []\n"
        "for b in range(len(bins) - 1):\n"
        "    m = idx == b\n"
        "    if m.sum() >= 3:\n"
        "        xs.append(p_hat[m].mean()); ys.append(y[m].mean())\n"
        "fig, ax = plt.subplots(figsize=(5, 5))\n"
        "ax.plot([0, 1], [0, 1], 'k--', label='perfect calibration')\n"
        "ax.plot(xs, ys, 'o-', color='#C44E52', label='binned observed')\n"
        "ax.set(xlabel='predicted p', ylabel='observed binding fraction',\n"
        "       title='Calibration of the logistic fit')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 7 — Model criticism & prior sensitivity",
        "We compare the recovered coefficients to the known truth, and re-fit under a "
        "tight, weak, and vague prior to confirm the posterior is robust *given "
        "data* — even though the vague prior was pathological a priori.",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "for res in check_recovery(idata, data['truth']):\n"
        "    print(res)"
    )
    nb.code(
        "rows = []\n"
        "for sd in (0.5, 1.5, 10.0):\n"
        "    ida = fit(data, prior_sd=sd, draws=500, tune=500, chains=2, seed=11)\n"
        "    s = az.summary(ida, var_names=['beta'], hdi_prob=0.94).loc['beta']\n"
        "    rows.append((sd, s['mean'], s['sd']))\n"
        "    print(f'prior_sd={sd:>4}: beta mean={s[\"mean\"]:.3f} sd={s[\"sd\"]:.3f}')"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Translate the posterior into the dose–response a collaborator needs: the "
        "probability that $\\beta>0$ (binding genuinely increases with $x$) and the "
        "covariate value at which binding crosses 50%.",
    )
    nb.code(
        "beta_post = idata.posterior['beta'].values.ravel()\n"
        "alpha_post = idata.posterior['alpha'].values.ravel()\n"
        "p_pos = float(np.mean(beta_post > 0))\n"
        "x50 = -alpha_post / beta_post\n"
        "lo, hi = np.percentile(x50, [3, 97])\n"
        "print(f'P(beta > 0 | data) = {p_pos:.3f}')\n"
        "print(f'x at p=0.5: median={np.median(x50):.2f} SD, 94% [{lo:.2f}, {hi:.2f}]')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** Binding probability increases strongly "
        "and almost-certainly with the covariate ($P(\\beta>0)\\approx1$). The "
        "half-maximal point sits near the mean covariate value. See "
        "`summary_onepager.md` for the decision framing.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 05 — BROKEN debugging exercise")
    nb.md(
        "# Project 05 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs** centred on link functions and prior "
        "widths. Run it, read the diagnostics, find each bug, and fix it. The clean "
        "reference is `notebook.ipynb`; the answer key is `BROKEN_BUGS.md` "
        "(don't peek first).",
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
        "### Model — two things are wrong: the prior, and the link.",
    )
    nb.code(
        "# BUG 1: absurdly wide coefficient priors. On the probability scale these\n"
        "#        imply p is almost surely 0 or 1 before any data are seen.\n"
        "# BUG 2: modeling the probability DIRECTLY (no logit link). 'p = alpha + beta*x'\n"
        "#        is not a probability: it leaves (0, 1) and Bernoulli(p) will error or\n"
        "#        the sampler will diverge wildly.\n"
        "with pm.Model() as model:\n"
        "    alpha = pm.Normal('alpha', 0.0, 10.0)\n"
        "    beta = pm.Normal('beta', 0.0, 10.0)\n"
        "    p = alpha + beta * x          # BUG 2: should be sigmoid(alpha + beta*x)\n"
        "    pm.Bernoulli('y', p=p, observed=y)\n"
        "    idata = pm.sample(draws=500, tune=500, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code("print(az.summary(idata, var_names=['alpha', 'beta']))")
    nb.md(
        "### Prior predictive — BUG 3: this 'check' never looks at the probability "
        "scale, so it hides the pathology of the wide prior.",
    )
    nb.code(
        "a = np.random.default_rng(RNG).normal(0, 10.0, size=5000)\n"
        "# BUG 3: histogramming the log-odds, not sigmoid(log-odds). Looks 'fine'\n"
        "#        (a nice bell curve) and conceals that p is pinned at 0/1.\n"
        "plt.hist(a, bins=30); plt.title('prior on alpha (WRONG scale)'); plt.tight_layout()"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
