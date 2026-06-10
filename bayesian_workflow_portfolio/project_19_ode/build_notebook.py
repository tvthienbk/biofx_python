"""Emit notebook.ipynb (clean PK/ODE workflow) and notebook_broken.ipynb.

Run:  python build_notebook.py
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
    nb = NotebookBuilder(title="Project 19 — Mechanistic Model (Bayesian PK / ODE)")

    nb.md(
        "# Project 19 — Mechanistic Model: 1-Compartment PK (Bayesian ODE)",
        "**Scenario.** A drug given as a single IV bolus is eliminated from a single "
        "compartment by a first-order process: $dC/dt = -kC$, $C(0)=D/V$. We observe "
        "noisy concentrations and infer the **mechanistic rate constants** $k$ "
        "(elimination) and $V$ (volume).",
        "**New skill.** ODE inference, identifiability, and the compute cost of "
        "solvers. **Key pitfall.** *Practical non-identifiability*: if the design "
        "doesn't pin down both $C_0=D/V$ (early times) and the decay slope $k$ (late "
        "times), $k$ and $V$ correlate — the PK analogue of the Michaelis-Menten "
        "$V_\\max/K_m$ correlation.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Compute note (read first)",
        "This model has a **closed-form solution** $C(t)=(D/V)e^{-kt}$. We fit that "
        "analytic form (exact, fast). PyMC also offers `pymc.ode.DifferentialEquation`, "
        "which integrates the ODE numerically at every sampler step — the genuine "
        "ODE-inference workflow, but far slower. We show it in Step 7 with tiny "
        "settings. **For a system with a closed form, using it is the responsible "
        "choice**; reserve the numerical solver for ODEs without one.",
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "$y_i = C(t_i) + \\varepsilon_i$, $\\varepsilon_i\\sim N(0,\\sigma^2)$, with "
        "$C(t)=(D/V)e^{-kt}$. **Assumptions:** (a) one well-mixed compartment; (b) "
        "first-order (linear) elimination; (c) instantaneous IV bolus at $t=0$; (d) "
        "additive Gaussian measurement noise. Truths: $k=0.35$/h, $V=8$ L, "
        "$\\sigma=0.4$ mg/L. The design includes **early** points (pin $C_0=D/V$) and "
        "**late** points (pin the slope $k$).",
    )
    nb.code(
        "from data.generate_data import generate, analytic_C\n"
        "data = generate()\n"
        "print(f\"n={data['n']} timepoints, dose={data['dose']:.0f} mg\")\n"
        "print(f\"truth: k={data['truth']['k']}, V={data['truth']['V']}, sigma={data['truth']['sigma']}\")\n"
        "tt = np.linspace(0, data['t'].max(), 200)\n"
        "fig, ax = plt.subplots(figsize=(6.5,3.6))\n"
        "ax.plot(tt, analytic_C(tt), 'k--', label='true C(t)')\n"
        "ax.scatter(data['t'], data['y'], color='#4C72B0', zorder=3, label='noisy data')\n"
        "ax.set(xlabel='time (h)', ylabel='concentration (mg/L)', title='PK profile')\n"
        "ax.legend(); plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model specification (mechanism + justified priors)",
        "We sample $k$ and $V$ on the **log scale** (they are positive and span orders "
        "of magnitude). Priors: $\\log k\\sim N(-1,0.7)$ (so $k\\approx 0.37$/h), "
        "$\\log V\\sim N(2,0.5)$ (so $V\\approx 7.4$ L), $\\sigma\\sim\\text{HalfNormal}(1)$. "
        "These encode plausible physiological ranges — mechanistic models *should* use "
        "informed priors.",
    )
    nb.code(
        "from model import build_model, fit, fit_ode\n"
        "model = build_model(data)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive checks",
        "We simulate concentration curves implied by the priors. They should look like "
        "plausible decay profiles — right order of magnitude for $C_0$, sensible "
        "half-lives — not absurd (megagram concentrations or instantaneous "
        "disappearance).",
    )
    nb.code(
        "rng = np.random.default_rng(RNG)\n"
        "fig, ax = plt.subplots(figsize=(6.5,3.6))\n"
        "for _ in range(12):\n"
        "    k = np.exp(rng.normal(-1,0.7)); V = np.exp(rng.normal(2,0.5))\n"
        "    ax.plot(tt, (data['dose']/V)*np.exp(-k*tt), lw=1, alpha=0.7)\n"
        "ax.set(xlabel='time (h)', ylabel='C(t)', title='Prior predictive PK curves')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=600, tune=1000, chains=2, target_accept=0.9, cores=1`. The "
        "log parameterisation gives a well-behaved geometry; the analytic likelihood "
        "makes this fast.",
    )
    nb.code("idata = fit(data, draws=600, tune=1000, chains=2, seed=101)")

    nb.md(
        "## Step 5 — Computational diagnostics & identifiability",
        "Check $\\hat R$, ESS, divergences. The key plot is the **$(k, V)$ pair plot**: "
        "with the full design it is a compact blob; a strong diagonal correlation would "
        "warn of practical non-identifiability. We also look at clearance "
        "$CL=k\\cdot V$, which is often *better* identified than either factor.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['k','V','sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_pair(idata, var_names=['k','V'], kind='scatter',\n"
            "             scatter_kwargs={'alpha':0.2}); plt.tight_layout()")
    nb.code(
        "k = idata.posterior['k'].values.ravel(); V = idata.posterior['V'].values.ravel()\n"
        "CL = k*V\n"
        "print(f'corr(k,V) = {np.corrcoef(k,V)[0,1]:.3f}')\n"
        "print(f'clearance CL=k*V: mean={CL.mean():.2f} L/h '\n"
        "      f'(94% [{np.percentile(CL,3):.2f},{np.percentile(CL,97):.2f}])')"
    )

    nb.md(
        "## Step 6 — Posterior predictive checks",
        "Overlay posterior-predictive concentration curves on the data; the observed "
        "points should sit inside the predictive band. We also report a Bayesian "
        "p-value on a discrepancy (e.g. the residual sum of squares).",
    )
    nb.code(
        "ax = az.plot_ppc(idata, num_pp_samples=100); plt.tight_layout()"
    )

    nb.md(
        "## Step 7 — Model criticism & the genuine ODE solver",
        "We demonstrate the same model via `pymc.ode.DifferentialEquation` (numerical "
        "integration) on tiny settings, and confirm it agrees with the analytic fit. "
        "This is the workflow you would use for an ODE **without** a closed form (e.g. "
        "saturable Michaelis-Menten elimination). It is much slower — note the time.",
    )
    nb.code(
        "import time; t0=time.time()\n"
        "idata_ode = fit_ode(data, draws=100, tune=200, chains=2, seed=101)\n"
        "print(f'ODE-solver fit took {time.time()-t0:.1f}s (vs the analytic fit, ~instant)')\n"
        "print(az.summary(idata_ode, var_names=['k','V']))\n"
        "print('analytic k,V:', float(idata.posterior['k'].mean()), float(idata.posterior['V'].mean()))"
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "Translate into a dosing-relevant quantity: the **half-life** "
        "$t_{1/2}=\\ln 2/k$ and the **clearance** $CL=kV$, each with a credible "
        "interval — the numbers a pharmacologist uses to choose a dosing interval.",
    )
    nb.code(
        "thalf = np.log(2)/k\n"
        "print(f'half-life t1/2 = {thalf.mean():.2f} h '\n"
        "      f'(94% [{np.percentile(thalf,3):.2f}, {np.percentile(thalf,97):.2f}])')\n"
        "print(f'clearance CL = {CL.mean():.2f} L/h '\n"
        "      f'(94% [{np.percentile(CL,3):.2f}, {np.percentile(CL,97):.2f}])')"
    )
    nb.md(
        "**Conclusion (for a collaborator).** The mechanism is identified by this "
        "design: $k$ and $V$ recover their true values, and clearance/half-life come "
        "with usable intervals. The identifiability hinged on having **both** early and "
        "late samples — see the broken notebook for what happens without the early "
        "points.",
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Seeded bugs: identifiability trap (no early points) + loose solver hint."""
    nb = NotebookBuilder(title="Project 19 — BROKEN debugging exercise")
    nb.md(
        "# Project 19 — BROKEN notebook (debugging exercise)",
        "Seeded bugs centred on the ODE pitfall: **practical non-identifiability** of "
        "$k$ and $V$ when the design is poor. Run it, read the $(k,V)$ pair plot and "
        "diagnostics, find each bug, fix it. Answer key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\nimport pytensor.tensor as pt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "full = generate()\n"
        "# BUG 1: keep ONLY late timepoints (>= 3h). Without early points, C0=D/V is\n"
        "#         unconstrained, so V and k become practically non-identifiable.\n"
        "mask = full['t'] >= 3.0\n"
        "data = {'t': full['t'][mask], 'y': full['y'][mask], 'dose': full['dose']}\n"
        "print('using', mask.sum(), 'of', full['n'], 'timepoints (late only)')"
    )
    nb.md("### Model — vague priors on top of a bad design make it worse.")
    nb.code(
        "# BUG 2: vague priors on log k and log V (sigma=3) remove the last bit of\n"
        "#         information that could have rescued the poor design.\n"
        "t = data['t']; y = data['y']; dose = data['dose']\n"
        "with pm.Model() as model:\n"
        "    log_k = pm.Normal('log_k', mu=0.0, sigma=3.0)\n"
        "    log_V = pm.Normal('log_V', mu=0.0, sigma=3.0)\n"
        "    k = pm.Deterministic('k', pt.exp(log_k))\n"
        "    V = pm.Deterministic('V', pt.exp(log_V))\n"
        "    sigma = pm.HalfNormal('sigma', sigma=1.0)\n"
        "    C = (dose/V)*pt.exp(-k*t)\n"
        "    pm.Normal('y_obs', mu=C, sigma=sigma, observed=y)\n"
        "    idata = pm.sample(draws=500, tune=800, chains=2, cores=1,\n"
        "                      target_accept=0.9, random_seed=RNG, progressbar=False)"
    )
    nb.code(
        "print(az.summary(idata, var_names=['k','V','sigma']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.md(
        "### The smoking gun — BUG 3: the (k, V) pair plot is a ridge.",
        "Without early timepoints, many $(k, V)$ pairs fit the late-time data equally "
        "well: a long diagonal correlation, inflated R-hat, low ESS. Note that the "
        "*product* (clearance $k V$) may still be okay while $k$ and $V$ separately are "
        "not — the hallmark of practical non-identifiability. Fixes: (1) restore the "
        "early timepoints (design); (2) use the informative priors from `model.py`.",
    )
    nb.code(
        "az.plot_pair(idata, var_names=['k','V'], kind='scatter',\n"
        "             scatter_kwargs={'alpha':0.2}); plt.tight_layout()\n"
        "kk = idata.posterior['k'].values.ravel(); VV = idata.posterior['V'].values.ravel()\n"
        "print('corr(k,V) =', round(float(np.corrcoef(kk,VV)[0,1]),3))"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
