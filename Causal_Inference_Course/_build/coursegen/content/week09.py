# -*- coding: utf-8 -*-
"""Week 9 — Regression Discontinuity. Content module (mirrors week01.py)."""

WEEK = {
    "number": 9,
    "slug": "regression_discontinuity",
    "title": "Regression Discontinuity",
    "block": "Block III — Quasi-experimental designs",
    "subtitle": "Just above vs. just below a cutoff is almost a coin flip — so "
                "the cutoff hands you a local experiment.",
    "deliverable": "Lab 6 — simulate a sharp RD, estimate the jump by local "
                   "linear regression, and run the standard validity checks "
                   "(bandwidth, placebo cutoffs, donut-hole, density).",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), concept set (1.5h), lab (2–3h).",
    "one_sentence": "When treatment is decided by whether a running variable "
        "crosses a known cutoff, units just above and just below the cutoff are "
        "comparable, so the jump in the outcome at the cutoff identifies a local "
        "causal effect — provided nothing else jumps there and no one can "
        "precisely manipulate which side they land on.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Distinguish a sharp RD (treatment is a deterministic step at the "
        "cutoff) from a fuzzy RD (the cutoff shifts treatment probability) and "
        "state what each one identifies.",
        "Explain the continuity assumption and the local-randomization intuition "
        "in plain language, and say which estimand RD recovers.",
        "Estimate the discontinuity with local linear regression inside a "
        "bandwidth, and reason about the bias–variance tradeoff in choosing it.",
        "Run the standard validity checks — a McCrary-style density test for "
        "manipulation, placebo cutoffs, and a donut-hole robustness check — and "
        "interpret each result.",
        "Scale a fuzzy-RD reduced form by its first stage (the Wald/IV ratio at "
        "the cutoff) and recover a known treatment effect in simulation.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Angrist & Pischke, Mostly Harmless Econometrics — Chapter 6.",
         "look_for": "the sharp vs. fuzzy RD setup, and exactly what the "
                     "discontinuity at the cutoff identifies in each case."},
        {"text": "Cattaneo, Idrobo & Titiunik, A Practical Introduction to "
                 "Regression Discontinuity Designs.",
         "look_for": "local-polynomial estimation, how the bandwidth is chosen, "
                     "and the standard validity/robustness checks."},
    ],
    "optional_readings": [
        {"text": "Huntington-Klein, The Effect — the Regression Discontinuity "
                 "chapter.",
         "note": "A friendly, picture-first walkthrough if the local-polynomial "
                 "machinery feels fast."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its "
        "own.",
    "concept_sections": [
        {"heading": "The setup: a cutoff creates a local experiment",
         "body": "A running variable R (a test score, a biomarker, an age, a "
            "vote share) determines treatment through a known cutoff c. In a "
            "SHARP design everyone with R ≥ c is treated and everyone below is "
            "not, so treatment is a deterministic step at c. Far from the cutoff, "
            "treated and untreated units are very different. But right at the "
            "cutoff a student scoring 89.9 and one scoring 90.1 are essentially "
            "interchangeable — the only systematic difference between them is the "
            "treatment. So the jump in the outcome as R crosses c is the causal "
            "effect, for units at the cutoff."},
        {"heading": "Sharp vs. fuzzy — and what each identifies",
         "bullets": [
            [("Sharp RD:  ", {"bold": True}),
             ("treatment is a deterministic function of R — P(D=1) jumps from 0 "
              "to 1 at c. The outcome jump at c is the average treatment effect "
              "for units at the cutoff.", {})],
            [("Fuzzy RD:  ", {"bold": True}),
             ("crossing c only shifts the PROBABILITY of treatment (e.g. from "
              "0.2 to 0.7), because eligibility is encouraged, not enforced. The "
              "outcome jump must be scaled by the jump in treatment probability.",
              {})],
            [("The fuzzy estimand:  ", {"bold": True}),
             ("(jump in Y) ÷ (jump in P(D=1)) — a Wald/IV ratio at the cutoff. "
              "It is a LATE: the effect for compliers, the units whose treatment "
              "status is actually moved by crossing c.", {})],
         ]},
        {"heading": "The continuity assumption and local randomization",
         "body": "RD does not need treatment to be randomly assigned everywhere. "
            "It needs the assumption that, absent treatment, the average outcome "
            "would be a CONTINUOUS function of the running variable at the "
            "cutoff. In words: nothing else changes discontinuously at c, so any "
            "jump in Y must be the treatment. The local-randomization view is the "
            "same idea in stronger form — in a tiny window around c, which side a "
            "unit lands on is as good as a coin flip, so the window behaves like a "
            "small randomized experiment.",
         "bullets": [
            [("What can break it:  ", {"bold": True}),
             ("another program uses the same cutoff; the cutoff coincides with a "
              "different eligibility rule; or units can precisely control R and "
              "sort to the favorable side.", {})],
            [("Why it's partly testable:  ", {"bold": True}),
             ("continuity itself is an assumption, but its consequences — smooth "
              "covariates at c and a smooth density of R at c — can be checked.",
              {})],
         ]},
        {"heading": "Estimation: local polynomials and the bandwidth",
         "body": "We do not fit one global curve through all the data; a global "
            "high-order polynomial can invent spurious jumps at the cutoff. "
            "Instead we fit a LOCAL regression — typically a separate linear (or "
            "quadratic) fit on each side, using only points within a bandwidth h "
            "of c — and read off the gap between the two fitted intercepts at c. "
            "Choosing h is a bias–variance tradeoff.",
         "bullets": [
            [("Wide bandwidth:  ", {"bold": True}),
             ("more data, smaller variance, but you reach into the curved part of "
              "the relationship and the linear approximation biases the jump.",
              {})],
            [("Narrow bandwidth:  ", {"bold": True}),
             ("less bias from curvature, but few points near c, so the estimate "
              "is noisy. Report estimates across several bandwidths and check the "
              "answer is stable.", {})],
         ],
         "callout": {"title": "Why local, not global",
            "color": "RED",
            "lines": ["A global polynomial fit to the whole sample can manufacture "
                      "a discontinuity at c out of curvature far away — a famous "
                      "failure mode (Gelman & Imbens).",
                      "RD is fundamentally a LOCAL comparison: trust points near "
                      "the cutoff, not the shape of the curve in the tails."]}},
        {"heading": "Validity checks that earn the design",
         "body": "An RD estimate is only as credible as its checks. Three are "
            "standard and you will run all of them in lab.",
         "bullets": [
            [("McCrary density test:  ", {"bold": True}),
             ("if units can manipulate R to land on the favorable side, the "
              "density of R will spike just above c. A smooth density at c is "
              "evidence against manipulation; a jump is a red flag.", {})],
            [("Placebo cutoffs:  ", {"bold": True}),
             ("re-run the estimator at fake cutoffs where no treatment changes "
              "(well inside one side). A real RD shows ~0 effect there; a "
              "non-zero 'effect' at a placebo cutoff means your method is picking "
              "up curvature, not treatment.", {})],
            [("Donut-hole check:  ", {"bold": True}),
             ("drop the units in a tiny window right at c and re-estimate. If the "
              "effect is driven by suspicious heaping or manipulation exactly at "
              "c, it will move; if it is stable, the design is more credible.",
              {})],
         ]},
    ],

    # --------------------------------------------------------------- problem set
    "problem_set": {
        "label": "Concept Set 9",
        "title": "Reading a discontinuity",
        "intro": "Short-answer reasoning about regression discontinuity. Write "
            "your answer before you look — full solutions follow. Aim for a "
            "precise sentence or two each; the point is to say WHAT is identified "
            "and WHY a check does or does not reassure you.",
        "problems": [
            {"title": "Sharp vs. fuzzy — what does each identify?",
             "prompt": "Program A admits every student with a test score ≥ 90 and "
                "no one below; admission is strictly enforced. Program B sends an "
                "encouragement letter to students scoring ≥ 90, after which 70% "
                "enroll versus 20% of those just below. For each program, is the "
                "design sharp or fuzzy, and what causal quantity does the "
                "discontinuity at 90 identify?",
             "solution_title": "A is sharp (ATE at the cutoff); B is fuzzy (a "
                "LATE for compliers, via the Wald ratio).",
             "solution": [
                "Program A: treatment is a deterministic step at 90, so it is a "
                "SHARP RD. The jump in the outcome at 90 estimates the average "
                "treatment effect for units AT the cutoff (score = 90).",
                "Program B: crossing 90 only raises the treatment probability "
                "(0.2 → 0.7), so it is a FUZZY RD. The outcome jump alone "
                "understates the effect because not everyone above is treated.",
                "For B you divide the jump in Y by the jump in treatment "
                "probability (≈0.5) — a Wald/IV ratio at the cutoff. It "
                "identifies a LATE: the effect for compliers, the students whose "
                "enrollment is actually moved by crossing 90."]},
            {"title": "The continuity assumption, in words",
             "prompt": "A colleague says 'RD works because treatment is randomly "
                "assigned at the cutoff.' That is not quite the assumption. State "
                "the actual identifying assumption of a sharp RD in plain "
                "language, and explain why a jump in the outcome at the cutoff "
                "then has to be the treatment effect.",
             "solution_title": "Assume the untreated potential outcome is "
                "continuous in R at the cutoff — then any jump is the treatment.",
             "solution": [
                "The assumption is continuity: in the absence of treatment, the "
                "average potential outcome E[Y(0) | R] (and E[Y(1) | R]) would be "
                "a smooth, continuous function of R at the cutoff c.",
                "Nothing is literally randomized. But if the no-treatment curve "
                "would have passed smoothly through c, then the ONLY thing that "
                "changes discontinuously at c is treatment status.",
                "Therefore a discontinuous jump in observed Y at c cannot be "
                "explained by the running variable evolving smoothly — it must be "
                "the causal effect of treatment for units at the cutoff."]},
            {"title": "Why manipulation of the running variable breaks RD",
             "prompt": "A clinic treats patients whose biomarker reading is ≥ a "
                "threshold. You find that the density of readings spikes just "
                "above the threshold — many more patients land at 'just eligible' "
                "than 'just ineligible.' Why does this threaten the RD, and which "
                "formal test captures the concern?",
             "solution_title": "Manipulation makes the two sides non-comparable; "
                "the McCrary density test flags it.",
             "solution": [
                "If patients (or clinicians) can nudge the reading to cross the "
                "threshold, those who land just above are a self-selected group — "
                "more motivated, sicker, or better-connected — not exchangeable "
                "with those just below.",
                "That sorting violates continuity: the units on the two sides now "
                "differ in ways that also affect the outcome, so the jump in Y "
                "mixes the treatment effect with the selection.",
                "The McCrary density test formalizes the check: estimate the "
                "density of the running variable on each side of c and test for a "
                "discontinuity. A spike just above c (a jump in the density) is "
                "evidence of manipulation; a smooth density is reassuring."]},
            {"title": "The bandwidth bias–variance tradeoff",
             "prompt": "You estimate a sharp RD by local linear regression. With "
                "h = 0.5 you get an effect of 4.0; with h = 0.1 you get 4.3 but a "
                "much wider confidence interval; with h = 1.0 you get 2.6. "
                "Explain, in terms of bias and variance, what is happening as h "
                "grows and how you would defend a choice of bandwidth.",
             "solution_title": "Wider h adds bias from curvature; narrower h adds "
                "variance from few points. Defend stability across a range.",
             "solution": [
                "A narrow bandwidth (h = 0.1) uses only points right at the "
                "cutoff, so the linear approximation is nearly exact (low bias) — "
                "but with few observations the estimate is noisy (high variance), "
                "hence the wide interval.",
                "A wide bandwidth (h = 1.0) borrows many far-away points; the "
                "true relationship curves there, so a straight line "
                "mis-extrapolates to c and biases the jump (here, toward 2.6). "
                "Variance shrinks but bias grows.",
                "Defend the choice by showing the estimate is STABLE across a "
                "sensible range of bandwidths (the 0.1–0.5 estimates agree near "
                "4), ideally using a data-driven optimal bandwidth, and by noting "
                "where it starts to drift as h gets large."]},
            {"title": "Interpreting a placebo-cutoff test",
             "prompt": "At the true cutoff your local linear RD estimates an "
                "effect of 5.0. As a check you re-run the SAME estimator at fake "
                "cutoffs of 80 and 100 (well inside one side, where no treatment "
                "actually changes) and get 'effects' of 2.8 and −3.1. What does "
                "this tell you about your headline estimate?",
             "solution_title": "Large placebo 'effects' undermine the design — "
                "the estimator is reading curvature, not treatment.",
             "solution": [
                "At a placebo cutoff nothing changes, so a valid RD estimator "
                "should return approximately zero. Estimates of 2.8 and −3.1 are "
                "far from zero.",
                "That means the method is detecting jumps where there is no "
                "treatment — almost certainly mistaking curvature in the outcome "
                "for a discontinuity. Your headline 5.0 is then suspect: some of "
                "it could be the same artifact.",
                "The fix is methodological, not cosmetic: shrink the bandwidth, "
                "use a more flexible local fit, or adopt a data-driven bandwidth, "
                "then confirm the placebo cutoffs return ~0 before you trust the "
                "estimate at the real cutoff."]},
        ],
    },

    # ----------------------------------------------------------------------- lab
    "lab": {
        "label": "Lab 6",
        "title": "Regression discontinuity",
        "goal": "simulate a sharp RD with a known jump, estimate it by local "
            "linear regression on each side of the cutoff, and stress-test the "
            "result with a bandwidth sweep, placebo cutoffs, a donut-hole check, "
            "and a McCrary-style density check — then repeat for a fuzzy design.",
        "steps": [
            {"heading": "Step 1 · Simulate a sharp RD with a known effect",
             "body": "Draw a running variable R, assign treatment by R ≥ c, and "
                "build an outcome with a smooth baseline plus a KNOWN jump TAU at "
                "the cutoff. Because you set TAU, you can check whether your "
                "estimator recovers it.",
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(9)\n"
                "n, c, TAU = 4000, 0.0, 8.0\n"
                "R = rng.uniform(-1, 1, n)            # running variable\n"
                "D = (R >= c).astype(float)           # sharp treatment\n"
                "mu = 30 + 4*R + 1.5*R**2             # smooth baseline\n"
                "Y = mu + TAU*D + rng.normal(0, 3, n) # known jump of 8 at c",
             "code_r": 'set.seed(9)\n'
                'n <- 4000; c <- 0; TAU <- 8\n'
                'R <- runif(n, -1, 1)\n'
                'D <- as.numeric(R >= c)\n'
                'mu <- 30 + 4*R + 1.5*R^2\n'
                'Y <- mu + TAU*D + rnorm(n, 0, 3)'},
            {"heading": "Step 2 · Estimate the jump with local linear regression",
             "body": "Keep points within a bandwidth h of c and fit "
                "Y ~ 1 + D + (R−c) + D·(R−c). The coefficient on D is the jump at "
                "the cutoff. (In R, rdrobust does the bandwidth, kernel, and "
                "bias-correction for you.)",
             "code_python": "def rd(R, Y, D, c=0.0, h=0.5):\n"
                "    m = np.abs(R - c) <= h\n"
                "    xc = R[m] - c\n"
                "    Z = np.column_stack([np.ones(m.sum()), D[m], xc, D[m]*xc])\n"
                "    return sm.OLS(Y[m], Z).fit().params[1]\n"
                "print('estimate =', round(rd(R, Y, D, c, 0.5), 3), ' truth =', TAU)",
             "code_r": '# install.packages("rdrobust")\n'
                'library(rdrobust)\n'
                'fit <- rdrobust(y = Y, x = R, c = 0)\n'
                'summary(fit)            # Coef = estimated jump at the cutoff'},
            {"heading": "Step 3 · Sweep the bandwidth",
             "body": "Re-estimate across several bandwidths. A credible RD is "
                "stable across a sensible range; watch it drift as h reaches into "
                "the curved part of the baseline.",
             "code_python": "for h in [0.15, 0.25, 0.5, 0.75, 1.0]:\n"
                "    print(f'h={h:>4}:  est = {rd(R, Y, D, c, h):.3f}')",
             "code_r": 'for (h in c(0.15, 0.25, 0.5, 0.75, 1.0)) {\n'
                '  f <- rdrobust(Y, R, c = 0, h = h)\n'
                '  cat(sprintf("h=%.2f est=%.3f\\n", h, f$coef[1]))\n}'},
            {"heading": "Step 4 · Placebo cutoffs and a donut-hole check",
             "body": "Re-run the estimator at fake cutoffs inside one side (no "
                "treatment changes there — expect ~0). Then drop a tiny window "
                "right at the real cutoff and re-estimate; a stable answer means "
                "the effect is not an artifact of heaping at c.",
             "code_python": "# placebo: stay entirely on the control side, fake cutoff at -0.5\n"
                "left = R < c\n"
                "pe = rd(R[left], Y[left], (R[left] >= -0.5).astype(float), -0.5, 0.3)\n"
                "print('placebo cutoff -0.5 (expect ~0):', round(pe, 3))\n\n"
                "# donut hole: drop |R-c| < 0.05, then re-estimate\n"
                "keep = np.abs(R - c) >= 0.05\n"
                "print('donut-hole estimate:',\n"
                "      round(rd(R[keep], Y[keep], D[keep], c, 0.5), 3))",
             "code_r": '# placebo cutoff on the control side\n'
                'rdrobust(Y[R < 0], R[R < 0], c = -0.5)\n'
                '# donut hole: drop |R| < 0.05\n'
                'k <- abs(R) >= 0.05\n'
                'rdrobust(Y[k], R[k], c = 0)'},
            {"heading": "Step 5 · (Sketch) a McCrary-style density check",
             "body": "Manipulation of the running variable shows up as a jump in "
                "its density at c. Bin R and compare the counts just below vs. "
                "just above c; a smooth density is reassuring, a spike is a red "
                "flag. (rddensity implements the formal McCrary/Cattaneo test.)",
             "code_python": "counts, edges = np.histogram(R, bins=40)\n"
                "ctr = 0.5*(edges[:-1] + edges[1:])\n"
                "lo = counts[(ctr < c) & (ctr > c-0.2)].mean()\n"
                "hi = counts[(ctr >= c) & (ctr < c+0.2)].mean()\n"
                "print(f'density just below={lo:.0f}  just above={hi:.0f}  '\n"
                "      f'ratio={hi/lo:.2f}  (≈1 ⇒ no manipulation)')",
             "code_r": '# install.packages("rddensity")\n'
                'library(rddensity)\n'
                'summary(rddensity(R, c = 0))   # p > 0.05 ⇒ no evidence of sorting'},
        ],
        "expected": "Local linear regression recovers the jump near 8 across "
            "bandwidths from about 0.15 to 0.5, then drifts as h grows and the "
            "straight line reaches into the curved baseline. Placebo cutoffs "
            "return roughly zero, the donut-hole estimate barely moves, and the "
            "density ratio at the cutoff is close to 1 — exactly the picture a "
            "credible RD should produce.",
        "submit": [
            "Push your notebook plus a short README reporting the bandwidth sweep "
            "and the placebo / donut / density results.",
            "In two sentences, state which estimand your RD identifies and the "
            "single assumption it rests on.",
            "Bring your active-reading sentences to lab.",
        ],
    },

    "self_check": [
        "Explain sharp vs. fuzzy RD and what each identifies, without notes.",
        "State the continuity assumption and why a jump in Y is then causal.",
        "Say why local linear beats a global polynomial, and how bandwidth trades "
        "bias against variance.",
        "Name the three validity checks and what a failure of each would look "
        "like.",
        "Recover a known fuzzy-RD effect by dividing the reduced form by the "
        "first stage.",
    ],
    "next_week": {
        "heading": "Coming up: Week 10 — Difference-in-differences & panel methods",
        "teaser": "We move from a cutoff in space to a break in time. With "
            "repeated observations on treated and control groups before and after "
            "an intervention, difference-in-differences nets out fixed differences "
            "and common trends to isolate the effect — under a parallel-trends "
            "assumption you will learn to probe. Skim the DiD chapter of "
            "Cunningham's Mixtape to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 9", "items": [
            {"t": "The cutoff idea", "d": "A known threshold turns an assignment "
             "rule into a local experiment."},
            {"t": "Sharp vs. fuzzy", "d": "Deterministic step versus a jump in "
             "treatment probability."},
            {"t": "Continuity", "d": "The one assumption RD rests on — and local "
             "randomization."},
            {"t": "Estimation", "d": "Local polynomials and the bias–variance "
             "bandwidth choice."},
            {"t": "Validity checks", "d": "McCrary density, placebo cutoffs, "
             "donut-hole robustness."},
            {"t": "Two cases + lab", "d": "A scholarship cutoff, a clinical "
             "threshold, then code it."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Block III: designs that borrow an experiment from the world",
         "bullets": [
            "Adjustment methods (Block II) need every confounder measured — a "
            "strong, often unmet, demand.",
            "Quasi-experimental designs instead exploit how treatment was "
            "assigned to mimic randomization.",
            ("Week 8 used an instrument; this week the instrument is a cutoff.", 1),
            "RD's appeal: the identifying assumption is unusually weak and "
            "unusually checkable.",
            "The price: the effect is LOCAL — it speaks only for units near the "
            "cutoff.",
         ],
         "note": {"title": "One-line idea",
            "body": "If a rule treats everyone above a threshold and no one "
            "below, compare units just above to units just below."}},
        {"type": "content", "kicker": "Motivation",
         "title": "Cutoffs are everywhere once you look", "bullets": [
            "Scholarships and admissions: a test score ≥ a passing mark.",
            "Clinical guidelines: treat if a biomarker crosses a threshold.",
            "Policy: benefits that switch on at an income or age line.",
            "Elections: who wins a seat at 50% of the vote.",
            ("Each rule hands you a comparison the world set up for free.", 1),
         ],
         "note": {"title": "Running variable",
            "body": "The score, biomarker, age, or vote share that the cutoff "
            "is applied to. Call it R."}},

        {"type": "section", "kicker": "Part 1", "title": "The cutoff idea",
         "subtitle": "Far from the threshold, treated and untreated units differ. "
            "Right at it, they are nearly interchangeable."},
        {"type": "content", "kicker": "Intuition",
         "title": "Just above vs. just below is almost a coin flip", "bullets": [
            "A student scoring 90.1 and one scoring 89.9 are essentially the same "
            "student.",
            "But one is admitted and one is not — the cutoff alone separates them.",
            "So any difference in their later outcomes is the program, not the "
            "students.",
            ("This is a randomized experiment the assignment rule ran for you.", 1),
            "It only holds NEAR the cutoff — that is the catch we keep returning "
            "to.",
         ],
         "note": {"title": "Estimand",
            "body": "The effect for units AT the cutoff — not the average over "
            "everyone."}},
        {"type": "statement",
         "quote": "Two students one point apart are the same student; only the "
            "cutoff differs. So the jump at the cutoff is the treatment.",
         "attribution": "Regression discontinuity turns a bureaucratic threshold "
            "into a local experiment — the design's whole power and its whole "
            "limitation."},

        {"type": "section", "kicker": "Part 2", "title": "Sharp vs. fuzzy",
         "subtitle": "Does crossing the cutoff DETERMINE treatment, or merely "
            "make it more likely?"},
        {"type": "compare", "kicker": "Two regimes",
         "title": "Sharp and fuzzy designs", "columns": [
            {"head": "SHARP RD", "sub": "D is a step at c", "points": [
                "Everyone above c treated; no one below.",
                "P(D=1) jumps 0 → 1 at the cutoff.",
                "The outcome jump IS the effect.",
                "Estimand: ATE for units at c."]},
            {"head": "FUZZY RD", "sub": "P(D) jumps at c", "points": [
                "Crossing c only raises the chance of treatment.",
                "e.g. enrollment 0.2 → 0.7 at c.",
                "Scale the outcome jump by the treatment jump.",
                "Estimand: a LATE (compliers)."]},
         ]},
        {"type": "content", "kicker": "Fuzzy estimation",
         "title": "Fuzzy RD is IV at the cutoff", "bullets": [
            "Reduced form: the jump in the OUTCOME at c.",
            "First stage: the jump in TREATMENT probability at c.",
            ("Effect = reduced form ÷ first stage — a Wald ratio.", 0),
            ("Identical algebra to the instrumental-variables estimator of "
             "Week 8.", 1),
            "It identifies a LATE: the effect for units moved across treatment by "
            "crossing c.",
         ],
         "note": {"title": "Why divide",
            "body": "If only half the above-cutoff units actually take treatment, "
            "the outcome jump is half the per-treated effect. Dividing restores "
            "it."}},
        {"type": "table", "kicker": "Two designs, side by side",
         "title": "What jumps, and what you estimate",
         "headers": ["Design", "What jumps at c", "Estimator", "Identifies"],
         "rows": [
            ["Sharp", "Treatment 0 → 1", "Jump in Y", "ATE at the cutoff"],
            ["Fuzzy", "P(treatment), e.g. .2 → .7", "Jump-Y ÷ jump-P",
             "LATE (compliers)"],
         ],
         "note": {"title": "Same backbone",
            "body": "Both read a discontinuity at c; fuzzy just rescales it by "
            "the first stage."}},

        {"type": "section", "kicker": "Part 3", "title": "The continuity assumption",
         "subtitle": "RD does not assume random assignment. It assumes the "
            "no-treatment world would be smooth at the cutoff."},
        {"type": "content", "kicker": "The identifying assumption",
         "title": "Continuity at the cutoff", "bullets": [
            "Assume E[Y(0) | R] and E[Y(1) | R] are continuous in R at c.",
            "In words: absent treatment, the outcome would pass smoothly through "
            "the cutoff.",
            "Then the ONLY thing that changes discontinuously at c is treatment.",
            ("So a jump in observed Y at c must be the treatment effect.", 1),
            "This is weaker and more transparent than 'no unmeasured "
            "confounders.'",
         ],
         "note": {"title": "Local randomization",
            "body": "Stronger sibling view: in a tiny window around c, which side "
            "you fall on is as good as random."}},
        {"type": "compare", "kicker": "What can go wrong",
         "title": "Threats to continuity", "columns": [
            {"head": "Manipulation / sorting", "points": [
                "Units precisely control R and jump the cutoff.",
                "The two sides stop being comparable.",
                "Caught by the density test."]},
            {"head": "A coinciding rule", "points": [
                "Another program uses the SAME cutoff.",
                "A second thing jumps at c.",
                "The jump mixes two effects."]},
            {"head": "Functional-form error", "points": [
                "A global polynomial invents a jump.",
                "Curvature masquerades as a discontinuity.",
                "Caught by placebo cutoffs."]},
         ]},

        {"type": "section", "kicker": "Part 4", "title": "Estimation",
         "subtitle": "Fit the relationship locally on each side of the cutoff — "
            "then read off the gap."},
        {"type": "steps", "kicker": "The recipe",
         "title": "Local linear RD in four moves", "steps": [
            {"title": "Window", "body": "— keep points within bandwidth h of the "
             "cutoff c."},
            {"title": "Fit each side", "body": "— a separate linear fit for "
             "R < c and R ≥ c."},
            {"title": "Read the gap", "body": "— the difference of fitted "
             "intercepts at c is the jump."},
            {"title": "Stress-test", "body": "— vary h; run placebo, donut, and "
             "density checks."},
         ],
         "note": "In practice one regression with a treatment dummy and its "
            "interaction with (R−c) does all of steps 2–3 at once."},
        {"type": "content", "kicker": "A warning worth a slide",
         "title": "Local, not global — never trust a high-order fit", "bullets": [
            "A global high-order polynomial uses faraway points to set the value "
            "at c.",
            "Curvature in the tails can manufacture a jump that isn't there.",
            "Gelman & Imbens: avoid high-order global polynomials in RD.",
            ("Trust points NEAR the cutoff; fit them with a line or a quadratic.",
             1),
         ],
         "note": {"title": "Rule of thumb",
            "body": "Linear or quadratic, local, within a sensible bandwidth — "
            "and report the bandwidth."}},
        {"type": "content", "kicker": "Choosing h",
         "title": "The bandwidth is a bias–variance dial", "bullets": [
            "Wide h: many points, low variance — but the line reaches curvature "
            "and biases the jump.",
            "Narrow h: little bias from curvature — but few points, so the "
            "estimate is noisy.",
            "Report the estimate across a range and show it is stable.",
            ("Data-driven optimal bandwidths (e.g. rdrobust) automate the "
             "tradeoff.", 1),
         ],
         "note": {"title": "What to show",
            "body": "An estimate-vs-bandwidth plot. A flat middle region is the "
            "reassuring picture."}},

        {"type": "section", "kicker": "Part 5", "title": "Validity checks",
         "subtitle": "An RD estimate is only as credible as the checks you run "
            "around it."},
        {"type": "content", "kicker": "Check 1 · Manipulation",
         "title": "The McCrary density test", "bullets": [
            "If units sort across the cutoff, the density of R spikes just above "
            "c.",
            "Estimate the density on each side and test for a jump at c.",
            "Smooth density ⇒ no evidence of manipulation (reassuring).",
            ("A spike just above c ⇒ self-selection; the two sides aren't "
             "comparable.", 1),
         ],
         "note": {"title": "Tooling",
            "body": "rddensity (R) implements the formal Cattaneo–Jansson–Ma "
            "version of the test."}},
        {"type": "content", "kicker": "Checks 2 & 3 · Falsification",
         "title": "Placebo cutoffs and the donut hole", "bullets": [
            "Placebo cutoff: re-run the estimator where no treatment changes — it "
            "should return ~0.",
            "A non-zero placebo 'effect' means you're reading curvature, not "
            "treatment.",
            "Donut hole: drop a tiny window right at c and re-estimate.",
            ("Stable ⇒ the effect isn't an artifact of heaping or manipulation "
             "at c.", 1),
         ],
         "note": {"title": "Also check",
            "body": "Pre-determined covariates should NOT jump at c — they're a "
            "placebo outcome."}},
        {"type": "statement",
         "quote": "Continuity is an assumption, but its fingerprints — smooth "
            "density, smooth covariates, zero placebo effects — are all "
            "checkable.",
         "attribution": "This is why RD is among the most trusted "
            "quasi-experimental designs: the thing you assume leaves testable "
            "traces."},

        {"type": "section", "kicker": "Part 6", "title": "Two cases",
         "subtitle": "A scholarship cutoff and a clinical treatment threshold — "
            "the same logic in different worlds."},
        {"type": "steps", "kicker": "Case A · A scholarship cutoff",
         "title": "Does a merit scholarship raise graduation rates?", "steps": [
            {"title": "Running variable", "body": "— a test score; the award "
             "needs score ≥ a published cutoff."},
            {"title": "Design", "body": "— sharp if the award is automatic; fuzzy "
             "if students must accept and some don't."},
            {"title": "Check", "body": "— density smooth at the cutoff? scores "
             "aren't easily gamed to the decimal."},
            {"title": "Read-off", "body": "— the jump in graduation at the cutoff "
             "is the scholarship's local effect."},
         ]},
        {"type": "steps", "kicker": "Case B · A clinical threshold",
         "title": "Does treating at a biomarker cutoff help patients?", "steps": [
            {"title": "Running variable", "body": "— a biomarker; guidelines "
             "treat at or above a threshold."},
            {"title": "Design", "body": "— often FUZZY: clinicians use judgment, "
             "so treatment probability only jumps."},
            {"title": "Check", "body": "— can readings be nudged across the line? "
             "test the density for sorting."},
            {"title": "Read-off", "body": "— scale the outcome jump by the "
             "treatment jump (a Wald ratio)."},
         ],
         "note": "Same machinery: a running variable, a cutoff, a jump — and the "
            "checks that earn it."},

        {"type": "section", "kicker": "Part 7", "title": "To the lab",
         "subtitle": "Simulate a known jump, recover it, then try to break it."},
        {"type": "content", "kicker": "Lab 6 preview",
         "title": "What you'll do this week", "bullets": [
            "Simulate a sharp RD with a KNOWN jump and recover it by local linear "
            "regression.",
            "Sweep the bandwidth and watch bias appear as the window widens.",
            "Run placebo cutoffs (expect ~0) and a donut-hole check (expect "
            "stability).",
            "Sketch a McCrary-style density check for manipulation.",
            ("Then a FUZZY RD: scale the reduced form by the first stage to "
             "recover the truth.", 1),
         ],
         "note": {"title": "Ground truth",
            "body": "Because you set the jump in code, you can assert your "
            "estimate recovers it."}},
        {"type": "statement",
         "quote": "Window · fit each side · read the gap · stress-test.",
         "attribution": "Next week we trade a cutoff in space for a break in "
            "time: difference-in-differences and panel methods. See you in the "
            "lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A cutoff is a local experiment\n\n"
            "In a **regression discontinuity** design, treatment is decided by "
            "whether a *running variable* `R` crosses a known cutoff `c`. Far from "
            "`c`, treated and untreated units differ a lot. But right at `c`, a "
            "unit just above and one just below are nearly interchangeable — so "
            "the **jump in the outcome at the cutoff** is the causal effect, for "
            "units at the cutoff.\n\n"
            "We'll simulate data where we *set* the true jump, so we can always "
            "check our estimate against the truth. We reuse the notebook's `RNG` "
            "and import `statsmodels` once here."},
        {"code": "import statsmodels.api as sm\n\n"
            "def make_sharp(n=4000, c=0.0, tau=8.0, slope=4.0, curve=1.5, noise=3.0):\n"
            "    \"\"\"Sharp RD: D = 1 iff R >= c, with a KNOWN jump `tau` at c.\"\"\"\n"
            "    R = RNG.uniform(-1, 1, n)                 # running variable\n"
            "    D = (R >= c).astype(float)                # sharp treatment\n"
            "    mu = 30 + slope*R + curve*R**2            # smooth baseline (continuous at c)\n"
            "    Y = mu + tau*D + RNG.normal(0, noise, n)  # jump of `tau` at the cutoff\n"
            "    return pd.DataFrame({'R': R, 'D': D, 'Y': Y})\n\n"
            "C, TAU = 0.0, 8.0          # cutoff and TRUE effect at the cutoff\n"
            "sharp = make_sharp(c=C, tau=TAU)\n"
            "print(sharp.head(3))\n"
            "print(f'\\nTrue jump at the cutoff: {TAU}')"},
        {"md": "### A picture first\n\n"
            "Scatter the data and overlay a separate linear fit on each side of "
            "the cutoff. The vertical gap between the two fitted lines *at* `c` is "
            "exactly what RD estimates."},
        {"code": "def side_fit(df, c, side):\n"
            "    d = df[df['D'] == side]\n"
            "    b = np.polyfit(d['R'], d['Y'], 1)        # local-ish linear fit per side\n"
            "    xs = np.linspace(d['R'].min(), d['R'].max(), 50)\n"
            "    return xs, np.polyval(b, xs)\n\n"
            "fig, ax = plt.subplots()\n"
            "samp = sharp.sample(800, random_state=0)\n"
            "ax.scatter(samp['R'], samp['Y'], s=6, alpha=0.3, color='#7F8694')\n"
            "for side, col in [(0.0, '#2F6DB5'), (1.0, '#2A9D8F')]:\n"
            "    xs, ys = side_fit(sharp, C, side)\n"
            "    ax.plot(xs, ys, color=col, lw=2.5)\n"
            "ax.axvline(C, color='#C0504D', ls='--')\n"
            "ax.set_xlabel('running variable R'); ax.set_ylabel('outcome Y')\n"
            "ax.set_title('Sharp RD: the jump at the cutoff is the effect')\n"
            "print('Eyeball the gap at R=0 — it should be about', TAU)"},
        {"md": "## 2 · Estimate the jump by local linear regression\n\n"
            "Keep only points within a **bandwidth** `h` of the cutoff and fit\n\n"
            "$$Y = \\beta_0 + \\tau\\,D + \\gamma\\,(R-c) + \\delta\\,D\\,(R-c) + \\varepsilon.$$\n\n"
            "The coefficient `τ` on the treatment dummy `D` is the jump at `c`. "
            "We print the estimate next to the truth and `assert` we recovered it."},
        {"code": "def rd_estimate(df, c=0.0, h=0.5):\n"
            "    \"\"\"Local linear RD: returns the estimated jump at the cutoff.\"\"\"\n"
            "    d = df[np.abs(df['R'] - c) <= h]\n"
            "    xc = d['R'].values - c\n"
            "    Z = np.column_stack([np.ones(len(d)), d['D'].values, xc, d['D'].values*xc])\n"
            "    return sm.OLS(d['Y'].values, Z).fit().params[1]   # coef on D\n\n"
            "est = rd_estimate(sharp, c=C, h=0.5)\n"
            "print(f'local linear RD estimate = {est:.3f}   (truth = {TAU})')\n"
            "assert abs(est - TAU) < 1.0, 'should recover the known jump'\n"
            "print('Recovered the known jump within tolerance.')"},
        {"md": "### 🔧 Exercise 2.1 — the naive within-window difference\n\n"
            "Before trusting the regression, build intuition with the crudest "
            "possible estimator: inside a *narrow* window around `c`, just take "
            "the **mean of `Y` above minus the mean below**. With a small enough "
            "window there is little curvature, so this simple difference should "
            "also land near `TAU`.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (it uses `...`), so "
            "you can execute it before solving."},
        {"code": "def naive_jump(df, c=0.0, h=0.1):\n"
            "    d = df[np.abs(df['R'] - c) <= h]\n"
            "    above = ...   # TODO: mean of Y where D == 1 inside the window\n"
            "    below = ...   # TODO: mean of Y where D == 0 inside the window\n"
            "    return above, below\n\n"
            "# Once filled in, this will print two numbers whose difference ≈ TAU.\n"
            "naive_jump(sharp, c=C, h=0.1)"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "def naive_jump(df, c=0.0, h=0.1):\n"
            "    d = df[np.abs(df['R'] - c) <= h]\n"
            "    above = d.loc[d['D'] == 1, 'Y'].mean()\n"
            "    below = d.loc[d['D'] == 0, 'Y'].mean()\n"
            "    return above - below\n\n"
            "nj = naive_jump(sharp, c=C, h=0.1)\n"
            "print(f'naive within-window difference = {nj:.3f}   (truth = {TAU})')\n"
            "assert abs(nj - TAU) < 1.5, 'narrow-window difference should be near the truth'"},
        {"md": "## 3 · Bandwidth sensitivity\n\n"
            "Choosing `h` is a **bias–variance tradeoff**. A *narrow* `h` has "
            "little bias from curvature but is noisy; a *wide* `h` reaches into "
            "the curved baseline and biases the jump. A credible RD is **stable** "
            "across a sensible range. We estimate across several bandwidths and "
            "plot the result."},
        {"code": "hs = [0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.00]\n"
            "ests = [rd_estimate(sharp, c=C, h=h) for h in hs]\n"
            "for h, e in zip(hs, ests):\n"
            "    print(f'h = {h:>4}:  est = {e:.3f}')\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot(hs, ests, 'o-', color='#2F6DB5')\n"
            "ax.axhline(TAU, color='#C0504D', ls='--', label=f'truth = {TAU}')\n"
            "ax.set_xlabel('bandwidth h'); ax.set_ylabel('estimated jump')\n"
            "ax.set_title('Bandwidth sensitivity'); ax.legend()\n\n"
            "# The mid-range estimates should cluster near the truth.\n"
            "mid = [e for h, e in zip(hs, ests) if h <= 0.5]\n"
            "assert abs(np.mean(mid) - TAU) < 1.0, 'small/medium-h estimates should be near truth'\n"
            "print('\\nMid-range bandwidths agree on the truth; watch the drift as h grows.')"},
        {"md": "## 4 · Placebo cutoffs — a falsification test\n\n"
            "At a **fake** cutoff where no treatment actually changes, a valid RD "
            "estimator should return *approximately zero*. To make sure there is "
            "genuinely no jump, we restrict to **one side** of the real cutoff "
            "(all-control or all-treated) and invent a placebo cutoff inside it. A "
            "near-zero estimate is reassuring; a large one means the method is "
            "reading curvature, not treatment."},
        {"code": "def placebo_estimate(df, real_c, fake_c, h=0.3):\n"
            "    # stay entirely on one side of the real cutoff -> no real treatment jump\n"
            "    side = df[df['D'] == (1.0 if fake_c > real_c else 0.0)].copy()\n"
            "    d = side[np.abs(side['R'] - fake_c) <= h]\n"
            "    xc = d['R'].values - fake_c\n"
            "    fakeD = (d['R'].values >= fake_c).astype(float)\n"
            "    Z = np.column_stack([np.ones(len(d)), fakeD, xc, fakeD*xc])\n"
            "    return sm.OLS(d['Y'].values, Z).fit().params[1]\n\n"
            "for fc in [-0.5, 0.5]:\n"
            "    pe = placebo_estimate(sharp, C, fc, h=0.3)\n"
            "    print(f'placebo cutoff {fc:+.1f}:  est = {pe:+.3f}   (expect ~0)')\n"
            "    assert abs(pe) < 2.0, 'placebo cutoff should give ~0 effect'\n"
            "print('Placebo cutoffs return ~0 — the estimator is not inventing jumps.')"},
        {"md": "## 5 · Donut-hole robustness\n\n"
            "If the effect were really driven by suspicious **heaping or "
            "manipulation right at the cutoff**, dropping a tiny window around `c` "
            "would change the answer. We re-estimate after removing units with "
            "`|R − c| < δ` for a few `δ` and confirm the estimate barely moves."},
        {"code": "def donut_estimate(df, c=0.0, h=0.5, delta=0.05):\n"
            "    d = df[(np.abs(df['R'] - c) <= h) & (np.abs(df['R'] - c) >= delta)]\n"
            "    xc = d['R'].values - c\n"
            "    Z = np.column_stack([np.ones(len(d)), d['D'].values, xc, d['D'].values*xc])\n"
            "    return sm.OLS(d['Y'].values, Z).fit().params[1]\n\n"
            "for delta in [0.0, 0.03, 0.05, 0.10]:\n"
            "    de = donut_estimate(sharp, c=C, h=0.5, delta=delta)\n"
            "    print(f'donut delta = {delta:>4}:  est = {de:.3f}')\n"
            "assert abs(donut_estimate(sharp, c=C, h=0.5, delta=0.05) - TAU) < 1.0\n"
            "print('Estimate is stable when the hole is removed — no heaping artifact.')"},
        {"md": "### 🔧 Exercise 5.1 — a McCrary-style density check\n\n"
            "Manipulation of the running variable shows up as a **jump in its "
            "density at the cutoff**: many more units land *just eligible* than "
            "*just ineligible*. Build a quick check: bin `R`, then compare the "
            "average bin count just below `c` to the average just above. For our "
            "clean simulation the ratio should be ≈ 1.\n\n"
            "Fill in the `# TODO`s; the skeleton runs as-is."},
        {"code": "def density_ratio(R, c=0.0, window=0.2, bins=40):\n"
            "    counts, edges = np.histogram(R, bins=bins)\n"
            "    ctr = 0.5*(edges[:-1] + edges[1:])\n"
            "    below = ...   # TODO: mean count for centers in [c-window, c)\n"
            "    above = ...   # TODO: mean count for centers in [c, c+window)\n"
            "    return below, above\n\n"
            "density_ratio(sharp['R'].values, c=C)"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "def density_ratio(R, c=0.0, window=0.2, bins=40):\n"
            "    counts, edges = np.histogram(R, bins=bins)\n"
            "    ctr = 0.5*(edges[:-1] + edges[1:])\n"
            "    below = counts[(ctr < c) & (ctr >= c - window)].mean()\n"
            "    above = counts[(ctr >= c) & (ctr < c + window)].mean()\n"
            "    return above / below\n\n"
            "ratio = density_ratio(sharp['R'].values, c=C)\n"
            "print(f'density ratio (above / below) = {ratio:.2f}   (~1 ⇒ no manipulation)')\n"
            "assert 0.7 < ratio < 1.3, 'clean simulation should have a smooth density at c'\n\n"
            "# Contrast: a manipulated running variable where units sort just above c.\n"
            "Rman = sharp['R'].values.copy()\n"
            "near_below = (Rman < C) & (Rman > C - 0.1)\n"
            "movers = near_below & (RNG.random(len(Rman)) < 0.6)   # 60% jump the cutoff\n"
            "Rman[movers] = C + RNG.uniform(0, 0.1, movers.sum())\n"
            "ratio_man = density_ratio(Rman, c=C)\n"
            "print(f'manipulated density ratio = {ratio_man:.2f}   (>> 1 ⇒ sorting detected)')\n"
            "assert ratio_man > 1.3, 'manipulation should show up as a density spike above c'"},
        {"md": "## 6 · Fuzzy RD — IV at the cutoff\n\n"
            "In a **fuzzy** design, crossing `c` does not flip treatment from 0 to "
            "1 — it only raises the *probability* of treatment (say 0.2 → 0.7). "
            "The outcome jump then **understates** the per-treated effect, because "
            "not everyone above `c` is actually treated.\n\n"
            "The fix is the Wald/IV ratio at the cutoff:\n\n"
            "$$\\hat\\tau_{\\text{fuzzy}} = \\frac{\\text{jump in }Y\\text{ at }c}"
            "{\\text{jump in }P(D=1)\\text{ at }c} = "
            "\\frac{\\text{reduced form}}{\\text{first stage}}.$$\n\n"
            "We simulate a fuzzy RD with a known per-treated effect and recover "
            "it."},
        {"code": "def make_fuzzy(n=8000, c=0.0, tau=8.0, slope=4.0, noise=3.0,\n"
            "               p_below=0.15, p_above=0.75):\n"
            "    \"\"\"Fuzzy RD: crossing c raises P(treated) from p_below to p_above.\"\"\"\n"
            "    R = RNG.uniform(-1, 1, n)\n"
            "    above = (R >= c).astype(float)             # the instrument: eligible side\n"
            "    prob = np.where(above == 1, p_above, p_below)\n"
            "    D = RNG.binomial(1, prob).astype(float)    # actual treatment (probabilistic)\n"
            "    Y = 30 + slope*R + tau*D + RNG.normal(0, noise, n)\n"
            "    return pd.DataFrame({'R': R, 'D': D, 'Y': Y, 'above': above})\n\n"
            "fuzzy = make_fuzzy(c=C, tau=TAU)\n"
            "print(fuzzy.groupby('above')['D'].mean().rename('P(treated)'))"},
        {"code": "def fuzzy_rd(df, c=0.0, h=0.5):\n"
            "    \"\"\"Wald ratio at the cutoff: (jump in Y) / (jump in P(D=1)).\"\"\"\n"
            "    d = df[np.abs(df['R'] - c) <= h]\n"
            "    xc = d['R'].values - c\n"
            "    Z = np.column_stack([np.ones(len(d)), d['above'].values, xc, d['above'].values*xc])\n"
            "    reduced_form = sm.OLS(d['Y'].values, Z).fit().params[1]   # jump in Y\n"
            "    first_stage  = sm.OLS(d['D'].values, Z).fit().params[1]   # jump in P(D)\n"
            "    return reduced_form / first_stage, reduced_form, first_stage\n\n"
            "late, rf, fs = fuzzy_rd(fuzzy, c=C, h=0.5)\n"
            "print(f'reduced form (jump in Y)      = {rf:.3f}')\n"
            "print(f'first stage  (jump in P(D=1)) = {fs:.3f}')\n"
            "print(f'fuzzy RD = reduced / first    = {late:.3f}   (truth = {TAU})')\n"
            "assert abs(late - TAU) < 1.5, 'Wald ratio should recover the per-treated effect'\n"
            "print('\\nDividing by the first stage restores the per-treated effect — IV at the cutoff.')"},
        {"md": "### 🔧 Exercise 6.1 — forgetting to scale\n\n"
            "A common mistake is to report the **reduced form** (the raw outcome "
            "jump) as if it were the treatment effect, forgetting that only part "
            "of the above-cutoff group is treated. Compute the reduced form alone "
            "and show it is well *below* `TAU`; then confirm that dividing by the "
            "first stage fixes it.\n\n"
            "Fill in the `# TODO`."},
        {"code": "late2, rf2, fs2 = fuzzy_rd(fuzzy, c=C, h=0.4)\n"
            "naive_fuzzy = ...   # TODO: the reduced form alone (the WRONG answer)\n"
            "# print('reduced form only:', round(naive_fuzzy, 3), ' vs truth', TAU)"},
        {"md": "### ✅ Solution 6.1"},
        {"code": "late2, rf2, fs2 = fuzzy_rd(fuzzy, c=C, h=0.4)\n"
            "naive_fuzzy = rf2                      # reporting the reduced form alone\n"
            "print(f'reduced form only = {naive_fuzzy:.3f}   (truth = {TAU}) -> too small')\n"
            "print(f'scaled (Wald)     = {late2:.3f}   (truth = {TAU}) -> correct')\n"
            "assert naive_fuzzy < TAU - 1.0, 'the raw jump understates the per-treated effect'\n"
            "assert abs(late2 - TAU) < 1.5, 'scaling by the first stage recovers the truth'"},
        {"md": "## Wrap-up & self-check\n\n"
            "- A **cutoff** on a running variable creates a local experiment: just "
            "above vs. just below is almost a coin flip.\n"
            "- **Sharp RD** identifies the ATE at the cutoff; **fuzzy RD** "
            "identifies a LATE via the **Wald ratio** (reduced form ÷ first "
            "stage).\n"
            "- The identifying assumption is **continuity** at `c` — and you "
            "estimate the jump with **local linear regression**, never a global "
            "high-order polynomial.\n"
            "- Choosing the **bandwidth** trades bias against variance; report the "
            "estimate across a range.\n"
            "- Earn the design with **validity checks**: a McCrary density test "
            "for manipulation, **placebo cutoffs** (≈0), and a **donut-hole** "
            "check (stable).\n\n"
            "**You're ready for Week 10** if you can state what each design "
            "identifies, recover a known jump in code, and explain what each "
            "check would catch. Next week: difference-in-differences trades a "
            "cutoff in space for a break in time."},
    ],
}
