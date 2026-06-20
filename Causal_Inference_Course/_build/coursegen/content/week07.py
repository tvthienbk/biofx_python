# -*- coding: utf-8 -*-
"""Week 7 — Weighting & Doubly Robust Estimation."""

WEEK = {
    "number": 7,
    "slug": "weighting_doubly_robust",
    "title": "Weighting & Doubly Robust Estimation",
    "block": "Block II — Adjustment for confounding",
    "subtitle": "Inverse-probability weighting, stabilized weights, and "
                "estimators that survive one modeling mistake.",
    "deliverable": "Problem Set 5 — weights, overlap, and double robustness; "
                   "Lab 4 — IPW & AIPW on a confounded cohort.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab (2–3h). The notebook "
                    "is the heart of the week — run it end to end.",
    "one_sentence": "Inverse-probability weighting rebuilds a pseudo-population "
        "in which treatment is unconfounded, and augmenting it with an outcome "
        "model buys you a safety net: the doubly robust estimator stays "
        "consistent if EITHER the propensity model OR the outcome model is "
        "right — you only need to win one of the two bets.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Derive the IP-weighting estimator and explain why weighting by the "
        "inverse propensity creates a pseudo-population in which treatment is "
        "independent of the measured confounders.",
        "State the exchangeability and positivity assumptions IP weighting "
        "relies on, and show why a weight is just 1 / P(observed treatment | X).",
        "Compute Horvitz–Thompson and Hájek (stabilized) estimates of the ATE "
        "and explain when to prefer each.",
        "Diagnose extreme weights, recognize them as a symptom of near-positivity "
        "violations, and tame them with stabilization or truncation.",
        "Build an augmented IPW / doubly robust estimator and demonstrate that "
        "it recovers the truth when only one of its two models is correct.",
        "Explain what positivity violations are, how to detect them, and the "
        "menu of responses (trim, redefine the estimand, or change the question).",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Hernán & Robins, Causal Inference: What If — Chapters 12–13.",
         "look_for": "how IP weighting creates a pseudo-population in which "
                     "treatment is unconfounded, and why stabilized weights have "
                     "mean one."},
        {"text": "Huntington-Klein, The Effect — weighting sections.",
         "look_for": "the intuition that weighting up-weights under-represented "
                     "covariate profiles so the treated and control groups look "
                     "alike."},
    ],
    "optional_readings": [
        {"text": "Robins, Hernán & Brumback (2000), 'Marginal Structural Models "
                 "and Causal Inference in Epidemiology.'",
         "note": "The paper that put IP weighting and MSMs on the map — read it "
                 "for the time-varying-treatment motivation."},
        {"text": "Bang & Robins (2005), 'Doubly Robust Estimation in Missing "
                 "Data and Causal Inference Models.'",
         "note": "The canonical reference for the augmented estimator you build "
                 "in lab; skim the double-robustness argument."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "Weighting, not matching: the pseudo-population",
         "body": "Last week we made the treated and control groups comparable by "
            "matching or by modeling the outcome. IP weighting takes a different "
            "route: it reweights the sample so that, in the reweighted "
            "'pseudo-population,' treatment no longer depends on the measured "
            "confounders. Each unit is weighted by the inverse of the probability "
            "of the treatment it actually received — 1/e for the treated, "
            "1/(1−e) for the controls, where e = P(T=1 | X) is the propensity "
            "score. Units in covariate regions that were unlikely to get their "
            "treatment are rare in the sample, so we up-weight them to stand in "
            "for the copies we did not observe."},
        {"heading": "Why the weights work (exchangeability + positivity)",
         "body": "Under conditional exchangeability (no unmeasured confounding) "
            "and positivity (every covariate profile has a non-zero chance of "
            "each treatment), the inverse-probability-weighted mean of the "
            "treated equals E[Y(1)], and likewise for the controls. The ATE is "
            "the difference of the two weighted means.",
         "bullets": [
            [("Exchangeability:  ", {"bold": True}),
             ("within levels of X, treatment is as good as random, so weighting "
              "by 1/P(T|X) removes its dependence on X.", {})],
            [("Positivity:  ", {"bold": True}),
             ("0 < e(X) < 1 for all X. If some profile is never treated, its "
              "weight is 1/0 — undefined — and the estimand is not identified "
              "there. Extreme weights are positivity screaming at you.", {})],
            [("The estimand:  ", {"bold": True}),
             ("ATE = E[Y(1)] − E[Y(0)], each leg an inverse-probability-weighted "
              "average over the whole pseudo-population.", {})],
         ]},
        {"heading": "Horvitz–Thompson vs. Hájek (stabilized)",
         "body": "Two ways to average with weights. The Horvitz–Thompson "
            "estimator divides by the sample size n; it is unbiased but high "
            "variance because the weights need not sum to n. The Hájek estimator "
            "divides by the sum of the weights — a self-normalizing, "
            "ratio-style estimate that is slightly biased but far more stable, "
            "and it is what stabilized weights deliver in practice.",
         "bullets": [
            [("Horvitz–Thompson:  ", {"bold": True}),
             ("mean of T·Y/e minus mean of (1−T)·Y/(1−e). Exactly unbiased; "
              "can swing wildly when some e are near 0 or 1.", {})],
            [("Hájek / stabilized:  ", {"bold": True}),
             ("normalize each arm by its own weight total. Multiply weights by "
              "the marginal P(T=t) and they get mean ≈ 1 — a sanity check you "
              "should always run.", {})],
         ]},
        {"heading": "Extreme weights & positivity violations",
         "body": "A single unit with weight 200 can dominate the estimate: your "
            "effective sample size collapses and the variance explodes. Extreme "
            "weights almost always mean a propensity near 0 or 1 — a region where "
            "one treatment arm is nearly empty (a near-positivity violation).",
         "bullets": [
            "Diagnose: plot the weight distribution; report the max weight and "
            "the effective sample size; overlay the propensity histograms by arm.",
            "Stabilize: use stabilized weights (mean ≈ 1) to shrink the spread "
            "without changing the target estimand.",
            "Truncate: cap weights at, say, the 1st/99th percentile. This trades "
            "a little bias for a large drop in variance — a deliberate bargain.",
            "Or change the question: redefine the estimand to the region of good "
            "overlap (e.g. the ATT, or an overlap-weighted effect).",
         ],
         "callout": {"title": "Extreme weights are a diagnosis, not a nuisance",
            "color": "RED",
            "lines": ["Reaching for truncation before you understand WHY the "
                      "weights are large hides a positivity problem instead of "
                      "solving it.",
                      "First look at the propensity overlap. If an arm is empty "
                      "in some region, no weight can conjure the missing "
                      "counterfactual — only a different estimand or new data can."]}},
        {"heading": "Marginal structural models & augmented IPW",
         "body": "A marginal structural model (MSM) is just a model for the "
            "potential-outcome means — e.g. E[Y(t)] = β0 + β1·t — fit by weighted "
            "regression using IP weights. MSMs shine with time-varying treatments "
            "and time-varying confounders, where standard regression adjustment "
            "is biased and weighting is the natural fix. Augmented IPW (AIPW) "
            "combines the weights with an outcome model and earns the doubly "
            "robust property.",
         "bullets": [
            [("AIPW estimator:  ", {"bold": True}),
             ("predict the outcome with a model, then add an "
              "IPW-weighted correction of its residuals. The correction term has "
              "mean zero if EITHER model is right.", {})],
            [("Double robustness:  ", {"bold": True}),
             ("consistent if the propensity model is correct OR the outcome model "
              "is correct (not necessarily both). Two shots at the truth.", {})],
            [("A first look at targeted learning:  ", {"bold": True}),
             ("TMLE goes further — it uses flexible machine learning for both "
              "nuisance models and a targeting step to remove plug-in bias, while "
              "keeping valid inference. AIPW is the doorway to it.", {})],
         ]},
    ],
    "problem_set": {
        "label": "Problem Set 5",
        "title": "Weights, overlap, and double robustness",
        "intro": "Five problems on the logic of weighting. Work each by hand "
            "before checking the solution; the notebook lets you verify your "
            "answers numerically.",
        "problems": [
            {"title": "Derive the IPW estimator",
             "prompt": "Let e(X) = P(T=1 | X) be the propensity score. Show that, "
                "under conditional exchangeability and positivity, "
                "E[ T·Y / e(X) ] = E[Y(1)]. Then write the analogous expression "
                "for E[Y(0)] and state the IPW estimator of the ATE. Explain in "
                "one sentence why each step needs the assumption it uses.",
             "solution_title": "Weighting by 1/e undoes the confounded sampling, "
                "so the weighted treated mean equals E[Y(1)].",
             "solution": [
                "By consistency, for a treated unit Y = Y(1). Condition on X and "
                "use the tower rule: E[ T·Y(1) / e(X) ] = E[ E[T | X, Y(1)] · "
                "Y(1) / e(X) ].",
                "Exchangeability gives T ⫫ Y(1) | X, so E[T | X, Y(1)] = "
                "E[T | X] = e(X). The e(X) cancels, leaving E[ Y(1) ] — provided "
                "positivity makes e(X) > 0 so the division is defined.",
                "Symmetrically E[ (1−T)·Y / (1−e(X)) ] = E[Y(0)], needing "
                "e(X) < 1. The ATE estimator is the sample analogue: the average "
                "of T·Y/ê minus the average of (1−T)·Y/(1−ê).",
                "Each assumption pulls its weight: exchangeability lets E[T|X] "
                "replace E[T|X,Y(1)]; positivity keeps the weights finite."]},
            {"title": "Stabilized vs. unstabilized weights",
             "prompt": "Unstabilized weights are 1/e and 1/(1−e); stabilized "
                "weights multiply these by the marginals P(T=1) and P(T=0). Both "
                "give the same large-sample ATE, so why bother stabilizing? State "
                "what changes and what does not, and predict the mean of a "
                "correctly stabilized weight.",
             "solution_title": "Stabilization shrinks weight variance without "
                "changing the estimand; stabilized weights have mean ≈ 1.",
             "solution": [
                "Multiplying by the constant marginal P(T=t) rescales every "
                "weight in an arm by the same factor, so the (Hájek, "
                "self-normalizing) point estimate is unchanged in expectation.",
                "What changes is the spread: a unit with e = 0.02 has weight 50 "
                "unstabilized but ≈ 50·P(T=1) stabilized — much closer to 1. "
                "Smaller spread means smaller variance and a larger effective "
                "sample size.",
                "A correctly specified stabilized weight has expectation 1 (each "
                "arm's weights average to about 1). A mean far from 1 is a red "
                "flag that the propensity model is misspecified.",
                "Stabilization is essentially free insurance, which is why it is "
                "the default — especially for marginal structural models."]},
            {"title": "What extreme weights signal",
             "prompt": "In an analysis, one control unit receives an IP weight of "
                "180 while the median weight is about 1.1. A colleague proposes "
                "simply deleting that unit. Diagnose what the large weight means, "
                "and critique the proposed fix.",
             "solution_title": "A near-positivity violation — deleting the unit "
                "hides the problem and biases the estimate.",
             "solution": [
                "Weight 180 for a control means 1/(1−e) ≈ 180, i.e. e ≈ 0.994: "
                "this unit's covariate profile is almost always treated. It is a "
                "lone control standing in for a region with virtually no controls "
                "— a near-positivity violation.",
                "It carries enormous influence: the effective sample size "
                "collapses and the variance balloons, so the estimate is fragile.",
                "Deleting it silently changes the estimand (you drop part of the "
                "covariate space) and understates the uncertainty. That is "
                "sweeping a structural problem under the rug.",
                "Better: inspect the propensity overlap, then either truncate "
                "transparently (and report it), or redefine the estimand to the "
                "region of common support (ATT or overlap weights)."]},
            {"title": "The doubly robust property — which model may be wrong",
             "prompt": "The AIPW estimator combines a propensity model ê(X) and "
                "an outcome model m̂(X). State precisely the sense in which it is "
                "'doubly robust': which of the two models is allowed to be "
                "misspecified, and what happens if both are wrong?",
             "solution_title": "Consistent if EITHER model is correct; fails only "
                "if BOTH are wrong.",
             "solution": [
                "AIPW = (outcome-model prediction) + (IPW-weighted correction of "
                "its residuals). The correction term's expectation is zero "
                "whenever the propensity model is right, so the outcome model can "
                "be arbitrary and the estimator is still consistent.",
                "Conversely, if the outcome model is right, the residuals it "
                "leaves have mean zero, so the correction vanishes in expectation "
                "and the estimator is consistent even if the propensity model is "
                "wrong.",
                "You only need to win ONE of the two bets — two independent "
                "chances to get the answer right.",
                "If BOTH are misspecified, double robustness gives no guarantee "
                "and AIPW is generally biased. 'Doubly robust' is not "
                "'assumption-free.'"]},
            {"title": "Why truncation trades bias for variance",
             "prompt": "Capping weights at the 99th percentile clearly reduces "
                "variance. Explain why it also introduces bias, and describe the "
                "shape of the bias–variance trade-off as you lower the truncation "
                "threshold from the 99th toward, say, the 90th percentile.",
             "solution_title": "Capping shrinks influential units toward the "
                "crowd, biasing the estimate but stabilizing it — a tunable dial.",
             "solution": [
                "The Horvitz–Thompson/Hájek estimator is unbiased only with the "
                "true weights. Replacing a weight of 180 with the cap of, say, 30 "
                "under-counts the rare covariate region that unit represents, so "
                "the weighted mean no longer targets the full-population estimand "
                "— that mismatch is the bias.",
                "But those same huge weights were the variance drivers; capping "
                "them sharply lowers the variance and raises the effective sample "
                "size.",
                "Lowering the threshold (99th → 95th → 90th) caps more and more "
                "units: bias grows monotonically while variance keeps falling. "
                "The mean-squared error is U-shaped, minimized at an interior "
                "cut-point.",
                "So truncation is a deliberate bias-for-variance bargain. Report "
                "the threshold and show a sensitivity curve rather than picking "
                "one cap silently."]},
        ],
    },
    "lab": {
        "label": "Lab 4",
        "title": "IPW & AIPW on a confounded cohort",
        "goal": "estimate a treatment effect by inverse-probability weighting, "
            "diagnose and tame the weights, and then build the doubly robust "
            "augmented estimator and compare the two. Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Estimate a propensity score",
             "body": "Fit a model for P(T=1 | X) on the confounders. Save the "
                "fitted probabilities ê; they are the engine of every weight you "
                "build today.",
             "code_python": "import numpy as np\n"
                "from sklearn.linear_model import LogisticRegression\n"
                "ps = LogisticRegression(max_iter=2000).fit(X, T)\n"
                "e  = np.clip(ps.predict_proba(X)[:, 1], 1e-3, 1 - 1e-3)",
             "code_r": 'ps <- glm(T ~ X1 + X2 + X1:X2, family = binomial,\n'
                '           data = df)\n'
                'e  <- pmin(pmax(fitted(ps), 1e-3), 1 - 1e-3)'},
            {"heading": "Step 2 · Form IPW (ATE) and stabilized weights",
             "body": "Unstabilized ATE weights are 1/ê for the treated and "
                "1/(1−ê) for the controls. Stabilized weights multiply by the "
                "marginal treatment probabilities and should average to ≈ 1.",
             "code_python": "w   = np.where(T == 1, 1/e, 1/(1 - e))\n"
                "pT  = T.mean()\n"
                "sw  = np.where(T == 1, pT/e, (1 - pT)/(1 - e))\n"
                "print('mean stabilized weight ~', round(sw.mean(), 3))",
             "code_r": 'w  <- ifelse(df$T == 1, 1/e, 1/(1 - e))\n'
                'pT <- mean(df$T)\n'
                'sw <- ifelse(df$T == 1, pT/e, (1 - pT)/(1 - e))\n'
                '# Or use WeightIt directly:\n'
                'library(WeightIt)\n'
                'W <- weightit(T ~ X1 + X2, data = df, method = "ps",\n'
                '              estimand = "ATE", stabilize = TRUE)'},
            {"heading": "Step 3 · Check the weight distribution",
             "body": "Always look before you estimate. Plot the weights, report "
                "the maximum, and overlay the propensity histograms by arm to spot "
                "regions of poor overlap.",
             "code_python": "import matplotlib.pyplot as plt\n"
                "print('max raw / stabilized weight:', round(w.max(), 1),\n"
                "      '/', round(sw.max(), 1))\n"
                "fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))\n"
                "ax[0].hist(w, bins=40);  ax[0].set_title('raw IPW weights')\n"
                "ax[1].hist(sw, bins=40); ax[1].set_title('stabilized')",
             "code_r": 'library(cobalt)\n'
                'summary(W)                # weight summaries & effective N\n'
                'bal.plot(W, var.name = "prop.score", which = "both")'},
            {"heading": "Step 4 · Estimate the ATE by weighting",
             "body": "Use the Hájek (self-normalizing) form for stability. "
                "Compare with the Horvitz–Thompson version and with a truncated "
                "weight to see the bias–variance trade-off.",
             "code_python": "def hajek(weight):\n"
                "    a = np.sum(weight*T*Y)     / np.sum(weight*T)\n"
                "    b = np.sum(weight*(1-T)*Y) / np.sum(weight*(1-T))\n"
                "    return a - b\n"
                "ht  = (T*Y/e).mean() - ((1-T)*Y/(1-e)).mean()\n"
                "print('Horvitz-Thompson:', round(ht, 3),\n"
                "      ' Hajek:', round(hajek(w), 3))",
             "code_r": 'library(survey)\n'
                'des <- svydesign(ids = ~1, weights = ~sw, data = df)\n'
                'coef(svyglm(Y ~ T, design = des))["T"]   # MSM slope = ATE'},
            {"heading": "Step 5 · Build the AIPW / doubly robust estimator",
             "body": "Fit outcome models m̂₁(X), m̂₀(X) on treated and controls, "
                "then add the IPW correction of their residuals. Compare to plain "
                "IPW — and deliberately break one model to watch AIPW survive.",
             "code_python": "from sklearn.linear_model import LinearRegression\n"
                "m1 = LinearRegression().fit(X[T==1], Y[T==1]).predict(X)\n"
                "m0 = LinearRegression().fit(X[T==0], Y[T==0]).predict(X)\n"
                "psi1 = m1 + T*(Y - m1)/e\n"
                "psi0 = m0 + (1 - T)*(Y - m0)/(1 - e)\n"
                "aipw = (psi1 - psi0).mean()\n"
                "print('AIPW (doubly robust) ATE:', round(aipw, 3))",
             "code_r": 'library(AIPW)\n'
                'dr <- AIPW$new(Y = df$Y, A = df$T,\n'
                '               W = df[, c("X1","X2")],\n'
                '               Q.SL.library = "SL.lm",\n'
                '               g.SL.library = "SL.glm")$fit()$summary()'},
        ],
        "expected": "Plain IPW with a good propensity model recovers the known "
            "ATE; the naive difference in means does not. The weight histogram is "
            "right-skewed with a long tail, which stabilization shortens. AIPW "
            "lands on the truth too — and, crucially, keeps doing so when you "
            "misspecify just one of its two models. Break both and it finally "
            "fails: that is double robustness made visible.",
        "submit": [
            "Push your notebook plus a short README reporting the naive, IPW "
            "(Horvitz–Thompson and Hájek), and AIPW estimates against the known "
            "truth, with the weight histogram.",
            "Include the three-case AIPW table (PS wrong / outcome wrong / both "
            "wrong) and one sentence interpreting it.",
            "Note the maximum weight before and after stabilization and whether "
            "you truncated.",
        ],
    },
    "self_check": [
        "Explain, without notes, why weighting by 1/e builds a pseudo-population "
        "in which treatment is unconfounded.",
        "State the two assumptions IPW needs and what a weight of 1/0 would mean.",
        "Say when you'd prefer Hájek over Horvitz–Thompson, and what a stabilized "
        "weight should average to.",
        "Describe the doubly robust property in one sentence: which model may be "
        "wrong, and when AIPW finally fails.",
        "Give two distinct responses to extreme weights and the cost of each.",
    ],
    "next_week": {
        "heading": "Coming up: Week 8 — Instrumental variables & Mendelian "
                   "randomization",
        "teaser": "Adjustment and weighting both assume no unmeasured "
            "confounding. Next week we drop that assumption and lean on an "
            "instrument — a variable that moves treatment but affects the outcome "
            "only through it. You'll meet the exclusion restriction, two-stage "
            "least squares, the local ATE for compliers, and Mendelian "
            "randomization, where a genetic variant plays the instrument. Skim "
            "Hernán & Robins Chapter 16 to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 7", "items": [
            {"t": "From matching to weighting", "d": "Reweighting builds a "
             "pseudo-population where treatment is unconfounded."},
            {"t": "The IPW estimator", "d": "Weight by 1/P(observed treatment | "
             "X); HT vs Hájek."},
            {"t": "Stabilized & truncated weights", "d": "Shrink the tail without "
             "changing the question."},
            {"t": "Extreme weights & positivity", "d": "A diagnosis, not a "
             "nuisance — overlap is everything."},
            {"t": "Marginal structural models", "d": "Weighting's home turf: "
             "time-varying treatments."},
            {"t": "AIPW & doubly robust", "d": "Two shots at the truth; a first "
             "look at targeted learning."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Block II so far — three ways to adjust", "bullets": [
            "Regression & control: model the outcome's dependence on confounders.",
            "Matching & propensity scores: build comparable treated/control sets.",
            "This week — weighting: reweight the sample so confounders no longer "
            "predict treatment.",
            ("All three need the same currency: no unmeasured confounding plus "
             "positivity.", 1),
            "Weighting is also the gateway to doubly robust and modern ML "
            "estimators.",
         ],
         "note": {"title": "The throughline",
            "body": "Same assumptions, different machinery. Weighting will hand us "
            "the cleanest path to double robustness."}},
        {"type": "statement",
         "quote": "Don't model the outcome — reweight the world until treatment "
            "looks random.",
         "attribution": "Inverse-probability weighting attacks confounding from "
            "the treatment side, not the outcome side. That single shift unlocks "
            "marginal structural models and doubly robust estimation."},

        {"type": "section", "kicker": "Part 1",
         "title": "Weighting & the pseudo-population",
         "subtitle": "Up-weight the under-represented covariate profiles until the "
            "treated and control groups are interchangeable."},
        {"type": "content", "kicker": "The core idea",
         "title": "Inverse-probability weighting", "bullets": [
            "Each unit gets weight 1 / P(the treatment it actually received | X).",
            "Treated unit: weight 1/e. Control unit: weight 1/(1−e).",
            "Rare-but-observed profiles stand in for the copies we didn't see.",
            "In the reweighted pseudo-population, treatment ⫫ confounders.",
            ("So a simple weighted difference in means estimates the ATE.", 1),
         ],
         "note": {"title": "Propensity score",
            "body": "e(X) = P(T=1 | X), the same score we matched on last week — "
            "now it powers the weights."}},
        {"type": "content", "kicker": "Intuition",
         "title": "What the weights actually do", "bullets": [
            "A treated unit with e = 0.1 was unlikely to be treated → weight 10, "
            "it represents ~10 similar units.",
            "A treated unit with e = 0.9 was almost certain to be treated → "
            "weight ~1.1, it represents mostly itself.",
            "Weighting manufactures the missing counterfactual copies from the "
            "units we did observe.",
            "Up-weighting the under-represented profiles balances the two arms.",
         ],
         "note": {"title": "Picture it",
            "body": "Weighting stretches and shrinks the sample until the "
            "covariate distributions of treated and control coincide."}},
        {"type": "compare", "kicker": "Two assumptions, no free lunch",
         "title": "What IPW needs to be valid", "columns": [
            {"head": "Exchangeability", "sub": "no unmeasured confounding",
             "points": [
                "Within X, treatment is as good as random.",
                "Lets E[T|X] = e(X) replace the unknowable.",
                "Untestable — argue it from the DAG."]},
            {"head": "Positivity", "sub": "overlap", "points": [
                "0 < e(X) < 1 for every covariate profile.",
                "Else a weight is 1/0 — undefined.",
                "Checkable: look at the propensity overlap."]},
            {"head": "Consistency / SUTVA", "sub": "well-defined treatment",
             "points": [
                "Observed Y equals the potential outcome under the received arm.",
                "No interference between units.",
                "Same backbone as every method this term."]},
         ]},

        {"type": "section", "kicker": "Part 2",
         "title": "The IPW estimator",
         "subtitle": "From weights to a number: Horvitz–Thompson, Hájek, and the "
            "weighted regression that gives the same answer."},
        {"type": "content", "kicker": "Derivation in one line",
         "title": "Why the weighted treated mean is E[Y(1)]", "bullets": [
            "E[ T·Y / e(X) ] = E[ E[T|X]·Y(1) / e(X) ] by exchangeability.",
            "E[T|X] = e(X) cancels the weight, leaving E[Y(1)].",
            "Symmetrically, (1−T)·Y / (1−e) averages to E[Y(0)].",
            ("ATE = mean of T·Y/e − mean of (1−T)·Y/(1−e).", 1),
            "Positivity is what keeps both denominators away from zero.",
         ],
         "note": {"title": "Estimand",
            "body": "This targets the ATE over the whole population — every "
            "profile is represented in the pseudo-population."}},
        {"type": "compare", "kicker": "Two estimators, one idea",
         "title": "Horvitz–Thompson vs. Hájek", "columns": [
            {"head": "Horvitz–Thompson", "sub": "divide by n", "points": [
                "mean(T·Y/e) − mean((1−T)·Y/(1−e)).",
                "Exactly unbiased.",
                "High variance; weights needn't sum to n."]},
            {"head": "Hájek", "sub": "divide by Σ weights", "points": [
                "Self-normalizing ratio in each arm.",
                "Slightly biased, much more stable.",
                "What stabilized weights deliver."]},
         ]},
        {"type": "steps", "kicker": "The IPW recipe",
         "title": "Five steps from data to an effect", "steps": [
            {"title": "Model treatment", "body": "— fit e(X) = P(T=1 | X)."},
            {"title": "Form weights", "body": "— 1/e for treated, 1/(1−e) for "
             "controls."},
            {"title": "Check weights", "body": "— distribution, max, effective "
             "sample size."},
            {"title": "Weighted mean", "body": "— Hájek difference across arms."},
            {"title": "Inference", "body": "— robust/sandwich or bootstrap "
             "standard errors."},
         ],
         "note": "A weighted regression of Y on T reproduces the same ATE — and "
            "generalizes to a marginal structural model."},

        {"type": "section", "kicker": "Part 3",
         "title": "Stabilized & truncated weights",
         "subtitle": "Taming the tail: shrink the variance of the weights without "
            "changing what you are estimating."},
        {"type": "content", "kicker": "Stabilization",
         "title": "Multiply by the marginal — get mean-one weights", "bullets": [
            "Stabilized weight = P(T=t) / P(T=t | X), versus 1 / P(T=t | X).",
            "Same large-sample estimand; far smaller weight variance.",
            "Correctly specified, stabilized weights average to ≈ 1 — a built-in "
            "diagnostic.",
            "The default for marginal structural models.",
         ],
         "note": {"title": "Sanity check",
            "body": "Mean stabilized weight far from 1? Your propensity model is "
            "probably misspecified."}},
        {"type": "content", "kicker": "Truncation",
         "title": "Cap the extremes — on purpose", "bullets": [
            "Clip weights at, e.g., the 1st and 99th percentiles.",
            "Variance drops sharply; a small bias is introduced.",
            "Lower the cap → more bias, less variance: MSE is U-shaped.",
            ("Report the threshold and a sensitivity curve — never cap "
             "silently.", 1),
         ],
         "note": {"title": "Trade-off",
            "body": "Truncation is a deliberate bias-for-variance bargain, not a "
            "bug fix."}},
        {"type": "table", "kicker": "Same data, three weightings",
         "title": "What stabilizing and truncating do to the tail",
         "headers": ["Weighting", "Mean", "Max weight", "Effect on estimate"],
         "rows": [
            ["Unstabilized (1/e)", "≈ 2.0", "very large", "unbiased, high var"],
            ["Stabilized", "≈ 1.0", "moderate", "unbiased, lower var"],
            ["Truncated @ 99th", "≈ 1.9", "capped", "small bias, lowest var"],
         ],
         "note": {"title": "Read the tail",
            "body": "The max weight is the headline number — it tells you how "
            "fragile the estimate is."}},

        {"type": "section", "kicker": "Part 4",
         "title": "Extreme weights & positivity",
         "subtitle": "When the weights explode, the data are telling you an arm is "
            "nearly empty somewhere. Listen."},
        {"type": "content", "kicker": "The symptom",
         "title": "Extreme weights are positivity screaming", "bullets": [
            "A weight of 180 means a propensity of ~0.994 — that profile is almost "
            "never in the other arm.",
            "One huge weight can dominate the estimate; effective sample size "
            "collapses.",
            "The cause is structural: poor overlap, not a coding bug.",
            "Diagnose first — plot the propensity histograms by arm.",
         ],
         "note": {"title": "Effective N",
            "body": "(Σw)² / Σw² tells you how many 'real' observations your "
            "weights are worth. Watch it fall."}},
        {"type": "compare", "kicker": "Positivity: detect, then respond",
         "title": "Your menu when overlap is poor", "columns": [
            {"head": "Detect", "points": [
                "Propensity histograms by arm.",
                "Max weight & effective sample size.",
                "Regions with e near 0 or 1."]},
            {"head": "Respond — cheap", "points": [
                "Stabilize the weights.",
                "Truncate transparently and report it.",
                "Bootstrap to show the fragility."]},
            {"head": "Respond — honest", "points": [
                "Redefine the estimand (ATT, overlap weights).",
                "Restrict to the region of common support.",
                "Concede the question is unanswerable here."]},
         ]},
        {"type": "statement",
         "quote": "No weight can conjure a counterfactual that the data never "
            "observed.",
         "attribution": "If an arm is empty in some covariate region, positivity "
            "fails there. Truncation hides it; a redefined estimand confronts it "
            "honestly."},

        {"type": "section", "kicker": "Part 5",
         "title": "Marginal structural models",
         "subtitle": "Weighting's killer app: time-varying treatments and "
            "time-varying confounders, where regression adjustment is biased."},
        {"type": "content", "kicker": "Definition",
         "title": "A model for the potential-outcome means", "bullets": [
            "An MSM models E[Y(t)] directly, e.g. E[Y(t)] = β0 + β1·t.",
            "Fit by weighted regression using (stabilized) IP weights.",
            "The slope β1 is the ATE in the pseudo-population.",
            "Extends naturally to a treatment history over many time points.",
         ],
         "note": {"title": "Why 'marginal'",
            "body": "It models the marginal (population) potential-outcome mean, "
            "not an outcome conditional on confounders."}},
        {"type": "content", "kicker": "The case for weighting",
         "title": "Why time-varying confounding breaks regression", "bullets": [
            "A confounder affected by past treatment is both a confounder and a "
            "mediator.",
            "Adjusting for it in regression blocks part of the effect (it's a "
            "mediator) yet leaving it out confounds (it's a confounder).",
            "No single regression can win — conditioning is the wrong tool.",
            "IP weighting sidesteps the trap by reweighting on treatment history "
            "instead of conditioning.",
         ],
         "note": {"title": "Epidemiology case",
            "body": "Classic example: time-varying drug exposure in a cohort, "
            "with a biomarker that both responds to and drives future dosing."}},
        {"type": "steps", "kicker": "Case · a time-varying treatment in a cohort",
         "title": "MSM for a longitudinal exposure", "steps": [
            {"title": "Exposure history", "body": "— treatment can switch on/off "
             "over visits."},
            {"title": "Time-varying confounder", "body": "— a biomarker driven by "
             "past treatment and driving future treatment."},
            {"title": "Stabilized weights", "body": "— product of visit-by-visit "
             "treatment probabilities."},
            {"title": "Fit the MSM", "body": "— weighted regression of the outcome "
             "on cumulative exposure."},
         ],
         "note": "Regression adjustment is biased here; weighting is the standard "
            "fix (Robins, Hernán & Brumback 2000)."},

        {"type": "section", "kicker": "Part 6",
         "title": "AIPW & doubly robust estimation",
         "subtitle": "Combine the propensity model and an outcome model so that "
            "getting EITHER one right is enough."},
        {"type": "content", "kicker": "The estimator",
         "title": "Augmented IPW = outcome model + weighted correction",
         "bullets": [
            "Start from the outcome-model prediction m̂(X).",
            "Add an IPW-weighted correction of its residuals (Y − m̂).",
            "The correction has mean zero if the propensity model is correct.",
            "The residuals have mean zero if the outcome model is correct.",
            ("Either way, one of the two pieces saves you.", 1),
         ],
         "note": {"title": "Plug-and-play",
            "body": "Any regressor for m̂ and any classifier for ê slot in — "
            "including flexible machine learning."}},
        {"type": "compare", "kicker": "The promise, stated precisely",
         "title": "What 'doubly robust' does and doesn't mean", "columns": [
            {"head": "Consistent if…", "points": [
                "Propensity model correct (outcome model wrong), OR",
                "Outcome model correct (propensity model wrong).",
                "Two independent shots at the truth."]},
            {"head": "Fails if…", "points": [
                "BOTH models are misspecified.",
                "Positivity is violated (no weights help).",
                "'Doubly robust' ≠ 'assumption-free.'"]},
        ]},
        {"type": "table", "kicker": "Double robustness, made visible",
         "title": "AIPW recovers the truth unless BOTH models are wrong",
         "headers": ["Propensity model", "Outcome model", "AIPW recovers ATE?"],
         "rows": [
            ["correct", "correct", "yes"],
            ["WRONG", "correct", "yes — outcome model rescues it"],
            ["correct", "WRONG", "yes — propensity model rescues it"],
            ["WRONG", "WRONG", "no — biased"],
         ],
         "note": {"title": "You'll prove this in the notebook",
            "body": "All four rows are demonstrated on simulated data with a "
            "known ATE."}},
        {"type": "content", "kicker": "Looking ahead",
         "title": "A first look at targeted learning", "bullets": [
            "AIPW is the doorway to TMLE (targeted maximum likelihood "
            "estimation).",
            "TMLE uses flexible ML for both nuisance models, plus a targeting "
            "step that removes plug-in bias.",
            "It keeps valid confidence intervals despite the machine learning.",
            "Same doubly robust spirit, with a sharper inference guarantee.",
         ],
         "note": {"title": "Week 12 preview",
            "body": "Double/debiased ML formalizes this: cross-fitting + "
            "Neyman-orthogonal scores. AIPW is the first orthogonal estimator you "
            "meet."}},

        {"type": "section", "kicker": "Part 7",
         "title": "Putting it together",
         "subtitle": "A workflow you can defend, and the habits that keep "
            "weighting honest."},
        {"type": "steps", "kicker": "The weighting workflow",
         "title": "From question to a defensible estimate", "steps": [
            {"title": "Estimand", "body": "— ATE, ATT, or an overlap-weighted "
             "effect?"},
            {"title": "Propensity", "body": "— fit and CHECK overlap before "
             "weighting."},
            {"title": "Weights", "body": "— stabilize; truncate only if you "
             "report it."},
            {"title": "Estimate", "body": "— Hájek IPW, then AIPW for "
             "robustness."},
            {"title": "Stress-test", "body": "— vary the truncation; bootstrap "
             "the interval."},
         ],
         "note": "If IPW and AIPW disagree sharply, suspect a misspecified "
            "propensity model or a positivity problem."},
        {"type": "compare", "kicker": "One-slide summary",
         "title": "When to reach for which tool", "columns": [
            {"head": "Plain IPW", "points": [
                "Transparent; one model to defend.",
                "Good overlap, trustworthy propensity.",
                "Vulnerable if e(X) is wrong."]},
            {"head": "AIPW / doubly robust", "points": [
                "Two models, two chances to be right.",
                "Default when unsure which to trust.",
                "Pairs naturally with ML nuisances."]},
            {"head": "Marginal structural model", "points": [
                "Time-varying treatment & confounding.",
                "Weighted regression of Y on exposure.",
                "Where regression adjustment fails."]},
         ]},
        {"type": "statement",
         "quote": "Weight to balance, augment to be safe, and always look at the "
            "tail of your weights.",
         "attribution": "This week: estimate an ATE by IPW, watch stabilization "
            "and truncation tame the weights, and prove double robustness to "
            "yourself on data with a known answer. See you in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A confounded cohort with a known answer\n\n"
            "We simulate an epidemiological-style cohort with two covariates "
            "`X1, X2` that **confound** a treatment `T` and an outcome `Y`. The "
            "confounding is deliberately **nonlinear**, because that is what makes "
            "weighting (and double robustness) earn their keep. The **true ATE is "
            "exactly 3.0** — we'll keep checking our estimates against it.\n\n"
            "Because treatment and outcome share the same nonlinear drivers, the "
            "naive difference in means will be badly biased."},
        {"code": "from sklearn.linear_model import LogisticRegression, LinearRegression\n\n"
            "TRUE_ATE = 3.0\n"
            "n = 20_000\n\n"
            "def simulate(n):\n"
            "    X1 = RNG.uniform(-2, 2, n)\n"
            "    X2 = RNG.uniform(-2, 2, n)\n"
            "    # nonlinear, strong confounding of TREATMENT\n"
            "    logit_e = 1.4*np.sin(1.5*X1) + 1.2*(X2**2 - 1.0) - 0.5\n"
            "    e_true  = 1/(1 + np.exp(-logit_e))\n"
            "    T = RNG.binomial(1, e_true)\n"
            "    # nonlinear, strong confounding of OUTCOME; additive effect = TRUE_ATE\n"
            "    mu0 = 2.0*np.sin(1.5*X1) + 2.0*X2**2 + 1.0*X1\n"
            "    Y = mu0 + TRUE_ATE*T + RNG.normal(size=n)\n"
            "    return pd.DataFrame({'X1': X1, 'X2': X2, 'T': T, 'Y': Y}), e_true\n\n"
            "df, e_true = simulate(n)\n"
            "T = df['T'].to_numpy()\n"
            "Y = df['Y'].to_numpy()\n"
            "print(f'n = {n},  treated fraction = {T.mean():.3f}')\n"
            "print(f'true propensity range: [{e_true.min():.3f}, {e_true.max():.3f}]')\n"
            "print(f'TRUE ATE = {TRUE_ATE}')"},
        {"md": "### The naive estimate is biased\n\n"
            "Compare the treated and control means directly — ignoring that the "
            "two groups have very different covariate profiles."},
        {"code": "naive = Y[T == 1].mean() - Y[T == 0].mean()\n"
            "print(f'naive difference in means = {naive:6.3f}')\n"
            "print(f'true ATE                  = {TRUE_ATE:6.3f}')\n"
            "print(f'naive bias                = {naive - TRUE_ATE:+.3f}')\n"
            "assert abs(naive - TRUE_ATE) > 1.0, 'naive should be badly biased here'"},
        {"md": "## 2 · The propensity score & the pseudo-population\n\n"
            "We fit `e(X) = P(T=1 | X)` with logistic regression. To capture the "
            "nonlinear assignment we feed it a **rich basis** (`sin(1.5·X1)`, "
            "`X2²`, and the raw covariates) — this is our *correct* propensity "
            "model. We'll deliberately break it later.\n\n"
            "The inverse-probability weights are `1/e` for the treated and "
            "`1/(1−e)` for the controls. In the reweighted **pseudo-population**, "
            "treatment no longer tracks the confounders, so a weighted difference "
            "in means recovers the ATE."},
        {"code": "def ps_design(d, correct=True):\n"
            "    \"\"\"Feature matrix for the propensity model.\"\"\"\n"
            "    if correct:\n"
            "        return np.column_stack([np.sin(1.5*d['X1']), d['X2']**2,\n"
            "                                d['X1'], d['X2']])\n"
            "    return np.column_stack([d['X1'], d['X2']])   # misspecified: linear only\n\n"
            "def fit_propensity(d, correct=True):\n"
            "    m = LogisticRegression(max_iter=5000)\n"
            "    m.fit(ps_design(d, correct), d['T'])\n"
            "    e = m.predict_proba(ps_design(d, correct))[:, 1]\n"
            "    return np.clip(e, 1e-3, 1 - 1e-3)   # guard the weights\n\n"
            "e = fit_propensity(df, correct=True)\n"
            "print('estimated propensity range:', f'[{e.min():.3f}, {e.max():.3f}]')\n\n"
            "# inverse-probability weights for the ATE\n"
            "w = np.where(T == 1, 1/e, 1/(1 - e))\n"
            "print(f'weights: mean = {w.mean():.2f}, max = {w.max():.1f}')"},
        {"md": "### Estimate the ATE: Horvitz–Thompson vs. Hájek\n\n"
            "Two ways to take a weighted difference of means:\n\n"
            "- **Horvitz–Thompson** divides each arm's weighted sum by `n` "
            "(unbiased, higher variance).\n"
            "- **Hájek** divides by the *sum of the weights* in that arm "
            "(self-normalizing, more stable).\n\n"
            "Both should land near the true ATE of 3.0."},
        {"code": "def ipw_ht(weight):\n"
            "    \"\"\"Horvitz-Thompson: normalize by n.\"\"\"\n"
            "    return (weight*T*Y).mean() - (weight*(1 - T)*Y).mean()\n\n"
            "def ipw_hajek(weight):\n"
            "    \"\"\"Hajek: normalize each arm by its own weight total.\"\"\"\n"
            "    a = np.sum(weight*T*Y)       / np.sum(weight*T)\n"
            "    b = np.sum(weight*(1 - T)*Y) / np.sum(weight*(1 - T))\n"
            "    return a - b\n\n"
            "ht    = ipw_ht(w)\n"
            "hajek = ipw_hajek(w)\n"
            "print(f'Horvitz-Thompson IPW = {ht:6.3f}')\n"
            "print(f'Hajek IPW            = {hajek:6.3f}')\n"
            "print(f'true ATE             = {TRUE_ATE:6.3f}')\n"
            "assert abs(hajek - TRUE_ATE) < 0.25, 'Hajek IPW should recover ~3.0'\n"
            "assert abs(ht    - TRUE_ATE) < 0.35, 'HT IPW should recover ~3.0'"},
        {"md": "Weighting recovered the truth while the naive estimate did not. "
            "The pseudo-population — the sample reweighted by `w` — has balanced "
            "covariates, so the confounding is gone."},
        {"md": "### 🔧 Exercise 2.1 — confirm the pseudo-population is balanced\n\n"
            "If weighting works, the **weighted** mean of `X2²` should be nearly "
            "the same in the treated and control arms, even though the "
            "**unweighted** means differ (that imbalance is the confounding). "
            "Compute both and compare.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (the `...` are "
            "placeholders); replace them, then run the solution cell."},
        {"code": "feat = df['X2'].to_numpy()**2\n\n"
            "# Unweighted arm means of X2**2 (these should DIFFER -> confounding):\n"
            "unw_treated = feat[T == 1].mean()\n"
            "unw_control = feat[T == 0].mean()\n\n"
            "# TODO: weighted arm means of X2**2 using w (these should MATCH):\n"
            "wt_treated = ...   # TODO: np.sum(w*T*feat) / np.sum(w*T)\n"
            "wt_control = ...   # TODO: weighted control mean\n\n"
            "print('unweighted treated/control:', round(unw_treated, 3),\n"
            "      round(unw_control, 3))\n"
            "# print('weighted   treated/control:', round(wt_treated, 3),\n"
            "#       round(wt_control, 3))"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "wt_treated = np.sum(w*T*feat)     / np.sum(w*T)\n"
            "wt_control = np.sum(w*(1 - T)*feat) / np.sum(w*(1 - T))\n\n"
            "print(f'unweighted  treated={unw_treated:.3f}  control={unw_control:.3f}'\n"
            "      f'  gap={unw_treated - unw_control:+.3f}')\n"
            "print(f'weighted    treated={wt_treated:.3f}  control={wt_control:.3f}'\n"
            "      f'  gap={wt_treated - wt_control:+.3f}')\n"
            "assert abs(unw_treated - unw_control) > 0.2, 'confounding: arms should differ'\n"
            "assert abs(wt_treated - wt_control) < 0.1, 'weighting should balance X2**2'\n"
            "print('\\nWeighting balanced the covariate -> the pseudo-population works.')"},
        {"md": "## 3 · Diagnosing & taming the weights\n\n"
            "Weighting lives or dies by its **weight distribution**. A few huge "
            "weights mean a propensity near 0 or 1 — a near-**positivity** "
            "violation — and they inflate the variance. We look at three "
            "weightings:\n\n"
            "- **raw** unstabilized `1/e`, `1/(1−e)` (mean ≈ 2),\n"
            "- **stabilized** weights, multiplied by the marginal `P(T=t)` "
            "(mean ≈ 1),\n"
            "- **truncated** weights, capped at the 1st/99th percentile."},
        {"code": "pT = T.mean()\n"
            "# stabilized weights: multiply by the marginal treatment probability\n"
            "sw = np.where(T == 1, pT/e, (1 - pT)/(1 - e))\n\n"
            "# truncated (raw) weights: cap at the 1st / 99th percentile\n"
            "lo, hi = np.percentile(w, [1, 99])\n"
            "wt = np.clip(w, lo, hi)\n\n"
            "def eff_n(weight):\n"
            "    \"\"\"Kish effective sample size.\"\"\"\n"
            "    return weight.sum()**2 / np.sum(weight**2)\n\n"
            "for name, ww in [('raw 1/e', w), ('stabilized', sw), ('truncated@99', wt)]:\n"
            "    print(f'{name:14s}  mean={ww.mean():5.2f}  max={ww.max():6.1f}  '\n"
            "          f'eff_N={eff_n(ww):8.0f}')\n\n"
            "assert sw.max() < w.max(), 'stabilization should shrink the max weight'\n"
            "assert abs(sw.mean() - 1) < 0.1, 'stabilized weights should average ~1'"},
        {"code": "# Visualize the tail-taming. (No plt.show(); the figure is just created.)\n"
            "fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))\n"
            "ax[0].hist(w,  bins=50, color='#2F6DB5'); ax[0].set_title('raw 1/e (mean~2)')\n"
            "ax[1].hist(sw, bins=50, color='#2A9D8F'); ax[1].set_title('stabilized (mean~1)')\n"
            "ax[2].hist(wt, bins=50, color='#E9A23B'); ax[2].set_title('truncated @ 99th')\n"
            "for a in ax:\n"
            "    a.set_xlabel('weight'); a.set_ylabel('count')\n"
            "fig.tight_layout()\n"
            "print('Stabilization shortens the tail; truncation chops it off entirely.')"},
        {"md": "### Truncation trades bias for variance\n\n"
            "The truncated weights are biased — they under-count the rare "
            "profiles those large weights represented — but far less variable. "
            "Let's see the small bias appear in the point estimate."},
        {"code": "ate_raw   = ipw_hajek(w)\n"
            "ate_trunc = ipw_hajek(wt)\n"
            "print(f'IPW (raw weights)        = {ate_raw:6.3f}')\n"
            "print(f'IPW (truncated @ 99th)   = {ate_trunc:6.3f}')\n"
            "print(f'true ATE                 = {TRUE_ATE:6.3f}')\n"
            "print('\\nTruncation moved the estimate (a little bias) in exchange for\\n'\n"
            "      'much smaller weights (less variance) -- a deliberate bargain.')"},
        {"md": "### 🔧 Exercise 3.1 — sweep the truncation threshold\n\n"
            "Walk the truncation cap from gentle (99th percentile) to aggressive "
            "(80th). As you cap harder, the **bias should grow** (the estimate "
            "drifts from 3.0) while the **max weight shrinks** (variance falls). "
            "Build the table.\n\n"
            "Complete the `# TODO`s below."},
        {"code": "for q in [99, 95, 90, 80]:\n"
            "    hi_q = np.percentile(w, q)\n"
            "    w_q  = np.clip(w, None, hi_q)        # cap only the upper tail\n"
            "    ate_q  = ...     # TODO: ipw_hajek(w_q)\n"
            "    bias_q = ...     # TODO: ate_q - TRUE_ATE\n"
            "    # print(f'cap@{q:>2}th  max_w={w_q.max():6.1f}  ATE={ate_q:5.2f} '\n"
            "    #       f' bias={bias_q:+.2f}')"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "print(f'{\"cap\":>7} {\"max_w\":>8} {\"ATE\":>7} {\"bias\":>7}')\n"
            "for q in [99, 95, 90, 80]:\n"
            "    hi_q = np.percentile(w, q)\n"
            "    w_q  = np.clip(w, None, hi_q)\n"
            "    ate_q  = ipw_hajek(w_q)\n"
            "    bias_q = ate_q - TRUE_ATE\n"
            "    print(f'{q:>5}th {w_q.max():8.1f} {ate_q:7.2f} {bias_q:+7.2f}')\n\n"
            "# Aggressive capping shrinks the max weight but grows the bias.\n"
            "max_at_99 = np.clip(w, None, np.percentile(w, 99)).max()\n"
            "max_at_80 = np.clip(w, None, np.percentile(w, 80)).max()\n"
            "assert max_at_80 < max_at_99, 'capping harder must shrink the max weight'\n"
            "print('\\nbias-variance dial confirmed: tighter cap -> smaller weights, more bias.')"},
        {"md": "## 4 · AIPW: the doubly robust estimator\n\n"
            "Augmented IPW pairs the propensity weights with an **outcome model** "
            "`m̂₁(X), m̂₀(X)` (predictions of `Y` under treatment and control). "
            "The estimator for each potential-outcome mean is\n\n"
            "```\n"
            "psi1 = m1 + T*(Y - m1)/e          # E[Y(1)]\n"
            "psi0 = m0 + (1-T)*(Y - m0)/(1-e)  # E[Y(0)]\n"
            "AIPW = mean(psi1 - psi0)\n"
            "```\n\n"
            "The magic — **double robustness** — is that AIPW is consistent if "
            "**either** the propensity model **or** the outcome model is correct. "
            "We'll prove it by deliberately breaking one at a time."},
        {"code": "def fit_outcome(d, correct=True):\n"
            "    \"\"\"Return predictions m1(X), m0(X) from arm-specific linear models.\"\"\"\n"
            "    if correct:\n"
            "        feats = np.column_stack([np.sin(1.5*d['X1']), d['X2']**2,\n"
            "                                 d['X1'], d['X2']])\n"
            "    else:\n"
            "        feats = np.column_stack([d['X1'], d['X2']])   # misspecified: linear\n"
            "    tv, yv = d['T'].to_numpy(), d['Y'].to_numpy()\n"
            "    m1 = LinearRegression().fit(feats[tv == 1], yv[tv == 1]).predict(feats)\n"
            "    m0 = LinearRegression().fit(feats[tv == 0], yv[tv == 0]).predict(feats)\n"
            "    return m1, m0\n\n"
            "def aipw(e_hat, m1, m0):\n"
            "    psi1 = m1 + T*(Y - m1)/e_hat\n"
            "    psi0 = m0 + (1 - T)*(Y - m0)/(1 - e_hat)\n"
            "    return (psi1 - psi0).mean()\n\n"
            "# the 'both correct' baseline\n"
            "e_good = fit_propensity(df, correct=True)\n"
            "m1_good, m0_good = fit_outcome(df, correct=True)\n"
            "print(f'AIPW (both models correct) = {aipw(e_good, m1_good, m0_good):.3f}')\n"
            "print(f'true ATE                   = {TRUE_ATE:.3f}')"},
        {"md": "### Break one model at a time — and watch AIPW survive\n\n"
            "We now build a **wrong** propensity model and a **wrong** outcome "
            "model (both linear-only, blind to the `sin`/square structure). Then "
            "we run all four combinations. AIPW should recover ~3.0 in every case "
            "**except** when *both* models are wrong."},
        {"code": "e_bad = fit_propensity(df, correct=False)        # wrong PS\n"
            "m1_bad, m0_bad = fit_outcome(df, correct=False)      # wrong outcome\n\n"
            "cases = {\n"
            "    'both correct      ': aipw(e_good, m1_good, m0_good),\n"
            "    'PS wrong, OM right': aipw(e_bad,  m1_good, m0_good),\n"
            "    'PS right, OM wrong': aipw(e_good, m1_bad,  m0_bad),\n"
            "    'both wrong         ': aipw(e_bad,  m1_bad,  m0_bad),\n"
            "}\n"
            "print(f'{\"case\":20s} {\"AIPW\":>7} {\"|error|\":>9}')\n"
            "for name, val in cases.items():\n"
            "    print(f'{name:20s} {val:7.3f} {abs(val - TRUE_ATE):9.3f}')\n\n"
            "# Double robustness: one wrong model is fine; both wrong is not.\n"
            "assert abs(cases['PS wrong, OM right'] - TRUE_ATE) < 0.25, 'OM should rescue'\n"
            "assert abs(cases['PS right, OM wrong'] - TRUE_ATE) < 0.25, 'PS should rescue'\n"
            "assert abs(cases['both wrong         '] - TRUE_ATE) > 0.8, 'both wrong -> biased'\n"
            "print('\\nDouble robustness confirmed: AIPW survives ONE modeling mistake.')"},
        {"md": "### Why plain IPW is *not* doubly robust\n\n"
            "For contrast: plain IPW relies on the propensity model alone. With "
            "the **wrong** propensity model it has no outcome model to fall back "
            "on, so it is biased — exactly the situation AIPW rescues."},
        {"code": "ipw_wrong = ipw_hajek(np.where(T == 1, 1/e_bad, 1/(1 - e_bad)))\n"
            "aipw_rescued = cases['PS wrong, OM right']\n"
            "print(f'plain IPW, WRONG propensity        = {ipw_wrong:6.3f}  (biased)')\n"
            "print(f'AIPW, same wrong PS + right outcome = {aipw_rescued:6.3f}  (recovered)')\n"
            "print(f'true ATE                            = {TRUE_ATE:6.3f}')\n"
            "assert abs(ipw_wrong - TRUE_ATE) > 0.8, 'plain IPW with wrong PS is biased'\n"
            "assert abs(aipw_rescued - TRUE_ATE) < 0.25, 'AIPW recovers it'"},
        {"md": "### 🔧 Exercise 4.1 — AIPW collapses to its pieces\n\n"
            "A nice sanity check: if you set the outcome predictions to **zero** "
            "(`m1 = m0 = 0`), the AIPW formula reduces to the Horvitz–Thompson "
            "IPW estimator. Verify it numerically with the good propensity "
            "scores.\n\n"
            "Complete the `# TODO`."},
        {"code": "zeros = np.zeros(n)\n"
            "# TODO: AIPW with zero outcome predictions should equal HT-IPW.\n"
            "aipw_zero = ...   # TODO: aipw(e_good, zeros, zeros)\n"
            "ht_ref    = ipw_ht(np.where(T == 1, 1/e_good, 1/(1 - e_good)))\n"
            "# print(aipw_zero, ht_ref)"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "aipw_zero = aipw(e_good, zeros, zeros)\n"
            "ht_ref    = ipw_ht(np.where(T == 1, 1/e_good, 1/(1 - e_good)))\n"
            "print(f'AIPW with zero outcome model = {aipw_zero:.4f}')\n"
            "print(f'Horvitz-Thompson IPW         = {ht_ref:.4f}')\n"
            "assert abs(aipw_zero - ht_ref) < 1e-8, 'AIPW with m=0 must equal HT-IPW'\n"
            "print('Confirmed: AIPW = outcome model + IPW correction. '\n"
            "      'Zero out the model and only the IPW piece remains.')"},
        {"md": "## 5 · Wrap-up & self-check\n\n"
            "- **IPW** weights each unit by `1 / P(observed treatment | X)`, "
            "building a **pseudo-population** in which treatment is unconfounded. "
            "The naive estimate was badly biased; IPW recovered the true ATE of "
            "3.0.\n"
            "- **Horvitz–Thompson** (divide by `n`) is unbiased but noisier; "
            "**Hájek** (self-normalizing) is the stable default.\n"
            "- **Extreme weights** signal near-**positivity** violations. "
            "**Stabilization** gives mean-one weights; **truncation** trades a "
            "little bias for much less variance.\n"
            "- **AIPW is doubly robust**: it recovered 3.0 whenever the "
            "propensity model **or** the outcome model was right, and only failed "
            "when **both** were wrong.\n\n"
            "**You're ready for Week 8** if you can explain why weighting by 1/e "
            "removes confounding, name the two assumptions it needs, and state the "
            "doubly robust property in one sentence. Next week: instrumental "
            "variables and Mendelian randomization, where we finally drop the "
            "no-unmeasured-confounding assumption."},
    ],
}
