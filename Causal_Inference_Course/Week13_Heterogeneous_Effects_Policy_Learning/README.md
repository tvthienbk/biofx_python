# Week 13 — Heterogeneous Effects & Policy Learning

**Block IV — Modern methods & application**

Move from "does it work on average?" to "for whom — and what should we do about it?"

## Contents of this folder

| File | What it is |
|------|------------|
| `Week13_Heterogeneous_Effects_Policy_Learning_Self_Study_Packet.docx` | Readings, concept refresher, problem set (+ full solutions), the lab, and a self-check. Work through it after lecture (~5–7 h). |
| `Week13_Heterogeneous_Effects_Policy_Learning_Lecture.pptx` | The ~30-slide lecture deck. |
| `Week13_Heterogeneous_Effects_Policy_Learning_Practice.ipynb` | Runnable Jupyter notebook: worked examples + graded-style exercises with solutions. All data is simulated with a known ground truth. |

## This week in one sentence

The average treatment effect can hide enormous variation across people; this week we estimate the conditional effect τ(x) = E[Y(1) − Y(0) | X = x] with meta-learners and causal forests, learn how to evaluate those estimates without ground truth, and turn them into a treatment policy that does better than treating everyone or no one.

## Deliverable

Problem Set 7 — CATE, meta-learners, and policy; Lab 10 — CATE & policy learning (T-/S-learners, uplift curves, and an optimal treatment rule).
