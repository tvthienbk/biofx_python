# -*- coding: utf-8 -*-
"""Week 8 — Instrumental Variables & Mendelian Randomization (MIDTERM week)."""

WEEK = {
    "number": 8,
    "slug": "instrumental_variables_mr",
    "title": "Instrumental Variables & Mendelian Randomization",
    "block": "Block III — Quasi-experimental designs",
    "subtitle": "When the confounder can't be measured, find a valve that moves "
                "treatment and nothing else.",
    "deliverable": "Midterm exam (Weeks 1–7); Lab 5 — 2SLS + a "
                   "Mendelian-randomization analysis.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "This is MIDTERM week. The in-class midterm covers Weeks 1–7 "
                    "(the causal question, potential outcomes, randomization, "
                    "DAGs, regression & control, matching/propensity, and "
                    "weighting/doubly-robust estimation) — so budget time to "
                    "review alongside the new material. For the new content, plan "
                    "~6–8 hours: reading (2h), midterm review (2h), problem set "
                    "(1.5h), and the IV/MR lab (2–3h).",
    "one_sentence": "An instrument is a variable that moves treatment but reaches "
        "the outcome only through treatment; if that story holds, it lets you "
        "estimate a causal effect even when the confounder is unmeasured — though "
        "only for the 'compliers' it actually moves.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "State the four instrumental-variable assumptions — relevance, exclusion, "
        "independence, and monotonicity — and say which ones the data can and "
        "cannot test.",
        "Implement two-stage least squares by hand as two OLS regressions and "
        "explain why the fitted first stage removes the confounding.",
        "Explain what LATE identifies, name the 'compliers,' and contrast LATE "
        "with the ATE and the ATT.",
        "Diagnose a weak instrument from the first-stage F statistic and describe "
        "how weakness biases IV toward OLS and inflates its variance.",
        "Explain why a genetic variant can act as a natural instrument in "
        "Mendelian randomization, and why pleiotropy threatens the exclusion "
        "restriction.",
        "Run a robustness check for pleiotropy (e.g. the MR-Egger intercept) and "
        "interpret what a non-zero intercept means.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Angrist & Pischke, Mostly Harmless Econometrics — Chapter 4.",
         "look_for": "the 2SLS mechanics and what LATE actually identifies — note "
                     "how the Wald estimator is just a ratio of reduced-form to "
                     "first-stage effects."},
        {"text": "Davey Smith & Ebrahim (2003), 'Mendelian randomization: can "
                 "genetic epidemiology contribute to understanding environmental "
                 "determinants of disease?'",
         "look_for": "why a genetic variant can serve as an instrument (random "
                     "allocation of alleles at conception) and how pleiotropy "
                     "threatens the exclusion restriction."},
    ],
    "optional_readings": [
        {"text": "Cunningham, The Mixtape — Instrumental Variables chapter.",
         "note": "The applied, code-first walk-through of 2SLS and weak "
                 "instruments, with the quarter-of-birth example worked end to end."},
        {"text": "Angrist & Krueger (1991), 'Does compulsory school attendance "
                 "affect schooling and earnings?'",
         "note": "The original quarter-of-birth study — read it for the design, "
                 "then for the weak-instrument critique it later attracted."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "The problem an instrument solves",
         "body": "When a confounder is unmeasured, adjustment is hopeless: you "
            "cannot control for a variable you never recorded, and 'control for "
            "everything you have' will not close the back-door path. An instrument "
            "Z offers a different route. Think of Z as a valve upstream of "
            "treatment X: turning the valve moves X, and the only way that "
            "movement can reach the outcome Y is by changing X. If Z's effect on Y "
            "travels purely through X, then the part of X that Z explains is "
            "'as-good-as-randomly' assigned and free of the hidden confounder — and "
            "we can read a causal effect off that part alone."},
        {"heading": "The four assumptions",
         "body": "An instrument is only as good as the story behind it. Three "
            "assumptions identify an average effect; the fourth (monotonicity) is "
            "what lets us name whose effect it is.",
         "bullets": [
            [("Relevance:  ", {"bold": True}),
             ("Z actually moves X (cov(Z, X) ≠ 0). This is the one assumption you "
              "CAN test — it is the first-stage regression, and a strong first "
              "stage is non-negotiable.", {})],
            [("Exclusion (the exclusion restriction):  ", {"bold": True}),
             ("Z affects Y ONLY through X — no direct path Z → Y and no other "
              "back door. Untestable; defended by argument, not by the data.", {})],
            [("Independence (exogeneity):  ", {"bold": True}),
             ("Z is unconfounded with Y — Z is as-good-as-randomly assigned with "
              "respect to the outcome's other causes. Also largely untestable.", {})],
            [("Monotonicity:  ", {"bold": True}),
             ("no 'defiers' — nobody does the opposite of what the instrument "
              "encourages. Required to interpret the estimate as the complier "
              "effect (LATE).", {})],
         ],
         "callout": {"title": "Two are testable, two are faith",
            "color": "RED",
            "lines": ["Relevance is testable (first-stage F). Monotonicity is "
                      "sometimes checkable. Exclusion and independence are NOT "
                      "testable from the data — they are causal claims you must "
                      "argue for.",
                      "Most bad IV papers die on exclusion: the instrument turns "
                      "out to touch the outcome through a second pathway."]}},
        {"heading": "2SLS and the Wald estimator",
         "body": "Two-stage least squares makes the idea operational. Stage 1: "
            "regress X on Z and keep the fitted values X̂ — the part of X that Z "
            "explains. Stage 2: regress Y on X̂. Because X̂ is built only from Z, "
            "it is purged of the unmeasured confounder, so its coefficient is a "
            "consistent estimate of the causal effect. For a single binary "
            "instrument this collapses to the Wald estimator: the effect of Z on Y "
            "divided by the effect of Z on X — the reduced form over the first "
            "stage.",
         "bullets": [
            [("βIV = cov(Z, Y) / cov(Z, X)", {"bold": True}),
             (" — the ratio that 2SLS computes. The numerator is the reduced "
              "form (Z → Y); the denominator is the first stage (Z → X).", {})],
            "OLS is biased under confounding because X is correlated with the "
            "error term (it carries U). IV is consistent because Z is not "
            "correlated with that error — it enters only through X.",
            [("Always report the first-stage F. ", {"bold": True}),
             ("A rule of thumb: F < 10 signals a weak instrument and IV estimates "
              "you should not trust.", {})],
         ]},
        {"heading": "LATE: whose effect is it?",
         "body": "An instrument does not move everyone. Split the population by "
            "how they respond to Z: always-takers (treated no matter what), "
            "never-takers (untreated no matter what), compliers (treated iff the "
            "instrument encourages it), and defiers (the perverse opposite — "
            "ruled out by monotonicity). Always- and never-takers contribute no "
            "variation in X that Z explains, so they drop out. What remains is the "
            "Local Average Treatment Effect — the average effect among compliers "
            "alone.",
         "bullets": [
            [("LATE ≠ ATE. ", {"bold": True}),
             ("IV identifies the effect for compliers, a subgroup you do not "
              "directly observe and whose effect may differ from the population "
              "average.", {})],
            [("Different instruments → different compliers → different LATEs. ",
              {"bold": True}),
             ("This is a feature, not a bug: the estimand is tied to the "
              "instrument.", {})],
            "The first-stage slope for a binary instrument equals the share of "
            "compliers — a strong first stage means the instrument moves many "
            "people, so the LATE generalizes more comfortably.",
         ]},
        {"heading": "Weak instruments",
         "body": "Relevance is not binary — an instrument can be technically "
            "relevant yet so weak it is useless. When cov(Z, X) is near zero, the "
            "Wald ratio divides by a number close to zero, so tiny chance "
            "correlations between Z and Y blow up. Two symptoms appear together: "
            "the IV estimate becomes wildly high-variance, and it is biased BACK "
            "toward the OLS estimate (toward the very confounding bias we were "
            "trying to escape). The diagnostic is the first-stage F statistic; "
            "an F well above 10 is the usual minimum, and modern work pushes that "
            "threshold higher.",
         "callout": {"title": "The weak-instrument trap",
            "color": "AMBER",
            "lines": ["A weak instrument gives you an estimate with a confidence "
                      "interval so wide it is uninformative — and a point estimate "
                      "quietly pulled toward OLS bias.",
                      "Diagnose it BEFORE interpreting the second stage: look at "
                      "the first-stage F every single time."]}},
        {"heading": "Mendelian randomization",
         "body": "Mendelian randomization (MR) uses a genetic variant as the "
            "instrument. The logic is biological: alleles are allocated "
            "essentially at random at conception (Mendel's second law), before any "
            "of the lifestyle and environmental confounders that plague "
            "observational epidemiology. A variant that raises, say, LDL "
            "cholesterol is like a lifelong natural experiment in higher LDL. If "
            "the variant influences heart disease only through LDL, it is a valid "
            "instrument and the ratio cov(G, CHD) / cov(G, LDL) estimates the "
            "causal effect of LDL on heart disease.",
         "bullets": [
            [("Independence comes 'for free-ish': ", {"bold": True}),
             ("random allocation of alleles makes genotype roughly independent of "
              "behavioural and social confounders.", {})],
            [("Exclusion is the soft spot — pleiotropy. ", {"bold": True}),
             ("A variant that affects the outcome through a SECOND pathway "
              "(not via the exposure) violates exclusion and biases the estimate.",
              {})],
            "Population stratification and linkage disequilibrium are the other "
            "classic threats — they can break independence or relevance.",
         ],
         "callout": {"title": "Robustness checks MR requires",
            "color": "TEAL",
            "lines": ["Use MANY independent variants and compare their "
                      "instrument-specific estimates: with valid instruments they "
                      "should agree.",
                      "MR-Egger regresses SNP–outcome effects on SNP–exposure "
                      "effects WITH an intercept; a non-zero intercept flags "
                      "directional pleiotropy, and the slope gives a "
                      "pleiotropy-robust effect.",
                      "Weighted-median and mode-based estimators are the other "
                      "standard sensitivity analyses."]}},
    ],
    "problem_set": {
        "label": "Problem Set (midterm review + IV)",
        "title": "Instruments, exclusion, and LATE",
        "intro": "Five problems on the IV/MR toolkit, pitched to double as "
            "midterm review (they lean on confounding, potential outcomes, and "
            "estimation from Weeks 1–7). For each, reason from the causal "
            "structure, not the regression output. Try all five before you look "
            "at the solutions.",
        "problems": [
            {"title": "Vetting a proposed instrument",
             "prompt": "A health economist wants the effect of military service "
                "(X) on later earnings (Y) and proposes the Vietnam-draft lottery "
                "number (Z) as an instrument. List the four IV assumptions and, "
                "for each, state what it requires here and whether the data can "
                "test it.",
             "solution_title": "Relevance is testable; exclusion, independence, "
                "and monotonicity are (mostly) argued, not tested.",
             "solution": [
                "Relevance: a low lottery number must actually raise the "
                "probability of serving. TESTABLE — it is the first stage; check "
                "the F statistic.",
                "Independence: the lottery number must be unrelated to anything "
                "else that drives earnings. Credible because numbers were drawn at "
                "random, but NOT testable from the data alone.",
                "Exclusion: the draft number must affect earnings ONLY through "
                "service — no effect via, say, staying in school to avoid the "
                "draft. UNTESTABLE; the central worry.",
                "Monotonicity: a low number never makes someone LESS likely to "
                "serve (no defiers). Plausible here, lets us read the estimate as "
                "the complier LATE; only partially checkable."]},
            {"title": "Why OLS is biased but IV is consistent",
             "prompt": "An unmeasured confounder U raises both treatment X and "
                "outcome Y. Using the regression error term, explain in one tight "
                "argument why ordinary least squares is biased for the causal "
                "effect, and why an instrument Z that satisfies the assumptions "
                "fixes it.",
             "solution_title": "OLS fails because X is correlated with the error; "
                "IV works because Z is not.",
             "solution": [
                "Write Y = βX + ε, where ε absorbs the unmeasured U. Because U "
                "drives X, we have cov(X, ε) ≠ 0 — the OLS exogeneity condition "
                "fails, so the OLS estimate of β is biased and inconsistent (it "
                "soaks up the confounding).",
                "An instrument satisfies cov(Z, ε) = 0 (independence + exclusion: "
                "Z touches Y only through X) and cov(Z, X) ≠ 0 (relevance).",
                "Then β = cov(Z, Y) / cov(Z, X) is identified from observable "
                "covariances, and its sample analogue (2SLS / Wald) is consistent: "
                "the confounder cancels because Z is uncorrelated with it."]},
            {"title": "LATE vs ATE — reading the estimand",
             "prompt": "A randomized 'encouragement' to take a flu shot is used as "
                "an instrument for actually getting vaccinated. The IV estimate of "
                "the effect on hospitalization is larger than the experimental ATE "
                "would be. Define the complier population here and give a reason "
                "the LATE could legitimately exceed the ATE.",
             "solution_title": "IV identifies the complier effect (LATE), which "
                "need not equal the population ATE.",
             "solution": [
                "Compliers are people who get vaccinated BECAUSE they were "
                "encouraged and would not have otherwise — not the always-takers "
                "(vaccinate regardless) or never-takers (refuse regardless).",
                "LATE = E[Y(1) − Y(0) | complier]. It says nothing about "
                "always-/never-takers, whose effects are not identified by this "
                "instrument.",
                "The LATE can exceed the ATE if compliers benefit more than "
                "average — e.g. they are higher-risk people on the fence, for whom "
                "the shot prevents more hospitalizations. Same treatment, "
                "different population, different number — both correct."]},
            {"title": "Diagnosing a weak instrument",
             "prompt": "A student runs 2SLS and gets a plausible-looking point "
                "estimate but a confidence interval ten times wider than the OLS "
                "one. The first-stage regression of X on Z has an F statistic of "
                "3.1. What is going on, which direction is the IV point estimate "
                "likely biased, and what should the student do?",
             "solution_title": "Classic weak instrument: F = 3.1 ≪ 10 — high "
                "variance and bias back toward OLS.",
             "solution": [
                "F = 3.1 is far below the usual ≥ 10 rule of thumb: the "
                "instrument barely moves X, so cov(Z, X) ≈ 0 and the Wald ratio "
                "divides by near-zero — hence the enormous confidence interval.",
                "Weak instruments bias the IV estimate TOWARD OLS (toward the "
                "confounding bias you were trying to escape), so the 'plausible' "
                "point estimate is not reassuring.",
                "Remedies: find a stronger instrument, use weak-instrument-robust "
                "inference (e.g. Anderson–Rubin confidence sets), or report the "
                "first-stage F honestly and decline to over-interpret the second "
                "stage."]},
            {"title": "Pleiotropy in MR and a robustness check",
             "prompt": "An MR study uses a genetic variant for LDL cholesterol to "
                "estimate the effect of LDL on heart disease. A reviewer worries "
                "the variant also lowers inflammation, which independently affects "
                "heart disease. Name the violation, say how it biases the "
                "estimate, and describe one robustness check that could detect it.",
             "solution_title": "Pleiotropy violates exclusion; MR-Egger's "
                "intercept can detect directional pleiotropy.",
             "solution": [
                "A second pathway G → inflammation → CHD means the variant affects "
                "the outcome NOT only through LDL — a violation of the exclusion "
                "restriction (pleiotropy). The ratio estimate is then biased "
                "because cov(G, CHD) includes the extra pathway.",
                "With one variant you cannot separate the two pathways. With many "
                "independent variants you can: under valid instruments their "
                "individual estimates should agree.",
                "MR-Egger regresses each SNP–outcome effect on its SNP–exposure "
                "effect WITH an intercept. A non-zero intercept signals directional "
                "pleiotropy; the slope then gives a pleiotropy-robust causal "
                "estimate. Weighted-median and mode estimators are complementary "
                "checks."]},
        ],
    },
    "lab": {
        "label": "Lab 5",
        "title": "2SLS + Mendelian randomization",
        "goal": "implement instrumental-variables estimation from scratch — "
            "simulate a valid instrument under unmeasured confounding, run 2SLS as "
            "two OLS stages, diagnose instrument strength, and finish with an "
            "MR-style analysis including a pleiotropy check.",
        "steps": [
            {"heading": "Step 1 · Simulate an instrument under hidden confounding",
             "body": "Build a world with an UNMEASURED confounder U that drives "
                "both X and Y, plus an instrument Z that moves X and reaches Y only "
                "through X. The TRUE effect of X on Y is exactly 1.5. Confirm that "
                "OLS is biased.",
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(8)\nn = 20000\n"
                "U = rng.normal(size=n)                      # UNMEASURED confounder\n"
                "Z = rng.normal(size=n)                      # the instrument\n"
                "X = 0.7*Z + 1.0*U + rng.normal(size=n)      # first stage + U\n"
                "Y = 1.5*X + 2.0*U + rng.normal(size=n)      # TRUE effect = 1.5\n"
                "ols = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
                'print(f"OLS = {ols:.3f}  (biased; truth 1.5)")',
             "code_r": 'set.seed(8); n <- 20000\n'
                'U <- rnorm(n); Z <- rnorm(n)\n'
                'X <- 0.7*Z + 1.0*U + rnorm(n)\n'
                'Y <- 1.5*X + 2.0*U + rnorm(n)\n'
                'cat(sprintf("OLS = %.3f (biased)\\n", coef(lm(Y ~ X))["X"]))'},
            {"heading": "Step 2 · 2SLS by hand (two OLS stages) + first-stage F",
             "body": "Regress X on Z, keep the fitted values, then regress Y on "
                "those fitted values. Report the first-stage F — it must be "
                "comfortably above 10. Compare OLS and IV.",
             "code_python": "first  = sm.OLS(X, sm.add_constant(Z)).fit()\n"
                "Xhat   = first.fittedvalues\n"
                "second = sm.OLS(Y, sm.add_constant(Xhat)).fit()\n"
                "iv = second.params[1]\n"
                'print(f"first-stage F = {first.fvalue:.1f}")\n'
                'print(f"OLS = {ols:.3f}   IV (2SLS) = {iv:.3f}   truth = 1.5")\n'
                "assert abs(iv - 1.5) < 0.1",
             "code_r": '# AER::ivreg does both stages and the diagnostics\n'
                'library(AER)\n'
                'fit <- ivreg(Y ~ X | Z)            # Y ~ endog | instrument\n'
                'summary(fit, diagnostics = TRUE)   # see weak-instrument F\n'
                'coef(fit)["X"]                      # the IV estimate (~1.5)'},
            {"heading": "Step 3 · The Wald estimator with a binary instrument",
             "body": "Re-do the estimate with a binary instrument and show that "
                "2SLS reduces to the Wald ratio: the difference in mean Y across "
                "Z, divided by the difference in mean X across Z.",
             "code_python": "Zb = rng.binomial(1, 0.5, n)\n"
                "Xb = 0.3 + 0.5*Zb + 0.8*U + rng.normal(size=n)\n"
                "Yb = 1.5*Xb + 1.5*U + rng.normal(size=n)\n"
                "wald = (Yb[Zb==1].mean()-Yb[Zb==0].mean()) / \\\n"
                "       (Xb[Zb==1].mean()-Xb[Zb==0].mean())\n"
                'print(f"Wald = {wald:.3f}  (~1.5)")',
             "code_r": 'Zb <- rbinom(n, 1, 0.5)\n'
                'Xb <- 0.3 + 0.5*Zb + 0.8*U + rnorm(n)\n'
                'Yb <- 1.5*Xb + 1.5*U + rnorm(n)\n'
                'wald <- (mean(Yb[Zb==1]) - mean(Yb[Zb==0])) /\n'
                '        (mean(Xb[Zb==1]) - mean(Xb[Zb==0]))\n'
                'cat(sprintf("Wald = %.3f\\n", wald))'},
            {"heading": "Step 4 · A weak instrument",
             "body": "Shrink the first-stage coefficient to near zero and watch "
                "the first-stage F collapse and the IV estimate become both "
                "high-variance and biased back toward OLS. Repeat over many draws "
                "to see the variance explode.",
             "code_python": "def iv2sls(Z, X, Y):\n"
                "    f = sm.OLS(X, sm.add_constant(Z)).fit()\n"
                "    s = sm.OLS(Y, sm.add_constant(f.fittedvalues)).fit()\n"
                "    return s.params[1], f.fvalue\n"
                "Zw = rng.normal(size=n)\n"
                "Xw = 0.03*Zw + 1.0*U + rng.normal(size=n)   # weak first stage\n"
                "Yw = 1.5*Xw + 2.0*U + rng.normal(size=n)\n"
                "est, F = iv2sls(Zw, Xw, Yw)\n"
                'print(f"weak: first-stage F = {F:.1f}, IV = {est:.2f} '
                '(unstable, biased toward OLS)")',
             "code_r": '# A near-zero first stage makes the IV estimate explode.\n'
                'Zw <- rnorm(n)\n'
                'Xw <- 0.03*Zw + 1.0*U + rnorm(n)\n'
                'Yw <- 1.5*Xw + 2.0*U + rnorm(n)\n'
                'summary(ivreg(Yw ~ Xw | Zw), diagnostics = TRUE)'},
            {"heading": "Step 5 · Mendelian randomization + a pleiotropy check",
             "body": "Replace Z with a genetic variant G (allele count 0/1/2). With "
                "a VALID instrument the ratio recovers the truth. Then add a direct "
                "pleiotropic path G → Y (exclusion violated) and watch the estimate "
                "break — the robustness check students implement in the notebook is "
                "MR-Egger.",
             "code_python": "G   = rng.binomial(2, 0.3, n).astype(float)\n"
                "LDL = 1.0 + 0.5*G + 1.0*U + rng.normal(size=n)\n"
                "CHD_valid = 0.8*LDL + 1.5*U + rng.normal(size=n)   # truth 0.8\n"
                "CHD_pleio = 0.8*LDL + 1.5*U + 0.9*G + rng.normal(size=n)  # G->Y!\n"
                "print('valid MR :', round(iv2sls(G, LDL, CHD_valid)[0], 3))\n"
                "print('pleiotropic MR (biased):', "
                "round(iv2sls(G, LDL, CHD_pleio)[0], 3))",
             "code_r": '# The MendelianRandomization / TwoSampleMR packages do this\n'
                '# in practice; here the same ratio logic via ivreg:\n'
                'G   <- rbinom(n, 2, 0.3)\n'
                'LDL <- 1.0 + 0.5*G + 1.0*U + rnorm(n)\n'
                'CHDv <- 0.8*LDL + 1.5*U + rnorm(n)\n'
                'CHDp <- 0.8*LDL + 1.5*U + 0.9*G + rnorm(n)   # pleiotropy\n'
                'cat("valid:", coef(ivreg(CHDv ~ LDL | G))["LDL"], "\\n")\n'
                'cat("pleio:", coef(ivreg(CHDp ~ LDL | G))["LDL"], "\\n")'},
        ],
        "expected": "OLS lands well above 1.5 (the confounder inflates it); 2SLS "
            "and the Wald estimator both recover ~1.5 with a first-stage F in the "
            "thousands. The weak instrument gives an F near or below 10 and a wild "
            "IV estimate. Valid MR returns ~0.8; the pleiotropic version is badly "
            "biased upward — and MR-Egger's non-zero intercept is what flags it.",
        "submit": [
            "Push your notebook and a short README reporting the OLS vs IV numbers, "
            "the first-stage F for the strong and weak instruments, and the valid "
            "vs pleiotropic MR estimates.",
            "In one paragraph, state which IV assumption the pleiotropy violates "
            "and how MR-Egger detects it.",
            "Bring your active-reading sentences (Angrist–Pischke Ch. 4 and Davey "
            "Smith & Ebrahim) to lab.",
        ],
    },
    "self_check": [
        "List the four IV assumptions and say which two the data can test.",
        "Implement 2SLS as two OLS regressions from memory and explain why the "
        "first stage removes the confounder.",
        "Explain LATE and name the complier population — and why LATE need not "
        "equal the ATE.",
        "Read a first-stage F of 4 and say what is wrong and which way the IV "
        "estimate is biased.",
        "Say why a genetic variant can be an instrument and how pleiotropy breaks "
        "it — and confirm you are ready for the Weeks 1–7 midterm.",
    ],
    "next_week": {
        "heading": "Coming up: Week 9 — Regression discontinuity",
        "teaser": "We keep mining quasi-experiments. When treatment switches on at "
            "a sharp cutoff of some running variable — a test score, an age, a "
            "poverty index — the units just above and just below the threshold are "
            "almost identical, so the jump in the outcome at the cutoff is a "
            "credible local causal effect. You'll meet sharp vs fuzzy designs, "
            "local linear regression, bandwidth choice, and the McCrary density "
            "test. Skim the RD chapter of Cunningham's Mixtape to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 8", "items": [
            {"t": "The unmeasured-confounder problem", "d": "When adjustment "
             "cannot save you — and what an instrument offers instead."},
            {"t": "The four IV assumptions", "d": "Relevance, exclusion, "
             "independence, monotonicity — two testable, two faith."},
            {"t": "2SLS & the Wald estimator", "d": "Two OLS stages; why the "
             "fitted first stage purges the confounder."},
            {"t": "LATE & the compliers", "d": "Whose effect an instrument "
             "actually identifies."},
            {"t": "Weak instruments", "d": "The first-stage F and the "
             "high-variance, OLS-biased trap."},
            {"t": "Mendelian randomization", "d": "Genotype as a natural "
             "instrument — and pleiotropy, its Achilles heel."},
        ]},
        {"type": "content", "kicker": "Midterm week",
         "title": "Housekeeping: the midterm covers Weeks 1–7", "bullets": [
            "The in-class midterm spans Block I and Block II (Weeks 1–7).",
            ("Block I: causal question, potential outcomes, randomization, DAGs.", 1),
            ("Block II: regression, matching & propensity, weighting & doubly-robust.", 1),
            "Expect to label confounders/colliders/mediators, write an estimand, "
            "and reason about identification vs estimation.",
            "Today's new material (IV/MR) is NOT on the midterm — but it builds "
            "directly on the confounding logic you are reviewing.",
            ("Lab 5 (2SLS + MR) is due alongside the exam.", 1),
         ],
         "note": {"title": "Review tip",
            "body": "Re-run your Week 1–7 notebooks. If you can reproduce the "
            "naive-vs-adjusted gap and the propensity-weighting recovery from "
            "memory, you are ready."}},
        {"type": "content", "kicker": "Where we are",
         "title": "Block III opens: designs, not adjustment", "bullets": [
            "Blocks I–II assumed the confounders were measured and we could adjust "
            "our way to a causal effect.",
            "Block III tackles the harder case: a confounder we cannot measure at "
            "all.",
            "The move is from ADJUSTMENT to DESIGN — exploit some external source "
            "of variation in treatment.",
            ("Instrumental variables is the first such design; RD and DiD follow.",
             1),
         ],
         "note": {"title": "The theme",
            "body": "Find variation in treatment that is as-good-as-random, even "
            "though the rest of the data is hopelessly confounded."}},

        {"type": "section", "kicker": "Part 1",
         "title": "The unmeasured-confounder problem",
         "subtitle": "Adjustment needs the confounder in hand. When it is "
            "unmeasured — or unmeasurable — we need a different lever."},
        {"type": "content", "kicker": "Why adjustment fails",
         "title": "You cannot control for what you never measured", "bullets": [
            "Back-door adjustment closes a path only if every confounder on it is "
            "observed.",
            "Ability, motivation, frailty, lifestyle — the usual suspects are "
            "rarely in the dataset.",
            "'Control for everything you have' leaves the hidden path wide open, "
            "and may open new ones (colliders).",
            "No estimator — matching, weighting, doubly-robust — can fix bias from "
            "a confounder that was never recorded.",
         ],
         "note": {"title": "The gap",
            "body": "Unmeasured confounding is the wall Block II runs into. "
            "Designs are how Block III climbs over it."}},
        {"type": "statement",
         "quote": "An instrument is a valve upstream of treatment: turn it, "
            "treatment moves — and the only way that movement reaches the outcome "
            "is through treatment itself.",
         "attribution": "If that story is true, the part of treatment the "
            "instrument explains is as-good-as-randomly assigned, free of the "
            "hidden confounder. That is the whole idea of IV."},
        {"type": "content", "kicker": "The picture",
         "title": "What a valid instrument looks like", "bullets": [
            "Z → X: the instrument moves treatment (relevance).",
            "X → Y: treatment affects the outcome (the effect we want).",
            "U → X and U → Y: an unmeasured confounder, lurking.",
            "Crucially NO arrow Z → Y except through X, and NO arrow U → Z.",
            ("Z is isolated from U and from Y's other causes — that isolation is "
             "what we exploit.", 1),
         ],
         "note": {"title": "Read the graph",
            "body": "Z ─→ X ─→ Y, with U ─→ X and U ─→ Y. The missing arrows "
            "(Z→Y, U→Z) ARE the IV assumptions."}},

        {"type": "section", "kicker": "Part 2", "title": "The four assumptions",
         "subtitle": "An instrument is only as good as the story behind it. Three "
            "identify an effect; the fourth names whose effect it is."},
        {"type": "content", "kicker": "The IV assumptions",
         "title": "Relevance, exclusion, independence, monotonicity", "bullets": [
            "RELEVANCE — Z actually moves X. cov(Z, X) ≠ 0. The one you can test.",
            "EXCLUSION — Z affects Y only through X. No direct path Z → Y.",
            "INDEPENDENCE — Z is as-good-as-random w.r.t. Y's other causes.",
            "MONOTONICITY — no defiers; nobody does the opposite of the "
            "encouragement.",
            ("Exclusion + independence are untestable causal claims — defend them "
             "by argument.", 1),
         ],
         "note": {"title": "Mnemonic",
            "body": "Relevance you measure; exclusion and independence you argue; "
            "monotonicity you assume to name the estimand."}},
        {"type": "compare", "kicker": "What the data can and cannot tell you",
         "title": "Testable vs faith", "columns": [
            {"head": "Testable", "sub": "from the data", "points": [
                "Relevance: the first-stage F statistic.",
                "Monotonicity: partially checkable (signs of subgroup first "
                "stages).",
                "If relevance fails, you see it — weak instrument."]},
            {"head": "Untestable", "sub": "argued, not estimated", "points": [
                "Exclusion: no second pathway Z → Y.",
                "Independence: Z unconfounded with the outcome.",
                "These are where most IV papers live or die."]},
        ]},
        {"type": "content", "kicker": "Case study · Angrist–Krueger (1991)",
         "title": "Quarter of birth & returns to schooling", "bullets": [
            "Compulsory-schooling laws let students leave at a fixed age, so birth "
            "quarter nudges years of schooling.",
            "Z = quarter of birth; X = years of schooling; Y = earnings.",
            "Quarter of birth is plausibly independent of ability — the clever "
            "part of the design.",
            "Estimated returns to a year of schooling around 7–10%.",
            ("Later critiqued as a WEAK instrument — birth quarter barely moves "
             "schooling.", 1),
         ],
         "note": {"title": "Why it is famous",
            "body": "It is both the textbook IV design AND the textbook cautionary "
            "tale about instrument strength."}},

        {"type": "section", "kicker": "Part 3",
         "title": "2SLS & the Wald estimator",
         "subtitle": "Making the idea operational: two ordinary regressions that "
            "together purge the unmeasured confounder."},
        {"type": "steps", "kicker": "Two-stage least squares",
         "title": "Two OLS regressions, run in sequence", "steps": [
            {"title": "Stage 1", "body": "— regress X on Z; keep the fitted "
             "values X̂ (the part of X the instrument explains)."},
            {"title": "Purge", "body": "— X̂ is built only from Z, so it carries "
             "none of the unmeasured confounder U."},
            {"title": "Stage 2", "body": "— regress Y on X̂; its coefficient is "
             "the consistent IV estimate of X → Y."},
            {"title": "Report", "body": "— always state the first-stage F so the "
             "reader can judge instrument strength."},
         ],
         "note": "Do not compute second-stage standard errors naively from the "
            "two regressions — use an IV routine; they differ."},
        {"type": "content", "kicker": "The binary-instrument special case",
         "title": "The Wald estimator: a ratio of two effects", "bullets": [
            "For a single binary Z, 2SLS collapses to βIV = cov(Z,Y) / cov(Z,X).",
            "Numerator = reduced form (Z → Y); denominator = first stage (Z → X).",
            "In means: (Ȳ at Z=1 − Ȳ at Z=0) / (X̄ at Z=1 − X̄ at Z=0).",
            "Intuition: scale up the instrument's effect on Y by how much it moved "
            "X.",
         ],
         "note": {"title": "Why the confounder cancels",
            "body": "Both covariances are taken with Z, which is uncorrelated with "
            "U — so U drops out of the ratio."}},
        {"type": "compare", "kicker": "The core contrast",
         "title": "Why OLS is biased but IV is consistent", "columns": [
            {"head": "OLS", "sub": "biased under confounding", "points": [
                "Y = βX + ε, with U hidden in ε.",
                "U drives X, so cov(X, ε) ≠ 0.",
                "Exogeneity fails → β estimate soaks up the confounding."]},
            {"head": "IV / 2SLS", "sub": "consistent", "points": [
                "Z satisfies cov(Z, ε) = 0 and cov(Z, X) ≠ 0.",
                "β = cov(Z,Y)/cov(Z,X) is identified.",
                "The confounder cancels because Z is uncorrelated with it."]},
        ]},

        {"type": "section", "kicker": "Part 4", "title": "LATE & the compliers",
         "subtitle": "An instrument does not move everyone. It identifies the "
            "effect only for the people it actually moves."},
        {"type": "content", "kicker": "Four response types",
         "title": "Always-takers, never-takers, compliers, defiers", "bullets": [
            "ALWAYS-TAKERS — treated no matter what the instrument says.",
            "NEVER-TAKERS — untreated no matter what.",
            "COMPLIERS — treated if and only if the instrument encourages it.",
            "DEFIERS — the perverse opposite; ruled out by monotonicity.",
            ("Only compliers supply the Z-driven variation in X — so only their "
             "effect is identified.", 1),
         ],
         "note": {"title": "Who counts",
            "body": "Always- and never-takers don't respond to Z, so they "
            "contribute nothing to the IV estimate."}},
        {"type": "content", "kicker": "The estimand",
         "title": "IV identifies the LATE, not the ATE", "bullets": [
            "LATE = E[Y(1) − Y(0) | complier] — the Local Average Treatment "
            "Effect.",
            "It can differ from the ATE if compliers benefit more (or less) than "
            "average.",
            "Different instruments move different compliers → different LATEs. The "
            "estimand is tied to the instrument.",
            "For a binary Z, the first-stage slope = the share of compliers.",
         ],
         "note": {"title": "Honesty",
            "body": "Report whose effect you estimated. 'The effect' is usually "
            "the complier effect — say so."}},
        {"type": "table", "kicker": "Estimands, revisited",
         "title": "Where LATE sits among the effects we estimate",
         "headers": ["Estimand", "Population", "Identified by"],
         "rows": [
            ["ATE", "everyone", "randomization / full adjustment"],
            ["ATT", "the treated", "matching, weighting (Block II)"],
            ["LATE", "compliers (move with Z)", "an instrument (this week)"],
            ["CATE", "a covariate stratum", "heterogeneous-effect methods (later)"],
         ],
         "note": {"title": "The lesson",
            "body": "The method you choose determines WHOSE effect you get. IV "
            "buys identification under hidden confounding — at the price of a "
            "narrower population."}},

        {"type": "section", "kicker": "Part 5", "title": "Weak instruments",
         "subtitle": "Relevance is not yes/no. A barely-relevant instrument is "
            "worse than useless — it is misleading."},
        {"type": "content", "kicker": "What goes wrong",
         "title": "Dividing by almost zero", "bullets": [
            "When cov(Z, X) ≈ 0, the Wald ratio divides by a near-zero "
            "denominator.",
            "Tiny chance correlations between Z and Y then blow up into huge "
            "estimates.",
            "Symptom 1: the IV estimate is wildly high-variance (enormous "
            "confidence intervals).",
            "Symptom 2: it is biased BACK toward OLS — toward the very confounding "
            "you fled.",
         ],
         "note": {"title": "Double jeopardy",
            "body": "A weak instrument gives you both a useless interval AND a "
            "point estimate quietly pulled toward bias."}},
        {"type": "content", "kicker": "The diagnostic",
         "title": "Look at the first-stage F — every time", "bullets": [
            "The first-stage F tests whether Z genuinely moves X.",
            "Rule of thumb: F < 10 → weak instrument; treat the second stage with "
            "deep suspicion.",
            "Modern work argues the threshold should often be much higher than 10.",
            "Angrist–Krueger's quarter-of-birth instrument is the cautionary "
            "example — clever, but weak.",
         ],
         "note": {"title": "Habit",
            "body": "Report the first-stage F before you ever interpret the IV "
            "coefficient. No F, no trust."}},
        {"type": "statement",
         "quote": "A weak instrument does not just widen your confidence interval "
            "— it quietly drags your point estimate back toward the bias you were "
            "trying to escape.",
         "attribution": "This is why instrument STRENGTH, not just validity, is "
            "part of every honest IV analysis."},

        {"type": "section", "kicker": "Part 6",
         "title": "Mendelian randomization",
         "subtitle": "Nature runs a randomized experiment at conception. MR uses "
            "a genetic variant as the instrument."},
        {"type": "content", "kicker": "The genetic instrument",
         "title": "Genotype as a natural experiment", "bullets": [
            "Mendel's second law: alleles are allocated essentially at random at "
            "conception.",
            "That randomization happens BEFORE lifestyle and environmental "
            "confounders can act.",
            "A variant that raises an exposure (e.g. LDL) is a lifelong natural "
            "experiment in higher exposure.",
            "If it touches the outcome only through that exposure, it is a valid "
            "instrument.",
            ("Estimate = cov(G, outcome) / cov(G, exposure) — the same ratio as "
             "ever.", 1),
         ],
         "note": {"title": "The appeal",
            "body": "Independence comes 'for free-ish': genotype is roughly "
            "unconfounded with behaviour and social factors."}},
        {"type": "content", "kicker": "Case study · LDL → heart disease",
         "title": "A textbook MR success", "bullets": [
            "Variants that lower LDL cholesterol are linked to lower coronary "
            "heart-disease risk.",
            "Direction and magnitude align with what LDL-lowering drugs (statins) "
            "achieve in trials.",
            "Contrast HDL: MR found NO protective causal effect, despite a strong "
            "observational correlation.",
            "MR thus separated a real causal exposure (LDL) from a confounded "
            "bystander (HDL).",
         ],
         "note": {"title": "Why it mattered",
            "body": "MR flagged that raising HDL would not help — later confirmed "
            "when HDL-raising drugs failed in trials."}},
        {"type": "compare", "kicker": "The Achilles heel",
         "title": "Pleiotropy and the other threats", "columns": [
            {"head": "Pleiotropy", "sub": "breaks exclusion", "points": [
                "Variant affects Y through a SECOND pathway, not via the "
                "exposure.",
                "Biases the ratio estimate.",
                "The central worry in every MR study."]},
            {"head": "Stratification", "sub": "breaks independence", "points": [
                "Ancestry relates to both genotype and outcome.",
                "Fixed by ancestry adjustment / within-family designs."]},
            {"head": "Weakness / LD", "sub": "breaks relevance", "points": [
                "Variant barely moves the exposure.",
                "Same weak-instrument problems as before."]},
        ]},
        {"type": "steps", "kicker": "The robustness checks MR requires",
         "title": "Never trust a single variant", "steps": [
            {"title": "Many variants", "body": "— use multiple independent SNPs; "
             "valid ones should give agreeing estimates."},
            {"title": "MR-Egger", "body": "— regress SNP–outcome on SNP–exposure "
             "WITH an intercept; a non-zero intercept flags directional "
             "pleiotropy."},
            {"title": "Egger slope", "body": "— the slope gives a "
             "pleiotropy-robust causal estimate when the intercept is non-zero."},
            {"title": "Median / mode", "body": "— weighted-median and mode-based "
             "estimators are the complementary sensitivity analyses."},
         ],
         "note": "You will implement the multi-variant MR-Egger check in this "
            "week's notebook and watch the intercept catch pleiotropy."},

        {"type": "section", "kicker": "Part 7", "title": "Putting it together",
         "subtitle": "The IV workflow, the limits, and where Block III goes next."},
        {"type": "steps", "kicker": "The IV/MR workflow",
         "title": "How to run a credible instrumental-variables study", "steps": [
            {"title": "Argue the instrument", "body": "— make the case for "
             "exclusion and independence in prose, from domain knowledge."},
            {"title": "Check relevance", "body": "— run the first stage; report "
             "the F. If it is weak, stop."},
            {"title": "Estimate", "body": "— 2SLS (or the Wald ratio); report the "
             "LATE and name the compliers."},
            {"title": "Stress-test", "body": "— sensitivity to exclusion; for MR, "
             "MR-Egger and median estimators."},
         ],
         "note": "Same five-step spirit as always: question → assume → identify → "
            "estimate → validate."},
        {"type": "compare", "kicker": "Honest limits",
         "title": "What IV buys you — and what it costs", "columns": [
            {"head": "What you gain", "points": [
                "Identification despite UNMEASURED confounding.",
                "A design-based, transparent argument.",
                "Often the only credible option in observational data."]},
            {"head": "What you pay", "points": [
                "Only the complier effect (LATE), not the ATE.",
                "Two untestable assumptions (exclusion, independence).",
                "Sensitivity to weak instruments and pleiotropy."]},
        ]},
        {"type": "statement",
         "quote": "Find a valve that moves treatment and nothing else — then scale "
            "its effect on the outcome by its effect on treatment.",
         "attribution": "That single sentence is IV, 2SLS, the Wald estimator, and "
            "Mendelian randomization. This week: build it in code, diagnose it, "
            "and break it with pleiotropy — and good luck on the midterm."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · The setup: an unmeasured confounder and a valve\n\n"
            "Block II assumed every confounder was measured. This week we drop "
            "that: a confounder `U` drives both treatment `X` and outcome `Y`, and "
            "**we never get to see `U`**. Adjustment is therefore hopeless. Our "
            "rescue is an **instrument** `Z` — a variable that moves `X` and "
            "reaches `Y` *only* through `X`.\n\n"
            "Throughout, the **true** causal effect of `X` on `Y` is a number we "
            "choose, so we can always check whether an estimate recovered it. We "
            "reuse the shared `RNG`."},
        {"code": "import statsmodels.api as sm\n\n"
            "TRUE_BETA = 1.5          # the causal effect of X on Y (we get to know it)\n"
            "n = 20_000\n\n"
            "U = RNG.normal(size=n)                        # UNMEASURED confounder\n"
            "Z = RNG.normal(size=n)                        # the instrument\n"
            "X = 0.7*Z + 1.0*U + RNG.normal(size=n)        # first stage (Z->X) + U\n"
            "Y = TRUE_BETA*X + 2.0*U + RNG.normal(size=n)  # U also hits Y; Z does NOT\n\n"
            "print(f'true effect of X on Y = {TRUE_BETA}')\n"
            "print('U is unmeasured, so we cannot adjust for it.')"},
        {"md": "Notice what is and isn't in the equations. `Z` enters `X` but "
            "**not** `Y` directly — that is the **exclusion restriction** baked "
            "into the simulation. `U` enters both `X` and `Y` — that is the "
            "confounding. Because `Z` does not depend on `U`, the instrument is "
            "**independent** of the outcome's other causes."},
        {"md": "## 2 · OLS is biased; 2SLS recovers the truth\n\n"
            "First, the naive regression of `Y` on `X`. Because `X` carries the "
            "hidden `U`, OLS is biased. Then **two-stage least squares**: regress "
            "`X` on `Z`, keep the fitted values `X̂` (the part of `X` the "
            "instrument explains, purged of `U`), and regress `Y` on `X̂`."},
        {"code": "# --- OLS: biased under confounding ---\n"
            "ols_beta = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n\n"
            "# --- 2SLS as two OLS stages ---\n"
            "first  = sm.OLS(X, sm.add_constant(Z)).fit()   # stage 1: X on Z\n"
            "Xhat   = first.fittedvalues                     # the Z-explained part of X\n"
            "second = sm.OLS(Y, sm.add_constant(Xhat)).fit() # stage 2: Y on X-hat\n"
            "iv_beta = second.params[1]\n\n"
            "print(f'OLS  = {ols_beta:.3f}   (biased upward by U)')\n"
            "print(f'2SLS = {iv_beta:.3f}   (truth = {TRUE_BETA})')\n"
            "assert abs(iv_beta - TRUE_BETA) < 0.1, '2SLS should recover the truth'\n"
            "assert ols_beta > TRUE_BETA + 0.2, 'OLS should be visibly biased here'"},
        {"md": "The first stage is what makes this work — and its strength is "
            "something we can **test**. The first-stage F statistic measures "
            "whether `Z` genuinely moves `X` (the **relevance** assumption)."},
        {"code": "print(f'first-stage F = {first.fvalue:,.1f}')\n"
            "assert first.fvalue > 100, 'this instrument is strong (good)'\n"
            "print('F is huge -> a strong instrument. We trust the second stage.')"},
        {"md": "## 3 · The Wald estimator for a binary instrument\n\n"
            "When the instrument is **binary**, 2SLS collapses to the **Wald "
            "estimator**: the instrument's effect on `Y` divided by its effect on "
            "`X`, i.e. the *reduced form over the first stage*. In means:\n\n"
            "$$\\hat\\beta_{Wald}=\\frac{\\bar Y_{Z=1}-\\bar Y_{Z=0}}"
            "{\\bar X_{Z=1}-\\bar X_{Z=0}}.$$"},
        {"code": "TRUE2 = 2.0\n"
            "Ub = RNG.normal(size=n)\n"
            "Zb = RNG.binomial(1, 0.5, n)                   # binary instrument\n"
            "Xb = 0.3 + 0.5*Zb + 0.8*Ub + RNG.normal(size=n)\n"
            "Yb = TRUE2*Xb + 1.5*Ub + RNG.normal(size=n)\n\n"
            "num = Yb[Zb==1].mean() - Yb[Zb==0].mean()      # reduced form (Z->Y)\n"
            "den = Xb[Zb==1].mean() - Xb[Zb==0].mean()      # first stage  (Z->X)\n"
            "wald = num / den\n\n"
            "# 2SLS on the same data, for comparison\n"
            "f2 = sm.OLS(Xb, sm.add_constant(Zb)).fit()\n"
            "tsls = sm.OLS(Yb, sm.add_constant(f2.fittedvalues)).fit().params[1]\n\n"
            "print(f'Wald  = {wald:.3f}')\n"
            "print(f'2SLS  = {tsls:.3f}   (identical, as it should be)')\n"
            "print(f'truth = {TRUE2}')\n"
            "assert abs(wald - TRUE2) < 0.15\n"
            "assert abs(wald - tsls) < 1e-6, 'Wald == 2SLS for a single binary Z'"},
        {"md": "### 🔧 Exercise 3.1 — write a reusable 2SLS function\n\n"
            "Package the two-stage logic into a helper `two_stage(Z, X, Y)` that "
            "returns the IV slope. You'll reuse it for the rest of the notebook. "
            "Fill in the `# TODO`s — the skeleton already runs (the placeholders "
            "are `...`)."},
        {"code": "def two_stage(Z, X, Y):\n"
            "    \"\"\"Return the 2SLS slope of Y on X, instrumented by Z.\"\"\"\n"
            "    first_stage = ...   # TODO: sm.OLS(X, sm.add_constant(Z)).fit()\n"
            "    Xhat        = ...   # TODO: first_stage.fittedvalues\n"
            "    second_stage = ...  # TODO: sm.OLS(Y, sm.add_constant(Xhat)).fit()\n"
            "    return ...          # TODO: second_stage.params[1]\n\n"
            "# Once filled in, this should print ~1.5 and pass the assert below.\n"
            "# print(two_stage(Z, X, Y))"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "def two_stage(Z, X, Y):\n"
            "    \"\"\"Return the 2SLS slope of Y on X, instrumented by Z.\"\"\"\n"
            "    first_stage  = sm.OLS(X, sm.add_constant(Z)).fit()\n"
            "    Xhat         = first_stage.fittedvalues\n"
            "    second_stage = sm.OLS(Y, sm.add_constant(Xhat)).fit()\n"
            "    return second_stage.params[1]\n\n"
            "est = two_stage(Z, X, Y)\n"
            "print(f'two_stage(Z, X, Y) = {est:.3f}   (truth {TRUE_BETA})')\n"
            "assert abs(est - TRUE_BETA) < 0.1\n\n"
            "def first_stage_F(Z, X):\n"
            "    return sm.OLS(X, sm.add_constant(Z)).fit().fvalue"},
        {"md": "## 4 · Weak instruments: high variance, biased toward OLS\n\n"
            "Relevance is not all-or-nothing. If `Z` barely moves `X`, the Wald "
            "ratio divides by a near-zero denominator and the estimate goes "
            "haywire. We compare a **strong** instrument (first-stage coefficient "
            "0.7) with a **weak** one (0.03) by repeating each on many fresh "
            "samples and looking at the spread of the IV estimates."},
        {"code": "def make_iv_sample(m, z_coef):\n"
            "    \"\"\"One IV dataset with first-stage coefficient z_coef.\"\"\"\n"
            "    u = RNG.normal(size=m)\n"
            "    z = RNG.normal(size=m)\n"
            "    x = z_coef*z + 1.0*u + RNG.normal(size=m)\n"
            "    y = TRUE_BETA*x + 2.0*u + RNG.normal(size=m)\n"
            "    return z, x, y\n\n"
            "strong, weak = [], []\n"
            "for _ in range(300):\n"
            "    strong.append(two_stage(*make_iv_sample(2000, 0.70)))\n"
            "    weak.append(  two_stage(*make_iv_sample(2000, 0.03)))\n"
            "strong, weak = np.array(strong), np.array(weak)\n\n"
            "print(f'STRONG  mean={strong.mean():.2f}  std={strong.std():.2f}')\n"
            "print(f'WEAK    mean={weak.mean():.2f}  std={weak.std():.2f}')\n"
            "print(f'truth={TRUE_BETA}   OLS (biased) = {ols_beta:.2f}')\n"
            "print(f'weak median = {np.median(weak):.2f}  '\n"
            "      f'(pulled away from {TRUE_BETA} toward the OLS value {ols_beta:.2f})')\n\n"
            "assert weak.std() > 3*strong.std(), 'weak IV must be far noisier'\n"
            "assert abs(np.median(weak) - TRUE_BETA) > abs(strong.mean() - TRUE_BETA)\n"
            "# the weak IV's center sits between the truth and the OLS bias\n"
            "assert TRUE_BETA < np.median(weak) < ols_beta, 'weak IV is dragged toward OLS'"},
        {"code": "# The diagnostic: a single weak sample's first-stage F is tiny.\n"
            "zs, xs, ys = make_iv_sample(2000, 0.70)\n"
            "zw, xw, yw = make_iv_sample(2000, 0.03)\n"
            "print(f'strong first-stage F = {first_stage_F(zs, xs):8.1f}')\n"
            "print(f'weak   first-stage F = {first_stage_F(zw, xw):8.1f}')\n"
            "print('Rule of thumb: F < 10 -> weak instrument, do not trust the IV "
            "estimate.')\n\n"
            "# A quick picture of the two sampling distributions.\n"
            "fig, ax = plt.subplots()\n"
            "ax.hist(np.clip(weak, -10, 12), bins=40, alpha=0.6, label='weak Z')\n"
            "ax.hist(strong, bins=40, alpha=0.8, label='strong Z')\n"
            "ax.axvline(TRUE_BETA, color='k', ls='--', label='truth = 1.5')\n"
            "ax.set_title('IV estimates: strong vs weak instrument')\n"
            "ax.set_xlabel('IV estimate'); ax.legend()\n"
            "print('(figure created)')"},
        {"md": "The weak-instrument histogram is enormously wide and its center is "
            "dragged away from 1.5 toward the OLS bias. **This is why you report "
            "the first-stage F before interpreting anything.**"},
        {"md": "## 5 · LATE: an instrument identifies the complier effect\n\n"
            "An instrument only moves *some* people. Split the population into "
            "**always-takers** (treated regardless), **never-takers** (untreated "
            "regardless), and **compliers** (treated iff encouraged). With "
            "monotonicity there are no **defiers**. We give compliers a *different* "
            "treatment effect from everyone else and show that IV recovers the "
            "**complier** effect — the **LATE** — not the population **ATE**."},
        {"code": "m = 60_000\n"
            "Z = RNG.binomial(1, 0.5, m)                    # randomized encouragement\n"
            "r = RNG.random(m)\n"
            "# 50% compliers, 30% never-takers, 20% always-takers\n"
            "kind = np.where(r < 0.50, 'complier',\n"
            "        np.where(r < 0.80, 'never', 'always'))\n\n"
            "# treatment status by type (note: compliers take treatment iff Z=1)\n"
            "X = np.where(kind == 'complier', Z,\n"
            "     np.where(kind == 'always', 1.0, 0.0))\n\n"
            "# HETEROGENEOUS effects: compliers gain 3.0, others only 1.0\n"
            "tau = np.where(kind == 'complier', 3.0, 1.0)\n"
            "Y = RNG.normal(size=m) + tau*X                 # outcome = baseline + effect\n\n"
            "ate  = tau.mean()                              # population ATE = E[tau]\n"
            "late = (Y[Z==1].mean()-Y[Z==0].mean()) / (X[Z==1].mean()-X[Z==0].mean())\n\n"
            "print(f'population ATE  = {ate:.3f}   (mix of 3.0 and 1.0)')\n"
            "print(f'IV estimate    = {late:.3f}   <- targets the COMPLIER effect 3.0')\n"
            "assert abs(late - 3.0) < 0.2, 'IV should recover the complier effect'\n"
            "assert abs(late - ate) > 0.5, 'LATE is deliberately != ATE here'"},
        {"code": "# The first-stage slope for a binary Z equals the SHARE of compliers.\n"
            "complier_share = X[Z==1].mean() - X[Z==0].mean()\n"
            "print(f'first-stage slope = {complier_share:.3f}  (true complier "
            "share 0.50)')\n"
            "assert abs(complier_share - 0.50) < 0.03\n"
            "print('A stronger first stage = more compliers = a more "
            "generalizable LATE.')"},
        {"md": "### 🔧 Exercise 5.1 — one-sided noncompliance\n\n"
            "Now make it **one-sided**: there are no always-takers (you cannot get "
            "treatment unless encouraged) — only compliers and never-takers. Build "
            "60% compliers / 40% never-takers, keep the complier effect at 3.0, "
            "and confirm IV still recovers 3.0. Fill in the `# TODO`s."},
        {"code": "Z2 = RNG.binomial(1, 0.5, m)\n"
            "r2 = RNG.random(m)\n"
            "kind2 = ...   # TODO: np.where(r2 < 0.60, 'complier', 'never')\n"
            "X2 = ...      # TODO: compliers take treatment iff Z2==1, else 0.0\n"
            "tau2 = ...    # TODO: 3.0 for compliers, 1.0 otherwise\n"
            "# Y2 = RNG.normal(size=m) + tau2*X2\n"
            "# late2 = (Y2[Z2==1].mean()-Y2[Z2==0].mean()) / \\\n"
            "#         (X2[Z2==1].mean()-X2[Z2==0].mean())\n"
            "# print(late2)"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "Z2 = RNG.binomial(1, 0.5, m)\n"
            "r2 = RNG.random(m)\n"
            "kind2 = np.where(r2 < 0.60, 'complier', 'never')\n"
            "X2 = np.where(kind2 == 'complier', Z2, 0.0)\n"
            "tau2 = np.where(kind2 == 'complier', 3.0, 1.0)\n"
            "Y2 = RNG.normal(size=m) + tau2*X2\n"
            "late2 = (Y2[Z2==1].mean()-Y2[Z2==0].mean()) / \\\n"
            "        (X2[Z2==1].mean()-X2[Z2==0].mean())\n"
            "print(f'one-sided LATE = {late2:.3f}   (complier effect 3.0)')\n"
            "assert abs(late2 - 3.0) < 0.2"},
        {"md": "## 6 · Mendelian randomization: genotype as the instrument\n\n"
            "Now the instrument is a **genetic variant** `G` — an allele count "
            "(0, 1, or 2). Because alleles are allocated at random at conception, "
            "`G` is plausibly independent of lifestyle confounders. We estimate the "
            "causal effect of an exposure (`LDL` cholesterol) on an outcome "
            "(`CHD`, heart disease). With a **valid** instrument the same 2SLS "
            "ratio recovers the truth."},
        {"code": "TRUE_MR = 0.8            # true causal effect of LDL on CHD\n"
            "n = 40_000\n\n"
            "C   = RNG.normal(size=n)                       # unmeasured confounder (lifestyle)\n"
            "G   = RNG.binomial(2, 0.3, n).astype(float)    # genotype: 0/1/2 risk alleles\n"
            "LDL = 1.0 + 0.5*G + 1.0*C + RNG.normal(size=n) # variant raises LDL\n"
            "CHD = TRUE_MR*LDL + 1.5*C + RNG.normal(size=n) # G affects CHD ONLY via LDL\n\n"
            "mr_valid = two_stage(G, LDL, CHD)\n"
            "print(f'valid MR estimate = {mr_valid:.3f}   (truth {TRUE_MR})')\n"
            "print(f'first-stage F     = {first_stage_F(G, LDL):,.0f}')\n"
            "assert abs(mr_valid - TRUE_MR) < 0.1"},
        {"md": "## 7 · Pleiotropy breaks the exclusion restriction\n\n"
            "**Pleiotropy** is the MR Achilles heel: the variant affects the "
            "outcome through a *second* pathway, not via the exposure. That is a "
            "direct arrow `G → CHD`, which violates **exclusion**. Watch the "
            "estimate break."},
        {"code": "# Same data, but now G ALSO hits CHD directly (pleiotropy):\n"
            "CHD_pleio = TRUE_MR*LDL + 1.5*C + 0.9*G + RNG.normal(size=n)\n"
            "#                                  ^^^^^ direct G->CHD path (exclusion violated)\n\n"
            "mr_pleio = two_stage(G, LDL, CHD_pleio)\n"
            "print(f'valid MR        = {mr_valid:.3f}   (truth {TRUE_MR})')\n"
            "print(f'pleiotropic MR  = {mr_pleio:.3f}   (badly biased upward)')\n"
            "assert mr_pleio > TRUE_MR + 0.3, 'pleiotropy should inflate the estimate'"},
        {"md": "With a **single** variant there is no way to tell a real effect "
            "from pleiotropy — the bias hides inside the ratio. The fix is to use "
            "**many** independent variants, which lets us *detect* pleiotropy."},
        {"md": "## 8 · The robustness check: MR-Egger\n\n"
            "With many variants, each contributes a (SNP→exposure, SNP→outcome) "
            "pair `(γⱼ, Γⱼ)`. Under valid instruments `Γⱼ ≈ β·γⱼ`, so a line "
            "through the origin has slope `β`. **MR-Egger** instead fits a line "
            "*with an intercept*: a non-zero intercept signals **directional "
            "pleiotropy**, and the slope is a pleiotropy-robust effect.\n\n"
            "We simulate 30 variants, each with its own direct (pleiotropic) effect "
            "on the outcome, and compare the naive inverse-variance-weighted (IVW) "
            "slope with MR-Egger."},
        {"code": "TRUE_BETA_MR = 0.8\n"
            "J = 30                                   # number of genetic variants\n"
            "N = 60_000\n\n"
            "gamma = RNG.uniform(0.10, 0.60, J)        # each variant's effect on exposure\n"
            "alpha = RNG.uniform(0.05, 0.25, J)        # DIRECTIONAL pleiotropy (all positive)\n\n"
            "Cc = RNG.normal(size=N)                                   # confounder\n"
            "Gm = np.column_stack([RNG.binomial(2, 0.3, N).astype(float)\n"
            "                      for _ in range(J)])\n"
            "Exposure = 1.0 + Gm @ gamma + 1.0*Cc + RNG.normal(size=N)\n"
            "Outcome  = TRUE_BETA_MR*Exposure + Gm @ alpha + 1.5*Cc + RNG.normal(size=N)\n\n"
            "# per-variant SNP->exposure (gx) and SNP->outcome (gy) associations\n"
            "gx = np.array([sm.OLS(Exposure, sm.add_constant(Gm[:, j])).fit().params[1]\n"
            "               for j in range(J)])\n"
            "gy = np.array([sm.OLS(Outcome,  sm.add_constant(Gm[:, j])).fit().params[1]\n"
            "               for j in range(J)])\n"
            "print(f'{J} variants simulated; pleiotropy is present (alpha > 0).')"},
        {"code": "# IVW: regress gy on gx THROUGH THE ORIGIN (slope only).\n"
            "ivw_slope = sm.OLS(gy, gx[:, None]).fit().params[0]\n\n"
            "# MR-Egger: regress gy on gx WITH an intercept.\n"
            "egger = sm.OLS(gy, sm.add_constant(gx)).fit()\n"
            "egger_intercept, egger_slope = egger.params[0], egger.params[1]\n\n"
            "print(f'truth            = {TRUE_BETA_MR}')\n"
            "print(f'IVW slope        = {ivw_slope:.3f}   (biased up by pleiotropy)')\n"
            "print(f'MR-Egger interc. = {egger_intercept:.3f}   (non-zero -> "
            "pleiotropy detected!)')\n"
            "print(f'MR-Egger slope   = {egger_slope:.3f}   (closer to the truth)')\n\n"
            "assert egger_intercept > 0.05, 'a non-zero intercept flags directional pleiotropy'\n"
            "assert abs(egger_slope - TRUE_BETA_MR) < abs(ivw_slope - TRUE_BETA_MR)"},
        {"code": "# The classic MR-Egger scatter: each point is a variant.\n"
            "xx = np.linspace(0, gx.max()*1.05, 50)\n"
            "fig, ax = plt.subplots()\n"
            "ax.scatter(gx, gy, s=30, alpha=0.7, label='variants')\n"
            "ax.plot(xx, ivw_slope*xx, label=f'IVW (slope {ivw_slope:.2f})')\n"
            "ax.plot(xx, egger_intercept + egger_slope*xx,\n"
            "        label=f'MR-Egger (int {egger_intercept:.2f})')\n"
            "ax.axhline(0, color='grey', lw=0.8)\n"
            "ax.set_xlabel('SNP -> exposure (gx)'); ax.set_ylabel('SNP -> outcome (gy)')\n"
            "ax.set_title('MR-Egger: a non-zero intercept = directional pleiotropy')\n"
            "ax.legend()\n"
            "print('(figure created) The Egger line does NOT pass through the origin.')"},
        {"md": "### 🔧 Exercise 8.1 — does Egger's intercept vanish without pleiotropy?\n\n"
            "Re-simulate the outcome with **no** pleiotropy (set every `alpha` to "
            "0, i.e. drop the `Gm @ alpha` term) and recompute the MR-Egger "
            "intercept. It should now sit near zero, and IVW and Egger should "
            "agree. Fill in the `# TODO`s."},
        {"code": "alpha0 = np.zeros(J)                       # NO pleiotropy\n"
            "Outcome0 = ...   # TODO: TRUE_BETA_MR*Exposure + Gm @ alpha0 + 1.5*Cc + RNG.normal(size=N)\n"
            "# gy0 = np.array([sm.OLS(Outcome0, sm.add_constant(Gm[:, j])).fit().params[1]\n"
            "#                 for j in range(J)])\n"
            "# egger0 = sm.OLS(gy0, sm.add_constant(gx)).fit()\n"
            "# print('intercept without pleiotropy:', egger0.params[0])"},
        {"md": "### ✅ Solution 8.1"},
        {"code": "alpha0 = np.zeros(J)\n"
            "Outcome0 = TRUE_BETA_MR*Exposure + Gm @ alpha0 + 1.5*Cc + RNG.normal(size=N)\n"
            "gy0 = np.array([sm.OLS(Outcome0, sm.add_constant(Gm[:, j])).fit().params[1]\n"
            "                for j in range(J)])\n"
            "egger0 = sm.OLS(gy0, sm.add_constant(gx)).fit()\n"
            "ivw0   = sm.OLS(gy0, gx[:, None]).fit().params[0]\n"
            "print(f'intercept WITHOUT pleiotropy = {egger0.params[0]:.3f}  (~0)')\n"
            "print(f'IVW slope = {ivw0:.3f}   Egger slope = {egger0.params[1]:.3f}'\n"
            "      f'   (both ~{TRUE_BETA_MR})')\n"
            "assert abs(egger0.params[0]) < 0.03, 'no pleiotropy -> intercept ~ 0'\n"
            "assert abs(ivw0 - TRUE_BETA_MR) < 0.05"},
        {"md": "## Wrap-up & self-check\n\n"
            "- **OLS is biased** under unmeasured confounding; **2SLS** (two OLS "
            "stages) and the **Wald** ratio recover the truth when the instrument "
            "is valid.\n"
            "- The four assumptions: **relevance** (testable — first-stage F), "
            "**exclusion** and **independence** (untestable — argued), and "
            "**monotonicity** (names the estimand).\n"
            "- IV identifies the **LATE** — the **complier** effect — which need "
            "not equal the ATE.\n"
            "- A **weak instrument** (small first-stage F) gives a high-variance "
            "estimate biased back toward OLS. Always report the F.\n"
            "- In **Mendelian randomization**, genotype is the instrument; "
            "**pleiotropy** breaks exclusion, and **MR-Egger**'s intercept detects "
            "directional pleiotropy.\n\n"
            "**You're ready for Week 9** (regression discontinuity) if you can "
            "implement 2SLS from memory, read a first-stage F, and explain why "
            "pleiotropy biases an MR estimate. And good luck on the **midterm "
            "(Weeks 1–7)**."},
    ],
}
