# Lessons — Project 09: Partial Pooling

This report records what Project 09 teaches, the failure modes met while building
and running it, and how hierarchical partial pooling generalizes to the rest of
the portfolio. The headline skill is **partial pooling / shrinkage**; the headline
hazard is **the funnel and centered-vs-non-centered parameterization**.

---

## 1. What this project is really about

Project 01 estimated one number. Project 09 estimates a *population* of numbers —
12 group means — that are tied together by a shared distribution we also estimate.
That single structural change (a prior on the group means whose parameters are
themselves estimated) buys an enormous amount: each group borrows strength from
the others, noisy groups are stabilized, and we get an honest estimate of how much
the groups truly differ. It also introduces the first genuinely **hard geometry**
in the portfolio.

The model:

```
mu    ~ Normal(5, 5)          # grand mean (hyperprior)
tau   ~ HalfNormal(2)         # between-group SD (hyperprior)
sigma ~ HalfNormal(2)         # within-group noise
theta_j ~ Normal(mu, tau)     # group means
y_ij    ~ Normal(theta_j, sigma)
```

Everything interesting flows from the fact that `theta_j` depends on `tau`.

---

## 2. Takeaways

### 2.1 Partial pooling is the bias–variance trade, made Bayesian

No pooling (per-group means) is unbiased but high-variance — with 4 wells a
group's mean is noisy. Complete pooling (one grand mean) is low-variance but
biased — it erases real differences. Partial pooling interpolates between them, and
**the data choose where** via `tau`. When `tau` is small relative to `sigma/sqrt(n)`
the model pools hard; when group differences dominate, it barely pools. The
shrinkage plot in Step 7 makes this visible: every group is pulled toward `mu_hat`,
and the noisiest groups move most. This is the single most reusable idea in applied
Bayesian statistics.

### 2.2 The natural parameterization is the dangerous one

`theta_j ~ Normal(mu, tau)` is how you'd write the model on paper, and it is
exactly the form that fails. Because each `theta_j`'s spread *is* `tau`, the joint
posterior of `(log tau, theta_j)` is **Neal's funnel**: wide at large `tau`,
pinching to a sharp neck as `tau -> 0`. NUTS picks one step size for the whole
space; that step is too big for the neck (it diverges) and too small for the mouth
(it crawls). The cure is the **non-centered** form `theta_j = mu + tau*z_j`,
`z_j ~ Normal(0,1)`: now the sampled quantity `z_j` has a fixed unit-Normal
geometry independent of `tau`, and the neck vanishes. Same model, same posterior,
radically different sampling geometry.

### 2.3 Divergences are data, not noise

A divergence is the integrator reporting "I could not follow the trajectory here".
In a funnel they cluster in the small-`tau` neck — the very region that controls
how much you pool. Ignoring them does not lose precision uniformly; it **biases
`tau` upward** (the sampler avoids the region it cannot enter) and therefore biases
shrinkage downward. The energy plot and the divergence-highlighted pairs plot turn
this abstract warning into a picture you can act on.

### 2.4 Scale parameters in hierarchical models are prior-sensitive

The prior-sensitivity run was the cleanest demonstration of a rule that does not
hold in flat models: with few groups, **`tau` is genuinely prior-sensitive** while
`mu` is not. The grand mean barely moved across three priors (spread 0.009); `tau`
swung by 0.167 and the tight prior biased it toward complete pooling. There are
only 12 "observations" (group means) informing `tau` — the prior is not outvoted
the way it was at N=80 in Project 01.

---

## 3. Surprises & failures encountered while building

### 3.1 The funnel is subtle at modest `tau`

With `tau_true = 0.8` and `target_accept=0.9`, the *centered* model produced only a
handful of divergences (~3), not a catastrophe — easy to dismiss. To make the
pitfall pedagogically clear in the broken notebook I had to *combine* the centered
parameterization with a low `target_accept=0.8`. The lesson for builders: the
funnel's severity scales with how small `tau` can get relative to the data's
constraint; a benign-looking divergence count can still signal a biased `tau`. Do
not calibrate "is this a problem?" by the raw count alone — look at *where* the
divergences land.

### 3.2 Hierarchical SBC is expensive

SBC here refits the model 40 times. Even with 1 chain, 400 tune, and 200 draws,
the full run flirts with the time budget; the first attempt at 60 simulations
timed out. The fix was to drop to 40 simulations and `compute_convergence_checks=
False`. The deeper lesson: SBC for hierarchical models is genuinely costly, so you
trade resolution for feasibility and read the histogram as "no detectable problem"
rather than a high-precision certificate.

### 3.3 Vague priors bite during SBC, not just inference

Drawing `tau* ~ HalfNormal(10)`-style values from a wide prior during SBC
occasionally produced extreme simulated datasets that triggered numerical overflow
warnings in the mass-matrix dot product. The model still recovered, but it was a
reminder that a prior you would never *want* operationally still gets exercised by
SBC's prior draws — another argument for weakly-informative scale priors.

### 3.4 `mu`'s SBC p-value looked borderline

`mu` came back at p=0.067 — uniform by the alpha=0.01 gate, but lower than `tau`'s
0.534. With only 40 sims and 10 bins the test has little power, so this is
expected fluctuation, not miscalibration. The takeaway is to resist over-reading a
single SBC p-value: it is a falsification test, and "did not reject" is the most it
can say.

---

## 4. How this generalizes

| Skill learned here | Where it returns |
|---|---|
| Partial pooling / shrinkage | Every hierarchical model: varying intercepts (P10), varying slopes (P11), and any grouped GLM. |
| Non-centered reparameterization | The default fix for *any* funnel — P10, P11, and every multilevel model with a scale parameter. |
| Energy plot + divergence pairs plot | The standard hierarchical diagnostic toolkit from here on. |
| Scale-parameter prior sensitivity | Critical wherever a variance is weakly identified (few groups, LKJ scales in P11, measurement-error SD in P12). |
| Reading SBC under a compute budget | Applies to every expensive model where full SBC is impractical. |

The move from one parameter (P01) to a population of exchangeable parameters (P09)
is the conceptual hinge of the whole portfolio. Master non-centering and shrinkage
here and the later hierarchical models are variations on a theme.

---

## 5. Concrete next experiments (for the reader)

- Re-run the broken notebook's centered model across `target_accept` in
  {0.8, 0.9, 0.95, 0.99} and plot divergences vs target. Watch the band-aid work
  partially — and never as well as non-centering.
- Shrink `tau_true` toward 0.2 in `generate_data.py` and refit *centered*. The
  funnel sharpens and divergences explode — the clearest way to *feel* the geometry.
- Add a 13th group with a single observation and watch it shrink almost entirely to
  `mu_hat`: partial pooling's behavior in the small-n limit.
- Replace the Normal population with Student-t and compare LOO when one group is an
  outlier (the rubric extension).
