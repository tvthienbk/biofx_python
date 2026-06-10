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
    nb = NotebookBuilder(title="Project 03 — Estimating a Rate")

    nb.md(
        "# Project 03 — Estimating a Rate (Poisson with exposure offset)",
        "**Scenario.** Genomics counts per unit exposure: each sample $i$ has an "
        "exposure $e_i$ (e.g. sequencing depth in kb) and an observed count $y_i$ of "
        "events occurring at a common rate $\\lambda$ per unit exposure.",
        "**New skill:** priors for a positive rate via a **log link** "
        "($\\lambda = e^{\\text{log\\_rate}}$). **Key pitfall:** ignoring the "
        "exposure/offset. Because exposures *vary*, the correct model is "
        "$y_i \\sim \\text{Poisson}(e_i\\,\\lambda)$ — forgetting $e_i$ biases the rate.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240603"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Each sample's count is Poisson with mean $e_i\\,\\lambda$: the rate per unit "
        "exposure is shared, but the exposure differs by sample. **Assumptions made "
        "explicit:** (a) events independent (Poisson), (b) a single common rate "
        "$\\lambda$ (no overdispersion / no covariates), (c) exposures $e_i$ known "
        "exactly. We synthesize from a known $\\text{log\\_rate}=-1.2$ "
        "($\\lambda\\approx 0.30$) with exposures spread over $[5, 40]$ so the offset "
        "genuinely matters.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, e = data['y'], data['exposure']\n"
        "print(f\"n={data['n']}, total events={y.sum()}, total exposure={e.sum():.1f}\")\n"
        "print(f\"naive mean count (IGNORES exposure) = {y.sum()/data['n']:.3f}\")\n"
        "print(f\"exposure-adjusted rate = {y.sum()/e.sum():.3f}  (true rate "
        "= {np.exp(data['truth']['log_rate']):.3f})\")"
    )
    nb.md(
        "Notice the two summaries already disagree: the *naive* mean count per sample "
        "(~7) is nothing like the true rate (~0.30). The difference is entirely the "
        "exposure. A plot of count vs exposure shows the tell-tale upward trend: "
        "samples with more exposure rack up more events at the *same* underlying rate.",
    )
    nb.code(
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.scatter(e, y, color='#4C72B0')\n"
        "ax.set(xlabel='exposure e_i', ylabel='count y_i',\n"
        "       title='counts rise with exposure at a fixed underlying rate')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (likelihood + justified priors)",
        "$$y_i \\sim \\text{Poisson}(e_i\\,\\lambda), \\qquad \\lambda = e^{r}, "
        "\\qquad r \\equiv \\text{log\\_rate} \\sim \\text{Normal}(0, 2).$$",
        "**Why a log link?** A rate must be positive. Putting a Normal prior on "
        "$\\text{log\\_rate}$ makes $\\lambda=e^{r}$ automatically positive and the "
        "prior symmetric on the log (multiplicative) scale — the natural scale for a "
        "rate. $\\text{Normal}(0,2)$ is weakly-informative: it covers roughly "
        "$e^{-4}$ to $e^{4}$, i.e. rates from $\\sim 0.02$ to $\\sim 55$. "
        "**The offset.** The expected count is $e_i\\,\\lambda$; equivalently "
        "$\\log E[y_i] = \\log e_i + r$, so $\\log e_i$ enters as a fixed **offset**.",
    )
    nb.code(
        "from model import build_model, fit\n"
        "model = build_model(data)   # use_offset=True by default\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate counts implied by the prior (with the real exposures). "
        "$\\text{Normal}(0,2)$ on log_rate should imply a wide but not insane range of "
        "total counts. A prior that placed all its mass on huge rates would imply "
        "millions of events; one too tight would forbid plausible rates.",
    )
    nb.code(
        "with model:\n"
        "    prior = pm.sample_prior_predictive(draws=500, random_seed=RNG)\n"
        "obs_dim = [d for d in prior.prior_predictive['y'].dims if d not in ('chain','draw')][0]\n"
        "prior_tot = prior.prior_predictive['y'].sum(dim=obs_dim).values.ravel()\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "ax.hist(np.log10(prior_tot + 1), bins=30, color='#55A868', edgecolor='white')\n"
        "ax.set(xlabel='log10(total events + 1) implied by prior', ylabel='count',\n"
        "       title='prior predictive — wide but finite')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "We sample with `draws=1000, tune=1000, chains=4`. The single parameter "
        "log_rate lives on an unconstrained scale (thanks to the log link), so the "
        "geometry is benign and NUTS mixes well.",
    )
    nb.code("idata = fit(data, draws=1000, tune=1000, chains=4, seed=303)")

    nb.md(
        "## Step 5 — Computational diagnostics",
        "Check $\\hat R\\approx 1.00$, bulk/tail ESS $\\gtrsim 400$, and 0 divergences. "
        "The log link gives a smooth, unconstrained posterior, so a clean report is "
        "expected.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['log_rate']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))\n"
        "print('true log_rate =', data['truth']['log_rate'])"
    )
    nb.code("az.plot_trace(idata, var_names=['log_rate']); plt.tight_layout()")

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "We compare observed counts to posterior-predictive replicates. Because the "
        "model uses the exposure offset, the predicted counts should track the observed "
        "counts *across the full exposure range* — not just on average.",
    )
    nb.code("az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()")
    nb.code(
        "pp = idata.posterior_predictive['y']\n"
        "obs_dim = [d for d in pp.dims if d not in ('chain','draw')][0]\n"
        "pp_tot = pp.sum(dim=obs_dim).values.ravel()\n"
        "p_value = float(np.mean(pp_tot >= y.sum()))\n"
        "print(f'observed total={y.sum()}; posterior-predictive p-value for total={p_value:.3f} "
        "(near 0.5 = good fit)')"
    )

    nb.md(
        "## Step 7 — Model criticism & comparison: the offset matters",
        "We criticize the model by fitting the **wrong** version that omits the "
        "exposure offset, and comparing. The correct model recovers the truth; the "
        "no-offset model is badly biased — it mistakes 'more exposure -> more counts' "
        "for 'a higher rate'.",
    )
    nb.code(
        "idata_no_offset = fit(data, draws=1000, tune=1000, chains=2, seed=303,\n"
        "                      use_offset=False)\n"
        "print('correct  log_rate mean =', float(idata.posterior['log_rate'].mean()))\n"
        "print('no-offset log_rate mean =', float(idata_no_offset.posterior['log_rate'].mean()))\n"
        "print('true     log_rate      =', data['truth']['log_rate'])\n"
        "print('the no-offset estimate ~ log(mean count) ~ log(7) ~ 1.95, far from -1.2')"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Report the rate on the interpretable (per-unit-exposure) scale, with a "
        "credible interval, and translate to an expected count for a stated exposure.",
    )
    nb.code(
        "r_post = idata.posterior['log_rate'].values.ravel()\n"
        "rate_post = np.exp(r_post)\n"
        "lo, hi = np.percentile(rate_post, [3, 97])\n"
        "print(f'Rate lambda = {rate_post.mean():.3f} events/unit, 94% CI [{lo:.3f}, {hi:.3f}]')\n"
        "exposure_q = 20.0\n"
        "exp_count = rate_post.mean() * exposure_q\n"
        "print(f'Expected count at exposure {exposure_q}: ~{exp_count:.1f} events')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The event rate is about 0.30 per unit "
        "exposure (94% CI roughly [0.27, 0.36]). A new sample with exposure 20 should "
        "yield about 6 events. The single most important modeling decision was using "
        "the **exposure offset**: without it the rate is off by an order of magnitude.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """A deliberately broken version for the debugging exercise. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 03 — BROKEN debugging exercise")
    nb.md(
        "# Project 03 — BROKEN notebook (debugging exercise)",
        "This notebook contains **seeded bugs**, the headline one being an **omitted "
        "exposure offset**. Run it, read the diagnostics, find each bug, and fix it. "
        "The clean reference is `notebook.ipynb`; the answer key is `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nRNG = 20240603"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate()\n"
        "y, e = data['y'], data['exposure']"
    )
    nb.md(
        "### Model — the exposure is ignored, and the rate prior is on the wrong scale.")
    nb.code(
        "# BUG 1 (headline): the exposure offset is OMITTED. mu = exp(log_rate) for\n"
        "#   every sample, ignoring that exposures vary over [5, 40]. This mistakes\n"
        "#   'more exposure -> more counts' for 'a higher rate' and biases the estimate.\n"
        "# BUG 2: a flat prior placed DIRECTLY on the positive rate (Uniform), instead\n"
        "#   of a Normal prior on the LOG rate. This breaks the log-link parameterization\n"
        "#   and puts implausible mass on huge rates.\n"
        "with pm.Model() as model:\n"
        "    rate = pm.Uniform('rate', lower=0.0, upper=1e4)   # BUG 2\n"
        "    mu = rate                                          # BUG 1: no * exposure\n"
        "    pm.Poisson('y', mu=mu, observed=y)\n"
        "    idata = pm.sample(draws=1000, tune=1000, chains=2, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['rate']))\n"
        "print('true rate =', np.exp(data['truth']['log_rate']),\n"
        "      '-> the estimate will be ~mean count ~7, not ~0.30')"
    )
    nb.md(
        "### Posterior predictive — BUG 3: a residual check summed over the wrong axis.")
    nb.code(
        "with model:\n"
        "    idata.extend(pm.sample_posterior_predictive(idata, random_seed=RNG,\n"
        "                                                progressbar=False))\n"
        "pp = idata.posterior_predictive['y']\n"
        "# BUG 3: summing over 'draw' instead of the observation axis for the total count\n"
        "pp_tot = pp.sum(dim='draw').values.ravel()\n"
        "print('observed total =', y.sum(), 'predicted total mean =', pp_tot.mean())"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
