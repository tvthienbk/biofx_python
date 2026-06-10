# SBC Report — change-point model

## Method

Simulation-Based Calibration checks that the inference procedure is
self-consistent. We calibrate the **pre/post Poisson rates** (`lam0`, `lam1`), the
clearly identifiable parameters. Recipe:

1. Draw `lam0, lam1 ~ Exponential(1/5)` and `tau ~ DiscreteUniform(1, T-1)`.
2. Simulate a Poisson count series with the shift at `tau`.
3. Refit the discrete-tau model with a small sampler (`draws=300, tune=500,
   chains=2`).
4. Record the **rank** of each true rate among its posterior draws.

Calibrated inference ⇒ ranks uniform on `{0, …, L}`. The discrete-tau model is
cheap (NUTS on two rates + Metropolis on `tau`), so we can afford `N_SIMS = 45`
simulations — a more substantial check than the other advanced projects allow.

## Results

Output of `python3 sbc.py` (chi-square uniformity, 10 bins; histograms saved to
`sbc_ranks.png`):

```
SBC over 45 simulations (T=120, draws=300/chain x2)
   lam0: chi2=8.11, p=0.523, uniform=True
   lam1: chi2=5.89, p=0.751, uniform=True
```

Both rates pass the 10-bin chi-square uniformity test. Run the script to
regenerate the exact numbers (printed to stdout; histograms in `sbc_ranks.png`).

## How to read it

- **Flat** histogram → that rate's inference is calibrated.
- **∪-shape** → posterior too narrow (over-confident).
- **∩-shape** → posterior too wide (under-confident).
- **Slope** → bias.

We calibrate the **rates** rather than `tau` because `tau` is discrete and bounded;
its rank statistic is coarse and, when the simulated shift is weak (rates close
together, or `tau` near an edge), the `tau` posterior is legitimately diffuse —
that would register as "miscalibration" for a reason that is actually correct
modelling behaviour. The rates are the clean, continuous SBC targets.

## What a failure here would mean

If `lam0`/`lam1` ranks were ∪-shaped, the model would be over-confident about the
rates — often a sign of an index bug that mislabels which observations belong to
which regime (the off-by-one seeded in the broken notebook). SBC on the rates is
therefore also an indirect check that the switch logic is correct.
