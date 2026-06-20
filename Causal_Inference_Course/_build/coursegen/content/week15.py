# -*- coding: utf-8 -*-
"""Week 15 — Capstone, Reproducibility & Communication. Content module."""

WEEK = {
    "number": 15,
    "slug": "capstone_reproducibility",
    "title": "Capstone, Reproducibility & Communication",
    "block": "Block IV — Modern methods & application",
    "subtitle": "Put it together: a defensible, reproducible causal analysis "
                "you can explain to a decision-maker.",
    "deliverable": "Capstone report + presentation (final deliverable).",

    # ------------------------------------------------------------------ packet
    "packet_intro": "This is the capstone week — there is no new estimator to "
                    "learn, only the discipline that makes a real analysis "
                    "trustworthy. Budget ~6–8 hours: reading (1.5h), the "
                    "capstone checklist (2h), and the reproducible-pipeline lab "
                    "(3–4h) that doubles as the skeleton for your final report.",
    "one_sentence": "A causal claim is only as good as the design that earns it, "
        "the assumptions you state out loud, the robustness checks that fail to "
        "overturn it, and the honest sentence you can say to someone who has to "
        "act on it.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Choose a credible identification strategy — RCT, matching, IV, RD, "
        "DiD, synthetic control, or DML — from the question and the data you "
        "actually have, and justify the choice against the alternatives.",
        "Write a crisp estimand and the identification assumptions your "
        "capstone leans on, naming the one assumption most likely to fail.",
        "Draft a pre-analysis plan that closes off the garden of forking paths "
        "before you ever touch the outcome.",
        "Run a robustness / multiverse analysis and a sensitivity check for "
        "unmeasured confounding, and report what would overturn your result.",
        "Build a one-command, seed-fixed, environment-logged pipeline that "
        "rebuilds your entire report from raw data with Quarto and Git.",
        "Communicate an effect and its uncertainty to a non-technical "
        "stakeholder in three honest sentences — neither overclaiming nor "
        "burying the finding.",
    ],
    "reading_intro": "Read with your own capstone in hand: for each item, write "
        "one sentence connecting it to a decision you are making in your project.",
    "readings": [
        {"text": "Gelman & Loken (2014), \"The garden of forking paths\".",
         "look_for": "how researcher degrees of freedom inflate false positives "
                     "even without 'p-hacking' — the analysis you would have run "
                     "had the data come out differently still counts against you."},
        {"text": "Reproducibility guides (Quarto + Git).",
         "look_for": "what a one-command, seed-fixed, environment-logged rebuild "
                     "actually requires — fixed seeds, a pinned environment, a "
                     "single render command, and version control of every input."},
    ],
    "optional_readings": [
        {"text": "Wilson et al., \"Good enough practices in scientific "
                 "computing\".",
         "note": "A pragmatic, non-purist checklist for data management, code, "
                 "and collaboration you can adopt this week without ceremony."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its "
        "own — the capstone is the whole course compressed into one workflow.",
    "concept_sections": [
        {"heading": "Let the question and the data choose the design",
         "body": "There is no universally best method — only the most credible "
            "design given what you can observe and what nature was willing to "
            "randomize for you. Start from the estimand and the assignment "
            "mechanism, not from the method you find most elegant.",
         "bullets": [
            [("A clean randomized assignment? ", {"bold": True}),
             ("Use the experiment (RCT); everything else is a fallback for when "
              "you cannot randomize.", {})],
            [("Rich measured confounders, overlap looks plausible? ", {"bold": True}),
             ("Back-door adjustment — matching, propensity weighting, or DML for "
              "flexible nuisances.", {})],
            [("A credible instrument or a quasi-random nudge? ", {"bold": True}),
             ("IV / Mendelian randomization (identifies a LATE for compliers).", {})],
            [("Treatment switches at a threshold on a running variable? ", {"bold": True}),
             ("Regression discontinuity (a local effect near the cutoff).", {})],
            [("A policy turned on at a date with untreated comparators? ", {"bold": True}),
             ("Difference-in-differences, or synthetic control for a single "
              "treated unit.", {})],
         ],
         "callout": {"title": "The capstone test",
            "color": "BLUE",
            "lines": ["For your project, can you name the SECOND-best design and "
                      "say why you rejected it? If not, you do not yet understand "
                      "why the first is credible.",
                      "Design choices are arguments, not defaults."]}},
        {"heading": "The garden of forking paths",
         "body": "You do not need to consciously p-hack to fool yourself. If your "
            "analysis choices — which covariates, which subgroup, which outcome "
            "coding, which outliers to drop — would have been different had the "
            "data come out differently, then your p-value no longer means what it "
            "claims, even on a single analysis you ran exactly once.",
         "bullets": [
            [("Researcher degrees of freedom: ", {"bold": True}),
             ("every defensible-looking fork is a multiple comparison you never "
              "see, because you only walked one path.", {})],
            [("The fix is procedural, not statistical: ", {"bold": True}),
             ("pre-register the estimand, the model, and the decision rule before "
              "you look at outcomes.", {})],
            [("Exploratory work is fine — ", {"bold": True}),
             ("just label it exploratory and confirm on held-out or future data.", {})],
         ],
         "callout": {"title": "Pre-analysis plan, minimal version",
            "color": "GREEN",
            "lines": ["State the estimand, the population, the adjustment set, "
                      "the estimator, and the one pre-specified primary outcome — "
                      "before unblinding.",
                      "Anything decided after seeing Y is exploratory and must be "
                      "flagged as such."]}},
        {"heading": "Robustness, multiverse, and sensitivity",
         "body": "A result you trust is one that survives the reasonable analyses "
            "you did not run. Instead of defending a single specification, run "
            "many and show the conclusion is stable — and quantify how strong an "
            "unmeasured confounder would have to be to explain it away.",
         "bullets": [
            [("Multiverse analysis: ", {"bold": True}),
             ("loop over the grid of reasonable specifications and plot the "
              "distribution of estimates, not one point.", {})],
            [("Sensitivity analysis: ", {"bold": True}),
             ("ask how strong an unmeasured confounder would need to be to nullify "
              "the effect (e.g. an E-value).", {})],
            [("Negative controls & placebo tests: ", {"bold": True}),
             ("an outcome that should show no effect, or a pre-period that should "
              "be flat — if they 'work', your design leaks.", {})],
         ],
         "callout": {"title": "Honest reporting",
            "color": "RED",
            "lines": ["Report the multiverse even when it is messy. A result that "
                      "only holds in 1 of 32 specifications is a result about your "
                      "luck, not the world.",
                      "Pre-commit to which specifications count as primary."]}},
        {"heading": "Reproducible pipelines and honest communication",
         "body": "If a colleague cannot rebuild your numbers with one command, "
            "you do not have a result — you have an anecdote. And if a "
            "decision-maker cannot understand the effect and its uncertainty, the "
            "result will not change anything. Reproducibility and communication "
            "are not afterthoughts; they are part of the claim.",
         "bullets": [
            [("One-command rebuild: ", {"bold": True}),
             ("raw data → cleaned data → estimates → figures → report, runnable "
              "from a single `quarto render` (or `make`), with a fixed seed.", {})],
            [("Log the environment: ", {"bold": True}),
             ("`sessionInfo()` / `pip freeze` captured into the report so 'works "
              "on my machine' becomes 'works on this machine, with these "
              "versions.'", {})],
            [("Communicate the effect, the uncertainty, and the caveat: ", {"bold": True}),
             ("a point estimate, an interval in the units the stakeholder cares "
              "about, and the assumption that would change the answer.", {})],
         ],
         "callout": {"title": "The ethics of a causal claim",
            "color": "RED",
            "lines": ["A causal claim licenses action — someone may change a "
                      "treatment, a price, or a policy because of you. State your "
                      "uncertainty and your assumptions as loudly as your point "
                      "estimate.",
                      "Overclaiming is not optimism; it is a transfer of your "
                      "risk onto people who trusted the number."]}},
    ],
    "problem_set": {
        "label": "Capstone checklist",
        "title": "Is your analysis defensible?",
        "intro": "Five review problems that span the whole course, framed against "
            "your own capstone. Write a real answer for YOUR project, then compare "
            "it to the model answer — which shows the shape of a strong response, "
            "not the only correct one.",
        "problems": [
            {"title": "Choose the design from the question and the data",
             "prompt": "You want the effect of a workplace wellness program on "
                "healthcare spending. You have: (a) enrollment that was voluntary, "
                "(b) two years of pre-enrollment spending for everyone, (c) a "
                "subset of sites where the program launched on different dates, "
                "and (d) a lottery that rationed slots at over-subscribed sites. "
                "Pick among RCT / matching / IV / RD / DiD / SC / DML and justify "
                "— and name your second choice.",
             "solution_title": "Lead with the lottery (RCT/IV); DiD as the "
                "design-based backup; matching/DML only as a last resort.",
             "solution": [
                "The slot lottery is a randomized encouragement: it gives a clean "
                "experiment on the lottery winners, or an IV (assignment → "
                "enrollment → spending) that identifies a LATE for compliers. This "
                "is the most credible because assignment is genuinely random.",
                "Staggered launch dates support a difference-in-differences / "
                "event-study design with never-yet-treated sites as controls — "
                "your strong second choice when the lottery is too small.",
                "Voluntary enrollment plus rich pre-period spending tempts "
                "matching or DML on the back-door set, but selection into a "
                "wellness program is exactly the kind of motivation that also "
                "drives spending — assume residual confounding and treat these as "
                "a sensitivity benchmark, not the headline."]},
            {"title": "Write the estimand and the identification assumptions",
             "prompt": "State the causal estimand for your capstone in one "
                "sentence, then list the assumptions that turn your observed "
                "comparison into that estimand. Mark the single assumption most "
                "likely to fail and how you would probe it.",
             "solution_title": "A named estimand plus an explicit, falsifiable "
                "assumption list — with the weakest link flagged.",
             "solution": [
                "Estimand example: 'the ATT of enrolling in the program on "
                "12-month healthcare spending, among employees who enrolled.' Name "
                "the contrast (treated vs. untreated), the population, the "
                "outcome, and the horizon.",
                "Assumptions, by design: consistency / SUTVA (no interference, one "
                "version of treatment), positivity / overlap, and the "
                "design-specific identifying assumption — conditional "
                "exchangeability (adjustment), exclusion + relevance (IV), or "
                "parallel trends (DiD).",
                "Most-likely-to-fail: usually no-unmeasured-confounding (or "
                "parallel trends). Probe it with a negative-control outcome, a "
                "pre-trend / placebo test, and a sensitivity analysis that says "
                "how big a hidden confounder would have to be."]},
            {"title": "Design a pre-analysis plan against forking paths",
             "prompt": "Your reviewer worries you will keep tweaking the model "
                "until p < 0.05. Write a pre-analysis plan for your capstone that "
                "removes the researcher degrees of freedom — what do you lock "
                "down, and what do you leave explicitly exploratory?",
             "solution_title": "Pre-register the estimand, the primary model, the "
                "covariate set, and the decision rule; fence off exploration.",
             "solution": [
                "Lock before unblinding: the single primary outcome and its "
                "coding, the adjustment set, the estimator and its tuning, the "
                "subgroup(s) (if any) and the stopping/decision rule — committed "
                "to a timestamped, version-controlled file.",
                "Pre-specify how you handle the forks that usually leak: outlier "
                "rules, missing-data handling, and which specification is primary "
                "vs. secondary (so the multiverse has a designated headline).",
                "Everything decided after seeing the outcome is labeled "
                "exploratory and is reported as hypothesis-generating, ideally "
                "confirmed on held-out or future data."]},
            {"title": "Propose a sensitivity analysis for unmeasured confounding",
             "prompt": "Suppose your headline estimate is an adjusted "
                "association, and a skeptic says 'an unmeasured confounder "
                "explains it.' Design a concrete sensitivity analysis that answers "
                "them quantitatively rather than rhetorically.",
             "solution_title": "Quantify how strong a hidden confounder must be — "
                "E-value / bounding — and compare it to measured confounders.",
             "solution": [
                "Compute an E-value: the minimum strength of association (on the "
                "risk-ratio scale) a confounder would need with BOTH treatment and "
                "outcome to fully explain the effect. A large E-value means the "
                "skeptic needs an implausibly strong hidden cause.",
                "Benchmark it: is that required strength larger than the strongest "
                "confounder you already measured and adjusted for? If a confounder "
                "as strong as your biggest known one could not nullify the result, "
                "the claim is robust.",
                "Complement with design-based checks — a negative-control outcome "
                "and a negative-control exposure — and report the bias-adjusted "
                "estimate, not just the naive one."]},
            {"title": "Communicate the effect to a non-technical stakeholder",
             "prompt": "Your VP of Operations has five minutes and no statistics "
                "background. In exactly three sentences, communicate your capstone "
                "effect and its uncertainty honestly — no jargon, no overclaiming.",
             "solution_title": "Effect in their units, the uncertainty, and the "
                "one caveat — three sentences, no p-values.",
             "solution": [
                "Sentence 1 — the effect in their units: 'On average, the program "
                "lowered spending by about $480 per enrollee over the year.'",
                "Sentence 2 — the uncertainty as a plausible range: 'Our best "
                "estimate could reasonably be anywhere from roughly $200 to $760, "
                "so the direction is clear but the exact size is not pinned down.'",
                "Sentence 3 — the load-bearing caveat: 'This holds if people who "
                "enrolled were comparable to those who didn't after we matched on "
                "health history — if motivated, healthier people self-selected in, "
                "the true savings are smaller.'"]},
        ],
    },
    "lab": {
        "label": "Capstone Lab · A reproducible pipeline",
        "title": "A reproducible pipeline",
        "goal": "a repository whose entire analysis — clean → estimate → check → "
            "report — rebuilds from one command, with a fixed seed and a logged "
            "environment, so your capstone is reproducible by construction. Pick R "
            "or Python; the structure is identical.",
        "steps": [
            {"heading": "Step 1 · Structure the repository",
             "body": "Separate raw inputs (never edited), code, and generated "
                "outputs. The golden rule: every file in results/ is disposable "
                "because one command can regenerate it.",
             "bullets": [
                "data/raw/ — read-only inputs; data/clean/ — generated.",
                "R/ or src/ — numbered scripts: 01_clean, 02_estimate, "
                "03_robustness.",
                "report.qmd — the Quarto report that calls the analysis.",
                "results/ and figures/ — generated, git-ignored or committed "
                "deliberately.",
             ],
             "code_python": "causal-capstone/\n"
                "├── data/\n"
                "│   ├── raw/          # read-only; never edited by hand\n"
                "│   └── clean/        # generated by 01_clean.py\n"
                "├── src/\n"
                "│   ├── 01_clean.py\n"
                "│   ├── 02_estimate.py\n"
                "│   └── 03_robustness.py\n"
                "├── report.qmd        # one-command render of the whole story\n"
                "├── requirements.txt  # pinned environment\n"
                "├── Makefile          # `make all` rebuilds everything\n"
                "└── README.md",
             "code_r": "causal-capstone/\n"
                "├── data/\n"
                "│   ├── raw/          # read-only; never edited by hand\n"
                "│   └── clean/        # generated by 01_clean.R\n"
                "├── R/\n"
                "│   ├── 01_clean.R\n"
                "│   ├── 02_estimate.R\n"
                "│   └── 03_robustness.R\n"
                "├── report.qmd        # one-command render of the whole story\n"
                "├── renv.lock         # pinned environment (renv)\n"
                "├── Makefile          # `make all` rebuilds everything\n"
                "└── README.md"},
            {"heading": "Step 2 · Fix seeds and log the environment",
             "body": "Reproducibility = same input, same code, same seed, same "
                "environment → same output. Set the seed once near the top of each "
                "entry point, and capture versions into the report so the log "
                "travels with the result.",
             "code_python": "# top of every script / notebook\n"
                "import numpy as np\n"
                "RNG = np.random.default_rng(7)   # one seed; pass RNG around\n\n"
                "# log the environment INTO the report (capture this output):\n"
                "#   python -m pip freeze > requirements.lock.txt\n"
                "import sys, numpy, pandas, sklearn, statsmodels\n"
                "print('python', sys.version.split()[0])\n"
                "for m in (numpy, pandas, sklearn, statsmodels):\n"
                "    print(m.__name__, m.__version__)",
             "code_r": "# top of every script / report\n"
                "set.seed(7)            # fixes base R + most samplers\n\n"
                "# log the environment INTO the report (knit this in):\n"
                "sessionInfo()\n"
                "# or, with renv, snapshot the exact package versions:\n"
                "#   renv::snapshot()   # writes renv.lock"},
            {"heading": "Step 3 · Run the 5-step workflow end-to-end",
             "body": "Wire the course workflow — Question → Assume → Identify → "
                "Estimate → Validate — into scripts that hand off through files, "
                "so each stage is independently rerunnable.",
             "code_python": "# Makefile (excerpt) — `make all` rebuilds the report\n"
                "all: report.html\n\n"
                "data/clean/panel.parquet: src/01_clean.py data/raw/*.csv\n"
                "\tpython src/01_clean.py\n\n"
                "results/estimates.json: src/02_estimate.py data/clean/panel.parquet\n"
                "\tpython src/02_estimate.py\n\n"
                "results/robustness.csv: src/03_robustness.py results/estimates.json\n"
                "\tpython src/03_robustness.py\n\n"
                "report.html: report.qmd results/estimates.json results/robustness.csv\n"
                "\tquarto render report.qmd",
             "code_r": "# Makefile (excerpt) — `make all` rebuilds the report\n"
                "all: report.html\n\n"
                "data/clean/panel.rds: R/01_clean.R data/raw/*.csv\n"
                "\tRscript R/01_clean.R\n\n"
                "results/estimates.rds: R/02_estimate.R data/clean/panel.rds\n"
                "\tRscript R/02_estimate.R\n\n"
                "results/robustness.csv: R/03_robustness.R results/estimates.rds\n"
                "\tRscript R/03_robustness.R\n\n"
                "report.html: report.qmd results/estimates.rds results/robustness.csv\n"
                "\tquarto render report.qmd"},
            {"heading": "Step 4 · Add a robustness / multiverse loop",
             "body": "Don't defend one specification — run the grid and summarize. "
                "Loop over the reasonable adjustment sets and functional forms, "
                "store every estimate, and let the report plot the distribution.",
             "code_python": "from itertools import product\n"
                "import statsmodels.api as sm, pandas as pd, numpy as np\n\n"
                "rows = []\n"
                "for use_z2, use_z3, logy in product([0, 1], [0, 1], [0, 1]):\n"
                "    cols = ['D', 'X1'] + (['X2'] if use_z2 else []) + \\\n"
                "           (['X3'] if use_z3 else [])\n"
                "    y = np.log1p(df['Y']) if logy else df['Y']\n"
                "    est = sm.OLS(y, sm.add_constant(df[cols])).fit().params['D']\n"
                "    rows.append(dict(X2=use_z2, X3=use_z3, logY=logy, ate=est))\n"
                "multiverse = pd.DataFrame(rows)\n"
                "multiverse.to_csv('results/robustness.csv', index=False)",
             "code_r": "library(purrr); library(dplyr)\n\n"
                "grid <- expand.grid(use_z2 = 0:1, use_z3 = 0:1, logy = 0:1)\n"
                "multiverse <- pmap_dfr(grid, function(use_z2, use_z3, logy) {\n"
                "  rhs <- c('D', 'X1', if (use_z2) 'X2', if (use_z3) 'X3')\n"
                "  yv  <- if (logy) 'log1p(Y)' else 'Y'\n"
                "  f   <- reformulate(rhs, response = yv)\n"
                "  tibble(use_z2, use_z3, logy, ate = coef(lm(f, df))['D'])\n"
                "})\n"
                "write.csv(multiverse, 'results/robustness.csv', row.names = FALSE)"},
            {"heading": "Step 5 · Render the report",
             "body": "The report IS the deliverable: it imports the saved "
                "estimates and figures, narrates the 5-step workflow, and ends "
                "with the three-sentence stakeholder summary. Rendering it is the "
                "one command that proves the whole pipeline runs.",
             "code_python": "# from a clean checkout, this is the ENTIRE rebuild:\n"
                "#   git clone <repo> && cd causal-capstone\n"
                "#   python -m venv .venv && source .venv/bin/activate\n"
                "#   pip install -r requirements.txt\n"
                "#   make all          # clean -> estimate -> robustness -> render\n"
                "# Output: report.html, fully reproduced, seed-fixed.",
             "code_r": "# from a clean checkout, this is the ENTIRE rebuild:\n"
                "#   git clone <repo> && cd causal-capstone\n"
                "#   Rscript -e 'renv::restore()'   # exact package versions\n"
                "#   make all          # clean -> estimate -> robustness -> render\n"
                "# Output: report.html, fully reproduced, seed-fixed."},
        ],
        "expected": "From a clean clone, one command (`make all`) regenerates the "
            "cleaned data, the estimates, the robustness table, and the rendered "
            "report.html — byte-for-byte on the numbers, because the seed and the "
            "environment are pinned. If a teammate gets different numbers, the "
            "logged environment tells you exactly which version drifted. That "
            "reproducible skeleton is precisely what your capstone submission "
            "should look like.",
        "submit": [
            "Push the repository with a README that gives the one-command rebuild "
            "and a paragraph stating your estimand and identification strategy.",
            "Include the multiverse / robustness figure and a sensitivity "
            "(E-value-style) number in the report.",
            "End the report with your three-sentence stakeholder summary — the "
            "same one you will open your presentation with.",
        ],
    },
    "self_check": [
        "Given a question and a dataset, name the most credible design AND your "
        "second choice, and say why the first wins.",
        "Write your capstone estimand and its identification assumptions from "
        "memory, flagging the weakest one.",
        "Explain the garden of forking paths to a classmate and name two forks "
        "your own analysis contains.",
        "Run a multiverse loop and a sensitivity check, and state what would "
        "overturn your result.",
        "Rebuild your entire analysis from a clean clone with one command — and "
        "say the effect and its uncertainty in three plain sentences.",
    ],
    "next_week": {
        "heading": "After the course — keep going",
        "teaser": "There is no Week 16: from here the syllabus is the world. Take "
            "the workflow — Question → Assume → Identify → Estimate → Validate — "
            "to a question someone actually has to act on, and earn the causal "
            "claim end to end. The toolkit (RCTs, matching, weighting, IV, RD, "
            "DiD, synthetic control, DML, heterogeneous effects) is now yours; the "
            "remaining skill is judgment — choosing the credible design, stating "
            "the assumption that could sink you, and communicating uncertainty "
            "without flinching. Keep a reproducible repo for every analysis, stay "
            "honest about what the data can and cannot answer, and go do causal "
            "inference in practice.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "Week 15 — the capstone, end to end", "items": [
            {"t": "Choosing a design", "d": "Let the question and the data pick "
             "the method, not your taste."},
            {"t": "Pre-analysis plans", "d": "Close the garden of forking paths "
             "before you see the outcome."},
            {"t": "Robustness & multiverse", "d": "Survive the analyses you did "
             "not run; bound the unmeasured."},
            {"t": "Reproducible pipelines", "d": "One command, fixed seed, logged "
             "environment, Quarto + Git."},
            {"t": "Communicating effects", "d": "Effect, uncertainty, caveat — in "
             "three honest sentences."},
            {"t": "Ethics + your capstone", "d": "A causal claim licenses action. "
             "Then: present and review."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Fifteen weeks come down to one defensible analysis",
         "bullets": [
            "You have the estimators: RCTs, matching, weighting, IV, RD, DiD, "
            "synthetic control, DML, heterogeneous effects.",
            "The capstone adds no new method — it adds the discipline that makes "
            "any of them trustworthy.",
            ("The deliverable is a report + presentation: a real question, "
             "answered defensibly.", 1),
            "Today: how to choose, pre-commit, stress-test, reproduce, and "
            "communicate — then present and peer-review.",
         ],
         "note": {"title": "One sentence",
            "body": "A causal claim is only as good as its design, its stated "
            "assumptions, the checks it survives, and the honest sentence you can "
            "say to whoever must act on it."}},
        {"type": "statement",
         "quote": "No new estimator today — only the difference between a number "
            "and a number someone can act on.",
         "attribution": "The capstone is the course compressed into one workflow: "
            "Question → Assume → Identify → Estimate → Validate, done for real and "
            "explained to a human."},

        {"type": "section", "kicker": "Part 1", "title": "Choosing a design",
         "subtitle": "There is no best method — only the most credible design "
            "given the estimand and the assignment mechanism you actually have."},
        {"type": "content", "kicker": "Start from the question",
         "title": "Design follows the estimand, not your taste", "bullets": [
            "First write the estimand: contrast, population, outcome, horizon.",
            "Then ask how treatment was assigned — that mechanism picks the "
            "credible designs.",
            "Method beauty is irrelevant; identification credibility is "
            "everything.",
            ("Always name your SECOND-best design and why you rejected it.", 1),
         ],
         "note": {"title": "The capstone test",
            "body": "If you can't name the second-best design and say why it "
            "loses, you don't yet know why the first is credible."}},
        {"type": "table", "kicker": "A decision guide",
         "title": "From what you observe to a credible design",
         "headers": ["If you have…", "Reach for", "It identifies"],
         "rows": [
            ["Randomized assignment", "RCT", "the ATE, by design"],
            ["Random encouragement / instrument", "IV / MR", "a LATE (compliers)"],
            ["Threshold on a running variable", "RD", "a local effect at the cutoff"],
            ["A policy date + comparators", "DiD", "ATT under parallel trends"],
            ["One treated unit + donors", "Synthetic control", "ATT vs. a synthetic twin"],
            ["Rich confounders, good overlap", "Matching / DML", "ATE/ATT under exchangeability"],
         ],
         "note": {"title": "Fallback ladder",
            "body": "Adjustment (matching/DML) sits at the bottom: use it when no "
            "design-based option is available, and treat it as a benchmark."}},
        {"type": "compare", "kicker": "Two honest questions",
         "title": "What would make each design fail?", "columns": [
            {"head": "Design-based", "sub": "RCT · IV · RD · DiD · SC", "points": [
                "Leans on the assignment mechanism.",
                "Fails via: weak instrument, cutoff manipulation, "
                "non-parallel trends.",
                "Probe with placebo / pre-trend tests."]},
            {"head": "Adjustment-based", "sub": "Matching · weighting · DML",
             "points": [
                "Leans on no-unmeasured-confounding + overlap.",
                "Fails via: a confounder you never measured.",
                "Probe with sensitivity analysis (E-value)."]},
         ]},

        {"type": "section", "kicker": "Part 2",
         "title": "The garden of forking paths",
         "subtitle": "You can fool yourself without ever 'p-hacking' — every "
            "analysis you would have run is a comparison you never see."},
        {"type": "content", "kicker": "Gelman & Loken (2014)",
         "title": "Researcher degrees of freedom", "bullets": [
            "Covariates, subgroups, outcome coding, outlier rules — each a fork.",
            "If your choice would differ had the data differed, your p-value is no "
            "longer honest.",
            "This bites even on a single analysis you ran exactly once.",
            ("The fix is procedural, not statistical.", 1),
         ],
         "note": {"title": "Why one analysis still lies",
            "body": "The multiple comparisons are the paths you WOULD have taken — "
            "invisible, but still counted against you."}},
        {"type": "steps", "kicker": "The remedy",
         "title": "A pre-analysis plan, minimal version", "steps": [
            {"title": "Estimand", "body": "— contrast, population, outcome, "
             "horizon, fixed before unblinding."},
            {"title": "Model & set", "body": "— estimator and adjustment set, "
             "pre-specified."},
            {"title": "Primary outcome", "body": "— one, named; the rest are "
             "secondary."},
            {"title": "Decision rule", "body": "— what result triggers what "
             "conclusion."},
            {"title": "Exploration", "body": "— allowed, but labeled and confirmed "
             "out-of-sample."},
         ],
         "note": "Anything decided after seeing Y is exploratory — flag it as such."},
        {"type": "compare", "kicker": "Two modes of inquiry",
         "title": "Confirmatory vs. exploratory — both are fine", "columns": [
            {"head": "Confirmatory", "points": [
                "Pre-registered estimand and model.",
                "Controls error rates honestly.",
                "This is what your headline claim rests on."]},
            {"head": "Exploratory", "points": [
                "Discovered after looking at outcomes.",
                "Generates hypotheses, not conclusions.",
                "Must be labeled and confirmed on new data."]},
        ]},

        {"type": "section", "kicker": "Part 3",
         "title": "Robustness, multiverse & sensitivity",
         "subtitle": "A result you trust is one that survives the reasonable "
            "analyses you did not run — and tells you what would overturn it."},
        {"type": "content", "kicker": "Multiverse analysis",
         "title": "Report a distribution, not a point", "bullets": [
            "Loop over the grid of defensible specifications — adjustment sets, "
            "functional forms, codings.",
            "Plot the spread of estimates; pre-commit which specs are primary.",
            "A result that holds in 1 of 32 specs is about your luck, not the "
            "world.",
            ("Specs that include the true confounder cluster on the truth; "
             "omitting it drifts away.", 1),
         ],
         "note": {"title": "Honesty",
            "body": "Show the messy multiverse. Hiding it is the forking-paths "
            "problem wearing a lab coat."}},
        {"type": "content", "kicker": "Sensitivity analysis",
         "title": "How strong must a hidden confounder be?", "bullets": [
            "Don't argue about whether unmeasured confounding exists — quantify "
            "how strong it would have to be.",
            "The E-value: the minimum confounder–exposure and confounder–outcome "
            "association needed to explain the effect away.",
            "Benchmark it against the strongest confounder you already measured.",
            "Big E-value = the skeptic needs an implausibly strong hidden cause.",
         ],
         "note": {"title": "Bias, bounded",
            "body": "Sensitivity analysis turns 'but what about confounding?' from "
            "a conversation-ender into a number."}},
        {"type": "compare", "kicker": "Design-based stress tests",
         "title": "Checks that try to break your result", "columns": [
            {"head": "Negative-control outcome", "points": [
                "An outcome the treatment cannot affect.",
                "If it 'shows an effect', your design leaks."]},
            {"head": "Placebo / pre-trend", "points": [
                "A pre-period that should be flat (DiD).",
                "A non-effect that should be zero (RD).",
                "Movement here = a warning."]},
            {"head": "Refutation", "points": [
                "Add a random common cause; drop a subset.",
                "A robust estimate barely moves."]},
        ]},

        {"type": "section", "kicker": "Part 4",
         "title": "Reproducible pipelines",
         "subtitle": "If a colleague can't rebuild your numbers with one command, "
            "you have an anecdote, not a result."},
        {"type": "steps", "kicker": "What a rebuild requires",
         "title": "One command, fixed seed, logged environment", "steps": [
            {"title": "Fix the seed", "body": "— np.random.default_rng(7) / "
             "set.seed(7), set once, passed around."},
            {"title": "Pin the environment", "body": "— requirements.txt / "
             "renv.lock; capture pip freeze / sessionInfo()."},
            {"title": "Version everything", "body": "— Git for code, raw data, and "
             "the report source."},
            {"title": "One command", "body": "— make all / quarto render rebuilds "
             "clean → estimate → check → report."},
         ],
         "note": "Same input + same code + same seed + same environment = same "
            "output. That is the whole definition."},
        {"type": "content", "kicker": "Repo layout",
         "title": "Structure that makes results disposable", "bullets": [
            "data/raw/ is read-only; data/clean/ is generated and never edited by "
            "hand.",
            "Numbered scripts: 01_clean → 02_estimate → 03_robustness, handing off "
            "through files.",
            "report.qmd imports saved estimates and figures and narrates the "
            "workflow.",
            ("Everything in results/ is regenerable — that is the test.", 1),
         ],
         "note": {"title": "Quarto + Git",
            "body": "Quarto renders code + prose + results into one document; Git "
            "makes every input and version recoverable."}},
        {"type": "statement",
         "quote": "'Works on my machine' becomes a result only when the machine, "
            "the seed, and the versions travel with it.",
         "attribution": "Capture the environment into the report itself. Future "
            "you, and your reviewers, will need exactly that log."},

        {"type": "section", "kicker": "Part 5",
         "title": "Communicating effects & uncertainty",
         "subtitle": "If the decision-maker can't understand the effect, the "
            "analysis changes nothing — communication is part of the claim."},
        {"type": "steps", "kicker": "The three-sentence summary",
         "title": "Effect, uncertainty, caveat — no jargon", "steps": [
            {"title": "The effect", "body": "— in the stakeholder's units: "
             "'about $480 lower per enrollee.'"},
            {"title": "The uncertainty", "body": "— a plausible range: 'reasonably "
             "$200 to $760.'"},
            {"title": "The caveat", "body": "— the assumption that would change "
             "the answer, said plainly."},
         ],
         "note": "No p-values, no 'statistically significant' — a number, a range, "
            "and the load-bearing assumption."},
        {"type": "compare", "kicker": "How effects go wrong",
         "title": "Two failure modes to avoid", "columns": [
            {"head": "Overclaiming", "sub": "the common sin", "points": [
                "Point estimate stated as certainty.",
                "Caveats buried or dropped.",
                "Transfers your risk onto the decider."]},
            {"head": "Drowning", "sub": "the timid sin", "points": [
                "Every caveat, no headline.",
                "Uncertainty without a recommendation.",
                "Leaves the decider with nothing to use."]},
        ]},
        {"type": "content", "kicker": "Show the uncertainty",
         "title": "Visualize intervals, not just points", "bullets": [
            "Plot the effect with its confidence interval, in real units.",
            "Show the multiverse spread so robustness is visible at a glance.",
            "Translate to consequences: cost, lives, conversions — what they "
            "decide on.",
            "Lead with the answer; let the method live in an appendix.",
         ],
         "note": {"title": "Audience first",
            "body": "Technical appendix for reviewers; one chart and three "
            "sentences for the decision-maker."}},

        {"type": "section", "kicker": "Part 6",
         "title": "Ethics & your capstone",
         "subtitle": "A causal claim licenses action — state your uncertainty and "
            "assumptions as loudly as your point estimate."},
        {"type": "content", "kicker": "The ethics of causal claims",
         "title": "Someone will act on your number", "bullets": [
            "A causal claim can move a treatment, a price, or a policy.",
            "Overclaiming is not optimism — it transfers your risk onto people who "
            "trusted you.",
            "State assumptions and uncertainty in proportion to the stakes.",
            "Reproducibility is an ethical practice, not just a tidy one.",
         ],
         "note": {"title": "The standard",
            "body": "Be as loud about what could be wrong as about what you "
            "found."}},
        {"type": "steps", "kicker": "Capstone deliverable",
         "title": "What you submit, and how it's reviewed", "steps": [
            {"title": "The report", "body": "— estimand, design, estimate, "
             "robustness, sensitivity, reproducible repo."},
            {"title": "The presentation", "body": "— opens with the three-sentence "
             "summary; method in the appendix."},
            {"title": "Peer review", "body": "— attack the weakest assumption; "
             "try to break the result."},
            {"title": "Revise", "body": "— address the review; reproducibility "
             "makes revision one command."},
         ],
         "note": "The peer review is not adversarial theater — it is the "
            "stress test your result must survive before the world runs it."},
        {"type": "statement",
         "quote": "Question → Assume → Identify → Estimate → Validate — now do it "
            "for something that matters, and earn the claim.",
         "attribution": "There is no Week 16: from here the syllabus is the "
            "world. Keep a reproducible repo, stay honest about what the data can "
            "answer, and go do causal inference in practice."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "# Mini capstone: one decision problem, the whole workflow\n\n"
            "This notebook is a **template for your capstone**. We invent a single "
            "decision problem with a **known true effect**, then walk every step "
            "of the course workflow on it:\n\n"
            "1. **State the estimand**\n"
            "2. **Encode assumptions** as a DAG-shaped data-generating process\n"
            "3. **Identify** the back-door adjustment set\n"
            "4. **Estimate** with **two** methods and check they agree *and* "
            "recover the truth\n"
            "5. **Validate** with a robustness / multiverse loop and a sensitivity "
            "(E-value) check\n\n"
            "…and finish with a plain-language **communicate-the-result** summary "
            "and a **reproducibility** log. Swap in your real data and this "
            "becomes your submission."},

        {"md": "## 0 · Reproducibility — fixed seed & logged environment\n\n"
            "Reproducibility starts here: one seed (`RNG`, defined in the setup "
            "cell — we **reuse** it, never reseed) and a printed log of library "
            "versions so the result travels with the environment that produced "
            "it."},
        {"code": "import sys\n"
            "import numpy as np, pandas as pd\n"
            "import statsmodels.api as sm\n"
            "import sklearn, statsmodels\n\n"
            "print('--- environment log (paste this into your report) ---')\n"
            "print('python     ', sys.version.split()[0])\n"
            "print('numpy      ', np.__version__)\n"
            "print('pandas     ', pd.__version__)\n"
            "print('scikit-learn', sklearn.__version__)\n"
            "print('statsmodels ', statsmodels.__version__)\n"
            "print('seed        7  (RNG = np.random.default_rng(7), reused)')"},

        {"md": "## 1 · State the estimand\n\n"
            "**Decision problem.** A company offers an optional *training program* "
            "`D` to employees and wants to know its effect on *productivity* `Y`. "
            "Enrollment is **not** random: more experienced and more motivated "
            "people enroll, and those traits also raise productivity. That is "
            "confounding.\n\n"
            "**Estimand.** The average treatment effect\n\n"
            "$$\\text{ATE} = E[Y(1) - Y(0)],$$\n\n"
            "the expected change in productivity if we moved everyone from "
            "untrained to trained. We will build the world so that the **true ATE "
            "is exactly 3.0**, then see which analyses recover it."},

        {"md": "## 2 · Encode assumptions — a DAG as a data-generating process\n\n"
            "Our assumed causal graph:\n\n"
            "```\n"
            "  experience (X1) ─┐        ┌─> Y\n"
            "                   ├─> D ───┤\n"
            "  motivation (X2) ─┘        └─> Y\n"
            "          noise (X3) ─────────> Y   (affects Y only, not D)\n"
            "```\n\n"
            "`X1` and `X2` are **confounders** (they cause both `D` and `Y`). "
            "`X3` affects only `Y`. There is **no unmeasured confounding** in the "
            "true world — we will *pretend* otherwise later, in the sensitivity "
            "step, to stress-test the conclusion."},
        {"code": "N = 8000\n"
            "TRUE_ATE = 3.0          # <-- the ground truth we must recover\n\n"
            "# Confounders\n"
            "X1 = RNG.normal(size=N)                  # experience\n"
            "X2 = RNG.normal(size=N)                  # motivation\n"
            "X3 = RNG.normal(size=N)                  # outcome-only driver\n\n"
            "# Treatment: experienced & motivated people enroll more (propensity)\n"
            "logit = -0.4 + 0.9 * X1 + 0.7 * X2\n"
            "propensity = 1.0 / (1.0 + np.exp(-logit))\n"
            "D = RNG.binomial(1, propensity)\n\n"
            "# Outcome: TRUE effect of D is exactly TRUE_ATE; confounders push Y too\n"
            "Y = (TRUE_ATE * D + 1.5 * X1 + 1.2 * X2 + 0.8 * X3\n"
            "     + RNG.normal(size=N))\n\n"
            "df = pd.DataFrame({'Y': Y, 'D': D, 'X1': X1, 'X2': X2, 'X3': X3,\n"
            "                   'propensity': propensity})\n"
            "print(f'n = {N},  treated = {D.mean():.1%},  TRUE ATE = {TRUE_ATE}')\n"
            "print(f'overlap: propensity in [{propensity.min():.2f}, '\n"
            "      f'{propensity.max():.2f}]  (positivity looks OK)')"},

        {"md": "### The naive comparison is biased\n\n"
            "Before doing anything clever, compare trained vs. untrained "
            "directly. Because enrollees were already more experienced and "
            "motivated, the raw gap **overstates** the effect — this is the "
            "confounding we must remove."},
        {"code": "naive = df.loc[df.D == 1, 'Y'].mean() - df.loc[df.D == 0, 'Y'].mean()\n"
            "print(f'Naive difference in means : {naive:.3f}')\n"
            "print(f'True ATE                  : {TRUE_ATE:.3f}')\n"
            "print(f'Bias from confounding     : {naive - TRUE_ATE:+.3f}  '\n"
            "      '(inflated, as expected)')\n"
            "assert naive > TRUE_ATE + 0.3, 'naive estimate should be biased upward'"},

        {"md": "## 3 · Identify — the back-door adjustment set\n\n"
            "To read the `D → Y` effect we must block every back-door path. The "
            "back-door paths run `D ← X1 → Y` and `D ← X2 → Y`, so the adjustment "
            "set is **{X1, X2}**.\n\n"
            "- `X1`, `X2`: **confounders → adjust.**\n"
            "- `X3`: affects only `Y`, opens no back-door path. Adjusting is "
            "harmless (and slightly improves precision), but it is *not required* "
            "for identification.\n\n"
            "With {X1, X2} measured and overlap holding, the ATE is **identified** "
            "by back-door adjustment."},

        {"md": "## 4 · Estimate with TWO methods\n\n"
            "We estimate the same identified ATE two independent ways and check "
            "they **agree with each other** and **recover the truth**:\n\n"
            "- **(A) OLS regression adjustment** — include the back-door set.\n"
            "- **(B) IPW** — inverse-probability weighting with a logistic "
            "propensity model.\n\n"
            "Two methods that disagree are a red flag; two that agree on the truth "
            "are reassuring."},
        {"code": "# --- (A) OLS regression adjustment on the back-door set {X1, X2} ---\n"
            "Xmat = sm.add_constant(df[['D', 'X1', 'X2']].to_numpy())\n"
            "ols = sm.OLS(df['Y'].to_numpy(), Xmat).fit()\n"
            "ate_ols = ols.params[1]                 # coefficient on D\n"
            "se_ols  = ols.bse[1]\n"
            "print(f'(A) OLS adjustment ATE = {ate_ols:.3f}  '\n"
            "      f'(95% CI {ate_ols - 1.96*se_ols:.2f} to {ate_ols + 1.96*se_ols:.2f})')\n"
            "assert abs(ate_ols - TRUE_ATE) < 0.15, 'OLS should recover ~3.0'"},
        {"code": "# --- (B) IPW with a logistic propensity model on {X1, X2} ---\n"
            "from sklearn.linear_model import LogisticRegression\n\n"
            "Xc = df[['X1', 'X2']].to_numpy()\n"
            "Dv = df['D'].to_numpy()\n"
            "Yv = df['Y'].to_numpy()\n\n"
            "ps = LogisticRegression().fit(Xc, Dv).predict_proba(Xc)[:, 1]\n"
            "ps = np.clip(ps, 0.02, 0.98)            # trim to respect positivity\n"
            "w  = np.where(Dv == 1, 1.0 / ps, 1.0 / (1.0 - ps))\n\n"
            "ate_ipw = (np.average(Yv[Dv == 1], weights=w[Dv == 1])\n"
            "           - np.average(Yv[Dv == 0], weights=w[Dv == 0]))\n"
            "print(f'(B) IPW ATE        = {ate_ipw:.3f}')\n"
            "print(f'    OLS ATE        = {ate_ols:.3f}')\n"
            "print(f'    TRUE ATE       = {TRUE_ATE:.3f}')\n"
            "assert abs(ate_ipw - TRUE_ATE) < 0.20, 'IPW should recover ~3.0'\n"
            "assert abs(ate_ipw - ate_ols) < 0.25, 'the two methods should agree'"},

        {"md": "### 🔧 Exercise 4.1 — add a third estimator (cross-fitted DML)\n\n"
            "Two methods agree; a third makes the result harder to dismiss. "
            "Implement **double / debiased machine learning** by the "
            "partialling-out trick, done with *linear* nuisance models and "
            "**5-fold cross-fitting**:\n\n"
            "1. Cross-fit predictions of `Y` from `{X1, X2}` and of `D` from "
            "`{X1, X2}`.\n"
            "2. Form residuals `Ỹ = Y − Ŷ` and `D̃ = D − D̂`.\n"
            "3. The DML ATE is the slope of `Ỹ` on `D̃`: "
            "`sum(D̃·Ỹ) / sum(D̃·D̃)`.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (it just falls back to "
            "the OLS estimate) so the notebook never breaks."},
        {"code": "from sklearn.linear_model import LinearRegression\n"
            "from sklearn.model_selection import KFold\n\n"
            "Xc = df[['X1', 'X2']].to_numpy()\n"
            "Dv = df['D'].to_numpy().astype(float)\n"
            "Yv = df['Y'].to_numpy()\n\n"
            "kf = KFold(n_splits=5, shuffle=True, random_state=0)\n"
            "Y_res = np.zeros(N)\n"
            "D_res = np.zeros(N)\n"
            "done = False   # flip to True once you fill the loop in\n\n"
            "for train_idx, test_idx in kf.split(Xc):\n"
            "    # TODO: fit LinearRegression of Y on Xc using train_idx,\n"
            "    #       then store the residual on test_idx into Y_res[test_idx]\n"
            "    # TODO: do the same for D into D_res[test_idx]\n"
            "    # TODO: set done = True\n"
            "    pass\n\n"
            "# Fallback so the skeleton runs even before you fill it in:\n"
            "if done:\n"
            "    ate_dml = np.sum(D_res * Y_res) / np.sum(D_res * D_res)\n"
            "else:\n"
            "    ate_dml = ate_ols   # placeholder until you implement the loop\n"
            "print(f'(skeleton) DML ATE = {ate_dml:.3f}')"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "from sklearn.linear_model import LinearRegression\n"
            "from sklearn.model_selection import KFold\n\n"
            "kf = KFold(n_splits=5, shuffle=True, random_state=0)\n"
            "Y_res = np.zeros(N)\n"
            "D_res = np.zeros(N)\n\n"
            "for train_idx, test_idx in kf.split(Xc):\n"
            "    m_y = LinearRegression().fit(Xc[train_idx], Yv[train_idx])\n"
            "    m_d = LinearRegression().fit(Xc[train_idx], Dv[train_idx])\n"
            "    Y_res[test_idx] = Yv[test_idx] - m_y.predict(Xc[test_idx])\n"
            "    D_res[test_idx] = Dv[test_idx] - m_d.predict(Xc[test_idx])\n\n"
            "ate_dml = np.sum(D_res * Y_res) / np.sum(D_res * D_res)\n"
            "print(f'(A) OLS  ATE = {ate_ols:.3f}')\n"
            "print(f'(B) IPW  ATE = {ate_ipw:.3f}')\n"
            "print(f'(C) DML  ATE = {ate_dml:.3f}')\n"
            "print(f'    TRUE ATE = {TRUE_ATE:.3f}')\n"
            "assert abs(ate_dml - TRUE_ATE) < 0.15, 'DML should recover ~3.0'\n"
            "print('\\nThree independent estimators, one truth. That is a result '\n"
            "      'you can defend.')"},

        {"md": "## 5 · Validate — robustness / multiverse loop\n\n"
            "Instead of defending one specification, run the **grid** of "
            "reasonable ones and look at the *distribution* of estimates. We vary:\n\n"
            "- whether we adjust for `X2` (a real confounder),\n"
            "- whether we adjust for `X3` (an outcome-only variable, optional),\n"
            "- whether we add a quadratic term in `X1` (functional form).\n\n"
            "`X1` is always included. The key lesson: specifications that include "
            "the **X2 confounder** cluster on the truth; dropping it drifts away."},
        {"code": "from itertools import product\n\n"
            "rows = []\n"
            "for use_x2, use_x3, quad in product([0, 1], [0, 1], [0, 1]):\n"
            "    cols = ['D', 'X1'] + (['X2'] if use_x2 else []) + \\\n"
            "           (['X3'] if use_x3 else [])\n"
            "    Xm = df[cols].to_numpy().astype(float)\n"
            "    if quad:\n"
            "        Xm = np.column_stack([Xm, df['X1'].to_numpy() ** 2])\n"
            "    est = sm.OLS(df['Y'].to_numpy(), sm.add_constant(Xm)).fit().params[1]\n"
            "    rows.append({'adj_X2': use_x2, 'adj_X3': use_x3,\n"
            "                 'quad_X1': quad, 'ate': est})\n\n"
            "multiverse = pd.DataFrame(rows).sort_values('ate').reset_index(drop=True)\n"
            "print(multiverse)\n"
            "print(f'\\nFull multiverse range: '\n"
            "      f'{multiverse.ate.min():.2f} to {multiverse.ate.max():.2f}')"},
        {"code": "# Split the multiverse by whether the X2 confounder was adjusted for\n"
            "with_x2 = multiverse.loc[multiverse.adj_X2 == 1, 'ate']\n"
            "without_x2 = multiverse.loc[multiverse.adj_X2 == 0, 'ate']\n"
            "print(f'Specs adjusting for X2   : mean {with_x2.mean():.3f}  '\n"
            "      f'(range {with_x2.min():.2f}-{with_x2.max():.2f})')\n"
            "print(f'Specs OMITTING X2        : mean {without_x2.mean():.3f}  '\n"
            "      f'(range {without_x2.min():.2f}-{without_x2.max():.2f})')\n"
            "print(f'True ATE                 : {TRUE_ATE:.3f}')\n\n"
            "# The correctly-specified family recovers the truth; the rest is bias.\n"
            "assert abs(with_x2.mean() - TRUE_ATE) < 0.15\n"
            "assert without_x2.mean() > with_x2.mean() + 0.3\n"
            "print('\\n-> Robust WITHIN the correctly-identified specifications; '\n"
            "      'the spread is driven by dropping a real confounder.')"},
        {"code": "import matplotlib.pyplot as plt\n\n"
            "fig, ax = plt.subplots()\n"
            "colors = ['#2A9D8F' if a else '#C0504D' for a in multiverse.adj_X2]\n"
            "ax.scatter(multiverse.ate, range(len(multiverse)), c=colors, s=70,\n"
            "           zorder=3)\n"
            "ax.axvline(TRUE_ATE, color='#1F2A44', ls='--', label='true ATE = 3.0')\n"
            "ax.set_xlabel('estimated ATE')\n"
            "ax.set_ylabel('specification (sorted)')\n"
            "ax.set_title('Multiverse: teal = adjusts for X2 confounder, '\n"
            "             'red = omits it')\n"
            "ax.legend(loc='lower right')\n"
            "# figure created (no blocking show); it would be embedded in the report"},

        {"md": "### Sensitivity — how strong would unmeasured confounding have to "
            "be?\n\n"
            "We adjusted for everything we measured (`X1`, `X2`), and our reported "
            "estimate is `ate_ols`. A skeptic still says 'but some confounder you "
            "*didn't* measure explains it!' We answer **quantitatively** with an "
            "**E-value**: the minimum strength (on the risk-ratio scale) that a "
            "*further, unmeasured* confounder would need with **both** treatment "
            "and outcome — beyond `X1` and `X2` — to fully explain the reported "
            "effect away. A large E-value means the skeptic needs an implausibly "
            "strong hidden cause. (In the next exercise we instead *drop* a known "
            "confounder to see the bias an unmeasured one would create.)"},
        {"code": "def e_value(rr):\n"
            "    \"\"\"E-value for an observed risk ratio rr (VanderWeele & Ding 2017).\"\"\"\n"
            "    rr = max(rr, 1.0 / rr)            # work on the >= 1 side\n"
            "    return rr + np.sqrt(rr * (rr - 1.0))\n\n"
            "# Translate a standardized mean effect into an approximate risk ratio\n"
            "# (a common rough conversion: RR ~ exp(0.91 * standardized effect)).\n"
            "sd_y = df['Y'].std()\n"
            "rr_observed = float(np.exp(0.91 * (ate_ols / sd_y)))\n"
            "ev = e_value(rr_observed)\n"
            "print(f'Approx. observed risk ratio : {rr_observed:.3f}')\n"
            "print(f'E-value                     : {ev:.3f}')\n"
            "print(f'Interpretation: an unmeasured confounder would need RR >= '\n"
            "      f'{ev:.2f}')\n"
            "print('with BOTH treatment and outcome to explain the effect away.')\n"
            "assert ev > 1.0, 'a non-null effect should have an E-value above 1'"},

        {"md": "### 🔧 Exercise 5.1 — quantify the bias from dropping a confounder\n\n"
            "Estimate the ATE while **omitting `X2`** (simulating an unmeasured "
            "confounder), and compute how much bias that introduces relative to "
            "the truth. Then state, in a comment, whether the bias is large enough "
            "that you would worry. Fill in the `# TODO`s; the skeleton runs."},
        {"code": "# TODO: regress Y on [D, X1] only (X2 omitted), pull the D coefficient\n"
            "Xm_omit = sm.add_constant(df[['D', 'X1']].to_numpy())\n"
            "ate_omit = ...        # TODO: fit OLS and take .params[1]\n"
            "# bias_omit = ...     # TODO: ate_omit - TRUE_ATE\n"
            "# print(ate_omit, bias_omit)\n\n"
            "# Fallback so the skeleton runs before you fill it in:\n"
            "if ate_omit is ...:\n"
            "    ate_omit = ate_ols\n"
            "print(f'(skeleton) ATE omitting X2 = {ate_omit:.3f}')"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "Xm_omit = sm.add_constant(df[['D', 'X1']].to_numpy())\n"
            "ate_omit = sm.OLS(df['Y'].to_numpy(), Xm_omit).fit().params[1]\n"
            "bias_omit = ate_omit - TRUE_ATE\n"
            "print(f'ATE adjusting for {{X1, X2}} : {ate_ols:.3f}  (correct)')\n"
            "print(f'ATE omitting X2            : {ate_omit:.3f}  (confounded)')\n"
            "print(f'Bias from the hidden X2    : {bias_omit:+.3f}')\n"
            "assert ate_omit > ate_ols + 0.3, 'omitting a real confounder inflates the ATE'\n"
            "print('\\nThe omitted confounder inflates the effect — exactly the '\n"
            "      'scenario the E-value is built to reason about.')"},

        {"md": "## 6 · Communicate the result\n\n"
            "The analysis is only useful if a decision-maker can act on it. Here "
            "is the **three-sentence stakeholder summary** — effect, uncertainty, "
            "caveat — with no jargon. (In your capstone, paste the real numbers "
            "from the cells above.)"},
        {"code": "lo = ate_ols - 1.96 * se_ols\n"
            "hi = ate_ols + 1.96 * se_ols\n"
            "summary = (\n"
            "    f'1. On average, the training program raised productivity by about '\n"
            "    f'{ate_ols:.1f} points per employee.\\n'\n"
            "    f'2. Our best estimate could reasonably lie between '\n"
            "    f'{lo:.1f} and {hi:.1f}, so the program clearly helps, though the '\n"
            "    f'exact size is uncertain.\\n'\n"
            "    f'3. This holds if enrollees and non-enrollees were comparable '\n"
            "    f'once we account for experience and motivation; if some other '\n"
            "    f'unmeasured trait drove both enrolling and productivity '\n"
            "    f'(E-value ~ {ev:.1f}), the true effect would be smaller.'\n"
            ")\n"
            "print(summary)"},
        {"md": "> **Effect, uncertainty, caveat — three sentences, no p-values.**\n"
            ">\n"
            "> Notice what the summary does *not* do: it does not say "
            "'statistically significant', it does not hide the assumption, and it "
            "does not pretend the point estimate is exact. That honesty is the "
            "whole point of the capstone."},

        {"md": "## Wrap-up & self-check\n\n"
            "You just ran a complete, defensible causal analysis end to end:\n\n"
            "- **Estimand** stated (ATE of training on productivity).\n"
            "- **Assumptions** encoded as a DAG-shaped DGP with a known truth "
            "(3.0).\n"
            "- **Identified** via the back-door set {X1, X2}.\n"
            "- **Estimated** three ways — OLS, IPW, DML — all recovering ~3.0 and "
            "agreeing.\n"
            "- **Validated** with a multiverse loop (robust within the correctly "
            "identified family) and an **E-value** sensitivity check.\n"
            "- **Communicated** the effect, its uncertainty, and the load-bearing "
            "caveat in three plain sentences.\n"
            "- **Reproducible**: one fixed seed (`RNG`), a printed environment "
            "log.\n\n"
            "**This is the skeleton of your capstone.** Replace the simulated "
            "world with your real question and data, keep every step, and you have "
            "a submission you can defend in front of a reviewer — and a "
            "decision-maker.\n\n"
            "*There is no Week 16: from here, the syllabus is the world. Go do "
            "causal inference in practice.*"},
    ],
}
