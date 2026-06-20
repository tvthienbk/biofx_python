# -*- coding: utf-8 -*-
"""Week 1 — The Causal Question. Gold-standard content module."""

WEEK = {
    "number": 1,
    "slug": "the_causal_question",
    "title": "The Causal Question",
    "block": "Block I — Foundations",
    "subtitle": "Why prediction is not intervention, why correlation is not "
                "causation, and the vocabulary that makes the difference precise.",
    "deliverable": "Problem Set 1 — spot the confounder/collider; "
                   "Lab 0 — environment setup + GitHub + your first causal estimate.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab (2–3h).",
    "one_sentence": "Prediction tells you what usually goes with what; causal "
        "inference tells you what would happen if you intervened — and the gap "
        "between them is created by confounding, reverse causation, and selection.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "State, in your own words, why P(Y | do(X)) can differ from P(Y | X).",
        "Look at a three-variable story and label the third variable a "
        "confounder, a collider, or a mediator.",
        "Decide whether to adjust for that variable — and justify the decision "
        "from the causal structure, not the data.",
        "Run a confounded simulation and show that a naive estimate is biased "
        "while an adjusted one recovers the truth.",
        "Have a working R or Python environment, a course repository, and your "
        "first commit pushed to GitHub.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Hernán & Robins, Causal Inference: What If — Chapter 1.",
         "look_for": "the definition of a causal effect for an individual vs. a "
                     "population, and why the individual effect is unobservable."},
        {"text": "Pearl, Glymour & Jewell, Primer — Chapter 1.",
         "look_for": "the three rungs of the ladder of causation, and one "
                     "question that lives on each rung."},
    ],
    "optional_readings": [
        {"text": "Huntington-Klein, The Effect — Chapters 1–2.",
         "note": "A gentle, example-driven on-ramp if the notation feels fast."},
        {"text": "Cunningham, The Mixtape — Introduction.",
         "note": "The applied, code-first perspective you'll lean on later."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "Prediction is not intervention",
         "body": "Seeing that umbrellas and rain go together lets you predict "
            "rain from umbrellas. It does not mean that handing out umbrellas "
            "causes rain. P(rain | umbrella seen) is large; P(rain | do(umbrella)) "
            "is unchanged. Causal questions are about the second quantity — the "
            "distribution of an outcome when we set a variable, not when we "
            "merely observe it."},
        {"heading": "Three engines of spurious association",
         "bullets": [
            [("Confounding:  ", {"bold": True}),
             ("a common cause C drives both X and Y, so they move together even "
              "with no arrow from X to Y. Heat raises both ice-cream sales and "
              "drownings.", {})],
            [("Reverse causation:  ", {"bold": True}),
             ("Y actually causes X, so the association is real but points the "
              "other way.", {})],
            [("Selection:  ", {"bold": True}),
             ("we are looking at a filtered sample, and the filter itself "
              "manufactures the association (a collider opened by conditioning).",
              {})],
         ]},
        {"heading": "The three structures you must recognize",
         "body": "Confounder vs. mediator vs. collider — the distinction that "
                 "organizes the entire term.",
         "bullets": [
            [("Confounder  C → X and C → Y. ", {"bold": True}),
             ("A common cause. Adjusting for it removes bias. (Adjust.)", {})],
            [("Mediator  X → M → Y. ", {"bold": True}),
             ("M lies on the causal path. Adjusting for it blocks part of the "
              "effect you want. (Don't adjust — if you want the total effect.)", {})],
            [("Collider  X → K ← Y. ", {"bold": True}),
             ("A common effect. It is already blocked; adjusting for it OPENS a "
              "spurious path. (Don't adjust.)", {})],
         ],
         "callout": {"title": "The single most common mistake in applied work",
            "color": "RED",
            "lines": ["Treating every covariate as a confounder and 'controlling "
                      "for everything.' Mediators and colliders punish that habit.",
                      "The graph — not the regression output — tells you which is "
                      "which."]}},
    ],
    "problem_set": {
        "label": "Problem Set 1",
        "title": "Spot the confounder/collider",
        "intro": "For each scenario: (a) draw the DAG, (b) label the third "
            "variable as confounder, mediator, or collider, (c) say whether you "
            "would adjust for it to estimate the effect of X on Y, and (d) give "
            "one sentence of justification. Try all five before you look.",
        "problems": [
            {"title": "Coffee, smoking, and pancreatic cancer",
             "prompt": "A study finds that coffee drinkers have higher rates of "
                "pancreatic cancer. Smokers tend to drink more coffee, and smoking "
                "is a known cause of pancreatic cancer. You want the effect of "
                "coffee (X) on cancer (Y). What role does smoking play, and do you "
                "adjust for it?",
             "solution_title": "Smoking is a confounder — adjust.",
             "solution": [
                "DAG: Smoking → Coffee, Smoking → Cancer, with the coffee→cancer "
                "arrow in question.",
                "Smoking is a common cause of both coffee drinking and cancer, so "
                "it opens a back-door path Coffee ← Smoking → Cancer that "
                "masquerades as a coffee effect.",
                "Adjusting for smoking (stratify, match, or regress) closes that "
                "path and isolates any genuine coffee effect. The textbook "
                "confounder."]},
            {"title": "Two diseases in a hospital ward",
             "prompt": "In the general population, disease A and disease B are "
                "unrelated. But among hospitalized patients, having A is associated "
                "with NOT having B. Admission is more likely if a patient has "
                "either disease. Taking X = disease A, Y = disease B, what role "
                "does hospital admission play, and should your analysis condition "
                "on 'being hospitalized'?",
             "solution_title": "Admission is a collider — do not condition on it.",
             "solution": [
                "DAG: Disease A → Admission ← Disease B (admission is a common "
                "EFFECT of both).",
                "In the full population the path A → Admission ← B is blocked, so "
                "A and B are independent. Restricting to hospitalized patients "
                "conditions on the collider and opens the path, manufacturing a "
                "negative association (Berkson's bias).",
                "The fix is not to adjust but to avoid the conditioning: study a "
                "population sample, or model the selection explicitly."]},
            {"title": "A blood-pressure drug and stroke",
             "prompt": "A drug (X) reduces stroke risk (Y). Its mechanism is to "
                "lower blood pressure (M), and lower blood pressure reduces "
                "strokes. You want the TOTAL effect of the drug on stroke. What "
                "role does blood pressure play, and do you adjust for it?",
             "solution_title": "Blood pressure is a mediator — do not adjust "
                "(for the total effect).",
             "solution": [
                "DAG: Drug → Blood pressure → Stroke (plus possibly a direct "
                "Drug → Stroke arrow).",
                "Blood pressure lies ON the causal path. Adjusting for it blocks "
                "the drug's main route to reducing stroke, leaving only any direct "
                "effect — you would badly understate the drug's value.",
                "Keep it unadjusted for the total effect. Condition on it only if "
                "you specifically want the direct effect (mediation, Week 14)."]},
            {"title": "The tempting pre-treatment variable (M-bias)",
             "prompt": "You study X → Y. There is a measured variable Z, recorded "
                "before treatment. Unknown to you, Z is caused by two hidden "
                "variables: U₁ (which also causes X) and U₂ (which also causes Y). "
                "There is no other connection. A colleague says 'control for it to "
                "be safe.' Is Z a confounder or a collider, and should you adjust?",
             "solution_title": "Z is a collider (M-bias) — do not adjust, despite "
                "being pre-treatment.",
             "solution": [
                "DAG: U₁ → Z ← U₂, with U₁ → X and U₂ → Y. The shape is the letter M.",
                "Z is a common effect of U₁ and U₂, i.e. a collider. Left alone, "
                "the path X ← U₁ → Z ← U₂ → Y is blocked at Z and carries no bias.",
                "Adjusting for Z opens that path and INTRODUCES confounding bias "
                "that wasn't there. 'Pre-treatment' does not mean 'safe to control "
                "for.' Structure, not timing, decides."]},
            {"title": "Job training, prior earnings, and occupation",
             "prompt": "You estimate the effect of a job-training program (X) on "
                "annual earnings (Y). You have two covariates: prior-year earnings "
                "(before the program) and occupation held after the program (a job "
                "the training helped people get). For EACH covariate, give its role "
                "and whether to adjust.",
             "solution_title": "Prior earnings: confounder (adjust). "
                "Post-program occupation: mediator/bad control (don't adjust).",
             "solution": [
                "Prior earnings → enrolling in training and Prior earnings → later "
                "earnings: a common cause, hence a confounder. Adjust for it.",
                "Occupation after training is caused by the training and affects "
                "earnings: Training → Occupation → Earnings. A mediator and a "
                "post-treatment variable — a classic 'bad control.'",
                "Lesson: covariates are not interchangeable. One scenario can "
                "contain both a must-adjust confounder and a must-not-adjust "
                "mediator."]},
        ],
    },
    "lab": {
        "label": "Lab 0",
        "title": "Environment, repository, and your first causal estimate",
        "goal": "a working toolchain, a course repository under version control, "
            "and a tiny analysis that demonstrates confounding in code. Pick R or "
            "Python — both are supported all term; you may switch later.",
        "steps": [
            {"heading": "Step 1 · Install the toolchain",
             "body": "Run one of the following. If a package fails to build, note "
                "the error in your lab log — fixing environments is a real skill.",
             "code_r": 'install.packages(c("tidyverse", "dagitty", "ggdag",\n'
                       '                   "MatchIt", "WeightIt", "cobalt"))',
             "code_python": "python -m venv .venv && source .venv/bin/activate\n"
                "pip install numpy pandas statsmodels dowhy econml scikit-learn"},
            {"heading": "Step 2 · Create and clone the repository",
             "code_python": "# Create an empty repo 'causal-inference-labs' on "
                "GitHub, then:\n"
                "git clone https://github.com/<your-username>/causal-inference-labs.git\n"
                "cd causal-inference-labs\nmkdir week01 && cd week01"},
            {"heading": "Step 3 · Hello, confounding — your first estimate",
             "body": "Simulate data where a confounder C raises both treatment X "
                "and outcome Y. The TRUE causal effect of X on Y is exactly 2. Show "
                "that the naive estimate is inflated and that adjusting for C "
                "recovers the truth.",
             "code_r": "set.seed(1)\nn  <- 5000\n"
                "C  <- rnorm(n)                      # confounder\n"
                "X  <- 0.8 * C + rnorm(n)            # C pushes treatment\n"
                "Y  <- 2 * X + 1.5 * C + rnorm(n)    # TRUE effect of X is 2\n"
                'naive    <- coef(lm(Y ~ X))["X"]\n'
                'adjusted <- coef(lm(Y ~ X + C))["X"]\n'
                'cat(sprintf("naive=%.2f  adjusted=%.2f\\n", naive, adjusted))',
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(1)\nn = 5000\n"
                "C = rng.normal(size=n)                 # confounder\n"
                "X = 0.8 * C + rng.normal(size=n)       # C pushes treatment\n"
                "Y = 2 * X + 1.5 * C + rng.normal(size=n)   # TRUE effect is 2\n"
                "naive    = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
                "adjusted = sm.OLS(Y, sm.add_constant(np.c_[X, C])).fit().params[1]\n"
                'print(f"naive={naive:.2f}  adjusted={adjusted:.2f}")'},
            {"heading": "Step 4 · Commit and push",
             "code_python": "git add week01/\n"
                'git commit -m "Week 1: hello confounding (naive vs adjusted)"\n'
                "git push origin main"},
        ],
        "expected": "The naive coefficient lands well above 2 (roughly 2.7–2.8) "
            "because part of C's effect is wrongly credited to X. The adjusted "
            "coefficient sits at about 2.0. Same data, two stories — and only the "
            "causal structure tells you which to believe. That is the entire "
            "course in eight lines.",
        "submit": [
            "Push your code and a one-paragraph README in week01/ reporting the "
            "two numbers and one sentence on why they differ.",
            "Paste the GitHub link to your week01 folder in the course LMS.",
            "Bring your active-reading sentences (from the guided reading) to lab.",
        ],
    },
    "self_check": [
        "Explain the umbrella/rain example without notes.",
        "Glance at a three-node story and call confounder / mediator / collider "
        "correctly.",
        "Say why 'control for everything' is wrong, with a collider example.",
        "Reproduce the naive-vs-adjusted gap from memory.",
    ],
    "next_week": {
        "heading": "Coming up: Week 2 — Potential outcomes",
        "teaser": "We make the intuition formal. You'll meet Y(1) and Y(0), the "
            "fundamental problem of causal inference, and the precise assumptions "
            "— SUTVA, consistency, exchangeability, positivity — that turn an "
            "observed difference into a causal one. Skim Hernán & Robins Chapter 2 "
            "to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 1", "items": [
            {"t": "Why causal?", "d": "The questions worth asking are about "
             "intervention, not just patterns."},
            {"t": "Correlation ≠ causation", "d": "Three engines of spurious "
             "association."},
            {"t": "Confounding", "d": "The single most important obstacle — and "
             "Simpson's paradox."},
            {"t": "Ladder of causation", "d": "Seeing, doing, imagining — three "
             "distinct rungs."},
            {"t": "Two frameworks", "d": "Potential outcomes and causal graphs, "
             "previewed."},
            {"t": "A real case + workflow", "d": "LaLonde job-training and the "
             "5-step causal workflow."},
        ]},
        {"type": "content", "kicker": "What this course is",
         "title": "A practical toolkit for answering causal questions with data",
         "bullets": [
            "Goal: take a real dataset and a causal question, choose a credible "
            "identification strategy, estimate an effect, and defend it.",
            "Every method is theory + assumptions + code + a reproducible real "
            "case study.",
            ("Causal inference is a workflow, not a single regression.", 1),
            ("question → assumptions → identification → estimation → validation", 1),
            "Domains span tech experiments, economics & policy, epidemiology and "
            "biomedicine — the logic transfers across all of them.",
         ],
         "note": {"title": "You will be able to",
            "body": "Design, run, and critique a credible causal study "
            "end-to-end — and know when the data simply cannot answer the question."}},
        {"type": "compare", "kicker": "Who this is for",
         "title": "Prerequisites & what you bring", "columns": [
            {"head": "Assumed", "points": [
                "Probability & statistics: expectation, variance, conditioning.",
                "Linear & logistic regression (interpretation).",
                "Programming in R or Python; comfort with a data frame."]},
            {"head": "We will build", "points": [
                "The potential-outcomes and DAG languages from scratch.",
                "Each estimator's assumptions, diagnostics, failure modes.",
                "A reproducible analysis habit (version control + notebooks)."]},
            {"head": "Not required", "points": [
                "Measure theory or advanced asymptotics.",
                "Prior econometrics or epidemiology.",
                "A specific domain background."]},
         ]},
        {"type": "content", "kicker": "The arc of the term",
         "title": "Fifteen weeks, four blocks", "bullets": [
            ("FOUNDATIONS — causal question · potential outcomes · randomized "
             "experiments · DAGs", 0),
            ("ADJUSTMENT — regression & control · matching & propensity · "
             "weighting & doubly robust", 0),
            ("QUASI-EXPERIMENTS — IV & Mendelian rand. · regression discontinuity "
             "· difference-in-differences · synthetic control", 0),
            ("MODERN & APPLIED — double/debiased ML · heterogeneous effects · "
             "advanced topics · capstone", 0),
            ("The midterm (Week 8) covers Weeks 1–7; the capstone is the final "
             "deliverable.", 1),
         ],
         "note": {"title": "Assessment",
            "body": "Problem sets 20% · Labs 25% · Midterm 20% · Capstone 30% · "
            "Participation 5%."}},

        {"type": "section", "kicker": "Part 1", "title": "Why causation?",
         "subtitle": "Almost every decision-relevant question is secretly a "
            "causal one — even when we phrase it as a prediction."},
        {"type": "content", "kicker": "Motivation",
         "title": "The questions that matter are causal", "bullets": [
            "Does this drug reduce mortality — or do healthier patients take it?",
            "Will raising the minimum wage cost jobs?",
            "Did the new checkout flow increase purchases, or did we ship it in a "
            "good week?",
            "Would this patient have survived had we treated earlier? "
            "(a counterfactual)",
            ("Each asks what would happen under an action — not merely what tends "
             "to co-occur.", 1),
         ],
         "note": {"title": "Common shape",
            "body": "'If we set treatment to value t, what happens to outcome Y?' "
            "— the do-operator we meet later today."}},
        {"type": "compare", "kicker": "The core distinction",
         "title": "Prediction is not intervention", "columns": [
            {"head": "PREDICTION — Seeing", "sub": "P(Y | X)", "points": [
                "Uses observed associations.",
                "'Patients on this drug live longer.'",
                "Great for forecasting & triage.",
                "Silent on what an action would do."]},
            {"head": "INTERVENTION — Doing", "sub": "P(Y | do(X))", "points": [
                "Asks what a deliberate change causes.",
                "'If we give the drug, do they live longer?'",
                "Needed for any decision or policy.",
                "Requires causal assumptions to identify."]},
         ]},
        {"type": "statement",
         "quote": "do(X) — the action we evaluate — is not the same as X | seen, "
            "the group that happened to have X.",
         "attribution": "People who take an action differ from everyone else in "
            "ways that also drive the outcome. Closing that gap — credibly — is "
            "the whole game."},

        {"type": "section", "kicker": "Part 2", "title": "Correlation ≠ causation",
         "subtitle": "A correlation is a fact about a joint distribution. A causal "
            "claim is a fact about interventions. They are different objects."},
        {"type": "content", "kicker": "The slogan, sharpened",
         "title": "True — but not enough", "bullets": [
            "The slogan tells you what NOT to conclude. It gives no recipe for "
            "what you CAN conclude.",
            "Causal inference replaces it with a procedure: state assumptions, "
            "check identifiability, estimate, stress-test.",
            "Crucially, correlation PLUS the right assumptions CAN justify "
            "causation — the optimistic core of the field.",
            "So the real question is never 'is it causal?' but 'what would have to "
            "be true for this to be causal, and is it?'",
         ],
         "note": {"title": "Reframe",
            "body": "Don't ask whether data prove causation. Ask which assumptions "
            "license a causal reading — then defend them."}},
        {"type": "compare", "kicker": "Why X and Y move together",
         "title": "Three engines of association without causation", "columns": [
            {"head": "Reverse causation", "points": [
                "Y actually causes X.",
                "Hospitals → death? Sick people go to hospitals."]},
            {"head": "Confounding", "points": [
                "A common cause Z drives both X and Y.",
                "Coffee & cancer, both driven by smoking."]},
            {"head": "Selection / collider", "points": [
                "Conditioning on a common effect creates a fake link.",
                "Talent vs. looks among hired actors."]},
         ]},

        {"type": "section", "kicker": "Part 3", "title": "Confounding",
         "subtitle": "The common-cause problem: the central obstacle to causal "
            "inference from observational data."},
        {"type": "content", "kicker": "Definition",
         "title": "A confounder is a common cause of treatment and outcome",
         "bullets": [
            "Z is a confounder of X → Y if Z causes X and Z (independently) "
            "causes Y.",
            "It induces association between X and Y that is not due to X's effect.",
            "Graphically a 'fork': X ← Z → Y, opening a back-door path.",
            "Measure and adjust for Z → we can (often) recover the causal effect.",
            "If Z is unmeasured, adjustment alone cannot save us — we need a "
            "design or an instrument.",
         ],
         "note": {"title": "Fork",
            "body": "X ← Z → Y. The back-door path we must block to read X → Y "
            "cleanly."}},
        {"type": "content", "kicker": "Classic example",
         "title": "Ice cream sales 'predict' drownings", "bullets": [
            "Hot weather raises both ice-cream sales and swimming (and so "
            "drownings). Neither causes the other.",
            "The spurious path is Ice cream ← Heat → Drownings.",
            ("Fix: condition on temperature.", 0),
            ("Within a narrow heat band, ice cream and drownings are unrelated.", 1),
            ("Adjustment = comparing like with like.", 1),
         ],
         "note": {"title": "The pattern",
            "body": "Every confounding story has this shape: a common cause you "
            "must block."}},
        {"type": "content", "kicker": "Biomedical example",
         "title": "Coffee, smoking, and lung cancer", "bullets": [
            "Early studies found coffee drinkers had higher lung-cancer rates.",
            "But coffee drinkers were also far more likely to smoke.",
            "Smoking is a common cause: it raises coffee consumption and causes "
            "lung cancer.",
            "Adjusting for smoking shrinks the coffee–cancer association toward "
            "null.",
         ],
         "note": {"title": "Unmeasured = danger",
            "body": "If smoking had not been recorded, no amount of clever "
            "statistics on this dataset could fix the bias."}},
        {"type": "compare", "kicker": "A warning we will earn",
         "title": "'Just control for everything' is wrong", "columns": [
            {"head": "Adjust for confounders", "points": [
                "Common causes of X and Y.", "Blocks back-door bias."]},
            {"head": "Never adjust for colliders", "points": [
                "Common effects of X and Y.", "Conditioning opens a fake path."]},
            {"head": "Don't adjust for mediators", "points": [
                "Things on the X → Y path.", "You'd remove the effect itself."]},
         ]},

        {"type": "section", "kicker": "Part 4", "title": "Simpson's paradox",
         "subtitle": "When an effect reverses sign after you split the data — and "
            "the data alone cannot tell you which answer is right."},
        {"type": "content", "kicker": "The paradox",
         "title": "An effect that flips when you condition", "bullets": [
            "A treatment looks better overall, yet worse within every subgroup — "
            "or vice versa.",
            "Not a statistical error; the numbers are all correct.",
            "It arises when the subgroup variable relates to both treatment "
            "assignment and outcome (a confounder).",
            "The resolution is not mathematical — it is causal.",
         ],
         "note": {"title": "Key idea",
            "body": "The same table supports opposite conclusions. Only a causal "
            "model picks the right one."}},
        {"type": "table", "kicker": "Worked example · kidney stones",
         "title": "Success rates: the reversal in numbers",
         "headers": ["Group", "Treatment A (open)", "Treatment B (keyhole)"],
         "rows": [
            ["Small stones", "93%  (81/87)", "87%  (234/270)"],
            ["Large stones", "73%  (192/263)", "69%  (55/80)"],
            ["Both combined", "78%  (273/350)", "83%  (289/350)"],
         ],
         "note": {"title": "Read it twice",
            "body": "A wins in both rows, yet B wins overall. Doctors gave A to "
            "the harder (large-stone) cases — severity confounds the totals."}},
        {"type": "compare", "kicker": "Which answer is correct?",
         "title": "The DAG decides", "columns": [
            {"head": "Severity → treatment", "sub": "(confounder)", "points": [
                "Sev → Tx, Sev → Cure.",
                "Trust the SUBGROUPS (adjust)."]},
            {"head": "Treatment → blood pressure", "sub": "(mediator)", "points": [
                "Tx → BP → Outcome.",
                "Trust the COMBINED (don't adjust)."]},
         ]},
        {"type": "statement", "quote": "No causal claim in, no causal claim out.",
         "attribution": "Data describe a distribution. To get an interventional "
            "answer you must add assumptions about the causal structure — from "
            "design, domain knowledge, or a credible graph. Statistics estimates; "
            "causal assumptions identify."},

        {"type": "section", "kicker": "Part 5", "title": "The ladder of causation",
         "subtitle": "Pearl's three rungs: seeing, doing, imagining. Each rung "
            "needs tools the rung below cannot provide."},
        {"type": "content", "kicker": "Rung 1 · Seeing",
         "title": "Association — P(Y | X)", "bullets": [
            "Pure observation: how does Y vary across values of X we happen to see?",
            "Covers correlation, regression, and essentially all of supervised ML.",
            "Powerful for forecasting when the world keeps behaving as in training.",
            "Cannot answer 'what if we intervene?' — that needs a different "
            "operator.",
         ],
         "note": {"title": "Tools",
            "body": "Correlation, regression, classifiers, deep nets. All live on "
            "rung 1."}},
        {"type": "content", "kicker": "Rung 2 · Doing",
         "title": "Intervention — P(Y | do(X))", "bullets": [
            "The distribution of Y when we SET X by external action, breaking its "
            "usual causes.",
            "do(X = x) erases the arrows into X — we override how X is normally "
            "determined.",
            "Randomized experiments physically realize do(X); that is why they are "
            "the gold standard.",
            "Most of this course = recovering P(Y | do(X)) from observational data "
            "plus assumptions.",
         ],
         "note": {"title": "do-operator",
            "body": "Set X by intervention, not by observation. Different from "
            "conditioning on X."}},
        {"type": "content", "kicker": "Rung 3 · Imagining",
         "title": "Counterfactuals — what would have happened", "bullets": [
            "Reason about a specific unit in a world that did not occur: 'had this "
            "patient not been treated…'.",
            "Requires the most structure — a full causal model, not just an "
            "intervention distribution.",
            "Underlies attribution, blame, fairness, and individual treatment "
            "effects.",
            "The potential-outcomes notation Y(1), Y(0) is built for this — next "
            "week.",
         ],
         "note": {"title": "Hardest rung",
            "body": "Individual counterfactuals are never both observed — the "
            "fundamental problem of causal inference."}},
        {"type": "steps", "kicker": "The ladder principle",
         "title": "You cannot climb with lower-rung tools alone", "steps": [
            {"title": "Rung-1 data", "body": "— P(Y|X) from any observational "
             "dataset."},
            {"title": "+ assumptions", "body": "— a design or a credible causal "
             "graph."},
            {"title": "= Rung-2 answer", "body": "— an identified interventional "
             "effect."},
         ],
         "note": "Lower-rung data + higher-rung assumptions = a higher-rung answer."},

        {"type": "section", "kicker": "Part 6",
         "title": "Two languages of causality",
         "subtitle": "Potential outcomes and causal graphs say the same things in "
            "different dialects. Fluent practitioners use both."},
        {"type": "content", "kicker": "Language A · Neyman–Rubin",
         "title": "Potential outcomes: Y(1) and Y(0)", "bullets": [
            "For each unit, imagine two outcomes: Y(1) if treated, Y(0) if not.",
            "Individual effect Y(1) − Y(0); average effect ATE = E[Y(1) − Y(0)].",
            "We only ever observe one of the two — the fundamental problem of "
            "causal inference.",
            "Identification asks: when does the observable difference equal the "
            "causal one?",
         ],
         "note": {"title": "Missing data",
            "body": "Causal inference = a missing-data problem. The counterfactual "
            "is the missing cell."}},
        {"type": "content", "kicker": "Language B · Pearl",
         "title": "Causal graphs: nodes and arrows", "bullets": [
            "A DAG encodes assumptions you can argue about.",
            "Arrows = direct causes; missing arrows = assumptions of no direct "
            "effect.",
            "Graph rules (d-separation) tell you what to adjust for.",
            "Transparent, testable, and arguable with collaborators.",
         ],
         "note": {"title": "Our stance",
            "body": "Graphs to decide what to adjust for; potential outcomes to "
            "define and estimate the effect."}},
        {"type": "table", "kicker": "Vocabulary you'll use all term",
         "title": "The effects we estimate",
         "headers": ["Estimand", "Name", "Definition / meaning"],
         "rows": [
            ["ATE", "Average Treatment Effect",
             "E[Y(1) − Y(0)] — effect if everyone were treated vs not."],
            ["ATT", "…on the Treated",
             "E[Y(1) − Y(0) | X=1] — effect among the actually treated."],
            ["CATE", "Conditional ATE",
             "E[Y(1) − Y(0) | covariates] — the basis for personalization."],
            ["LATE", "Local ATE",
             "Effect for 'compliers' — what an instrument identifies (Week 8)."],
         ]},
        {"type": "compare", "kicker": "Two separate jobs",
         "title": "Identification ≠ estimation", "columns": [
            {"head": "IDENTIFICATION", "points": [
                "Can the quantity be written as a function of the data, under "
                "stated assumptions?",
                "A logic/assumptions question.",
                "Answered with DAGs or ignorability.",
                "If it fails, more data won't help."]},
            {"head": "ESTIMATION", "points": [
                "Given identification, how well can we compute it from a finite, "
                "noisy sample?",
                "A statistics question.",
                "Bias, variance, confidence intervals.",
                "More data tightens the estimate."]},
         ]},

        {"type": "section", "kicker": "Part 7", "title": "A real case + the workflow",
         "subtitle": "From a famous job-training study to the five-step routine "
            "you will repeat all term."},
        {"type": "steps", "kicker": "Case study · LaLonde (1986)",
         "title": "Does job training raise earnings?", "steps": [
            {"title": "The question", "body": "Effect of a job-training program on "
             "later earnings."},
            {"title": "Naïve comparison", "body": "Trainees vs a general survey "
             "sample → training looks harmful (they started poorer)."},
            {"title": "Experimental benchmark", "body": "A randomized arm gives the "
             "credible answer: a modest positive gain."},
            {"title": "The lesson", "body": "Observational adjustment must "
             "reproduce the experiment — we revisit it with matching, weighting & "
             "DML."},
         ]},
        {"type": "steps", "kicker": "The causal analysis workflow",
         "title": "Every lab and the capstone follow these five steps", "steps": [
            {"title": "Question", "body": "— state the estimand & population."},
            {"title": "Assume", "body": "— draw the DAG; list assumptions."},
            {"title": "Identify", "body": "— can the effect be recovered?"},
            {"title": "Estimate", "body": "— fit; report uncertainty."},
            {"title": "Validate", "body": "— sensitivity & robustness checks."},
         ],
         "note": "Validation feeds back into your assumptions — the loop is "
            "iterative, not linear."},
        {"type": "compare", "kicker": "Your toolkit",
         "title": "Software you'll set up this week", "columns": [
            {"head": "R", "points": [
                "dagitty, ggdag — graphs",
                "MatchIt, WeightIt, cobalt — adjustment",
                "AER, fixest — IV & panel",
                "rdrobust, did, tidysynth",
                "grf, DoubleML — modern ML"]},
            {"head": "Python", "points": [
                "DoWhy — end-to-end workflow",
                "EconML, CausalML — effects",
                "statsmodels, linearmodels",
                "causal-learn — discovery",
                "pandas, scikit-learn"]},
            {"head": "Reproducibility", "points": [
                "Git + GitHub for everything",
                "Quarto / Jupyter notebooks",
                "Set a random seed; log versions",
                "One-command rebuild of results"]},
         ]},
        {"type": "statement",
         "quote": "Question → Assume → Identify → Estimate → Validate.",
         "attribution": "This week: install the toolkit, push your first commit, "
            "and prove confounding to yourself in eight lines of code. See you in "
            "the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · Prediction is not intervention\n\n"
            "We'll build the umbrella/rain intuition in code. Umbrellas are *seen* "
            "before rain, so they **predict** rain — but handing out umbrellas does "
            "nothing to the weather. The point of this notebook is to feel the "
            "difference between **conditioning** (`P(Y|X)`) and **intervening** "
            "(`P(Y|do(X))`) on simulated data where we *know* the truth."},
        {"code": "# A tiny world: clouds cause both umbrellas and rain.\n"
            "n = 100_000\n"
            "clouds = RNG.binomial(1, 0.3, n)            # 30% of days are cloudy\n"
            "umbrella = RNG.binomial(1, 0.05 + 0.8*clouds, n)  # people react to clouds\n"
            "rain = RNG.binomial(1, 0.05 + 0.7*clouds, n)      # clouds cause rain\n"
            "df = pd.DataFrame({'clouds': clouds, 'umbrella': umbrella, 'rain': rain})\n\n"
            "# Seeing: P(rain | umbrella) — umbrellas 'predict' rain\n"
            "p_seen = df.groupby('umbrella')['rain'].mean()\n"
            "print('P(rain | umbrella seen):')\nprint(p_seen)\n"
            "print(f\"\\nNaive 'effect' of umbrellas on rain: \"\n"
            "      f\"{p_seen[1] - p_seen[0]:+.3f}\")"},
        {"md": "Umbrellas look strongly associated with rain. Now **intervene**: "
            "force everyone to carry an umbrella (`do(umbrella=1)`) vs nobody "
            "(`do(umbrella=0)`). Because nothing downstream of clouds touches the "
            "weather, the rain rate is unchanged — the *causal* effect is ~0."},
        {"code": "# do(umbrella): break the arrow clouds -> umbrella by setting it.\n"
            "# Rain only depends on clouds, so intervening on umbrella changes nothing.\n"
            "rain_do1 = (0.05 + 0.7*clouds).mean()   # everyone carries an umbrella\n"
            "rain_do0 = (0.05 + 0.7*clouds).mean()   # no one does\n"
            "print(f'P(rain | do(umbrella=1)) = {rain_do1:.3f}')\n"
            "print(f'P(rain | do(umbrella=0)) = {rain_do0:.3f}')\n"
            "print(f'Causal effect of umbrellas on rain: {rain_do1 - rain_do0:+.3f}')\n"
            "print('\\nSeeing said ~+0.5; doing says 0. That gap is confounding.')"},
        {"md": "## 2 · Hello, confounding (the eight-line course)\n\n"
            "A confounder `C` pushes both treatment `X` and outcome `Y`. The "
            "**true** effect of `X` on `Y` is exactly `2`. A naive regression "
            "credits some of `C`'s effect to `X`; adjusting for `C` recovers the "
            "truth."},
        {"code": "import statsmodels.api as sm\n\n"
            "n = 5000\n"
            "C = RNG.normal(size=n)                       # confounder\n"
            "X = 0.8 * C + RNG.normal(size=n)             # C pushes treatment\n"
            "Y = 2 * X + 1.5 * C + RNG.normal(size=n)     # TRUE effect of X is 2\n\n"
            "naive    = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
            "adjusted = sm.OLS(Y, sm.add_constant(np.c_[X, C])).fit().params[1]\n"
            "print(f'naive    = {naive:.3f}   (biased upward)')\n"
            "print(f'adjusted = {adjusted:.3f}   (~2.0, the truth)')"},
        {"md": "### 🔧 Exercise 2.1 — make the bias worse, then fix it\n\n"
            "Change the confounder's strength so it pushes `X` **and** `Y` harder "
            "(e.g. `X = 1.5*C + noise`, `Y = 2*X + 3*C + noise`). Predict whether "
            "the naive estimate goes up or down *before* you run it. Then confirm "
            "the adjusted estimate still recovers ~2.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: set stronger confounding and re-estimate.\n"
            "C2 = RNG.normal(size=n)\n"
            "X2 = ...        # TODO: make C push X harder\n"
            "Y2 = ...        # TODO: true effect of X2 still 2, but C pushes Y harder\n"
            "# naive2    = ...\n"
            "# adjusted2 = ...\n"
            "# print(naive2, adjusted2)"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "C2 = RNG.normal(size=n)\n"
            "X2 = 1.5 * C2 + RNG.normal(size=n)\n"
            "Y2 = 2 * X2 + 3.0 * C2 + RNG.normal(size=n)\n"
            "naive2    = sm.OLS(Y2, sm.add_constant(X2)).fit().params[1]\n"
            "adjusted2 = sm.OLS(Y2, sm.add_constant(np.c_[X2, C2])).fit().params[1]\n"
            "print(f'naive2    = {naive2:.3f}   (more bias than before)')\n"
            "print(f'adjusted2 = {adjusted2:.3f}   (still ~2.0)')\n"
            "assert abs(adjusted2 - 2) < 0.15, 'adjustment should recover ~2'"},
        {"md": "## 3 · Confounder vs. mediator vs. collider\n\n"
            "Same three-node shapes, three different correct actions. We simulate "
            "each and watch what 'controlling for' the third variable does to the "
            "estimated `X → Y` effect. **In all three, the true direct effect of "
            "`X` on `Y` is 1.**"},
        {"code": "def est(y, *cols):\n"
            "    \"\"\"OLS slope on the first regressor (X), adjusting for the rest.\"\"\"\n"
            "    Xmat = sm.add_constant(np.column_stack(cols))\n"
            "    return sm.OLS(y, Xmat).fit().params[1]\n\n"
            "n = 8000\n\n"
            "# --- CONFOUNDER:  Z -> X, Z -> Y  (adjust!) ---\n"
            "Z = RNG.normal(size=n)\n"
            "Xc = 1.0*Z + RNG.normal(size=n)\n"
            "Yc = 1.0*Xc + 2.0*Z + RNG.normal(size=n)     # true X->Y = 1\n"
            "print('CONFOUNDER  naive=%.2f  adjusted=%.2f  (truth 1.0)' %\n"
            "      (est(Yc, Xc), est(Yc, Xc, Z)))"},
        {"code": "# --- MEDIATOR:  X -> M -> Y  (do NOT adjust for total effect) ---\n"
            "Xm = RNG.normal(size=n)\n"
            "M  = 1.0*Xm + RNG.normal(size=n)\n"
            "Ym = 1.0*M + RNG.normal(size=n)              # total X->Y = 1 (via M)\n"
            "print('MEDIATOR    total=%.2f  over-adjusted=%.2f  (truth 1.0)' %\n"
            "      (est(Ym, Xm), est(Ym, Xm, M)))\n"
            "print('  -> adjusting for M wrongly removes the effect.\\n')\n\n"
            "# --- COLLIDER:  X -> K <- Y  (do NOT adjust) ---\n"
            "Xk = RNG.normal(size=n)\n"
            "Yk = 1.0*Xk + RNG.normal(size=n)             # true X->Y = 1\n"
            "K  = 1.0*Xk + 1.0*Yk + RNG.normal(size=n)    # common effect\n"
            "print('COLLIDER    clean=%.2f  adjusted=%.2f  (truth 1.0)' %\n"
            "      (est(Yk, Xk), est(Yk, Xk, K)))\n"
            "print('  -> adjusting for K opens a spurious path and biases the estimate.')"},
        {"md": "Notice the pattern: **adjusting helped only the confounder.** For "
            "the mediator and collider it *hurt*. This is why 'control for "
            "everything' is wrong — and why we draw the graph first."},
        {"md": "### 🔧 Exercise 3.1 — M-bias\n\n"
            "Build the M-bias structure from Problem Set 1 #4: hidden `U1 → X`, "
            "`U2 → Y`, and a pre-treatment `Z` with `U1 → Z ← U2`. There is **no** "
            "real confounding, so the naive `X → Y` estimate is already unbiased. "
            "Show that adjusting for the innocent-looking pre-treatment `Z` "
            "*introduces* bias."},
        {"code": "# TODO: simulate U1, U2, then X, Y, and collider Z = U1 + U2 + noise.\n"
            "# true effect of X on Y here is 1.0\n"
            "# U1 = ...\n# U2 = ...\n# Xz = 1.0*U1 + RNG.normal(size=n)\n"
            "# Yz = 1.0*Xz + 1.0*U2 + RNG.normal(size=n)\n"
            "# Z  = ...   # collider of U1 and U2\n"
            "# print(est(Yz, Xz), est(Yz, Xz, Z))"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "U1 = RNG.normal(size=n)\nU2 = RNG.normal(size=n)\n"
            "Xz = 1.0*U1 + RNG.normal(size=n)\n"
            "Yz = 1.0*Xz + 1.0*U2 + RNG.normal(size=n)     # true X->Y = 1\n"
            "Z  = 1.0*U1 + 1.0*U2 + RNG.normal(size=n)      # M-bias collider\n"
            "print('M-BIAS  unadjusted=%.2f  adjusted-for-Z=%.2f  (truth 1.0)' %\n"
            "      (est(Yz, Xz), est(Yz, Xz, Z)))\n"
            "print('Pre-treatment did NOT mean safe: adjusting for Z added bias.')"},
        {"md": "## 4 · Simpson's paradox in code (kidney stones)\n\n"
            "We reconstruct the famous table and watch an effect flip when we "
            "aggregate across stone size — the confounder."},
        {"code": "tab = pd.DataFrame({\n"
            "    'size':      ['small','small','large','large'],\n"
            "    'treatment': ['A','B','A','B'],\n"
            "    'success':   [81, 234, 192, 55],\n"
            "    'n':         [87, 270, 263, 80]})\n"
            "tab['rate'] = tab['success'] / tab['n']\n\n"
            "print('Within each stone size (A beats B both times):')\n"
            "print(tab.pivot(index='size', columns='treatment', values='rate'), '\\n')\n\n"
            "combined = tab.groupby('treatment').apply(\n"
            "    lambda g: g['success'].sum() / g['n'].sum(), include_groups=False)\n"
            "print('Combined (B beats A!):')\nprint(combined)"},
        {"md": "Doctors gave Treatment A (open surgery) to the harder large-stone "
            "cases. **Stone size is a confounder of treatment and success**, so the "
            "subgroup numbers — not the combined ones — answer the causal question. "
            "The table alone can't tell you that; the *causal story* does."},
        {"md": "### 🔧 Exercise 4.1 — which number would you report?\n\n"
            "Suppose instead the third variable were a **mediator** "
            "(treatment → blood pressure → cure) rather than a confounder. Which "
            "number — subgroup or combined — should you trust then? Write your "
            "answer in the next cell as a comment, then reveal the solution."},
        {"code": "# Your answer here:\n# ...\n"},
        {"md": "### ✅ Solution 4.1\n\n"
            "If the splitting variable is a **mediator** on the causal path, you "
            "want the **combined** (unadjusted) estimate — conditioning on a "
            "mediator removes part of the very effect you're after. Same table, "
            "opposite advice: only the DAG decides. (This is exactly the contrast "
            "on the 'The DAG decides' lecture slide.)"},
        {"md": "## 5 · Wrap-up & self-check\n\n"
            "- `P(Y|X)` ≠ `P(Y|do(X))` whenever a back-door path is open.\n"
            "- **Confounder → adjust; mediator → don't (for total effect); "
            "collider → don't.**\n"
            "- Adjusting for the wrong variable *creates* bias — you saw it in "
            "code for both the collider and M-bias.\n"
            "- Simpson's paradox is confounding in disguise; the causal model "
            "picks the right number.\n\n"
            "**You're ready for Week 2** if you can reproduce the naive-vs-adjusted "
            "gap from memory and call confounder / mediator / collider on sight. "
            "Next week: potential outcomes `Y(1), Y(0)` and the assumptions that "
            "license a causal claim."},
    ],
}
