# Week 7 — Weighting & Doubly Robust Estimation

**Block II — Adjustment for confounding**

Inverse-probability weighting, stabilized weights, and estimators that survive one modeling mistake.

## Contents of this folder

| File | What it is |
|------|------------|
| `Week07_Weighting_Doubly_Robust_Estimation_Self_Study_Packet.docx` | Readings, concept refresher, problem set (+ full solutions), the lab, and a self-check. Work through it after lecture (~5–7 h). |
| `Week07_Weighting_Doubly_Robust_Estimation_Lecture.pptx` | The ~32-slide lecture deck. |
| `Week07_Weighting_Doubly_Robust_Estimation_Practice.ipynb` | Runnable Jupyter notebook: worked examples + graded-style exercises with solutions. All data is simulated with a known ground truth. |

## This week in one sentence

Inverse-probability weighting rebuilds a pseudo-population in which treatment is unconfounded, and augmenting it with an outcome model buys you a safety net: the doubly robust estimator stays consistent if EITHER the propensity model OR the outcome model is right — you only need to win one of the two bets.

## Deliverable

Problem Set 5 — weights, overlap, and double robustness; Lab 4 — IPW & AIPW on a confounded cohort.
