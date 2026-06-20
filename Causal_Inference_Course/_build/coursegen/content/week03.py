# -*- coding: utf-8 -*-
"""Week 3 — Randomized Experiments & A/B Testing. Content module."""

WEEK = {
    "number": 3,
    "slug": "randomized_experiments",
    "title": "Randomized Experiments & A/B Testing",
    "block": "Block I — Foundations",
    "subtitle": "Designing and analyzing experiments — the cleanest route to "
                "causation — and the failure modes that appear at scale.",
    "deliverable": "Concept Set 3 — design trustworthy experiments; "
                   "Lab 1 — design and analyze an A/B test (power, CUPED, ITT).",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), concept set (1.5h), lab (2–3h).",
    "one_sentence": "Random assignment makes treatment independent of the "
        "potential outcomes, so a simple difference in means is an unbiased "
        "causal effect — but at scale, power, variance, compliance, "
        "interference, and peeking are what actually decide whether you can "
        "trust the answer.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Explain why randomization makes treatment independent of the potential "
        "outcomes, and why that turns a difference in means into a causal effect.",
        "Choose among completely randomized, stratified, and block designs, and "
        "say what covariate balance buys you and how to check it.",
        "Compute a required sample size from a baseline rate, a minimum "
        "detectable effect, and a target power — and sanity-check it by "
        "simulation.",
        "Apply CUPED (or covariate adjustment) to cut variance using a "
        "pre-period covariate, and verify the standard error shrinks while the "
        "estimate stays unbiased.",
        "Distinguish intention-to-treat from per-protocol under noncompliance, "
        "and name the failure modes of online tests — peeking, SRM, and "
        "interference.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Cunningham, The Mixtape — potential outcomes & RCTs.",
         "look_for": "why random assignment makes treatment independent of "
                     "potential outcomes, so selection bias is zero by design."},
        {"text": "Kohavi, Tang & Xu, Trustworthy Online Controlled Experiments "
                 "(selected chapters).",
         "look_for": "the most common ways large-scale A/B tests are fooled — "
                     "peeking, sample-ratio mismatch (SRM), and interference."},
    ],
    "optional_readings": [
        {"text": "Huntington-Klein, The Effect — the experiments chapter.",
         "note": "A gentle, example-driven treatment of why experiments work."},
        {"text": "Gerber & Green, Field Experiments.",
         "note": "The canonical reference for design, blocking, and "
                 "noncompliance in real field settings."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "Why randomization works",
         "body": "Each unit has two potential outcomes, Y(1) under treatment and "
            "Y(0) under control; we only ever see one. The bias in a naive "
            "comparison is selection bias — the treated and control groups differ "
            "in their Y(0) before any treatment. Randomly assigning treatment "
            "makes the assignment Z independent of (Y(0), Y(1)). Independence "
            "kills selection bias, so the two groups are exchangeable and a simple "
            "difference in means, E[Y | Z=1] − E[Y | Z=0], equals the average "
            "treatment effect E[Y(1) − Y(0)]. No regression, no adjustment, no "
            "untestable graph — the design does the identification."},
        {"heading": "Three designs, and what balance buys you",
         "body": "Randomization makes covariates balanced in expectation, but any "
            "single experiment can still draw an unlucky split. Design choices "
            "reduce that risk and tighten precision.",
         "bullets": [
            [("Completely randomized:  ", {"bold": True}),
             ("flip a coin per unit. Simplest; balance holds only on average, so "
              "small samples can look lopsided.", {})],
            [("Stratified / blocked:  ", {"bold": True}),
             ("randomize within strata (e.g. country, device, baseline-risk "
              "tier) so each block is balanced by construction. Cuts variance "
              "and guarantees balance on the blocking variables.", {})],
            [("Check, don't assume:  ", {"bold": True}),
             ("report a covariate-balance table (standardized mean differences). "
              "A large imbalance after randomization is a flag for a bug or a "
              "sample-ratio mismatch, not something to 'fix' by adjusting away.", {})],
         ]},
        {"heading": "Power, MDE, and sample size",
         "body": "Power is the probability of detecting a true effect of a given "
            "size. The minimum detectable effect (MDE) is the smallest effect "
            "your design can reliably catch at your chosen power and "
            "significance. These three — sample size, MDE, and power — trade off "
            "against one another, and you must fix two to solve for the third "
            "BEFORE you launch.",
         "bullets": [
            [("Plan first:  ", {"bold": True}),
             ("decide α (false-positive rate), power (often 0.80), the baseline "
              "rate, and the MDE you care about; then solve for n.", {})],
            [("Bigger n, smaller MDE:  ", {"bold": True}),
             ("the detectable effect shrinks like 1/√n, so halving the MDE "
              "roughly quadruples the sample.", {})],
            [("Underpowered ≠ null:  ", {"bold": True}),
             ("a non-significant result in a small test means 'we couldn't "
              "tell,' not 'there is no effect.'", {})],
         ],
         "callout": {"title": "Variance reduction is free power",
            "color": "GREEN",
            "lines": ["CUPED and covariate adjustment use a PRE-experiment "
                      "covariate to explain away outcome noise. The estimate "
                      "stays unbiased (the covariate is pre-treatment) but the "
                      "standard error shrinks — often by 30–50%.",
                      "A smaller SE is equivalent to a larger sample: you reach "
                      "the same MDE faster, for free."]}},
        {"heading": "ITT vs. per-protocol under noncompliance",
         "body": "Real experiments leak: some assigned-to-treat units don't take "
            "the treatment (noncompliance), and some units drop out (attrition).",
         "bullets": [
            [("Intention-to-treat (ITT):  ", {"bold": True}),
             ("analyze by ASSIGNMENT, ignoring what people actually did. "
              "Randomization is intact, so ITT is unbiased for the effect of "
              "being OFFERED treatment — but it is diluted toward zero by "
              "noncompliance.", {})],
            [("Per-protocol:  ", {"bold": True}),
             ("compare by treatment RECEIVED. This breaks randomization: "
              "compliers differ from non-compliers, so per-protocol is generally "
              "biased.", {})],
            [("Recover the effect on compliers:  ", {"bold": True}),
             ("scaling ITT by the compliance rate (an instrumental-variables / "
              "CACE estimate) recovers the effect on compliers — a preview of "
              "Week 9.", {})],
         ],
         "callout": {"title": "The most common ways an A/B test lies to you",
            "color": "RED",
            "lines": ["Peeking — checking the p-value repeatedly and stopping at "
                      "the first 'significant' look — inflates the false-positive "
                      "rate far above 5%.",
                      "Sample-ratio mismatch (SRM) — the observed split differs "
                      "from the intended 50/50 — signals a logging or assignment "
                      "bug that invalidates the comparison.",
                      "Interference — one unit's treatment affects another "
                      "(network effects, shared marketplace supply) — breaks "
                      "SUTVA and biases the estimate."]}},
    ],
    "problem_set": {
        "label": "Concept Set 3",
        "title": "Designing trustworthy experiments",
        "intro": "For each problem, reason from the design — what randomization "
            "guarantees and what it does not. Show your arithmetic where asked, "
            "and state the assumption that each conclusion depends on. Try all "
            "five before you look.",
        "problems": [
            {"title": "Sizing the test",
             "prompt": "Your checkout page converts at a baseline rate of 10%. "
                "You care about an absolute lift of 2 percentage points (to 12%). "
                "You want 80% power at a two-sided α = 0.05, with a balanced "
                "50/50 split. Roughly how many users per arm do you need, and "
                "what happens to that number if you instead care about a 1-point "
                "lift?",
             "solution_title": "≈ 3,800 per arm for a 2-pt lift; a 1-pt lift "
                "needs roughly four times as many.",
             "solution": [
                "Two-proportion sample size: n ≈ (z_{α/2}√(2 p̄(1−p̄)) + "
                "z_β√(p₀(1−p₀)+p₁(1−p₁)))² / (p₁−p₀)². With p₀=0.10, p₁=0.12, "
                "z_{α/2}=1.96, z_β=0.84, this gives about 3,800 per arm "
                "(~7,600 total).",
                "Power scales with the effect size relative to noise, and the "
                "MDE shrinks like 1/√n. So halving the detectable effect "
                "(2 pts → 1 pt) roughly QUADRUPLES the required sample — about "
                "15,000+ per arm.",
                "Lesson: tiny effects are expensive. Decide the smallest effect "
                "worth detecting BEFORE launch; that choice, not the data, sets "
                "the budget."]},
            {"title": "Why peeking lies",
             "prompt": "An analyst watches the dashboard daily and plans to ship "
                "the moment the p-value drops below 0.05. The treatment is in "
                "truth identical to control (a true null). Why does this inflate "
                "the false-positive rate above 5%, and what is the fix?",
             "solution_title": "Repeated looks are repeated chances to cross the "
                "threshold — the fixed-sample α no longer holds.",
             "solution": [
                "A single test at α = 0.05 rejects a true null 5% of the time. "
                "But each additional look is another independent-ish opportunity "
                "for the wandering test statistic to cross ±1.96 by chance, so "
                "the chance of EVER crossing grows well past 5% (often 20–30% "
                "with daily peeking).",
                "Stopping at the first significant look selects the luckiest "
                "moment — classic multiple testing across time. The reported "
                "p-value is no longer valid.",
                "Fixes: fix the sample size in advance and look once; or use a "
                "sequential method designed for continuous monitoring "
                "(group-sequential boundaries, alpha-spending, or always-valid "
                "confidence sequences)."]},
            {"title": "ITT vs. per-protocol",
             "prompt": "In a trial of a wellness program, 60% of those assigned "
                "to treatment actually enroll, and healthier people are more "
                "likely to enroll. ITT compares groups by assignment; "
                "per-protocol compares enrollees to non-enrollees. Which estimate "
                "is unbiased, and for what quantity?",
             "solution_title": "ITT is unbiased for the effect of being OFFERED "
                "the program; per-protocol is biased.",
             "solution": [
                "ITT keeps the randomization intact — it compares the assigned "
                "groups regardless of enrollment — so it is unbiased for the "
                "effect of the OFFER (the policy you can actually deploy). Its "
                "cost: it is diluted toward zero because 40% never took up.",
                "Per-protocol compares enrollees to non-enrollees, but those "
                "groups differ in health, which also drives the outcome. "
                "Randomization no longer protects the comparison, so per-protocol "
                "is confounded and generally biased.",
                "To recover the effect ON the compliers, scale ITT by the "
                "compliance rate (ITT / 0.60) — the instrumental-variables / "
                "CACE estimand we formalize in Week 9."]},
            {"title": "Spotting a sample-ratio mismatch",
             "prompt": "You intended a 50/50 split. After a week you have "
                "498,000 users in control and 502,000 in treatment — but a "
                "chi-square test against 50/50 returns p ≈ 0.001. The treatment "
                "metric looks great. What does the SRM imply, and what should you "
                "do?",
             "solution_title": "The split itself is broken — do not trust the "
                "metric until you find the cause.",
             "solution": [
                "Under a correct 50/50 randomization the counts should match the "
                "intended ratio up to sampling noise. A p ≈ 0.001 against 50/50 "
                "means the imbalance is far larger than chance — a sample-ratio "
                "mismatch.",
                "SRM almost always signals a bug in assignment, logging, or "
                "filtering (e.g. treatment users with errors silently dropped, "
                "bots routed to one arm, redirect latency). The two groups are no "
                "longer comparable, so any effect estimate is suspect — often the "
                "'great' result is the artifact.",
                "Do not analyze or ship. Diagnose the pipeline, fix the cause, "
                "and re-run. An SRM is a hard stop, not a footnote."]},
            {"title": "Interference breaks SUTVA",
             "prompt": "A ride-share app A/B tests a new rider discount. Treated "
                "riders request more rides, which soaks up drivers and lengthens "
                "wait times for the control riders in the same city. Give the "
                "SUTVA violation and explain why the naive estimate is wrong.",
             "solution_title": "One unit's treatment affects another's outcome — "
                "SUTVA fails, and the control group is contaminated.",
             "solution": [
                "SUTVA requires that a unit's outcome depend only on its OWN "
                "treatment (no interference). Here a treated rider's extra demand "
                "degrades a control rider's wait time — the control outcome "
                "depends on others' treatment.",
                "The control arm is no longer a clean counterfactual: it is worse "
                "than a no-experiment world, so the treatment-minus-control gap "
                "overstates the true effect (and may not generalize once everyone "
                "is treated and supply is strained everywhere).",
                "Designs that respect interference: randomize at the cluster "
                "level (whole cities/markets), use switchback (time-based) "
                "designs, or model the marketplace equilibrium explicitly."]},
        ],
    },
    "lab": {
        "label": "Lab 1",
        "title": "Design and analyze an A/B test",
        "goal": "plan a test from first principles and analyze it end to end — "
            "size it for a target MDE, simulate it with a known effect, estimate "
            "with a difference in means and a confidence interval, cut variance "
            "with CUPED, and compare ITT to per-protocol under noncompliance. "
            "Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Power and sample size",
             "body": "Fix the baseline conversion rate, the minimum detectable "
                "effect, α, and power. Solve for the per-arm sample size with the "
                "two-proportion formula, then keep that n for the rest of the lab.",
             "code_r": 'p0 <- 0.10; mde <- 0.02; alpha <- 0.05; power <- 0.80\n'
                'p1 <- p0 + mde\n'
                'za <- qnorm(1 - alpha/2); zb <- qnorm(power)\n'
                'pbar <- (p0 + p1) / 2\n'
                'n <- ((za*sqrt(2*pbar*(1-pbar)) +\n'
                '       zb*sqrt(p0*(1-p0) + p1*(1-p1)))^2) / mde^2\n'
                'cat(sprintf("required n per arm = %d\\n", ceiling(n)))',
             "code_python": "import numpy as np\nfrom scipy import stats\n"
                "p0, mde, alpha, power = 0.10, 0.02, 0.05, 0.80\n"
                "p1 = p0 + mde\n"
                "za = stats.norm.ppf(1 - alpha/2); zb = stats.norm.ppf(power)\n"
                "pbar = (p0 + p1) / 2\n"
                "n = ((za*np.sqrt(2*pbar*(1-pbar)) +\n"
                "      zb*np.sqrt(p0*(1-p0) + p1*(1-p1)))**2) / mde**2\n"
                "n_per_arm = int(np.ceil(n))\n"
                'print(f"required n per arm = {n_per_arm}")'},
            {"heading": "Step 2 · Simulate an experiment with a known effect",
             "body": "Generate a pre-period covariate, randomly assign treatment "
                "50/50, and add a TRUE additive effect. Knowing the truth lets "
                "you check every estimate that follows.",
             "code_r": 'set.seed(7); n <- 8000; TRUE_ATE <- 2.0\n'
                'pre <- rnorm(n, 50, 10)\n'
                'base <- 0.6*pre + rnorm(n, 0, 8)\n'
                'Z <- rbinom(n, 1, 0.5)\n'
                'Y <- base + TRUE_ATE*Z + rnorm(n, 0, 5)',
             "code_python": "rng = np.random.default_rng(7)\n"
                "n = 8000; TRUE_ATE = 2.0\n"
                "pre  = rng.normal(50, 10, n)\n"
                "base = 0.6*pre + rng.normal(0, 8, n)\n"
                "Z = rng.binomial(1, 0.5, n)\n"
                "Y = base + TRUE_ATE*Z + rng.normal(0, 5, n)"},
            {"heading": "Step 3 · Difference in means + confidence interval",
             "body": "The whole payoff of randomization: a plain difference in "
                "means is an unbiased ATE. Build its standard error and a 95% CI "
                "and confirm the truth lands inside.",
             "code_r": 'yt <- Y[Z==1]; yc <- Y[Z==0]\n'
                'ate <- mean(yt) - mean(yc)\n'
                'se  <- sqrt(var(yt)/length(yt) + var(yc)/length(yc))\n'
                'cat(sprintf("ATE=%.3f  CI=[%.3f, %.3f]  truth=%.1f\\n",\n'
                '            ate, ate-1.96*se, ate+1.96*se, TRUE_ATE))',
             "code_python": "yt, yc = Y[Z==1], Y[Z==0]\n"
                "ate = yt.mean() - yc.mean()\n"
                "se  = np.sqrt(yt.var(ddof=1)/yt.size + yc.var(ddof=1)/yc.size)\n"
                'print(f"ATE={ate:.3f}  CI=[{ate-1.96*se:.3f}, '
                '{ate+1.96*se:.3f}]  truth={TRUE_ATE}")'},
            {"heading": "Step 4 · CUPED variance reduction",
             "body": "Use the pre-period covariate to subtract predictable noise. "
                "Theta is the regression slope of Y on the (centered) covariate; "
                "the adjusted outcome has the same mean difference but a smaller "
                "standard error.",
             "code_r": 'theta <- cov(Y, pre) / var(pre)\n'
                'Ycuped <- Y - theta * (pre - mean(pre))\n'
                'at <- Ycuped[Z==1]; ac <- Ycuped[Z==0]\n'
                'ate_c <- mean(at) - mean(ac)\n'
                'se_c  <- sqrt(var(at)/length(at) + var(ac)/length(ac))\n'
                'cat(sprintf("CUPED ATE=%.3f  SE=%.3f  (vs naive SE=%.3f)\\n",\n'
                '            ate_c, se_c, se))',
             "code_python": "theta = np.cov(Y, pre)[0, 1] / pre.var(ddof=1)\n"
                "Ycuped = Y - theta * (pre - pre.mean())\n"
                "at, ac = Ycuped[Z==1], Ycuped[Z==0]\n"
                "ate_c = at.mean() - ac.mean()\n"
                "se_c  = np.sqrt(at.var(ddof=1)/at.size + ac.var(ddof=1)/ac.size)\n"
                'print(f"CUPED ATE={ate_c:.3f}  SE={se_c:.3f}  '
                '(vs naive SE={se:.3f})")\n'
                "assert se_c < se   # variance reduction"},
            {"heading": "Step 5 · ITT vs. per-protocol under noncompliance",
             "body": "Introduce one-sided noncompliance where healthier units are "
                "more likely to comply. ITT (by assignment) stays unbiased for "
                "the offer effect; per-protocol (by uptake) is confounded; "
                "ITT / compliance recovers the compliers' effect.",
             "code_r": 'set.seed(7); n <- 30000; TRUE <- 3.0\n'
                'Z <- rbinom(n, 1, 0.5)\n'
                'health <- rnorm(n)\n'
                'comply <- rbinom(n, 1, plogis(0.5 + 1.0*health))\n'
                'D <- Z * comply\n'
                'Y <- 10 + 4*health + TRUE*D + rnorm(n, 0, 3)\n'
                'itt <- mean(Y[Z==1]) - mean(Y[Z==0])\n'
                'pp  <- mean(Y[D==1]) - mean(Y[D==0])\n'
                'cace <- itt / mean(D[Z==1])\n'
                'cat(sprintf("ITT=%.2f  per-protocol=%.2f  CACE=%.2f\\n",\n'
                '            itt, pp, cace))',
             "code_python": "rng = np.random.default_rng(7)\n"
                "n = 30000; TRUE = 3.0\n"
                "Z = rng.binomial(1, 0.5, n)\n"
                "health = rng.normal(size=n)\n"
                "p_comply = 1/(1 + np.exp(-(0.5 + 1.0*health)))\n"
                "comply = rng.binomial(1, p_comply, n)\n"
                "D = Z * comply\n"
                "Y = 10 + 4*health + TRUE*D + rng.normal(0, 3, n)\n"
                "itt  = Y[Z==1].mean() - Y[Z==0].mean()\n"
                "pp   = Y[D==1].mean() - Y[D==0].mean()\n"
                "cace = itt / D[Z==1].mean()\n"
                'print(f"ITT={itt:.2f}  per-protocol={pp:.2f}  CACE={cace:.2f}")'},
        ],
        "expected": "Step 1 returns about 3,800 per arm. The Step 3 difference "
            "in means sits near 2.0 with the truth inside the CI. CUPED keeps the "
            "estimate near 2.0 but cuts the standard error noticeably (often "
            "15–40%). In Step 5, ITT lands below the true 3.0 (diluted by "
            "noncompliance), per-protocol is inflated well above 3.0 (confounded "
            "by health), and CACE recovers ≈ 3.0. Same data, three numbers — only "
            "the design logic tells you which answers which question.",
        "submit": [
            "Push your code and a short README reporting the required sample "
            "size, the difference-in-means CI, the CUPED SE reduction, and the "
            "ITT/per-protocol/CACE trio.",
            "Add one sentence on why per-protocol is biased here but ITT is not.",
            "Bring your active-reading sentences (from the guided reading) to lab.",
        ],
    },
    "self_check": [
        "Explain why random assignment makes Z independent of (Y(0), Y(1)).",
        "Compute a required sample size from a baseline rate, an MDE, and a "
        "target power.",
        "Say what CUPED does to the estimate and to the standard error, and why.",
        "State which of ITT and per-protocol is unbiased, and for what estimand.",
        "Name three ways a large-scale A/B test gets fooled and what each implies.",
    ],
    "next_week": {
        "heading": "Coming up: Week 4 — Causal graphs (DAGs)",
        "teaser": "When you can't randomize, you need a language for stating "
            "exactly which comparisons are fair. We build directed acyclic "
            "graphs, read off back-door paths with d-separation, and turn "
            "'what should I adjust for?' into a rule you can check. Skim Pearl's "
            "Primer Chapter 2 to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 3", "items": [
            {"t": "Why randomize?", "d": "Random assignment makes treatment "
             "independent of the potential outcomes."},
            {"t": "Designs", "d": "Completely randomized, stratified, and block "
             "designs — and covariate balance."},
            {"t": "Power & MDE", "d": "Sizing a test before you launch; the "
             "sample / MDE / power triangle."},
            {"t": "Variance reduction", "d": "CUPED and covariate adjustment — "
             "free power from a pre-period covariate."},
            {"t": "Noncompliance", "d": "ITT vs. per-protocol, attrition, and the "
             "effect on compliers."},
            {"t": "Failure modes at scale", "d": "Peeking, SRM, interference, and "
             "multiple testing online."},
        ]},
        {"type": "content", "kicker": "The promise",
         "title": "The experiment is the cleanest route to causation", "bullets": [
            "Confounding is the central obstacle in observational data — common "
            "causes that drive both treatment and outcome.",
            "Randomization removes it by construction: the coin flip has no "
            "common cause with the outcome.",
            "So a simple difference in means is already an unbiased causal "
            "effect — no graph, no adjustment.",
            ("That is why the RCT is the benchmark every other method tries to "
             "match.", 1),
            "The catch: at scale, the threats move from identification to "
            "design, power, and operations.",
         ],
         "note": {"title": "This week",
            "body": "Design an experiment, size it, analyze it — and learn the "
            "specific ways large online tests get fooled."}},
        {"type": "compare", "kicker": "Where this sits",
         "title": "Experiments vs. observational adjustment", "columns": [
            {"head": "Randomized experiment", "points": [
                "Design guarantees exchangeability.",
                "Difference in means is unbiased.",
                "Assumptions are about operations, not graphs.",
                "Gold standard — when feasible and ethical."]},
            {"head": "Observational study", "points": [
                "Must assume no unmeasured confounding.",
                "Needs adjustment, matching, or weighting.",
                "Identification is an untestable argument.",
                "The rest of the course — when you can't randomize."]},
        ]},

        {"type": "section", "kicker": "Part 1", "title": "Why randomization works",
         "subtitle": "The one-line miracle: assignment independent of the "
            "potential outcomes turns a difference in means into a causal effect."},
        {"type": "content", "kicker": "The setup",
         "title": "Potential outcomes and selection bias", "bullets": [
            "Each unit has Y(1) and Y(0); the individual effect Y(1) − Y(0) is "
            "never both observed.",
            "A naive comparison E[Y|Z=1] − E[Y|Z=0] equals the ATE PLUS a "
            "selection-bias term.",
            "Selection bias = how the groups differ in Y(0) before treatment — "
            "the treated may be sicker, richer, keener.",
            "Adjustment tries to estimate that term; randomization sets it to "
            "zero.",
         ],
         "note": {"title": "The decomposition",
            "body": "naive gap = ATT + (E[Y(0)|Z=1] − E[Y(0)|Z=0]). The second "
            "term is selection bias."}},
        {"type": "statement",
         "quote": "Randomize the treatment and Z ⟂ (Y(0), Y(1)): the groups are "
            "exchangeable, so E[Y | Z=1] − E[Y | Z=0] = E[Y(1) − Y(0)].",
         "attribution": "The coin flip shares no common cause with the outcome, "
            "so there is no back-door path to block. The design does the "
            "identification that observational studies must argue for."},
        {"type": "content", "kicker": "What you still must defend",
         "title": "Randomization is necessary, not sufficient", "bullets": [
            "SUTVA: one unit's outcome depends only on its OWN treatment "
            "(no interference).",
            "Consistency: the treatment is well-defined and the same for everyone "
            "who gets it.",
            "Full compliance and no differential attrition — or you analyze by "
            "intention to treat.",
            "A correct assignment mechanism — no leakage, no sample-ratio "
            "mismatch.",
         ],
         "note": {"title": "Reframe",
            "body": "Randomization buys identification. Design and operations buy "
            "you a trustworthy estimate."}},

        {"type": "section", "kicker": "Part 2", "title": "Designs & balance",
         "subtitle": "Completely randomized, stratified, and block designs — and "
            "how to check that the split came out fair."},
        {"type": "compare", "kicker": "Three ways to assign",
         "title": "Pick the design that controls the right variance", "columns": [
            {"head": "Completely randomized", "points": [
                "Independent coin flip per unit.",
                "Balance holds only on average.",
                "Simple; risk of an unlucky split."]},
            {"head": "Stratified", "points": [
                "Randomize within strata (country, device).",
                "Balanced on strata by construction.",
                "Lower variance for strong predictors."]},
            {"head": "Block / matched", "points": [
                "Form similar blocks, randomize inside each.",
                "Tightest balance on blocking variables.",
                "Great for small samples."]},
        ]},
        {"type": "content", "kicker": "Diagnostics",
         "title": "Check covariate balance — then leave it alone", "bullets": [
            "Report standardized mean differences on pre-treatment covariates "
            "across arms.",
            "Small SMDs (rule of thumb < 0.1) say the randomization looks healthy.",
            "A big imbalance is a flag for a bug or SRM — investigate, don't "
            "silently 'adjust it away.'",
            "Pre-specified covariate adjustment for precision is fine; "
            "data-dredged adjustment is not.",
         ],
         "note": {"title": "Balance ≠ proof",
            "body": "Balance on MEASURED covariates is reassuring; randomization "
            "also balances the UNMEASURED ones in expectation."}},

        {"type": "section", "kicker": "Part 3", "title": "Power, MDE & sample size",
         "subtitle": "The three quantities you must pin down before launch — and "
            "why you can never solve for all three at once."},
        {"type": "content", "kicker": "Definitions",
         "title": "Power and the minimum detectable effect", "bullets": [
            "Power = P(reject the null | a true effect of a given size exists). "
            "Convention: 0.80.",
            "MDE = the smallest effect your design can reliably detect at your α "
            "and power.",
            "Sample size, MDE, and power trade off: fix any two and the third is "
            "determined.",
            ("Detectable effect shrinks like 1/√n.", 1),
            ("Halving the MDE roughly quadruples the sample.", 1),
         ],
         "note": {"title": "Underpowered ≠ null",
            "body": "A non-significant result in a small test means 'we couldn't "
            "tell,' not 'no effect.'"}},
        {"type": "steps", "kicker": "Sizing a two-proportion test",
         "title": "From baseline rate and MDE to a number", "steps": [
            {"title": "Fix the inputs", "body": "baseline p₀, MDE, α (e.g. 0.05), "
             "power (e.g. 0.80)."},
            {"title": "Get the z-scores", "body": "z_{α/2}=1.96, z_β=0.84 for a "
             "two-sided test at 80% power."},
            {"title": "Plug in the formula", "body": "n per arm ∝ (z-terms)² / "
             "(MDE)² — variance over effect, squared."},
            {"title": "Sanity-check by simulation", "body": "simulate at that n "
             "and confirm empirical power ≈ target."},
         ],
         "note": "Always verify the formula with a quick simulation — it catches "
            "wrong assumptions about the test."},
        {"type": "table", "kicker": "The cost of precision",
         "title": "How n scales with the effect you chase",
         "headers": ["Baseline", "Lift (MDE)", "≈ n per arm (80% power)"],
         "rows": [
            ["10%", "+4 pts → 14%", "≈ 1,000"],
            ["10%", "+2 pts → 12%", "≈ 3,800"],
            ["10%", "+1 pt → 11%", "≈ 15,000"],
            ["10%", "+0.5 pt → 10.5%", "≈ 60,000"],
         ],
         "note": {"title": "Read the pattern",
            "body": "Each halving of the MDE roughly quadruples the sample. "
            "Small effects are expensive — decide what's worth detecting first."}},

        {"type": "section", "kicker": "Part 4", "title": "Variance reduction",
         "subtitle": "CUPED and covariate adjustment: use a pre-period covariate "
            "to buy precision without touching the estimate."},
        {"type": "content", "kicker": "The idea",
         "title": "CUPED — controlled experiment using pre-experiment data",
         "bullets": [
            "Subtract the predictable part of the outcome using a PRE-treatment "
            "covariate (often the same metric, pre-period).",
            "Y_cuped = Y − θ (X_pre − mean), with θ = Cov(Y, X_pre) / Var(X_pre).",
            "Because X_pre is pre-treatment, it is balanced across arms — the "
            "estimate stays unbiased.",
            "Variance drops by roughly the squared correlation; SE reductions of "
            "30–50% are common.",
         ],
         "note": {"title": "Free power",
            "body": "A smaller SE is equivalent to a larger sample. You reach the "
            "same MDE faster, for free."}},
        {"type": "compare", "kicker": "Two routes to the same gain",
         "title": "CUPED vs. regression adjustment", "columns": [
            {"head": "CUPED", "points": [
                "Transform the outcome, then difference in means.",
                "θ from the pre-period covariate.",
                "Standard at large tech firms."]},
            {"head": "Covariate-adjusted OLS", "points": [
                "Regress Y on Z plus pre-treatment covariates.",
                "Coefficient on Z is the adjusted ATE.",
                "Equivalent gain; identical logic."]},
            {"head": "The one rule", "points": [
                "Covariates must be PRE-treatment.",
                "Post-treatment controls reintroduce bias.",
                "Pre-specify them to avoid fishing."]},
        ]},

        {"type": "section", "kicker": "Part 5",
         "title": "Noncompliance & attrition",
         "subtitle": "Real experiments leak. Intention-to-treat keeps the "
            "randomization; per-protocol throws it away."},
        {"type": "compare", "kicker": "Two ways to analyze a leaky trial",
         "title": "ITT vs. per-protocol", "columns": [
            {"head": "Intention-to-treat", "points": [
                "Analyze by ASSIGNMENT.",
                "Randomization intact → unbiased for the OFFER effect.",
                "Diluted toward zero by noncompliance.",
                "The policy-relevant number."]},
            {"head": "Per-protocol", "points": [
                "Analyze by treatment RECEIVED.",
                "Compliers differ from non-compliers.",
                "Randomization broken → generally biased.",
                "Tempting but confounded."]},
        ]},
        {"type": "content", "kicker": "Recovering the compliers' effect",
         "title": "Scale ITT by the compliance rate", "bullets": [
            "Under one-sided noncompliance, CACE = ITT / (share who comply when "
            "assigned).",
            "This is the instrumental-variables estimand with assignment as the "
            "instrument.",
            "It identifies the effect on COMPLIERS, not the whole population.",
            ("We formalize instruments and the LATE in Week 9.", 1),
         ],
         "note": {"title": "Attrition too",
            "body": "Differential dropout reintroduces selection. Track it, "
            "report it, and bound its impact."}},
        {"type": "statement",
         "quote": "When people don't comply, ITT answers a real question — what "
            "happens if we OFFER the treatment — even though it isn't the effect "
            "of taking it.",
         "attribution": "Per-protocol answers a question you didn't randomize, so "
            "it usually answers it wrong. Report ITT; estimate the compliers' "
            "effect with an instrument."},

        {"type": "section", "kicker": "Part 6",
         "title": "How A/B tests get fooled at scale",
         "subtitle": "Peeking, sample-ratio mismatch, interference, and multiple "
            "testing — the operational failure modes of online experiments."},
        {"type": "content", "kicker": "Failure 1",
         "title": "Peeking inflates the false-positive rate", "bullets": [
            "Checking the p-value repeatedly and stopping at the first "
            "'significant' look is multiple testing across time.",
            "Each look is another chance for a true null to cross the threshold "
            "by luck.",
            "Daily peeking can push the false-positive rate from 5% to 20–30%.",
            "Fix: fix n in advance and look once, OR use sequential / "
            "always-valid methods.",
         ],
         "note": {"title": "The discipline",
            "body": "Pre-register the sample size and the stopping rule. Don't let "
            "the dashboard decide when to stop."}},
        {"type": "content", "kicker": "Failure 2",
         "title": "Sample-ratio mismatch (SRM) — a hard stop", "bullets": [
            "Intended 50/50 but the observed split fails a chi-square test "
            "against the target ratio.",
            "Almost always a bug: assignment, logging, filtering, redirect "
            "latency, or bots.",
            "The arms are no longer comparable — any effect estimate is suspect.",
            "Do not ship. Find the cause and re-run; an SRM invalidates the test.",
         ],
         "note": {"title": "Check it first",
            "body": "An SRM check should be the first thing you run, before you "
            "ever look at the metric."}},
        {"type": "content", "kicker": "Failure 3",
         "title": "Interference breaks SUTVA", "bullets": [
            "One unit's treatment affects another's outcome — network effects, "
            "shared marketplace supply, congestion.",
            "Treated users can degrade (or boost) the control group, "
            "contaminating the counterfactual.",
            "The naive difference then over- or under-states the true effect.",
            "Designs: cluster randomization (whole markets), switchback "
            "(time-based) tests, equilibrium models.",
         ],
         "note": {"title": "The tell",
            "body": "If treatment changes a shared resource, your control group "
            "is no longer a clean baseline."}},
        {"type": "content", "kicker": "Failure 4",
         "title": "Many metrics, many tests", "bullets": [
            "Online tests track dozens of metrics; at α=0.05, false positives "
            "accumulate fast.",
            "Twenty independent null metrics give a ~64% chance of at least one "
            "'significant' hit.",
            "Pre-declare one primary metric; treat the rest as exploratory.",
            "Correct for multiplicity (e.g. Bonferroni, FDR) when you must test "
            "many.",
         ],
         "note": {"title": "Discipline beats cleverness",
            "body": "A pre-registered primary metric is the single best defense "
            "against fooling yourself."}},

        {"type": "section", "kicker": "Part 7", "title": "Two real cases",
         "subtitle": "A large-scale technology A/B test and a randomized field "
            "experiment — the same logic, very different operations."},
        {"type": "steps", "kicker": "Case A · A large online experiment",
         "title": "Shipping a UI change to millions of users", "steps": [
            {"title": "Design", "body": "50/50 randomization by user; pre-declare "
             "the primary metric and the sample size."},
            {"title": "Guardrails", "body": "run an SRM check, monitor "
             "interference and latency, apply CUPED for power."},
            {"title": "Analyze", "body": "difference in means with a CI on the "
             "primary metric; no peeking — wait for n."},
            {"title": "Decide", "body": "ship only if the primary metric clears "
             "the bar and guardrails hold."},
         ],
         "note": "Most of the trustworthiness comes from design and guardrails, "
            "not from a fancier estimator."},
        {"type": "steps", "kicker": "Case B · A randomized field experiment",
         "title": "An agricultural trial across many plots", "steps": [
            {"title": "Block the plots", "body": "group by field / soil / region, "
             "then randomize treatment within each block."},
            {"title": "Why block", "body": "soil and weather dominate yield; "
             "blocking removes that variance and guarantees balance."},
            {"title": "Watch spillover", "body": "fertilizer or pests can cross "
             "plot boundaries — interference, so use buffer rows."},
            {"title": "Analyze", "body": "difference in means within blocks; "
             "report the effect with its CI."},
         ],
         "note": "Fisher's agricultural trials are where randomization and "
            "blocking were invented — the ideas long predate the web."},
        {"type": "table", "kicker": "Same logic, different threats",
         "title": "Where the risk lives in each setting",
         "headers": ["Concern", "Online A/B test", "Field experiment"],
         "rows": [
            ["Unit", "User / session", "Plot / village"],
            ["Main threat", "Peeking, SRM, interference", "Spillover, attrition"],
            ["Variance trick", "CUPED on pre-period metric", "Blocking by "
             "field/region"],
            ["Compliance", "Exposure logging", "Take-up of the program"],
         ]},
        {"type": "statement",
         "quote": "Design the test, size it, run an SRM check, look once, and "
            "report ITT with a confidence interval.",
         "attribution": "This week: size a real test, simulate it, recover the "
            "truth with a difference in means, cut variance with CUPED, and watch "
            "peeking inflate your error rate. See you in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · Random assignment makes the difference in means unbiased\n\n"
            "We simulate an experiment where we **know** the true average "
            "treatment effect is `2.0`. A pre-period covariate `pre` drives the "
            "baseline outcome (we'll exploit it later for CUPED). Because "
            "treatment `Z` is assigned by a coin flip, `Z` is independent of the "
            "potential outcomes — so the plain difference in means "
            "`E[Y|Z=1] − E[Y|Z=0]` is an unbiased estimate of the effect."},
        {"code": "import statsmodels.api as sm\nfrom scipy import stats\n\n"
            "TRUE_ATE = 2.0\n\n"
            "def simulate_experiment(n=8000, ate=TRUE_ATE):\n"
            "    \"\"\"One randomized experiment with a known additive effect.\"\"\"\n"
            "    pre  = RNG.normal(50, 10, n)                 # pre-period covariate\n"
            "    base = 0.6 * pre + RNG.normal(0, 8, n)       # baseline outcome\n"
            "    Z    = RNG.binomial(1, 0.5, n)               # randomized 50/50\n"
            "    Y    = base + ate * Z + RNG.normal(0, 5, n)  # TRUE effect = ate\n"
            "    return pd.DataFrame({'Z': Z, 'Y': Y, 'pre': pre})\n\n"
            "df = simulate_experiment()\n"
            "yt = df.loc[df.Z == 1, 'Y']\n"
            "yc = df.loc[df.Z == 0, 'Y']\n"
            "ate = yt.mean() - yc.mean()\n"
            "print(f'difference in means = {ate:.3f}   (truth = {TRUE_ATE})')"},
        {"md": "A single experiment is noisy. The real claim is that the "
            "estimator is **unbiased** — averaged over many experiments it lands "
            "on the truth. Let's run 400 fresh experiments and check the mean of "
            "the estimates."},
        {"code": "ests = []\n"
            "for _ in range(400):\n"
            "    d = simulate_experiment()\n"
            "    ests.append(d.loc[d.Z == 1, 'Y'].mean() - d.loc[d.Z == 0, 'Y'].mean())\n"
            "ests = np.array(ests)\n"
            "print(f'mean of 400 estimates = {ests.mean():.3f}   (truth = {TRUE_ATE})')\n"
            "print(f'std of the estimates  = {ests.std():.3f}')\n"
            "assert abs(ests.mean() - TRUE_ATE) < 0.1, 'estimator should be unbiased'"},
        {"md": "### Build the confidence interval\n\n"
            "The standard error of a difference in means is "
            "`sqrt(var_t/n_t + var_c/n_c)`. The 95% CI is `ate ± 1.96·SE`. On "
            "a single experiment we expect the truth to fall inside ~95% of such "
            "intervals."},
        {"code": "df = simulate_experiment()\n"
            "yt = df.loc[df.Z == 1, 'Y']\n"
            "yc = df.loc[df.Z == 0, 'Y']\n"
            "ate = yt.mean() - yc.mean()\n"
            "se  = np.sqrt(yt.var(ddof=1)/yt.size + yc.var(ddof=1)/yc.size)\n"
            "lo, hi = ate - 1.96*se, ate + 1.96*se\n"
            "print(f'ATE = {ate:.3f}   SE = {se:.3f}   95% CI = [{lo:.3f}, {hi:.3f}]')\n"
            "print(f'truth {TRUE_ATE} inside CI? {lo <= TRUE_ATE <= hi}')"},
        {"md": "### 🔧 Exercise 1.1 — recover the same estimate with OLS\n\n"
            "Regressing `Y` on a constant and `Z` gives the difference in means "
            "as the coefficient on `Z`, plus a standard error and CI for free. "
            "Fit `sm.OLS` and pull out the `Z` coefficient. Confirm it matches "
            "the hand-computed `ate` above.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: regress Y on a constant and Z, then read off the slope on Z.\n"
            "X = sm.add_constant(df['Z'].to_numpy(dtype=float))   # design matrix\n"
            "beta_Z = ...        # TODO: fit sm.OLS(df['Y'], X) and take params[1]\n"
            "# print(f'OLS coefficient on Z = {beta_Z:.3f}')"},
        {"md": "### ✅ Solution 1.1"},
        {"code": "X = sm.add_constant(df['Z'].to_numpy(dtype=float))\n"
            "fit = sm.OLS(df['Y'].to_numpy(dtype=float), X).fit()\n"
            "beta_Z = fit.params[1]\n"
            "print(f'OLS coefficient on Z = {beta_Z:.3f}   (hand-computed {ate:.3f})')\n"
            "assert abs(beta_Z - ate) < 1e-6, 'OLS slope on Z IS the difference in means'"},
        {"md": "## 2 · Power and the minimum detectable effect (MDE)\n\n"
            "Before launching, you size the test. For a two-proportion test "
            "(conversion at baseline `p0` vs `p1 = p0 + MDE`), the per-arm sample "
            "size has a closed form. We compute it, then **verify it by "
            "simulation**: at that `n`, the empirical power should be ≈ the "
            "target we asked for."},
        {"code": "p0, mde, alpha, power = 0.10, 0.02, 0.05, 0.80\n"
            "p1 = p0 + mde\n"
            "za = stats.norm.ppf(1 - alpha/2)      # 1.96 for a two-sided 5% test\n"
            "zb = stats.norm.ppf(power)            # 0.84 for 80% power\n"
            "pbar = (p0 + p1) / 2\n"
            "n_per_arm = int(np.ceil(\n"
            "    (za*np.sqrt(2*pbar*(1-pbar)) + zb*np.sqrt(p0*(1-p0)+p1*(1-p1)))**2\n"
            "    / mde**2))\n"
            "print(f'baseline {p0:.0%}, MDE {mde:.0%}, power {power:.0%}')\n"
            "print(f'required n per arm = {n_per_arm:,}')"},
        {"md": "Now simulate: draw two arms of size `n_per_arm` with the **true** "
            "rates `p0` and `p1`, run a two-proportion z-test, and repeat. The "
            "fraction of trials that reject the null is the empirical power — it "
            "should land near `0.80`."},
        {"code": "def trial_rejects(n, p0, p1):\n"
            "    a = RNG.binomial(1, p0, n)\n"
            "    b = RNG.binomial(1, p1, n)\n"
            "    pa, pb = a.mean(), b.mean()\n"
            "    pp = (a.sum() + b.sum()) / (2*n)             # pooled rate\n"
            "    se = np.sqrt(pp*(1-pp) * (2/n))\n"
            "    return se > 0 and abs((pb - pa) / se) > za   # reject H0?\n\n"
            "reps = 2000\n"
            "emp_power = np.mean([trial_rejects(n_per_arm, p0, p1) for _ in range(reps)])\n"
            "print(f'empirical power at n={n_per_arm:,}: {emp_power:.3f}  (target {power})')\n"
            "assert abs(emp_power - power) < 0.06, 'sizing formula should hit the target power'"},
        {"md": "### 🔧 Exercise 2.1 — halving the MDE\n\n"
            "Detectable effects shrink like `1/√n`, so the sample size scales "
            "like `1/MDE²`. Recompute `n_per_arm` for a **1-point** lift "
            "(`mde = 0.01`) and confirm it is roughly **four times** the "
            "2-point sample.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "def sample_size(p0, mde, alpha=0.05, power=0.80):\n"
            "    p1 = p0 + mde\n"
            "    za = stats.norm.ppf(1 - alpha/2)\n"
            "    zb = stats.norm.ppf(power)\n"
            "    pbar = (p0 + p1) / 2\n"
            "    return int(np.ceil(\n"
            "        (za*np.sqrt(2*pbar*(1-pbar)) + zb*np.sqrt(p0*(1-p0)+p1*(1-p1)))**2\n"
            "        / mde**2))\n\n"
            "n_2pt = sample_size(0.10, 0.02)\n"
            "n_1pt = ...        # TODO: call sample_size with mde = 0.01\n"
            "# print(n_2pt, n_1pt, n_1pt / n_2pt)"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "n_2pt = sample_size(0.10, 0.02)\n"
            "n_1pt = sample_size(0.10, 0.01)\n"
            "print(f'n per arm: 2-pt lift = {n_2pt:,}   1-pt lift = {n_1pt:,}')\n"
            "print(f'ratio = {n_1pt / n_2pt:.2f}x  (≈ 4 — quartering the MDE squares the cost)')\n"
            "assert 3.5 < n_1pt / n_2pt < 4.5, 'halving the MDE ~quadruples n'"},
        {"md": "## 3 · CUPED — variance reduction from a pre-period covariate\n\n"
            "We have a covariate `pre` measured **before** treatment. CUPED "
            "subtracts the predictable part of `Y`:\n\n"
            "`Y_cuped = Y − θ·(pre − mean(pre))`, with `θ = Cov(Y, pre)/Var(pre)`.\n\n"
            "Because `pre` is pre-treatment, it is balanced across arms, so the "
            "**estimate stays unbiased** — but the residual outcome has less "
            "variance, so the **standard error shrinks**. We assert both."},
        {"code": "df = simulate_experiment(n=8000)\n\n"
            "# --- naive difference in means ---\n"
            "yt, yc = df.loc[df.Z==1, 'Y'], df.loc[df.Z==0, 'Y']\n"
            "ate_naive = yt.mean() - yc.mean()\n"
            "se_naive  = np.sqrt(yt.var(ddof=1)/yt.size + yc.var(ddof=1)/yc.size)\n\n"
            "# --- CUPED-adjusted outcome ---\n"
            "theta = np.cov(df['Y'], df['pre'])[0, 1] / df['pre'].var(ddof=1)\n"
            "df = df.assign(Ycuped=df['Y'] - theta*(df['pre'] - df['pre'].mean()))\n"
            "at, ac = df.loc[df.Z==1, 'Ycuped'], df.loc[df.Z==0, 'Ycuped']\n"
            "ate_cuped = at.mean() - ac.mean()\n"
            "se_cuped  = np.sqrt(at.var(ddof=1)/at.size + ac.var(ddof=1)/ac.size)\n\n"
            "print(f'naive : ATE = {ate_naive:.3f}   SE = {se_naive:.4f}')\n"
            "print(f'CUPED : ATE = {ate_cuped:.3f}   SE = {se_cuped:.4f}')\n"
            "print(f'SE reduction = {100*(1 - se_cuped/se_naive):.1f}%   (truth {TRUE_ATE})')\n\n"
            "assert abs(ate_cuped - TRUE_ATE) < 0.6, 'CUPED estimate stays unbiased'\n"
            "assert se_cuped < se_naive, 'CUPED must reduce the standard error'"},
        {"md": "The CUPED estimate is still ~`2.0` but its SE is meaningfully "
            "smaller — that is *free power*. The stronger the pre-period "
            "covariate correlates with the outcome, the bigger the win. Let's "
            "visualize the two sampling distributions to make the variance drop "
            "concrete."},
        {"code": "naive_draws, cuped_draws = [], []\n"
            "for _ in range(300):\n"
            "    d = simulate_experiment(n=4000)\n"
            "    th = np.cov(d['Y'], d['pre'])[0, 1] / d['pre'].var(ddof=1)\n"
            "    yc_ = d['Y'] - th*(d['pre'] - d['pre'].mean())\n"
            "    naive_draws.append(d.loc[d.Z==1,'Y'].mean() - d.loc[d.Z==0,'Y'].mean())\n"
            "    cuped_draws.append(yc_[d.Z==1].mean() - yc_[d.Z==0].mean())\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.hist(naive_draws, bins=30, alpha=0.5, label='naive')\n"
            "ax.hist(cuped_draws, bins=30, alpha=0.5, label='CUPED')\n"
            "ax.axvline(TRUE_ATE, color='k', ls='--', label='truth')\n"
            "ax.set_title('CUPED narrows the sampling distribution (same center)')\n"
            "ax.legend()\n"
            "print(f'std(naive) = {np.std(naive_draws):.3f}   '\n"
            "      f'std(CUPED) = {np.std(cuped_draws):.3f}')\n"
            "assert np.std(cuped_draws) < np.std(naive_draws)"},
        {"md": "### 🔧 Exercise 3.1 — covariate-adjusted OLS gives the same gain\n\n"
            "Instead of transforming the outcome, regress `Y` on `Z` **and** the "
            "pre-period covariate `pre`. The coefficient on `Z` is the adjusted "
            "ATE, and its reported standard error should be close to the CUPED "
            "SE — same idea, different bookkeeping.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: build the design matrix [const, Z, pre] and fit OLS.\n"
            "Xmat = sm.add_constant(np.column_stack([df['Z'], df['pre']]))\n"
            "fit_adj = ...      # TODO: sm.OLS(df['Y'], Xmat).fit()\n"
            "# beta_Z   = fit_adj.params[1]\n"
            "# se_Z     = fit_adj.bse[1]\n"
            "# print(beta_Z, se_Z)"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "Xmat = sm.add_constant(np.column_stack([df['Z'], df['pre']]))\n"
            "fit_adj = sm.OLS(df['Y'].to_numpy(dtype=float), Xmat).fit()\n"
            "beta_Z = fit_adj.params[1]\n"
            "se_Z   = fit_adj.bse[1]\n"
            "print(f'covariate-adjusted ATE = {beta_Z:.3f}   SE = {se_Z:.4f}')\n"
            "print(f'CUPED SE was {se_cuped:.4f} — same ballpark, both << naive {se_naive:.4f}')\n"
            "assert abs(beta_Z - TRUE_ATE) < 0.6, 'adjusted estimate stays unbiased'\n"
            "assert se_Z < se_naive, 'covariate adjustment also reduces the SE'"},
        {"md": "## 4 · Peeking inflates the false-positive rate\n\n"
            "Now a **true null**: treatment and control have the **same** rate, "
            "so any 'significant' result is a false positive. We compare two "
            "analysts. One looks **once** at the end. The other **peeks** at the "
            "running result many times and stops the instant it crosses ±1.96. "
            "We measure how often each falsely rejects."},
        {"code": "def run_with_peeks(n_final, p, n_peeks):\n"
            "    \"\"\"Sequential experiment under a TRUE NULL; reject at first 'sig' look.\"\"\"\n"
            "    a = RNG.binomial(1, p, n_final)\n"
            "    b = RNG.binomial(1, p, n_final)\n"
            "    ca, cb = np.cumsum(a), np.cumsum(b)\n"
            "    look_at = np.linspace(n_final // n_peeks, n_final, n_peeks).astype(int)\n"
            "    for t in look_at:\n"
            "        pa, pb = ca[t-1]/t, cb[t-1]/t\n"
            "        pp = (ca[t-1] + cb[t-1]) / (2*t)\n"
            "        se = np.sqrt(pp*(1-pp) * (2/t))\n"
            "        if se > 0 and abs((pb - pa) / se) > 1.96:\n"
            "            return True       # falsely declared a winner\n"
            "    return False\n\n"
            "reps = 1500\n"
            "fpr_once  = np.mean([run_with_peeks(2000, 0.10, 1)  for _ in range(reps)])\n"
            "fpr_peek  = np.mean([run_with_peeks(2000, 0.10, 10) for _ in range(reps)])\n"
            "print(f'false-positive rate, look ONCE   : {fpr_once:.3f}  (should be ~0.05)')\n"
            "print(f'false-positive rate, 10 PEEKS    : {fpr_peek:.3f}  (inflated!)')\n"
            "assert fpr_once < 0.09, 'a single fixed-n look controls alpha near 5%'\n"
            "assert fpr_peek > fpr_once + 0.05, 'peeking must inflate the false-positive rate'"},
        {"md": "Looking once controls the error rate near the nominal 5%. "
            "Peeking ten times pushes it far higher — every extra look is another "
            "chance for the wandering statistic to cross the line under a true "
            "null. The fix is to fix `n` in advance and look once, or to use a "
            "sequential testing method designed for continuous monitoring."},
        {"md": "### 🔧 Exercise 4.1 — error rate grows with the number of looks\n\n"
            "Sweep the number of peeks over `[1, 5, 10, 20]` and record the "
            "false-positive rate for each. Confirm it is **monotonically "
            "increasing** in the number of looks.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "peek_counts = [1, 5, 10, 20]\n"
            "fprs = []\n"
            "for k in peek_counts:\n"
            "    # TODO: estimate the FPR with k peeks over `reps` true-null experiments\n"
            "    rate = ...   # TODO: np.mean([run_with_peeks(2000, 0.10, k) for _ in range(reps)])\n"
            "    fprs.append(rate)\n"
            "# print(list(zip(peek_counts, fprs)))"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "peek_counts = [1, 5, 10, 20]\n"
            "fprs = [np.mean([run_with_peeks(2000, 0.10, k) for _ in range(reps)])\n"
            "        for k in peek_counts]\n"
            "for k, r in zip(peek_counts, fprs):\n"
            "    print(f'{k:2d} peeks -> false-positive rate {r:.3f}')\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot(peek_counts, fprs, marker='o')\n"
            "ax.axhline(0.05, color='k', ls='--', label='nominal 5%')\n"
            "ax.set_xlabel('number of looks'); ax.set_ylabel('false-positive rate')\n"
            "ax.set_title('More peeking → more false positives'); ax.legend()\n"
            "assert fprs[-1] > fprs[0], 'FPR should rise with the number of looks'"},
        {"md": "## 5 · ITT vs. per-protocol under noncompliance\n\n"
            "Finally, a leaky experiment. Treatment is randomly **assigned** "
            "(`Z`), but only some assigned units actually **comply** and receive "
            "it (`D`). Here healthier units are more likely to comply, and health "
            "also boosts the outcome — so compliance is confounded with the "
            "outcome. The true effect on those who take the treatment is `3.0`."},
        {"code": "n = 30000; TRUE = 3.0\n"
            "Z = RNG.binomial(1, 0.5, n)                     # randomized assignment\n"
            "health = RNG.normal(size=n)                     # drives compliance AND outcome\n"
            "p_comply = 1 / (1 + np.exp(-(0.5 + 1.0*health)))\n"
            "comply = RNG.binomial(1, p_comply, n)\n"
            "D = Z * comply                                  # treatment RECEIVED (one-sided)\n"
            "Y = 10 + 4*health + TRUE*D + RNG.normal(0, 3, n)\n\n"
            "itt = Y[Z==1].mean() - Y[Z==0].mean()           # by ASSIGNMENT\n"
            "pp  = Y[D==1].mean() - Y[D==0].mean()           # by treatment RECEIVED\n"
            "compliance = D[Z==1].mean()                     # share who comply when assigned\n"
            "cace = itt / compliance                         # IV / effect on compliers\n\n"
            "print(f'compliance rate          = {compliance:.3f}')\n"
            "print(f'ITT (by assignment)      = {itt:.3f}   (unbiased for the OFFER, diluted)')\n"
            "print(f'per-protocol (by uptake) = {pp:.3f}   (BIASED — confounded by health)')\n"
            "print(f'CACE = ITT / compliance  = {cace:.3f}   (truth on compliers = {TRUE})')\n\n"
            "assert abs(cace - TRUE) < 0.5, 'ITT scaled by compliance recovers the compliers effect'\n"
            "assert pp > TRUE + 0.8, 'per-protocol is inflated by healthy compliers'"},
        {"md": "Three numbers from one dataset. **ITT** is below the true `3.0` "
            "because 40% of the assigned never took the treatment — but it is the "
            "honest, unbiased effect of *offering* the program. **Per-protocol** "
            "is inflated because compliers are healthier than non-compliers — "
            "randomization no longer protects that comparison. **CACE** "
            "(`ITT / compliance`) rescales the diluted ITT and recovers the "
            "effect on compliers. We formalize this instrument in Week 9."},
        {"md": "## Wrap-up & self-check\n\n"
            "- **Random assignment** makes `Z ⟂ (Y(0), Y(1))`, so a plain "
            "difference in means is an **unbiased** ATE — you verified it over "
            "400 experiments.\n"
            "- **Power/MDE/sample size** trade off; you sized a test and "
            "confirmed the empirical power matched the target by simulation.\n"
            "- **CUPED** (and covariate-adjusted OLS) cut the standard error "
            "using a pre-period covariate while leaving the estimate unbiased — "
            "free power.\n"
            "- **Peeking** turns repeated looks into multiple testing and "
            "inflates the false-positive rate well above 5%.\n"
            "- **ITT vs. per-protocol**: ITT is unbiased for the offer effect; "
            "per-protocol is confounded; `ITT / compliance` recovers the "
            "compliers' effect.\n\n"
            "**You're ready for Week 4** if you can size a test, explain why "
            "CUPED is free power, and name the failure modes — peeking, SRM, and "
            "interference. Next week: causal graphs (DAGs) and what to adjust for "
            "when you *can't* randomize."},
    ],
}
