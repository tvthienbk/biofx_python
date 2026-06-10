# Simulation-Based Calibration (SBC) — Project 01

**Model:** `y_i ~ Bernoulli(theta)`, `theta ~ Beta(2, 2)`
**Script:** `sbc.py` · **Figure:** `sbc_ranks.png`

---

## 1. Why SBC, and what it actually checks

Convergence diagnostics (R-hat, ESS, divergences) tell you the sampler explored
the posterior *it was given*. They are silent about whether that posterior is the
**correct** one for your model. A model with a coding error, a mis-specified
prior, or a buggy likelihood can converge beautifully to the *wrong* distribution.

Simulation-Based Calibration tests the inference *procedure* as a whole — model +
sampler together — for self-consistency. The guarantee it leans on is exact:

> If `theta* ~ prior` and `y ~ likelihood(theta*)`, then the rank of `theta*`
> among `L` draws from the posterior `p(theta | y)` is **uniform** on
> `{0, 1, ..., L}` — provided inference is correct.

Any systematic departure from uniformity is a fingerprint of a specific failure:

| Rank histogram shape | Diagnosis |
|---|---|
| Uniform (flat) | Calibrated — what we want. |
| ∪-shaped (heavy at both ends) | Posterior **too narrow** (over-confident). |
| ∩-shaped (heavy in the middle) | Posterior **too wide** (under-confident). |
| Sloped / shifted | **Biased** posterior (location off). |

---

## 2. Procedure used here

For each of `N_SIMS = 400` simulations:

1. Draw `theta* ~ Beta(2, 2)` (the prior).
2. Simulate `k ~ Binomial(N=80, theta*)` (the likelihood).
3. Obtain `L = 256` posterior draws. **We use the exact conjugate posterior**
   `Beta(2+k, 2+N-k)` rather than MCMC. This is deliberate: it makes SBC
   essentially instantaneous and isolates *modeling* correctness from sampler
   noise. (An MCMC variant would test the sampler too, at much higher cost.)
4. Record the rank statistic via `shared.bayes_utils.sbc_rank`.

Uniformity is then tested with a chi-square goodness-of-fit test
(`shared.bayes_utils.assert_calibrated`, 16 bins).

Reproduce with:

```bash
python3 sbc.py
```

---

## 3. Results

```
SBC over 400 simulations (N=80, L=256)
  chi-square uniformity test: chi2=8.48, dof=15, p=0.903
  ranks look uniform: True
  saved sbc_ranks.png
```

| Quantity | Value |
|---|---|
| Simulations | 400 |
| Data size per sim, N | 80 |
| Posterior draws per sim, L | 256 |
| Chi-square statistic | 8.48 |
| Degrees of freedom | 15 |
| p-value | **0.903** |
| Verdict | **Uniform — calibrated** |

The rank histogram (`sbc_ranks.png`) is flat: every bin sits near the uniform
expectation line (400 / 16 = 25 counts per bin), with no ∪, ∩, or slope.

---

## 4. Interpretation

A chi-square p-value of **0.903** means the observed rank distribution is entirely
consistent with uniformity — there is no evidence of miscalibration. Concretely:

- **No over-confidence** (no ∪): the Beta posterior is not too narrow; its
  credible intervals have correct coverage.
- **No under-confidence** (no ∩): nor is it too wide.
- **No bias** (no slope): the posterior is centred correctly relative to truth.

This is the *expected* outcome for a correctly-implemented conjugate model — and
that is exactly why Project 01 is the right place to *first* run SBC: we know what
"pass" must look like, so we learn to read the histogram against a known-good
case before trusting it on hard models where there is no analytic check.

### A note on reading the p-value

A high p-value here is reassuring, but SBC is a *falsification* tool: it can show
miscalibration, it cannot prove perfect calibration. A pass means "no detectable
problem at this resolution (400 sims, 16 bins)". To stress it harder, raise
`N_SIMS` and the bin count, or deliberately corrupt the posterior (e.g. inflate
its width) and confirm the test then *fails* — a recommended exercise in
`lessons.md`.

---

## 5. Files

| File | Role |
|---|---|
| `sbc.py` | Runs the 400-simulation SBC and saves the histogram. |
| `sbc_ranks.png` | Rank histogram with the uniform-expectation reference line. |
| `shared/bayes_utils.py` | `sbc_rank`, `assert_calibrated` (chi-square test). |
