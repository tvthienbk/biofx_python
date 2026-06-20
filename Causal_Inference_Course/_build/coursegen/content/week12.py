# -*- coding: utf-8 -*-
"""Week 12 — Double / Debiased Machine Learning."""

WEEK = {
    "number": 12,
    "slug": "double_ml",
    "title": "Double / Debiased Machine Learning",
    "block": "Block IV — Modern methods & application",
    "subtitle": "Use flexible ML for the nuisance parts without letting it bias "
                "the effect you care about.",
    "deliverable": "Concept Set 12 — orthogonality & cross-fitting; "
                   "Lab 9 — partially-linear DML from scratch on high-dimensional "
                   "confounding.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), concept set (1.5h), lab (2–3h). The notebook is "
                    "the heart of the week — build the cross-fitted estimator by "
                    "hand and watch it beat the naive plug-in.",
    "one_sentence": "Double/debiased ML lets you throw a flexible learner at the "
        "nuisance functions — the parts of the model you do not care about — and "
        "still get an unbiased, normally-distributed estimate of the one effect "
        "you do, by combining a Neyman-orthogonal score with cross-fitting so that "
        "the learner's regularization bias and overfitting cannot leak into the "
        "target parameter.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Explain why naively plugging a regularized ML prediction into an "
        "adjustment formula biases the treatment-effect estimate, and name the two "
        "culprits: regularization bias and overfitting.",
        "State the Frisch–Waugh–Lovell idea and use it to motivate the "
        "residual-on-residual recipe at the core of the partially linear model.",
        "Define Neyman orthogonality and say, in words, what property of the score "
        "function makes the estimate first-order insensitive to small errors in "
        "the nuisance estimates.",
        "Describe cross-fitting (sample splitting) and explain precisely why it "
        "removes own-observation overfitting bias while keeping full efficiency.",
        "Implement the partially-linear DML estimator from scratch — cross-fit "
        "flexible models for E[Y|X] and E[D|X], residualize, regress — and recover "
        "a known effect with a valid standard error.",
        "Combine DML with an instrument for the partially-linear IV model, and "
        "state clearly what DML does NOT fix (unmeasured confounding).",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Chernozhukov et al. (2018), \"Double/Debiased Machine Learning "
                 "for Treatment and Structural Parameters.\"",
         "look_for": "why naive plug-in ML is biased and how orthogonalization + "
                     "cross-fitting fixes it — the two ingredients that make the "
                     "whole method work."},
        {"text": "DoubleML / EconML user guides.",
         "look_for": "the partially-linear-model recipe: residualize Y and D on X "
                     "with any learner, then regress the residuals to read off the "
                     "effect."},
    ],
    "optional_readings": [
        {"text": "Mullainathan & Spiess (2017), \"Machine Learning: An Applied "
                 "Econometric Approach.\"",
         "note": "Why prediction tools are not estimation tools — the cleanest "
                 "statement of the gap DML closes."},
        {"text": "Belloni, Chernozhukov & Hansen (2014), \"Inference on Treatment "
                 "Effects after Selection among High-Dimensional Controls.\"",
         "note": "The post-double-selection LASSO that pre-dates and motivates "
                 "DML; read it for the double-selection intuition."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "The setup: a partially linear model",
         "body": "We want the effect θ of a treatment D on an outcome Y, in the "
            "presence of a possibly huge set of confounders X. Write "
            "Y = θ·D + g(X) + ε and D = m(X) + v, where g and m are unknown, "
            "nonlinear, high-dimensional nuisance functions. The structure is "
            "'partially linear': linear in the parameter we care about (θ), "
            "arbitrary in the parts we do not (g, m). Classical adjustment would "
            "fit g(X) with OLS; modern data are too high-dimensional and too "
            "nonlinear for that, so we reach for flexible machine learning. The "
            "whole week is about doing so without letting the learner's biases "
            "contaminate θ."},
        {"heading": "Why naive plug-in ML is biased",
         "body": "The tempting move is to fit one flexible model of Y on (D, X) and "
            "read off the coefficient on D, or to predict ĝ(X) and regress the "
            "leftover on D. Both fail. A flexible learner is regularized — it "
            "trades a little bias for a lot of variance — and that regularization "
            "bias in ĝ does not vanish fast enough; it transmits directly into θ̂. "
            "On top of that, a model fit on the same rows it then predicts overfits "
            "them, so its residuals are too small and correlated with the noise.",
         "bullets": [
            [("Regularization bias:  ", {"bold": True}),
             ("LASSO, ridge, trees, and forests all shrink toward simplicity. "
              "That shrinkage in the nuisance estimate biases a naive plug-in of "
              "θ̂ at a rate that does not disappear quickly enough to ignore.", {})],
            [("Overfitting / leakage:  ", {"bold": True}),
             ("a model that has seen a row predicts it too well; the in-sample "
              "residual is artificially small and entangled with that row's noise, "
              "so own-observation error sneaks into the estimate.", {})],
            [("The fix is two-part:  ", {"bold": True}),
             ("orthogonalize the score so it ignores small nuisance errors, and "
              "cross-fit so no row is predicted by a model trained on it. Neither "
              "alone suffices.", {})],
         ],
         "callout": {"title": "Prediction is not estimation",
            "color": "RED",
            "lines": ["A learner tuned to minimize prediction error is not tuned "
                      "to give an unbiased coefficient. Low test MSE does not buy "
                      "you a trustworthy θ̂.",
                      "DML is precisely the bridge: keep the ML for prediction of "
                      "the nuisances, but estimate θ through an orthogonal, "
                      "cross-fitted score."]}},
        {"heading": "Frisch–Waugh–Lovell: residual on residual",
         "body": "The recipe at the heart of DML is older than ML. The "
            "Frisch–Waugh–Lovell (FWL) theorem says the OLS coefficient on D in a "
            "regression of Y on D and X equals the coefficient from regressing the "
            "part of Y not explained by X on the part of D not explained by X. In "
            "symbols: residualize Y by E[Y|X], residualize D by E[D|X], then "
            "regress one residual on the other. DML simply replaces the linear "
            "E[Y|X] and E[D|X] with flexible ML predictions.",
         "bullets": [
            [("Partial out X:  ", {"bold": True}),
             ("Ỹ = Y − Ê[Y|X] and D̃ = D − Ê[D|X] strip the confounding from both "
              "sides.", {})],
            [("Regress residuals:  ", {"bold": True}),
             ("θ̂ = (D̃ᵀỸ) / (D̃ᵀD̃) — the slope of the residualized outcome on the "
              "residualized treatment.", {})],
            [("Why it is clean:  ", {"bold": True}),
             ("with the confounding partialled out of D, the leftover variation in "
              "D̃ is as-good-as-random, so its association with Ỹ is the causal "
              "effect.", {})],
         ]},
        {"heading": "Neyman orthogonality: what it buys you",
         "body": "An estimating equation (score) ψ(W; θ, η) involves the target θ "
            "and the nuisance η = (g, m). It is Neyman-orthogonal if its expected "
            "value is insensitive — to first order — to small perturbations of η "
            "around the truth: the Gateaux derivative in the η direction is zero. "
            "Practically, that means a small error in the nuisance estimate moves "
            "θ̂ only at second order. The naive plug-in score is NOT orthogonal, so "
            "first-order nuisance error leaks straight into θ̂. The residual-on-"
            "residual score for the partially linear model IS orthogonal — that is "
            "why it survives slow, biased ML nuisances.",
         "bullets": [
            [("Orthogonal score:  ", {"bold": True}),
             ("ψ = (Y − ĝ − θ·(D − m̂))·(D − m̂). Its sensitivity to errors in ĝ "
              "and m̂ is zero at first order.", {})],
            [("The rate bargain:  ", {"bold": True}),
             ("orthogonality means nuisances only need to converge at a slow rate "
              "(roughly n^(−1/4)) for θ̂ to be √n-consistent and asymptotically "
              "normal — well within reach of forests, boosting, or LASSO.", {})],
            [("AIPW was your first orthogonal score:  ", {"bold": True}),
             ("the doubly robust estimator from Week 7 is the orthogonal score for "
              "the ATE. DML is the same idea made systematic, with cross-fitting "
              "added.", {})],
         ]},
        {"heading": "Cross-fitting: remove own-observation overfitting",
         "body": "Orthogonality controls regularization bias; cross-fitting "
            "controls overfitting. Split the sample into K folds. To form the "
            "residual for a row, use nuisance models trained on the OTHER folds — "
            "never the fold containing that row. No observation is ever predicted "
            "by a model that has seen it, so the entanglement between a row's "
            "residual and its own noise is broken. Averaging the K orthogonal "
            "score equations restores full efficiency; you lose nothing for the "
            "protection.",
         "bullets": [
            "Partition the data into K folds (K = 2–5 is typical).",
            "For each fold k: train nuisance models on the rows NOT in k, predict "
            "the rows IN k. Stack the out-of-fold residuals.",
            "Estimate θ from the pooled residuals; optionally repeat the random "
            "split and average for stability.",
            "Symptom of skipping it: in-sample residuals are far too small "
            "(the model memorized the rows), so the standard error is invalid.",
         ],
         "callout": {"title": "Orthogonality and cross-fitting are a pair",
            "color": "BLUE",
            "lines": ["Orthogonality alone still overfits; cross-fitting alone "
                      "still suffers regularization bias. You need both for valid "
                      "inference.",
                      "Together they let you use any sufficiently good learner as a "
                      "black box and still report an honest confidence interval."]}},
        {"heading": "Variations and the hard limit",
         "body": "The same machinery extends. The interactive model lets the "
            "effect differ by treatment arm and targets the ATE via the AIPW / "
            "doubly robust score — DML for the ATE. Add an instrument Z and you get "
            "the partially-linear IV model (PLIV): residualize Y, D, and Z on X, "
            "then do residual 2SLS. But none of this manufactures identification. "
            "DML is an estimation technology, not an identification one: if a "
            "confounder is unmeasured it is not in X, the orthogonal score is built "
            "around the wrong nuisances, and θ̂ is biased no matter how flexible the "
            "learner.",
         "bullets": [
            [("Partially linear (PLR):  ", {"bold": True}),
             ("constant effect θ; residual-on-residual.", {})],
            [("Interactive / ATE:  ", {"bold": True}),
             ("effect may vary; AIPW score cross-fitted for E[Y(1)] − E[Y(0)].", {})],
            [("Partially linear IV (PLIV):  ", {"bold": True}),
             ("endogenous D, instrument Z; residual 2SLS using the residualized "
              "instrument.", {})],
            [("DML does NOT fix:  ", {"bold": True}),
             ("unmeasured confounding, positivity violations, or a wrong causal "
              "graph. Garbage X in, biased θ out.", {})],
         ]},
    ],
    "problem_set": {
        "label": "Concept Set 12",
        "title": "Orthogonality & cross-fitting",
        "intro": "Five problems on the logic of debiased ML. Reason each through by "
            "hand before checking; the notebook lets you confirm every claim "
            "numerically on data with a known θ.",
        "problems": [
            {"title": "Why naive ML adjustment is biased",
             "prompt": "You fit a flexible learner ĝ(X) for E[Y|X], form the "
                "leftover R = Y − ĝ(X), and regress R on D to estimate θ in "
                "Y = θ·D + g(X) + ε. Explain why the resulting θ̂ is biased even "
                "with a learner that predicts Y well. Identify the source precisely.",
             "solution_title": "Regularization bias in ĝ does not partial X out of "
                "D, so confounding leaks into θ̂.",
             "solution": [
                "Regressing R = Y − ĝ(X) on D only partials X out of Y, not out of "
                "D. Because D still depends on X through m(X), the part of D that "
                "is driven by X is left in the regressor, and its correlation with "
                "the residual confounding contaminates θ̂.",
                "ĝ is also regularized: a flexible learner shrinks toward "
                "simplicity, so ĝ(X) carries a systematic error b(X) = g(X) − "
                "ĝ(X). That error enters R and, projected onto D, biases θ̂ at a "
                "rate governed by the learner's (slow) nuisance convergence.",
                "The naive plug-in score is not orthogonal: its expectation moves "
                "at FIRST order in the nuisance error, so even small ĝ errors are "
                "not forgiven.",
                "Fix: also residualize D (FWL / orthogonal score) and cross-fit. "
                "Then only the as-good-as-random part of D is used, and nuisance "
                "errors hit θ̂ at second order."]},
            {"title": "The Frisch–Waugh–Lovell intuition",
             "prompt": "State the FWL theorem for OLS and explain how it justifies "
                "the residual-on-residual estimator. Then say what changes when we "
                "replace the linear projections E[Y|X], E[D|X] with machine "
                "learning, and what stays the same.",
             "solution_title": "FWL: the D-coefficient equals the regression of "
                "Y-residuals on D-residuals; DML swaps OLS partialling for ML "
                "partialling.",
             "solution": [
                "FWL: in OLS of Y on (D, X), the coefficient on D equals the "
                "coefficient from regressing (Y − proj_X Y) on (D − proj_X D), "
                "where proj_X is the linear projection onto X. Partialling X out "
                "of both sides isolates the D-specific variation.",
                "This makes the recipe transparent: strip X's influence from Y and "
                "from D, then the leftover slope is θ. With X partialled out of D, "
                "the remaining variation in D is unconfounded.",
                "DML replaces the LINEAR projection by a flexible ĝ(X) ≈ E[Y|X] and "
                "m̂(X) ≈ E[D|X]. The residual-on-residual step is identical; only "
                "the way we estimate the conditional expectations changes.",
                "What stays the same is the orthogonal structure; what changes is "
                "that we must cross-fit, because ML projections (unlike the linear "
                "hat matrix) overfit the rows they are trained on."]},
            {"title": "What Neyman orthogonality buys you",
             "prompt": "Define Neyman orthogonality for a score ψ(W; θ, η). A "
                "colleague says 'orthogonality means the nuisance estimates don't "
                "matter.' Correct them precisely: what does orthogonality require "
                "of the nuisances, and what does it free you from?",
             "solution_title": "First-order insensitivity to nuisance error — "
                "nuisances still matter, but only at second order.",
             "solution": [
                "Orthogonality: the Gateaux derivative of E[ψ(W; θ₀, η)] with "
                "respect to η, evaluated at the truth, is zero. Small perturbations "
                "of the nuisance change the moment condition only at second order.",
                "So the colleague is wrong that nuisances 'don't matter': you still "
                "need consistent ĝ and m̂. What you are freed from is FAST "
                "convergence — a slow rate (≈ n^(−1/4)) suffices, because the "
                "first-order nuisance error has been zeroed out.",
                "That n^(−1/4) requirement is exactly what flexible learners "
                "(forests, boosting, LASSO under sparsity) can deliver, which is "
                "why DML can use them as black boxes.",
                "Consequence: θ̂ is √n-consistent and asymptotically normal, so the "
                "usual confidence interval is valid — despite the machine learning "
                "in the nuisance step."]},
            {"title": "Why cross-fitting removes overfitting bias",
             "prompt": "Sample splitting feels wasteful — you train on part of the "
                "data and predict the rest. Explain why cross-fitting is "
                "nonetheless essential, what specific bias it removes, and why "
                "averaging over folds means you do not actually lose efficiency.",
             "solution_title": "It breaks the entanglement between a row's residual "
                "and the model that saw it; averaging folds restores full sample "
                "use.",
             "solution": [
                "A nuisance model trained on a row predicts that row too well "
                "(overfitting). Its in-sample residual is artificially small and "
                "correlated with the row's own noise, so own-observation error "
                "contaminates the score — a bias that does not vanish at the "
                "needed rate.",
                "Cross-fitting predicts each row only with models trained on OTHER "
                "folds, so no row informs the model that residualizes it. The "
                "residual and the fitting noise become independent, killing the "
                "own-observation term.",
                "Efficiency is preserved because every row is eventually in a "
                "held-out fold and contributes to the final estimate; you average "
                "the K orthogonal score equations rather than discarding data.",
                "Diagnostic: if you skip cross-fitting, the in-sample residual "
                "variance collapses far below the cross-fitted value — a red flag "
                "that the standard error is too small and the inference invalid."]},
            {"title": "What DML does NOT fix",
             "prompt": "Your collaborator is thrilled: 'DML uses powerful ML, so it "
                "handles confounding for us.' A key confounder was never measured. "
                "Will DML — with cross-fitting and an orthogonal score — recover "
                "the true effect? Explain, and state the general principle.",
             "solution_title": "No. DML is an estimation tool, not an "
                "identification tool; unmeasured confounding still biases θ̂.",
             "solution": [
                "If a confounder U is unmeasured it is not in X. The orthogonal "
                "score is built from E[Y|X] and E[D|X], which condition only on the "
                "measured X — they cannot partial out U.",
                "So the residualized D still carries the U-driven, confounded "
                "variation, and θ̂ is biased no matter how flexible or well "
                "cross-fitted the learner is. More data or fancier ML cannot help.",
                "General principle: DML buys you valid, efficient ESTIMATION once "
                "the effect is IDENTIFIED. It does nothing for identification, "
                "which still requires the no-unmeasured-confounding assumption (or "
                "a design / instrument).",
                "Same warning for positivity and a wrong causal graph: garbage X "
                "in, biased θ out. Run a sensitivity analysis; do not let the ML "
                "lull you into thinking confounding was handled."]},
        ],
    },
    "lab": {
        "label": "Lab 9",
        "title": "Double ML",
        "goal": "build the partially-linear DML estimator from scratch — "
            "cross-fit flexible models for E[Y|X] and E[D|X], residualize, and "
            "regress — recover a known effect with a valid SE, and prove the naive "
            "plug-in is biased. Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Simulate high-dimensional confounding",
             "body": "Generate Y = θ·D + g(X) + ε and D = m(X) + v with nonlinear "
                "g, m, many covariates, and a KNOWN θ. This is the partially linear "
                "model; X confounds both the treatment and the outcome.",
             "code_python": "import numpy as np\n"
                "rng = np.random.default_rng(7)\n"
                "n, p, THETA = 3000, 20, 0.8\n"
                "X = rng.uniform(-1.5, 1.5, size=(n, p))\n"
                "common = (1.5*np.maximum(X[:,0], 0) + X[:,1]**2\n"
                "          + 0.8*np.sin(2*X[:,2]))   # nonlinear nuisance\n"
                "D = common + rng.normal(size=n)              # m(X) = common\n"
                "Y = THETA*D + common + rng.normal(size=n)    # g(X) = common",
             "code_r": 'set.seed(7)\n'
                'n <- 3000; p <- 20; theta <- 0.8\n'
                'X <- matrix(runif(n*p, -1.5, 1.5), n, p)\n'
                'common <- 1.5*pmax(X[,1],0) + X[,2]^2 + 0.8*sin(2*X[,3])\n'
                'D <- common + rnorm(n)\n'
                'Y <- theta*D + common + rnorm(n)\n'
                'df <- data.frame(Y, D, X)'},
            {"heading": "Step 2 · Show the naive single-model adjustment is biased",
             "body": "Fit one flexible learner that sees D and X together and read "
                "off the implied effect of D (or regress Y on D and linear X). "
                "Because the nuisance is nonlinear and the score is not orthogonal, "
                "the estimate is biased away from θ = 0.8.",
             "code_python": "from sklearn.ensemble import RandomForestRegressor\n"
                "rf = RandomForestRegressor(n_estimators=100, max_depth=10,\n"
                "                           random_state=7).fit(np.c_[D, X], Y)\n"
                "naive = (rf.predict(np.c_[D+1, X]) - rf.predict(np.c_[D, X])).mean()\n"
                "print('naive single-forest effect:', round(naive, 3),\n"
                "      ' (truth', THETA, ')')",
             "code_r": '## naive: regress Y on D and X linearly (cannot capture g)\n'
                'naive <- coef(lm(Y ~ D + ., data = df))["D"]\n'
                'cat("naive OLS effect:", round(naive, 3), " truth", theta, "\\n")'},
            {"heading": "Step 3 · Cross-fit the nuisance models",
             "body": "Split into K folds. For each fold, train E[Y|X] and E[D|X] on "
                "the OTHER folds and predict the held-out fold. Stack the "
                "out-of-fold residuals Ỹ = Y − Ê[Y|X] and D̃ = D − Ê[D|X].",
             "code_python": "from sklearn.model_selection import KFold\n"
                "rY = np.zeros(n); rD = np.zeros(n)\n"
                "for tr, te in KFold(5, shuffle=True, random_state=7).split(X):\n"
                "    mY = RandomForestRegressor(n_estimators=100,\n"
                "                               random_state=7).fit(X[tr], Y[tr])\n"
                "    mD = RandomForestRegressor(n_estimators=100,\n"
                "                               random_state=7).fit(X[tr], D[tr])\n"
                "    rY[te] = Y[te] - mY.predict(X[te])\n"
                "    rD[te] = D[te] - mD.predict(X[te])",
             "code_r": '## DoubleML does the cross-fitting for you\n'
                'library(DoubleML); library(mlr3); library(mlr3learners)\n'
                'dml_data <- DoubleMLData$new(df, y_col = "Y", d_cols = "D")\n'
                'lrn <- lrn("regr.ranger", num.trees = 100)\n'
                'plr <- DoubleMLPLR$new(dml_data, ml_l = lrn, ml_m = lrn,\n'
                '                       n_folds = 5)\n'
                'plr$fit()'},
            {"heading": "Step 4 · Regress residual on residual; report θ̂ and SE",
             "body": "The orthogonal estimate is the slope of Ỹ on D̃. Use a "
                "heteroskedasticity-robust SE. The interval should cover the true "
                "θ = 0.8, while the naive estimate from Step 2 did not.",
             "code_python": "import statsmodels.api as sm\n"
                "fit = sm.OLS(rY, rD).fit(cov_type='HC1')\n"
                "theta_hat, se = fit.params[0], fit.bse[0]\n"
                "print(f'DML theta = {theta_hat:.3f}  SE = {se:.3f}')\n"
                "print(f'95% CI = [{theta_hat-1.96*se:.3f}, '\n"
                "      f'{theta_hat+1.96*se:.3f}]   truth = {THETA}')",
             "code_r": 'plr$summary()        # estimate, SE, t, p, CI\n'
                'plr$confint()        # 95% confidence interval for theta'},
            {"heading": "Step 5 · Variations: instruments and a Lasso learner",
             "body": "Swap the learner (a LASSO is a one-line change) to see the "
                "recipe is learner-agnostic. For an endogenous D with an instrument "
                "Z, residualize Y, D, AND Z on X, then do residual 2SLS — the "
                "partially-linear IV (PLIV) estimator.",
             "code_python": "from sklearn.linear_model import LassoCV\n"
                "# residual-IV (PLIV): theta = cov(Z_res, Y_res)/cov(Z_res, D_res)\n"
                "# rZ built by cross-fitting E[Z|X] exactly like rY, rD above\n"
                "# theta_iv = (rZ @ rY) / (rZ @ rD)\n"
                "# Lasso nuisances: just replace RandomForestRegressor with\n"
                "#   LassoCV(cv=3, random_state=7, max_iter=5000)",
             "code_r": '## partially linear IV with an instrument z\n'
                'dml_iv <- DoubleMLData$new(df_iv, y_col = "Y",\n'
                '            d_cols = "D", z_cols = "Z")\n'
                'pliv <- DoubleMLPLIV$new(dml_iv, ml_l = lrn, ml_m = lrn,\n'
                '                         ml_r = lrn)$fit()\n'
                'pliv$summary()'},
        ],
        "expected": "The naive single-model adjustment lands well above 0.8 "
            "(regularization bias). The cross-fitted DML estimate sits at ≈ 0.80–"
            "0.81 with a tight, valid SE, and its 95% interval covers the truth. "
            "If you rerun Steps 3–4 WITHOUT cross-fitting, the in-sample residuals "
            "shrink dramatically (the forest memorized the rows) and the SE is no "
            "longer trustworthy. Hide one strong confounder column from X and the "
            "estimate jumps back to a biased value — DML cannot rescue unmeasured "
            "confounding.",
        "submit": [
            "Push your notebook plus a short README reporting the naive estimate, "
            "the cross-fitted DML θ̂ with its SE and 95% CI, and the known θ.",
            "Include the cross-fit vs no-cross-fit residual-variance comparison and "
            "one sentence on why the in-sample version is untrustworthy.",
            "Show the unmeasured-confounding case (drop a confounder column) and "
            "note the resulting bias.",
        ],
    },
    "self_check": [
        "Explain, without notes, why a naive plug-in of an ML prediction biases "
        "θ̂, naming regularization bias and overfitting.",
        "State the residual-on-residual recipe and tie it to Frisch–Waugh–Lovell.",
        "Define Neyman orthogonality in one sentence and say what convergence rate "
        "it lets the nuisances get away with.",
        "Say precisely why cross-fitting removes own-observation overfitting bias "
        "without costing efficiency.",
        "Name three things DML does NOT fix (unmeasured confounding, positivity, a "
        "wrong graph).",
    ],
    "next_week": {
        "heading": "Coming up: Week 13 — Heterogeneous effects & policy learning",
        "teaser": "DML gave us one honest number, the average effect. Next week we "
            "ask 'for whom?' — estimating conditional average treatment effects "
            "(CATEs) with meta-learners and causal forests, then turning those "
            "estimates into a policy that decides who to treat. The orthogonal, "
            "cross-fitted machinery you built this week is exactly what powers the "
            "modern CATE estimators. Skim the EconML CATE user guide to get a head "
            "start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 12", "items": [
            {"t": "The partially linear model", "d": "Linear in the effect we want, "
             "flexible in the nuisances we don't."},
            {"t": "Why naive plug-in ML is biased", "d": "Regularization bias and "
             "overfitting leak into θ̂."},
            {"t": "Frisch–Waugh–Lovell", "d": "Residualize Y and D on X, then "
             "regress the residuals."},
            {"t": "Neyman orthogonality", "d": "A score that ignores small nuisance "
             "errors to first order."},
            {"t": "Cross-fitting", "d": "Predict each row with models that never "
             "saw it."},
            {"t": "Variants & limits", "d": "ATE, instruments — and what DML can't "
             "fix."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "Block IV: flexible ML meets causal estimation", "bullets": [
            "Blocks II–III gave us adjustment, weighting, IV, RD, DiD — mostly with "
            "parametric nuisance models.",
            "Modern problems have hundreds of confounders and nonlinear structure: "
            "OLS for the nuisance is not enough.",
            "We want to use flexible ML for the nuisances — without biasing the "
            "effect we report.",
            ("DML is the bridge: ML for prediction, an orthogonal cross-fitted "
             "score for estimation.", 1),
            "AIPW (Week 7) was a first taste; this week makes it systematic.",
         ],
         "note": {"title": "The throughline",
            "body": "Separate the part you care about (θ) from the parts you don't "
            "(g, m), and protect θ from the learner's biases."}},
        {"type": "statement",
         "quote": "Use machine learning for the nuisances you don't care about — "
            "and protect the one number you do.",
         "attribution": "Double/debiased ML lets a black-box learner handle "
            "high-dimensional confounding while an orthogonal, cross-fitted score "
            "keeps the treatment effect unbiased and the confidence interval valid."},

        {"type": "section", "kicker": "Part 1",
         "title": "The partially linear model",
         "subtitle": "Linear in the parameter we want; arbitrary in the nuisance "
            "functions we are happy to hand to a learner."},
        {"type": "content", "kicker": "The model",
         "title": "Y = θ·D + g(X) + ε,  D = m(X) + v", "bullets": [
            "θ is the causal effect of treatment D on outcome Y — the one number "
            "we report.",
            "g(X) and m(X) are unknown, nonlinear, possibly high-dimensional "
            "nuisances.",
            "X confounds: it drives both the treatment (through m) and the outcome "
            "(through g).",
            "'Partially linear' = linear in θ, flexible everywhere else.",
            ("Goal: estimate θ while letting ML do g and m.", 1),
         ],
         "note": {"title": "Why this shape",
            "body": "It isolates a single interpretable parameter θ, so we can "
            "focus all our care on protecting it."}},
        {"type": "compare", "kicker": "Two regimes",
         "title": "Classical adjustment vs. the modern problem", "columns": [
            {"head": "Classical", "sub": "low-dim, linear", "points": [
                "Fit g(X) with OLS.",
                "Few, hand-picked confounders.",
                "Coefficient on D is the effect."]},
            {"head": "Modern", "sub": "high-dim, nonlinear", "points": [
                "Hundreds of confounders; genomics-scale X.",
                "g, m are nonlinear and unknown.",
                "Need flexible ML — but carefully."]},
            {"head": "The risk", "sub": "if you are naive", "points": [
                "ML is regularized and overfits.",
                "That bias leaks straight into θ̂.",
                "Low test error ≠ unbiased effect."]},
         ]},
        {"type": "content", "kicker": "Two motivating cases",
         "title": "Where high-dimensional confounding bites", "bullets": [
            "Pricing: demand depends on price plus a flood of market, seasonal, and "
            "customer covariates — all confounding.",
            "Genomics: a treatment's effect on a phenotype, confounded by thousands "
            "of measured genetic covariates.",
            "In both, the confounder set is too large and too nonlinear for OLS "
            "adjustment.",
            "Flexible ML can model the nuisances — DML makes the resulting effect "
            "trustworthy.",
         ],
         "note": {"title": "Common thread",
            "body": "Lots of X, nonlinear structure, one effect to defend. The DML "
            "use case exactly."}},

        {"type": "section", "kicker": "Part 2",
         "title": "Why naive plug-in ML is biased",
         "subtitle": "Two culprits — regularization bias and overfitting — turn a "
            "great predictor into a bad estimator."},
        {"type": "content", "kicker": "Culprit 1",
         "title": "Regularization bias", "bullets": [
            "Every flexible learner shrinks toward simplicity to control variance.",
            "That shrinkage leaves a systematic error in ĝ(X): bias, not just "
            "noise.",
            "The naive plug-in score is not orthogonal, so this bias hits θ̂ at "
            "FIRST order.",
            "It does not vanish fast enough to ignore — θ̂ is biased even in large "
            "samples.",
         ],
         "note": {"title": "Key point",
            "body": "A learner tuned for low prediction error is not tuned for an "
            "unbiased coefficient."}},
        {"type": "content", "kicker": "Culprit 2",
         "title": "Overfitting & leakage", "bullets": [
            "A model that has seen a row predicts that row too well.",
            "Its in-sample residual is artificially small and tangled with the "
            "row's own noise.",
            "That own-observation error sneaks into the score and biases θ̂.",
            ("The cure is to never predict a row with a model trained on it — "
             "cross-fitting.", 1),
         ],
         "note": {"title": "Diagnostic",
            "body": "In-sample residual variance far below the out-of-fold value is "
            "the overfitting fingerprint."}},
        {"type": "statement",
         "quote": "Prediction is not estimation.",
         "attribution": "Low test MSE does not buy you a trustworthy θ̂. DML keeps "
            "the ML for predicting the nuisances but estimates the effect through "
            "an orthogonal, cross-fitted score."},

        {"type": "section", "kicker": "Part 3",
         "title": "Frisch–Waugh–Lovell",
         "subtitle": "The residual-on-residual idea at the core of DML — older than "
            "machine learning by eighty years."},
        {"type": "content", "kicker": "The classic theorem",
         "title": "Partial X out of both sides", "bullets": [
            "FWL: the OLS coefficient on D in Y ~ D + X equals the slope from "
            "regressing Y-residuals on D-residuals.",
            "Residualize Y: Ỹ = Y − Ê[Y|X]. Residualize D: D̃ = D − Ê[D|X].",
            "Then θ̂ = (D̃ᵀỸ) / (D̃ᵀD̃) — a one-variable regression.",
            "With X partialled out of D, the leftover D̃ is as-good-as-random.",
         ],
         "note": {"title": "Why it works",
            "body": "Confounding lives in the X-driven part of D. Remove it, and "
            "what's left identifies the effect."}},
        {"type": "steps", "kicker": "DML = FWL with a learner",
         "title": "The partially-linear recipe", "steps": [
            {"title": "Model E[Y|X]", "body": "— any flexible learner for the "
             "outcome's nuisance."},
            {"title": "Model E[D|X]", "body": "— any flexible learner for the "
             "treatment's nuisance."},
            {"title": "Residualize", "body": "— Ỹ = Y − Ê[Y|X], D̃ = D − Ê[D|X]."},
            {"title": "Regress", "body": "— slope of Ỹ on D̃ gives θ̂."},
            {"title": "SE", "body": "— robust SE from the residual regression."},
         ],
         "note": "Identical to FWL; only the conditional-expectation estimator "
            "changes from OLS to ML."},
        {"type": "compare", "kicker": "Linear vs. ML partialling",
         "title": "What changes, what stays", "columns": [
            {"head": "Stays the same", "points": [
                "Residual-on-residual structure.",
                "Orthogonality of the score.",
                "θ̂ as a one-variable slope."]},
            {"head": "Changes", "points": [
                "OLS projection → flexible ML.",
                "Captures nonlinear g, m.",
                "Now MUST cross-fit (ML overfits)."]},
        ]},

        {"type": "section", "kicker": "Part 4",
         "title": "Neyman orthogonality",
         "subtitle": "The score property that makes the estimate first-order "
            "insensitive to nuisance error — the heart of 'debiased.'"},
        {"type": "content", "kicker": "Definition",
         "title": "First-order insensitivity to the nuisance", "bullets": [
            "A score ψ(W; θ, η) involves the target θ and nuisance η = (g, m).",
            "Orthogonal if the derivative of E[ψ] in the η-direction is zero at the "
            "truth.",
            "So small nuisance errors move θ̂ only at SECOND order.",
            "The naive plug-in score lacks this; the residualized score has it.",
         ],
         "note": {"title": "The orthogonal score",
            "body": "ψ = (Y − ĝ − θ(D − m̂))(D − m̂). Built so first-order nuisance "
            "error cancels."}},
        {"type": "content", "kicker": "The payoff",
         "title": "Slow nuisances are good enough", "bullets": [
            "Orthogonality means nuisances need only converge at a slow rate "
            "(≈ n^(−1/4)).",
            "Forests, boosting, and LASSO comfortably hit that rate.",
            "Then θ̂ is √n-consistent and asymptotically normal.",
            ("So the usual confidence interval is valid — despite the ML.", 1),
         ],
         "note": {"title": "Two for the price of one",
            "body": "Flexibility for the nuisances AND honest inference for the "
            "effect."}},
        {"type": "content", "kicker": "You've met this before",
         "title": "AIPW was your first orthogonal score", "bullets": [
            "Week 7's doubly robust estimator IS the orthogonal score for the ATE.",
            "Double robustness and Neyman orthogonality are the same property in "
            "disguise.",
            "DML generalizes it: any nuisance learner, plus systematic "
            "cross-fitting.",
            "The interactive-model DML for the ATE is cross-fitted AIPW.",
         ],
         "note": {"title": "Continuity",
            "body": "Week 7 → Week 12 is one idea growing up: orthogonal scores for "
            "flexible nuisances."}},

        {"type": "section", "kicker": "Part 5",
         "title": "Cross-fitting",
         "subtitle": "Orthogonality tames regularization bias; cross-fitting tames "
            "overfitting. You need both."},
        {"type": "steps", "kicker": "The procedure",
         "title": "Out-of-fold residuals in K steps", "steps": [
            {"title": "Split", "body": "— partition the data into K folds "
             "(K = 2–5)."},
            {"title": "Train away", "body": "— fit nuisances on the K−1 OTHER "
             "folds."},
            {"title": "Predict in", "body": "— residualize the held-out fold."},
            {"title": "Pool", "body": "— stack all out-of-fold residuals."},
            {"title": "Estimate", "body": "— regress pooled Ỹ on D̃; average over "
             "splits."},
         ],
         "note": "No row is ever predicted by a model that has seen it — that is "
            "the whole point."},
        {"type": "content", "kicker": "Why it works",
         "title": "Break the entanglement", "bullets": [
            "Predicting a row with a model trained on it correlates its residual "
            "with its own noise.",
            "Cross-fitting uses only other folds, so residual and fitting-noise are "
            "independent.",
            "The own-observation bias term disappears.",
            "Averaging the folds uses every row, so no efficiency is lost.",
         ],
         "note": {"title": "Free protection",
            "body": "You give up nothing in efficiency and gain a valid standard "
            "error."}},
        {"type": "table", "kicker": "Cross-fit vs. in-sample, on simulated data",
         "title": "In-sample residuals collapse — the overfitting fingerprint",
         "headers": ["Quantity", "Cross-fit", "In-sample (no CF)"],
         "rows": [
            ["Var of D-residual", "≈ 1.1", "≈ 0.15  (collapsed)"],
            ["Var of Y-residual", "≈ 1.9", "≈ 0.27  (collapsed)"],
            ["Standard error", "valid", "too small — invalid"],
            ["θ̂ guarantee", "√n-normal", "none"],
         ],
         "note": {"title": "You'll see this in the notebook",
            "body": "Skip cross-fitting and the residual variances crater — a clear "
            "signal the inference is broken."}},

        {"type": "section", "kicker": "Part 6",
         "title": "Variants & a case study",
         "subtitle": "DML for the ATE, DML with instruments, and high-dimensional "
            "confounding in practice."},
        {"type": "compare", "kicker": "Three model flavors",
         "title": "One framework, several scores", "columns": [
            {"head": "Partially linear", "sub": "PLR", "points": [
                "Constant effect θ.",
                "Residual-on-residual.",
                "The recipe you build in lab."]},
            {"head": "Interactive / ATE", "points": [
                "Effect may vary by arm.",
                "Cross-fitted AIPW score.",
                "Targets E[Y(1)] − E[Y(0)]."]},
            {"head": "Partially linear IV", "sub": "PLIV", "points": [
                "Endogenous D, instrument Z.",
                "Residualize Y, D, AND Z on X.",
                "Then residual 2SLS."]},
        ]},
        {"type": "steps", "kicker": "Case · a pricing problem",
         "title": "High-dimensional confounding in demand estimation", "steps": [
            {"title": "The question", "body": "— effect of price (D) on quantity "
             "sold (Y)."},
            {"title": "The confounders", "body": "— seasonality, market, customer "
             "and product features: hundreds of X."},
            {"title": "Nuisances by ML", "body": "— flexible models for E[Y|X] and "
             "E[price|X]."},
            {"title": "Orthogonal θ̂", "body": "— cross-fitted residual regression "
             "gives a credible price elasticity."},
         ],
         "note": "Same story for a genomics-scale covariate set: thousands of "
            "measured confounders, one effect."},
        {"type": "content", "kicker": "Combining with instruments",
         "title": "DML meets IV (PLIV)", "bullets": [
            "When D is endogenous, an instrument Z restores identification.",
            "Residualize Y, D, AND Z on X with cross-fitted ML.",
            "Then 2SLS on the residuals: θ̂ = cov(Z̃, Ỹ) / cov(Z̃, D̃).",
            "Same orthogonality and cross-fitting; one more nuisance to learn.",
         ],
         "note": {"title": "Reuse",
            "body": "Mendelian randomization (Week 8) plus high-dimensional "
            "controls is a natural PLIV application."}},

        {"type": "section", "kicker": "Part 7",
         "title": "Pitfalls & limits",
         "subtitle": "DML is powerful estimation — but it is not magic, and it "
            "does not identify effects for you."},
        {"type": "content", "kicker": "Two traps to avoid",
         "title": "Regularization bias and leakage, revisited", "bullets": [
            "Skip orthogonalization → regularization bias from the nuisance learner "
            "contaminates θ̂.",
            "Skip cross-fitting → overfitting leakage shrinks residuals and breaks "
            "the SE.",
            "Tune nuisances for prediction, but never read θ off the nuisance "
            "model.",
            "Always sanity-check: do the cross-fit residual variances look right?",
         ],
         "note": {"title": "Rule of thumb",
            "body": "Orthogonality and cross-fitting are a pair. Neither alone "
            "gives valid inference."}},
        {"type": "compare", "kicker": "Be precise about scope",
         "title": "What DML does and does NOT fix", "columns": [
            {"head": "DML fixes", "points": [
                "Regularization bias (orthogonal score).",
                "Overfitting leakage (cross-fitting).",
                "High-dimensional, nonlinear nuisances."]},
            {"head": "DML does NOT fix", "points": [
                "Unmeasured confounding.",
                "Positivity violations.",
                "A wrong causal graph."]},
        ]},
        {"type": "statement",
         "quote": "DML is an estimation tool, not an identification tool.",
         "attribution": "If a confounder is unmeasured, it is not in X — the "
            "orthogonal score is built around the wrong nuisances, and no learner, "
            "however flexible, can rescue θ̂. Identification still requires your "
            "assumptions."},
        {"type": "steps", "kicker": "The DML workflow",
         "title": "From question to a defensible estimate", "steps": [
            {"title": "Identify", "body": "— argue no-unmeasured-confounding (or "
             "find an instrument)."},
            {"title": "Choose learners", "body": "— flexible models for E[Y|X], "
             "E[D|X]."},
            {"title": "Cross-fit", "body": "— out-of-fold residuals, K folds."},
            {"title": "Orthogonal estimate", "body": "— residual regression; robust "
             "SE & CI."},
            {"title": "Stress-test", "body": "— vary learners and folds; "
             "sensitivity to unmeasured X."},
         ],
         "note": "If the estimate swings wildly across learners or folds, distrust "
            "it — and check identification first."},
        {"type": "statement",
         "quote": "ML for the nuisances, orthogonality plus cross-fitting for the "
            "effect.",
         "attribution": "This week: build the partially-linear DML estimator by "
            "hand, watch it beat the naive plug-in on data with a known θ, and see "
            "for yourself that unmeasured confounding is beyond its reach. See you "
            "in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A partially linear model with a known effect\n\n"
            "We simulate the workhorse of this week:\n\n"
            "$$Y = \\theta\\,D + g(X) + \\varepsilon, \\qquad D = m(X) + v$$\n\n"
            "with **nonlinear** nuisance functions `g, m`, a **high-dimensional** "
            "covariate matrix `X` (20 columns), and a **known** true effect "
            "`θ = 0.8`. The covariates `X` confound: they drive both the treatment "
            "`D` (through `m`) and the outcome `Y` (through `g`). Because the same "
            "nonlinear `common(X)` enters both, a naive analysis will be badly "
            "biased — and that is the point.\n\n"
            "We reuse the provided `RNG` (seeded once at setup); we never reseed."},
        {"code": "from sklearn.ensemble import RandomForestRegressor\n"
            "import statsmodels.api as sm\n\n"
            "TRUE_THETA = 0.8\n"
            "n, p = 3000, 20\n\n"
            "def simulate(n, p):\n"
            "    X = RNG.uniform(-1.5, 1.5, size=(n, p))\n"
            "    # one nonlinear function drives BOTH treatment and outcome\n"
            "    common = (1.5*np.maximum(X[:, 0], 0)   # kink in X0\n"
            "              + X[:, 1]**2                 # curvature in X1\n"
            "              + 0.8*np.sin(2*X[:, 2]))     # wiggle in X2\n"
            "    g = common                              # outcome nuisance g(X)\n"
            "    m = common                              # treatment nuisance m(X)\n"
            "    D = m + RNG.normal(size=n)              # D = m(X) + v\n"
            "    Y = TRUE_THETA*D + g + RNG.normal(size=n)  # Y = theta*D + g(X) + e\n"
            "    return X, D, Y\n\n"
            "X, D, Y = simulate(n, p)\n"
            "print(f'n = {n}, p = {p} covariates,  TRUE theta = {TRUE_THETA}')\n"
            "print(f'D ranges [{D.min():.2f}, {D.max():.2f}],  '\n"
            "      f'corr(D, common-driver) is large by construction')"},
        {"md": "## 2 · The naive estimates are biased\n\n"
            "Two tempting naive analyses, both wrong:\n\n"
            "1. **OLS of Y on D and (linear) X** — linear terms cannot absorb the "
            "nonlinear `g(X)`, so leftover confounding inflates the coefficient on "
            "`D`.\n"
            "2. **A single flexible forest** of `Y` on `(D, X)`, reading off the "
            "implied effect of a one-unit bump in `D` — regularization bias pulls "
            "it away from the truth.\n\n"
            "Both should miss `θ = 0.8`."},
        {"code": "# Naive 1: OLS of Y on D and X (linear) -- arrays, so .params[1] is D\n"
            "naive_ols = sm.OLS(Y, sm.add_constant(np.c_[D, X])).fit().params[1]\n\n"
            "# Naive 2: one forest on (D, X); effect = avg predicted bump from D->D+1\n"
            "rf_all = RandomForestRegressor(n_estimators=100, max_depth=10,\n"
            "                               random_state=7).fit(np.c_[D, X], Y)\n"
            "naive_ml = float((rf_all.predict(np.c_[D + 1.0, X])\n"
            "                  - rf_all.predict(np.c_[D, X])).mean())\n\n"
            "print(f'naive OLS (D + linear X) = {naive_ols:.3f}')\n"
            "print(f'naive single-forest      = {naive_ml:.3f}')\n"
            "print(f'TRUE theta               = {TRUE_THETA:.3f}')\n"
            "assert abs(naive_ols - TRUE_THETA) > 0.2, 'naive OLS should be biased'\n"
            "assert abs(naive_ml - TRUE_THETA) > 0.1, 'naive plug-in should be biased'"},
        {"md": "The naive estimates land well above 0.8. The flexible forest "
            "predicts `Y` well, yet its implied effect is still biased — "
            "**prediction is not estimation.** We need to change *how* we read the "
            "effect off, not just *how flexible* the learner is."},
        {"md": "## 3 · Frisch–Waugh–Lovell, warmed up with OLS\n\n"
            "Before the ML version, confirm the **residual-on-residual** identity "
            "on a purely linear toy. FWL says the coefficient on `D` in "
            "`Y ~ D + X` equals the slope of (Y residualized on X) on (D "
            "residualized on X). We'll verify the two give the *same* number."},
        {"code": "# Linear toy: Y = 0.8*D + X@beta + noise, D = X@gamma + noise\n"
            "Xl = RNG.normal(size=(4000, 6))\n"
            "beta  = RNG.normal(size=6)\n"
            "gamma = RNG.normal(size=6)\n"
            "Dl = Xl @ gamma + RNG.normal(size=4000)\n"
            "Yl = 0.8*Dl + Xl @ beta + RNG.normal(size=4000)\n\n"
            "# (a) full OLS coefficient on D\n"
            "full = sm.OLS(Yl, sm.add_constant(np.c_[Dl, Xl])).fit().params[1]\n\n"
            "# (b) FWL: residualize Y and D on X (with intercept), regress residuals\n"
            "Xc = sm.add_constant(Xl)\n"
            "rY = Yl - sm.OLS(Yl, Xc).fit().predict(Xc)\n"
            "rD = Dl - sm.OLS(Dl, Xc).fit().predict(Xc)\n"
            "fwl = sm.OLS(rY, rD).fit().params[0]\n\n"
            "print(f'full OLS coef on D       = {full:.4f}')\n"
            "print(f'residual-on-residual (FWL) = {fwl:.4f}')\n"
            "assert abs(full - fwl) < 1e-8, 'FWL identity should hold exactly'\n"
            "print('FWL identity confirmed: partialling X out of both sides is enough.')"},
        {"md": "DML is exactly this, with the **linear** projections `E[Y|X]`, "
            "`E[D|X]` replaced by **flexible ML**. One catch the linear case hides: "
            "ML models *overfit* the rows they are trained on, so we must "
            "**cross-fit** (Section 5)."},
        {"md": "## 4 · Partially-linear DML, by hand\n\n"
            "Now the real thing on the nonlinear, high-dimensional data:\n\n"
            "1. **Cross-fit** flexible models for `E[Y|X]` and `E[D|X]` with K-fold "
            "splitting (predict each row using models trained on the *other* "
            "folds).\n"
            "2. Form out-of-fold residuals `Ỹ = Y − Ê[Y|X]`, `D̃ = D − Ê[D|X]`.\n"
            "3. **Regress `Ỹ` on `D̃`** to get `θ̂`, with a robust standard error.\n\n"
            "The estimate should recover `θ = 0.8` with a valid CI."},
        {"code": "from sklearn.model_selection import KFold\n\n"
            "def dml_plm(X, D, Y, n_splits=5, crossfit=True,\n"
            "            n_estimators=100, max_depth=None):\n"
            "    \"\"\"Partially-linear DML. Returns theta_hat, SE, and residuals.\"\"\"\n"
            "    nn = len(Y)\n"
            "    rY = np.zeros(nn)\n"
            "    rD = np.zeros(nn)\n"
            "    if crossfit:\n"
            "        for tr, te in KFold(n_splits, shuffle=True,\n"
            "                            random_state=7).split(X):\n"
            "            mY = RandomForestRegressor(n_estimators=n_estimators,\n"
            "                     max_depth=max_depth, random_state=7).fit(X[tr], Y[tr])\n"
            "            mD = RandomForestRegressor(n_estimators=n_estimators,\n"
            "                     max_depth=max_depth, random_state=7).fit(X[tr], D[tr])\n"
            "            rY[te] = Y[te] - mY.predict(X[te])\n"
            "            rD[te] = D[te] - mD.predict(X[te])\n"
            "    else:  # in-sample: fit and predict on the SAME rows (overfits!)\n"
            "        mY = RandomForestRegressor(n_estimators=n_estimators,\n"
            "                 max_depth=max_depth, random_state=7).fit(X, Y)\n"
            "        mD = RandomForestRegressor(n_estimators=n_estimators,\n"
            "                 max_depth=max_depth, random_state=7).fit(X, D)\n"
            "        rY = Y - mY.predict(X)\n"
            "        rD = D - mD.predict(X)\n"
            "    # orthogonal estimate: slope of residual on residual (robust SE)\n"
            "    fit = sm.OLS(rY, rD).fit(cov_type='HC1')\n"
            "    return fit.params[0], fit.bse[0], rY, rD\n\n"
            "theta_hat, se, rY, rD = dml_plm(X, D, Y, crossfit=True)\n"
            "lo, hi = theta_hat - 1.96*se, theta_hat + 1.96*se\n"
            "print(f'DML (cross-fitted) theta_hat = {theta_hat:.3f}  SE = {se:.3f}')\n"
            "print(f'95% CI = [{lo:.3f}, {hi:.3f}]    TRUE theta = {TRUE_THETA}')\n"
            "assert abs(theta_hat - TRUE_THETA) < 0.1, 'DML should recover ~0.8'\n"
            "assert lo < TRUE_THETA < hi, 'CI should cover the truth'"},
        {"md": "DML recovered the truth and its interval covers `0.8`, while every "
            "naive estimate in Section 2 was biased. The orthogonal "
            "residual-on-residual score, fed cross-fitted ML nuisances, is what "
            "made the difference."},
        {"md": "### 🔧 Exercise 4.1 — residualization removes the confounding\n\n"
            "If residualizing worked, the **treatment residual** `D̃` should be "
            "(nearly) uncorrelated with the confounding driver `common(X)`, even "
            "though raw `D` is strongly correlated with it. Compute both "
            "correlations and compare.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (`...` are "
            "placeholders); replace them, then run the solution cell."},
        {"code": "driver = (1.5*np.maximum(X[:, 0], 0) + X[:, 1]**2\n"
            "          + 0.8*np.sin(2*X[:, 2]))   # the confounding common(X)\n\n"
            "corr_raw = np.corrcoef(D, driver)[0, 1]      # large (confounded)\n\n"
            "# TODO: correlation of the residualized treatment D~ with the driver\n"
            "corr_resid = ...   # TODO: np.corrcoef(rD, driver)[0, 1]\n\n"
            "print(f'corr(raw D, driver)      = {corr_raw:+.3f}')\n"
            "# print(f'corr(residual D~, driver) = {corr_resid:+.3f}')"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "corr_resid = np.corrcoef(rD, driver)[0, 1]\n"
            "print(f'corr(raw D, driver)       = {corr_raw:+.3f}')\n"
            "print(f'corr(residual D~, driver) = {corr_resid:+.3f}')\n"
            "assert abs(corr_raw) > 0.5, 'raw D should be confounded by the driver'\n"
            "assert abs(corr_resid) < 0.15, 'residualization should strip the driver'\n"
            "print('\\nResidualizing D on X removed almost all of the confounding '\n"
            "      'variation -> what is left is as-good-as-random.')"},
        {"md": "## 5 · Why cross-fitting matters\n\n"
            "Cross-fitting predicts each row using models trained on the *other* "
            "folds. The naive alternative fits the nuisance on **all** rows and "
            "predicts those same rows — so the forest **memorizes** them and the "
            "in-sample residuals are far too small. We compare the two and watch "
            "the residual variances **collapse** without cross-fitting."},
        {"code": "theta_nc, se_nc, rY_nc, rD_nc = dml_plm(X, D, Y, crossfit=False)\n\n"
            "print(f'{\"\":22s}{\"cross-fit\":>12s}{\"in-sample\":>12s}')\n"
            "print(f'{\"theta_hat\":22s}{theta_hat:12.3f}{theta_nc:12.3f}')\n"
            "print(f'{\"reported SE\":22s}{se:12.3f}{se_nc:12.3f}')\n"
            "print(f'{\"Var(D residual)\":22s}{np.var(rD):12.3f}{np.var(rD_nc):12.3f}')\n"
            "print(f'{\"Var(Y residual)\":22s}{np.var(rY):12.3f}{np.var(rY_nc):12.3f}')\n\n"
            "# The in-sample residual variances collapse -- the overfitting fingerprint.\n"
            "assert np.var(rD_nc) < 0.5*np.var(rD), 'in-sample D resid should collapse'\n"
            "assert np.var(rY_nc) < 0.5*np.var(rY), 'in-sample Y resid should collapse'\n"
            "print('\\nIn-sample residual variances collapsed: the forest memorized the\\n'\n"
            "      'rows, so the in-sample SE is too small and the inference is invalid.')"},
        {"md": "The point estimates look similar here, but the **in-sample residual "
            "variances cratered** (D: ~1.1 → ~0.15; Y: ~1.9 → ~0.27). That is the "
            "overfitting fingerprint: the model fit the noise of the very rows it "
            "then 'predicts,' so the reported standard error is too small and the "
            "asymptotic-normality guarantee is gone. Cross-fitting is what keeps "
            "the inference honest — and it is essentially free."},
        {"md": "### 🔧 Exercise 5.1 — the in-sample fit is suspiciously perfect\n\n"
            "Confirm the overfitting directly: a forest fit on all rows predicts "
            "those same rows with an **in-sample** R² close to 1, even though "
            "`D = common(X) + noise` has irreducible noise that no honest model "
            "could explain. Compute the in-sample R² of the `D`-model.\n\n"
            "Complete the `# TODO`."},
        {"code": "mD_full = RandomForestRegressor(n_estimators=100,\n"
            "                                random_state=7).fit(X, D)\n\n"
            "# TODO: in-sample R^2 of the D-model (fit and scored on the SAME X, D)\n"
            "r2_insample = ...   # TODO: mD_full.score(X, D)\n\n"
            "# print(f'in-sample R^2 of E[D|X] forest = {r2_insample:.3f}')\n"
            "# print('Irreducible noise means an HONEST R^2 should be well below 1.')"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "r2_insample = mD_full.score(X, D)\n"
            "print(f'in-sample R^2 of E[D|X] forest = {r2_insample:.3f}')\n"
            "assert r2_insample > 0.8, 'in-sample R^2 is inflated by overfitting'\n"
            "print('The forest explains far more in-sample variance than is real:\\n'\n"
            "      'that inflation is exactly the leakage cross-fitting removes.')"},
        {"md": "## 6 · DML cannot rescue unmeasured confounding\n\n"
            "DML is an *estimation* tool, not an *identification* tool. If a "
            "confounder is not in `X`, the orthogonal score is built around the "
            "wrong nuisances and `θ̂` is biased — no matter how flexible the learner "
            "or how careful the cross-fitting. We demonstrate by **hiding column "
            "`X0`** (a strong confounder) from the learner."},
        {"code": "X_obs = X[:, 1:]   # drop X0 -- now it is an UNMEASURED confounder\n\n"
            "theta_unm, se_unm, _, _ = dml_plm(X_obs, D, Y, crossfit=True)\n"
            "print(f'DML with X0 measured   = {theta_hat:.3f}  (recovers ~0.8)')\n"
            "print(f'DML with X0 UNMEASURED = {theta_unm:.3f}  (biased)')\n"
            "print(f'TRUE theta             = {TRUE_THETA:.3f}')\n"
            "assert abs(theta_unm - TRUE_THETA) > 0.2, 'unmeasured confounding biases DML'\n"
            "print('\\nThe orthogonal, cross-fitted machinery is intact -- but X0 is not\\n'\n"
            "      'in X, so its confounding leaks straight back into theta_hat.')"},
        {"md": "### 🔧 Exercise 6.1 — does a fancier learner help?\n\n"
            "A natural hope: maybe a *deeper, bigger* forest can compensate for the "
            "missing confounder. Re-run the unmeasured-confounding case with a more "
            "flexible learner (more trees) and check whether the bias goes away. "
            "Predict the answer before running.\n\n"
            "Complete the `# TODO`."},
        {"code": "# TODO: run DML on X_obs (X0 still hidden) with a bigger forest.\n"
            "theta_big = ...   # TODO: dml_plm(X_obs, D, Y, crossfit=True,\n"
            "                  #                n_estimators=300)[0]\n"
            "# print(f'bigger-forest theta (X0 hidden) = {theta_big:.3f}')\n"
            "# print('More flexibility cannot conjure a confounder that is not in X.')"},
        {"md": "### ✅ Solution 6.1"},
        {"code": "theta_big = dml_plm(X_obs, D, Y, crossfit=True,\n"
            "                    n_estimators=300)[0]\n"
            "print(f'standard forest (X0 hidden) = {theta_unm:.3f}')\n"
            "print(f'bigger forest   (X0 hidden) = {theta_big:.3f}')\n"
            "print(f'TRUE theta                  = {TRUE_THETA:.3f}')\n"
            "assert abs(theta_big - TRUE_THETA) > 0.2, 'still biased -- flexibility cannot help'\n"
            "print('\\nConfirmed: a fancier learner does NOT fix unmeasured confounding.\\n'\n"
            "      'Identification is an assumption, not something ML can estimate away.')"},
        {"md": "## 7 · Wrap-up & self-check\n\n"
            "- The **partially linear model** `Y = θD + g(X) + ε`, `D = m(X) + v` "
            "isolates one effect `θ` amid flexible, high-dimensional nuisances.\n"
            "- **Naive plug-in ML is biased**: regularization bias and overfitting "
            "leak into `θ̂`. *Prediction is not estimation.*\n"
            "- **Frisch–Waugh–Lovell** gives the cure's skeleton: residualize `Y` "
            "and `D` on `X`, then regress the residuals. DML swaps OLS partialling "
            "for ML partialling.\n"
            "- **Neyman orthogonality** makes the score first-order insensitive to "
            "nuisance error, so slow ML rates suffice for a √n-normal `θ̂`.\n"
            "- **Cross-fitting** removes own-observation overfitting; skip it and "
            "the in-sample residual variances collapse and the SE is invalid.\n"
            "- **DML does NOT fix** unmeasured confounding (we saw `θ̂` jump when we "
            "hid `X0`), positivity, or a wrong graph.\n\n"
            "**You're ready for Week 13** if you can build the cross-fitted "
            "residual-on-residual estimator from memory, explain why it beats the "
            "naive plug-in, and state one thing DML cannot do. Next week: "
            "heterogeneous effects and policy learning — turning one average effect "
            "into 'for whom, and what should we do?'"},
    ],
}
