#!/usr/bin/env python3
"""Build the Week-8 Midterm Exam (covers Weeks 1-7) for "Causal Inference in
Practice", in the same visual style as the weekly self-study packets.

Produces two documents in ``Causal_Inference_Course/Assessments/``:

    Midterm_Exam_Weeks_1-7.docx            — the exam students take
    Midterm_Exam_Weeks_1-7_SOLUTIONS.docx  — the same exam with model answers

Both are generated from a single in-file question bank so the exam and its
solutions can never drift apart. Run:

    python build_midterm.py

This script imports the low-level styling helpers from ``coursegen.packet`` so
the exam matches the course look (banner, h1/h2, callouts, tables, code blocks).
It does NOT touch any existing course file.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # Causal_Inference_Course/
OUT_DIR = os.path.join(ROOT, "Assessments")

sys.path.insert(0, HERE)
from coursegen import packet as P                 # noqa: E402
from coursegen import theme                       # noqa: E402
from docx import Document                         # noqa: E402

# ---------------------------------------------------------------------------
# Exam metadata
# ---------------------------------------------------------------------------
EXAM_TITLE = "Midterm Exam"
SUBTITLE = "Weeks 1–7 — Foundations & Adjustment for Confounding"
DURATION_MIN = 90
WEIGHT_PCT = 20
TOTAL_POINTS = 100

INSTRUCTIONS = [
    [("Time: ", {"bold": True}),
     (f"{DURATION_MIN} minutes. ", {}),
     ("Total: ", {"bold": True}),
     (f"{TOTAL_POINTS} points (worth {WEIGHT_PCT}% of the course grade). "
      "Point values are shown beside each question; budget roughly one minute "
      "per point.", {})],
    [("Closed book, ", {"bold": True}),
     ("with one exception: you may bring ", {}),
     ("a single one-sided page of handwritten notes", {"bold": True}),
     (". A basic or scientific calculator is allowed; phones and laptops are "
      "not.", {})],
    [("Show your work. ", {"bold": True}),
     ("For any numerical answer, write the expression you evaluate, not just "
      "the final number — partial credit follows the reasoning.", {})],
    [("State your assumptions. ", {"bold": True}),
     ("Whenever you claim an estimate is causal, name the identifying "
      "assumptions you are relying on (e.g. exchangeability / no unmeasured "
      "confounding, positivity, SUTVA, consistency). Unstated assumptions cost "
      "points.", {})],
    [("Notation. ", {"bold": True}),
     ("Y is the outcome, T (or A) the treatment/exposure, X the covariates; "
      "Y(1), Y(0) are potential outcomes; e(X) = P(T = 1 | X) is the "
      "propensity score. do(·) denotes Pearl's intervention operator.", {})],
    [("Be concise. ", {"bold": True}),
     ("Two or three precise sentences usually earn full marks on a "
      "short-answer part; long essays do not earn extra credit.", {})],
]

# Section -> points, for the cover-page summary and sanity checks.
SECTION_POINTS = [
    ("A", "Conceptual foundations", 18),
    ("B", "Causal graphs (DAGs)", 18),
    ("C", "Potential outcomes & estimands", 16),
    ("D", "Randomized experiments & A/B testing", 16),
    ("E", "Regression & adjustment", 14),
    ("F", "Matching, propensity scores & weighting", 18),
]

# ---------------------------------------------------------------------------
# Question bank.
#
# Each question is a dict:
#   q       : int  question number (continuous across the whole exam)
#   pts     : int  point value
#   title   : str | list  the prompt headline (bold), passed to P.numbered
#   parts   : list of dicts, each {label, pts, prompt(list-of-paras), answer}
#             - prompt: list of paragraphs; each paragraph is a segment list or str
#             - answer: list of bullet segment-lists (model answer)
#   tables  : optional list of (caption, headers, rows) rendered after the stem
#   stem    : optional list of paragraphs shown before the parts
# ---------------------------------------------------------------------------

def seg(s):
    """Convenience: wrap a plain string as a one-segment paragraph."""
    return s


QUESTIONS = [
    # ----- SECTION A : conceptual foundations ------------------------------
    {
        "section": "A",
        "q": 1, "pts": 10,
        "title": "Prediction vs. intervention, and the do-operator",
        "stem": [
            [("A hospital's analytics team finds that, in their records, "
              "patients who receive a particular antibiotic have ", {}),
             ("higher", {"italic": True}),
             (" 30-day mortality than patients who do not. A vendor proposes a "
              "model that predicts mortality very accurately from the chart, "
              "including the antibiotic indicator.", {})],
        ],
        "parts": [
            {"label": "(a)", "pts": 4,
             "prompt": [[("Explain the difference between the predictive "
                          "quantity P(Y = 1 | T = 1) and the interventional "
                          "quantity P(Y = 1 | do(T = 1)). Why can the vendor's "
                          "model be excellent at the first while saying nothing "
                          "reliable about the second?", {})]],
             "answer": [
                 [("P(Y|T=1) is the distribution of the outcome among the "
                   "subpopulation that was observed to receive the antibiotic — "
                   "a property of how the data were generated, confounding and "
                   "selection included.", {})],
                 [("P(Y|do(T=1)) is the distribution we would see if we "
                   "intervened and set treatment to 1 for everyone, breaking the "
                   "arrows from causes of T into T (a property of a "
                   "hypothetical world we may never have observed).", {})],
                 [("The model learns the conditional (observational) "
                   "association, so it can be highly accurate predictively yet "
                   "estimate the wrong thing for a decision: here, sicker "
                   "patients are the ones given the antibiotic, so the "
                   "observed association is confounded by indication.", {})],
             ]},
            {"label": "(b)", "pts": 3,
             "prompt": [[("Name the phenomenon that most plausibly produces the "
                          "positive antibiotic–mortality association in the "
                          "records, and explain in one sentence why it does not "
                          "imply the drug is harmful.", {})]],
             "answer": [
                 [("Confounding by indication: severity of illness causes both "
                   "the prescription and death.", {})],
                 [("Severity is a common cause, so it opens a non-causal "
                   "(back-door) path T <- severity -> Y; the association mixes "
                   "the drug's effect with the effect of being sicker, so a "
                   "positive crude association is consistent with a zero or even "
                   "protective causal effect.", {})],
             ]},
            {"label": "(c)", "pts": 3,
             "prompt": [[("State, in one sentence each, the kind of study or "
                          "analysis that would let the team estimate the "
                          "interventional quantity, and the single most "
                          "important assumption it would rely on.", {})]],
             "answer": [
                 [("A randomized trial of the antibiotic (or, with "
                   "observational data, an adjustment / weighting analysis on "
                   "the measured confounders) targets do(T).", {})],
                 [("The key assumption is no unmeasured confounding / "
                   "conditional exchangeability — randomization guarantees it by "
                   "design; the observational route only if all common causes "
                   "(notably severity) are measured and adjusted for, plus "
                   "positivity and SUTVA.", {})],
             ]},
        ],
    },
    {
        "section": "A",
        "q": 2, "pts": 8,
        "title": "The three elementary structures",
        "stem": [
            [("Causal effects flow through chains, forks, and colliders. "
              "Consider three measured variables A, B, C.", {})],
        ],
        "parts": [
            {"label": "(a)", "pts": 6,
             "prompt": [[("For each of the three structures below, state "
                          "whether A and C are marginally (unconditionally) "
                          "associated, and whether conditioning on B "
                          "(the middle variable) creates or removes "
                          "association. Fill in the logic for all three:", {})],
                        [("  (i) Chain  A → B → C    (ii) Fork  A ← B → C    "
                          "(iii) Collider  A → B ← C", {"font": theme.FONT_MONO,
                                                        "size": 10})]],
             "answer": [
                 [("Chain A→B→C: A and C are associated marginally; "
                   "conditioning on the mediator B blocks the path and removes "
                   "the association (A ⫫ C | B).", {})],
                 [("Fork A←B→C: A and C are associated marginally (common cause "
                   "B); conditioning on the confounder B blocks the path and "
                   "removes the association (A ⫫ C | B).", {})],
                 [("Collider A→B←C: A and C are NOT associated marginally "
                   "(path is blocked by the collider); conditioning on the "
                   "collider B (or its descendant) OPENS the path and creates a "
                   "spurious association.", {})],
             ]},
            {"label": "(b)", "pts": 2,
             "prompt": [[("Which one of the three is the reason that "
                          '"controlling for more variables" is not always '
                          "safer? Answer in one sentence.", {})]],
             "answer": [
                 [("The collider: adjusting for a collider (or a descendant of "
                   "one) introduces collider/selection bias, so adding controls "
                   "can create bias rather than remove it.", {})],
             ]},
        ],
    },

    # ----- SECTION B : DAGs ------------------------------------------------
    {
        "section": "B",
        "q": 3, "pts": 18,
        "title": "Reading a DAG: paths, blocking, and a valid adjustment set",
        "stem": [
            [("A team studies the effect of a job-training program ", {}),
             ("T", {"bold": True}),
             (" on later earnings ", {}),
             ("Y", {"bold": True}),
             (". Their assumed DAG has the following directed edges "
              "(arrow = direct cause):", {})],
            [("    W → T      W → Y      T → M → Y      T → Y      "
              "Y → H      M → H", {"font": theme.FONT_MONO, "size": 10})],
            [("Here W = prior work history (a common cause), M = skills gained "
              "during the program (a mediator), H = a post-program "
              "certification exam score, and there is a direct effect T → Y.", {})],
        ],
        "parts": [
            {"label": "(a)", "pts": 5,
             "prompt": [[("List every path (causal and non-causal) between T "
                          "and Y. For each, say whether it is a directed/causal "
                          "path or a back-door path.", {})]],
             "answer": [
                 [("T → Y  —  directed (causal), the direct effect.", {})],
                 [("T → M → Y  —  directed (causal), through the mediator.", {})],
                 [("T ← W → Y  —  back-door path through the common cause W "
                   "(non-causal).", {})],
                 [("T → M → H ← Y is a path that reaches Y but ends by pointing "
                   "into Y’s descendant H; the standard back-door paths to enumerate "
                   "for confounding are the three above. H is a collider on "
                   "M → H ← Y and is closed unless we condition on it.", {})],
             ]},
            {"label": "(b)", "pts": 4,
             "prompt": [[("With the empty conditioning set (adjust for "
                          "nothing), classify each path in (a) as open or "
                          "blocked. Is the crude T–Y association equal to the "
                          "total causal effect? Why or why not?", {})]],
             "answer": [
                 [("Empty set: T → Y open; T → M → Y open; T ← W → Y open "
                   "(no collider on it, nothing blocks it).", {})],
                 [("The collider path through H is blocked because H is an "
                   "uncontrolled collider.", {})],
                 [("The crude association does NOT equal the total effect: the "
                   "back-door path T ← W → Y is open, so the association is "
                   "confounded by W.", {})],
             ]},
            {"label": "(c)", "pts": 4,
             "prompt": [[("Give a valid back-door adjustment set for the "
                          "TOTAL effect of T on Y, and justify it with the "
                          "back-door criterion. Explain why you must NOT put "
                          "the mediator M in the set if the total effect is the "
                          "target.", {})]],
             "answer": [
                 [("Adjust for {W}. It blocks the only back-door path "
                   "(T ← W → Y) and contains no descendant of T, satisfying the "
                   "back-door criterion.", {})],
                 [("Do not include M: M lies on the causal path T → M → Y, so "
                   "conditioning on it blocks part of the effect we want — that "
                   "is over-control / mediation bias, leaving only the direct "
                   "effect rather than the total effect.", {})],
             ]},
            {"label": "(d)", "pts": 5,
             "prompt": [[("Identify the collider in this graph and explain "
                          "what goes wrong if an analyst, trying to "
                          '"control for everything observable", adds it to '
                          "the adjustment set {W, ...}. Name the bias.", {})]],
             "answer": [
                 [("H is a collider: M → H ← Y (and T → M → H, Y → H).", {})],
                 [("Conditioning on H opens the path M → H ← Y, inducing a "
                   "spurious association between M (a descendant of T) and Y; "
                   "this is collider / selection bias (also called "
                   "M-bias-style over-adjustment).", {})],
                 [("Because H is a descendant of both T (via M) and Y, "
                   "adjusting for it also violates the back-door criterion and "
                   "biases the estimated effect of T — controlling for it makes "
                   "the estimate worse, not safer.", {})],
             ]},
        ],
    },

    # ----- SECTION C : potential outcomes & estimands ----------------------
    {
        "section": "C",
        "q": 4, "pts": 16,
        "title": "Estimands and their identifying assumptions",
        "stem": [
            [("A city offers an optional after-school tutoring program to "
              "8th graders. The district wants to know its effect on a "
              "standardized math score Y. Let T = 1 if a student enrolls. "
              "Potential outcomes are Y(1) and Y(0).", {})],
        ],
        "parts": [
            {"label": "(a)", "pts": 4,
             "prompt": [[("Write the ATE, the ATT, and a CATE for "
                          "first-generation students, each as an expectation "
                          "of potential outcomes. State in one phrase the "
                          "policy question each one answers.", {})]],
             "answer": [
                 [("ATE = E[Y(1) − Y(0)]  — effect of enrolling everyone vs. "
                   "no one (whole population).", {})],
                 [("ATT = E[Y(1) − Y(0) | T = 1]  — effect among those who "
                   "actually enrolled (e.g., should we keep funding the program "
                   "for its current takers).", {})],
                 [("CATE(x) = E[Y(1) − Y(0) | X = x]; for first-generation "
                   "students, X = first-gen — the effect within that subgroup "
                   "(targeting / equity question).", {})],
             ]},
            {"label": "(b)", "pts": 5,
             "prompt": [[("State the identifying assumptions under which the "
                          "ATE is identified from observational data by "
                          "adjusting for a covariate set X, and write the "
                          "adjustment (g-formula / standardization) "
                          "expression.", {})]],
             "answer": [
                 [("Conditional exchangeability / no unmeasured confounding: "
                   "{Y(1), Y(0)} ⫫ T | X.", {})],
                 [("Positivity: 0 < P(T = 1 | X = x) < 1 for every x with "
                   "positive density.", {})],
                 [("Consistency / SUTVA: the observed Y equals Y(T), no "
                   "interference, one version of treatment.", {})],
                 [("Then ATE = E_X[ E[Y | T = 1, X] − E[Y | T = 0, X] ] "
                   "(standardize the within-stratum contrasts over the "
                   "distribution of X).", {})],
             ]},
            {"label": "(c)", "pts": 4,
             "prompt": [[("Positivity check. Suppose no first-generation "
                          "student with a prior-year score below the 10th "
                          "percentile ever enrolls. Which estimand is "
                          "threatened, and why? What is the honest fix?", {})]],
             "answer": [
                 [("Positivity is violated in that stratum (P(T = 1 | X) = 0): "
                   "there are no enrolled students to estimate Y(1) for.", {})],
                 [("The population ATE is threatened — it would require "
                   "extrapolating Y(1) into a region with no treated support, "
                   "which the data cannot support.", {})],
                 [("Honest fix: redefine the target to the region of common "
                   "support (e.g., estimate the ATT or an ATE restricted to "
                   "strata with overlap) and report the trimmed population, "
                   "rather than extrapolating a model.", {})],
             ]},
            {"label": "(d)", "pts": 3,
             "prompt": [[("SUTVA. Give one concrete, plausible way SUTVA could "
                          "fail in THIS tutoring example, and say which part of "
                          "SUTVA it violates.", {})]],
             "answer": [
                 [("Interference / spillover: tutored students share methods or "
                   "raise the class curve, changing untreated peers' outcomes — "
                   "violates the no-interference part of SUTVA.", {})],
                 [("(Alternatively) multiple versions of treatment: tutoring "
                   "quality varies by tutor, so 'T = 1' is not a single "
                   "well-defined intervention — violates the "
                   "single-version / consistency part.", {})],
             ]},
        ],
    },

    # ----- SECTION D : randomized experiments ------------------------------
    {
        "section": "D",
        "q": 5, "pts": 16,
        "title": "A/B test: power/MDE, variance reduction, and ITT",
        "stem": [
            [("A product team runs a 50/50 A/B test of a checkout redesign. "
              "The outcome is revenue per visitor. They will need power for "
              "the analysis below.", {})],
        ],
        "parts": [
            {"label": "(a)", "pts": 5,
             "prompt": [[("For a two-sided test at level α with power 1 − β, "
                          "comparing two equal-sized groups of n each, the "
                          "minimum detectable effect (MDE) on the difference in "
                          "means is approximately", {})],
                        [("    MDE ≈ (z_{1−α/2} + z_{1−β}) · σ · √(2 / n).",
                          {"font": theme.FONT_MONO, "size": 10})],
                        [("Using z_{0.975} = 1.96 and z_{0.80} = 0.84, by what "
                          "factor must n increase to detect an effect HALF as "
                          "large, holding α, β, σ fixed? Show the reasoning.", {})]],
             "answer": [
                 [("MDE ∝ 1/√n, so to halve the MDE you need √n to double, "
                   "i.e. n must increase by a factor of 2² = 4.", {})],
                 [("Quantitatively: MDE_2/MDE_1 = √(n_1/n_2) = 1/2 ⇒ "
                   "n_2 = 4·n_1. (The constant (1.96 + 0.84) = 2.8 cancels.)", {})],
             ]},
            {"label": "(b)", "pts": 5,
             "prompt": [[("CUPED. The team has each visitor's PRE-experiment "
                          "spend, which correlates ρ = 0.6 with the outcome. "
                          "CUPED adjusts the outcome using this covariate. By "
                          "what factor does the variance of the estimated effect "
                          "shrink, and hence by what factor can the required "
                          "sample size shrink for the same power? "
                          "(Var reduction factor = 1 − ρ².)", {})]],
             "answer": [
                 [("Variance is multiplied by (1 − ρ²) = 1 − 0.36 = 0.64 — a "
                   "36% reduction in the variance of the effect estimate.", {})],
                 [("Required n scales with the variance for fixed power, so n "
                   "can shrink by the same factor: n_new ≈ 0.64·n_old "
                   "(about a 36% smaller sample for the same MDE/power).", {})],
                 [("Why it is valid: the pre-period covariate is measured before "
                   "randomization, so it cannot be affected by treatment — "
                   "adjusting for it removes noise without introducing bias.", {})],
             ]},
            {"label": "(c)", "pts": 6,
             "prompt": [[("Noncompliance. 20% of visitors assigned to the new "
                          "checkout fall back to the old one (the assignment "
                          "did not 'take'); the control group all see the old "
                          "one. Define the ITT and the per-protocol estimates "
                          "here, say which one randomization protects, and "
                          "explain the direction of bias if the fallback "
                          "visitors are systematically different (e.g., "
                          "mobile users on poor connections).", {})]],
             "answer": [
                 [("ITT (intention-to-treat): compare outcomes by ASSIGNED "
                   "group regardless of which checkout they actually used — the "
                   "effect of being offered the redesign.", {})],
                 [("Per-protocol: compare those who actually used the new "
                   "checkout vs. controls (dropping/exposing only compliers).", {})],
                 [("Randomization protects the ITT: assignment is random, so "
                   "the ITT contrast is unconfounded by design.", {})],
                 [("Per-protocol breaks randomization: keeping only compliers "
                   "conditions on a post-randomization variable. If fallback "
                   "users are systematically worse (poor-connection mobile "
                   "users with lower revenue), dropping them leaves a "
                   "healthier-looking treated group, biasing the per-protocol "
                   "estimate away from null (overstating the redesign's "
                   "benefit). ITT remains valid but dilutes toward the null.", {})],
             ]},
        ],
    },

    # ----- SECTION E : regression & adjustment -----------------------------
    {
        "section": "E",
        "q": 6, "pts": 14,
        "title": "Choosing controls and the Table 2 fallacy",
        "stem": [
            [("A researcher regresses an outcome Y on a treatment T and wants "
              "to decide which of several variables to include as controls. "
              "Using the SAME DAG as Question 3 "
              "(W → T, W → Y, T → M → Y, T → Y, Y → H, M → H), classify each "
              "candidate.", {})],
        ],
        "tables": [
            ("Candidate controls (total effect of T on Y is the target)",
             ["Variable", "Role w.r.t. T → Y", "Include for the total effect?"],
             [
                 ["W (work history)", "Confounder (common cause of T and Y)",
                  "Yes — adjusting removes back-door bias"],
                 ["M (skills gained)", "Mediator (on the causal path T→M→Y)",
                  "No — blocks part of the total effect (over-control)"],
                 ["H (exam score)", "Collider / descendant of Y and M",
                  "No — opens a path and induces selection bias"],
                 ["Z (a pre-T variable affecting only Y)",
                  "Neutral / precision covariate (predicts Y, not T)",
                  "Optional — harmless, often improves precision"],
             ]),
        ],
        "parts": [
            {"label": "(a)", "pts": 8,
             "prompt": [[("Reproduce the right-most column of the table above "
                          "in your booklet (Include? Yes/No/Optional) and give "
                          "a one-clause reason for each of W, M, H, Z.", {})]],
             "answer": [
                 [("W — Yes: it is a confounder; adjusting blocks the back-door "
                   "path T ← W → Y.", {})],
                 [("M — No: it is a mediator; controlling for it removes the "
                   "indirect part of the total effect (leaves only the direct "
                   "effect).", {})],
                 [("H — No: it is a collider / descendant of the outcome; "
                   "controlling for it opens M → H ← Y and induces selection "
                   "bias.", {})],
                 [("Z — Optional: a pre-treatment predictor of Y only; it does "
                   "not affect bias but reduces residual variance, improving "
                   "precision (a good 'neutral' control).", {})],
             ]},
            {"label": "(b)", "pts": 6,
             "prompt": [[("State the Table 2 fallacy. The researcher's "
                          "regression of Y on (T, W) reports a coefficient on W "
                          "as well as on T, and the write-up interprets the W "
                          "coefficient as 'the causal effect of work history.' "
                          "Explain why that interpretation is unjustified even "
                          "though the SAME model gives a valid estimate of the "
                          "effect of T.", {})]],
             "answer": [
                 [("The Table 2 fallacy: reading every coefficient in a single "
                   "adjusted model as a causal effect, when the model was only "
                   "designed to identify ONE of them (the effect of T).", {})],
                 [("The set {W} satisfies the back-door criterion for T → Y, so "
                   "the T coefficient is a valid (conditional) effect of T. But "
                   "the W coefficient is the effect of W holding T fixed — and "
                   "the model does not adjust for W's own confounders, nor is T "
                   "(a mediator/descendant of W via T → Y) an appropriate thing "
                   "to hold fixed when estimating W's total effect.", {})],
                 [("So the W coefficient mixes W's direct effect with bias from "
                   "uncontrolled confounding of W and from conditioning on a "
                   "mediator of W; it should not be reported as a causal "
                   "effect of work history.", {})],
             ]},
        ],
    },

    # ----- SECTION F : matching / PS / weighting ---------------------------
    {
        "section": "F",
        "q": 7, "pts": 10,
        "title": "Propensity scores: the balancing property and overlap",
        "parts": [
            {"label": "(a)", "pts": 4,
             "prompt": [[("State the balancing property of the propensity score "
                          "e(X) = P(T = 1 | X). What does it let you do that "
                          "matching on the full covariate vector X does not, "
                          "and why is that practically useful in high "
                          "dimensions?", {})]],
             "answer": [
                 [("Balancing property: T ⫫ X | e(X) — conditional on the "
                   "(true) propensity score, treatment is independent of X, so "
                   "treated and control units with the same e(X) have the same "
                   "covariate distribution on average.", {})],
                 [("It reduces a high-dimensional matching problem to balancing "
                   "on a single scalar e(X) instead of the full vector X.", {})],
                 [("Practically useful because exact/near matching on many "
                   "covariates suffers the curse of dimensionality (few exact "
                   "matches); the scalar score makes overlap and balance "
                   "tractable.", {})],
             ]},
            {"label": "(b)", "pts": 3,
             "prompt": [[("If, after estimating e(X), you adjust/condition on "
                          "e(X) and check covariate balance, what does GOOD "
                          "balance buy you, and what does it NOT buy you? "
                          "(One sentence each.)", {})]],
             "answer": [
                 [("Good balance buys you exchangeability ON THE MEASURED "
                   "covariates — the comparison mimics a randomized one with "
                   "respect to X.", {})],
                 [("It does NOT buy you protection against unmeasured "
                   "confounding: balancing measured X says nothing about "
                   "variables not in X.", {})],
             ]},
            {"label": "(c)", "pts": 3,
             "prompt": [[("An analyst finds that treated units have estimated "
                          "propensity scores in [0.4, 0.99] while controls span "
                          "[0.01, 0.6]. What estimand is well supported, and "
                          "what should they do about the non-overlapping "
                          "regions?", {})]],
             "answer": [
                 [("Overlap is only in roughly [0.4, 0.6]; outside it one arm is "
                   "essentially absent, so positivity is weak.", {})],
                 [("The ATT is better supported than the ATE if controls exist "
                   "for the treated region; the clean fix is to TRIM to the "
                   "common-support region and report the estimand on that "
                   "trimmed population (or use overlap weights), not to "
                   "extrapolate.", {})],
             ]},
        ],
    },
    {
        "section": "F",
        "q": 8, "pts": 8,
        "title": "Numeric: IPW by hand, and the doubly-robust idea",
        "stem": [
            [("Six patients are observed. T is treatment, Y the outcome, and "
              "e = P(T = 1 | X) is the (given, correctly specified) propensity "
              "score for each patient. Use the stabilized / Hájek IPW "
              "estimator: weight treated units by 1/e and controls by "
              "1/(1 − e), then take the weighted mean outcome in each arm and "
              "subtract.", {})],
        ],
        "tables": [
            ("Patient-level data",
             ["Patient", "T", "Y", "e = P(T=1|X)"],
             [
                 ["1", "1", "10", "0.50"],
                 ["2", "1", "14", "0.25"],
                 ["3", "1", "8", "0.50"],
                 ["4", "0", "6", "0.50"],
                 ["5", "0", "4", "0.75"],
                 ["6", "0", "2", "0.50"],
             ]),
        ],
        "parts": [
            {"label": "(a)", "pts": 2,
             "prompt": [[("Write the IPW weight for each patient.", {})]],
             "answer": [
                 [("Treated (weight 1/e): P1 = 1/0.50 = 2, P2 = 1/0.25 = 4, "
                   "P3 = 1/0.50 = 2.", {})],
                 [("Control (weight 1/(1−e)): P4 = 1/0.50 = 2, "
                   "P5 = 1/0.25 = 4, P6 = 1/0.50 = 2.", {})],
             ]},
            {"label": "(b)", "pts": 4,
             "prompt": [[("Compute the weighted mean outcome in the treated arm "
                          "and in the control arm (Hájek), and report the IPW "
                          "estimate of the ATE. Show the arithmetic.", {})]],
             "answer": [
                 [("Treated: Σwy = 2·10 + 4·14 + 2·8 = 20 + 56 + 16 = 92; "
                   "Σw = 2 + 4 + 2 = 8; μ̂₁ = 92/8 = 11.5.", {})],
                 [("Control: Σwy = 2·6 + 4·4 + 2·2 = 12 + 16 + 4 = 32; "
                   "Σw = 2 + 4 + 2 = 8; μ̂₀ = 32/8 = 4.0.", {})],
                 [("IPW ATE = 11.5 − 4.0 = 7.5.", {"bold": True})],
             ]},
            {"label": "(c)", "pts": 2,
             "prompt": [[("The NAÏVE difference in raw group means is "
                          "10.67 − 4.0 = 6.67. In one or two sentences, explain "
                          "why a doubly-robust (AIPW) estimator is preferred "
                          "over plain IPW in practice — what 'double' "
                          "protection does it give?", {})]],
             "answer": [
                 [("Reweighting up-weights patient 2 (low e), pulling the "
                   "treated mean above the naïve 10.67 to correct for "
                   "under-represented covariate strata — hence 7.5 vs. 6.67.", {})],
                 [("A doubly-robust / AIPW estimator combines an outcome model "
                   "with the propensity model and is consistent if EITHER model "
                   "is correctly specified (not necessarily both); it also "
                   "tends to be more stable when some weights are large.", {})],
             ]},
        ],
    },
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _points_label(pts: int) -> list:
    return [(f"   [{pts} pts]", {"bold": True, "color": theme.AMBER})]


def render_cover(doc, *, solutions: bool) -> None:
    P.banner(doc, "8", EXAM_TITLE + (" — Solutions" if solutions else ""))
    P.body(doc, [(SUBTITLE, {"bold": True, "color": theme.NAVY})])
    P.body(doc, [("Graduate course: ", {}),
                 (theme.COURSE_TITLE, {"italic": True}),
                 (f".   Covers Weeks 1–7.   {DURATION_MIN} minutes.   "
                  f"{TOTAL_POINTS} points = {WEIGHT_PCT}% of grade.", {})],
           italic=False)

    if solutions:
        P.callout(doc, "Instructor solution key",
                  [[("Model answers and the point breakdown follow each "
                     "question. Award partial credit for correct reasoning even "
                     "when the final number differs; deduct for unstated "
                     "identifying assumptions where the question asks for "
                     "them.", {})]],
                  color=theme.RED)

    P.h1(doc, "Instructions")
    for ins in INSTRUCTIONS:
        P.bullet(doc, ins)

    P.h1(doc, "How the points are distributed")
    P.table(doc,
            ["Section", "Topic", "Points"],
            [[s, t, str(p)] for (s, t, p) in SECTION_POINTS]
            + [["", "Total", str(sum(p for *_, p in SECTION_POINTS))]])


def render_question(doc, qd: dict, *, solutions: bool) -> None:
    # Question headline with point value.
    title = qd["title"]
    headline = (title if isinstance(title, list)
                else [(title, {"bold": True})]) + _points_label(qd["pts"])
    P.numbered(doc, qd["q"], headline)

    for para in qd.get("stem", []):
        P.body(doc, para)

    for tb in qd.get("tables", []):
        caption, headers, rows = tb
        if caption:
            P.body(doc, [(caption, {"italic": True, "color": theme.GREY})],
                   space=2)
        P.table(doc, headers, rows)

    for part in qd["parts"]:
        # part prompt: bold label + point chip, then prompt paragraphs
        first = part["prompt"][0]
        first_segs = ([(first, {})] if isinstance(first, str) else list(first))
        lead = ([(part["label"] + " ", {"bold": True, "color": theme.BLUE})]
                + first_segs + _points_label(part["pts"]))
        P.body(doc, lead, space=3)
        for extra in part["prompt"][1:]:
            P.body(doc, extra, space=3)

        if solutions:
            P.body(doc, [("Model answer:", {"bold": True,
                                            "color": theme.GREEN})], space=2)
            for ans in part["answer"]:
                P.bullet(doc, ans)
        else:
            # leave a little breathing room / answer space cue
            P.body(doc, [("", {})], space=10)


def build(out_path: str, *, solutions: bool) -> str:
    doc = Document()
    P._setup(doc)
    render_cover(doc, solutions=solutions)

    current_section = None
    for qd in QUESTIONS:
        sec = qd["section"]
        if sec != current_section:
            current_section = sec
            label = next(t for (s, t, _) in SECTION_POINTS if s == sec)
            pts = next(p for (s, _, p) in SECTION_POINTS if s == sec)
            P.h1(doc, f"Section {sec} — {label}  ({pts} points)")
        render_question(doc, qd, solutions=solutions)

    # closing line
    P.h1(doc, "End of exam")
    if solutions:
        P.body(doc, [("Total: ", {"bold": True}),
                     (f"{TOTAL_POINTS} points across {len(QUESTIONS)} "
                      "questions. Reasoning-based partial credit throughout.",
                      {})])
    else:
        P.body(doc, [("Check that you have answered every part. Re-read any "
                      "question where you did not state the identifying "
                      "assumptions. Good luck.", {"italic": True})])

    doc.save(out_path)
    return out_path


def _sanity_check_points() -> None:
    """Fail loudly if the bank does not sum to the advertised totals."""
    bank_total = sum(q["pts"] for q in QUESTIONS)
    assert bank_total == TOTAL_POINTS, (
        f"question points sum to {bank_total}, expected {TOTAL_POINTS}")
    section_total = sum(p for *_, p in SECTION_POINTS)
    assert section_total == TOTAL_POINTS, (
        f"section points sum to {section_total}, expected {TOTAL_POINTS}")
    for q in QUESTIONS:
        part_sum = sum(p["pts"] for p in q["parts"])
        assert part_sum == q["pts"], (
            f"Q{q['q']} parts sum to {part_sum}, header says {q['pts']}")
        sec_pts = next(p for (s, _, p) in SECTION_POINTS if s == q["section"])
        # (section totals checked in aggregate below)
    # per-section aggregate
    from collections import defaultdict
    agg = defaultdict(int)
    for q in QUESTIONS:
        agg[q["section"]] += q["pts"]
    for (s, _, p) in SECTION_POINTS:
        assert agg[s] == p, f"Section {s} questions sum to {agg[s]}, table says {p}"


def main() -> None:
    _sanity_check_points()
    os.makedirs(OUT_DIR, exist_ok=True)
    exam = build(os.path.join(OUT_DIR, "Midterm_Exam_Weeks_1-7.docx"),
                 solutions=False)
    sols = build(os.path.join(OUT_DIR, "Midterm_Exam_Weeks_1-7_SOLUTIONS.docx"),
                 solutions=True)
    print("Wrote:")
    print("  " + exam)
    print("  " + sols)
    print(f"Bank: {len(QUESTIONS)} questions, "
          f"{sum(q['pts'] for q in QUESTIONS)} points total.")


if __name__ == "__main__":
    main()
