# Grading rubric — Project 14 (Hidden Markov Model)

Total: **100 points**, across the 8 workflow steps, plus an extension.

| # | Workflow step | Points | What earns them |
|---|---------------|:------:|-----------------|
| 1 | Problem & data story | 8 | States the HMM generative model; flags 2 states, first-order Markov, time-homogeneity, shared sigma as assumptions. |
| 2 | Model & marginalization | 20 | Correct **forward algorithm** in log space (logsumexp, not max); implemented in `pytensor.scan` + `pm.Potential`; **ordered** emission means to break label symmetry; justified Beta/Normal/HalfNormal priors. |
| 3 | Prior predictive | 8 | Checks the parameter prior (dwell times implied by Beta) is physically plausible. |
| 4 | Inference | 8 | NUTS settings stated; acknowledges per-step scan cost; enough chains for R-hat. |
| 5 | Diagnostics & transition matrix | 16 | R-hat/ESS/divergences; reassembles and reports the recovered transition matrix vs truth. |
| 6 | Posterior predictive | 12 | Simulates trajectories from the posterior; compares occupancy / dwell / emission histogram to data. |
| 7 | Criticism & identifiability | 14 | Reports label-invariant + direction-aware quantities; checks recovery; discusses missing-states / non-exponential dwell times. |
| 8 | Decision & communication | 8 | Translates to occupancy and dwell times a collaborator can use. |
| — | Reproducibility & hygiene | 6 | Fixed seeds; runs top-to-bottom; shared helpers; tight plots. |

**Deductions.** `max` instead of `logsumexp` in the recursion (−10, it is wrong
even if it runs). Unordered means without noticing label switching (−6). Sampling
discrete states with poor mixing instead of marginalizing (−4). Claiming
robustness without the prior sweep (−3).

---

## Open-ended extension prompt

> **Extend to three states and recover the state path.** (a) Generalize the
> forward algorithm to K=3 states with a full 3×3 transition matrix (rows ~
> Dirichlet) and ordered emission means; confirm it still samples and check whether
> LOO / posterior-predictive dwell-time checks prefer K=2 or K=3 on the original
> 2-state data (do you over-fit?). (b) Add the **backward** pass to compute smoothed
> state posteriors P(s_t | y) (forward–backward), and overlay the most-probable
> state path on the data — compare to the true hidden path. (c) Discuss: why is the
> *marginal likelihood* (forward) the right quantity for parameter inference, while
> the *most-probable path* (Viterbi) is the right quantity for state decoding —
> i.e. why mixing them up (Bug 1) is a conceptual error, not just a coding slip?
