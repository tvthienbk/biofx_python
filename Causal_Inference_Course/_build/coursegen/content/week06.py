# -*- coding: utf-8 -*-
"""Week 6 — Matching & Propensity Scores."""

WEEK = {
    "number": 6,
    "slug": "matching_propensity",
    "title": "Matching & Propensity Scores",
    "block": "Block II — Adjustment for confounding",
    "subtitle": "Recreating a randomized comparison by balancing the covariate "
                "distributions of treated and control units.",
    "deliverable": "Concept Set 6 — propensity scores & balance; "
                   "Lab 3 — matching & balance on a confounded dataset.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), concept set (1.5h), lab (2–3h).",
    "one_sentence": "Matching and the propensity score try to recover a "
        "randomized comparison from observational data by selecting, weighting, "
        "or grouping units so that — within the analysis sample — treated and "
        "control groups have the same covariate distribution.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Explain why the propensity score e(X) = P(D=1 | X) is a balancing score, "
        "so that conditioning on it removes covariate-induced confounding.",
        "Distinguish exact, coarsened, and nearest-neighbor matching, and say "
        "when each is appropriate.",
        "Compute and read a standardized mean difference (SMD) as a balance "
        "diagnostic, and interpret a love-plot of before/after balance.",
        "Diagnose common support / overlap, decide when to trim, and explain how "
        "trimming changes the estimand.",
        "Estimate the ATT by 1:1 nearest-neighbor matching on the propensity "
        "score and explain why naive post-matching standard errors are wrong.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Imbens & Rubin, Causal Inference for Statistics… — "
                 "Chapters 12–15.",
         "look_for": "the propensity-score theorem (the balancing property) and "
                     "how the ATT is estimated after matching."},
        {"text": "Stuart (2010), \"Matching methods for causal inference: A "
                 "review\" (Statistical Science).",
         "look_for": "the practical workflow — estimate the propensity score → "
                     "match → check balance → estimate the effect."},
    ],
    "optional_readings": [
        {"text": "Cunningham, The Mixtape — Matching & Subclassification.",
         "note": "A code-first walkthrough of matching, subclassification, and "
                 "the propensity score on the LaLonde data."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its "
        "own.",
    "concept_sections": [
        {"heading": "The goal: rebuild the experiment we did not run",
         "body": "Under unconfoundedness — (Y(0), Y(1)) ⟂ D | X — a randomized "
            "trial is what you would have if treated and control units had the "
            "same distribution of X. Matching and propensity-score methods do not "
            "create that randomization; they approximate it after the fact by "
            "building a comparison group whose covariates look like the treated "
            "group's. The payoff is a design-stage step you can check (balance) "
            "before you ever look at the outcome — which keeps you honest."},
        {"heading": "The propensity score and its balancing property",
         "body": "The propensity score is e(X) = P(D = 1 | X), the probability of "
            "treatment given covariates. Rosenbaum & Rubin's theorem says e(X) is "
            "a balancing score: X ⟂ D | e(X). Conditioning on a single scalar "
            "therefore removes the same confounding that conditioning on the full "
            "vector X would — which is why matching or weighting on e(X) works.",
         "bullets": [
            [("Balancing score:  ", {"bold": True}),
             ("within a thin stratum of e(X), treated and control units have the "
              "same covariate distribution, so they are comparable.", {})],
            [("Dimension reduction:  ", {"bold": True}),
             ("you match on one number instead of many covariates, sidestepping "
              "the curse of dimensionality of exact matching.", {})],
            [("It must be estimated:  ", {"bold": True}),
             ("e(X) is unknown; we fit it (e.g. logistic regression). The score "
              "is a means to balance, not an end — judge it by the balance it "
              "produces, not by its classification accuracy.", {})],
         ]},
        {"heading": "Flavors of matching",
         "bullets": [
            [("Exact matching:  ", {"bold": True}),
             ("pair units with identical covariate values. Perfect balance, but "
              "infeasible with many or continuous covariates.", {})],
            [("Coarsened exact matching (CEM):  ", {"bold": True}),
             ("bin covariates into coarse strata, then exact-match on the bins — "
              "a tunable trade between balance and retained sample.", {})],
            [("Nearest-neighbor on the PS:  ", {"bold": True}),
             ("match each treated unit to the control with the closest "
              "propensity score; the workhorse of this lab.", {})],
            [("Knobs:  ", {"bold": True}),
             ("a caliper caps the allowed distance; 1:k matching uses k controls "
              "per treated unit; matching with replacement reuses good controls.",
              {})],
         ]},
        {"heading": "Balance diagnostics, overlap, and the estimand",
         "body": "After matching you check balance, not fit. The standardized "
            "mean difference (SMD) — the difference in means scaled by the "
            "pooled standard deviation — is the standard per-covariate diagnostic; "
            "|SMD| < 0.1 is a common rule of thumb. A love-plot stacks the SMDs "
            "before and after matching so you can see balance improve at a glance.",
         "bullets": [
            [("Common support / overlap:  ", {"bold": True}),
             ("positivity requires 0 < e(X) < 1 for every covariate profile. "
              "Where the PS distributions of the groups do not overlap, there are "
              "no comparable units and the effect is not estimable there.", {})],
            [("Trimming:  ", {"bold": True}),
             ("dropping units outside the region of common support restores "
              "overlap — but it changes the population, so you are now estimating "
              "the effect for that trimmed sub-population.", {})],
            [("ATT vs ATE:  ", {"bold": True}),
             ("1:1 matching of controls to treated units targets the ATT — the "
              "effect for the treated. It only needs overlap one direction (a "
              "control-like match for each treated unit), which is why it is the "
              "natural matching estimand.", {})],
         ],
         "callout": {"title": "Inference after matching is not free",
            "color": "RED",
            "lines": ["Matching is a DESIGN step. Estimating an SE as if the "
                      "matched sample were i.i.d. ignores that the propensity "
                      "score was estimated and that controls were reused — so "
                      "naive SEs are usually too small.",
                      "Use matching-aware variance estimators (Abadie–Imbens), a "
                      "bootstrap that re-runs the WHOLE pipeline, or report a "
                      "doubly robust estimator (Week 7)."]}},
    ],
    "problem_set": {
        "label": "Concept Set 6",
        "title": "Propensity scores & balance",
        "intro": "Short-answer problems on the logic of matching and the "
            "propensity score. Try all five before you look at the solutions; "
            "write your reasoning in full sentences.",
        "problems": [
            {"title": "Why the propensity score is a balancing score",
             "prompt": "State the balancing property of the propensity score "
                "e(X) = P(D=1 | X). In one or two sentences, explain what "
                "X ⟂ D | e(X) means in words, and why it lets you condition on a "
                "single scalar instead of the full covariate vector X.",
             "solution_title": "Within a level of e(X), treatment is as-if "
                "unrelated to X — so balancing on e(X) balances all of X.",
             "solution": [
                "The balancing property is X ⟂ D | e(X): conditional on the "
                "propensity score, the covariates carry no further information "
                "about treatment assignment.",
                "Operationally, among units with (nearly) the same e(X), the "
                "treated and control covariate distributions coincide — they look "
                "like a randomized block.",
                "So matching, stratifying, or weighting on the scalar e(X) "
                "achieves the same confounding removal as conditioning on the "
                "whole vector X, dodging the curse of dimensionality. (It does "
                "NOT fix bias from unmeasured confounders not in X.)"]},
            {"title": "Standardized mean difference as a balance diagnostic",
             "prompt": "Define the standardized mean difference (SMD) for a "
                "covariate between treated and control groups. Why standardize by "
                "the pooled SD rather than just report the raw mean difference, "
                "and what rough threshold do people use to call a covariate "
                "'balanced'?",
             "solution_title": "SMD = mean gap ÷ pooled SD; scale-free, with "
                "|SMD| < 0.1 a common target.",
             "solution": [
                "SMD = (x̄_treated − x̄_control) / sqrt[(s²_treated + s²_control)/2]: "
                "the group mean difference expressed in pooled-standard-deviation "
                "units.",
                "Standardizing makes it unit-free and comparable across covariates "
                "(age in years vs income in dollars), and — unlike a t-test — it "
                "does not shrink to 'significant' just because n is large.",
                "A widely used rule of thumb is |SMD| < 0.1 for adequate balance "
                "(0.1–0.2 marginal). Check it BEFORE looking at outcomes; a "
                "love-plot shows every covariate's SMD before vs after matching."]},
            {"title": "Common support, positivity, and trimming",
             "prompt": "A reviewer notes that some treated units have propensity "
                "scores above the maximum control score, and some controls fall "
                "below the minimum treated score. What assumption is threatened, "
                "what does trimming to the region of common support do, and what "
                "is the cost of trimming?",
             "solution_title": "Positivity/overlap is threatened; trimming "
                "restores it but changes the estimand.",
             "solution": [
                "The threatened assumption is positivity (overlap): 0 < e(X) < 1 "
                "for every covariate profile. Where the PS distributions do not "
                "overlap there are no comparable units, so the effect is not "
                "estimable from data — only from extrapolation.",
                "Trimming drops units outside the common-support region, leaving a "
                "sub-sample where treated and control overlap and comparisons are "
                "made among genuinely similar units.",
                "The cost: you are no longer estimating the effect for the "
                "original population but for the trimmed sub-population (often a "
                "milder ATT). Report what you dropped and how the estimand shifted."]},
            {"title": "ATT versus ATE under matching",
             "prompt": "You match each treated unit to its nearest control. "
                "Which estimand does this most naturally target — ATT or ATE — and "
                "why? What changes about the overlap requirement if you instead "
                "want the ATE?",
             "solution_title": "Matching controls to the treated targets the ATT; "
                "the ATE needs two-sided overlap.",
             "solution": [
                "Pairing a control to every treated unit reconstructs the "
                "counterfactual outcome for the treated group, so the natural "
                "estimand is the ATT = E[Y(1) − Y(0) | D=1].",
                "The ATT only needs a control-like match for each treated unit "
                "(overlap on the treated side of the PS distribution).",
                "The ATE = E[Y(1) − Y(0)] additionally requires a treated-like "
                "match for each control — two-sided overlap across the entire PS "
                "range — and is more fragile when one group is rare in part of the "
                "covariate space."]},
            {"title": "Why naive post-matching standard errors can be wrong",
             "prompt": "After 1:1 nearest-neighbor matching with replacement, a "
                "student computes the SE of the ATT as if the matched pairs were "
                "an independent sample. Give two reasons this SE is likely too "
                "small, and name one valid alternative.",
             "solution_title": "It ignores PS estimation and control reuse — use "
                "a matching-aware SE or a full-pipeline bootstrap.",
             "solution": [
                "The propensity score was ESTIMATED from the same data; treating "
                "it as known understates uncertainty (the matching itself is "
                "random).",
                "With replacement, some controls are reused across many pairs, so "
                "the matched 'observations' are dependent — the i.i.d. assumption "
                "behind the naive SE fails, and matched-pair counts are themselves "
                "random.",
                "Valid options: the Abadie–Imbens matching variance estimator, a "
                "bootstrap that re-runs the ENTIRE pipeline (refit PS, rematch, "
                "re-estimate), or a doubly robust estimator with proper inference "
                "(Week 7). A within-pair paired analysis is not enough."]},
        ],
    },
    "lab": {
        "label": "Lab 3",
        "title": "Matching & balance",
        "goal": "estimate a propensity score, match treated to control units, "
            "verify that matching improved covariate balance, and report an ATT — "
            "the full design-then-estimate workflow. Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Estimate the propensity score",
             "body": "Fit e(X) = P(D=1 | X) with logistic regression on your "
                "confounders. You will judge this model by the balance it buys, "
                "not by its classification accuracy.",
             "code_python": "import numpy as np, pandas as pd\n"
                "from sklearn.linear_model import LogisticRegression\n"
                "X = df[['age', 'educ', 'prior']].values\n"
                "ps_model = LogisticRegression(max_iter=1000).fit(X, df['D'])\n"
                "df['ps'] = ps_model.predict_proba(X)[:, 1]",
             "code_r": 'ps_fit <- glm(D ~ age + educ + prior,\n'
                '               family = binomial, data = df)\n'
                'df$ps  <- predict(ps_fit, type = "response")'},
            {"heading": "Step 2 · Nearest-neighbor match (targets the ATT)",
             "body": "Match each treated unit to the control with the closest "
                "propensity score. In R, MatchIt does this in one call.",
             "code_python": "from sklearn.neighbors import NearestNeighbors\n"
                "trt = df[df.D == 1]; ctl = df[df.D == 0]\n"
                "nn = NearestNeighbors(n_neighbors=1).fit(ctl[['ps']])\n"
                "_, idx = nn.kneighbors(trt[['ps']])\n"
                "matched_ctl = ctl.iloc[idx.ravel()]",
             "code_r": 'library(MatchIt)\n'
                'm.out <- matchit(D ~ age + educ + prior, data = df,\n'
                '                 method = "nearest", distance = "glm",\n'
                '                 estimand = "ATT")\n'
                'md <- match.data(m.out)'},
            {"heading": "Step 3 · Check covariate balance (SMD before/after)",
             "body": "Compute the standardized mean difference for each covariate "
                "before and after matching; the love-plot stacks them. Aim for "
                "|SMD| < 0.1 after matching. In R, cobalt draws the love-plot.",
             "code_python": "def smd(a, b):\n"
                "    return (a.mean() - b.mean()) / np.sqrt(\n"
                "        (a.var(ddof=1) + b.var(ddof=1)) / 2)\n"
                "for c in ['age', 'educ', 'prior']:\n"
                "    before = smd(trt[c], ctl[c])\n"
                "    after  = smd(trt[c], matched_ctl[c])\n"
                "    print(f'{c:6s} SMD before={before:+.2f}  after={after:+.2f}')",
             "code_r": 'library(cobalt)\n'
                'bal.tab(m.out, un = TRUE)              # SMD before & after\n'
                'love.plot(m.out, thresholds = c(m = .1))   # the love-plot'},
            {"heading": "Step 4 · Estimate the ATT",
             "body": "The ATT is the mean within-pair outcome difference. Compare "
                "it to the naive (unadjusted) difference to see how much "
                "confounding you removed.",
             "code_python": "naive = trt['Y'].mean() - ctl['Y'].mean()\n"
                "att   = (trt['Y'].values - matched_ctl['Y'].values).mean()\n"
                "print(f'naive diff = {naive:.2f}')\n"
                "print(f'matched ATT = {att:.2f}')",
             "code_r": 'fit <- lm(Y ~ D, data = md, weights = weights)\n'
                'coef(fit)["D"]    # matched ATT'},
        ],
        "expected": "Before matching the covariate SMDs are large (well above 0.1) "
            "and the naive treated-minus-control difference is badly biased. After "
            "matching every SMD drops below ~0.1 and the ATT moves close to the "
            "true effect built into your simulation. Same data, two answers — and "
            "the balance table is what tells you to trust the matched one.",
        "submit": [
            "Push your code plus the before/after SMD table (or love-plot) for "
            "every covariate.",
            "Report the naive difference and the matched ATT, with one sentence on "
            "why they differ.",
            "Add one sentence on why your reported SE would understate uncertainty "
            "if you treated the matched sample as i.i.d.",
        ],
    },
    "self_check": [
        "State the propensity-score balancing property X ⟂ D | e(X) and explain "
        "it in one sentence.",
        "Compute an SMD by hand and say whether |SMD| = 0.07 is balanced.",
        "Explain what trimming to common support does to the estimand.",
        "Say why 1:1 matching targets the ATT, not the ATE.",
        "Give two reasons naive post-matching SEs are too small.",
    ],
    "next_week": {
        "heading": "Coming up: Week 7 — Weighting & doubly robust estimation",
        "teaser": "Instead of discarding units by matching, we reweight them by "
            "the inverse of their propensity score so the whole sample mimics a "
            "trial. Then we combine an outcome model with a weighting model into a "
            "doubly robust estimator that is consistent if EITHER model is right — "
            "and fixes the matching inference headaches from this week. Skim the "
            "IPW sections of Hernán & Robins to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 6", "items": [
            {"t": "The matching idea", "d": "Rebuild a randomized comparison by "
             "balancing covariates."},
            {"t": "Propensity score", "d": "e(X) = P(D|X) and its balancing "
             "property."},
            {"t": "Flavors of matching", "d": "Exact, coarsened, "
             "nearest-neighbor — and the knobs."},
            {"t": "Balance & overlap", "d": "SMDs, love-plots, common support, "
             "trimming."},
            {"t": "Estimand & inference", "d": "ATT vs ATE, and why naive SEs are "
             "wrong."},
            {"t": "The LaLonde case", "d": "Can matching recover the experimental "
             "benchmark?"},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Block II: adjustment for measured confounders", "bullets": [
            "Last week: regression and control — adjust by modeling the outcome.",
            "This week: matching & the propensity score — adjust by balancing the "
            "groups.",
            "Both assume unconfoundedness: (Y(0), Y(1)) ⟂ D | X for measured X.",
            ("Different tool, same target: remove confounding by measured "
             "covariates.", 1),
            "Next week: weighting & doubly robust — combine both, get a safety "
            "net.",
         ],
         "note": {"title": "The assumption that powers all of Block II",
            "body": "Unconfoundedness + positivity. If a confounder is not in X, "
            "no amount of matching can save you — that is what Block III is for."}},
        {"type": "statement",
         "quote": "Matching is a design step you can check before you ever look "
            "at the outcome.",
         "attribution": "Balance is judged on covariates alone. That separation — "
            "design first, outcome later — is what keeps matching honest and hard "
            "to fool yourself with."},

        {"type": "section", "kicker": "Part 1", "title": "The matching idea",
         "subtitle": "If treated and control units had the same covariate "
            "distribution, comparing their outcomes would be like a trial. So "
            "build a comparison group that does."},
        {"type": "content", "kicker": "Intuition",
         "title": "Compare like with like", "bullets": [
            "A naive treated−control difference mixes the treatment effect with "
            "pre-existing differences.",
            "Idea: for each treated unit, find control unit(s) with the same "
            "covariates.",
            "Within matched sets, X is balanced, so the outcome gap is (closer "
            "to) the causal effect.",
            "It is non-parametric in the outcome — no assumption that Y is linear "
            "in X.",
            ("You check the design (balance) before touching the outcome.", 1),
         ],
         "note": {"title": "Why not just regress?",
            "body": "Matching makes the comparison transparent and flags where "
            "there is simply no comparable control — regression silently "
            "extrapolates there."}},
        {"type": "compare", "kicker": "Two ways to adjust",
         "title": "Regression vs. matching", "columns": [
            {"head": "Regression (Week 5)", "points": [
                "Models E[Y | D, X] and reads off the D coefficient.",
                "Extrapolates into regions with no overlap.",
                "Leans on a functional form for Y."]},
            {"head": "Matching (this week)", "points": [
                "Builds a comparison group balanced on X.",
                "Makes lack of overlap visible and refusable.",
                "Non-parametric in the outcome; check balance first."]},
         ]},

        {"type": "section", "kicker": "Part 2", "title": "The propensity score",
         "subtitle": "Rosenbaum & Rubin's trick: collapse the whole covariate "
            "vector into one number you can match on."},
        {"type": "content", "kicker": "Definition",
         "title": "e(X) = P(D = 1 | X)", "bullets": [
            "The propensity score is the probability of treatment given "
            "covariates.",
            "Estimate it — logistic regression is the standard first choice.",
            "It is a one-dimensional summary of all confounders in X.",
            ("Curse of dimensionality: exact matching on many covariates is "
             "hopeless; one score is tractable.", 1),
         ],
         "note": {"title": "Judge it by balance",
            "body": "A good PS model is one that BALANCES covariates — not one "
            "with high classification accuracy. Different goal."}},
        {"type": "content", "kicker": "The theorem",
         "title": "The balancing property: X ⟂ D | e(X)", "bullets": [
            "Given the propensity score, covariates carry no extra info about "
            "treatment.",
            "So within a thin band of e(X), treated and control X look alike — a "
            "mini-randomized block.",
            "Conditioning on the scalar e(X) removes the same bias as "
            "conditioning on all of X.",
            "Match, stratify, or weight on e(X) — all exploit this one fact.",
         ],
         "note": {"title": "What it does NOT do",
            "body": "It only balances MEASURED X. Unmeasured confounders are "
            "untouched — the propensity score is not magic."}},
        {"type": "statement",
         "quote": "The propensity score is a means to balance, not an end.",
         "attribution": "You never interpret its coefficients. You fit it, match "
            "or weight on it, and then check whether the covariates actually "
            "balanced. If they didn't, change the model."},

        {"type": "section", "kicker": "Part 3", "title": "Flavors of matching",
         "subtitle": "From perfect-but-infeasible exact matching to the "
            "nearest-neighbor workhorse — plus the knobs that trade balance "
            "against sample size."},
        {"type": "table", "kicker": "A menu of methods",
         "title": "Matching methods at a glance",
         "headers": ["Method", "How it pairs", "Trade-off"],
         "rows": [
            ["Exact", "Identical covariate values",
             "Perfect balance; infeasible with continuous X"],
            ["Coarsened exact (CEM)", "Identical coarse bins",
             "Tunable balance vs. retained sample"],
            ["NN on the PS", "Closest propensity score",
             "Practical; balance depends on the PS model"],
            ["Caliper", "Closest PS within a max distance",
             "Drops bad matches; can change the estimand"],
         ],
         "note": {"title": "Default",
            "body": "1:1 nearest-neighbor on the estimated PS is the standard "
            "starting point — then refine with calipers or 1:k."}},
        {"type": "content", "kicker": "The knobs",
         "title": "Calipers, 1:k, and replacement", "bullets": [
            "Caliper: refuse a match if the PS distance exceeds a cap (often "
            "0.2 × SD of the logit).",
            "1:k matching: use k controls per treated unit — less variance, "
            "possibly worse balance.",
            "With replacement: reuse the best controls — better balance, but "
            "matched units are dependent.",
            ("Every knob trades bias (balance) against variance (effective sample "
             "size).", 1),
         ],
         "note": {"title": "No free lunch",
            "body": "Tighter calipers and 1:1 improve balance but shrink the "
            "sample. There is no setting that wins on every axis."}},

        {"type": "section", "kicker": "Part 4",
         "title": "Balance, overlap, and trimming",
         "subtitle": "After matching you audit the design: did the covariates "
            "actually balance, and is there a region where the groups simply do "
            "not overlap?"},
        {"type": "content", "kicker": "The diagnostic",
         "title": "Standardized mean difference (SMD)", "bullets": [
            "SMD = (mean_treated − mean_control) / pooled SD, per covariate.",
            "Scale-free, so you can compare age, income, and test scores on one "
            "axis.",
            "Rule of thumb: |SMD| < 0.1 is well balanced; 0.1–0.2 is marginal.",
            "Unlike a p-value it does not get 'better' just because n is large.",
         ],
         "note": {"title": "Love-plot",
            "body": "Plot each covariate's SMD before vs after matching. Points "
            "should march from the right (imbalanced) to near zero."}},
        {"type": "content", "kicker": "Positivity",
         "title": "Common support / overlap", "bullets": [
            "Positivity: 0 < e(X) < 1 for every covariate profile — both "
            "treatments are possible.",
            "Plot the PS distributions by group: where they don't overlap, there "
            "are no comparable units.",
            "Trimming drops the non-overlap region to restore comparability.",
            ("But trimming changes the population — you now estimate the effect "
             "for the trimmed sub-group.", 1),
         ],
         "note": {"title": "Honest refusal",
            "body": "Where there is no overlap, the data cannot answer the "
            "question. Trimming makes that refusal explicit instead of "
            "extrapolating."}},
        {"type": "compare", "kicker": "Which effect are we even estimating?",
         "title": "ATT vs. ATE under matching", "columns": [
            {"head": "ATT — effect on the treated", "sub": "E[Y(1)−Y(0) | D=1]",
             "points": [
                "Match a control to each treated unit.",
                "Needs overlap only on the treated side.",
                "The natural matching estimand."]},
            {"head": "ATE — effect on everyone", "sub": "E[Y(1)−Y(0)]", "points": [
                "Also needs a treated match for each control.",
                "Requires two-sided overlap.",
                "More fragile where a group is rare."]},
         ]},

        {"type": "section", "kicker": "Part 5", "title": "Inference after matching",
         "subtitle": "The estimate is the easy part. Getting an honest standard "
            "error is where most applied matching analyses go wrong."},
        {"type": "content", "kicker": "The trap",
         "title": "Why naive post-matching SEs are too small", "bullets": [
            "The propensity score was estimated from the same data — that "
            "uncertainty is ignored.",
            "Matching is itself random; treating the matched sample as fixed "
            "understates variance.",
            "With replacement, controls are reused, so matched units are "
            "dependent, not i.i.d.",
            "Matched-pair counts are random too — a paired t-test is not enough.",
         ],
         "note": {"title": "Symptom",
            "body": "Confidence intervals that are implausibly tight and "
            "'significant' results that don't replicate."}},
        {"type": "steps", "kicker": "What to do instead",
         "title": "Valid inference after matching", "steps": [
            {"title": "Abadie–Imbens", "body": "— a matching-aware variance "
             "estimator built for this design."},
            {"title": "Full-pipeline bootstrap", "body": "— resample, then REFIT "
             "the PS, rematch, and re-estimate each time."},
            {"title": "Go doubly robust", "body": "— pair matching/weighting with "
             "an outcome model; proper SEs (Week 7)."},
         ],
         "note": "The fix is to make inference account for the design — not to "
            "patch a formula that assumed i.i.d. data."},

        {"type": "section", "kicker": "Part 6", "title": "The LaLonde problem",
         "subtitle": "A famous stress test: can observational matching recover "
            "the answer from an actual randomized experiment?"},
        {"type": "steps", "kicker": "Case study · NSW vs. PSID",
         "title": "Does matching recover the experimental benchmark?", "steps": [
            {"title": "The experiment", "body": "The NSW job-training trial "
             "randomized treatment → a credible benchmark ATT (~$1,800)."},
            {"title": "Swap the controls", "body": "Replace the randomized "
             "controls with a PSID survey sample — now it is observational."},
            {"title": "Naive comparison", "body": "Trainees look far worse: the "
             "PSID controls are richer and very different on covariates."},
            {"title": "Match on the PS", "body": "With good overlap and balance, "
             "matching moves the estimate back toward the experimental benchmark."},
         ],
         "note": "Dehejia & Wahba (1999) revived the method; Smith & Todd (2005) "
            "showed it is fragile to specification and overlap. Both lessons "
            "matter."},
        {"type": "compare", "kicker": "The takeaway",
         "title": "When does matching work?", "columns": [
            {"head": "It can recover the benchmark when…", "points": [
                "The key confounders are measured (e.g. earnings history).",
                "There is real overlap in covariates.",
                "Balance is achieved and checked."]},
            {"head": "It fails when…", "points": [
                "Important confounders are unmeasured.",
                "The groups barely overlap.",
                "You skip balance checks and trust the PS model blindly."]},
         ]},
        {"type": "statement",
         "quote": "Estimate the PS → match → check balance → estimate the effect "
            "→ question your SEs.",
         "attribution": "That is the whole workflow. In lab you will run it "
            "end-to-end on simulated data with a known ATT and watch a badly "
            "biased difference snap back to the truth."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A confounded world with a KNOWN effect\n\n"
            "We simulate an observational study of a job-training-style program. "
            "Three covariates — `age`, `educ`, `prior` (earnings history) — drive "
            "**both** who gets treated (`D`) and the outcome (`Y`). We build in a "
            "**constant individual treatment effect of exactly 2.0**, so the true "
            "ATT and ATE are both `2.0` and we can check every estimate against "
            "the truth.\n\n"
            "Because the treated are systematically different (higher `prior`, "
            "etc.), the *naive* treated−control difference will be badly biased."},
        {"code": "from sklearn.linear_model import LogisticRegression\n"
            "from sklearn.neighbors import NearestNeighbors\n\n"
            "TRUE_EFFECT = 2.0          # constant individual effect we build in\n\n"
            "def simulate(n=4000):\n"
            "    age   = RNG.normal(0, 1, n)\n"
            "    educ  = RNG.normal(0, 1, n)\n"
            "    prior = 0.6*age - 0.4*educ + RNG.normal(0, 1, n)   # earnings history\n"
            "    # confounders push the probability of treatment\n"
            "    logit = 0.8*age - 0.7*educ + 0.6*prior\n"
            "    ps_true = 1 / (1 + np.exp(-logit))\n"
            "    D = RNG.binomial(1, ps_true)\n"
            "    # potential outcomes; Y(1) = Y(0) + TRUE_EFFECT for everyone\n"
            "    Y0 = 1.0 + 1.2*age - 0.9*educ + 1.1*prior + RNG.normal(0, 1, n)\n"
            "    Y1 = Y0 + TRUE_EFFECT\n"
            "    Y  = np.where(D == 1, Y1, Y0)\n"
            "    return pd.DataFrame({'age': age, 'educ': educ, 'prior': prior,\n"
            "                         'D': D, 'Y': Y, 'Y0': Y0, 'Y1': Y1})\n\n"
            "df = simulate()\n"
            "# The ATT is computable here because we know both potential outcomes.\n"
            "TRUE_ATT = (df.loc[df.D==1, 'Y1'] - df.loc[df.D==1, 'Y0']).mean()\n"
            "print(f'treated n = {int(df.D.sum())},  control n = {int((1-df.D).sum())}')\n"
            "print(f'TRUE ATT  = {TRUE_ATT:.3f}   (built in as {TRUE_EFFECT})')"},
        {"md": "### The naive estimate is biased\n\n"
            "Just subtract the group means. Because treated units started with "
            "higher `prior` (and other confounders), this **overstates** the "
            "effect — it credits pre-existing advantages to the program."},
        {"code": "naive = df.loc[df.D==1, 'Y'].mean() - df.loc[df.D==0, 'Y'].mean()\n"
            "print(f'naive difference = {naive:.3f}')\n"
            "print(f'true ATT         = {TRUE_ATT:.3f}')\n"
            "print(f'bias             = {naive - TRUE_ATT:+.3f}   (large!)')\n"
            "assert naive - TRUE_ATT > 1.0, 'the naive estimate should be badly biased'"},
        {"md": "## 2 · Fit a propensity score\n\n"
            "Estimate `e(X) = P(D=1 | X)` with `LogisticRegression`. Remember: we "
            "judge this model by the **balance** it buys, not its accuracy."},
        {"code": "covs = ['age', 'educ', 'prior']\n"
            "X = df[covs].values\n"
            "ps_model = LogisticRegression(max_iter=1000).fit(X, df['D'].values)\n"
            "df['ps'] = ps_model.predict_proba(X)[:, 1]\n"
            "# logit of the PS — the scale on which we usually set calipers\n"
            "df['logit_ps'] = np.log(df['ps'] / (1 - df['ps']))\n"
            "print(df.groupby('D')['ps'].describe()[['mean', 'min', 'max']])"},
        {"md": "## 3 · Overlap and balance — *before* matching\n\n"
            "Two design checks, done before we touch the outcome again.\n\n"
            "**(a) Overlap.** Plot the PS distribution in each group. Where they "
            "don't overlap, there are no comparable units.\n\n"
            "**(b) Balance.** The standardized mean difference (SMD) per covariate."},
        {"code": "fig, ax = plt.subplots()\n"
            "ax.hist(df.loc[df.D==1, 'ps'], bins=30, alpha=0.6, density=True,\n"
            "        label='treated')\n"
            "ax.hist(df.loc[df.D==0, 'ps'], bins=30, alpha=0.6, density=True,\n"
            "        label='control')\n"
            "ax.set_xlabel('propensity score  e(X)'); ax.set_ylabel('density')\n"
            "ax.set_title('Overlap of the propensity score by group')\n"
            "ax.legend()\n"
            "# Treated mass sits to the right — but the supports do overlap.\n"
            "print('PS overlap region:',\n"
            "      f\"[{max(df[df.D==1].ps.min(), df[df.D==0].ps.min()):.3f},\",\n"
            "      f\"{min(df[df.D==1].ps.max(), df[df.D==0].ps.max()):.3f}]\")"},
        {"code": "def smd(a, b):\n"
            "    \"\"\"Standardized mean difference: mean gap / pooled SD.\"\"\"\n"
            "    return (a.mean() - b.mean()) / np.sqrt(\n"
            "        (a.var(ddof=1) + b.var(ddof=1)) / 2)\n\n"
            "trt = df[df.D == 1]; ctl = df[df.D == 0]\n"
            "smd_before = {c: smd(trt[c], ctl[c]) for c in covs}\n"
            "print('SMD before matching (|SMD| < 0.1 is the goal):')\n"
            "for c in covs:\n"
            "    print(f'  {c:6s} {smd_before[c]:+.3f}')\n"
            "assert max(abs(v) for v in smd_before.values()) > 0.3, \\\n"
            "    'covariates should be clearly imbalanced before matching'"},
        {"md": "## 4 · 1:1 nearest-neighbor matching on the PS → the ATT\n\n"
            "Match each treated unit to the control with the closest propensity "
            "score (`NearestNeighbors`). This targets the **ATT**. The ATT is then "
            "the mean within-pair outcome difference — and it should land near "
            "`2.0`."},
        {"code": "trt = df[df.D == 1].copy()\n"
            "ctl = df[df.D == 0].copy()\n"
            "nn = NearestNeighbors(n_neighbors=1).fit(ctl[['ps']].values)\n"
            "_, idx = nn.kneighbors(trt[['ps']].values)\n"
            "matched_ctl = ctl.iloc[idx.ravel()].copy()\n\n"
            "att_match = (trt['Y'].values - matched_ctl['Y'].values).mean()\n"
            "print(f'matched ATT = {att_match:.3f}')\n"
            "print(f'true ATT    = {TRUE_ATT:.3f}')\n"
            "print(f'naive       = {naive:.3f}   (for contrast)')\n"
            "assert abs(att_match - TRUE_ATT) < 0.15, \\\n"
            "    'matching should recover the true ATT within 0.15'"},
        {"md": "### Balance *after* matching (the love-plot idea)\n\n"
            "Recompute the SMDs on the matched sample. They should collapse toward "
            "zero — that is the love-plot: every covariate marching from imbalanced "
            "to balanced."},
        {"code": "smd_after = {c: smd(trt[c], matched_ctl[c]) for c in covs}\n\n"
            "y = np.arange(len(covs))\n"
            "fig, ax = plt.subplots()\n"
            "ax.scatter([abs(smd_before[c]) for c in covs], y, label='before', s=70)\n"
            "ax.scatter([abs(smd_after[c])  for c in covs], y, label='after', s=70)\n"
            "ax.axvline(0.1, ls='--', color='grey')   # |SMD| = 0.1 threshold\n"
            "ax.set_yticks(y); ax.set_yticklabels(covs)\n"
            "ax.set_xlabel('|standardized mean difference|')\n"
            "ax.set_title('Love-plot: covariate balance before vs after matching')\n"
            "ax.legend()\n\n"
            "print('covariate   before    after')\n"
            "for c in covs:\n"
            "    print(f'  {c:6s} {smd_before[c]:+.3f}   {smd_after[c]:+.3f}')\n"
            "assert max(abs(v) for v in smd_after.values()) < 0.15, \\\n"
            "    'matching should bring every SMD near zero'"},
        {"md": "## 5 · Trimming the non-overlap region\n\n"
            "Restrict to the **common support** — the PS range where both groups "
            "appear — and re-estimate. Here overlap is already good, so trimming "
            "drops only a few units and barely moves the ATT; the point is the "
            "*mechanic* and that trimming changes which units (hence which "
            "population) you analyze."},
        {"code": "lo = max(trt['ps'].min(), ctl['ps'].min())\n"
            "hi = min(trt['ps'].max(), ctl['ps'].max())\n"
            "on_support = df[(df.ps >= lo) & (df.ps <= hi)].copy()\n"
            "print(f'common support PS in [{lo:.3f}, {hi:.3f}]')\n"
            "print(f'kept {len(on_support)} of {len(df)} units '\n"
            "      f'({len(df) - len(on_support)} trimmed)')\n\n"
            "t2 = on_support[on_support.D == 1]; c2 = on_support[on_support.D == 0]\n"
            "nn2 = NearestNeighbors(n_neighbors=1).fit(c2[['ps']].values)\n"
            "_, idx2 = nn2.kneighbors(t2[['ps']].values)\n"
            "att_trim = (t2['Y'].values - c2.iloc[idx2.ravel()]['Y'].values).mean()\n"
            "print(f'ATT after trimming = {att_trim:.3f}  (vs untrimmed {att_match:.3f})')\n"
            "assert abs(att_trim - TRUE_ATT) < 0.2"},
        {"md": "### 🔧 Exercise 5.1 — caliper matching on the logit\n\n"
            "A **caliper** refuses any match whose propensity-score distance is too "
            "large, dropping low-quality pairs. The standard caliper is "
            "`0.2 × SD(logit(ps))`.\n\n"
            "Match each treated unit to its nearest control **on `logit_ps`**, then "
            "keep only pairs within the caliper, and estimate the ATT on the kept "
            "pairs. Fill in the `# TODO`s."},
        {"code": "# TODO: build a caliper match on the logit of the propensity score.\n"
            "caliper = 0.2 * df['logit_ps'].std()\n"
            "print(f'caliper = {caliper:.3f} (on the logit scale)')\n\n"
            "# nn_l = NearestNeighbors(n_neighbors=1).fit(...)      # fit on ctl logit_ps\n"
            "# dist, idx_l = nn_l.kneighbors(...)                   # query trt logit_ps\n"
            "# keep = ...               # boolean: dist within the caliper\n"
            "# att_caliper = ...        # mean within-pair diff over KEPT pairs\n"
            "# print(att_caliper, 'matched', int(keep.sum()), 'of', len(trt))\n"
            "att_caliper = ...   # placeholder so the notebook still runs"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "nn_l = NearestNeighbors(n_neighbors=1).fit(ctl[['logit_ps']].values)\n"
            "dist, idx_l = nn_l.kneighbors(trt[['logit_ps']].values)\n"
            "dist = dist.ravel(); idx_l = idx_l.ravel()\n"
            "keep = dist <= caliper\n\n"
            "matched_y = ctl.iloc[idx_l]['Y'].values\n"
            "att_caliper = (trt['Y'].values[keep] - matched_y[keep]).mean()\n"
            "print(f'caliper ATT = {att_caliper:.3f}   '\n"
            "      f'(kept {int(keep.sum())} of {len(trt)} treated)')\n"
            "print(f'true ATT    = {TRUE_ATT:.3f}')\n"
            "assert abs(att_caliper - TRUE_ATT) < 0.2, 'caliper match should recover ~2.0'"},
        {"md": "### 🔧 Exercise 5.2 — a second estimator: IPW for the ATT\n\n"
            "Matching is not the only way to use the propensity score. **Inverse-"
            "probability weighting** for the ATT keeps treated units at weight 1 and "
            "weights each control by `e(X) / (1 − e(X))`, so the reweighted controls "
            "mimic the treated group's covariate distribution.\n\n"
            "Estimate the ATT as `mean(Y | treated) − weighted_mean(Y | control)` "
            "and check it also recovers `2.0`. (This previews Week 7.)"},
        {"code": "# TODO: ATT via inverse-probability weighting.\n"
            "# odds = df['ps'] / (1 - df['ps'])      # the control weights\n"
            "# treated_mean = ...                    # plain mean of treated Y\n"
            "# control_wmean = ...                   # weighted mean of control Y, weights=odds\n"
            "# att_ipw = treated_mean - control_wmean\n"
            "# print(att_ipw)\n"
            "att_ipw = ...   # placeholder so the notebook still runs"},
        {"md": "### ✅ Solution 5.2"},
        {"code": "odds = (df['ps'] / (1 - df['ps'])).values\n"
            "is_t = df['D'].values == 1\n"
            "treated_mean  = df['Y'].values[is_t].mean()\n"
            "control_wmean = np.average(df['Y'].values[~is_t], weights=odds[~is_t])\n"
            "att_ipw = treated_mean - control_wmean\n"
            "print(f'IPW ATT  = {att_ipw:.3f}')\n"
            "print(f'true ATT = {TRUE_ATT:.3f}')\n"
            "assert abs(att_ipw - TRUE_ATT) < 0.2, 'IPW should also recover ~2.0'"},
        {"md": "### 🔧 Exercise 5.3 — naive SEs are too small\n\n"
            "Here we *demonstrate* the inference warning. The honest way to get a "
            "matching SE is to bootstrap the **whole pipeline**: resample the data, "
            "refit the PS, rematch, re-estimate. Compare the spread of those "
            "bootstrap ATTs to a naive within-pair SE.\n\n"
            "Implement the full-pipeline bootstrap below."},
        {"code": "# TODO: full-pipeline bootstrap of the ATT.\n"
            "def matched_att(data):\n"
            "    \"\"\"Refit PS, 1:1 match, return ATT for a dataframe.\"\"\"\n"
            "    Xb = data[covs].values\n"
            "    psb = LogisticRegression(max_iter=1000).fit(Xb, data['D'].values)\\\n"
            "             .predict_proba(Xb)[:, 1]\n"
            "    d = data.assign(ps=psb)\n"
            "    t, c = d[d.D == 1], d[d.D == 0]\n"
            "    j = NearestNeighbors(n_neighbors=1).fit(c[['ps']].values)\\\n"
            "          .kneighbors(t[['ps']].values, return_distance=False).ravel()\n"
            "    return (t['Y'].values - c.iloc[j]['Y'].values).mean()\n\n"
            "B = 200\n"
            "# boot = np.array([matched_att(df.sample(len(df), replace=True,\n"
            "#                 random_state=int(RNG.integers(1e9)))) for _ in range(B)])\n"
            "# boot_se = boot.std(ddof=1)\n"
            "boot_se = ...   # placeholder so the notebook still runs"},
        {"md": "### ✅ Solution 5.3"},
        {"code": "B = 200\n"
            "boot = np.array([\n"
            "    matched_att(df.sample(len(df), replace=True,\n"
            "                          random_state=int(RNG.integers(1_000_000_000))))\n"
            "    for _ in range(B)])\n"
            "boot_se = boot.std(ddof=1)\n\n"
            "# A naive within-pair SE treats matched pairs as i.i.d. observations.\n"
            "pair_diff = trt['Y'].values - matched_ctl['Y'].values\n"
            "naive_se = pair_diff.std(ddof=1) / np.sqrt(len(pair_diff))\n\n"
            "print(f'bootstrap (full-pipeline) SE = {boot_se:.3f}')\n"
            "print(f'naive within-pair SE         = {naive_se:.3f}')\n"
            "print(f'ratio = {boot_se / naive_se:.2f}x')\n"
            "assert boot_se > naive_se, \\\n"
            "    'the naive SE understates uncertainty vs the full-pipeline bootstrap'"},
        {"md": "## 6 · Wrap-up & self-check\n\n"
            "- The naive treated−control difference was badly biased "
            "(confounding).\n"
            "- The **propensity score** `e(X)=P(D|X)` is a *balancing score*: "
            "matching on one number balanced all three covariates "
            "(SMDs → near 0).\n"
            "- **1:1 NN matching on the PS** recovered the true ATT of `2.0`; so "
            "did **caliper matching** and **IPW** — three roads, one estimand.\n"
            "- **Trimming** to common support enforces overlap but changes the "
            "population you analyze.\n"
            "- **Naive post-matching SEs are too small**: the full-pipeline "
            "bootstrap gave a larger, honest SE.\n\n"
            "**You're ready for Week 7** if you can state the balancing property, "
            "read a love-plot, and say why matching targets the ATT. Next week: "
            "weighting & doubly robust estimation — keep every unit, reweight the "
            "sample, and get a method that is right if *either* model is."},
    ],
}
