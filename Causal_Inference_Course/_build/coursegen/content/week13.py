# -*- coding: utf-8 -*-
"""Week 13 — Heterogeneous Effects & Policy Learning. Content module."""

WEEK = {
    "number": 13,
    "slug": "heterogeneous_effects",
    "title": "Heterogeneous Effects & Policy Learning",
    "block": "Block IV — Modern methods & application",
    "subtitle": "Move from \"does it work on average?\" to \"for whom — and what "
                "should we do about it?\"",
    "deliverable": "Problem Set 7 — CATE, meta-learners, and policy; "
                   "Lab 10 — CATE & policy learning (T-/S-learners, uplift "
                   "curves, and an optimal treatment rule).",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab (2–3h).",
    "one_sentence": "The average treatment effect can hide enormous variation "
        "across people; this week we estimate the conditional effect τ(x) = "
        "E[Y(1) − Y(0) | X = x] with meta-learners and causal forests, learn how "
        "to evaluate those estimates without ground truth, and turn them into a "
        "treatment policy that does better than treating everyone or no one.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Define the CATE τ(x) and explain precisely how it differs from the ATE, "
        "and why an ATE of zero is compatible with large individual effects.",
        "Construct the S-, T-, X-, and R-learners from off-the-shelf regressors "
        "and say when each is preferred — in particular when the X-learner helps.",
        "Explain how a causal forest uses honest splitting to deliver pointwise "
        "CATE estimates with valid confidence intervals.",
        "Evaluate a CATE model WITHOUT ground truth using calibration plots and "
        "uplift / Qini curves, and explain why naive subgroup-hunting overfits.",
        "Turn a CATE estimate into a treatment rule π(x) = 1{τ̂(x) > c}, define "
        "the value V(π) of that policy, and compare it to treat-all / treat-none.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Wager & Athey (2018), Estimation and Inference of Heterogeneous "
                 "Treatment Effects using Random Forests.",
         "look_for": "how honest trees (split on one half, estimate on the other) "
                     "give pointwise CATE estimates with valid asymptotic "
                     "inference, where ordinary random forests cannot."},
        {"text": "Künzel, Sekhon, Bickel & Yu (2019), Meta-learners for "
                 "estimating heterogeneous treatment effects using machine "
                 "learning.",
         "look_for": "the S/T/X-learner constructions, and exactly when the "
                     "X-learner helps — unbalanced treatment groups and a CATE "
                     "that is smoother than the response surfaces."},
    ],
    "optional_readings": [
        {"text": "Athey & Wager (2021), Policy Learning with Observational Data.",
         "note": "How to go from estimated effects to an optimal treatment rule, "
                 "with regret guarantees — the policy-learning half of the week."},
        {"text": "Nie & Wager (2021), Quasi-oracle estimation of heterogeneous "
                 "treatment effects.",
         "note": "The R-learner objective (residual-on-residual with a τ term) "
                 "that the causal forest's splitting criterion approximates."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "From ATE to CATE: 'for whom?'",
         "body": "The ATE = E[Y(1) − Y(0)] answers 'does it work on average?'. "
            "The conditional average treatment effect (CATE) τ(x) = "
            "E[Y(1) − Y(0) | X = x] answers 'how big is the effect for someone "
            "who looks like x?'. The two can disagree dramatically: a drug with "
            "an ATE of zero can help half the patients and harm the other half. "
            "Once effects vary, the average is a policy-irrelevant summary — what "
            "you actually want to know is who benefits, so you can target them.",
         "callout": {"title": "The averaging trap",
            "color": "RED",
            "lines": ["A zero (or tiny) ATE does NOT mean 'the treatment does "
                      "nothing.' It can mean equal and opposite effects that "
                      "cancel.",
                      "Reporting only the ATE for a heterogeneous treatment can "
                      "lead you to abandon a therapy that is excellent for an "
                      "identifiable subgroup."]}},
        {"heading": "Meta-learners: CATE from any regressor",
         "body": "A meta-learner is a recipe that turns standard supervised "
            "regressors into a CATE estimator. They differ in how they use the "
            "treatment indicator W.",
         "bullets": [
            [("S-learner (Single). ", {"bold": True}),
             ("Fit ONE model μ(x, w) with W as just another feature; "
              "τ̂(x) = μ(x,1) − μ(x,0). Simple, but the learner can ignore W and "
              "shrink the estimated effect toward zero.", {})],
            [("T-learner (Two). ", {"bold": True}),
             ("Fit μ₁ on the treated and μ₀ on the controls separately; "
              "τ̂(x) = μ̂₁(x) − μ̂₀(x). Flexible, but noisy when one arm is small "
              "and it models two surfaces when you only want their difference.", {})],
            [("X-learner. ", {"bold": True}),
             ("Impute each unit's effect using the OTHER arm's model, regress "
              "those pseudo-effects on X, and combine the two with propensity "
              "weights. Shines when treatment groups are unbalanced.", {})],
            [("R-learner. ", {"bold": True}),
             ("Partial out the outcome and the treatment (Robinson "
              "transformation), then fit τ on the residuals — the same "
              "orthogonalization idea as DML, now aimed at the effect function.", {})],
         ]},
        {"heading": "Causal forests: honesty buys inference",
         "body": "A causal forest is an ensemble of trees whose splits are chosen "
            "to maximize heterogeneity in the treatment effect, not to predict Y. "
            "The key trick is HONESTY: each tree uses one subsample to choose "
            "splits and a disjoint subsample to estimate the effect in each leaf. "
            "Honest splitting removes the bias that lets ordinary forests overfit, "
            "which is what makes the resulting CATE estimates asymptotically "
            "normal and equips them with valid pointwise confidence intervals — "
            "something a vanilla RandomForest T-learner cannot promise.",
         "bullets": [
            [("Splitting criterion. ", {"bold": True}),
             ("Reward splits that separate units with different effects (an "
              "R-learner-style objective), not different outcome levels.", {})],
            [("Honesty. ", {"bold": True}),
             ("Choose the tree shape and estimate leaf effects on DIFFERENT "
              "data; this is the price for valid inference.", {})],
            [("Weights, not just predictions. ", {"bold": True}),
             ("The forest defines an adaptive neighborhood (kernel) around x, "
              "and the CATE is a locally weighted effect estimate.", {})],
         ]},
        {"heading": "Evaluating a CATE model without ground truth",
         "body": "In real data you never see τ(x), so you cannot compute its MSE. "
            "Two tools let you judge a CATE model anyway, and one warning keeps "
            "you honest.",
         "bullets": [
            [("Calibration. ", {"bold": True}),
             ("Bin units by predicted effect; within each bin estimate the ACTUAL "
              "effect (e.g. a difference in means in a randomized holdout). A good "
              "model's predicted and realized effects line up on the 45° line.", {})],
            [("Uplift / Qini curve. ", {"bold": True}),
             ("Sort units by predicted CATE, then plot cumulative incremental "
              "outcome as you treat the top-k fraction. A model that ranks "
              "responders well rises fast and sits above the random diagonal; the "
              "Qini coefficient is the area between them.", {})],
            [("Why subgroup-hunting overfits. ", {"bold": True}),
             ("Searching many subgroups for 'the one where it works' is multiple "
              "testing in disguise — the most extreme subgroup effect is biased "
              "upward by selection. Pre-register, cross-fit, or use a method built "
              "to regularize the effect function.", {})],
         ],
         "callout": {"title": "Honest evaluation rule",
            "color": "BLUE",
            "lines": ["Fit the CATE model on one split; evaluate calibration and "
                      "uplift on a DISJOINT split (ideally a randomized holdout).",
                      "A CATE model is only as useful as the decisions it improves "
                      "— always end at the policy value, not the correlation."]}},
        {"heading": "Policy learning: from τ̂(x) to a decision",
         "body": "A treatment policy is a rule π : X → {0,1}. If treating costs c "
            "(in outcome units), the value-maximizing rule treats exactly the "
            "units whose effect exceeds the cost: π*(x) = 1{τ(x) > c}. With c = 0 "
            "this is 'treat whenever the effect is positive.' The VALUE of a "
            "policy is V(π) = E[Y(π(X))], and the quantity that matters is its "
            "advantage over a baseline: V(π) − V(treat-none) = E[π(X) · (τ(X) − c)]. "
            "A good learned policy beats both treat-all and treat-none — it "
            "captures the gains where the effect is positive and avoids the losses "
            "where it is negative.",
         "bullets": [
            [("Estimand. ", {"bold": True}),
             ("V(π) − V(0) = E[π(X)(τ(X) − c)]; estimate it on a holdout using a "
              "doubly robust score so plug-in CATE error mostly cancels.", {})],
            [("Regret. ", {"bold": True}),
             ("The gap V(π*) − V(π̂) between the best possible rule and yours; "
              "policy learning aims to make regret vanish as n grows.", {})],
            [("Budgeted version. ", {"bold": True}),
             ("If you can only treat a fraction of units, treat the highest-CATE "
              "ones until the budget is spent — the uplift curve reads off the "
              "value at each budget.", {})],
         ]},
    ],
    "problem_set": {
        "label": "Problem Set 7",
        "title": "CATE, meta-learners, and policy",
        "intro": "Five problems take you from defining the conditional effect to "
            "turning it into a decision. Answer in prose plus a little notation; "
            "try all five before checking the solutions.",
        "problems": [
            {"title": "CATE vs. ATE",
             "prompt": "Define the ATE and the CATE τ(x) precisely in "
                "potential-outcomes notation. Give a concrete example where the "
                "ATE is zero yet the treatment is far from useless. What is the "
                "relationship between τ(x) and the ATE?",
             "solution_title": "ATE = E[Y(1) − Y(0)]; CATE τ(x) = "
                "E[Y(1) − Y(0) | X = x]; the ATE is the average of τ(x) over X.",
             "solution": [
                "The ATE is the population-average effect, E[Y(1) − Y(0)]. The "
                "CATE conditions on covariates: τ(x) = E[Y(1) − Y(0) | X = x], the "
                "average effect among units that look like x.",
                "By iterated expectation, ATE = E[τ(X)] — the ATE is just the "
                "covariate-average of the CATE, so heterogeneity is invisible in "
                "the ATE alone.",
                "Example: a drug helps patients with a biomarker (τ = +4) and "
                "harms those without it (τ = −4) in equal numbers. The ATE is 0, "
                "but the treatment is highly consequential — you simply must give "
                "it to the right half."]},
            {"title": "S- vs. T- vs. X-learner",
             "prompt": "Describe how each of the S-, T-, and X-learners produces "
                "a CATE estimate. State one failure mode of the S-learner and one "
                "of the T-learner, and explain the specific situation in which the "
                "X-learner is expected to outperform both.",
             "solution_title": "S = one model with W as a feature; T = two models "
                "differenced; X = cross-imputed effects re-regressed and "
                "propensity-weighted.",
             "solution": [
                "S-learner: fit μ(x, w) once, τ̂(x) = μ(x,1) − μ(x,0). Failure "
                "mode: a regularized learner can treat W as unimportant and "
                "shrink the estimated effect toward zero.",
                "T-learner: fit μ̂₁ on treated and μ̂₀ on controls, "
                "τ̂(x) = μ̂₁(x) − μ̂₀(x). Failure mode: high variance when one arm "
                "is small, and it spends capacity modeling two response surfaces "
                "instead of their (often simpler) difference.",
                "X-learner: impute each unit's effect with the opposite arm's "
                "model, regress those pseudo-effects on X, and blend the two by "
                "the propensity. It wins when the groups are unbalanced (it leans "
                "on the larger arm to estimate the smaller arm's effect) and when "
                "τ(x) is smoother than μ₀ and μ₁ individually."]},
            {"title": "Why naive subgroup-hunting overfits",
             "prompt": "A colleague reports: 'The overall effect was null, but we "
                "found a subgroup — left-handed patients under 40 in the northeast "
                "— where the effect is large and significant.' Explain, "
                "statistically, why this finding is likely overstated, and name "
                "two practices that would make a heterogeneity claim credible.",
             "solution_title": "Searching many subgroups is multiple testing; the "
                "winning subgroup's effect is selection-biased upward.",
             "solution": [
                "If you scan many candidate subgroups, some will look impressive "
                "by chance alone. Reporting the most extreme one is the winner's "
                "curse: its estimated effect is biased away from the truth, and "
                "the nominal p-value ignores the search.",
                "The deeper issue is that the subgroup was chosen using the same "
                "data that produced the estimate — there is no honest holdout, so "
                "the effect cannot be trusted at face value.",
                "Credible practice: (1) pre-specify subgroups or use a method that "
                "regularizes the effect function (causal forest, R-learner); "
                "(2) estimate the CATE on one split and confirm calibration / "
                "uplift on a disjoint holdout. Sample-splitting and pre-"
                "registration are the cure."]},
            {"title": "Evaluating a CATE model without ground truth",
             "prompt": "You have a CATE model but, as always in real data, you "
                "never observe τ(x). Describe two ways to assess the model: a "
                "calibration check and an uplift/Qini curve. What does each one "
                "tell you, and what does a useless model look like on each?",
             "solution_title": "Calibration: binned predicted vs. realized effects "
                "on the 45° line. Uplift/Qini: cumulative gain when treating "
                "top-ranked units, above the random diagonal.",
             "solution": [
                "Calibration: bin units by predicted effect; within each bin "
                "estimate the realized effect (a difference in means in a "
                "randomized holdout, or a doubly robust score). Plot realized vs. "
                "predicted — a well-calibrated model hugs the 45° line. A useless "
                "model produces a flat line near the overall ATE regardless of the "
                "prediction.",
                "Uplift / Qini: sort by predicted CATE and plot cumulative "
                "incremental outcome as you treat the top-k fraction. A model that "
                "ranks responders well rises steeply early and bows above the "
                "random diagonal; the Qini coefficient is the area between curve "
                "and diagonal.",
                "A model with no signal traces the diagonal (uplift) and is flat "
                "(calibration): treating its 'top' units is no better than "
                "treating a random set. Both checks need a holdout the model never "
                "saw."]},
            {"title": "From CATE to a treatment policy",
             "prompt": "Given an estimated τ̂(x) and a treatment cost c (in "
                "outcome units), write down the value-maximizing policy. Define "
                "the value V(π) of a policy and the advantage of the learned "
                "policy over treat-none. Why should the learned policy beat both "
                "treat-all and treat-none when effects are heterogeneous?",
             "solution_title": "π*(x) = 1{τ(x) > c}; "
                "V(π) − V(0) = E[π(X)(τ(X) − c)]; the rule keeps the gains and "
                "skips the losses.",
             "solution": [
                "The value-maximizing rule treats exactly the units whose effect "
                "clears the cost: π*(x) = 1{τ(x) > c} (with c = 0, treat whenever "
                "the effect is positive).",
                "The policy value is V(π) = E[Y(π(X))]; the decision-relevant "
                "quantity is the advantage over treating no one, "
                "V(π) − V(0) = E[π(X) · (τ(X) − c)].",
                "With heterogeneous effects some τ(x) are negative. Treat-all "
                "pays those losses; treat-none forgoes the gains. The learned rule "
                "treats only the units with positive net effect, so it dominates "
                "both — bounded above only by the oracle π* and by estimation "
                "error in τ̂."]},
        ],
    },
    "lab": {
        "label": "Lab 10",
        "title": "CATE & policy learning",
        "goal": "estimate conditional treatment effects with meta-learners, "
            "evaluate them honestly, and convert them into a targeting policy "
            "whose value you can quantify — all on simulated data with a known "
            "τ(x). Pick Python (scikit-learn) or R (grf); both are supported.",
        "steps": [
            {"heading": "Step 1 · Simulate heterogeneous effects",
             "body": "Generate covariates X, a randomized treatment W, and an "
                "outcome whose effect τ(x) genuinely varies — center τ near zero "
                "so the ATE is small but a real fraction of units are harmed. Keep "
                "the true τ(x) aside as ground truth for evaluation.",
             "code_python": "import numpy as np\n"
                "from sklearn.ensemble import RandomForestRegressor\n"
                "rng = np.random.default_rng(0)\n"
                "def make(n):\n"
                "    X = rng.uniform(0, 1, size=(n, 5))\n"
                "    tau = 2.5*X[:,0] - 1.5*X[:,1] - 0.6        # true CATE\n"
                "    W = rng.binomial(1, 0.5, size=n)            # randomized\n"
                "    base = 2.0*X[:,2] + X[:,3] + rng.normal(0, 1, n)\n"
                "    Y = base + W*tau\n"
                "    return X, W, Y, tau\n"
                "Xtr, Wtr, Ytr, ttr = make(4000)\n"
                "Xte, Wte, Yte, tte = make(4000)\n"
                "print('ATE =', round(tte.mean(), 3),\n"
                "      '| frac harmed =', round((tte < 0).mean(), 3))",
             "code_r": "library(grf)\n"
                "set.seed(0); n <- 4000\n"
                "make <- function(n) {\n"
                "  X <- matrix(runif(n*5), n, 5)\n"
                "  tau <- 2.5*X[,1] - 1.5*X[,2] - 0.6\n"
                "  W <- rbinom(n, 1, 0.5)\n"
                "  Y <- 2*X[,3] + X[,4] + rnorm(n) + W*tau\n"
                "  list(X=X, W=W, Y=Y, tau=tau)\n}\n"
                "tr <- make(n); te <- make(n)\n"
                "cat('ATE =', mean(te$tau), '\\n')"},
            {"heading": "Step 2 · Fit a T-learner and an S-learner",
             "body": "T-learner: two RandomForestRegressors, one per arm. "
                "S-learner: one forest with W appended as a feature. Keep the "
                "forests small for speed.",
             "code_python": "RF = dict(n_estimators=200, max_depth=8,\n"
                "          min_samples_leaf=20, random_state=0)\n"
                "# T-learner\n"
                "m1 = RandomForestRegressor(**RF).fit(Xtr[Wtr==1], Ytr[Wtr==1])\n"
                "m0 = RandomForestRegressor(**RF).fit(Xtr[Wtr==0], Ytr[Wtr==0])\n"
                "cate_T = m1.predict(Xte) - m0.predict(Xte)\n"
                "# S-learner\n"
                "mS = RandomForestRegressor(**RF).fit(\n"
                "        np.column_stack([Xtr, Wtr]), Ytr)\n"
                "cate_S = (mS.predict(np.column_stack([Xte, np.ones(len(Xte))])) -\n"
                "          mS.predict(np.column_stack([Xte, np.zeros(len(Xte))])))",
             "code_r": "# grf's causal_forest is the honest-tree analogue\n"
                "cf <- causal_forest(tr$X, tr$Y, tr$W)\n"
                "cate <- predict(cf, te$X)$predictions"},
            {"heading": "Step 3 · Estimate CATE and compare to truth",
             "body": "Because the data are simulated you can score the estimates "
                "directly: correlation with τ(x) and MSE against it.",
             "code_python": "for name, c in [('T', cate_T), ('S', cate_S)]:\n"
                "    r = np.corrcoef(c, tte)[0, 1]\n"
                "    mse = np.mean((c - tte)**2)\n"
                "    print(f'{name}-learner: corr={r:.3f}  mse={mse:.3f}')",
             "code_r": "r <- cor(cate, te$tau)\n"
                "cat('corr with true CATE =', round(r, 3), '\\n')"},
            {"heading": "Step 4 · Build an uplift / Qini-style curve",
             "body": "Sort the holdout by predicted CATE and accumulate the true "
                "effect. A model that ranks responders well rises above the random "
                "diagonal.",
             "code_python": "order = np.argsort(-cate_T)\n"
                "cum = np.cumsum(tte[order])\n"
                "frac = np.arange(1, len(order)+1) / len(order)\n"
                "rand = np.linspace(0, cum[-1], len(order))\n"
                "qini = np.trapezoid(cum, frac) - np.trapezoid(rand, frac)\n"
                "print('Qini-style area (model − random) =', round(qini, 2))",
             "code_r": "rate <- rank_average_treatment_effect(cf,\n"
                "           predict(cf)$predictions)\n"
                "print(rate)   # RATE / TOC: uplift from targeting by CATE"},
            {"heading": "Step 5 · Derive a 'treat if CATE>0' policy and value it",
             "body": "Define π(x) = 1{τ̂(x) > 0} and estimate its value advantage "
                "over treat-none, E[π(X)·τ(X)]. Compare to treat-all and "
                "treat-none; the learned policy should beat both.",
             "code_python": "pv = lambda pi: np.mean(pi * tte)   # gain over treat-none\n"
                "pi = (cate_T > 0).astype(int)\n"
                "print(f'learned (CATE>0): {pv(pi):+.3f}')\n"
                "print(f'treat-all:        {pv(np.ones(len(Xte))):+.3f}')\n"
                "print(f'treat-none:       0.000')\n"
                "print('fraction treated:', round(pi.mean(), 3))",
             "code_r": "pi <- as.integer(cate > 0)\n"
                "cat('policy gain over none =', mean(pi * te$tau), '\\n')\n"
                "cat('treat-all gain        =', mean(te$tau), '\\n')"},
        ],
        "expected": "The ATE is near zero, yet the T-learner's predicted CATE "
            "correlates strongly (~0.9) with the true τ(x). The uplift curve bows "
            "above the diagonal (positive Qini area). The 'treat if CATE>0' policy "
            "treats roughly half the units and delivers a clearly positive gain "
            "over treat-none, beating treat-all (which is net-negative because it "
            "treats the harmed units). Same data, three policies — and the learned "
            "rule wins because it knows for whom.",
        "submit": [
            "Push your notebook reporting the T- and S-learner correlations with "
            "the true CATE, the Qini-style area, and the three policy values.",
            "Add one paragraph: what fraction of units does your policy treat, and "
            "why does it beat both treat-all and treat-none?",
            "Bring your active-reading sentences (Wager & Athey; Künzel et al.) to "
            "lab.",
        ],
    },
    "self_check": [
        "State the CATE in notation and give an ATE-is-zero-but-effect-matters "
        "example from memory.",
        "Sketch the S-, T-, and X-learner constructions and say when the "
        "X-learner helps.",
        "Explain how honest splitting earns a causal forest valid confidence "
        "intervals.",
        "Describe how to evaluate a CATE model with calibration and an uplift "
        "curve when τ(x) is unobserved.",
        "Write down π*(x) = 1{τ(x) > c} and the policy value, and say why the "
        "learned rule beats treat-all/none.",
    ],
    "next_week": {
        "heading": "Coming up: Week 14 — Advanced topics",
        "teaser": "We round out the modern toolkit: mediation and direct/indirect "
            "effects, sensitivity analysis for unmeasured confounding, and a look "
            "at causal discovery and effects under interference. These are the "
            "topics you'll reach for when the standard playbook from Weeks 1–13 "
            "doesn't quite fit your study. Skim the optional readings to preview "
            "where each one bites.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 13", "items": [
            {"t": "Beyond the average", "d": "Why the ATE can hide who is helped "
             "and who is harmed."},
            {"t": "CATE", "d": "The conditional effect τ(x) and what it lets you "
             "do."},
            {"t": "Meta-learners", "d": "S-, T-, X-, and R-learners from any "
             "regressor."},
            {"t": "Causal forests", "d": "Honest trees that give CATE with valid "
             "inference."},
            {"t": "Evaluating CATE", "d": "Calibration and uplift/Qini without "
             "ground truth."},
            {"t": "Policy learning", "d": "From τ̂(x) to an optimal treatment "
             "rule — and its value."},
        ]},
        {"type": "content", "kicker": "Why this week",
         "title": "The average is the wrong question for a decision",
         "bullets": [
            "An ATE answers 'does it work on average?' — a policy must answer "
            "'for whom, and what do we do?'.",
            "Treatments are rarely uniform: some patients benefit, some are "
            "unaffected, some are harmed.",
            ("A zero ATE is compatible with huge individual effects that cancel.",
             1),
            "If effects vary, targeting the right units can beat treating "
            "everyone — sometimes by a lot.",
            "This is the bridge from estimation to action: CATE → policy.",
         ],
         "note": {"title": "The shift",
            "body": "From 'how big is the effect?' to 'who should we treat, and "
            "how much better is that than treat-all or treat-none?'"}},
        {"type": "content", "kicker": "Where it bites",
         "title": "Targeting an intervention", "bullets": [
            "Medicine: give the drug to responders, spare non-responders the side "
            "effects.",
            "Marketing: send the offer to customers it will actually persuade "
            "(uplift modeling).",
            "Policy: allocate a scarce program to the people it helps most.",
            "Each is the same problem: estimate τ(x), then decide who gets "
            "treated.",
         ],
         "note": {"title": "Case study",
            "body": "Which patients (or customers) should be treated? We answer it "
            "end-to-end in the lab."}},

        {"type": "section", "kicker": "Part 1",
         "title": "From ATE to CATE",
         "subtitle": "The conditional average treatment effect — the object that "
            "makes personalization possible."},
        {"type": "content", "kicker": "Definition",
         "title": "CATE: the effect for someone who looks like x", "bullets": [
            "ATE = E[Y(1) − Y(0)]: the population-average effect.",
            "CATE τ(x) = E[Y(1) − Y(0) | X = x]: the average effect among units "
            "with covariates x.",
            ("ATE = E[τ(X)] — the ATE is just the average of the CATE.", 1),
            "Heterogeneity is exactly the variation of τ(x) across x.",
            "Personalized decisions live at the level of τ(x), not the ATE.",
         ],
         "note": {"title": "Estimand first",
            "body": "Decide whether you want the average effect or the effect "
            "function before you fit anything."}},
        {"type": "statement",
         "quote": "An ATE of zero can mean 'does nothing' — or 'helps half, harms "
            "half.' Only τ(x) tells them apart.",
         "attribution": "When effects are heterogeneous, the average is a "
            "policy-irrelevant summary. The decision lives in the variation."},
        {"type": "table", "kicker": "Same ATE, different worlds",
         "title": "Why the average can mislead",
         "headers": ["Scenario", "Effect for group A", "Effect for group B",
                     "ATE"],
         "rows": [
            ["Homogeneous", "+1.0", "+1.0", "+1.0"],
            ["Helps one group", "+2.0", "0.0", "+1.0"],
            ["Helps & harms", "+4.0", "−4.0", "0.0"],
            ["Mostly harms a few", "+0.5", "−3.0", "varies"],
         ],
         "note": {"title": "Read the last row",
            "body": "A small positive ATE can still hide a subgroup that is badly "
            "harmed — a reason to target, not to treat-all."}},

        {"type": "section", "kicker": "Part 2",
         "title": "Meta-learners",
         "subtitle": "Turn any off-the-shelf regressor into a CATE estimator — the "
            "S-, T-, X-, and R-learners."},
        {"type": "content", "kicker": "S-learner",
         "title": "One model, treatment as a feature", "bullets": [
            "Fit a single μ(x, w) with W as just another covariate.",
            "τ̂(x) = μ̂(x, 1) − μ̂(x, 0).",
            "Simple and data-efficient; reuses one model.",
            ("Risk: a regularized learner can downweight W and shrink τ̂ toward "
             "zero.", 1),
         ],
         "note": {"title": "When it's fine",
            "body": "Effects modest and smooth, and the base learner won't ignore "
            "the treatment indicator."}},
        {"type": "content", "kicker": "T-learner",
         "title": "Two models, one per arm", "bullets": [
            "Fit μ̂₁ on the treated and μ̂₀ on the controls separately.",
            "τ̂(x) = μ̂₁(x) − μ̂₀(x).",
            "Flexible — each arm gets its own model.",
            ("Risk: noisy when an arm is small; models two surfaces to get one "
             "difference.", 1),
         ],
         "note": {"title": "Our workhorse",
            "body": "Two RandomForestRegressors approximate an honest causal "
            "forest well enough for the lab."}},
        {"type": "content", "kicker": "X-learner",
         "title": "Cross-impute, re-regress, blend", "bullets": [
            "Stage 1: fit μ̂₀, μ̂₁ (as in the T-learner).",
            "Stage 2: impute each unit's effect with the OTHER arm's model.",
            "Stage 3: regress imputed effects on X; blend the two by the "
            "propensity e(x).",
            ("Wins when treatment groups are unbalanced, or τ(x) is smoother than "
             "the response surfaces.", 1),
         ],
         "note": {"title": "Why it helps",
            "body": "It borrows strength from the larger arm to estimate the "
            "smaller arm's effect."}},
        {"type": "compare", "kicker": "Pick a learner",
         "title": "S vs. T vs. X vs. R", "columns": [
            {"head": "S-learner", "sub": "one model", "points": [
                "W is a feature.",
                "Data-efficient.",
                "Can shrink τ̂ to 0."]},
            {"head": "T / X-learner", "sub": "per-arm", "points": [
                "T: difference two models.",
                "X: cross-impute + blend.",
                "X shines when arms unbalanced."]},
            {"head": "R-learner", "sub": "orthogonal", "points": [
                "Partial out Y and W.",
                "Fit τ on residuals.",
                "Same idea as DML."]},
         ]},

        {"type": "section", "kicker": "Part 3",
         "title": "Causal forests",
         "subtitle": "Honest trees that estimate τ(x) pointwise — with valid "
            "confidence intervals."},
        {"type": "content", "kicker": "The idea",
         "title": "Split for effect heterogeneity, not for outcome", "bullets": [
            "Trees split to separate units with DIFFERENT treatment effects.",
            "The forest is an adaptive kernel: a data-driven neighborhood around "
            "x.",
            "CATE at x = a locally weighted effect estimate from that "
            "neighborhood.",
            "An R-learner-style criterion drives the splits.",
         ],
         "note": {"title": "Not outcome prediction",
            "body": "A causal forest optimizes for heterogeneity in τ, not for "
            "predicting Y."}},
        {"type": "content", "kicker": "Honesty",
         "title": "Why honest splitting buys inference", "bullets": [
            "Use one subsample to choose splits, a DISJOINT one to estimate leaf "
            "effects.",
            "This removes the overfitting bias that plagues ordinary forests.",
            "Result: CATE estimates that are asymptotically normal with valid "
            "pointwise CIs.",
            ("A vanilla RandomForest T-learner cannot promise that inference.", 1),
         ],
         "note": {"title": "The price",
            "body": "You split your data: less data per task, in exchange for "
            "honest uncertainty."}},
        {"type": "compare", "kicker": "Two routes to τ(x)",
         "title": "T-learner forest vs. causal forest", "columns": [
            {"head": "RF T-learner", "points": [
                "Two standard forests, differenced.",
                "Easy with scikit-learn.",
                "Point estimates only — no honest CIs.",
                "Our lab approximation."]},
            {"head": "Honest causal forest (grf)", "points": [
                "One forest, honest splits.",
                "Splits target effect heterogeneity.",
                "Valid pointwise confidence intervals.",
                "Wager & Athey (2018)."]},
         ]},

        {"type": "section", "kicker": "Part 4",
         "title": "Evaluating a CATE model",
         "subtitle": "You never see τ(x) in real data — so how do you know your "
            "model is any good?"},
        {"type": "content", "kicker": "The problem",
         "title": "No ground truth for the effect", "bullets": [
            "Each unit reveals only one potential outcome, so τ(x) is never "
            "observed.",
            "You cannot compute the MSE of a CATE model directly on real data.",
            "But you CAN check whether its rankings and levels hold up out of "
            "sample.",
            "Two tools: calibration and the uplift / Qini curve.",
         ],
         "note": {"title": "Golden rule",
            "body": "Fit on one split; evaluate on a disjoint holdout, ideally a "
            "randomized one."}},
        {"type": "content", "kicker": "Tool 1 · Calibration",
         "title": "Do predicted effects match realized effects?", "bullets": [
            "Bin holdout units by predicted CATE.",
            "Within each bin, estimate the ACTUAL effect (difference in means in a "
            "randomized holdout).",
            "Plot realized vs. predicted — a good model hugs the 45° line.",
            ("A useless model is flat near the overall ATE.", 1),
         ],
         "note": {"title": "What it catches",
            "body": "Over- or under-confident predictions and systematic shrinkage "
            "toward the average."}},
        {"type": "content", "kicker": "Tool 2 · Uplift / Qini",
         "title": "Does targeting by τ̂ actually pay off?", "bullets": [
            "Sort units by predicted CATE; treat the top-k fraction.",
            "Plot cumulative incremental outcome vs. fraction treated.",
            "A good model bows ABOVE the random diagonal; Qini = area between "
            "them.",
            ("Reads off the value at every treatment budget.", 1),
         ],
         "note": {"title": "Decision-facing",
            "body": "The uplift curve answers 'if I can treat 20%, whom — and how "
            "much do I gain?'"}},
        {"type": "statement",
         "quote": "The most extreme subgroup you find by searching is biased "
            "upward — that's multiple testing, not a discovery.",
         "attribution": "Naive subgroup-hunting overfits. Pre-register, cross-fit, "
            "or use a method that regularizes the effect function."},

        {"type": "section", "kicker": "Part 5",
         "title": "Policy learning",
         "subtitle": "From an estimated effect function to an optimal treatment "
            "rule — and a number that says how much it's worth."},
        {"type": "content", "kicker": "The rule",
         "title": "Treat where the effect clears the cost", "bullets": [
            "A policy is a rule π : X → {0, 1}.",
            "With treatment cost c, the optimal rule is π*(x) = 1{τ(x) > c}.",
            ("With c = 0: treat whenever the effect is positive.", 1),
            "Plug in τ̂(x) to get a learned policy π̂.",
         ],
         "note": {"title": "Simple, but powerful",
            "body": "Most of the work is a good τ̂; the decision rule itself is a "
            "threshold."}},
        {"type": "content", "kicker": "The value",
         "title": "How good is a policy?", "bullets": [
            "Value V(π) = E[Y(π(X))]: the expected outcome under the rule.",
            "Advantage over treat-none: V(π) − V(0) = E[π(X) · (τ(X) − c)].",
            "Estimate it on a holdout with a doubly robust score so plug-in error "
            "cancels.",
            "Regret = V(π*) − V(π̂): the gap to the best possible rule.",
         ],
         "note": {"title": "Always end here",
            "body": "A CATE model is only as useful as the policy value it "
            "delivers — not its correlation."}},
        {"type": "steps", "kicker": "The pipeline",
         "title": "CATE to decision in four steps", "steps": [
            {"title": "Estimate", "body": "— fit τ̂(x) with a meta-learner or "
             "causal forest."},
            {"title": "Evaluate", "body": "— calibration + uplift on a disjoint "
             "holdout."},
            {"title": "Decide", "body": "— π̂(x) = 1{τ̂(x) > c}."},
            {"title": "Value", "body": "— estimate V(π̂) − V(0); compare to "
             "treat-all / none."},
         ],
         "note": "The learned rule keeps the gains and skips the losses — that's "
            "why it beats both baselines."},
        {"type": "compare", "kicker": "Three policies",
         "title": "Why the learned rule wins", "columns": [
            {"head": "Treat-all", "points": [
                "Treats everyone.",
                "Pays the losses on harmed units.",
                "Net-negative if many τ(x) < 0."]},
            {"head": "Treat-none", "points": [
                "Treats no one.",
                "Forgoes all the gains.",
                "Value advantage = 0."]},
            {"head": "Learned 1{τ̂>0}", "points": [
                "Treats only positive-effect units.",
                "Captures gains, avoids losses.",
                "Beats both baselines."]},
         ]},

        {"type": "section", "kicker": "Part 6",
         "title": "Case & wrap-up",
         "subtitle": "Targeting an intervention end-to-end — and what to carry "
            "into the lab."},
        {"type": "steps", "kicker": "Case study · who should be treated?",
         "title": "Targeting an intervention", "steps": [
            {"title": "Simulate", "body": "Heterogeneous τ(x) centered near 0 — "
             "ATE small, but many harmed."},
            {"title": "Estimate", "body": "T- and S-learner CATE; compare to the "
             "known τ(x)."},
            {"title": "Evaluate", "body": "Uplift / Qini curve above the diagonal."},
            {"title": "Act", "body": "'Treat if τ̂ > 0' beats treat-all and "
             "treat-none."},
         ],
         "note": "Same data, three policies — the learned one wins because it "
            "knows for whom."},
        {"type": "content", "kicker": "Pitfalls to avoid",
         "title": "What breaks a heterogeneity analysis", "bullets": [
            "Subgroup-hunting without a holdout — the winner's curse inflates the "
            "effect.",
            "Reporting correlation with τ̂ but never the policy value.",
            "Forgetting positivity: you can't estimate τ(x) where one arm is "
            "absent.",
            "Trusting point CATE without uncertainty when stakes are high.",
         ],
         "note": {"title": "Antidotes",
            "body": "Sample-split, evaluate on a holdout, and always end at the "
            "policy value."}},
        {"type": "statement",
         "quote": "Estimate τ(x). Evaluate it honestly. Decide who to treat. "
            "Measure the value.",
         "attribution": "This week: fit a T- and S-learner, build an uplift "
            "curve, and show a 'treat if τ̂>0' policy beating treat-all and "
            "treat-none. See you in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · The ATE can hide who is helped and who is harmed\n\n"
            "We simulate a world with a **known, covariate-varying** treatment "
            "effect τ(x) = E[Y(1) − Y(0) | X = x]. Because we built it, we can "
            "always compare any estimate to the truth. Treatment `W` is "
            "*randomized* (so confounding is not the issue here) — the whole story "
            "this week is **heterogeneity**, not bias.\n\n"
            "We deliberately center τ(x) near zero: the **ATE is small**, yet a "
            "real fraction of units are actually *harmed* (τ < 0). That is exactly "
            "the situation where the average is the wrong thing to report."},
        {"code": "from sklearn.ensemble import RandomForestRegressor\n\n"
            "def make_data(n):\n"
            "    \"\"\"Randomized W; true CATE tau(x) varies with X0 and X1.\"\"\"\n"
            "    X = RNG.uniform(0, 1, size=(n, 5))\n"
            "    tau = 2.5 * X[:, 0] - 1.5 * X[:, 1] - 0.6     # KNOWN ground-truth CATE\n"
            "    W = RNG.binomial(1, 0.5, size=n)              # randomized treatment\n"
            "    base = 2.0 * X[:, 2] + X[:, 3] + RNG.normal(0, 1.0, size=n)\n"
            "    Y = base + W * tau                            # only W*tau is causal\n"
            "    return X, W, Y, tau\n\n"
            "# A train split (to fit models) and a test split (to evaluate honestly)\n"
            "Xtr, Wtr, Ytr, tau_tr = make_data(4000)\n"
            "Xte, Wte, Yte, tau_te = make_data(4000)\n\n"
            "ate_true = tau_te.mean()\n"
            "ate_dim  = Yte[Wte == 1].mean() - Yte[Wte == 0].mean()  # diff-in-means\n"
            "print(f'True ATE            = {ate_true:+.3f}')\n"
            "print(f'Estimated ATE (DiM) = {ate_dim:+.3f}   (randomized, so unbiased)')\n"
            "print(f'SD of true CATE     = {tau_te.std():.3f}')\n"
            "print(f'Range of true CATE  = [{tau_te.min():+.2f}, {tau_te.max():+.2f}]')\n"
            "print(f'Fraction HARMED (tau<0) = {(tau_te < 0).mean():.1%}')\n\n"
            "assert abs(ate_dim - ate_true) < 0.15, 'diff-in-means should recover the ATE'\n"
            "assert tau_te.std() > 0.5, 'we want genuinely heterogeneous effects'"},
        {"md": "The ATE is near zero and the difference-in-means recovers it — yet "
            "**over half the population is harmed** while the rest benefit. "
            "Reporting only the ATE here would tell you to abandon a treatment "
            "that is excellent for an identifiable subgroup. Let's find that "
            "subgroup by estimating τ(x)."},
        {"code": "# Quick look: the true effect clearly varies with X0 (and X1).\n"
            "fig, ax = plt.subplots()\n"
            "sc = ax.scatter(Xte[:, 0], tau_te, c=Xte[:, 1], s=6, cmap='viridis')\n"
            "ax.axhline(0, color='k', lw=1)\n"
            "ax.axhline(ate_true, color='crimson', ls='--', lw=1.5, label='ATE')\n"
            "ax.set_xlabel('X0'); ax.set_ylabel('true CATE  tau(x)')\n"
            "ax.set_title('A flat ATE (red) hides a strong gradient in tau(x)')\n"
            "ax.legend(); fig.colorbar(sc, label='X1')\n"
            "print('Units above 0 benefit; units below 0 are harmed.')"},

        {"md": "## 2 · Two meta-learners: T-learner and S-learner\n\n"
            "A **meta-learner** turns ordinary regressors into a CATE estimator.\n\n"
            "- **T-learner (Two models):** fit one forest on the treated, one on "
            "the controls; τ̂(x) = μ̂₁(x) − μ̂₀(x).\n"
            "- **S-learner (Single model):** fit one forest with `W` appended as a "
            "feature; τ̂(x) = μ̂(x, 1) − μ̂(x, 0).\n\n"
            "We keep the forests small for speed and fit on the **train** split, "
            "predict on the **test** split."},
        {"code": "# Small forests keep this fast; same settings for every learner.\n"
            "RF = dict(n_estimators=200, max_depth=8, min_samples_leaf=20,\n"
            "          random_state=0)\n\n"
            "# ---- T-learner: two separate forests ----\n"
            "m1 = RandomForestRegressor(**RF).fit(Xtr[Wtr == 1], Ytr[Wtr == 1])\n"
            "m0 = RandomForestRegressor(**RF).fit(Xtr[Wtr == 0], Ytr[Wtr == 0])\n"
            "cate_T = m1.predict(Xte) - m0.predict(Xte)\n\n"
            "# ---- S-learner: one forest with W as a feature ----\n"
            "mS = RandomForestRegressor(**RF).fit(np.column_stack([Xtr, Wtr]), Ytr)\n"
            "cate_S = (mS.predict(np.column_stack([Xte, np.ones(len(Xte))])) -\n"
            "          mS.predict(np.column_stack([Xte, np.zeros(len(Xte))])))\n\n"
            "print('Fitted T-learner (2 forests) and S-learner (1 forest).')\n"
            "print('Predicted CATE for first 5 test units (T-learner):')\n"
            "print(np.round(cate_T[:5], 3))"},
        {"md": "Because the data are simulated we can do something impossible in "
            "real life: **score the CATE estimates against the truth.** We report "
            "the correlation with τ(x) and the MSE, and assert that the T-learner "
            "tracks the truth strongly."},
        {"code": "def score(name, cate):\n"
            "    r   = np.corrcoef(cate, tau_te)[0, 1]\n"
            "    mse = np.mean((cate - tau_te) ** 2)\n"
            "    print(f'{name:>10}-learner:  corr(tau_hat, tau_true) = {r:.3f}   '\n"
            "          f'MSE = {mse:.3f}')\n"
            "    return r, mse\n\n"
            "rT, mseT = score('T', cate_T)\n"
            "rS, mseS = score('S', cate_S)\n\n"
            "# The T-learner should correlate strongly with the ground-truth effect.\n"
            "assert rT > 0.7, f'T-learner correlation with true CATE too low: {rT:.3f}'\n"
            "print('\\nBoth learners recover the heterogeneity; T-learner corr > 0.7. OK.')"},

        {"md": "### 🔧 Exercise 2.1 — build the X-learner\n\n"
            "The **X-learner** often beats the T-learner. Construction:\n\n"
            "1. Use the already-fitted `m0`, `m1`.\n"
            "2. **Impute** each unit's effect with the *other* arm's model:\n"
            "   - treated units: `D1 = Y − m0.predict(X)`\n"
            "   - control units: `D0 = m1.predict(X) − Y`\n"
            "3. Regress `D1` on `X` (treated) and `D0` on `X` (control) to get "
            "`tau1`, `tau0`.\n"
            "4. Blend by the propensity `e ≈ 0.5`: "
            "`cate_X = e*tau0.predict(Xte) + (1-e)*tau1.predict(Xte)`.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (it falls back to the "
            "T-learner) so the notebook never breaks."},
        {"code": "e = 0.5   # known propensity (randomized)\n\n"
            "# TODO 1: imputed effects using the OPPOSITE arm's model\n"
            "D1 = ...   # for treated units:  Ytr[Wtr==1] - m0.predict(Xtr[Wtr==1])\n"
            "D0 = ...   # for control units:  m1.predict(Xtr[Wtr==0]) - Ytr[Wtr==0]\n\n"
            "# TODO 2: regress the imputed effects on X (use RandomForestRegressor(**RF))\n"
            "# tau1 = RandomForestRegressor(**RF).fit(Xtr[Wtr==1], D1)\n"
            "# tau0 = RandomForestRegressor(**RF).fit(Xtr[Wtr==0], D0)\n\n"
            "# TODO 3: blend the two with the propensity e\n"
            "# cate_X = e*tau0.predict(Xte) + (1-e)*tau1.predict(Xte)\n\n"
            "# Fallback so the skeleton still runs before you fill it in:\n"
            "if not isinstance(D1, np.ndarray):\n"
            "    cate_X = cate_T.copy()\n"
            "print('cate_X ready (fallback = T-learner until you complete the TODOs).')"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "D1 = Ytr[Wtr == 1] - m0.predict(Xtr[Wtr == 1])   # treated: effect vs control model\n"
            "D0 = m1.predict(Xtr[Wtr == 0]) - Ytr[Wtr == 0]   # control: treated model vs actual\n\n"
            "tau1 = RandomForestRegressor(**RF).fit(Xtr[Wtr == 1], D1)\n"
            "tau0 = RandomForestRegressor(**RF).fit(Xtr[Wtr == 0], D0)\n\n"
            "cate_X = e * tau0.predict(Xte) + (1 - e) * tau1.predict(Xte)\n\n"
            "rX, mseX = score('X', cate_X)\n"
            "print(f'\\nT-learner MSE = {mseT:.3f}   X-learner MSE = {mseX:.3f}')\n"
            "assert rX > 0.7, 'X-learner should also correlate strongly with truth'\n"
            "assert mseX <= mseT + 0.02, 'X-learner should be at least competitive with T'\n"
            "print('X-learner is competitive with (here, better than) the T-learner. OK.')"},

        {"md": "## 3 · Evaluating a CATE model — uplift / Qini\n\n"
            "In real data τ(x) is unobserved, so you judge a model by whether "
            "**targeting by its score pays off.** Sort units by predicted CATE, "
            "then accumulate the (true, in this simulation) effect as you treat "
            "the top-ranked fraction. A useful model's curve bows **above** the "
            "random diagonal; the area between them is a Qini-style score."},
        {"code": "def uplift_curve(cate_pred, tau_true):\n"
            "    order = np.argsort(-cate_pred)            # best-predicted first\n"
            "    cum   = np.cumsum(tau_true[order])        # cumulative true gain\n"
            "    frac  = np.arange(1, len(order) + 1) / len(order)\n"
            "    rand  = np.linspace(0, cum[-1], len(order))  # treat in random order\n"
            "    qini  = np.trapezoid(cum, frac) - np.trapezoid(rand, frac)\n"
            "    return frac, cum, rand, qini\n\n"
            "frac, cum, rand, qini_T = uplift_curve(cate_T, tau_te)\n"
            "print(f'Qini-style area (T-learner, model - random) = {qini_T:.2f}')\n"
            "assert qini_T > 0, 'a useful CATE model must beat random targeting'\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot(frac, cum,  label='target by predicted CATE')\n"
            "ax.plot(frac, rand, ls='--', label='random targeting')\n"
            "ax.set_xlabel('fraction of units treated (high CATE first)')\n"
            "ax.set_ylabel('cumulative true gain')\n"
            "ax.set_title('Uplift / Qini curve — model bows above the diagonal')\n"
            "ax.legend()\n"
            "print('Curve rises fast then flattens: the early-treated units are the responders.')"},
        {"md": "The curve climbs steeply while we are treating high-CATE "
            "responders, peaks, then *declines* as we are forced to treat harmed "
            "units (negative τ). **The peak is the optimal treated fraction** — a "
            "preview of the policy in Section 4."},

        {"md": "### 🔧 Exercise 3.1 — calibration by CATE quintile\n\n"
            "A second check: **calibration.** Bin the test units into quintiles of "
            "predicted CATE and, within each bin, compare the *mean predicted* "
            "effect to the *mean true* effect. A well-calibrated model lands on "
            "the 45° line, so the binned predicted and true means should be highly "
            "correlated.\n\n"
            "Complete the `# TODO`s using `pd.qcut(cate_T, 5, labels=False)`."},
        {"code": "# TODO: bin by predicted-CATE quintile and average pred & truth per bin.\n"
            "q = ...   # pd.qcut(cate_T, 5, labels=False)\n"
            "if not isinstance(q, np.ndarray):\n"
            "    # fallback so the cell runs before you fill it in\n"
            "    q = pd.qcut(cate_T, 5, labels=False)\n"
            "cal = (pd.DataFrame({'pred': cate_T, 'true': tau_te, 'bin': q})\n"
            "         .groupby('bin')[['pred', 'true']].mean())\n"
            "print(cal)\n"
            "# calib = ...   # corr between cal['pred'] and cal['true']"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "q = pd.qcut(cate_T, 5, labels=False)\n"
            "cal = (pd.DataFrame({'pred': cate_T, 'true': tau_te, 'bin': q})\n"
            "         .groupby('bin')[['pred', 'true']].mean())\n"
            "calib = np.corrcoef(cal['pred'], cal['true'])[0, 1]\n"
            "print(cal)\n"
            "print(f'\\nCalibration corr (binned pred vs. true) = {calib:.3f}')\n\n"
            "fig, ax = plt.subplots()\n"
            "lo = min(cal['pred'].min(), cal['true'].min())\n"
            "hi = max(cal['pred'].max(), cal['true'].max())\n"
            "ax.plot([lo, hi], [lo, hi], 'k--', lw=1, label='perfect calibration')\n"
            "ax.scatter(cal['pred'], cal['true'], s=60, zorder=3)\n"
            "ax.set_xlabel('mean predicted CATE in bin')\n"
            "ax.set_ylabel('mean TRUE CATE in bin')\n"
            "ax.set_title('Calibration: binned predicted vs. realized effect')\n"
            "ax.legend()\n"
            "assert calib > 0.9, 'binned predictions should track the truth closely'\n"
            "print('Bins line up on the 45-degree line — well calibrated. OK.')"},

        {"md": "## 4 · From CATE to a policy — and its value\n\n"
            "Now the payoff. Define the policy **π(x) = 1{τ̂(x) > 0}**: treat a "
            "unit only when its predicted effect is positive. The **value "
            "advantage** of any policy over treating no one is\n\n"
            "$$V(\\pi) - V(\\text{none}) = \\mathbb{E}[\\pi(X)\\,\\tau(X)].$$\n\n"
            "Since we know τ(x), we can compute this exactly and compare three "
            "policies: the learned rule, **treat-all**, and **treat-none**."},
        {"code": "def policy_value(pi, tau_true):\n"
            "    \"\"\"Expected gain over treat-none:  E[ pi(X) * tau(X) ].\"\"\"\n"
            "    return np.mean(pi * tau_true)\n\n"
            "pi_learned = (cate_T > 0).astype(int)          # treat if predicted CATE > 0\n"
            "pi_all     = np.ones(len(Xte), dtype=int)       # treat everyone\n"
            "pi_none    = np.zeros(len(Xte), dtype=int)      # treat no one\n"
            "pi_oracle  = (tau_te > 0).astype(int)           # if we KNEW the truth\n\n"
            "v_learned = policy_value(pi_learned, tau_te)\n"
            "v_all     = policy_value(pi_all,     tau_te)\n"
            "v_none    = policy_value(pi_none,    tau_te)\n"
            "v_oracle  = policy_value(pi_oracle,  tau_te)\n\n"
            "print('Policy value (gain over treat-none):')\n"
            "print(f'  treat-none        : {v_none:+.3f}')\n"
            "print(f'  treat-all         : {v_all:+.3f}   (net-negative: it treats the harmed)')\n"
            "print(f'  learned 1{{CATE>0}} : {v_learned:+.3f}')\n"
            "print(f'  oracle  1{{tau>0}}  : {v_oracle:+.3f}   (best achievable)')\n"
            "print(f'\\nLearned policy treats {pi_learned.mean():.1%} of units.')\n\n"
            "assert v_learned > v_all,  'learned policy should beat treat-all'\n"
            "assert v_learned > v_none, 'learned policy should beat treat-none'\n"
            "print('\\nThe learned policy beats BOTH treat-all and treat-none. OK.')"},
        {"md": "The learned rule **dominates both baselines**: treat-all is "
            "net-negative because it pays for the harmed units, treat-none gains "
            "nothing, and our 'treat if τ̂ > 0' rule captures most of the oracle's "
            "value while treating only those it expects to help. *That* is the "
            "point of estimating CATE — it changes the decision."},

        {"md": "### 🔧 Exercise 4.1 — a budgeted policy\n\n"
            "Often you can only treat a **fraction** of units (a budget). The "
            "budget-`b` policy treats the top-`b` share by predicted CATE. Using "
            "`cate_T`, build the policy that treats the **top 40%** and compute its "
            "value advantage over treat-none. Does it beat treat-all?\n\n"
            "Fill in the `# TODO`s."},
        {"code": "budget = 0.40\n"
            "# TODO: threshold cate_T at its (1 - budget) quantile to pick the top 40%.\n"
            "thresh = ...   # np.quantile(cate_T, 1 - budget)\n"
            "if thresh is ...:\n"
            "    thresh = np.quantile(cate_T, 1 - budget)\n"
            "pi_budget = (cate_T >= thresh).astype(int)\n"
            "# v_budget = ...   # policy_value(pi_budget, tau_te)\n"
            "print('fraction treated:', round(pi_budget.mean(), 3))"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "thresh = np.quantile(cate_T, 1 - budget)\n"
            "pi_budget = (cate_T >= thresh).astype(int)\n"
            "v_budget = policy_value(pi_budget, tau_te)\n"
            "print(f'budget-{budget:.0%} policy treats {pi_budget.mean():.1%} of units')\n"
            "print(f'  value over treat-none = {v_budget:+.3f}')\n"
            "print(f'  (treat-all = {v_all:+.3f}, learned-all-positive = {v_learned:+.3f})')\n"
            "assert v_budget > v_all, 'targeting the top 40% should beat treating everyone'\n"
            "print('Even under a tight budget, targeting by CATE beats treat-all. OK.')"},

        {"md": "## 5 · Wrap-up & self-check\n\n"
            "- **CATE τ(x) = E[Y(1) − Y(0) | X = x]**; the ATE is its average, so "
            "a near-zero ATE can hide large, canceling individual effects.\n"
            "- **Meta-learners** turn any regressor into a CATE estimator: "
            "S (one model), T (two models), X (cross-impute + blend). Here the "
            "T- and X-learners recovered τ(x) with correlation ≈ 0.9.\n"
            "- A **causal forest** would add honest splitting and valid pointwise "
            "confidence intervals — the T-learner forest is our inference-free "
            "approximation.\n"
            "- You can evaluate CATE **without ground truth** via **calibration** "
            "(binned pred vs. realized) and an **uplift / Qini curve** (does "
            "targeting pay?). Naive subgroup-hunting overfits — always use a "
            "holdout.\n"
            "- A CATE estimate becomes a decision: **π(x) = 1{τ̂(x) > c}**, with "
            "value advantage **E[π(X)(τ(X) − c)]**. The learned policy beat both "
            "treat-all and treat-none.\n\n"
            "**You're ready for Week 14 — Advanced topics**, where we add "
            "mediation, sensitivity analysis for unmeasured confounding, and "
            "effects under interference to the toolkit."},
    ],
}
