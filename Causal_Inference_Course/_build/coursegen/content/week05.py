# -*- coding: utf-8 -*-
"""Week 5 — Regression & Adjustment. Block II content module."""

WEEK = {
    "number": 5,
    "slug": "regression_adjustment",
    "title": "Regression & Adjustment",
    "block": "Block II — Adjustment for confounding",
    "subtitle": "What regression can and cannot do for causation — and the "
                "precise ways that \"controlling for\" backfires.",
    "deliverable": "Problem Set 4 — classify every control (good/bad/collider/"
                   "neutral/M-bias); Workshop 5 — good & bad controls in code.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab/workshop (2–3h).",
    "one_sentence": "OLS estimates a causal effect only when you condition on the "
        "right set of covariates — and 'the right set' is dictated by the causal "
        "graph, not by what improves fit, because adjusting for mediators or "
        "colliders manufactures bias that wasn't there.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Explain regression as a covariate-adjusted, weighted-average matching "
        "estimator, and state the conditional independence assumption it needs.",
        "Given a DAG, classify each covariate as a good control (confounder), a "
        "bad control (mediator), a collider, a neutral control, or an M-bias "
        "trap — and give an adjust / don't-adjust verdict with justification.",
        "Explain the Table 2 fallacy and why a regression coefficient on a "
        "covariate is not, in general, that covariate's own causal effect.",
        "Show in code that adjusting for a confounder removes bias while adjusting "
        "for a mediator or a collider introduces it, comparing each estimate to a "
        "known ground truth.",
        "Fit and interpret an interaction term to recover an effect that differs "
        "across subgroups (effect modification).",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Angrist & Pischke, Mostly Harmless Econometrics — Chapter 3.",
         "look_for": "regression as a weighted-average matching estimator and the "
                     "conditional independence assumption that makes its slope "
                     "causal."},
        {"text": "Cinelli, Forney & Pearl, \"A Crash Course in Good and Bad "
                 "Controls\".",
         "look_for": "the taxonomy of controls — which ones remove bias, which "
                     "ones add it, and the surprising cases (M-bias, neutral "
                     "controls that only affect variance)."},
    ],
    "optional_readings": [
        {"text": "Huntington-Klein, The Effect — Chapters 4–6.",
         "note": "A gentle, example-driven treatment of regression as description "
                 "vs. as causal adjustment, and of good vs. bad controls."},
        {"text": "Westreich & Greenland, \"The Table 2 Fallacy\" (Am. J. "
                 "Epidemiol., 2013).",
         "note": "The original short paper naming the mistake of reading every "
                 "coefficient in a model as a causal effect."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "OLS is covariate-adjusted comparison",
         "body": "Regressing Y on a treatment X and covariates Z gives a slope on "
            "X that is a weighted average of within-stratum X–Y comparisons — "
            "roughly, it compares units with similar Z. Under the conditional "
            "independence assumption (CIA), that Y(0), Y(1) ⫫ X | Z, this "
            "weighted average equals the causal effect of X. So OLS is a "
            "matching/adjustment estimator in disguise: it 'controls for' Z by "
            "comparing like with like. The whole question is whether the Z you put "
            "in the model is the Z that makes the CIA true."},
        {"heading": "The conditional expectation function (CEF)",
         "body": "Regression's population target is the CEF, E[Y | X, Z] — the "
            "best predictor of Y given the regressors, and OLS is its best linear "
            "approximation. Prediction lives entirely here. But the CEF is a fact "
            "about the observed distribution; turning a CEF slope into a causal "
            "effect requires the extra, untestable assumption that you have "
            "adjusted for all confounders and for nothing on the causal path."},
        {"heading": "Omitted-variable bias and what 'controlling for X' means",
         "body": "Leave out a confounder and the slope on X absorbs the back-door "
            "path: bias = (effect of the omitted variable on Y) × (its regression "
            "relationship with X). 'Controlling for X' literally means partialling "
            "it out — regressing both the treatment and the outcome on X and "
            "relating the residuals (Frisch–Waugh–Lovell). That is exactly right "
            "for a confounder and exactly wrong for a mediator or collider."},
        {"heading": "Good controls vs. bad controls",
         "bullets": [
            [("Good control (confounder)  Z → X, Z → Y. ", {"bold": True}),
             ("A common cause; opens a back-door path. Adjust — it removes bias.",
              {})],
            [("Bad control (mediator)  X → M → Y. ", {"bold": True}),
             ("On the causal path. Adjusting blocks part of the effect you want. "
              "Don't adjust (for the total effect).", {})],
            [("Collider  X → K ← Y  (or descendant). ", {"bold": True}),
             ("A common effect. Already blocked; adjusting OPENS a spurious path. "
              "Don't adjust.", {})],
            [("Neutral control  Z → Y only (not → X). ", {"bold": True}),
             ("Off the back-door. Harmless for bias and can reduce variance — but "
              "a predictor of X-only inflates variance instead.", {})],
         ],
         "callout": {"title": "The single most common mistake in applied work",
            "color": "RED",
            "lines": ["'Throw every available covariate into the regression and "
                      "report the X coefficient.' Mediators and colliders punish "
                      "that habit, turning an unbiased estimate into a biased one.",
                      "The graph — not the R² or the p-values — tells you which "
                      "covariates belong in the model."]}},
        {"heading": "The Table 2 fallacy",
         "body": "A single regression of Y on treatment X and confounders "
            "Z₁, Z₂, … produces a coefficient for every regressor. The Table 2 "
            "fallacy is reading each of those coefficients as the causal effect of "
            "that variable. It is not. The X coefficient may be the causal effect "
            "of X (if Z is the right adjustment set for X), but the coefficient on "
            "a confounder Z is adjusted for X — and X may be a mediator on Z's own "
            "path to Y. One model cannot deliver every variable's causal effect "
            "simultaneously; each effect has its own adjustment set.",
         "callout": {"title": "Read your own regression table correctly",
            "color": "AMBER",
            "lines": ["The coefficient you designed the model around may be "
                      "causal; the other coefficients in the same row of the "
                      "output are, in general, NOT.",
                      "If you want the effect of Z, build the model for Z — a "
                      "different adjustment set, possibly a different sample."]}},
        {"heading": "Collider & mediator bias from over-adjustment",
         "body": "Two ways 'controlling for more' backfires. Conditioning on a "
            "mediator removes the very effect you set out to measure (and, if the "
            "mediator shares an unmeasured cause with Y, can even flip the sign). "
            "Conditioning on a collider — or anything downstream of one, including "
            "a variable affected by both treatment and outcome — opens a path and "
            "creates association from nothing. The birth-weight 'paradox' is the "
            "textbook cautionary tale: stratifying on birth weight (a collider "
            "between maternal smoking and unmeasured causes of infant mortality) "
            "makes smoking look protective for low-birth-weight infants."},
        {"heading": "Interaction & effect modification",
         "body": "A single slope assumes one effect for everyone. When the effect "
            "of X on Y differs by a subgroup variable G — the drug helps the old "
            "more than the young — that is effect modification, and a model with "
            "only X and G will report an average that fits no one. Adding an X×G "
            "interaction lets each subgroup have its own slope and recovers the "
            "conditional effects. Effect modification (G changes the size of X's "
            "effect) is distinct from confounding (G biases X's effect); a "
            "variable can do one, both, or neither."},
    ],
    "problem_set": {
        "label": "Problem Set 4",
        "title": "Classify every control",
        "intro": "For each scenario: (a) sketch the DAG, (b) classify the named "
            "covariate as a good control (confounder), a bad control (mediator), a "
            "collider, a neutral control, or an M-bias trap, (c) give the "
            "adjust / don't-adjust verdict for estimating the total effect of X on "
            "Y, and (d) justify it in one sentence from the structure. Try all "
            "five before you look.",
        "problems": [
            {"title": "Smoking, exercise, and heart disease",
             "prompt": "You estimate the effect of regular exercise (X) on heart "
                "disease (Y). Age (Z) makes people both less likely to exercise "
                "and more likely to develop heart disease. Classify age and give "
                "the verdict.",
             "solution_title": "Age is a confounder (good control) — adjust.",
             "solution": [
                "DAG: Age → Exercise, Age → Heart disease, with the exercise → "
                "disease arrow in question.",
                "Age is a common cause of treatment and outcome, opening the "
                "back-door path Exercise ← Age → Disease that masquerades as an "
                "exercise effect.",
                "Adjusting for age closes that path and isolates the exercise "
                "effect. The textbook good control."]},
            {"title": "The drug that works through blood pressure",
             "prompt": "A drug (X) lowers stroke risk (Y) by lowering blood "
                "pressure (M), and lower blood pressure reduces strokes. You want "
                "the TOTAL effect of the drug on stroke. A reviewer asks you to "
                "'control for blood pressure.' Classify M and give the verdict.",
             "solution_title": "Blood pressure is a mediator (bad control) — do "
                "not adjust (for the total effect).",
             "solution": [
                "DAG: Drug → Blood pressure → Stroke (possibly plus a direct "
                "Drug → Stroke arrow).",
                "Blood pressure lies ON the causal path; adjusting for it blocks "
                "the drug's main route and leaves only any direct effect, badly "
                "understating the drug.",
                "Keep it unadjusted for the total effect; condition on it only if "
                "you specifically want the direct effect (mediation analysis)."]},
            {"title": "Admission to the study (a collider)",
             "prompt": "You study whether a genetic marker (X) affects disease "
                "severity (Y). Your sample is patients enrolled in a specialty "
                "clinic; both the marker and severe disease independently raise "
                "the chance of being referred there (S = referred). A colleague "
                "suggests adjusting for referral status. Classify S and give the "
                "verdict.",
             "solution_title": "Referral is a collider — do not adjust (and beware "
                "you already conditioned on it by sampling).",
             "solution": [
                "DAG: Marker → Referral ← Severity (referral is a common EFFECT of "
                "both).",
                "In the full population the path X → Referral ← Y is blocked. "
                "Conditioning on referral — by adjusting OR by sampling only "
                "referred patients — opens it and manufactures a marker–severity "
                "association (selection / Berkson bias).",
                "Do not adjust; better, fix the design by sampling from the "
                "population rather than from the clinic."]},
            {"title": "A pure outcome predictor (neutral control)",
             "prompt": "In a randomized A/B test of a checkout flow (X) on "
                "purchase (Y), you have each user's pre-experiment 7-day spend (Z). "
                "Because the flow was randomized, Z does not affect assignment, "
                "but it strongly predicts purchasing. Classify Z and give the "
                "verdict.",
             "solution_title": "Z is a neutral control (good for precision) — "
                "adjusting is optional and helpful.",
             "solution": [
                "DAG: X randomized (no arrow into X), Z → Y, no Z → X edge. Z is "
                "off every back-door path.",
                "Adjusting for Z cannot remove bias (there is none) and cannot "
                "create it; because Z explains outcome variance, it tightens the "
                "estimate — the logic behind CUPED-style covariate adjustment.",
                "Verdict: adjust if you like (lower variance); your point estimate "
                "stays unbiased either way. Contrast a predictor of X-only, which "
                "would only inflate variance."]},
            {"title": "The tempting pre-treatment variable (M-bias)",
             "prompt": "You study X → Y. A measured variable Z is recorded before "
                "treatment. Unknown to you, Z is caused by two hidden variables: "
                "U₁ (which also causes X) and U₂ (which also causes Y), with no "
                "other connections. A colleague says 'it's pre-treatment, control "
                "for it to be safe.' Classify Z and give the verdict.",
             "solution_title": "Z is a collider (M-bias) — do not adjust, despite "
                "being pre-treatment.",
             "solution": [
                "DAG: U₁ → Z ← U₂, with U₁ → X and U₂ → Y. The shape is the "
                "letter M.",
                "Z is a common effect of U₁ and U₂. Left alone, the path "
                "X ← U₁ → Z ← U₂ → Y is blocked at the collider Z and carries no "
                "bias.",
                "Adjusting for Z opens that path and INTRODUCES confounding bias "
                "that was not there. 'Pre-treatment' does not mean 'safe to control "
                "for' — structure, not timing, decides."]},
            {"title": "The Table 2 fallacy & the birth-weight paradox",
             "prompt": "You fit one model of infant mortality (Y) on maternal "
                "smoking (X) and birth weight (BW), reporting both coefficients. "
                "Smoking lowers birth weight; birth weight and mortality also share "
                "unmeasured causes (e.g. birth defects). (a) Can you read the BW "
                "coefficient as BW's causal effect? (b) Why does smoking look "
                "protective among low-birth-weight babies?",
             "solution_title": "(a) No — Table 2 fallacy. (b) Conditioning on "
                "birth weight (a collider) creates the 'paradox.'",
             "solution": [
                "DAG: Smoking → BW, Smoking → Mortality, plus U (defects) → BW and "
                "U → Mortality. BW is a mediator of smoking AND a collider on "
                "Smoking ← BW → U → Mortality once you condition on it.",
                "(a) The smoking coefficient is adjusted for BW — a mediator — so "
                "it is neither the total effect of smoking nor the causal effect "
                "of BW. Reading both coefficients off one table is the Table 2 "
                "fallacy; each variable needs its own adjustment set.",
                "(b) Stratifying on low birth weight conditions on the collider BW, "
                "opening Smoking ← BW ← U → Mortality. Among low-BW infants, a "
                "non-smoking mother's baby is more likely low-weight for a worse "
                "reason (defects), so smokers' low-BW babies fare better — smoking "
                "looks protective. Don't adjust for birth weight."]},
        ],
    },
    "lab": {
        "label": "Workshop 5",
        "title": "Good & bad controls",
        "goal": "build one simulated system and watch, in code, how adjusting for "
            "a good control removes bias while adjusting for a bad control "
            "(mediator) or a collider adds it — then demonstrate the Table 2 "
            "fallacy on the same fit. Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Simulate a system with a known truth",
             "body": "Build a world with a confounder Z, a mediator M, and a "
                "collider K. The TRUE total effect of X on Y is exactly 2. Keep "
                "the data so you can re-run several regressions on it.",
             "code_r": "set.seed(5)\nn  <- 8000\n"
                "Z  <- rnorm(n)                      # confounder: Z -> X, Z -> Y\n"
                "X  <- 0.9*Z + rnorm(n)              # treatment\n"
                "Y  <- 2*X + 1.5*Z + rnorm(n)        # TRUE total effect of X is 2\n"
                "M  <- 1.2*X + rnorm(n)              # mediator: X -> M (-> nothing extra here)\n"
                "K  <- 1.0*X + 1.0*Y + rnorm(n)      # collider: X -> K <- Y",
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(5)\nn = 8000\n"
                "Z = rng.normal(size=n)                 # confounder: Z->X, Z->Y\n"
                "X = 0.9*Z + rng.normal(size=n)         # treatment\n"
                "Y = 2*X + 1.5*Z + rng.normal(size=n)   # TRUE total effect is 2\n"
                "M = 1.2*X + rng.normal(size=n)         # mediator on X's path\n"
                "K = 1.0*X + 1.0*Y + rng.normal(size=n) # collider: X->K<-Y"},
            {"heading": "Step 2 · Good control: adjust for the confounder",
             "body": "Compare the naive slope on X to the slope after adjusting "
                "for Z. The good control should pull the estimate to ~2.",
             "code_r": 'naive <- coef(lm(Y ~ X))["X"]\n'
                'good  <- coef(lm(Y ~ X + Z))["X"]\n'
                'cat(sprintf("naive=%.2f  +Z=%.2f  (truth 2)\\n", naive, good))',
             "code_python": "naive = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
                "good  = sm.OLS(Y, sm.add_constant(np.c_[X, Z])).fit().params[1]\n"
                'print(f"naive={naive:.2f}  +Z={good:.2f}  (truth 2)")'},
            {"heading": "Step 3 · Bad controls: mediator and collider add bias",
             "body": "Now adjust additionally for the mediator M, then for the "
                "collider K. Both move the estimate AWAY from 2 — over-adjustment "
                "is not 'being careful', it is introducing bias.",
             "code_r": 'badM <- coef(lm(Y ~ X + Z + M))["X"]\n'
                'badK <- coef(lm(Y ~ X + Z + K))["X"]\n'
                'cat(sprintf("+Z+M(mediator)=%.2f  +Z+K(collider)=%.2f  '
                '(truth 2)\\n", badM, badK))',
             "code_python": "badM = sm.OLS(Y, sm.add_constant(np.c_[X, Z, M])).fit().params[1]\n"
                "badK = sm.OLS(Y, sm.add_constant(np.c_[X, Z, K])).fit().params[1]\n"
                'print(f"+Z+M(mediator)={badM:.2f}  +Z+K(collider)={badK:.2f}  '
                '(truth 2)")'},
            {"heading": "Step 4 · The Table 2 fallacy",
             "body": "In the correct model Y ~ X + Z, the coefficient on the "
                "confounder Z is NOT Z's own total causal effect on Y. Z's total "
                "effect runs partly through X (Z → X → Y), so reading the Z "
                "coefficient as Z's effect understates it. Compute Z's true total "
                "effect and compare.",
             "code_r": 'cZ <- coef(lm(Y ~ X + Z))["Z"]          # coefficient in the model\n'
                'totZ <- coef(lm(Y ~ Z))["Z"]                  # Z total effect (no X)\n'
                'cat(sprintf("Z coef in model=%.2f  vs Z true total=%.2f\\n", cZ, totZ))',
             "code_python": "cZ   = sm.OLS(Y, sm.add_constant(np.c_[X, Z])).fit().params[2]\n"
                "totZ = sm.OLS(Y, sm.add_constant(Z)).fit().params[1]\n"
                'print(f"Z coef in model={cZ:.2f}  vs Z true total={totZ:.2f}")\n'
                "# direct(1.5) via model; total ~ 1.5 + 0.9*2 = 3.3 — different numbers."},
        ],
        "expected": "Naive ≈ 2.7 (Z's effect leaks into X); +Z ≈ 2.0 (good "
            "control fixes it). Adding the mediator M crushes the estimate toward "
            "0, and adding the collider K biases it the other way — both are worse "
            "than not adjusting. In Step 4 the in-model Z coefficient (~1.5, the "
            "direct effect) is visibly smaller than Z's true total effect (~3.3): "
            "same regression, but you cannot read every coefficient as a causal "
            "effect. That contrast is the Table 2 fallacy.",
        "submit": [
            "Push your code and a short README reporting the five numbers (naive, "
            "+Z, +Z+M, +Z+K, and the two Z numbers) with one sentence each on why "
            "they differ.",
            "Add one paragraph: which covariates would you put in the model to "
            "estimate the effect of X, and why M and K are excluded.",
            "Bring your active-reading sentences (from the guided reading) to lab.",
        ],
    },
    "self_check": [
        "Explain regression as a matching/weighted-average estimator and state "
        "the conditional independence assumption it needs.",
        "Glance at a DAG and call each covariate good control / mediator / "
        "collider / neutral / M-bias, with the adjust verdict.",
        "Say why a regression coefficient on a confounder is not that variable's "
        "causal effect (the Table 2 fallacy).",
        "Reproduce, from memory, the result that adjusting for a mediator or "
        "collider moves an estimate away from the truth.",
        "Recover a subgroup-specific effect with an interaction term.",
    ],
    "next_week": {
        "heading": "Coming up: Week 6 — Matching & propensity scores",
        "teaser": "Regression adjusts by modeling the outcome; matching adjusts by "
            "rebuilding a comparable control group. We'll meet exact and "
            "nearest-neighbor matching, the propensity score as a one-number "
            "summary of all confounders, and balance diagnostics that tell you "
            "whether 'like is being compared with like.' Skim the matching "
            "chapter to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 5", "items": [
            {"t": "Regression as adjustment", "d": "OLS is a weighted-average "
             "matching estimator under the CIA."},
            {"t": "The CEF", "d": "Regression's target is E[Y|X,Z]; causation "
             "needs more than fit."},
            {"t": "Omitted-variable bias", "d": "What 'controlling for X' really "
             "does — and doesn't."},
            {"t": "Good vs. bad controls", "d": "A taxonomy: confounder, mediator, "
             "collider, neutral."},
            {"t": "The Table 2 fallacy", "d": "A coefficient is not the same as a "
             "causal effect."},
            {"t": "Interaction & a real case", "d": "Effect modification, and the "
             "birth-weight paradox."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Block II — adjusting for confounding", "bullets": [
            "Last block we defined the problem; now we estimate effects by "
            "comparing like with like.",
            "Regression is the workhorse — and the most over-trusted tool in "
            "applied work.",
            ("This week: when an OLS slope IS the causal effect, and the precise "
             "ways it stops being one.", 1),
            "Method = theory + assumptions + code + a real case, as always.",
         ],
         "note": {"title": "You will be able to",
            "body": "Decide which covariates belong in a regression — from the "
            "graph — and defend why the others are left out."}},
        {"type": "statement",
         "quote": "Regression doesn't know what a confounder is. You do — from the "
            "graph. The model just partials out whatever you hand it.",
         "attribution": "The covariate list is a causal assumption, not a "
            "statistical convenience. Choosing it well is most of the job."},

        {"type": "section", "kicker": "Part 1",
         "title": "Regression as adjustment",
         "subtitle": "OLS is a covariate-adjusted, weighted-average comparison — a "
            "matching estimator wearing a linear-algebra costume."},
        {"type": "content", "kicker": "The mechanism",
         "title": "What the slope on X actually is", "bullets": [
            "Regress Y on treatment X and covariates Z; the X slope compares units "
            "with similar Z.",
            "It is a variance-weighted average of within-stratum X–Y comparisons.",
            "Frisch–Waugh–Lovell: the slope = residual-X vs residual-Y after "
            "partialling out Z.",
            "So 'control for Z' literally means 'remove Z's linear part from both "
            "sides, then compare.'",
         ],
         "note": {"title": "Matching in disguise",
            "body": "Regression and matching answer the same question; they only "
            "differ in how they weight the comparisons."}},
        {"type": "content", "kicker": "The assumption",
         "title": "When is that slope causal?", "bullets": [
            "Conditional independence (CIA / selection-on-observables): "
            "Y(0), Y(1) ⫫ X | Z.",
            "In words: within levels of Z, treatment is as-good-as-randomly "
            "assigned.",
            "Then E[Y|X,Z] differences in X equal the causal effect of X.",
            "The CIA is an assumption about unobservables — untestable from the "
            "data alone.",
         ],
         "note": {"title": "The catch",
            "body": "Better fit does NOT make the CIA more true. Only the right "
            "covariates do."}},
        {"type": "content", "kicker": "Prediction's target",
         "title": "The conditional expectation function", "bullets": [
            "The CEF is E[Y | X, Z], the best predictor of Y given the regressors.",
            "OLS is the best LINEAR approximation to the CEF — pure description.",
            "Prediction lives entirely at the CEF; it never needs a causal "
            "assumption.",
            ("Causation = CEF + the claim that Z blocks every back-door path and "
             "nothing else.", 1),
         ],
         "note": {"title": "Two jobs",
            "body": "Describing the CEF is statistics. Calling a CEF slope an "
            "effect is a causal claim."}},

        {"type": "section", "kicker": "Part 2",
         "title": "Omitted-variable bias",
         "subtitle": "Leave out a confounder and its back-door path gets "
            "credited to your treatment — with a formula you can compute."},
        {"type": "content", "kicker": "The formula",
         "title": "Bias has a precise shape", "bullets": [
            "Short regression slope = long (correct) slope + bias.",
            "Bias = (effect of omitted Z on Y) × (slope of Z on X).",
            "Both factors non-zero ⇒ confounding; either zero ⇒ no OVB from "
            "omitting Z.",
            "Sign of the bias is the product of the two signs — you can predict "
            "its direction.",
         ],
         "note": {"title": "Useful corollary",
            "body": "A covariate unrelated to X (or to Y) cannot be a confounder, "
            "whatever it does to R²."}},
        {"type": "table", "kicker": "Reading the direction of bias",
         "title": "Sign of omitted-variable bias",
         "headers": ["Z → Y", "Z → X", "Bias in X slope", "Example"],
         "rows": [
            ["+", "+", "positive (too high)", "Ability ↑ wage, ability ↑ school"],
            ["−", "−", "positive (too high)", "Two negatives reinforce"],
            ["+", "−", "negative (too low)", "Health ↑ Y, health ↓ treatment"],
            ["0", "any", "none", "Z affects neither path"],
         ],
         "note": {"title": "Takeaway",
            "body": "You can sign the bias from the graph before you ever run the "
            "regression."}},

        {"type": "section", "kicker": "Part 3",
         "title": "Good controls vs. bad controls",
         "subtitle": "Not all covariates are confounders. Some remove bias, some "
            "add it, and some only move the variance."},
        {"type": "table", "kicker": "The core taxonomy",
         "title": "Four roles a covariate can play",
         "headers": ["Role", "Structure", "Adjust?", "What adjusting does"],
         "rows": [
            ["Good control (confounder)", "Z → X and Z → Y", "Yes",
             "Closes a back-door path — removes bias."],
            ["Bad control (mediator)", "X → M → Y", "No",
             "Blocks the very effect you want."],
            ["Collider (common effect)", "X → K ← Y", "No",
             "Opens a spurious path — adds bias."],
            ["Neutral (outcome predictor)", "Z → Y only", "Optional",
             "Off every back-door — only lowers variance."],
         ],
         "note": {"title": "The one rule",
            "body": "Structure, not timing, decides. Read the role off the "
            "graph before you touch the regression."}},
        {"type": "content", "kicker": "Don't adjust for mediators",
         "title": "A mediator hides the effect you want", "bullets": [
            "Drug → blood pressure → stroke: blood pressure is the mechanism.",
            "Control for it and you block the drug's main route to helping.",
            "You'd report only the (small) direct effect and call the drug useless.",
            ("Total effect: leave mediators OUT. Direct effect: that's mediation "
             "analysis, later.", 1),
         ],
         "note": {"title": "Rule",
            "body": "Anything caused by the treatment is a post-treatment "
            "variable — handle with great care."}},
        {"type": "content", "kicker": "Never adjust for colliders",
         "title": "A collider creates association from nothing", "bullets": [
            "X → K ← Y: the path through K is blocked until you condition on K.",
            "Conditioning on K (or on a descendant of K) opens it and biases X.",
            "Selection is conditioning: studying a filtered sample = adjusting for "
            "the filter.",
            "Famous cases: Berkson's bias, and the birth-weight paradox (coming "
            "up).",
         ],
         "note": {"title": "Surprise",
            "body": "Even a pre-treatment covariate can be a collider — see "
            "M-bias on the next slide."}},
        {"type": "steps", "kicker": "The M-bias trap",
         "title": "Pre-treatment does not mean safe", "steps": [
            {"title": "The shape", "body": "U₁ → Z ← U₂, with U₁ → X and "
             "U₂ → Y — the letter M."},
            {"title": "Left alone", "body": "the path X ← U₁ → Z ← U₂ → Y is "
             "blocked at the collider Z."},
            {"title": "Adjust for Z", "body": "you OPEN it and introduce bias that "
             "wasn't there."},
            {"title": "Lesson", "body": "structure, not timing, decides what to "
             "control for."},
         ],
         "note": "'Control for it to be safe' is exactly wrong when Z is a "
            "collider."},

        {"type": "section", "kicker": "Part 4",
         "title": "The Table 2 fallacy",
         "subtitle": "One regression, many coefficients — and the temptation to "
            "read every one of them as a causal effect."},
        {"type": "content", "kicker": "The mistake",
         "title": "A coefficient is not an effect", "bullets": [
            "Fit Y ~ X + Z₁ + Z₂; the output gives a coefficient for each.",
            "The X coefficient may be causal — if Z is the right adjustment set "
            "for X.",
            "The Z coefficients are adjusted for X, which may be a mediator on Z's "
            "own path.",
            ("Each variable's causal effect needs its OWN adjustment set — one "
             "model can't serve all.", 1),
         ],
         "note": {"title": "Name",
            "body": "Westreich & Greenland (2013) named it the 'Table 2 fallacy' "
            "after the typical results table."}},
        {"type": "compare", "kicker": "Two different questions",
         "title": "Effect of X vs. effect of Z", "columns": [
            {"head": "You want: effect of X", "points": [
                "Adjust for confounders of X → Y.",
                "Z belongs in the model.",
                "Read the X coefficient.",
                "Z's coefficient is a nuisance."]},
            {"head": "You want: effect of Z", "points": [
                "Adjust for confounders of Z → Y.",
                "X may be a MEDIATOR — exclude it.",
                "Different model, maybe different sample.",
                "Don't reuse the first table's Z row."]},
         ]},

        {"type": "section", "kicker": "Part 5",
         "title": "Interaction & effect modification",
         "subtitle": "When one slope fits no one: letting the effect of X depend "
            "on who you are."},
        {"type": "content", "kicker": "The idea",
         "title": "One effect for everyone is often wrong", "bullets": [
            "A single X slope reports an average that may fit no subgroup.",
            "Effect modification: the effect of X on Y differs by a variable G.",
            "Add an X×G interaction: each subgroup gets its own slope.",
            ("Effect modification (G scales X's effect) ≠ confounding (G biases "
             "X's effect).", 1),
         ],
         "note": {"title": "Read it",
            "body": "Coefficient on X = effect at G=0; coefficient on X×G = how "
            "much the effect changes per unit G."}},
        {"type": "table", "kicker": "Modification vs. confounding",
         "title": "A variable G can do either, both, or neither",
         "headers": ["G's role", "Affects X?", "Affects effect size?", "Action"],
         "rows": [
            ["Confounder", "yes (G → X)", "no", "adjust for it"],
            ["Effect modifier", "no", "yes", "interact with it"],
            ["Both", "yes", "yes", "adjust AND interact"],
            ["Neither", "no", "no", "ignore (maybe precision)"],
         ],
         "note": {"title": "Caution",
            "body": "Subgroup analyses multiply false positives — pre-specify and "
            "correct for multiplicity."}},

        {"type": "section", "kicker": "Part 6",
         "title": "A real case: the birth-weight paradox",
         "subtitle": "A famous reversal that dissolves the moment you draw the "
            "DAG — collider bias in the wild."},
        {"type": "steps", "kicker": "Case study · birth weight & smoking",
         "title": "Why smoking looks 'protective' for small babies", "steps": [
            {"title": "The finding", "body": "Among low-birth-weight infants, "
             "those of smoking mothers have LOWER mortality."},
            {"title": "The graph", "body": "Smoking → birth weight; and U "
             "(e.g. defects) → birth weight AND → mortality."},
            {"title": "The trap", "body": "Birth weight is a collider of smoking "
             "and U; stratifying on it opens Smoking ← BW ← U → Mortality."},
            {"title": "The resolution", "body": "Don't condition on birth weight; "
             "the unstratified effect of smoking is harmful, as expected."},
         ],
         "note": "The 'paradox' is collider bias — and the Table 2 fallacy if you "
            "read the birth-weight coefficient as causal."},
        {"type": "statement",
         "quote": "Controlling for more is not being careful. It is making a "
            "causal assumption — and the wrong one can invent an effect.",
         "attribution": "The graph decides the covariate list. Fit statistics "
            "decide nothing about bias."},

        {"type": "section", "kicker": "Part 7",
         "title": "Putting it together",
         "subtitle": "A short checklist you can apply to any regression before you "
            "trust a single coefficient."},
        {"type": "steps", "kicker": "The adjustment workflow",
         "title": "Before you read an OLS slope as an effect", "steps": [
            {"title": "Draw", "body": "— the DAG for X → Y with every covariate."},
            {"title": "Classify", "body": "— good control, mediator, collider, "
             "neutral, M-bias."},
            {"title": "Select", "body": "— a valid adjustment set; exclude "
             "post-treatment vars."},
            {"title": "Estimate", "body": "— fit; report only the coefficient you "
             "designed for."},
            {"title": "Stress-test", "body": "— sign the OVB; check effect "
             "modification."},
        ],
         "note": "One coefficient per question. Build the model around the effect "
            "you actually want."},
        {"type": "compare", "kicker": "What regression can and cannot do",
         "title": "Honest about the workhorse", "columns": [
            {"head": "Regression CAN", "points": [
                "Adjust for measured confounders.",
                "Approximate the CEF for prediction.",
                "Recover effects under the CIA.",
                "Model interactions / heterogeneity."]},
            {"head": "Regression CANNOT", "points": [
                "Fix unmeasured confounding.",
                "Tell a confounder from a collider.",
                "Make every coefficient causal.",
                "Earn the CIA by adding more covariates."]},
         ]},
        {"type": "statement",
         "quote": "Classify every control before you trust any coefficient.",
         "attribution": "This week: prove to yourself in code that a good control "
            "fixes bias and a bad one creates it — and that a coefficient is not "
            "an effect. See you in the workshop."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · Regression as covariate adjustment\n\n"
            "We start where Week 1 left off: a confounder `Z` pushes both the "
            "treatment `X` and the outcome `Y`. The **true** total effect of `X` "
            "on `Y` is exactly `2`. A naive regression credits part of `Z`'s "
            "effect to `X`; adjusting for `Z` recovers the truth. The point of "
            "this notebook is to see — on data where we *know* the answer — "
            "exactly when an OLS slope is a causal effect and the precise ways it "
            "stops being one."},
        {"code": "import statsmodels.api as sm\nimport statsmodels.formula.api as smf\n\n"
            "TRUE_EFFECT = 2.0          # the ground truth we will keep checking\n"
            "n = 8000\n"
            "Z = RNG.normal(size=n)                          # confounder Z -> X, Z -> Y\n"
            "X = 0.9 * Z + RNG.normal(size=n)                # treatment\n"
            "Y = TRUE_EFFECT * X + 1.5 * Z + RNG.normal(size=n)   # true X->Y = 2\n\n"
            "naive    = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
            "adjusted = sm.OLS(Y, sm.add_constant(np.c_[X, Z])).fit().params[1]\n"
            "print(f'naive    = {naive:.3f}   (biased: Z leaks into X)')\n"
            "print(f'adjusted = {adjusted:.3f}   vs truth {TRUE_EFFECT}')\n"
            "assert abs(adjusted - TRUE_EFFECT) < 0.15, 'adjusting for Z should recover 2'\n"
            "assert naive - adjusted > 0.3, 'naive should be visibly biased upward'"},
        {"md": "**Frisch–Waugh–Lovell:** 'controlling for `Z`' literally means "
            "partialling `Z` out of *both* `X` and `Y`, then relating the "
            "residuals. Let's confirm the adjusted slope equals the "
            "residual-on-residual slope — regression really is a matching/"
            "comparison estimator in disguise."},
        {"code": "def resid(target, *regs):\n"
            "    \"\"\"Residual of `target` after regressing it on the given regressors.\"\"\"\n"
            "    A = sm.add_constant(np.column_stack(regs))\n"
            "    fit = sm.OLS(target, A).fit()\n"
            "    return target - fit.predict(A)\n\n"
            "rX = resid(X, Z)        # X with Z partialled out\n"
            "rY = resid(Y, Z)        # Y with Z partialled out\n"
            "fwl = sm.OLS(rY, rX).fit().params[0]    # no intercept needed on residuals\n"
            "print(f'residual-on-residual slope = {fwl:.3f}')\n"
            "print(f'multivariate adjusted slope = {adjusted:.3f}')\n"
            "assert abs(fwl - adjusted) < 1e-6, 'FWL: the two slopes must match exactly'\n"
            "print('FWL holds: controlling for Z == partialling Z out of both sides.')"},
        {"md": "## 2 · Good controls vs. bad controls\n\n"
            "Same machinery, four roles. We extend the system with a **mediator** "
            "`M` (on the path `X → M → Y`), a **collider** `K` (a common effect, "
            "`X → K ← Y`), and a **neutral** predictor `V` — an independent cause "
            "of `Y` (`V → Y`) that has no relationship with `X`. Watch what "
            "adjusting for each does to the estimated `X → Y` effect. The truth is "
            "still `2`."},
        {"code": "# Construction: a direct effect of 1.0 plus an indirect effect of 1.0\n"
            "# through the mediator M, for a TOTAL effect of X on Y of 2.0 — our truth.\n"
            "M    = 1.0 * X + RNG.normal(size=n)            # X -> M  (path coeff 1.0)\n"
            "V    = RNG.normal(size=n)                      # neutral: an independent cause of Y\n"
            "Yc   = 1.0 * X + 1.0 * M + 1.5 * Z + 1.5 * V + RNG.normal(size=n)  # direct 1.0 + M*1.0\n"
            "K    = 1.0 * X + 1.0 * Yc + RNG.normal(size=n) # collider X -> K <- Y\n\n"
            "def xslope(y, *cols):\n"
            "    \"\"\"OLS slope on X (first regressor), adjusting for the rest.\"\"\"\n"
            "    return sm.OLS(y, sm.add_constant(np.column_stack((X,) + cols))).fit().params[1]\n\n"
            "good     = xslope(Yc, Z)          # adjust confounder only  -> total effect 2\n"
            "with_med = xslope(Yc, Z, M)       # + mediator (bad)        -> blocks indirect path\n"
            "with_col = xslope(Yc, Z, K)       # + collider (bad)        -> opens fake path\n"
            "with_neu = xslope(Yc, Z, V)       # + neutral predictor     -> harmless\n"
            "print(f'adjust Z only       = {good:.3f}   <- truth 2.0')\n"
            "print(f'+ mediator M        = {with_med:.3f}   (drops ~1.0: the indirect path is blocked)')\n"
            "print(f'+ collider K        = {with_col:.3f}   (biased: a fake path opened)')\n"
            "print(f'+ neutral V         = {with_neu:.3f}   (still ~2.0: harmless)')"},
        {"md": "Read the four numbers. **Only the good and the neutral controls "
            "left the estimate at the truth.** The mediator removed the part of "
            "the effect that runs through it; the collider opened a spurious path. "
            "The neutral predictor `V` didn't move the point estimate — and "
            "because it explains outcome variance, it actually *tightens* it. "
            "That precision payoff is the whole reason to keep a neutral control."},
        {"code": "# The neutral control is harmless for bias AND helps precision:\n"
            "se_without = sm.OLS(Yc, sm.add_constant(np.c_[X, Z])).fit().bse[1]\n"
            "se_with    = sm.OLS(Yc, sm.add_constant(np.c_[X, Z, V])).fit().bse[1]\n"
            "print(f'SE on X  without V = {se_without:.4f}   with V = {se_with:.4f}')\n"
            "assert se_with < se_without, 'a neutral outcome-predictor should shrink the SE on X'\n\n"
            "# Make the bias lesson machine-checkable against the known truth.\n"
            "assert abs(good - 2.0) < 0.15,        'confounder adjustment should recover 2'\n"
            "assert abs(with_neu - 2.0) < 0.15,    'neutral control should not bias the estimate'\n"
            "assert abs(with_med - 2.0) > 0.5,     'mediator adjustment SHOULD bias it (away from 2)'\n"
            "assert abs(with_col - 2.0) > 0.3,     'collider adjustment SHOULD bias it (away from 2)'\n"
            "print('All four roles behaved as the DAG predicts. Over-adjustment is not caution.')"},
        {"md": "### 🔧 Exercise 2.1 — the birth-weight paradox (a collider story)\n\n"
            "Reconstruct the famous reversal. Maternal **smoking** `S` lowers "
            "**birth weight** `BW`. An unmeasured factor `U` (think birth defects) "
            "*also* lowers birth weight **and** independently raises infant "
            "**mortality** `Mort`. Crucially, in this simulation smoking has **no "
            "real effect on mortality** — the true coefficient is `0`.\n\n"
            "Show that (a) the unadjusted smoking–mortality association is ~0 (the "
            "truth), but (b) **stratifying on / adjusting for birth weight — a "
            "collider — makes smoking look protective** (a negative coefficient).\n\n"
            "Fill in the `# TODO`s."},
        {"code": "# TODO: build S, U, BW (collider of S and U), and Mort (caused by U, NOT by S).\n"
            "# true effect of smoking on mortality is 0.0\n"
            "S    = RNG.binomial(1, 0.4, size=n)              # smoking (0/1)\n"
            "U    = RNG.normal(size=n)                        # unmeasured (e.g. defects)\n"
            "BW   = ...        # TODO: lower with smoking AND with U  (e.g. 3300 - 200*S - 300*U + noise)\n"
            "Mort = ...        # TODO: rises with U only, NOT with S  (e.g. 0.5*U + noise)\n"
            "# unadj = ...     # TODO: slope of Mort on S, no adjustment   -> ~0\n"
            "# adj   = ...     # TODO: slope of Mort on S, adjusting for BW -> negative (the 'paradox')\n"
            "# print(unadj, adj)"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "S    = RNG.binomial(1, 0.4, size=n).astype(float)   # smoking\n"
            "U    = RNG.normal(size=n)                               # unmeasured cause\n"
            "BW   = 3300 - 200*S - 300*U + RNG.normal(0, 100, size=n) # collider: S and U both lower it\n"
            "Mort = 0.5*U + RNG.normal(0, 0.5, size=n)               # U raises mortality; S does NOT\n\n"
            "unadj = sm.OLS(Mort, sm.add_constant(S)).fit().params[1]            # crude S->Mort\n"
            "adj   = sm.OLS(Mort, sm.add_constant(np.c_[S, BW])).fit().params[1] # adjusting the collider BW\n"
            "print(f'smoking->mortality, unadjusted     = {unadj:+.4f}   (truth 0)')\n"
            "print(f'smoking->mortality, adjusting BW    = {adj:+.4f}   (now looks PROTECTIVE!)')\n"
            "assert abs(unadj) < 0.10,  'with no real effect, the crude association is ~0'\n"
            "assert adj < -0.15,        'adjusting for the collider BW invents a protective effect'\n"
            "print('\\nBirth weight is a COLLIDER of smoking and U. Conditioning on it')\n"
            "print('opens S -> BW <- U -> Mort and manufactures a spurious benefit.')"},
        {"md": "## 3 · The Table 2 fallacy\n\n"
            "A single regression hands you a coefficient for **every** regressor. "
            "The Table 2 fallacy is reading each one as that variable's causal "
            "effect. We fit the *correct* model for `X` — `Y ~ X + Z` — and show "
            "that the coefficient on the confounder `Z` is **not** `Z`'s own total "
            "causal effect, even though the coefficient on `X` is right."},
        {"code": "# A system where we know BOTH true effects:\n"
            "#   true total effect of X on Y = 2.0\n"
            "#   Z affects Y directly (1.5) AND through X (0.9 * 2.0) -> Z's TOTAL effect = 1.5 + 1.8 = 3.3\n"
            "Zt = RNG.normal(size=n)\n"
            "Xt = 0.9 * Zt + RNG.normal(size=n)\n"
            "Yt = 2.0 * Xt + 1.5 * Zt + RNG.normal(size=n)\n\n"
            "fit = sm.OLS(Yt, sm.add_constant(np.c_[Xt, Zt])).fit()\n"
            "coef_X = fit.params[1]            # this IS the causal effect of X (Z is its confounder)\n"
            "coef_Z = fit.params[2]            # this is NOT Z's causal effect\n"
            "true_total_Z = sm.OLS(Yt, sm.add_constant(Zt)).fit().params[1]   # Z's actual total effect\n\n"
            "print(f'coef on X in the model      = {coef_X:.3f}   (= true effect of X, 2.0)')\n"
            "print(f'coef on Z in the SAME model = {coef_Z:.3f}   (the DIRECT effect, ~1.5)')\n"
            "print(f\"Z's true TOTAL effect       = {true_total_Z:.3f}   (~3.3)\")\n"
            "assert abs(coef_X - 2.0) < 0.15\n"
            "assert abs(coef_Z - 1.5) < 0.2          # the in-model Z coef is the DIRECT effect\n"
            "assert abs(true_total_Z - 3.3) < 0.2    # Z's true total effect is bigger\n"
            "assert abs(coef_Z - true_total_Z) > 1.0 # ... and they are NOT the same number"},
        {"md": "Same regression, two coefficients — and only the one we **designed "
            "the model for** is a clean causal effect. The `Z` coefficient is `Z`'s "
            "effect *holding `X` fixed*, i.e. the direct effect, because `X` is a "
            "**mediator** on `Z`'s path to `Y`. To get `Z`'s total effect you would "
            "build a *different* model. That is the Table 2 fallacy: **one model, "
            "one trustworthy coefficient.**"},
        {"md": "### 🔧 Exercise 3.1 — give Z its own (correct) model\n\n"
            "Using the `Xt, Zt, Yt` from the previous cell, estimate `Z`'s **total** "
            "causal effect *correctly*. Think about `Z`'s back-door paths: is `X` a "
            "confounder of `Z → Y`, or a mediator? Decide what (if anything) to "
            "adjust for, then recover ~`3.3`.\n\n"
            "Fill in the `# TODO`."},
        {"code": "# TODO: build the right model for the TOTAL effect of Z on Y.\n"
            "# Hint: X lies on a path Z -> X -> Y, so X is a MEDIATOR for Z's total effect.\n"
            "# total_Z = ...   # TODO: regress Y on Z WITHOUT adjusting for the mediator X\n"
            "# print(total_Z)"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "# X is a mediator of Z's effect on Y, so we must NOT adjust for it.\n"
            "total_Z = sm.OLS(Yt, sm.add_constant(Zt)).fit().params[1]\n"
            "print(f\"Z's total effect (X left out, as a mediator) = {total_Z:.3f}   (truth ~3.3)\")\n"
            "assert abs(total_Z - 3.3) < 0.2, 'leaving the mediator X out recovers Z total effect'\n"
            "print('Each variable needs its OWN adjustment set: X for X, none-but-Z for Z.')"},
        {"md": "## 4 · Interaction & effect modification\n\n"
            "A single slope assumes one effect for everyone. Here the treatment "
            "effect genuinely **differs by subgroup** `G`: it is `1.0` when `G=0` "
            "and `3.0` when `G=1`. A model with `X` and `G` but no interaction "
            "reports an average that fits neither group; adding an `X×G` "
            "interaction recovers both conditional effects."},
        {"code": "G  = RNG.binomial(1, 0.5, size=n)                   # subgroup indicator\n"
            "Xi = RNG.normal(size=n)                              # treatment (randomized here)\n"
            "EFFECT = 1.0 + 2.0 * G                               # 1.0 if G=0, 3.0 if G=1\n"
            "Yi = EFFECT * Xi + 0.5 * G + RNG.normal(size=n)\n"
            "dfi = pd.DataFrame({'Y': Yi, 'X': Xi, 'G': G})\n\n"
            "no_int = smf.ols('Y ~ X + G', data=dfi).fit().params['X']\n"
            "print(f'single-slope model: effect of X = {no_int:.3f}  (an average that fits no one)')\n"
            "mi = smf.ols('Y ~ X * G', data=dfi).fit()\n"
            "eff_G0 = mi.params['X']                              # effect at G=0\n"
            "eff_G1 = mi.params['X'] + mi.params['X:G']           # effect at G=1\n"
            "print(f'interaction model:  effect at G=0 = {eff_G0:.3f}  (truth 1.0)')\n"
            "print(f'interaction model:  effect at G=1 = {eff_G1:.3f}  (truth 3.0)')\n"
            "assert abs(eff_G0 - 1.0) < 0.15, 'interaction should recover the G=0 effect'\n"
            "assert abs(eff_G1 - 3.0) < 0.15, 'interaction should recover the G=1 effect'"},
        {"md": "The single-slope estimate (~2.0) is the average of the two true "
            "effects but describes neither subgroup. The interaction term lets the "
            "effect of `X` depend on `G` and recovers `1.0` and `3.0` on the nose. "
            "**Effect modification** (`G` changes the *size* of the effect) is a "
            "different phenomenon from **confounding** (`G` would *bias* the "
            "effect) — here `G` is independent of `X`, so it modifies without "
            "confounding."},
        {"md": "### 🔧 Exercise 4.1 — recover the average treatment effect\n\n"
            "From the interaction fit, the population **ATE** is the average of the "
            "subgroup effects weighted by subgroup size. With `G` split 50/50 it "
            "should be ~`2.0`. Compute it from the interaction coefficients and the "
            "observed mean of `G`, and check it matches the simple single-slope "
            "model's estimate.\n\nFill in the `# TODO`."},
        {"code": "# TODO: ATE = E[ effect(G) ] = effect_at_G0 + coef(X:G) * E[G]\n"
            "# pG  = ...       # TODO: observed P(G=1)\n"
            "# ate = ...       # TODO: combine eff_G0 and the interaction coefficient\n"
            "# print(ate)"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "pG  = dfi['G'].mean()                               # P(G=1)\n"
            "ate = eff_G0 + mi.params['X:G'] * pG                # weighted-average effect\n"
            "print(f'ATE from interaction model = {ate:.3f}   (truth ~2.0)')\n"
            "print(f'single-slope estimate      = {no_int:.3f}   (should be close)')\n"
            "assert abs(ate - 2.0) < 0.15, 'weighted subgroup effects give the ATE'\n"
            "assert abs(ate - no_int) < 0.2, 'and it matches the simple single-slope model'\n"
            "print('The single slope was the ATE all along — it just hid the heterogeneity.')"},
        {"md": "## 5 · A picture: bias by what you adjust for\n\n"
            "One figure to fix the intuition. We plot the estimated `X → Y` effect "
            "under four adjustment choices against the known truth. Good and "
            "neutral controls sit on the line; the mediator and collider do not."},
        {"code": "labels = ['adjust Z\\n(good)', '+ mediator M\\n(bad)',\n"
            "          '+ collider K\\n(bad)', '+ neutral V\\n(ok)']\n"
            "vals   = [good, with_med, with_col, with_neu]\n"
            "colors = ['#2A9D8F', '#C0504D', '#C0504D', '#2F6DB5']\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.bar(labels, vals, color=colors)\n"
            "ax.axhline(2.0, color='#E9A23B', linestyle='--', linewidth=2, label='truth = 2.0')\n"
            "ax.set_ylabel('estimated effect of X on Y')\n"
            "ax.set_title('Only the good (and neutral) controls land on the truth')\n"
            "ax.legend()\n"
            "fig.tight_layout()\n"
            "print('Figure built. Bars off the dashed line = bias you created by over-adjusting.')"},
        {"md": "## Wrap-up & self-check\n\n"
            "- **Regression is adjustment.** Under the conditional independence "
            "assumption, the OLS slope on `X` is the causal effect; FWL shows it "
            "is residual-on-residual matching.\n"
            "- **Classify every control.** Confounder → adjust; mediator → don't "
            "(for the total effect); collider → don't; neutral → optional "
            "(precision).\n"
            "- **Over-adjustment is not caution.** You watched the mediator and "
            "collider move the estimate *away* from the known truth, and rebuilt "
            "the birth-weight paradox from a collider.\n"
            "- **The Table 2 fallacy.** A regression gives one coefficient per "
            "regressor, but only the one you designed the model for is a clean "
            "causal effect; `Z` needs its own adjustment set.\n"
            "- **Interactions** recover effects that differ by subgroup, and the "
            "weighted average returns the ATE.\n\n"
            "**You're ready for Week 6** if you can classify each covariate on a "
            "DAG and say why a coefficient is not an effect. Next week: matching "
            "and propensity scores — adjusting by rebuilding a comparable control "
            "group instead of modeling the outcome."},
    ],
}
