# Week 5 — Regression & Adjustment

**Block II — Adjustment for confounding**

What regression can and cannot do for causation — and the precise ways that "controlling for" backfires.

## Contents of this folder

| File | What it is |
|------|------------|
| `Week05_Regression_Adjustment_Self_Study_Packet.docx` | Readings, concept refresher, problem set (+ full solutions), the lab, and a self-check. Work through it after lecture (~5–7 h). |
| `Week05_Regression_Adjustment_Lecture.pptx` | The ~28-slide lecture deck. |
| `Week05_Regression_Adjustment_Practice.ipynb` | Runnable Jupyter notebook: worked examples + graded-style exercises with solutions. All data is simulated with a known ground truth. |

## This week in one sentence

OLS estimates a causal effect only when you condition on the right set of covariates — and 'the right set' is dictated by the causal graph, not by what improves fit, because adjusting for mediators or colliders manufactures bias that wasn't there.

## Deliverable

Problem Set 4 — classify every control (good/bad/collider/neutral/M-bias); Workshop 5 — good & bad controls in code.
