# Simulation-Based Calibration (SBC) — Project 12

**Model:** errors-in-variables (latent true predictor)
`x_true ~ Normal(mu_x, sd_x)`, `x_obs ~ Normal(x_true, tau_x)`,
`y ~ Normal(alpha + beta*x_true, sigma_y)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC here, and what we target

The EIV model introduces a per-observation latent vector `x_true` and a measurement
model — exactly the kind of structure where a subtle bug (a misaligned latent, a
wrong noise wiring) can converge cleanly to a wrong posterior. SBC checks the whole
procedure: with parameters drawn from the prior and data simulated from them, each
true value's rank among the posterior draws must be uniform.

We target the **regression coefficients** `alpha` and `beta` — the quantities the
project is about, and the ones the naive model attenuates. (`sigma_y` is the most
weakly-identified parameter and is not the inferential target, so we do not SBC it.)
`tau_x` is held at its known value throughout, matching how the model is used.

---

## 2. Procedure

For each of `N_SIMS = 18` simulations: draw `alpha* ~ Normal(0,5)`,
`beta* ~ Normal(0,5)`, `sigma_y* ~ HalfNormal(2)`; draw `x_true ~ Normal(0,1)`,
`x_obs = x_true + Normal(0, tau_x)` with known `tau_x = 0.6`, and
`y = alpha* + beta* x_true + Normal(0, sigma_y*)` for N=60 units; refit the EIV model
(1 chain, 400 tune, L≈150 draws, `target_accept=0.95`); record the ranks. Uniformity
tested with chi-square (`assert_calibrated`, 6 bins). Light by design — the latent
vector makes each refit costly. Reproduce: `python3 sbc.py`.

---

## 3. Results

```
SBC over 18 simulations (N=60, tau_x=0.6, L~150)
  alpha: chi2=2.00, dof=5, p=0.849, uniform=True
  beta:  chi2=5.33, dof=5, p=0.377, uniform=True
  saved sbc_ranks.png
```

| Parameter | chi2 | dof | p-value | Verdict |
|---|---|---|---|---|
| `alpha` | 2.00 | 5 | 0.849 | Uniform |
| `beta`  | 5.33 | 5 | 0.377 | Uniform |

Both rank histograms are consistent with uniformity.

---

## 4. Interpretation

The EIV model is **calibrated** for both regression coefficients (when `tau_x` is
known and correct). This is the reassuring complement to the recovery test: not only
does the model recover the true slope on one dataset, the *procedure* is
self-consistent across many. In particular, the latent-predictor machinery and the
measurement model are wired correctly — a misaligned latent (the broken notebook's
Bug 2) would distort `beta`'s ranks.

A caveat specific to this model: SBC here assumes `tau_x` is known and **matches**
the value used to simulate. That is the model's stated assumption. SBC does **not**
exonerate a *wrong* `tau_x` — that failure mode is bias, studied separately in
`prior_sensitivity.py` (the de-attenuation curve). SBC checks "given the assumptions,
is inference correct?"; prior sensitivity checks "what if an assumption is wrong?".

With 18 simulations and 6 bins this is a moderate-resolution test — enough to catch a
gross calibration failure, read as "no detectable miscalibration".

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the EIV SBC for `(alpha, beta)` and saves the histograms. |
| `sbc_ranks.png` | Rank histograms for `alpha`, `beta`. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated`. |
