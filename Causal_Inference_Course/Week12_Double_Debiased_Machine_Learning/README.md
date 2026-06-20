# Week 12 — Double / Debiased Machine Learning

**Block IV — Modern methods & application**

Use flexible ML for the nuisance parts without letting it bias the effect you care about.

## Contents of this folder

| File | What it is |
|------|------------|
| `Week12_Double_Debiased_Machine_Learning_Self_Study_Packet.docx` | Readings, concept refresher, problem set (+ full solutions), the lab, and a self-check. Work through it after lecture (~5–7 h). |
| `Week12_Double_Debiased_Machine_Learning_Lecture.pptx` | The ~33-slide lecture deck. |
| `Week12_Double_Debiased_Machine_Learning_Practice.ipynb` | Runnable Jupyter notebook: worked examples + graded-style exercises with solutions. All data is simulated with a known ground truth. |

## This week in one sentence

Double/debiased ML lets you throw a flexible learner at the nuisance functions — the parts of the model you do not care about — and still get an unbiased, normally-distributed estimate of the one effect you do, by combining a Neyman-orthogonal score with cross-fitting so that the learner's regularization bias and overfitting cannot leak into the target parameter.

## Deliverable

Concept Set 12 — orthogonality & cross-fitting; Lab 9 — partially-linear DML from scratch on high-dimensional confounding.
