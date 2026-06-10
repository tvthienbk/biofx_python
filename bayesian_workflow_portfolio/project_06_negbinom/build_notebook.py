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
    nb = NotebookBuilder(title="Project 06 — Overdispersed Counts (Negative-Binomial)")

    nb.md(
        "# Project 06 — Overdispersed Counts (Poisson vs Negative-Binomial)",
        "**Scenario.** RNA-seq-like read counts for a gene across $N$ samples. "
        "Expression depends on a covariate $x$ on the log scale. The counts are "
        "**overdispersed** — their variance far exceeds their mean — as sequencing "
        "data almost always are.",
        "**New skill.** *Overdispersion and count models.* A Poisson GLM forces "
        "$\\operatorname{Var}(y)=\\mu$. We fit **both** a Poisson and a "
        "Negative-Binomial GLM and let `az.compare` (LOO) show the NB wins. The "
        "Poisson's posterior-predictive check reveals its predictions are far too "
        "tight — the signature symptom of forced equidispersion.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Counts arise from a log-linear mean and a Negative-Binomial likelihood:",
        "$$\\log(\\mu_i)=\\beta_0+\\beta_1 x_i,\\qquad y_i\\sim\\text{NB}(\\mu_i,\\alpha),"
        "\\qquad \\operatorname{Var}(y_i)=\\mu_i+\\mu_i^2/\\alpha.$$",
        "**Assumptions made explicit:** (a) samples independent; (b) the *log-mean* "
        "is linear in $x$; (c) overdispersion is constant (single $\\alpha$); (d) no "
        "excess zeros beyond what the NB implies. Truth: $\\beta_0=2.2$, "
        "$\\beta_1=0.8$, $\\alpha=2.0$ (strong overdispersion).",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']\n"
        "print(f\"n={data['n']}, mean={y.mean():.2f}, var={y.var():.2f}, \"\n"
        "      f\"var/mean={y.var()/y.mean():.2f} (>>1 => overdispersed)\")"
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6, 3.4))\n"
        "ax.hist(y, bins=30, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='count y', ylabel='samples', title='Observed counts — heavy right tail')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Two models: Poisson and Negative-Binomial",
        "Both share $\\log(\\mu_i)=\\beta_0+\\beta_1 x_i$ (log link keeps $\\mu>0$). "
        "The Poisson stops there; the NB adds a dispersion parameter $\\alpha$.",
        "**Priors (weakly informative on the log scale):** $\\beta_0\\sim N(0,2)$, "
        "$\\beta_1\\sim N(0,1)$, $\\alpha\\sim\\text{Gamma}(2,0.1)$ (mean 20, "
        "heavy-tailed so it supports both mild and strong dispersion). As "
        "$\\alpha\\to\\infty$ the NB collapses to Poisson, so NB strictly nests it.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "m_pois = build_model(data, model='poisson')\n"
        "m_nb = build_model(data, model='nb')\n"
        "m_nb"
    )

    nb.md(
        "## Step 3 — Prior predictive check",
        "We simulate counts implied by the NB prior and confirm they span a "
        "plausible, heavy-tailed range rather than collapsing to 0 or exploding. "
        "Count priors are easy to set absurdly: a wide prior on $\\beta_0$ implies "
        "astronomically large means after exponentiation.",
    )
    nb.code(
        "with m_nb:\n"
        "    prior = pm.sample_prior_predictive(draws=300, random_seed=RNG)\n"
        "pp = prior.prior_predictive['y'].values.ravel()\n"
        "pp = pp[pp < np.percentile(pp, 99)]  # clip the extreme prior tail for the plot\n"
        "fig, ax = plt.subplots(figsize=(6, 3.4))\n"
        "ax.hist(pp, bins=40, color='#4C72B0', edgecolor='white')\n"
        "ax.set(xlabel='prior-implied count', ylabel='draws',\n"
        "       title='NB prior predictive (99th-pct clipped) — broad, heavy-tailed')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS) for both models",
        "Settings: `draws=1000, tune=1000, chains=4`. Log-linear count GLMs with "
        "standardized $x$ sample easily. We fit both models and keep both idatas.",
    )
    nb.code(
        "idata_pois = fit(data, model='poisson', draws=1000, tune=1000, chains=4, seed=101)\n"
        "idata_nb = fit(data, model='nb', draws=1000, tune=1000, chains=4, seed=101)\n"
        "print('poisson divergences:', int(idata_pois.sample_stats['diverging'].sum()))\n"
        "print('nb divergences     :', int(idata_nb.sample_stats['diverging'].sum()))"
    )

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Both models should show $\\hat R\\approx1.00$, healthy ESS, and 0 "
        "divergences. (A failure to converge is *not* how the Poisson reveals its "
        "inadequacy — it converges fine to a wrong-shaped predictive; the PPC is "
        "what exposes it.)",
    )
    nb.code(
        "print('--- Poisson ---')\n"
        "print(az.summary(idata_pois, var_names=['beta0', 'beta1']))\n"
        "print('--- Negative-Binomial ---')\n"
        "print(az.summary(idata_nb, var_names=['beta0', 'beta1', 'alpha']))"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks (where Poisson fails)",
        "Overlay each model's posterior-predictive count distribution on the data. "
        "The Poisson predictions are **far too narrow** — it cannot reproduce the "
        "observed heavy tail because it is locked to $\\operatorname{Var}=\\mu$. The "
        "NB, with its free dispersion, covers the spread.",
    )
    nb.code(
        "fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))\n"
        "az.plot_ppc(idata_pois, num_pp_samples=100, ax=axes[0])\n"
        "axes[0].set_title('Poisson PPC — predictions too tight')\n"
        "az.plot_ppc(idata_nb, num_pp_samples=100, ax=axes[1])\n"
        "axes[1].set_title('Negative-Binomial PPC — covers the spread')\n"
        "plt.tight_layout()"
    )
    nb.code(
        "# Quantify: compare observed variance to the posterior-predictive variance.\n"
        "for name, idata in [('Poisson', idata_pois), ('NB', idata_nb)]:\n"
        "    ppy = idata.posterior_predictive['y'].values.reshape(-1, len(y))\n"
        "    pred_var = ppy.var(axis=1).mean()\n"
        "    print(f'{name:>8}: observed var={y.var():.1f}, predicted var~{pred_var:.1f}')"
    )

    nb.md(
        "## Step 7 — Model comparison with LOO (`az.compare`)",
        "We rank the two models by expected log predictive density via "
        "PSIS-LOO. The NB should win decisively, with the difference in `elpd_loo` "
        "many standard errors beyond zero. This is the formal version of the visual "
        "PPC story: ignoring overdispersion costs real predictive accuracy.",
    )
    nb.code(
        "cmp = az.compare({'poisson': idata_pois, 'negbinom': idata_nb}, ic='loo')\n"
        "print(cmp[['rank', 'elpd_loo', 'p_loo', 'elpd_diff', 'dse', 'weight']])"
    )
    nb.code(
        "az.plot_compare(cmp); plt.tight_layout()"
    )
    nb.md(
        "**Read it:** `negbinom` is rank 0; `elpd_diff` for the Poisson is large and "
        "many `dse` away from 0, so the preference is decisive. `p_loo` (effective "
        "parameters) for the Poisson may also be inflated — a classic symptom of "
        "misspecification under LOO.",
    )

    nb.md(
        "## Step 8 — Decision, recovery & communication",
        "Confirm the NB recovers the known truth, then state the effect a "
        "collaborator cares about: the fold-change in expression per unit $x$.",
    )
    nb.code(
        "from shared.bayes_utils import check_recovery\n"
        "for res in check_recovery(idata_nb, data['truth']):\n"
        "    print(res)"
    )
    nb.code(
        "b1 = idata_nb.posterior['beta1'].values.ravel()\n"
        "fold = np.exp(b1)\n"
        "lo, hi = np.percentile(fold, [3, 97])\n"
        "print(f'fold-change per +1 SD of x: median={np.median(fold):.2f}, '\n"
        "      f'94% [{lo:.2f}, {hi:.2f}]')\n"
        "print(f'P(beta1 > 0 | data) = {float(np.mean(b1 > 0)):.3f}')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** Expression rises ~2.2-fold per "
        "standard-deviation increase in $x$, and the effect is essentially certain. "
        "Crucially we used the **Negative-Binomial**: a Poisson would have reported "
        "a falsely precise effect and badly underestimated count variability. See "
        "`summary_onepager.md`.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 06 — BROKEN debugging exercise")
    nb.md(
        "# Project 06 — BROKEN notebook (debugging exercise)",
        "This notebook forces a **Poisson** model on overdispersed data and then "
        "fails to notice. Run it, read the posterior-predictive check, find each "
        "bug, and fix it. Clean reference: `notebook.ipynb`; answer key: "
        "`BROKEN_BUGS.md` (don't peek first).",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "x, y = data['x'], data['y']\n"
        "print('var/mean =', y.var()/y.mean(), '(>>1 => overdispersed!)')"
    )
    nb.md(
        "### Model — BUG 1: a Poisson likelihood on data we just saw are "
        "overdispersed.",
    )
    nb.code(
        "# BUG 1: Poisson forces Var(y)=mu. The data have var/mean ~ 14, so this is\n"
        "#        the wrong family. The fit will CONVERGE (don't be fooled) but its\n"
        "#        predictions will be far too tight.\n"
        "with pm.Model() as model:\n"
        "    beta0 = pm.Normal('beta0', 0.0, 2.0)\n"
        "    beta1 = pm.Normal('beta1', 0.0, 1.0)\n"
        "    mu = pm.math.exp(beta0 + beta1 * x)\n"
        "    pm.Poisson('y', mu=mu, observed=y)\n"
        "    idata = pm.sample(draws=800, tune=800, chains=2, random_seed=RNG,\n"
        "                      progressbar=False, idata_kwargs={'log_likelihood': True})\n"
        "    idata.extend(pm.sample_posterior_predictive(idata, random_seed=RNG,\n"
        "                                                progressbar=False))"
    )
    nb.code(
        "# Converges fine -> easy to declare victory here. That is the trap.\n"
        "print(az.summary(idata, var_names=['beta0', 'beta1']))"
    )
    nb.md(
        "### Criticism — BUG 2: 'checking' only R-hat, never a PPC. The "
        "misspecification is invisible to convergence diagnostics.",
    )
    nb.code(
        "# BUG 2: stopping at R-hat. Convergence != adequacy. A correct workflow runs\n"
        "#        a posterior-predictive check; here is the check that WOULD reveal the\n"
        "#        problem (predicted variance << observed variance). Uncomment-style fix:\n"
        "ppy = idata.posterior_predictive['y'].values.reshape(-1, len(y))\n"
        "print('observed var =', round(float(y.var()), 1),\n"
        "      'predicted var ~', round(float(ppy.var(axis=1).mean()), 1))\n"
        "# The two numbers are wildly different -> the Poisson is under-dispersed.\n"
        "# BUG 3 (implicit): there is no second model to compare against. Fit a\n"
        "# NegativeBinomial and run az.compare to see it win."
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
