# Lessons — Project 05: Binary Outcomes (Logistic Regression)

This is the lessons report for the logistic-GLM project. It records what the
project *teaches*, the surprises met while building and running it, and how the
ideas generalize to every GLM that follows in the portfolio.

---

## 1. What this project is really about

On the surface it fits a logistic regression — alpha, beta, done. The real
subject is the **link function** and the fact that *priors do not mean what you
think once a nonlinearity sits between parameters and data*. Project 01 taught
the eight-step workflow on one parameter with a conjugate check. Project 05 takes
the first real step into regression and immediately breaks a piece of folk
wisdom: "a wide prior is an uninformative prior." Under the logit link that
sentence is false, and the project is built to make the falseness visible.

The eight workflow steps map to artifacts exactly as in Project 01:

1. Data story — `data/generate_data.py` (Bernoulli with logistic link).
2. Model + priors — `model.py` (logit link, `Normal(0,1.5)`).
3. Prior predictive — Step 3 cell, **on the probability scale**.
4. Inference — `model.fit`, NUTS with standardized $x$.
5. Diagnostics — $\hat R$ / ESS / divergences in Step 5.
6. Posterior predictive — `plot_ppc` + a calibration curve.
7. Criticism — recovery vs truth + prior sensitivity.
8. Decision — $P(\beta>0)$ and the $p=0.5$ crossover.

Plus the three correctness artifacts: SBC (`sbc.py`), prior sensitivity
(`prior_sensitivity.py`), and the seeded-bug exercise (`notebook_broken.ipynb`).

---

## 2. Takeaways

### 2.1 "Wide" is not "uninformative" under a link

This is the single most transferable lesson, and it is the Project-01 lesson
("flat is not uninformative") promoted to the regression setting. A
`Normal(0,10)` prior on a logistic coefficient *looks* agnostic on the log-odds
scale. Push it through the sigmoid and the implied probability at the mean
covariate is a U pinned at 0 and 1 — the prior secretly believes the assay is a
near-deterministic switch. `Normal(0,1.5)` instead spreads the implied
probability sensibly around 0.5. The only way to *see* this is to run the prior
predictive check on the **probability** scale. Build that reflex now; every GLM in
the rest of the portfolio depends on it.

### 2.2 A GLM lives on two scales, and you must keep crossing between them

Parameters, priors, and the linear predictor live on the log-odds scale.
Meaning, checks, and decisions live on the probability scale. Almost every
mistake in this project — and all three seeded bugs — is a failure to cross from
one scale to the other at the right moment:

- justifying a prior on the log-odds scale (looks fine, hides the U),
- modeling $p$ directly (skipping the link entirely),
- checking the prior on the log-odds scale (hides the pathology).

### 2.3 Standardizing the covariate is a *sampling* decision, not just tidiness

Centering and scaling $x$ makes $\alpha$ interpretable (log-odds at the mean) and,
just as importantly, decorrelates $\alpha$ from $\beta$ in the posterior. Without
it the posterior is a tilted ridge that NUTS explores inefficiently — higher
$\hat R$, lower ESS. The fix is upstream, in the data representation, not in the
sampler settings.

### 2.4 Separation is the binary-data trap, and the prior is the cure

If a covariate perfectly predicts the outcome, the maximum-likelihood coefficient
runs to $\pm\infty$ and a flat-prior sampler chases it forever. A
weakly-informative prior gently regularizes the estimate to something finite and
sensible. This is a clean example of priors doing real work — not "subjective
contamination" but numerical and inferential stabilization.

### 2.5 Calibration is the PPC that matters for binary data

Individual 0/1 outcomes carry almost no information about fit. The informative
posterior-predictive check bins wells by predicted probability and compares the
observed fraction of 1s to the predicted probability. A well-specified logistic
model tracks the diagonal; an S-shaped departure signals a missing nonlinearity
in $x$ — which is exactly the extension prompt in `rubric.md`.

---

## 3. Surprises & failure modes encountered while building

### 3.1 The vague prior's posterior looked *fine*

The most instructive surprise: in `prior_sensitivity.py`, the `Normal(0,10)`
posterior for $\beta$ is essentially identical to the `Normal(0,1.5)` posterior.
With $N=120$ informative observations the likelihood swamps the prior. It would be
easy to conclude "the wide prior is harmless." The resolution is to separate two
questions: *given these data*, the wide prior is harmless; *as a statement of
prior belief*, it is absurd. Both are true. The danger only materializes when data
are scarce or separation strikes — and that is precisely when you cannot afford a
pathological prior.

### 3.2 SBC can pass even with a bad prior

SBC draws parameters from the prior, so it validates *self-consistency*, not *good
modeling*. A pathological prior can still yield uniform ranks. This sharpened the
division of labor: SBC certifies the sampler/model implementation; the prior
predictive check certifies the prior. Neither substitutes for the other.

### 3.3 The broken notebook's "directly model p" bug is loud, not subtle

Feeding `p = alpha + beta*x` to `Bernoulli` produces out-of-$(0,1)$ probabilities
and the sampler erupts in divergences (or errors outright). This is a *good* bug
for teaching: the failure is dramatic and the diagnostic — "where did the sigmoid
go?" — is memorable.

### 3.4 SBC runtime is dominated by simulation count

The first SBC pass at 80 simulations took ~2.5 minutes. Dropping to 50 brought it
to ~70 seconds with no loss of conclusion (both coefficients still uniform). The
lesson for light-sampling SBC: the number of simulations, not the per-fit draws,
is the runtime knob.

---

## 4. How this generalizes

Every model in the rest of the portfolio is a GLM or a hierarchical GLM, so the
two-scale discipline learned here is reused constantly:

- **Project 06 (Negative-Binomial counts)** uses a **log link**; priors on the
  log-mean scale must be read back as counts, exactly as we read log-odds back as
  probabilities here.
- **Projects 09–11 (hierarchical / varying-slopes logistic)** stack this logit
  model under a hierarchy; the prior-predictive-on-the-response-scale check
  becomes even more important because the implied marginal is a mixture.
- **Project 08 (horseshoe)** puts shrinkage priors on many coefficients; the
  habit of asking "what does this prior imply on the response scale?" carries over
  directly.

The portable rule: **whenever a link function stands between your parameters and
your data, justify priors and run prior predictive checks on the response scale,
never on the linear-predictor scale.**
