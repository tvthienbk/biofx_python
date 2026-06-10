# One-Pager — How Fast Does the Drug Clear? (Project 19)

**Audience:** a pharmacologist or clinician who wants the drug's clearance and
half-life — with uncertainty — to set a dose, not a modelling tutorial.

## The question

After a single IV dose, how quickly does the drug leave the body, and how big is
the body's apparent "tank" for it? Concretely: the **elimination rate** `k`, the
**volume of distribution** `V`, and the two numbers you actually dose on -- the
**half-life** and the **clearance**.

## What we did

We fit a standard **one-compartment pharmacokinetic model** -- the mechanistic
equation for a drug eliminated at a constant fractional rate -- to noisy blood
concentrations measured at ten timepoints. Bayesian inference returns full
uncertainty on every quantity, not just a best guess.

## What we found

- The elimination rate and volume are recovered close to their true values, with
  tight credible intervals.
- The **half-life** and **clearance** -- the dosing-relevant numbers -- come with
  usable intervals you can carry into a dosing decision.

## The one thing that made it work: the sampling schedule

Separating the two parameters depends entirely on **when** blood is drawn. You
need **early** samples (which fix the starting concentration, hence the volume)
**and** **late** samples (which fix the decay rate). If you only draw late samples,
the model literally cannot tell a large volume with fast clearance from a small
volume with slow clearance -- the two trade off. We verified this failure mode and
its fix. Practical implication: **insist on early draws**, not just a convenient
late-time series.

## A robustness note

Even when the two parameters individually become uncertain, their **product
(clearance)** stays reliable -- so when in doubt, dose on clearance and half-life,
which are the quantities the design constrains best.

## Bottom line

We have defensible, uncertainty-aware estimates of clearance and half-life. Use
them to set the dosing interval and maintenance dose -- and design future studies
with early sampling so the individual parameters stay identifiable.
