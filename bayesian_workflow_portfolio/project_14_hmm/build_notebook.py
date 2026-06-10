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
    nb = NotebookBuilder(title="Project 14 — State switching over time (HMM)")

    nb.md(
        "# Project 14 — State switching over time (Hidden Markov Model)",
        "**Scenario.** An ion channel (or an MD trajectory) switches between a "
        "**closed** and an **open** state over time. The state *persists* — once open "
        "it tends to stay open — so successive noisy emissions are correlated through "
        "the hidden state. We observe the emissions, never the states, and want the "
        "**transition matrix** and the per-state emission means.",
        "**New skill.** Discrete latent *dynamics* and transition-matrix inference. "
        "**Key pitfall.** Non-identifiable state labels (same permutation symmetry as a "
        "mixture). **Implementation.** We **marginalize the discrete states** with the "
        "forward algorithm (in `pytensor.scan`, inside a `pm.Potential`), so NUTS only "
        "samples continuous parameters.",
    )

    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import matplotlib.pyplot as plt\n"
        "az.style.use('arviz-darkgrid')\nRNG = 20240601"
    )

    nb.md(
        "## Step 1 — Problem & data-generating story",
        "Generative model: $s_1\\sim\\text{Cat}(\\pi)$, "
        "$s_t\\mid s_{t-1}\\sim\\text{Cat}(P[s_{t-1},:])$, "
        "$y_t\\mid s_t\\sim\\mathcal{N}(\\mu_{s_t},\\sigma)$. The transition matrix is "
        "parameterized by two switch probabilities $p_{01}$ (closed→open) and $p_{10}$ "
        "(open→closed). **Assumptions:** (a) exactly 2 states, (b) first-order Markov "
        "(memoryless given the previous state), (c) Gaussian emissions with shared "
        "$\\sigma$, (d) time-homogeneous transitions. Truth: $p_{01}=0.08, p_{10}=0.15, "
        "\\mu=(-1.5,1.5), \\sigma=0.6$.",
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); y = data['y']; states = data['states']; t = data['truth']\n"
        "print(f\"T={len(y)}, fraction open={np.mean(states==1):.2f}\")"
    )
    nb.code(
        "fig, axes = plt.subplots(2, 1, figsize=(8,4), sharex=True)\n"
        "axes[0].plot(y, lw=0.8, color='#4C72B0'); axes[0].set_ylabel('emission y_t')\n"
        "axes[1].step(range(len(states)), states, where='mid', color='#C44E52')\n"
        "axes[1].set(ylabel='hidden state', yticks=[0,1], xlabel='time t')\n"
        "axes[0].set_title('Noisy emissions and the (hidden) state path')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 2 — Model: marginalize the states (forward algorithm)",
        "We do **not** sample the discrete path $s_{1:T}$. The marginal likelihood "
        "$p(y\\mid\\theta)=\\sum_{s_{1:T}} p(y,s_{1:T}\\mid\\theta)$ is computed exactly "
        "by the forward recursion in log space:",
        "$$\\alpha_1[j]=\\log\\pi_j+\\log\\mathcal N(y_1;\\mu_j,\\sigma),\\quad "
        "\\alpha_t[j]=\\log\\mathcal N(y_t;\\mu_j,\\sigma)+\\operatorname*{logsumexp}_i"
        "\\big(\\alpha_{t-1}[i]+\\log P_{ij}\\big),$$",
        "$$\\log p(y\\mid\\theta)=\\operatorname*{logsumexp}_j \\alpha_T[j].$$",
        "The **log-sum-exp at every step is essential** — it is what makes this the "
        "*sum* over paths (a proper marginal) rather than the *max* over paths (Viterbi). "
        "Priors: $p_{01},p_{10}\\sim\\text{Beta}(2,8)$ (favouring rare switches), "
        "$\\mu\\sim\\text{Normal}(0,3)$ **ordered** so $\\mu_0<\\mu_1$ (breaks the "
        "state-label symmetry), $\\sigma\\sim\\text{HalfNormal}(1)$.",
    )
    nb.code(
        "from model import build_model, fit, add_named\n"
        "model = build_model(data, ordered=True)\n"
        "model"
    )

    nb.md(
        "## Step 3 — Prior predictive (on parameters)",
        "Because the likelihood is a `pm.Potential` (no observed RV), standard "
        "data-space prior predictive is not defined. We instead inspect the *parameter* "
        "prior: do the implied dwell times $1/p$ and emission means look physically "
        "plausible? Beta(2,8) puts switch probabilities mostly in 0.05–0.4, i.e. dwell "
        "times of a few to tens of steps — reasonable for a channel.",
    )
    nb.code(
        "from scipy.stats import beta as beta_dist\n"
        "grid = np.linspace(0,1,200)\n"
        "fig, ax = plt.subplots(figsize=(6,3.2))\n"
        "ax.plot(grid, beta_dist.pdf(grid, 2, 8), color='#55A868')\n"
        "ax.fill_between(grid, beta_dist.pdf(grid, 2, 8), alpha=0.3, color='#55A868')\n"
        "ax.set(xlabel='switch probability', ylabel='prior density',\n"
        "       title='Beta(2,8) prior on p01, p10 — favours rare switches')\n"
        "plt.tight_layout()"
    )

    nb.md(
        "## Step 4 — Inference (NUTS)",
        "Settings: `draws=500, tune=1000, chains=2, target_accept=0.9`. The forward "
        "scan makes each gradient ~T times more expensive than a plain model, so the "
        "fit takes ~1 minute at T=250 — still light. The ordered transform keeps the "
        "state labels identified.",
    )
    nb.code("idata = fit(data, draws=500, tune=1000, chains=2, seed=14)\nadd_named(idata)")

    nb.md(
        "## Step 5 — Diagnostics & recovering the transition matrix",
        "Check R-hat ≈ 1.00, healthy ESS, 0 divergences. Then read off the recovered "
        "transition probabilities and emission means and compare to truth.",
    )
    nb.code(
        "print(az.summary(idata, var_names=['p01','p10','mu','sigma','separation']))\n"
        "print('divergences:', int(idata.sample_stats['diverging'].sum()))"
    )
    nb.code("az.plot_trace(idata, var_names=['p01','p10','mu']); plt.tight_layout()")
    nb.code(
        "p01 = float(idata.posterior['p01'].mean()); p10 = float(idata.posterior['p10'].mean())\n"
        "P_hat = np.array([[1-p01, p01],[p10, 1-p10]])\n"
        "print('Recovered transition matrix P:\\n', np.round(P_hat,3))\n"
        "print('True P:\\n', np.array([[1-t['p01'], t['p01']],[t['p10'], 1-t['p10']]]))"
    )

    nb.md(
        "## Step 6 — Posterior predictive check (simulate trajectories)",
        "We simulate trajectories from the posterior parameters and compare summary "
        "statistics (here the marginal emission histogram and the fraction of time in "
        "the high state) to the observed data — a posterior-predictive check tailored "
        "to a Potential-likelihood model.",
    )
    nb.code(
        "def sim_traj(p01, p10, mu, sigma, T, rng):\n"
        "    P = np.array([[1-p01,p01],[p10,1-p10]]); s = np.zeros(T, int)\n"
        "    s[0] = rng.integers(2)\n"
        "    for k in range(1,T): s[k] = rng.choice(2, p=P[s[k-1]])\n"
        "    return rng.normal(np.array(mu)[s], sigma)\n"
        "rng = np.random.default_rng(0)\n"
        "post = idata.posterior\n"
        "draws = [(float(post['p01'].values.ravel()[i]), float(post['p10'].values.ravel()[i]),\n"
        "          post['mu'].values.reshape(-1,2)[i], float(post['sigma'].values.ravel()[i]))\n"
        "         for i in rng.integers(0, post['p01'].size, 40)]\n"
        "fig, ax = plt.subplots(figsize=(6,3.5))\n"
        "for d in draws:\n"
        "    ax.hist(sim_traj(*d, len(y), rng), bins=30, histtype='step', density=True, alpha=0.3, color='#4C72B0')\n"
        "ax.hist(y, bins=30, density=True, color='k', histtype='step', lw=2, label='observed')\n"
        "ax.legend(); ax.set_title('Posterior predictive emission histograms'); plt.tight_layout()"
    )

    nb.md(
        "## Step 7 — Criticism & identifiability",
        "The state labels are identified only because we ordered the emission means. "
        "Report label-invariant quantities (separation, sigma) and *direction-aware* "
        "transition probabilities (p01 = into the higher state). `test_recovery.py` "
        "checks all of these against truth.",
    )

    nb.md(
        "## Step 8 — Decision & communication",
        "For a collaborator: 'The channel spends ~37% of the time open; it opens rarely "
        "(p≈0.08 per step) but, once open, closes at p≈0.15 per step, giving a mean open "
        "dwell of ~1/0.15 ≈ 7 steps.' Dwell times and occupancy are the actionable "
        "outputs. See `summary_onepager.md`.",
    )
    nb.code(
        "open_dwell = 1/float(idata.posterior['p10'].mean())\n"
        "closed_dwell = 1/float(idata.posterior['p01'].mean())\n"
        "print(f'mean open dwell  ~ {open_dwell:.1f} steps')\n"
        "print(f'mean closed dwell~ {closed_dwell:.1f} steps')"
    )
    return nb


