# -*- coding: utf-8 -*-
"""Week 2 — Potential Outcomes. Content module."""

WEEK = {
    "number": 2,
    "slug": "potential_outcomes",
    "title": "Potential Outcomes",
    "block": "Block I — Foundations",
    "subtitle": "The Neyman–Rubin framework: counterfactuals, estimands, and the "
                "assumptions that license a causal claim.",
    "deliverable": "Problem Set 2 — define the estimand, check the assumptions; "
                   "Workshop 2 — potential outcomes in code (science table, "
                   "randomization vs. confounded comparison).",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab (2–3h).",
    "one_sentence": "Every causal claim is a statement about potential outcomes "
        "Y(1) and Y(0); since we never see both for the same unit, a causal "
        "effect is identified only when stated assumptions let an observed "
        "comparison stand in for the missing counterfactual.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Write a causal effect in potential-outcomes notation and explain the "
        "fundamental problem of causal inference in one sentence.",
        "State the estimand FIRST — ATE, ATT, or CATE — and say which question "
        "each one answers and for whom.",
        "List the identifying assumptions (SUTVA, consistency, conditional "
        "exchangeability, positivity) and name where each one is used.",
        "Diagnose a scenario: decide whether each assumption plausibly holds, "
        "and name the specific violation when it does not.",
        "Explain why randomization buys exchangeability for free, and "
        "distinguish identification from estimation as two separate steps.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Hernán & Robins, Causal Inference: What If — Chapters 1–3.",
         "look_for": "the precise statement of consistency and exchangeability, "
                     "and where each one is used in moving from data to a causal "
                     "effect."},
        {"text": "Imbens & Rubin, Causal Inference for Statistics, Social, and "
                 "Biomedical Sciences — Chapters 1–2.",
         "look_for": "the potential-outcomes table and what the 'science table' "
                     "would contain if we could observe both columns at once."},
    ],
    "optional_readings": [
        {"text": "Huntington-Klein, The Effect — potential outcomes.",
         "note": "A gentle, example-driven on-ramp to Y(1)/Y(0) if the notation "
                 "feels fast."},
        {"text": "Cunningham, The Mixtape — potential outcomes chapter.",
         "note": "The applied, code-first treatment, with switching-equation "
                 "bookkeeping you'll reuse all term."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "Two potential outcomes per unit",
         "body": "For each unit i imagine two numbers: Y_i(1), the outcome if i "
            "were treated, and Y_i(0), the outcome if i were not. The individual "
            "causal effect is the contrast Y_i(1) − Y_i(0). Reality reveals only "
            "the one that matches the treatment actually received; the other is "
            "the counterfactual. The 'science table' — every unit's full pair — "
            "is what we wish we had; the observed data is that table with one "
            "cell per row blacked out."},
        {"heading": "The fundamental problem of causal inference",
         "body": "We never observe both Y_i(1) and Y_i(0) for the same unit, so "
            "the individual effect is never directly measurable. Causal inference "
            "is therefore a missing-data problem. We give up on individuals and "
            "target a population average instead — which is recoverable only if "
            "the units we DO see treated are a fair stand-in for the units we see "
            "untreated."},
        {"heading": "State the estimand first",
         "body": "Before any data or model, name the quantity you want. Different "
            "estimands answer different questions and need not be equal.",
         "bullets": [
            [("ATE  E[Y(1) − Y(0)]. ", {"bold": True}),
             ("Average effect if EVERYONE were treated vs. everyone untreated. "
              "The policy-wide question.", {})],
            [("ATT  E[Y(1) − Y(0) | A = 1]. ", {"bold": True}),
             ("Average effect among the actually treated. The right target when "
              "you ask 'did the program help the people who took it?'", {})],
            [("CATE  E[Y(1) − Y(0) | X = x]. ", {"bold": True}),
             ("Effect within a covariate stratum — the basis for "
              "personalization and heterogeneity (Week 13).", {})],
         ],
         "callout": {"title": "Why the order matters",
            "color": "RED",
            "lines": ["If you fit the model first and read off 'the effect,' you "
                      "have let the software choose your estimand — usually a "
                      "weird weighted average no one asked for.",
                      "Question → estimand → assumptions → identification → "
                      "estimation. In that order, every time."]}},
        {"heading": "The four assumptions that license a causal claim",
         "body": "These turn an observed difference in means into E[Y(1) − Y(0)]. "
                 "Each does a specific job; drop one and identification fails.",
         "bullets": [
            [("SUTVA. ", {"bold": True}),
             ("No interference (your treatment doesn't affect my outcome) and a "
              "single well-defined version of treatment. Vaccines and "
              "marketplace prices routinely break the no-interference half.", {})],
            [("Consistency. ", {"bold": True}),
             ("The outcome we observe under the treatment actually taken equals "
              "that unit's potential outcome: A = a ⇒ Y = Y(a). Needs a "
              "well-defined intervention — 'effect of obesity' has many.", {})],
            [("Conditional exchangeability (ignorability). ", {"bold": True}),
             ("Within levels of measured covariates X, treatment is independent "
              "of the potential outcomes: Y(a) ⟂ A | X. No unmeasured "
              "confounding. This is the unverifiable one.", {})],
            [("Positivity (overlap). ", {"bold": True}),
             ("Every covariate stratum that exists has some chance of each "
              "treatment: 0 < P(A = 1 | X = x) < 1. Without it there is no one "
              "to compare to and the estimand is undefined there.", {})],
         ],
         "callout": {"title": "Identification ≠ estimation",
            "color": "BLUE",
            "lines": ["Identification asks: under these assumptions, can the "
                      "effect be written as a function of the observable "
                      "distribution at all? It is a logic question; more data "
                      "cannot rescue a failure.",
                      "Estimation asks: given that it can, how well do we compute "
                      "it from a finite, noisy sample? That is statistics — bias, "
                      "variance, confidence intervals."]}},
        {"heading": "Randomization, the assumption-light gold standard",
         "body": "Randomly assigning treatment makes A independent of EVERYTHING "
            "about a unit, including Y(1) and Y(0) — measured or not. That delivers "
            "(unconditional) exchangeability by design, so the simple difference "
            "in group means is unbiased for the ATE. You still need SUTVA, "
            "consistency, and positivity, but you no longer have to defend "
            "'no unmeasured confounding' — the coin flip guarantees it. Everything "
            "else this term is an attempt to recover, from observational data, "
            "what randomization would have given you for free."},
    ],
    "problem_set": {
        "label": "Problem Set 2",
        "title": "Define the estimand, check the assumptions",
        "intro": "For each scenario: (a) write the target estimand in "
            "potential-outcomes notation, (b) name the assumption in question, "
            "(c) state whether it plausibly holds, and (d) give one sentence of "
            "justification or the specific fix. Try all five before you look.",
        "problems": [
            {"title": "Translate a vague question into an estimand",
             "prompt": "A hospital asks: 'Does our new discharge-planning program "
                "work?' The program is offered to all patients but only some "
                "enroll. Leadership cares about the patients who actually go "
                "through it. Write the appropriate estimand, and contrast it with "
                "the ATE. Which would a city-wide mandate need instead?",
             "solution_title": "Target the ATT for 'did it help enrollees'; the "
                "ATE for a mandate.",
             "solution": [
                "'Did the program help the people who took it?' is the ATT: "
                "E[Y(1) − Y(0) | A = 1], averaged only over enrollees.",
                "The ATE, E[Y(1) − Y(0)], imagines giving the program to "
                "everyone — including patients who would never have enrolled and "
                "may respond differently. It answers the mandate question.",
                "They coincide only under constant or randomly-distributed "
                "effects. State which one you mean before estimating, because the "
                "two numbers can differ in size and even in sign."]},
            {"title": "A vaccine trial in shared households (SUTVA)",
             "prompt": "You randomize a vaccine within households and measure each "
                "person's infection. Vaccinating one member lowers the others' "
                "exposure. You also discover two 'doses' were administered: a "
                "full course and a partial course recorded identically. Does "
                "SUTVA hold? What breaks, and what would you do?",
             "solution_title": "SUTVA fails on both counts — interference and "
                "multiple versions of treatment.",
             "solution": [
                "Interference: one person's treatment changes another's outcome, "
                "so Y_i(a_i) is not well defined without the whole household's "
                "assignment vector. Y_i now depends on others' a, not just a_i.",
                "Multiple versions: 'vaccinated' lumps full and partial courses "
                "with different effects, so consistency has no single Y(1) to "
                "point at.",
                "Fixes: randomize at the household (cluster) level and define the "
                "estimand on clusters; or model interference explicitly "
                "(spillover/exposure mapping). Separate the two dose versions "
                "into distinct, well-defined treatments."]},
            {"title": "Spot the positivity violation",
             "prompt": "You want the effect of an intensive-care protocol on "
                "survival, adjusting for age. In your data, NO patient over 80 "
                "ever received the protocol, and EVERY patient under 40 did. You "
                "fit a model with an age term and read off an effect for all "
                "ages. What assumption is violated and what does the model do at "
                "those ages?",
             "solution_title": "Positivity fails at the age extremes — the effect "
                "there is not identified.",
             "solution": [
                "Positivity needs 0 < P(A = 1 | age) < 1 for every age that "
                "occurs. Here P(A = 1 | age > 80) = 0 and P(A = 1 | age < 40) = 1, "
                "so there is no untreated <40 and no treated >80 to compare.",
                "Any 'effect' the model reports at those ages is pure "
                "extrapolation from the functional form, not from data — the "
                "regression silently invents the missing counterfactuals.",
                "Fix: restrict the estimand to the region of overlap (e.g. ages "
                "40–80), or trim/redefine the target population. Honest "
                "non-identification beats a confident extrapolation."]},
            {"title": "The effect of obesity (consistency)",
             "prompt": "A paper estimates 'the causal effect of obesity (BMI ≥ 30) "
                "on mortality.' A reviewer objects that 'obesity' is not a "
                "well-defined intervention. Whose objection targets which "
                "assumption, and why does it matter for what the estimate means?",
             "solution_title": "Consistency is ill-posed — 'obesity' has many "
                "versions, so Y(1) is ambiguous.",
             "solution": [
                "Consistency requires A = a ⇒ Y = Y(a), which presumes a single "
                "version of 'being obese.' But BMI ≥ 30 reached via diet, via "
                "inactivity, or via a metabolic disorder may carry different "
                "mortality — there is no one Y(1).",
                "Without a well-defined intervention the counterfactual 'what if "
                "this person were not obese' has no unique meaning, so the "
                "estimand itself is unclear before any data issue arises.",
                "Fix: define a concrete, manipulable intervention — e.g. 'the "
                "effect of a specified diet/exercise program on mortality' — for "
                "which Y(1) and Y(0) are unambiguous."]},
            {"title": "Why randomization buys exchangeability",
             "prompt": "In an observational study, sicker patients are more likely "
                "to get a drug, so treated and untreated differ in baseline risk. "
                "A colleague says 'just randomize.' Explain precisely, in "
                "potential-outcomes terms, what randomization changes — and what "
                "it does NOT free you from.",
             "solution_title": "Randomization makes A ⟂ {Y(1), Y(0)} by design — "
                "exchangeability for free.",
             "solution": [
                "Observationally, A correlates with the potential outcomes "
                "(sicker → treated and sicker → worse Y(0)), so E[Y | A=1] − "
                "E[Y | A=0] mixes the drug effect with baseline differences.",
                "A coin flip assigns A independently of every unit characteristic, "
                "so Y(a) ⟂ A holds unconditionally — measured AND unmeasured "
                "confounders are balanced in expectation. The naive difference in "
                "means is then unbiased for the ATE.",
                "It does NOT free you from SUTVA, consistency, or positivity, and "
                "in a finite sample chance imbalance and noncompliance can still "
                "bite — randomization licenses identification, not perfect "
                "estimation."]},
        ],
    },
    "lab": {
        "label": "Workshop 2",
        "title": "Potential outcomes in code",
        "goal": "build a finite-population 'science table' with a known true ATE, "
            "confirm that a randomized experiment recovers it in expectation, and "
            "show that a confounded observational comparison does not. Pick R or "
            "Python — both are supported all term.",
        "steps": [
            {"heading": "Step 1 · Build the science table",
             "body": "Create N units, each with BOTH potential outcomes Y(0) and "
                "Y(1). Because you wrote them, the TRUE individual effects — and "
                "their average, the true ATE — are known exactly. This is the "
                "table nature hides from us.",
             "code_r": "set.seed(2)\nN  <- 5000\n"
                "X  <- rnorm(N)                      # a baseline covariate (risk)\n"
                "Y0 <- 1.0 + 0.8 * X + rnorm(N)      # potential outcome if untreated\n"
                "tau <- 2.0 + 0.5 * X                # heterogeneous true effect\n"
                "Y1 <- Y0 + tau                      # potential outcome if treated\n"
                "true_ATE <- mean(Y1 - Y0)\n"
                'cat(sprintf("true ATE = %.3f\\n", true_ATE))',
             "code_python": "import numpy as np\nrng = np.random.default_rng(2)\n"
                "N  = 5000\n"
                "X  = rng.normal(size=N)                 # baseline covariate (risk)\n"
                "Y0 = 1.0 + 0.8 * X + rng.normal(size=N) # potential outcome if untreated\n"
                "tau = 2.0 + 0.5 * X                     # heterogeneous true effect\n"
                "Y1 = Y0 + tau                           # potential outcome if treated\n"
                "true_ATE = (Y1 - Y0).mean()\n"
                'print(f"true ATE = {true_ATE:.3f}")'},
            {"heading": "Step 2 · The fundamental problem — reveal one column",
             "body": "Assign treatment A and reveal only the matching potential "
                "outcome via the switching equation Y = A·Y(1) + (1−A)·Y(0). The "
                "other column is now missing, exactly as in real data.",
             "code_r": "A <- rbinom(N, 1, 0.5)              # complete randomization\n"
                "Y <- A * Y1 + (1 - A) * Y0          # switching equation\n"
                "# Y0 for the treated and Y1 for the untreated are now unobserved.",
             "code_python": "A = rng.binomial(1, 0.5, N)          # complete randomization\n"
                "Y = A * Y1 + (1 - A) * Y0            # switching equation\n"
                "# Y0 for the treated and Y1 for the untreated are now unobserved."},
            {"heading": "Step 3 · Randomization recovers the ATE",
             "body": "Under random assignment the simple difference in observed "
                "group means estimates the ATE. Compare it to the truth — it "
                "should land within sampling error.",
             "code_r": 'rand_est <- mean(Y[A == 1]) - mean(Y[A == 0])\n'
                'cat(sprintf("randomized diff = %.3f  (true %.3f)\\n",\n'
                '            rand_est, true_ATE))',
             "code_python": "rand_est = Y[A == 1].mean() - Y[A == 0].mean()\n"
                'print(f"randomized diff = {rand_est:.3f}  (true {true_ATE:.3f})")'},
            {"heading": "Step 4 · A confounded comparison is biased",
             "body": "Now assign treatment by the covariate X (sicker units more "
                "likely treated). X drives both A and the potential outcomes, so "
                "the naive difference is contaminated. The SAME science table — a "
                "different assignment — and the estimate breaks.",
             "code_r": "p   <- plogis(1.2 * X)              # X pushes treatment\n"
                "Ac  <- rbinom(N, 1, p)\n"
                "Yc  <- Ac * Y1 + (1 - Ac) * Y0\n"
                "conf_est <- mean(Yc[Ac == 1]) - mean(Yc[Ac == 0])\n"
                'cat(sprintf("confounded diff = %.3f  (true %.3f)\\n",\n'
                '            conf_est, true_ATE))',
             "code_python": "p   = 1 / (1 + np.exp(-1.2 * X))    # X pushes treatment\n"
                "Ac  = rng.binomial(1, p)\n"
                "Yc  = Ac * Y1 + (1 - Ac) * Y0\n"
                "conf_est = Yc[Ac == 1].mean() - Yc[Ac == 0].mean()\n"
                'print(f"confounded diff = {conf_est:.3f}  (true {true_ATE:.3f})")'},
        ],
        "expected": "The randomized difference sits right on the true ATE (~2.0). "
            "The confounded difference is pulled away from it — because the "
            "treated units had systematically higher X (and thus higher Y(0) AND "
            "Y(1)), part of that baseline gap is misread as a treatment effect. "
            "Same potential outcomes, two assignment mechanisms, two stories — and "
            "only the design that breaks the A–{Y(1),Y(0)} link tells the truth.",
        "submit": [
            "Push your code and a one-paragraph README reporting the true ATE, the "
            "randomized estimate, and the confounded estimate, with one sentence "
            "on why the last one is off.",
            "Add a short note: which assumption did the confounded design violate, "
            "and how would adjusting for X help?",
            "Bring your active-reading sentences (from the guided reading) to lab.",
        ],
    },
    "self_check": [
        "Write the ATE, ATT, and CATE in potential-outcomes notation from memory.",
        "State the fundamental problem of causal inference in one sentence.",
        "Name the four identifying assumptions and what each one rules out.",
        "Explain why randomization gives exchangeability without measuring "
        "confounders.",
        "Say in one line how identification differs from estimation.",
    ],
    "next_week": {
        "heading": "Coming up: Week 3 — Randomized experiments & A/B testing",
        "teaser": "We cash in the gold standard. With exchangeability guaranteed "
            "by design, we turn to running experiments well: randomization "
            "schemes, A/B tests at scale, power and sample size, and the threats "
            "— noncompliance, attrition, and peeking — that can still bias a "
            "perfectly randomized study. Skim Gerber & Green Chapters 2–3 to get "
            "a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 2", "items": [
            {"t": "Potential outcomes", "d": "Y(1) and Y(0): two worlds for every "
             "unit."},
            {"t": "The fundamental problem", "d": "Why the individual effect is "
             "never observed."},
            {"t": "Estimands", "d": "ATE, ATT, CATE — and stating the target "
             "first."},
            {"t": "Identifying assumptions", "d": "SUTVA, consistency, "
             "exchangeability, positivity."},
            {"t": "Randomization", "d": "The assumption-light gold standard."},
            {"t": "A real case + workflow", "d": "Perry Preschool and identify vs. "
             "estimate."},
        ]},
        {"type": "content", "kicker": "Recap & bridge",
         "title": "Last week's graphs, made into quantities",
         "bullets": [
            "Week 1 gave us the vocabulary: confounder, mediator, collider, and "
            "P(Y | do(X)).",
            "Graphs tell you WHAT to adjust for. Potential outcomes tell you "
            "WHAT you are estimating and whether it is recoverable.",
            ("Today we make the counterfactual a concrete number: Y(1) − Y(0).", 1),
            "Same causal content, a complementary dialect — Neyman–Rubin "
            "alongside Pearl.",
            "By the end you can state an estimand and defend the assumptions that "
            "identify it.",
         ],
         "note": {"title": "Stance",
            "body": "Graphs to decide what to adjust for; potential outcomes to "
            "define and estimate the effect."}},

        {"type": "section", "kicker": "Part 1", "title": "Potential outcomes",
         "subtitle": "Two outcomes live inside every unit; the world reveals only "
            "one. Causal inference is the science of the missing one."},
        {"type": "content", "kicker": "The core object",
         "title": "Y(1) and Y(0): two outcomes per unit", "bullets": [
            "For each unit, imagine Y(1) if treated and Y(0) if not — both exist "
            "as quantities.",
            "The individual causal effect is the contrast Y(1) − Y(0).",
            "Treatment doesn't create the effect from nothing; it selects which "
            "world we get to see.",
            ("'Effect' is always a comparison of two potential outcomes for the "
             "SAME unit.", 1),
         ],
         "note": {"title": "Notation",
            "body": "A = treatment (1/0), Y = observed outcome, Y(a) = potential "
            "outcome under treatment a."}},
        {"type": "content", "kicker": "Bookkeeping",
         "title": "The switching equation links worlds to data", "bullets": [
            "We observe Y = A·Y(1) + (1 − A)·Y(0) — only the column that matches "
            "the treatment taken.",
            "Consistency is what lets us write Y = Y(A) at all.",
            "The other potential outcome becomes the counterfactual: real, but "
            "unobserved.",
            "So the observed dataset is the full science table with one cell per "
            "row erased.",
         ],
         "note": {"title": "Switching equation",
            "body": "Y = A·Y(1) + (1−A)·Y(0). Observation = selection, not "
            "creation."}},
        {"type": "table", "kicker": "What nature hides",
         "title": "The science table (if only we could see it)",
         "headers": ["Unit", "Y(0)", "Y(1)", "Effect Y(1)−Y(0)"],
         "rows": [
            ["Ann", "3", "5", "+2"],
            ["Ben", "4", "4", "0"],
            ["Cal", "2", "7", "+5"],
            ["Dee", "6", "5", "−1"],
            ["…", "…", "…", "…"],
         ],
         "note": {"title": "Reality",
            "body": "For each row you see exactly ONE of Y(0), Y(1) — the other "
            "is blacked out. That missing column is the whole challenge."}},
        {"type": "statement",
         "quote": "We never observe an individual causal effect. Not once. Not "
            "ever.",
         "attribution": "The fundamental problem of causal inference. The "
            "counterfactual is missing by construction — so we trade the "
            "individual for a population average we CAN recover."},

        {"type": "section", "kicker": "Part 2",
         "title": "The fundamental problem",
         "subtitle": "Causal inference is a missing-data problem. The fix is to "
            "stop chasing individuals and target an average."},
        {"type": "content", "kicker": "From individual to average",
         "title": "Give up the individual, target the population", "bullets": [
            "Y(1) − Y(0) for one person is unknowable — its counterfactual is "
            "missing.",
            "But the AVERAGE E[Y(1) − Y(0)] can be recovered if groups are "
            "comparable.",
            "Naively, E[Y(1)] ≈ mean Y among treated, E[Y(0)] ≈ mean Y among "
            "untreated.",
            ("That swap is legitimate ONLY when treated and untreated are "
             "exchangeable.", 1),
         ],
         "note": {"title": "Key move",
            "body": "Population averages are estimable; individual effects are "
            "not. State the average you want."}},
        {"type": "compare", "kicker": "Where bias comes from",
         "title": "Why the naive difference can lie", "columns": [
            {"head": "What we want", "sub": "causal", "points": [
                "E[Y(1)] − E[Y(0)]",
                "Same units, both worlds.",
                "The treatment effect."]},
            {"head": "What we compute", "sub": "observed", "points": [
                "E[Y | A=1] − E[Y | A=0]",
                "Different units in each arm.",
                "Effect + baseline difference."]},
            {"head": "The gap", "sub": "bias", "points": [
                "E[Y(0) | A=1] − E[Y(0) | A=0]",
                "Selection / confounding bias.",
                "Zero only if exchangeable."]},
         ]},

        {"type": "section", "kicker": "Part 3", "title": "Estimands",
         "subtitle": "Name the quantity before you touch the data. Different "
            "estimands answer different questions — and need not be equal."},
        {"type": "content", "kicker": "Discipline",
         "title": "State the estimand FIRST", "bullets": [
            "An estimand is the precise quantity you want, defined before any "
            "model.",
            "Fit-first analysis lets the software pick a weird weighted average "
            "you never chose.",
            "The question fixes the estimand; the estimand constrains the method.",
            ("Question → estimand → assumptions → identification → estimation.", 1),
         ],
         "note": {"title": "Habit",
            "body": "If you can't write the estimand in one line, you don't yet "
            "know what you're estimating."}},
        {"type": "table", "kicker": "The three you'll use most",
         "title": "ATE, ATT, CATE",
         "headers": ["Estimand", "Definition", "Question it answers"],
         "rows": [
            ["ATE", "E[Y(1) − Y(0)]",
             "Effect if EVERYONE were treated vs. not — policy-wide."],
            ["ATT", "E[Y(1) − Y(0) | A=1]",
             "Effect among those who actually got treated."],
            ["CATE", "E[Y(1) − Y(0) | X=x]",
             "Effect within a subgroup — basis for personalization."],
         ],
         "note": {"title": "Not interchangeable",
            "body": "ATE and ATT coincide only under constant or randomly-spread "
            "effects. Say which you mean."}},
        {"type": "compare", "kicker": "Choosing the target",
         "title": "ATE vs. ATT — a worked contrast", "columns": [
            {"head": "Ask the ATT when…", "points": [
                "You care about the people who took the treatment.",
                "'Did the program help its enrollees?'",
                "Evaluating a voluntary program."]},
            {"head": "Ask the ATE when…", "points": [
                "You'd roll the treatment out to everyone.",
                "'Should we mandate this for all?'",
                "Including never-takers who may respond differently."]},
        ]},

        {"type": "section", "kicker": "Part 4",
         "title": "The identifying assumptions",
         "subtitle": "Four conditions turn an observed difference into a causal "
            "effect. Each does one job; drop one and identification fails."},
        {"type": "content", "kicker": "Assumption 1",
         "title": "SUTVA — no interference, one version", "bullets": [
            "No interference: my treatment doesn't change your outcome.",
            "One version of treatment: 'treated' means a single well-defined "
            "thing.",
            "Breaks under spillovers (vaccines, networks) and ambiguous doses.",
            ("Lets us write a unit's Y(a) from its OWN a alone.", 1),
         ],
         "note": {"title": "Watch for",
            "body": "Marketplaces, infectious disease, social networks — "
            "interference is the rule, not the exception."}},
        {"type": "content", "kicker": "Assumption 2",
         "title": "Consistency — observed equals potential", "bullets": [
            "If A = a then the observed Y equals that unit's Y(a): A = a ⇒ Y = "
            "Y(a).",
            "Requires a well-defined intervention you could actually assign.",
            "'Effect of obesity' fails it — too many versions, no single Y(1).",
            ("Connects the abstract potential outcome to the number in your data.",
             1),
         ],
         "note": {"title": "Test",
            "body": "Could you write the treatment as a concrete protocol someone "
            "could administer? If not, fix the estimand."}},
        {"type": "content", "kicker": "Assumption 3",
         "title": "Conditional exchangeability (ignorability)", "bullets": [
            "Within levels of measured X, treatment is independent of potential "
            "outcomes: Y(a) ⟂ A | X.",
            "Equivalently: no unmeasured confounding given X.",
            "This is the assumption you cannot verify from data — you defend it.",
            ("It is what 'adjust for confounders' is really buying you.", 1),
         ],
         "note": {"title": "The hard one",
            "body": "Untestable. Argued from design and domain knowledge, "
            "stress-tested with sensitivity analysis (later weeks)."}},
        {"type": "content", "kicker": "Assumption 4",
         "title": "Positivity (overlap)", "bullets": [
            "Every covariate stratum has a real chance of each treatment: 0 < "
            "P(A=1 | X) < 1.",
            "Without overlap there is literally no one to compare to.",
            "Models 'fix' it silently by extrapolating — confident, and wrong.",
            ("Check it; if it fails, restrict the estimand to the overlap region.",
             1),
         ],
         "note": {"title": "Diagnostic",
            "body": "Plot the propensity-score distributions by arm. Gaps at 0 or "
            "1 are positivity violations."}},
        {"type": "steps", "kicker": "How the assumptions stack",
         "title": "From observed difference to the ATE", "steps": [
            {"title": "Consistency", "body": "— ties Y to Y(A), so means are "
             "means of potential outcomes."},
            {"title": "Exchangeability", "body": "— makes the treated a fair "
             "stand-in for the untreated (given X)."},
            {"title": "Positivity", "body": "— guarantees a comparison group "
             "exists in every stratum."},
            {"title": "SUTVA", "body": "— keeps each Y(a) well defined "
             "throughout."},
         ],
         "note": "All four together license E[Y|A=1,X]−E[Y|A=0,X], averaged over "
            "X, as the ATE."},

        {"type": "section", "kicker": "Part 5", "title": "Randomization",
         "subtitle": "The assumption-light gold standard: a coin flip buys "
            "exchangeability without measuring a single confounder."},
        {"type": "content", "kicker": "Why it works",
         "title": "Randomization makes A ⟂ {Y(1), Y(0)}", "bullets": [
            "Assigning treatment by chance makes it independent of every unit "
            "trait — measured or not.",
            "So Y(a) ⟂ A holds UNCONDITIONALLY: exchangeability for free.",
            "The simple difference in group means is then unbiased for the ATE.",
            ("No need to defend 'no unmeasured confounding' — design guarantees "
             "it.", 1),
         ],
         "note": {"title": "Gold standard",
            "body": "Randomized experiments physically realize do(A) — the cleanest "
            "route to a causal effect."}},
        {"type": "compare", "kicker": "Still not free of everything",
         "title": "What randomization does and does not buy", "columns": [
            {"head": "Gives you", "points": [
                "Exchangeability by design.",
                "Balance of measured AND unmeasured confounders (in expectation).",
                "An unbiased difference-in-means."]},
            {"head": "Still need", "points": [
                "SUTVA, consistency, positivity.",
                "Compliance, low attrition, no peeking.",
                "Enough n — chance imbalance shrinks with size."]},
        ]},

        {"type": "section", "kicker": "Part 6",
         "title": "Identification vs. estimation",
         "subtitle": "Two distinct jobs. One is logic; the other is statistics. "
            "Conflating them is a classic error."},
        {"type": "compare", "kicker": "Two separate questions",
         "title": "Can we, vs. how well can we", "columns": [
            {"head": "IDENTIFICATION", "points": [
                "Can the estimand be written from the observable distribution at "
                "all?",
                "A logic/assumptions question.",
                "Answered with potential outcomes or DAGs.",
                "If it fails, more data won't help."]},
            {"head": "ESTIMATION", "points": [
                "Given identification, how well from a finite sample?",
                "A statistics question.",
                "Bias, variance, confidence intervals.",
                "More data tightens the estimate."]},
        ]},
        {"type": "statement",
         "quote": "No identification, no amount of data. No estimation, no number.",
         "attribution": "First prove the effect is recoverable under your "
            "assumptions; only then worry about computing it precisely. Skipping "
            "the first step is how confident, wrong answers are made."},

        {"type": "section", "kicker": "Part 7", "title": "A real case + workflow",
         "subtitle": "From the Perry Preschool experiment to a clean estimand for "
            "a clinical trial."},
        {"type": "steps", "kicker": "Case study · Perry Preschool",
         "title": "A randomized early-childhood experiment", "steps": [
            {"title": "The question", "body": "Effect of a preschool program on "
             "later-life outcomes for disadvantaged children."},
            {"title": "The design", "body": "Children randomized to program vs. "
             "control — exchangeability by construction."},
            {"title": "The estimand", "body": "ATE on outcomes like graduation, "
             "earnings, arrests — stated up front."},
            {"title": "The payoff", "body": "Credible long-run causal effects "
             "BECAUSE randomization broke confounding with family background."},
         ]},
        {"type": "steps", "kicker": "Application · a clinical trial",
         "title": "Define the estimand before you enroll a patient", "steps": [
            {"title": "Population", "body": "— who is eligible; that fixes whether "
             "ATE or ATT is the target."},
            {"title": "Treatment", "body": "— a concrete, well-defined protocol "
             "(consistency)."},
            {"title": "Outcome & contrast", "body": "— Y(1) − Y(0) on a "
             "pre-specified endpoint."},
            {"title": "Assumptions", "body": "— randomization for exchangeability; "
             "check positivity and SUTVA."},
         ],
         "note": "The estimand goes in the protocol BEFORE data — the discipline "
            "this whole week is teaching."},
        {"type": "content", "kicker": "The recurring workflow",
         "title": "Every lab and the capstone follow these five steps", "bullets": [
            "Question — state the estimand and the population precisely.",
            "Assume — list SUTVA, consistency, exchangeability, positivity.",
            "Identify — can the effect be written from observable data?",
            "Estimate — compute it; report uncertainty.",
            ("Validate — sensitivity and robustness checks feed back to "
             "assumptions.", 1),
         ],
         "note": {"title": "Same loop all term",
            "body": "Question → Assume → Identify → Estimate → Validate. This week "
            "lives in the first three."}},
        {"type": "statement",
         "quote": "State the estimand. Defend the assumptions. Then, and only "
            "then, estimate.",
         "attribution": "This week: build the science table in code, watch "
            "randomization recover the ATE, and watch a confounded comparison "
            "miss it. See you in the workshop."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · The science table — two outcomes per unit\n\n"
            "Causal inference would be easy if nature showed us, for every unit, "
            "**both** the treated outcome `Y(1)` and the untreated outcome `Y(0)`. "
            "That full table is the *science table*. Because we build it here in "
            "simulation, we **know the true effect for every unit** — and so the "
            "true ATE exactly. Later we'll hide one column and see how well "
            "different study designs recover that number."},
        {"code": "# Build a finite-population science table with a KNOWN true ATE.\n"
            "N = 20_000\n"
            "X  = RNG.normal(size=N)                      # baseline covariate (e.g. risk)\n"
            "Y0 = 1.0 + 0.8 * X + RNG.normal(size=N)      # potential outcome if UNtreated\n"
            "tau = 2.0 + 0.5 * X                          # heterogeneous TRUE effect\n"
            "Y1 = Y0 + tau                                # potential outcome if treated\n\n"
            "science = pd.DataFrame({'X': X, 'Y0': Y0, 'Y1': Y1, 'effect': Y1 - Y0})\n"
            "TRUE_ATE = science['effect'].mean()\n"
            "print(science.head())\n"
            "print(f'\\nTRUE ATE = E[Y(1) - Y(0)] = {TRUE_ATE:.3f}')"},
        {"md": "Every row has an individual effect `Y1 - Y0`, and the effect "
            "varies with `X` (it is *heterogeneous*). The population average of "
            "that column is the **true ATE** — about `2.0`, since "
            "`tau = 2 + 0.5*X` and `X` is mean-zero. Hold onto `TRUE_ATE`: it is "
            "the answer key for the rest of the notebook."},
        {"md": "## 2 · The fundamental problem — you only ever see one column\n\n"
            "Assign a treatment `A` and reveal only the matching potential outcome "
            "through the **switching equation** `Y = A·Y(1) + (1−A)·Y(0)`. The "
            "other column becomes the unobserved counterfactual. This is the data "
            "a real study would hand you."},
        {"code": "A = RNG.binomial(1, 0.5, N)                  # complete randomization, 50/50\n"
            "Y = np.where(A == 1, Y1, Y0)                 # switching equation\n\n"
            "obs = pd.DataFrame({'X': X, 'A': A, 'Y': Y})\n"
            "# The counterfactual column is gone: we don't get Y0 for treated units,\n"
            "# nor Y1 for untreated units.\n"
            "print(obs.head())\n"
            "n_missing = N   # exactly one potential outcome is hidden per unit\n"
            "print(f'\\nHidden counterfactuals: {n_missing} of {2*N} cells '\n"
            "      f'({100*n_missing/(2*N):.0f}% of the science table).')"},
        {"md": "Half the science table is gone — one cell per row. No estimator "
            "can ever look at an individual's missing cell. The best we can do is "
            "recover a **population average**, and only when the units we see "
            "treated are a fair stand-in for the units we see untreated."},
        {"md": "## 3 · Randomization recovers the ATE (in expectation)\n\n"
            "Because `A` was a fair coin flip, it is independent of "
            "`{Y(0), Y(1)}`: the treated and untreated groups are *exchangeable*. "
            "So the **simple difference in observed group means** should estimate "
            "the ATE. One sample carries noise; let's check a single draw, then "
            "average over many random assignments to see it is right *in "
            "expectation*."},
        {"code": "def diff_in_means(A, Y):\n"
            "    return Y[A == 1].mean() - Y[A == 0].mean()\n\n"
            "single = diff_in_means(A, Y)\n"
            "print(f'one randomized sample: {single:.3f}   (true {TRUE_ATE:.3f})')\n\n"
            "# Average the estimator over many independent random assignments.\n"
            "ests = []\n"
            "for _ in range(2000):\n"
            "    a = RNG.binomial(1, 0.5, N)\n"
            "    y = np.where(a == 1, Y1, Y0)\n"
            "    ests.append(diff_in_means(a, y))\n"
            "ests = np.array(ests)\n"
            "print(f'mean over 2000 assignments: {ests.mean():.3f}   (true {TRUE_ATE:.3f})')\n"
            "assert abs(ests.mean() - TRUE_ATE) < 0.05, 'randomization should recover the ATE'"},
        {"code": "# The sampling distribution of the randomized estimator is centred on the truth.\n"
            "fig, ax = plt.subplots()\n"
            "ax.hist(ests, bins=40, color='#4C72B0', alpha=0.85)\n"
            "ax.axvline(TRUE_ATE, color='crimson', lw=2, label=f'true ATE = {TRUE_ATE:.2f}')\n"
            "ax.axvline(ests.mean(), color='black', lw=2, ls='--',\n"
            "           label=f'mean estimate = {ests.mean():.2f}')\n"
            "ax.set_xlabel('difference-in-means estimate'); ax.set_ylabel('count')\n"
            "ax.set_title('Randomization: unbiased for the ATE'); ax.legend()\n"
            "None  # figure created; no blocking show()"},
        {"md": "The histogram of estimates is centred on the red truth line: "
            "individual experiments scatter, but the procedure is **unbiased**. "
            "That is exactly what 'recovers the ATE in expectation' means."},
        {"md": "## 4 · A confounded observational comparison is biased\n\n"
            "Now keep the **same science table** but let treatment depend on the "
            "covariate `X` — higher-`X` units are more likely to be treated. "
            "Because `X` also drives the potential outcomes, treatment is now "
            "correlated with `{Y(0), Y(1)}` and exchangeability fails. The naive "
            "difference in means mixes the real effect with a baseline gap."},
        {"code": "p = 1 / (1 + np.exp(-1.5 * X))               # propensity rises with X\n"
            "Ac = RNG.binomial(1, p)                      # confounded assignment\n"
            "Yc = np.where(Ac == 1, Y1, Y0)\n\n"
            "naive = diff_in_means(Ac, Yc)\n"
            "print(f'confounded naive diff = {naive:.3f}   (true {TRUE_ATE:.3f})')\n\n"
            "# The bias is exactly the baseline imbalance in Y(0) between the arms:\n"
            "baseline_gap = Y0[Ac == 1].mean() - Y0[Ac == 0].mean()\n"
            "print(f'baseline Y(0) gap between arms = {baseline_gap:.3f}  (this IS the bias)')\n"
            "assert naive - TRUE_ATE > 0.2, 'confounding should bias the naive estimate upward'"},
        {"md": "The naive number overstates the effect: treated units had higher "
            "`X`, hence higher `Y(0)` to begin with, and that head start is "
            "wrongly credited to the treatment. The printed `baseline Y(0) gap` is "
            "precisely the selection bias term `E[Y(0)|A=1] − E[Y(0)|A=0]`. "
            "Adjusting for `X` (later weeks) is how we'd close it — here we just "
            "diagnose it."},
        {"md": "### 🔧 Exercise 4.1 — recover the ATT, then compare to the ATE\n\n"
            "The **ATT** is the effect among the *treated* units only: "
            "`E[Y(1) − Y(0) | A = 1]`. Because we built the science table, we can "
            "compute it *exactly* — we know both columns. Using the **confounded** "
            "assignment `Ac`, fill in the `# TODO`s to compute the true ATT and "
            "compare it to the true ATE. They differ here because effects are "
            "heterogeneous and the treated have higher `X`.\n\n"
            "The skeleton still runs (it uses `...` placeholders); replace them."},
        {"code": "# TODO: compute the TRUE ATT among the confounded-treated units (Ac == 1),\n"
            "# using the full science table (we know both Y1 and Y0 here).\n"
            "treated_mask = (Ac == 1)\n"
            "true_ATT = ...      # TODO: mean of (Y1 - Y0) over treated_mask\n"
            "# print(f'true ATT = {true_ATT:.3f}   true ATE = {TRUE_ATE:.3f}')"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "treated_mask = (Ac == 1)\n"
            "true_ATT = (Y1 - Y0)[treated_mask].mean()\n"
            "print(f'true ATT = {true_ATT:.3f}   true ATE = {TRUE_ATE:.3f}')\n"
            "# Treated units have higher X, and effect tau = 2 + 0.5*X rises with X,\n"
            "# so the ATT exceeds the ATE here.\n"
            "assert true_ATT > TRUE_ATE, 'with positive selection on effect, ATT > ATE'\n"
            "print('ATT > ATE: the treated are exactly the units with larger effects.')"},
        {"md": "## 5 · Positivity — when there is no one to compare to\n\n"
            "Exchangeability says we *could* adjust for `X`; **positivity** says "
            "there is actually data in every stratum to adjust *with*. Here we "
            "simulate a hard violation: above a cutoff in `X`, **everyone** is "
            "treated, so no untreated comparison unit exists there. Estimation in "
            "that region is pure extrapolation."},
        {"code": "# Deterministic assignment above a cutoff: a positivity violation.\n"
            "cutoff = 0.5\n"
            "Av = np.where(X > cutoff, 1, RNG.binomial(1, 0.5, N))   # forced treated when X>cutoff\n"
            "Yv = np.where(Av == 1, Y1, Y0)\n\n"
            "hi = X > cutoff\n"
            "p_treated_hi = Av[hi].mean()\n"
            "n_untreated_hi = int((Av[hi] == 0).sum())\n"
            "print(f'For X > {cutoff}:  P(treated) = {p_treated_hi:.3f},  '\n"
            "      f'untreated units available = {n_untreated_hi}')\n"
            "assert n_untreated_hi == 0, 'positivity is violated: no untreated units above the cutoff'\n"
            "print('No untreated units exist above the cutoff -> the effect there is NOT identified.')"},
        {"md": "Within `X > 0.5` there is no untreated unit, so `E[Y(0) | X>0.5]` "
            "has nothing to estimate from. A model with an `X` term will still "
            "print an effect for that region — but it is invented by the "
            "functional form, not supported by data. The honest move is to "
            "**restrict the estimand to the overlap region**, which we do next."},
        {"md": "### 🔧 Exercise 5.1 — restrict to the overlap region\n\n"
            "Estimate the ATE **only where both treatments occur** — the stratum "
            "`X ≤ cutoff`, where assignment was a 50/50 coin flip and so is "
            "(locally) randomized. Fill in the `# TODO`s and check the restricted "
            "estimate recovers the *true ATE within that region*."},
        {"code": "# TODO: restrict to the overlap region X <= cutoff and estimate there.\n"
            "ok = X <= cutoff\n"
            "ate_overlap_true = (Y1 - Y0)[ok].mean()        # true ATE in the overlap region\n"
            "est_overlap = ...   # TODO: diff_in_means on the units with `ok`, using Av and Yv\n"
            "# print(f'overlap est = {est_overlap:.3f}   true (region) = {ate_overlap_true:.3f}')"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "ok = X <= cutoff\n"
            "ate_overlap_true = (Y1 - Y0)[ok].mean()\n"
            "est_overlap = diff_in_means(Av[ok], Yv[ok])\n"
            "print(f'overlap est = {est_overlap:.3f}   true (region) = {ate_overlap_true:.3f}')\n"
            "assert abs(est_overlap - ate_overlap_true) < 0.1, 'should recover the region ATE'\n"
            "print('Honest non-identification: we report the effect only where data support it.')"},
        {"md": "## 6 · Wrap-up & self-check\n\n"
            "- A causal effect is a contrast of **potential outcomes** "
            "`Y(1) − Y(0)`; we never see both for one unit (the **fundamental "
            "problem**).\n"
            "- **State the estimand first** — ATE, ATT, or CATE. We saw ATT > ATE "
            "when the treated are selected on larger effects.\n"
            "- **Randomization** makes `A ⟂ {Y(0), Y(1)}`, so the "
            "difference-in-means is unbiased — confirmed by averaging over many "
            "assignments.\n"
            "- A **confounded** comparison is biased by exactly the baseline "
            "`Y(0)` gap between arms.\n"
            "- **Positivity** can fail outright; the honest fix is to restrict the "
            "estimand to the overlap region.\n\n"
            "**You're ready for Week 3** if you can write ATE/ATT/CATE from "
            "memory, name the four assumptions, and say why a coin flip buys "
            "exchangeability. Next week: designing and running randomized "
            "experiments and A/B tests well."},
    ],
}
