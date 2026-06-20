# -*- coding: utf-8 -*-
"""Week 11 — Synthetic Control. Content module (mirrors week01 gold standard)."""

WEEK = {
    "number": 11,
    "slug": "synthetic_control",
    "title": "Synthetic Control",
    "block": "Block III — Quasi-experimental designs",
    "subtitle": "Build a synthetic version of the treated unit from a weighted "
                "blend of untreated ones.",
    "deliverable": "Concept Set 11 — weights, fit, and placebo inference; "
                   "Lab 8 — code a synthetic-control estimator and run in-space "
                   "placebo inference.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), concept set (1.5h), lab (2–3h).",
    "one_sentence": "When a single unit is treated and you have a panel of "
        "untreated 'donor' units, synthetic control builds a weighted average of "
        "those donors that tracks the treated unit before the intervention — and "
        "uses its continuation afterward as the counterfactual.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Explain the synthetic-control estimator: choose non-negative donor "
        "weights summing to one so the weighted donor pool matches the treated "
        "unit's pre-treatment path, then read the post-period gap as the effect.",
        "Contrast synthetic control with difference-in-differences — data-driven "
        "weights versus equal weights, and why SC does not need a parallel-trends "
        "assumption to hold for the raw averages.",
        "Judge pre-treatment fit and say why a good fit is the precondition that "
        "makes the post-period gap interpretable as an effect.",
        "Run placebo / permutation inference: apply the estimator to each donor "
        "as if it were treated and locate the real unit in that distribution.",
        "Decide when synthetic control is inappropriate — no donor mix fits the "
        "pre-period, or the treated unit sits outside the donors' convex hull so "
        "you would be extrapolating.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Abadie (2021), \"Using Synthetic Controls: Feasibility, Data "
                 "Requirements, and Methodological Aspects\" (Journal of Economic "
                 "Literature).",
         "look_for": "the convex-weighting estimator — non-negative weights that "
                     "sum to one — and the central role of good pre-treatment fit "
                     "in justifying the counterfactual."},
        {"text": "Abadie, Diamond & Hainmueller (2010), \"Synthetic Control "
                 "Methods for Comparative Case Studies,\" the California tobacco "
                 "(Proposition 99) study.",
         "look_for": "how placebo / permutation inference produces a p-value from "
                     "a single treated unit — no large-sample theory required."},
    ],
    "optional_readings": [
        {"text": "Cunningham, The Mixtape — Synthetic Control chapter.",
         "note": "A code-first walk-through that re-derives the California "
                 "tobacco result and the placebo plots step by step."},
        {"text": "Abadie & Gardeazabal (2003), Basque Country terrorism study.",
         "note": "The original application: a regional economic shock estimated "
                 "against a synthetic Basque Country."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "One treated unit, a pool of donors, a weighted match",
         "body": "Synthetic control is built for the awkward case where exactly "
            "one unit (a state, a region, a firm) is treated at a known time and "
            "you have a panel of untreated comparison units — the donor pool. "
            "Rather than pick a single 'most similar' comparison, you build a "
            "synthetic comparison: a weighted average of donors whose weighted "
            "outcome path hugs the treated unit's path in the pre-treatment "
            "period. After the intervention, the synthetic unit keeps tracking "
            "what the treated unit would have done absent treatment, and the gap "
            "between the two is the estimated effect."},
        {"heading": "The weighting problem and its constraints",
         "body": "The weights are not free. They are chosen to minimize "
            "pre-treatment fit error (typically the root-mean-square prediction "
            "error of the weighted donors against the treated unit), subject to "
            "two constraints that give the method its character.",
         "bullets": [
            [("Non-negative:  ", {"bold": True}),
             ("each weight is at least zero — you may include a donor or leave it "
              "out, but you never subtract one. No short positions.", {})],
            [("Sum to one:  ", {"bold": True}),
             ("the weights form a convex combination, so the synthetic unit is a "
              "weighted average that lives inside the donors' range — it cannot "
              "extrapolate beyond the data you actually have.", {})],
            [("Sparse by nature:  ", {"bold": True}),
             ("the constraints push most weights to exactly zero, so the synthetic "
              "unit is usually a blend of a handful of donors you can name and "
              "inspect — transparency is a feature, not an accident.", {})],
         ],
         "callout": {"title": "Why convexity matters",
            "color": "TEAL",
            "lines": ["Convex weights forbid extrapolation: the synthetic control "
                      "is an interpolation among observed units, never an "
                      "out-of-sample projection.",
                      "If the treated unit lies outside the donors' convex hull, "
                      "no convex blend can reach it — and that failure is "
                      "informative: the method tells you it cannot do the job."]}},
        {"heading": "Pre-treatment fit is the whole argument",
         "body": "The credibility of a synthetic-control study rests almost "
            "entirely on pre-treatment fit. If the synthetic unit reproduces the "
            "treated unit's outcomes (and key predictors) over a long pre-period, "
            "it is plausible that it would have continued to do so — so the "
            "post-period gap is a clean effect. If the fit is poor, the "
            "post-period gap mixes the true effect with whatever the synthetic "
            "unit was already getting wrong, and no amount of post-hoc reasoning "
            "rescues it. A long, well-matched pre-period is the price of "
            "admission.",
         "bullets": [
            [("Match the outcome path, not just one moment:  ", {"bold": True}),
             ("a synthetic unit that matches the level in the final pre-period but "
              "diverges earlier is a warning, not a success.", {})],
            [("Report the pre-period RMSE:  ", {"bold": True}),
             ("it is the natural fit statistic and the denominator of the "
              "inference test below.", {})],
         ]},
        {"heading": "Placebo (permutation) inference without large samples",
         "body": "With a single treated unit there is no sampling distribution to "
            "lean on. Instead you ask: is the gap we see for the treated unit "
            "unusual compared with the gaps we get when we pretend each donor was "
            "treated? Re-run the entire estimator on every donor (an 'in-space' "
            "placebo), collect each placebo's gap, and compare. A common test "
            "statistic is the ratio of post-period to pre-period RMSE, which "
            "rewards units that fit well before and diverge sharply after. The "
            "treated unit's rank among all the ratios gives an exact permutation "
            "p-value — if it is the largest of twenty, p ≈ 1/20 = 0.05.",
         "callout": {"title": "The inference is a rank, not a t-statistic",
            "color": "RED",
            "lines": ["You are not estimating a standard error. You are asking "
                      "whether the treated unit's gap is extreme within a "
                      "reference set of placebo gaps.",
                      "Discard placebos with bad pre-period fit before ranking — "
                      "a unit the method could not fit produces a huge gap for "
                      "reasons that have nothing to do with treatment."]}},
        {"heading": "When synthetic control beats difference-in-differences",
         "body": "DiD assigns every comparison unit equal weight and trusts that "
            "the treated and control averages would have moved in parallel. "
            "Synthetic control instead lets the data pick weights so the "
            "pre-treatment paths actually coincide, which can hold even when raw "
            "parallel trends plainly do not. SC shines when you have one treated "
            "unit, a long pre-period, and a rich donor pool — and when a single "
            "good comparison does not exist but a blend does. It is the wrong "
            "tool when the pre-period is short, the donor pool is thin, the "
            "treated unit is an outlier, or anticipation and interference "
            "contaminate the donors.",
         "bullets": [
            [("DiD:  ", {"bold": True}),
             ("equal weights, parallel-trends assumption on raw averages, many "
              "treated units welcome.", {})],
            [("Synthetic control:  ", {"bold": True}),
             ("data-driven convex weights, fit enforced in the pre-period, built "
              "for the single-treated-unit comparative case study.", {})],
         ]},
    ],
    "problem_set": {
        "label": "Concept Set 11",
        "title": "Weights, fit, and placebo inference",
        "intro": "Answer in your own words. Where a contrast with "
            "difference-in-differences is useful, draw it explicitly. Try all "
            "five before you look at the solutions.",
        "problems": [
            {"title": "How synthetic control differs from difference-in-differences",
             "prompt": "Both methods estimate the effect on a treated unit using "
                "untreated comparisons over time. State the two key differences in "
                "how they use the comparison units, and explain why synthetic "
                "control does not require the raw treated and control averages to "
                "move in parallel.",
             "solution_title": "Data-driven convex weights vs. equal weights; SC "
                "enforces pre-period fit instead of assuming parallel trends.",
             "solution": [
                "DiD gives every control unit equal weight and identifies the "
                "effect under parallel trends: absent treatment, the treated and "
                "the (equally weighted) control average would have changed by the "
                "same amount.",
                "Synthetic control chooses non-negative weights summing to one so "
                "the weighted donor path matches the treated unit's path in the "
                "pre-period. The match is built, not assumed.",
                "Because the synthetic unit is constructed to coincide with the "
                "treated unit before treatment, parallel movement of the raw "
                "averages is unnecessary — the relevant 'parallel trend' is "
                "between the treated unit and its synthetic, and it is enforced by "
                "construction over the whole pre-period."]},
            {"title": "Why weights are non-negative and sum to one",
             "prompt": "The synthetic-control weights are constrained to be "
                "non-negative and to sum to one. What would go wrong if you "
                "dropped each constraint — allowed negative weights, or let the "
                "weights sum to something other than one? What property do the two "
                "constraints together guarantee?",
             "solution_title": "Convexity prevents extrapolation and keeps the "
                "estimator interpretable.",
             "solution": [
                "Allowing negative weights lets the synthetic unit subtract "
                "donors, which can fit the pre-period almost perfectly by "
                "overfitting noise and can place the synthetic outcome far outside "
                "anything observed — pure extrapolation.",
                "Dropping the sum-to-one constraint lets the synthetic level drift "
                "away from the donors' scale, again extrapolating rather than "
                "interpolating.",
                "Together, non-negativity and sum-to-one make the weights a convex "
                "combination: the synthetic unit lies inside the convex hull of "
                "the donors, so it interpolates among real units. It also makes "
                "the solution sparse and transparent — usually a few named donors "
                "carry all the weight."]},
            {"title": "Why good pre-treatment fit matters",
             "prompt": "A colleague reports a large post-intervention gap between "
                "the treated unit and its synthetic control, but the two curves "
                "visibly diverge during the pre-treatment period as well. Why is "
                "this estimate not credible, and what is the role of pre-treatment "
                "fit in the identification argument?",
             "solution_title": "Without pre-period fit, the post-period gap is not "
                "an effect — it is the fit error continued.",
             "solution": [
                "The entire logic is: if the synthetic unit tracked the treated "
                "unit closely before treatment, it is reasonable to believe it "
                "would have continued to do so absent treatment, making the "
                "post-period gap the causal effect.",
                "If the curves already diverge in the pre-period, that premise "
                "fails. The post-period gap now blends the true effect with the "
                "pre-existing mismatch, and you cannot tell them apart.",
                "Good pre-treatment fit — a small pre-period RMSE over a long "
                "window — is the precondition that licenses reading the gap as an "
                "effect. Report it; a poor fit means the design has not "
                "identified anything."]},
            {"title": "How placebo (in-space) tests give inference",
             "prompt": "You have one treated unit and nineteen donors, so "
                "classical standard errors are unavailable. Describe the in-space "
                "placebo procedure and explain how it yields a p-value. What "
                "statistic is commonly ranked, and why is it preferable to the raw "
                "post-period gap?",
             "solution_title": "Permute the treatment across units; rank the "
                "post/pre RMSE ratio to get an exact p-value.",
             "solution": [
                "Re-run the full synthetic-control estimator pretending each donor "
                "is the treated unit (its donor pool is the remaining units). This "
                "produces a gap trajectory for every placebo — a reference "
                "distribution of 'effects' where none should exist.",
                "Rank the treated unit's test statistic within this distribution. "
                "If its statistic is the largest of twenty units, the permutation "
                "p-value is about 1/20 = 0.05 — an exact randomization-style "
                "p-value that needs no large-sample theory.",
                "The usual statistic is the ratio of post-period RMSE to "
                "pre-period RMSE, not the raw gap. A donor that simply fits badly "
                "before treatment will show a large post gap for the wrong reason; "
                "the ratio penalizes poor pre-period fit and isolates units that "
                "fit well then diverge."]},
            {"title": "When synthetic control is inappropriate",
             "prompt": "Give two distinct situations in which synthetic control "
                "should not be used, even though you have panel data on a treated "
                "unit and several comparisons. Tie each to a specific feature of "
                "the method.",
             "solution_title": "No convex blend fits the pre-period, or the "
                "treated unit is outside the donors' hull (extrapolation).",
             "solution": [
                "Poor pre-treatment fit: if no convex combination of donors can "
                "track the treated unit's pre-period (short pre-window, thin or "
                "dissimilar donor pool), the fit error is large and the gap is "
                "uninterpretable — the method cannot construct a credible "
                "counterfactual.",
                "Extrapolation / outlier treated unit: if the treated unit lies "
                "outside the convex hull of the donors (e.g. its outcome is more "
                "extreme than any donor on a key dimension), the convexity "
                "constraint makes a good match impossible, and forcing one would "
                "require the very extrapolation the method forbids.",
                "Other red flags: anticipation effects before the official date, "
                "spillover/interference contaminating donors, or structural breaks "
                "in the donor pool — each violates the assumption that donors "
                "behave like an untreated version of the treated unit."]},
        ],
    },
    "lab": {
        "label": "Lab 8",
        "title": "Synthetic control",
        "goal": "code a synthetic-control estimator from scratch — solve for "
            "convex donor weights that match a treated unit's pre-period, build "
            "the synthetic counterfactual, estimate the gap, and run in-space "
            "placebo inference to get a permutation p-value. Pick R or Python.",
        "steps": [
            {"heading": "Step 1 · Simulate a panel with a known effect",
             "body": "Make one treated unit and a donor pool of ~20 untreated "
                "units, all driven by a few shared latent factors so a synthetic "
                "match exists. Choose an intervention time and inject a KNOWN "
                "additive treatment effect into the treated unit's post-period — "
                "that is your ground truth to recover.",
             "bullets": [
                "Keep the treated unit's factor loadings inside the donors' spread "
                "so a convex blend can reach it.",
                "Use a long pre-period (e.g. 20 of 30 periods) so fit is "
                "well-determined.",
             ]},
            {"heading": "Step 2 · Solve for convex weights (pre-period RMSE)",
             "body": "Minimize the pre-treatment mean-squared error of the "
                "weighted donors against the treated unit, subject to weights ≥ 0 "
                "and weights summing to 1. In Python use scipy.optimize.minimize "
                "with an equality constraint and box bounds (SLSQP); in R use "
                "tidysynth, which wraps the same optimization.",
             "code_python": "import numpy as np\n"
                "from scipy.optimize import minimize\n\n"
                "def synth_weights(target_pre, donors_pre):\n"
                "    \"\"\"Non-negative weights summing to 1, min pre-period MSE.\"\"\"\n"
                "    J = donors_pre.shape[0]\n"
                "    loss = lambda w: np.mean((target_pre - w @ donors_pre) ** 2)\n"
                "    cons = ({'type': 'eq', 'fun': lambda w: w.sum() - 1.0},)\n"
                "    res = minimize(loss, np.full(J, 1.0 / J), method='SLSQP',\n"
                "                   bounds=[(0.0, 1.0)] * J, constraints=cons,\n"
                "                   options={'maxiter': 1000, 'ftol': 1e-12})\n"
                "    return res.x\n\n"
                "w = synth_weights(treated[:T0], donors[:, :T0])\n"
                "print('weights sum to', round(w.sum(), 3),\n"
                "      '| pre-RMSE', round(np.sqrt(np.mean(\n"
                "          (treated[:T0] - w @ donors[:, :T0]) ** 2)), 3))",
             "code_r": 'library(tidysynth)\n'
                '# panel: long data frame with columns unit, time, outcome\n'
                'sc <- panel %>%\n'
                '  synthetic_control(outcome = outcome, unit = unit, time = time,\n'
                '                    i_unit = "treated", i_time = intervention_time,\n'
                '                    generate_placebos = TRUE) %>%\n'
                '  generate_predictor(time_window = pre_period,\n'
                '                     mean_outcome = mean(outcome)) %>%\n'
                '  generate_weights(optimization_window = pre_period) %>%\n'
                '  generate_control()\n'
                'sc %>% grab_unit_weights()   # the donor weights (>= 0, sum to 1)'},
            {"heading": "Step 3 · Build the synthetic unit and estimate the gap",
             "body": "Apply the weights across ALL periods to get the synthetic "
                "outcome path. The gap is treated minus synthetic; average it over "
                "the post-period and compare to the true effect you injected. "
                "Confirm recovery within a tolerance.",
             "code_python": "synthetic = w @ donors            # weights applied "
                "to every period\n"
                "gap = treated - synthetic\n"
                "post_gap = gap[T0:].mean()\n"
                "print(f'estimated effect = {post_gap:.2f}  | true = {TRUE_EFFECT}')\n"
                "assert abs(post_gap - TRUE_EFFECT) < 2.0",
             "code_r": 'sc %>% grab_synthetic_control()        # treated vs '
                'synthetic per period\nsc %>% plot_trends()                   '
                '# eyeball pre-period fit and the post gap'},
            {"heading": "Step 4 · In-space placebo / permutation inference",
             "body": "Re-run the whole estimator with each donor playing the "
                "treated unit (its donor pool is the remaining units). For each, "
                "compute the post/pre RMSE ratio. The treated unit's rank among "
                "all ratios is an exact permutation p-value.",
             "code_python": "def post_pre_ratio(g):\n"
                "    pre  = np.sqrt(np.mean(g[:T0] ** 2))\n"
                "    post = np.sqrt(np.mean(g[T0:] ** 2))\n"
                "    return post / max(pre, 1e-8)\n\n"
                "def placebo_gap(idx, Y):\n"
                "    target, pool = Y[idx], np.delete(Y, idx, axis=0)\n"
                "    wj = synth_weights(target[:T0], pool[:, :T0])\n"
                "    return target - wj @ pool\n\n"
                "treated_ratio = post_pre_ratio(gap)\n"
                "placebos = np.array([post_pre_ratio(placebo_gap(j, Y))\n"
                "                     for j in range(1, len(Y))])\n"
                "p = np.mean(np.append(placebos, treated_ratio) >= treated_ratio)\n"
                "print(f'permutation p-value = {p:.3f}')",
             "code_r": 'sc %>% plot_placebos()                 '
                '# treated gap vs every placebo gap\n'
                'sc %>% plot_mspe_ratio()               '
                '# ranked post/pre MSPE ratios -> the p-value\n'
                'sc %>% grab_significance()             # the permutation p-value'},
        ],
        "expected": "The convex weights sum to one with most donors at exactly "
            "zero, the synthetic unit hugs the treated unit's pre-period (small "
            "RMSE), and the estimated post-period gap lands close to the injected "
            "true effect. In the placebo plot the treated unit's gap is a clear "
            "outlier, and its post/pre RMSE ratio is the largest (or nearly so) of "
            "all units, giving a small permutation p-value (≈ 0.05 with twenty "
            "units). Same panel, but only the fitted comparison — not a raw "
            "average — makes the gap a credible effect.",
        "submit": [
            "Push your code plus the treated-vs-synthetic plot and the placebo "
            "plot to your week11 folder.",
            "Report the donor weights, the pre-period RMSE, the estimated effect "
            "next to the truth, and the permutation p-value.",
            "Write two sentences on whether SC or DiD is the better fit for your "
            "simulated panel, and why.",
        ],
    },
    "self_check": [
        "Explain to a classmate, without notes, how synthetic control builds the "
        "counterfactual and why the weights are convex.",
        "State the two ways SC differs from DiD and why SC sidesteps raw "
        "parallel trends.",
        "Say why pre-treatment fit is the precondition for reading the post gap "
        "as an effect.",
        "Describe the in-space placebo test and how it produces a p-value from "
        "one treated unit.",
        "Name two situations where synthetic control is the wrong tool.",
    ],
    "next_week": {
        "heading": "Coming up: Week 12 — Double / debiased machine learning",
        "teaser": "We leave the single-treated-unit world and return to many "
            "units with many covariates. You'll meet the Neyman-orthogonal score "
            "and cross-fitting: how to plug flexible machine-learning models in "
            "for the nuisance functions (the outcome model and the propensity "
            "model) without letting their regularization bias leak into the "
            "treatment-effect estimate. Skim the Chernozhukov et al. (2018) "
            "abstract to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 11", "items": [
            {"t": "The setup", "d": "One treated unit, a donor pool, a known "
             "intervention time."},
            {"t": "The estimator", "d": "Convex donor weights that match the "
             "pre-treatment path."},
            {"t": "Pre-treatment fit", "d": "Why a good pre-period is the whole "
             "argument."},
            {"t": "Placebo inference", "d": "Permuting treatment across units for "
             "a p-value."},
            {"t": "SC vs. DiD", "d": "Data-driven weights versus equal weights and "
             "parallel trends."},
            {"t": "California Prop 99", "d": "The canonical tobacco-control case "
             "study."},
        ]},
        {"type": "content", "kicker": "The problem",
         "title": "Sometimes only one unit is treated",
         "bullets": [
            "A state passes a law; a region suffers a shock; a single firm adopts "
            "a policy. n_treated = 1.",
            "There is no randomized control and no obvious single comparison unit "
            "that is 'just like' the treated one.",
            "But you have a panel: the treated unit and many untreated 'donor' "
            "units, observed over many periods.",
            "Difference-in-differences would average all donors equally and hope "
            "for parallel trends — often a stretch.",
            ("Synthetic control builds a tailored comparison instead of assuming "
             "one.", 1),
         ],
         "note": {"title": "Comparative case study",
            "body": "One treated unit, a long pre-period, a rich donor pool. This "
            "is the niche synthetic control was designed for."}},
        {"type": "content", "kicker": "The idea in one line",
         "title": "Reconstruct the treated unit from a blend of donors",
         "bullets": [
            "Find weights on the donors so their weighted outcome path matches the "
            "treated unit BEFORE treatment.",
            "Carry those weights forward: the weighted donors become the synthetic "
            "counterfactual after treatment.",
            "The gap between treated and synthetic in the post-period is the "
            "estimated effect.",
            "No single donor need resemble the treated unit — the blend does.",
         ],
         "note": {"title": "Counterfactual",
            "body": "What would the treated unit have looked like had the "
            "intervention never happened? The synthetic unit answers that."}},

        {"type": "section", "kicker": "Part 1", "title": "The estimator",
         "subtitle": "Convex weights chosen to minimize pre-treatment fit error — "
            "the optimization at the heart of the method."},
        {"type": "content", "kicker": "The weighting problem",
         "title": "Choose weights to match the pre-period", "bullets": [
            "Pick weights w on the donor units to minimize pre-treatment "
            "prediction error (e.g. RMSE of weighted donors vs. treated).",
            "Subject to two constraints that define the method's character.",
            ("Non-negative: every weight ≥ 0 — include or omit a donor, never "
             "subtract one.", 1),
            ("Sum to one: the weights form a convex combination — a weighted "
             "average.", 1),
            "Solve it with constrained optimization (SLSQP) or projected gradient.",
         ],
         "note": {"title": "Objective",
            "body": "minimize ||Y_treated,pre − W·Y_donors,pre|| subject to "
            "w ≥ 0 and Σw = 1."}},
        {"type": "compare", "kicker": "Why these constraints",
         "title": "Convexity buys interpolation and transparency", "columns": [
            {"head": "Non-negative weights", "sub": "w ≥ 0", "points": [
                "No short positions on donors.",
                "Forbids fitting by subtraction.",
                "Keeps the blend interpretable."]},
            {"head": "Weights sum to one", "sub": "Σw = 1", "points": [
                "A weighted average, on the donors' scale.",
                "Synthetic lies in the convex hull.",
                "No extrapolation beyond the data."]},
            {"head": "Consequence", "sub": "sparsity", "points": [
                "Most weights are exactly zero.",
                "A handful of named donors carry it.",
                "You can inspect and defend the mix."]},
        ]},
        {"type": "statement",
         "quote": "The synthetic control is an interpolation among real units — "
            "never a projection beyond them.",
         "attribution": "Convex weights mean the synthetic unit can only blend "
            "donors you actually observed. If the treated unit lies outside their "
            "hull, the method tells you so by fitting badly."},

        {"type": "section", "kicker": "Part 2", "title": "Pre-treatment fit",
         "subtitle": "The credibility of the whole design lives or dies on how "
            "well the synthetic unit tracks the treated one before treatment."},
        {"type": "content", "kicker": "Why fit is the argument",
         "title": "Good pre-period fit licenses the counterfactual", "bullets": [
            "If the synthetic unit matched the treated unit for many pre-periods, "
            "it likely would have kept matching absent treatment.",
            "Then the post-period gap is the effect — the synthetic is a credible "
            "'what would have happened.'",
            "If the curves diverge before treatment, the premise fails and the gap "
            "is contaminated by fit error.",
            "Match the whole path, not a single moment; report the pre-period "
            "RMSE.",
         ],
         "note": {"title": "Precondition",
            "body": "No good pre-fit, no identification. A poor match means the "
            "design has not produced a counterfactual at all."}},
        {"type": "content", "kicker": "Diagnostics",
         "title": "How to judge the fit honestly", "bullets": [
            "Plot treated vs. synthetic over the full pre-period — eyeball the "
            "tracking.",
            "Report pre-period RMSE as the headline fit statistic.",
            "Check that the match holds early, not just in the last pre-period.",
            "A long pre-period makes a good fit meaningful; a short one makes it "
            "cheap.",
         ],
         "note": {"title": "Red flag",
            "body": "A synthetic that matches only the final pre-period level but "
            "misses the earlier trajectory is overfitting, not fitting."}},

        {"type": "section", "kicker": "Part 3", "title": "Placebo inference",
         "subtitle": "With one treated unit there is no standard error — so we "
            "permute the treatment across units and rank what we see."},
        {"type": "steps", "kicker": "In-space placebo test",
         "title": "Inference by permuting the treatment", "steps": [
            {"title": "Pretend each donor is treated",
             "body": "— re-run the full estimator with that donor as the target."},
            {"title": "Collect placebo gaps",
             "body": "— a reference distribution of 'effects' where none should "
             "exist."},
            {"title": "Pick a statistic",
             "body": "— the ratio of post-period to pre-period RMSE."},
            {"title": "Rank the treated unit",
             "body": "— its position gives an exact permutation p-value."},
        ],
         "note": "Largest of 20 ratios → p ≈ 1/20 = 0.05. No large-sample theory "
            "required."},
        {"type": "content", "kicker": "Why the RMSE ratio",
         "title": "Rank the post/pre RMSE ratio, not the raw gap", "bullets": [
            "A donor that simply fits badly before treatment shows a big post gap "
            "for the wrong reason.",
            "The post/pre RMSE ratio penalizes poor pre-period fit.",
            "It rewards exactly the signature we want: a tight pre-period match "
            "then a sharp post-period divergence.",
            "Drop placebos with terrible pre-fit before ranking — they are noise, "
            "not evidence.",
         ],
         "note": {"title": "The statistic",
            "body": "ratio = post-period RMSE ÷ pre-period RMSE. Large only when "
            "the unit fit well and then broke away."}},
        {"type": "statement",
         "quote": "The p-value is a rank, not a t-statistic.",
         "attribution": "You are not estimating a standard error. You are asking "
            "whether the treated unit's gap is extreme within a reference set of "
            "placebo gaps you generated yourself."},

        {"type": "section", "kicker": "Part 4", "title": "SC versus DiD",
         "subtitle": "Both compare a treated unit to untreated ones over time — "
            "but they make very different bets about the comparison."},
        {"type": "compare", "kicker": "Two ways to build the counterfactual",
         "title": "Equal weights vs. fitted weights", "columns": [
            {"head": "Difference-in-differences", "points": [
                "Every control unit weighted equally.",
                "Assumes parallel trends on raw averages.",
                "Happy with many treated units.",
                "Fails if trends visibly diverge."]},
            {"head": "Synthetic control", "points": [
                "Data-driven convex weights.",
                "Fit enforced over the pre-period.",
                "Built for one treated unit.",
                "Fails if no blend fits or treated is an outlier."]},
        ]},
        {"type": "table", "kicker": "Which tool when",
         "title": "Choosing between SC and DiD",
         "headers": ["Situation", "Lean toward"],
         "rows": [
            ["One treated unit, long pre-period, rich donors", "Synthetic control"],
            ["Many treated units, short panel", "Difference-in-differences"],
            ["Raw parallel trends look implausible", "Synthetic control"],
            ["Treated unit is an outlier (outside hull)", "Neither — extrapolation"],
            ["Thin donor pool, short pre-period", "Neither — poor fit"],
         ],
         "note": {"title": "Rule of thumb",
            "body": "SC is the comparative-case-study tool: one treated unit, a "
            "long pre-period, and donors that can blend to match it."}},
        {"type": "content", "kicker": "When NOT to use it",
         "title": "Synthetic control's failure modes", "bullets": [
            "No convex blend fits the pre-period — short window or thin/dissimilar "
            "donors.",
            "Treated unit lies outside the donors' convex hull — a match would "
            "require extrapolation.",
            "Anticipation: the effect starts before the official date, "
            "contaminating the pre-period.",
            "Interference: the intervention spills over onto donors, so they are "
            "no longer 'untreated.'",
         ],
         "note": {"title": "The method is honest",
            "body": "A large pre-period RMSE is the method telling you it cannot "
            "build a credible counterfactual. Listen to it."}},

        {"type": "section", "kicker": "Part 5", "title": "California & Prop 99",
         "subtitle": "The canonical application: did California's 1988 "
            "tobacco-control program cut cigarette consumption?"},
        {"type": "steps", "kicker": "Case study · Proposition 99 (1988)",
         "title": "A synthetic California", "steps": [
            {"title": "The intervention",
             "body": "— California's Prop 99 raised cigarette taxes and funded "
             "anti-smoking programs."},
            {"title": "The donor pool",
             "body": "— other U.S. states without comparable programs, observed "
             "for years before 1988."},
            {"title": "The synthetic",
             "body": "— a weighted blend of a few states that tracks California's "
             "pre-1988 consumption."},
            {"title": "The result",
             "body": "— per-capita sales fall well below synthetic California; "
             "placebo tests make it significant."},
        ],
         "note": "A single treated state, a clean pre-period, and inference by "
            "permuting across the other states — the template for the field."},
        {"type": "content", "kicker": "What made it convincing",
         "title": "Why the Prop 99 study persuaded", "bullets": [
            "Long pre-period fit: synthetic California hugged real California for "
            "years before 1988.",
            "A transparent, sparse donor mix you could name and scrutinize.",
            "Placebo tests: California's gap was an outlier among all states' "
            "placebo gaps.",
            "The estimate survived dropping high-weight donors and shifting the "
            "pre-period.",
         ],
         "note": {"title": "Robustness",
            "body": "Leave-one-out and backdating checks are now standard "
            "companions to any synthetic-control result."}},
        {"type": "statement",
         "quote": "Build the comparison; don't assume it.",
         "attribution": "This week: simulate a panel with a known effect, solve "
            "for convex weights, recover the truth, and earn a p-value by "
            "permuting the treatment across donors. See you in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · The setup — one treated unit and a donor pool\n\n"
            "Synthetic control lives in a world where **exactly one unit is "
            "treated** at a known time and we have a panel of untreated *donor* "
            "units. We simulate that here. All units are driven by a few **shared "
            "latent factors** (so a weighted blend of donors can reproduce the "
            "treated unit), and we inject a **known additive treatment effect** "
            "into the treated unit's post-period. That ground truth is what our "
            "estimator must recover."},
        {"code": "from scipy.optimize import minimize\n\n"
            "n_donors = 20\n"
            "T, T0 = 30, 20          # 30 periods; treatment after period index 19\n"
            "TRUE_EFFECT = 8.0       # known additive effect on the treated post-period\n\n"
            "time = np.arange(T)\n"
            "# three shared latent factors everyone loads on\n"
            "factors = np.column_stack([\n"
            "    np.sin(time / 3.0),\n"
            "    np.linspace(0, 4, T),\n"
            "    np.cos(time / 5.0) + time * 0.05,\n"
            "])\n\n"
            "def make_unit(loadings, level, noise=0.6):\n"
            "    return level + factors @ loadings + RNG.normal(0, noise, size=T)\n\n"
            "# Treated unit: loadings INSIDE the donors' spread so a convex blend can match it.\n"
            "treated_loadings = np.array([2.0, 1.5, 2.5])\n"
            "donor_loadings = RNG.normal(treated_loadings, 1.2, size=(n_donors, 3))\n"
            "donor_levels   = RNG.normal(5.0, 1.5, size=n_donors)\n\n"
            "Y = np.zeros((1 + n_donors, T))\n"
            "Y[0] = make_unit(treated_loadings, 5.0)          # row 0 = treated\n"
            "for j in range(n_donors):\n"
            "    Y[1 + j] = make_unit(donor_loadings[j], donor_levels[j])\n\n"
            "Y[0, T0:] += TRUE_EFFECT                          # inject the effect\n"
            "treated, donors = Y[0], Y[1:]\n"
            "print(f'panel: 1 treated + {n_donors} donors over {T} periods '\n"
            "      f'({T0} pre, {T - T0} post)')"},
        {"md": "## 2 · Solve for convex donor weights\n\n"
            "The estimator: choose weights `w` on the donors that **minimize "
            "pre-treatment RMSE** against the treated unit, subject to **`w ≥ 0`** "
            "and **`Σw = 1`**. We hand that constrained problem to "
            "`scipy.optimize.minimize` with SLSQP — box bounds for non-negativity "
            "and an equality constraint for the sum."},
        {"code": "def synth_weights(target_pre, donors_pre):\n"
            "    \"\"\"Non-negative weights summing to 1 that minimize pre-period MSE.\"\"\"\n"
            "    J = donors_pre.shape[0]\n"
            "    loss = lambda w: np.mean((target_pre - w @ donors_pre) ** 2)\n"
            "    cons = ({'type': 'eq', 'fun': lambda w: w.sum() - 1.0},)\n"
            "    res = minimize(loss, np.full(J, 1.0 / J), method='SLSQP',\n"
            "                   bounds=[(0.0, 1.0)] * J, constraints=cons,\n"
            "                   options={'maxiter': 1000, 'ftol': 1e-12})\n"
            "    return res.x\n\n"
            "w = synth_weights(treated[:T0], donors[:, :T0])\n"
            "pre_rmse = np.sqrt(np.mean((treated[:T0] - w @ donors[:, :T0]) ** 2))\n\n"
            "print(f'weights sum to {w.sum():.3f}   (should be 1)')\n"
            "print(f'min weight     {w.min():.4f}   (should be >= 0)')\n"
            "print(f'donors used    {(w > 0.01).sum()} of {n_donors}   "
            "(convexity makes it sparse)')\n"
            "print(f'pre-period RMSE {pre_rmse:.3f}')\n"
            "assert abs(w.sum() - 1.0) < 1e-4, 'weights must sum to 1'\n"
            "assert w.min() > -1e-6, 'weights must be non-negative'\n"
            "assert pre_rmse < 1.0, 'a good blend should fit the pre-period tightly'"},
        {"md": "Note how **most weights are exactly zero** — the convexity "
            "constraints make the solution sparse, so the synthetic unit is a "
            "blend of just a few donors you could name and inspect."},
        {"md": "## 3 · Build the synthetic control and plot it\n\n"
            "Apply the weights across **all** periods. Before treatment the "
            "synthetic should hug the treated unit; after treatment it keeps "
            "tracking the counterfactual while the real treated unit jumps by the "
            "injected effect."},
        {"code": "synthetic = w @ donors                 # weights applied every period\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot(time, treated,   label='treated unit', lw=2)\n"
            "ax.plot(time, synthetic, '--', label='synthetic control', lw=2)\n"
            "ax.axvline(T0 - 0.5, color='grey', ls=':', label='intervention')\n"
            "ax.set_xlabel('period'); ax.set_ylabel('outcome')\n"
            "ax.set_title('Treated vs. synthetic control')\n"
            "ax.legend()\n"
            "print('Pre-treatment: the two curves overlap. '\n"
            "      'Post-treatment: a gap opens — that is the effect.')"},
        {"md": "## 4 · Estimate the gap and check it against the truth\n\n"
            "The estimated effect is the average post-period gap, "
            "`treated − synthetic`. We compare it to the injected `TRUE_EFFECT` "
            "and assert recovery."},
        {"code": "gap = treated - synthetic\n"
            "post_gap = gap[T0:].mean()\n"
            "print(f'estimated effect = {post_gap:.3f}')\n"
            "print(f'true effect      = {TRUE_EFFECT:.3f}')\n"
            "print(f'pre-period gap   = {gap[:T0].mean():.3f}   "
            "(should be ~0 — good fit)')\n"
            "assert abs(post_gap - TRUE_EFFECT) < 2.0, \\\n"
            "    'synthetic control should recover the injected effect'"},
        {"md": "### 🔧 Exercise 4.1 — convex weights beat equal weights\n\n"
            "Difference-in-differences would weight every donor **equally**. Build "
            "the equal-weight synthetic (a plain average of all donors) and "
            "compare its **pre-period RMSE** to the fitted convex weights from "
            "Section 2. Which fits the treated unit's pre-period better, and why "
            "does that matter for the post-period gap?\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: build the equal-weight synthetic and its pre-period RMSE.\n"
            "equal_w = ...        # TODO: 1/n_donors on every donor\n"
            "# synth_equal     = equal_w @ donors\n"
            "# equal_pre_rmse  = np.sqrt(np.mean((treated[:T0] - synth_equal[:T0]) ** 2))\n"
            "# print(equal_pre_rmse, pre_rmse)"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "equal_w = np.full(n_donors, 1.0 / n_donors)\n"
            "synth_equal = equal_w @ donors\n"
            "equal_pre_rmse = np.sqrt(np.mean((treated[:T0] - synth_equal[:T0]) ** 2))\n"
            "print(f'equal-weight pre-RMSE = {equal_pre_rmse:.3f}')\n"
            "print(f'convex-weight pre-RMSE = {pre_rmse:.3f}')\n"
            "print('Fitted convex weights track the pre-period far better, so the '\n"
            "      'post gap is a cleaner effect.')\n"
            "assert equal_pre_rmse > pre_rmse, \\\n"
            "    'data-driven weights should fit the pre-period better than equal weights'"},
        {"md": "## 5 · Placebo-in-space inference (a permutation p-value)\n\n"
            "With one treated unit there is no standard error. Instead we **pretend "
            "each donor was treated**: re-run the whole estimator with that donor "
            "as the target and the remaining units as its donor pool. The test "
            "statistic is the **ratio of post-period to pre-period RMSE**, which "
            "rewards a tight pre-period fit followed by a sharp post divergence. "
            "The treated unit's rank among all the ratios is an exact permutation "
            "p-value."},
        {"code": "def post_pre_ratio(g):\n"
            "    pre  = np.sqrt(np.mean(g[:T0] ** 2))\n"
            "    post = np.sqrt(np.mean(g[T0:] ** 2))\n"
            "    return post / max(pre, 1e-8)\n\n"
            "def placebo_gap(idx, Y):\n"
            "    \"\"\"Treat unit `idx` as if treated; donor pool = everyone else.\"\"\"\n"
            "    target, pool = Y[idx], np.delete(Y, idx, axis=0)\n"
            "    wj = synth_weights(target[:T0], pool[:, :T0])\n"
            "    return target - wj @ pool\n\n"
            "treated_ratio = post_pre_ratio(gap)\n"
            "placebo_ratios = np.array([post_pre_ratio(placebo_gap(j, Y))\n"
            "                           for j in range(1, 1 + n_donors)])\n\n"
            "all_ratios = np.append(placebo_ratios, treated_ratio)\n"
            "p_value = np.mean(all_ratios >= treated_ratio)\n\n"
            "print(f'treated post/pre RMSE ratio = {treated_ratio:.2f}')\n"
            "print(f'placebo ratios: median {np.median(placebo_ratios):.2f}, "
            "max {placebo_ratios.max():.2f}')\n"
            "print(f'permutation p-value = {p_value:.3f}')\n"
            "assert p_value <= 0.10, 'the genuine effect should stand out from placebos'"},
        {"code": "# Visualize: every placebo gap (grey) against the treated gap (red).\n"
            "fig, ax = plt.subplots()\n"
            "for j in range(1, 1 + n_donors):\n"
            "    ax.plot(time, placebo_gap(j, Y), color='0.75', lw=1)\n"
            "ax.plot(time, gap, color='crimson', lw=2.5, label='treated unit')\n"
            "ax.axvline(T0 - 0.5, color='grey', ls=':')\n"
            "ax.axhline(0, color='black', lw=0.8)\n"
            "ax.set_xlabel('period'); ax.set_ylabel('gap (unit − synthetic)')\n"
            "ax.set_title('In-space placebo gaps')\n"
            "ax.legend()\n"
            "print('The treated unit (red) is a clear outlier after the intervention.')"},
        {"md": "### 🔧 Exercise 5.1 — a permutation test on the raw post gap\n\n"
            "Instead of the RMSE ratio, rank the **average post-period gap** "
            "itself. Compute each placebo's mean post-period gap, then the "
            "two-sided permutation p-value: the fraction of units (placebos plus "
            "the treated) whose `|post gap|` is at least as large as the treated "
            "unit's. Does the treated unit still come out significant?\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: collect each placebo's mean post-period gap, then a two-sided p-value.\n"
            "placebo_post_gaps = ...     # TODO: array of mean post gaps for donors 1..n\n"
            "# treated_post = gap[T0:].mean()\n"
            "# allg = np.append(placebo_post_gaps, treated_post)\n"
            "# p_raw = np.mean(np.abs(allg) >= abs(treated_post))\n"
            "# print(p_raw)"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "placebo_post_gaps = np.array(\n"
            "    [placebo_gap(j, Y)[T0:].mean() for j in range(1, 1 + n_donors)])\n"
            "treated_post = gap[T0:].mean()\n"
            "allg = np.append(placebo_post_gaps, treated_post)\n"
            "p_raw = np.mean(np.abs(allg) >= abs(treated_post))\n"
            "print(f'treated mean post gap = {treated_post:.2f}')\n"
            "print(f'placebo |post gap| median = "
            "{np.median(np.abs(placebo_post_gaps)):.2f}')\n"
            "print(f'two-sided permutation p-value = {p_raw:.3f}')\n"
            "assert p_raw <= 0.10, 'the treated gap should be extreme vs. placebos'"},
        {"md": "### 🔧 Exercise 5.2 — when synthetic control should refuse\n\n"
            "Synthetic control fails when the treated unit lies **outside the "
            "donors' convex hull** — no convex blend can reach it. Construct a "
            "would-be treated unit with **extreme** factor loadings (far beyond "
            "any donor), fit weights to its pre-period, and show the pre-period "
            "RMSE is now huge. That large fit error is the method honestly "
            "refusing to build a counterfactual.\n\n"
            "Fill in the `# TODO`s below."},
        {"code": "# TODO: an outlier unit with extreme loadings, then its pre-period RMSE.\n"
            "bad_loadings = ...     # TODO: e.g. np.array([12.0, -10.0, 9.0])\n"
            "# bad_unit = 5.0 + factors @ bad_loadings + RNG.normal(0, 0.6, size=T)\n"
            "# w_bad    = synth_weights(bad_unit[:T0], donors[:, :T0])\n"
            "# bad_rmse = np.sqrt(np.mean((bad_unit[:T0] - w_bad @ donors[:, :T0]) ** 2))\n"
            "# print(bad_rmse, pre_rmse)"},
        {"md": "### ✅ Solution 5.2"},
        {"code": "bad_loadings = np.array([12.0, -10.0, 9.0])     # far outside donor spread\n"
            "bad_unit = 5.0 + factors @ bad_loadings + RNG.normal(0, 0.6, size=T)\n"
            "w_bad = synth_weights(bad_unit[:T0], donors[:, :T0])\n"
            "bad_rmse = np.sqrt(np.mean((bad_unit[:T0] - w_bad @ donors[:, :T0]) ** 2))\n"
            "print(f'outlier pre-RMSE = {bad_rmse:.2f}')\n"
            "print(f'good-fit pre-RMSE = {pre_rmse:.2f}')\n"
            "print('No convex blend can match an out-of-hull unit — '\n"
            "      'the huge RMSE is the method telling you not to trust the gap.')\n"
            "assert bad_rmse > 3 * pre_rmse, \\\n"
            "    'an out-of-hull treated unit should fit far worse'"},
        {"md": "## 6 · Wrap-up & self-check\n\n"
            "- **Synthetic control** builds the counterfactual as a *convex blend* "
            "of donors (`w ≥ 0`, `Σw = 1`) that matches the treated unit's "
            "pre-period.\n"
            "- **Pre-treatment fit is the whole argument**: a small pre-period "
            "RMSE is what licenses reading the post-period gap as an effect — you "
            "recovered the injected truth here.\n"
            "- **Convex weights interpolate, never extrapolate**: an out-of-hull "
            "treated unit fits badly, and that failure is informative (Exercise "
            "5.2).\n"
            "- **Inference is a permutation rank**, not a standard error: pretend "
            "each donor was treated and locate the real unit in the placebo "
            "distribution.\n"
            "- **SC vs. DiD**: data-driven weights and enforced pre-period fit "
            "instead of equal weights and assumed parallel trends (Exercise "
            "4.1).\n\n"
            "**You're ready for Week 12** if you can solve for convex weights, "
            "explain why pre-treatment fit matters, and run an in-space placebo "
            "test from memory. Next week: **double / debiased machine learning** — "
            "Neyman-orthogonal scores and cross-fitting to plug ML into causal "
            "estimation."},
    ],
}
