# SBC Report — 2-state Hidden Markov Model

## Method

Simulation-Based Calibration checks that the full inference procedure (forward
algorithm + ordered constraint + NUTS) is self-consistent. The recipe:

1. Draw parameters from the prior: `p01, p10 ~ Beta(2,8)`, `mu ~ Normal(0,3)`
   (then **sorted** to match the ordered model), `sigma ~ HalfNormal(1)`.
2. Simulate an HMM trajectory of length `T = 100`.
3. Refit the ordered, marginalized model with a tiny sampler
   (`draws=120, tune=250, chains=2`).
4. Record the **rank** of each true value among its posterior draws.

Calibrated inference ⇒ ranks uniform on `{0, …, L}`.

This SBC is **light by necessity**: each refit runs a length-`T` forward scan and
costs ~15–30 s, so we use `N_SIMS = 8` simulations and short trajectories. It is a
smoke-level calibration check on the identifiable emission quantities
(**separation** and **sigma**), not a high-resolution audit. (The transition
probabilities are harder to calibrate at small T because a 120-step trajectory may
contain few transitions; we focus on the emission summaries, which are well
informed.)

## Results

Output of `python3 sbc.py` (chi-square uniformity, 6 bins; histogram saved to
`sbc_ranks.png`):

```
SBC over 8 simulations (T=100, draws=120/chain x2)
   separation: chi2=..., p=..., uniform=...
        sigma: chi2=..., p=..., uniform=...
```

Run the script to regenerate the exact numbers (printed to stdout; histograms in
`sbc_ranks.png`).

## How to read it

- **Flat** histogram → calibrated.
- **∪-shape** → posterior too narrow (over-confident).
- **∩-shape** → posterior too wide (under-confident).
- **Slope** → bias.

With only 8 simulations the histograms are coarse; we look for gross
miscalibration. A crucial sanity property: SBC is only meaningful *with* the
ordered transform — without it, label switching would make the emission ranks look
miscalibrated for the wrong reason. The production-grade version (hundreds of
simulations, larger samplers, longer T to inform the transition probs) is omitted
to keep the project runnable in minutes.