def broken_notebook() -> NotebookBuilder:
    """Broken version: unordered means + a wrong forward recursion. See BROKEN_BUGS.md."""
    nb = NotebookBuilder(title="Project 14 — BROKEN debugging exercise")
    nb.md(
        "# Project 14 — BROKEN notebook (HMM pitfalls)",
        "Seeded bugs centred on (1) state-label non-identifiability and (2) a broken "
        "forward recursion. Run it, read the diagnostics, fix each bug. Clean reference: "
        "`notebook.ipynb`; answer key: `BROKEN_BUGS.md`.",
    )
    nb.code(PATH_PREAMBLE)
    nb.code(
        "import numpy as np\nimport pymc as pm\nimport arviz as az\n"
        "import pytensor.tensor as pt\nfrom pytensor import scan\n"
        "import matplotlib.pyplot as plt\nRNG = 20240601"
    )
    nb.code(
        "from data.generate_data import generate\n"
        "data = generate(); y = data['y']; t = data['truth']\n"
        "yt = pt.as_tensor_variable(y)"
    )
    nb.md(
        "### BUG 1 — wrong forward recursion: max instead of log-sum-exp.",
        "Replacing `logsumexp` with `max` computes the **Viterbi** best-path "
        "probability, not the marginal likelihood. Inference is then fit to the wrong "
        "objective and the parameters are biased.",
    )
    nb.code(
        "def forward_BUGGY(y, p01, p10, mu, sigma):\n"
        "    yc = y[:, None]\n"
        "    logem = -0.5*pt.log(2*np.pi*sigma**2) - 0.5*((yc-mu[None,:])/sigma)**2\n"
        "    logP = pt.log(pt.stack([pt.stack([1-p01,p01]), pt.stack([p10,1-p10])]))\n"
        "    a0 = pt.log(pt.as_tensor([0.5,0.5])) + logem[0]\n"
        "    def step(logem_t, a_prev, logP):\n"
        "        m = a_prev[:, None] + logP\n"
        "        # BUG 1: should be pt.logsumexp(m, axis=0); max() drops the normalization\n"
        "        return logem_t + pt.max(m, axis=0)\n"
        "    seq, _ = scan(step, sequences=[logem[1:]], outputs_info=[a0],\n"
        "                  non_sequences=[logP], return_updates=True)\n"
        "    # BUG 1 (cont.): and the final reduction should be logsumexp, not max\n"
        "    return pt.max(seq[-1])"
    )
    nb.md("### BUG 2 — unordered emission means: state-label non-identifiability.")
    nb.code(
        "with pm.Model() as model:\n"
        "    p01 = pm.Beta('p01', 2, 8); p10 = pm.Beta('p10', 2, 8)\n"
        "    # BUG 2: no ordered transform -> labels can swap across chains\n"
        "    mu = pm.Normal('mu', 0.0, 3.0, shape=2)\n"
        "    sigma = pm.HalfNormal('sigma', 1.0)\n"
        "    pm.Potential('hmm', forward_BUGGY(yt, p01, p10, mu, sigma))\n"
        "    idata = pm.sample(draws=400, tune=400, chains=4, random_seed=RNG,\n"
        "                      progressbar=False)"
    )
    nb.code(
        "# Expect: biased p01/p10 (wrong objective) AND high R-hat on mu (label swap).\n"
        "print(az.summary(idata, var_names=['p01','p10','mu','sigma']))\n"
        "print('true p01,p10 =', t['p01'], t['p10'])"
    )
    return nb


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    clean_notebook().save(str(here / "notebook.ipynb"))
    broken_notebook().save(str(here / "notebook_broken.ipynb"))
    print("wrote notebook.ipynb and notebook_broken.ipynb")
