# -*- coding: utf-8 -*-
"""Week 10 — Difference-in-Differences & Panel Methods."""

WEEK = {
    "number": 10,
    "slug": "difference_in_differences",
    "title": "Difference-in-Differences & Panel Methods",
    "block": "Block III — Quasi-experimental designs",
    "subtitle": "Let a comparison group subtract out everything that would have "
                "happened anyway.",
    "deliverable": "Problem Set 6 — parallel trends & staggered timing; "
                   "Lab 7 — difference-in-differences from a simulated panel.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), lab (2–3h).",
    "one_sentence": "Difference-in-differences compares the before/after change in "
        "a treated group to the before/after change in an untreated group, so any "
        "trend common to both — the counterfactual of 'what would have happened "
        "anyway' — cancels, leaving the causal effect under a parallel-trends "
        "assumption.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Compute a 2×2 difference-in-differences estimate by hand and explain why "
        "the second difference removes both fixed group gaps and the common time "
        "trend.",
        "State the parallel-trends identifying assumption precisely, and explain "
        "what a pre-trend test can and cannot tell you about it.",
        "Read an event-study plot: recognise flat pre-period leads as evidence "
        "for parallel trends and interpret the post-period lags as a dynamic "
        "effect.",
        "Explain why two-way fixed effects with staggered adoption and "
        "heterogeneous effects can be biased — the 'forbidden comparisons' and "
        "negative-weights problem.",
        "Estimate a clean group-time effect that avoids those comparisons, and "
        "justify clustering standard errors at the unit level.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Angrist & Pischke, Mostly Harmless Econometrics — Chapter 5.",
         "look_for": "the DiD identification assumption (parallel trends) and the "
                     "regression form that delivers the estimate as an "
                     "interaction coefficient."},
        {"text": "Roth, Sant'Anna, Bilinski & Poe (2023), 'What's Trending in "
                 "Difference-in-Differences?' — the DiD review.",
         "look_for": "why two-way fixed effects fails under staggered adoption "
                     "and heterogeneous effects, and what the modern estimators "
                     "do instead."},
    ],
    "optional_readings": [
        {"text": "Cunningham, The Mixtape — Difference-in-Differences & panel data.",
         "note": "An applied, code-first walk through Card & Krueger and the "
                 "staggered-timing problem."},
        {"text": "Callaway & Sant'Anna (2021), JoE — group-time average treatment "
                 "effects.",
         "note": "The reference for the ATT(g,t) building block you implement in "
                 "lab and the notebook."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "The 2×2 estimator: a difference of differences",
         "body": "Take two groups (treated, control) and two periods (before, "
            "after). The treated group's change over time mixes the treatment "
            "effect with whatever else happened. The control group's change "
            "measures that 'whatever else' alone. Subtract the second from the "
            "first and the common part cancels, leaving the effect. Algebraically "
            "DiD = (Ȳ_T,post − Ȳ_T,pre) − (Ȳ_C,post − Ȳ_C,pre): the first "
            "difference removes any fixed, time-invariant gap between the groups; "
            "the second difference removes the common time trend."},
        {"heading": "Parallel trends is the whole assumption",
         "body": "DiD does not assume the groups are identical. It assumes that, "
            "absent treatment, the treated group's outcome would have moved "
            "parallel to the control group's — same trend, possibly different "
            "level. That counterfactual trend is untestable by definition, but a "
            "pre-treatment pattern is a probe.",
         "bullets": [
            [("Levels can differ. ", {"bold": True}),
             ("A constant gap between groups is differenced away; only the "
              "trends must match.", {})],
            [("Pre-trends are a diagnostic, not a proof. ", {"bold": True}),
             ("Parallel pre-period paths make parallel post-period "
              "counterfactuals more credible — but the assumption is about the "
              "unobserved post-period, which no test can see.", {})],
            [("Functional form matters. ", {"bold": True}),
             ("Trends parallel in levels need not be parallel in logs. The "
              "assumption is scale-dependent; choose the scale deliberately.", {})],
         ]},
        {"heading": "Event-study plots as a diagnostic",
         "body": "Replace the single post×treat term with one coefficient per "
            "period relative to adoption (an omitted reference, usually the "
            "period just before treatment). Plotting these 'leads' and 'lags' "
            "gives the canonical DiD picture.",
         "bullets": [
            [("Leads (pre-period) ≈ 0 ", {"bold": True}),
             ("is the visual parallel-trends check: treated and control were on "
              "the same path before treatment.", {})],
            [("Lags (post-period) ", {"bold": True}),
             ("trace the dynamic effect — whether it jumps, ramps up, or "
              "fades.", {})],
            [("A sloping lead pattern ", {"bold": True}),
             ("is a red flag: the groups were already diverging, so the design's "
              "core assumption is in doubt.", {})],
         ]},
        {"heading": "TWFE and its staggered-adoption pitfalls",
         "body": "With many units and periods, people run y = unit FE + time FE + "
            "δ·treated_now + ε and read δ as 'the' effect. With a single "
            "adoption date this is exactly DiD. With STAGGERED adoption it is a "
            "weighted average of many 2×2 comparisons — and some of those use "
            "already-treated units as controls for the not-yet-treated.",
         "bullets": [
            [("Forbidden comparisons. ", {"bold": True}),
             ("When a late-adopting unit switches on, an early adopter that is "
              "already treated gets used as its 'control.' Its own evolving "
              "effect contaminates the comparison.", {})],
            [("Negative weights. ", {"bold": True}),
             ("Goodman-Bacon / de Chaisemartin–D'Haultfœuille show some 2×2 terms "
              "enter δ with negative weight, so δ can even have the wrong sign "
              "when effects are heterogeneous and dynamic.", {})],
            [("It is not a bug in the data. ", {"bold": True}),
             ("The bias is built into the estimator under heterogeneity; clean "
              "data with a known positive effect can still produce a biased "
              "(or sign-flipped) TWFE coefficient.", {})],
         ],
         "callout": {"title": "The modern fix in one line",
            "color": "RED",
            "lines": ["Estimate effects cohort-by-cohort and period-by-period — "
                      "ATT(g, t) — using only clean controls (never-treated or "
                      "not-yet-treated), then aggregate.",
                      "Callaway–Sant'Anna, Sun–Abraham, and "
                      "de Chaisemartin–D'Haultfœuille are different recipes for "
                      "this same idea."]}},
        {"heading": "Inference: cluster at the unit",
        "body": "Panel outcomes for the same unit are serially correlated across "
            "periods, and treatment is assigned at the unit level. Treating the "
            "unit-periods as independent badly understates the standard error. "
            "Cluster-robust standard errors at the unit (Bertrand, Duflo & "
            "Mullainathan 2004) fix this; with few clusters, lean on "
            "wild-cluster bootstrap or randomization inference instead.",
        },
    ],
    "problem_set": {
        "label": "Problem Set 6",
        "title": "Parallel trends & staggered timing",
        "intro": "Five problems on the logic of difference-in-differences: the "
            "2×2 arithmetic, what parallel trends does (and does not) assume, how "
            "to read an event study, why naive two-way fixed effects breaks under "
            "staggered adoption, and why we cluster. Try all five before you look "
            "at the solutions.",
        "problems": [
            {"title": "A 2×2 DiD by hand",
             "prompt": "A state raises its minimum wage; a neighbouring state does "
                "not. Average employment per restaurant is: treated state 20.0 "
                "before and 21.0 after; control state 22.0 before and 24.0 after. "
                "Compute the difference-in-differences estimate of the policy's "
                "effect on employment, and say in words what it means.",
             "solution_title": "DiD = −1.0 job per restaurant.",
             "solution": [
                "Treated change: 21.0 − 20.0 = +1.0. Control change: "
                "24.0 − 22.0 = +2.0.",
                "DiD = (treated change) − (control change) = 1.0 − 2.0 = −1.0. "
                "Employment grew in both states, but it grew 1.0 less where the "
                "wage rose.",
                "The control's +2.0 is the estimated 'what would have happened "
                "anyway' for the treated state; subtracting it nets out the "
                "common trend, leaving the −1.0 attributed to the policy (under "
                "parallel trends)."]},
            {"title": "What parallel trends actually assumes",
             "prompt": "A reviewer objects that DiD is invalid here because the "
                "treated and control regions had very different employment LEVELS "
                "before the policy. Separately, you ran a test showing the two "
                "regions moved in parallel for the five years before treatment "
                "and report it as 'proof that parallel trends holds.' Critique "
                "both statements.",
             "solution_title": "Different levels are fine; a passed pre-trend "
                "test is supportive evidence, not proof.",
             "solution": [
                "The reviewer is wrong: DiD differences away any fixed level gap. "
                "It requires only that the treated region's counterfactual trend "
                "would have matched the control's — equal levels are not needed.",
                "Your claim overstates the evidence. Parallel trends is a "
                "statement about the unobserved post-treatment counterfactual, "
                "which is fundamentally untestable.",
                "A flat pre-period makes the assumption more credible (and "
                "low-power tests can miss real violations), but matching trends "
                "before treatment never guarantees they would have continued to "
                "match after. Report it as a diagnostic, not a proof."]},
            {"title": "Reading an event-study plot",
             "prompt": "An event-study plot shows coefficients by period relative "
                "to adoption (reference = the period just before). The pre-period "
                "(negative) coefficients hover around zero with tight bands; the "
                "post-period (non-negative) coefficients start near zero, then "
                "rise to a plateau around +2.5. Interpret the leads and the lags. "
                "What would a downward-sloping set of pre-period coefficients have "
                "told you instead?",
             "solution_title": "Flat leads support parallel trends; rising lags "
                "are a dynamic effect that builds to ~2.5.",
             "solution": [
                "Leads near zero mean treated and control were on the same path "
                "before treatment — the visual parallel-trends check passes.",
                "Lags trace the effect over time: it is not instantaneous but "
                "ramps up and stabilises around +2.5, a dynamic treatment "
                "effect.",
                "Sloping (e.g. downward) pre-period coefficients would signal "
                "the groups were already diverging before treatment, "
                "undermining the design and suggesting the 'effect' partly "
                "reflects a pre-existing trend."]},
            {"title": "Why TWFE breaks under staggered adoption",
             "prompt": "Cohort A adopts a policy in 2010, cohort B in 2016; some "
                "units never adopt. You regress the outcome on unit fixed "
                "effects, year fixed effects, and a single 'currently treated' "
                "dummy. A colleague says the coefficient is 'the average effect.' "
                "Explain why it can be biased — even with no confounding — when "
                "treatment effects are heterogeneous and grow over time.",
             "solution_title": "TWFE averages many 2×2s, some with already-treated "
                "units as controls (forbidden comparisons) and negative weights.",
             "solution": [
                "The single coefficient is a weighted average of all possible "
                "2×2 DiDs. Some of them compare the newly treated cohort B "
                "against cohort A — which is ALREADY treated and whose effect is "
                "still evolving.",
                "Using an already-treated, dynamically-changing group as a "
                "'control' subtracts its growing effect, contaminating the "
                "comparison; Goodman-Bacon shows these terms can enter with "
                "negative weights.",
                "With heterogeneous, time-varying effects the negative weights "
                "can push the estimate far from the true average ATT — even to "
                "the wrong sign. The fix is to use only clean controls "
                "(never-treated or not-yet-treated) via a group-time estimator."]},
            {"title": "Why cluster standard errors at the unit",
             "prompt": "You have 50 states observed over 20 years and treat the "
                "1,000 state-years as independent observations when computing "
                "standard errors. Why is this inference likely to be wrong, and "
                "what is the standard fix?",
             "solution_title": "Serial correlation within states makes naive SEs "
                "far too small — cluster at the state (unit) level.",
             "solution": [
                "A state's outcomes are highly correlated across its own years "
                "(persistent shocks), so the 1,000 rows carry far less "
                "independent information than 1,000 truly independent draws.",
                "Treatment is assigned at the state level and tends to persist, "
                "which compounds the problem; naive standard errors can be "
                "several times too small, producing spurious significance "
                "(Bertrand, Duflo & Mullainathan 2004).",
                "Cluster-robust standard errors at the unit (state) level allow "
                "arbitrary within-state correlation. With few clusters, prefer a "
                "wild-cluster bootstrap or randomization inference."]},
        ],
    },
    "lab": {
        "label": "Lab 7",
        "title": "Difference-in-differences",
        "goal": "build a difference-in-differences analysis end-to-end on a "
            "simulated panel: the 2×2 estimate, the equivalent two-way "
            "fixed-effects regression with cluster-robust inference, an "
            "event-study plot, and a demonstration that naive TWFE is biased "
            "under staggered adoption — with a clean group-time fix. Pick R or "
            "Python.",
        "steps": [
            {"heading": "Step 1 · Simulate a panel with a known effect",
             "body": "Create units × periods with unit fixed effects, a common "
                "time trend, and a treatment effect switched on post-adoption for "
                "treated units. Because you build it, you know the true effect — "
                "your answer key.",
             "code_python": "import numpy as np, pandas as pd\n"
                "rng = np.random.default_rng(7)\n"
                "N, T, g, TRUE = 600, 2, 1, 3.0\n"
                "treated = (np.arange(N) < N//2).astype(int)\n"
                "ufe = rng.normal(0, 2, N)\n"
                "rows = []\n"
                "for i in range(N):\n"
                "    for t in range(T):\n"
                "        post = int(t >= g)\n"
                "        y = 5 + ufe[i] + 1.5*t + TRUE*treated[i]*post + rng.normal(0,1)\n"
                "        rows.append((i, t, treated[i], post, y))\n"
                "df = pd.DataFrame(rows, columns=['unit','time','treated','post','y'])",
             "code_r": 'library(fixest); library(data.table)\n'
                'set.seed(7)\n'
                'N <- 600; TRUE_ATT <- 3\n'
                'treated <- as.integer(seq_len(N) <= N/2)\n'
                'ufe <- rnorm(N, 0, 2)\n'
                'dt <- CJ(unit = 1:N, time = 0:1)\n'
                'dt[, treated := treated[unit]]\n'
                'dt[, post := as.integer(time >= 1)]\n'
                'dt[, y := 5 + ufe[unit] + 1.5*time + TRUE_ATT*treated*post + rnorm(.N)]'},
            {"heading": "Step 2 · The 2×2 difference-in-differences",
             "body": "Take the four group×period cell means and difference twice. "
                "It should land on the true effect.",
             "code_python": "m = df.groupby(['treated','post'])['y'].mean().unstack()\n"
                "did = (m.loc[1,1]-m.loc[1,0]) - (m.loc[0,1]-m.loc[0,0])\n"
                "print(f'2x2 DiD = {did:.3f}  (true {TRUE})')",
             "code_r": 'cells <- dcast(dt[, mean(y), by=.(treated, post)],\n'
                '                treated ~ post, value.var = "V1")\n'
                'did <- (cells[treated==1][["1"]] - cells[treated==1][["0"]]) -\n'
                '       (cells[treated==0][["1"]] - cells[treated==0][["0"]])\n'
                'print(did)'},
            {"heading": "Step 3 · TWFE regression with cluster-robust SEs",
             "body": "The interaction coefficient post×treat equals the 2×2 DiD. "
                "Fit unit and time fixed effects via dummies and cluster the "
                "standard errors at the unit.",
             "code_python": "import statsmodels.formula.api as smf\n"
                "fit = smf.ols('y ~ treated + post + treated:post', data=df).fit(\n"
                "    cov_type='cluster', cov_kwds={'groups': df['unit']})\n"
                "b = fit.params['treated:post']; se = fit.bse['treated:post']\n"
                "print(f'TWFE interaction = {b:.3f}  (SE {se:.3f}, clustered)')",
             "code_r": '# fixest absorbs unit & time FE; clusters by unit by default\n'
                'est <- feols(y ~ i(post, treated, ref = 0) | unit + time,\n'
                '             data = dt, cluster = ~unit)\n'
                'summary(est)'},
            {"heading": "Step 4 · An event-study plot",
             "body": "Rebuild the panel with several pre and post periods, then "
                "estimate one coefficient per event time (omit the period just "
                "before adoption). Plot leads and lags: flat leads support "
                "parallel trends, lags show the dynamic effect.",
             "code_python": "# leads near 0 = parallel pre-trends; lags = dynamic effect\n"
                "# (full runnable version is in the practice notebook, Section 4)\n"
                "import statsmodels.api as sm\n"
                "ev = [k for k in range(-g, T - g) if k != -1]\n"
                "# build treated x (event-time==k) dummies + unit & time dummies,\n"
                "# regress, then plot the event-time coefficients with 95% bands.",
             "code_r": 'es <- feols(y ~ i(time - g, treated, ref = -1) | unit + time,\n'
                '            data = dt_long, cluster = ~unit)\n'
                'iplot(es)   # leads ~ 0, lags trace the effect'},
            {"heading": "Step 5 · Staggered adoption: the bias and a fix",
             "body": "Give three cohorts different adoption dates and "
                "heterogeneous, growing effects. The naive 'currently treated' "
                "TWFE coefficient misses the true average ATT; a clean "
                "group-time estimate that uses only never-treated controls "
                "recovers it.",
             "code_python": "# naive TWFE on 'treated_now' is biased under staggered\n"
                "# adoption + heterogeneous dynamic effects. Compare it to a\n"
                "# Callaway-Sant'Anna-style ATT(g,t) built from clean 2x2s vs the\n"
                "# never-treated, then aggregate. Full code in notebook Section 5.\n"
                "print('naive TWFE != true ATT;  group-time average == true ATT')",
             "code_r": '# the did package implements Callaway-Sant\'Anna directly:\n'
                'library(did)\n'
                'cs <- att_gt(yname="y", tname="time", idname="unit",\n'
                '             gname="g", control_group="nevertreated", data=dt_stag)\n'
                'aggte(cs, type = "simple")   # recovers the true average ATT'},
        ],
        "expected": "The 2×2 DiD and the TWFE interaction coefficient agree and "
            "land near the true effect (3.0). The event-study leads sit near "
            "zero while the lags trace the dynamic effect. In the staggered "
            "design the naive TWFE coefficient is visibly off the true average "
            "ATT, while the clean group-time average recovers it.",
        "submit": [
            "Push your code and a short README reporting the 2×2 DiD, the TWFE "
            "coefficient and its clustered SE, and the naive-vs-clean numbers "
            "from the staggered design.",
            "Include your event-study figure (PNG) and one sentence on whether "
            "the leads support parallel trends.",
            "Paste the GitHub link to your week10 folder in the course LMS.",
        ],
    },
    "self_check": [
        "Compute a 2×2 DiD from four cell means and explain why the second "
        "difference removes the common trend.",
        "State parallel trends in one sentence and say why a passed pre-trend "
        "test is not a proof.",
        "Read an event-study plot: call the leads and the lags correctly.",
        "Explain, with the forbidden-comparison idea, why naive TWFE can be "
        "biased under staggered adoption.",
        "Say why standard errors are clustered at the unit and what goes wrong "
        "if they are not.",
    ],
    "next_week": {
        "heading": "Coming up: Week 11 — Synthetic control",
        "teaser": "When you have one treated unit and many potential controls, "
            "difference-in-differences with a single comparison group is shaky. "
            "Synthetic control builds a weighted combination of control units "
            "that tracks the treated unit's pre-treatment path, then reads the "
            "post-treatment gap as the effect. We'll construct one from scratch "
            "and discuss inference by placebo. Skim Abadie (2021) to get a head "
            "start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 10", "items": [
            {"t": "The 2×2 estimator", "d": "A difference of differences cancels "
             "the common trend."},
            {"t": "Parallel trends", "d": "The one assumption — and what it does "
             "and doesn't require."},
            {"t": "Event-study plots", "d": "Leads as a diagnostic, lags as the "
             "dynamic effect."},
            {"t": "Two-way fixed effects", "d": "The regression form, and where it "
             "breaks."},
            {"t": "Staggered adoption", "d": "Forbidden comparisons, negative "
             "weights, modern fixes."},
            {"t": "Case + inference", "d": "Card & Krueger, and why we cluster "
             "standard errors."},
        ]},
        {"type": "content", "kicker": "The idea",
         "title": "Subtract out what would have happened anyway", "bullets": [
            "A treated group's before/after change mixes the treatment effect "
            "with everything else that moved.",
            "A comparison group's before/after change measures that 'everything "
            "else' on its own.",
            ("Difference-in-differences = (treated change) − (control change).", 0),
            ("The common part cancels; the effect remains.", 1),
            "Where it shines: a policy hits some units at some time, and you have "
            "untreated units to compare against.",
         ],
         "note": {"title": "One-liner",
            "body": "Let a comparison group subtract out the counterfactual trend "
            "for you."}},
        {"type": "content", "kicker": "Where it comes from",
         "title": "A classic: Card & Krueger and the minimum wage", "bullets": [
            "1992: New Jersey raised its minimum wage; neighbouring Pennsylvania "
            "did not.",
            "Simple theory predicted job losses where the wage rose.",
            "Comparing the employment CHANGE in NJ fast-food restaurants to the "
            "change in PA found no relative drop.",
            "The control state nets out region-wide trends — the heart of the DiD "
            "design.",
         ],
         "note": {"title": "Why it mattered",
            "body": "A credible quasi-experiment reshaped a textbook debate — and "
            "made DiD famous."}},
        {"type": "table", "kicker": "Card & Krueger (1994), stylised",
         "title": "The minimum-wage DiD in numbers",
         "headers": ["State", "Before (FTE)", "After (FTE)", "Change"],
         "rows": [
            ["New Jersey (wage ↑)", "20.4", "21.0", "+0.6"],
            ["Pennsylvania (control)", "23.3", "21.2", "−2.1"],
            ["DiD (NJ − PA)", "—", "—", "+2.7"],
         ],
         "note": {"title": "Read it",
            "body": "Employment fell in the control state; relative to that "
            "trend, the wage rise did not cost jobs — it nudged them up."}},

        {"type": "section", "kicker": "Part 1", "title": "The 2×2 estimator",
         "subtitle": "Two groups, two periods, and two differences that strip away "
            "everything except the effect."},
        {"type": "table", "kicker": "The four cells",
         "title": "Difference twice", "headers":
            ["Group", "Before", "After", "Change (After − Before)"],
         "rows": [
            ["Treated", "Ȳ_T,pre", "Ȳ_T,post", "ΔT"],
            ["Control", "Ȳ_C,pre", "Ȳ_C,post", "ΔC"],
            ["DiD", "—", "—", "ΔT − ΔC"],
         ],
         "note": {"title": "Read it",
            "body": "First difference (over time) kills the fixed group gap; the "
            "second difference (across groups) kills the common time trend."}},
        {"type": "content", "kicker": "What each difference removes",
         "title": "Two nuisances, two differences", "bullets": [
            "Fixed group gap: treated and control may differ in LEVEL for all "
            "time — differenced away by the over-time change.",
            "Common time trend: anything that moves both groups together — "
            "differenced away by comparing the two changes.",
            "What survives both is the part that hit only the treated group only "
            "after treatment.",
            ("That surviving part is the DiD estimate of the effect.", 1),
         ],
         "note": {"title": "Equivalently",
            "body": "DiD is the post×treat interaction coefficient in a "
            "regression — same number, more machinery."}},
        {"type": "statement",
         "quote": "DiD doesn't need the groups to be the same — only their trends.",
         "attribution": "A constant gap between treated and control is harmless; "
            "it cancels in the first difference. All the identifying weight rests "
            "on the trends, not the levels."},

        {"type": "section", "kicker": "Part 2", "title": "Parallel trends",
         "subtitle": "The single identifying assumption — what it claims, and why "
            "no test can confirm it."},
        {"type": "content", "kicker": "The assumption",
         "title": "Absent treatment, the trends would have matched", "bullets": [
            "Parallel trends: the treated group's counterfactual (untreated) "
            "trend equals the control group's observed trend.",
            "It licenses using ΔC as the treated group's 'what would have "
            "happened anyway.'",
            "It is about an UNOBSERVED counterfactual — so it cannot be verified "
            "directly.",
            "It is scale-dependent: parallel in levels need not mean parallel in "
            "logs. Choose the scale deliberately.",
         ],
         "note": {"title": "Not assumed",
            "body": "Equal levels, equal variances, or identical units. Only the "
            "trends must line up."}},
        {"type": "compare", "kicker": "A common confusion",
         "title": "What parallel trends does and does not require", "columns": [
            {"head": "Required", "points": [
                "Equal counterfactual TRENDS.",
                "A credible untreated comparison group.",
                "A deliberate choice of scale (levels vs logs).",
                "No treatment-driven composition change."]},
            {"head": "NOT required", "points": [
                "Equal pre-treatment LEVELS.",
                "Randomized treatment assignment.",
                "Identical groups in every respect.",
                "Balance on every covariate."]},
        ]},
        {"type": "content", "kicker": "The probe",
         "title": "Pre-trend tests: useful, not decisive", "bullets": [
            "If treated and control moved in parallel BEFORE treatment, the "
            "post-period assumption is more believable.",
            "But the assumption concerns the post-period counterfactual, which a "
            "pre-trend test never observes.",
            "Tests can be low-powered: a flat pre-period can hide a real "
            "violation.",
            "And conditioning the analysis on passing the test distorts the "
            "subsequent inference.",
         ],
         "note": {"title": "Report it as",
            "body": "Supportive diagnostic evidence — never as 'proof that "
            "parallel trends holds.'"}},

        {"type": "section", "kicker": "Part 3", "title": "Event-study plots",
         "subtitle": "One coefficient per period relative to adoption — the "
            "canonical DiD diagnostic in a single picture."},
        {"type": "content", "kicker": "The construction",
         "title": "Leads and lags around adoption", "bullets": [
            "Replace the single post×treat term with one term per event time "
            "(periods since/until adoption).",
            "Omit one reference period — usually the period just before treatment "
            "— so the rest are read relative to it.",
            "Negative event times are 'leads' (pre-treatment); non-negative are "
            "'lags' (post-treatment).",
            "Plot the coefficients with confidence bands against event time.",
         ],
         "note": {"title": "Reference period",
            "body": "Every coefficient is a contrast against the omitted period "
            "(t = −1). The reference is mechanically zero."}},
        {"type": "compare", "kicker": "How to read it",
         "title": "Leads diagnose, lags describe", "columns": [
            {"head": "Leads ≈ 0 (pre-period)", "points": [
                "Treated & control on the same path before treatment.",
                "The visual parallel-trends check.",
                "Flat, tight bands = reassuring."]},
            {"head": "Lags (post-period)", "points": [
                "Trace the effect over time.",
                "Jump, ramp-up, or fade-out.",
                "This is the dynamic treatment effect."]},
            {"head": "Sloping leads = trouble", "points": [
                "Groups already diverging pre-treatment.",
                "Parallel trends in doubt.",
                "Effect may be a pre-existing trend."]},
        ]},
        {"type": "statement",
         "quote": "Flat leads, then rising lags: the picture every DiD paper hopes "
            "to show.",
         "attribution": "The pre-period is your evidence the design is credible; "
            "the post-period is your story about how the effect unfolds. One plot "
            "carries both."},

        {"type": "section", "kicker": "Part 4", "title": "Two-way fixed effects",
         "subtitle": "The workhorse regression — and the staggered-adoption trap "
            "hiding inside it."},
        {"type": "content", "kicker": "The regression",
         "title": "Unit FE + time FE + a treatment dummy", "bullets": [
            "Fit y = αᵢ (unit FE) + λₜ (time FE) + δ·treated_now + ε.",
            "Unit FE absorb fixed level differences; time FE absorb the common "
            "trend — exactly the two nuisances DiD removes.",
            "With ONE adoption date, δ is precisely the 2×2 DiD. Clean and "
            "intuitive.",
            "The trouble starts when different units adopt at different times.",
         ],
         "note": {"title": "Single-date case",
            "body": "Two-way fixed effects = difference-in-differences. The "
            "machinery and the 2×2 agree."}},
        {"type": "content", "kicker": "What δ really is",
         "title": "A weighted average of many 2×2 comparisons", "bullets": [
            "Under staggered adoption, δ is a weighted blend of every possible "
            "2×2 DiD in the data.",
            "Some compare newly-treated units to not-yet-treated ones — fine.",
            "Others compare newly-treated units to ALREADY-treated ones — the "
            "forbidden comparisons.",
            "An already-treated 'control' whose own effect is still evolving "
            "contaminates the contrast.",
         ],
         "note": {"title": "Goodman-Bacon",
            "body": "The decomposition that names each 2×2 and its weight — "
            "including the bad ones."}},
        {"type": "compare", "kicker": "The pitfall, sharpened",
         "title": "Why TWFE can mislead under staggering", "columns": [
            {"head": "Forbidden comparisons", "points": [
                "Already-treated units used as controls.",
                "Their evolving effect leaks in.",
                "Worst with dynamic effects."]},
            {"head": "Negative weights", "points": [
                "Some 2×2 terms enter with negative sign.",
                "δ can land outside the range of true effects.",
                "Even the SIGN can flip."]},
            {"head": "Not a data bug", "points": [
                "Clean data, known positive effect.",
                "Bias is built into the estimator.",
                "Heterogeneity + dynamics trigger it."]},
        ]},
        {"type": "statement",
         "quote": "With staggered timing and heterogeneous effects, the TWFE "
            "coefficient can have the wrong sign.",
         "attribution": "It is not noise and it is not confounding — the negative "
            "weights are baked into the estimator. This is the result that "
            "launched the modern DiD literature."},

        {"type": "section", "kicker": "Part 5", "title": "Modern DiD estimators",
         "subtitle": "Estimate clean cohort-by-period effects, then aggregate — "
            "never let an already-treated unit be a control."},
        {"type": "content", "kicker": "The building block",
         "title": "Group-time effects ATT(g, t)", "bullets": [
            "For each adoption cohort g and each period t, estimate the effect "
            "ATT(g, t) on that cohort in that period.",
            "Use only CLEAN controls: never-treated units, or units not-yet-"
            "treated by period t.",
            "Each ATT(g, t) is a clean 2×2 DiD — no forbidden comparison.",
            "Aggregate the ATT(g, t) into an overall, an event-study, or a "
            "cohort-specific summary.",
         ],
         "note": {"title": "Callaway–Sant'Anna",
            "body": "The canonical recipe for ATT(g, t) and its aggregations. "
            "What you implement in lab."}},
        {"type": "table", "kicker": "Same idea, different recipes",
         "title": "The modern DiD toolkit", "headers":
            ["Estimator", "Core idea", "Software"],
         "rows": [
            ["Callaway–Sant'Anna", "ATT(g,t) vs clean controls, then aggregate",
             "R: did · py: differences"],
            ["Sun–Abraham", "Saturated event-study, interaction-weighted",
             "R: fixest sunab()"],
            ["de Chaisemartin–D'Haultfœuille", "Effects on switchers, no bad 2×2s",
             "R: DIDmultiplegt"],
            ["Borusyak et al.", "Impute the untreated counterfactual",
             "R: didimputation"],
         ],
         "note": {"title": "Shared principle",
            "body": "Build clean cohort×period comparisons, then aggregate — "
            "they differ mainly in the controls and the weighting."}},
        {"type": "steps", "kicker": "Your workflow",
         "title": "Doing staggered DiD safely", "steps": [
            {"title": "Define cohorts", "body": "— group units by adoption "
             "period g (never-treated as the clean control)."},
            {"title": "Estimate ATT(g,t)", "body": "— a clean 2×2 for each cohort "
             "and period against valid controls."},
            {"title": "Aggregate", "body": "— overall, by event time, or by "
             "cohort, with the right weights."},
            {"title": "Plot & test", "body": "— event-study from the ATT(g,t); "
             "inspect leads for pre-trends."},
        ],
         "note": "Same DiD logic — just refuse the forbidden comparisons."},

        {"type": "section", "kicker": "Part 6", "title": "Inference",
         "subtitle": "Panel data are serially correlated; naive standard errors "
            "are badly too small."},
        {"type": "content", "kicker": "The problem",
         "title": "Why naive standard errors lie", "bullets": [
            "A unit's outcomes are correlated across its own periods — persistent "
            "shocks, not fresh draws.",
            "So 1,000 unit-periods carry far less information than 1,000 "
            "independent observations.",
            "Treatment is assigned at the unit level and persists, compounding "
            "the dependence.",
            "Result: naive SEs can be several times too small — spurious "
            "significance (Bertrand, Duflo & Mullainathan 2004).",
         ],
         "note": {"title": "The symptom",
            "body": "Implausibly tight confidence intervals and t-stats that are "
            "too good to be true."}},
        {"type": "compare", "kicker": "The fix",
         "title": "Cluster — and what to do with few clusters", "columns": [
            {"head": "Many clusters", "points": [
                "Cluster-robust SEs at the unit.",
                "Allows arbitrary within-unit correlation.",
                "The default for panel DiD."]},
            {"head": "Few clusters", "points": [
                "Cluster-robust SEs become unreliable.",
                "Wild-cluster bootstrap.",
                "Randomization / permutation inference."]},
        ]},
        {"type": "content", "kicker": "The five traps",
         "title": "Where DiD studies go wrong", "bullets": [
            "Assuming equal LEVELS instead of equal trends — a non-issue dressed "
            "up as a fatal flaw.",
            "Calling a passed pre-trend test 'proof' of parallel trends.",
            "Reading naive TWFE as 'the effect' under staggered adoption.",
            "Ignoring scale — trends parallel in levels need not be parallel in "
            "logs.",
            "Forgetting to cluster, and reporting standard errors that are far "
            "too small.",
         ],
         "note": {"title": "Antidote",
            "body": "An event-study plot, a group-time estimator, and "
            "cluster-robust SEs handle four of the five."}},

        {"type": "section", "kicker": "Part 7", "title": "Putting it together",
         "subtitle": "From a single 2×2 to a defensible staggered-adoption study."},
        {"type": "steps", "kicker": "The DiD checklist",
         "title": "What a credible DiD study reports", "steps": [
            {"title": "Design", "body": "— who is treated, when, and which "
             "untreated group is the comparison."},
            {"title": "Parallel trends", "body": "— argue it, then show an "
             "event-study with flat leads."},
            {"title": "Estimator", "body": "— 2×2/TWFE for a single date; a "
             "group-time method if staggered."},
            {"title": "Inference", "body": "— cluster at the unit; bootstrap with "
             "few clusters."},
            {"title": "Robustness", "body": "— scale (levels vs logs), "
             "alternative controls, placebo dates."},
        ],
         "note": "Same five-step causal workflow — specialised to panels."},
        {"type": "content", "kicker": "Takeaways",
         "title": "What to carry into the lab", "bullets": [
            "DiD lets a comparison group subtract out the counterfactual trend.",
            "Parallel trends is the whole assumption — untestable, but probed by "
            "an event study.",
            "Naive TWFE is fine for one adoption date and dangerous under "
            "staggered adoption with heterogeneity.",
            "Use clean group-time comparisons, and cluster your standard errors "
            "at the unit.",
         ],
         "note": {"title": "Next week",
            "body": "One treated unit, many controls — synthetic control builds a "
            "bespoke comparison."}},
        {"type": "statement",
         "quote": "Difference away what would have happened anyway — but only "
            "compare units you are allowed to compare.",
         "attribution": "This week: recover a known effect with a 2×2 and a TWFE "
            "regression, read an event study, and watch naive TWFE break under "
            "staggered adoption — then fix it. See you in the lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A panel with a known effect\n\n"
            "Difference-in-differences would be untestable in the wild — we never "
            "see the treated group's untreated counterfactual. So we **simulate** "
            "a panel where we control everything: unit fixed effects (some units "
            "are just higher), a common time trend (everything drifts up "
            "together), and a treatment effect we **switch on** for treated units "
            "in the post period. Because we built it, we know the true effect — "
            "our answer key for the whole notebook."},
        {"code": "import statsmodels.api as sm\n"
            "import statsmodels.formula.api as smf\n\n"
            "N, TRUE_ATT = 600, 3.0            # units, and the known effect\n"
            "treated = (np.arange(N) < N // 2).astype(int)   # half are treated\n"
            "unit_fe = RNG.normal(0, 2, N)     # fixed, time-invariant unit levels\n"
            "time_fe = {0: 0.0, 1: 1.5}        # common trend: both groups drift up\n\n"
            "rows = []\n"
            "for i in range(N):\n"
            "    for t in (0, 1):              # t=0 pre, t=1 post\n"
            "        post = t\n"
            "        y = (5 + unit_fe[i] + time_fe[t]\n"
            "             + TRUE_ATT * treated[i] * post      # effect only when treated AND post\n"
            "             + RNG.normal(0, 1))\n"
            "        rows.append((i, t, treated[i], post, y))\n"
            "panel = pd.DataFrame(rows, columns=['unit','time','treated','post','y'])\n"
            "print(panel.head())\n"
            "print(f'\\nTrue effect built into the treated post cells: {TRUE_ATT}')"},
        {"md": "Note the structure: treated and control start at **different "
            "levels** (unit fixed effects differ) and both move up by the same "
            "common trend. Only the treated-and-post cells get the extra "
            "`TRUE_ATT`. That is exactly the world DiD is designed for."},
        {"md": "## 2 · The 2×2 estimator recovers the effect\n\n"
            "Take the four group×period **cell means** and difference twice. The "
            "first difference (after − before, within a group) removes that "
            "group's fixed level. The second difference (treated − control) "
            "removes the common time trend. What's left is the effect."},
        {"code": "cell = panel.groupby(['treated','post'])['y'].mean().unstack()\n"
            "print('Cell means (rows=treated, cols=post):')\n"
            "print(cell, '\\n')\n\n"
            "d_treated = cell.loc[1, 1] - cell.loc[1, 0]   # treated change over time\n"
            "d_control = cell.loc[0, 1] - cell.loc[0, 0]   # control change over time\n"
            "did = d_treated - d_control\n"
            "print(f'treated change = {d_treated:.3f}')\n"
            "print(f'control change = {d_control:.3f}   (= the common trend)')\n"
            "print(f'2x2 DiD        = {did:.3f}   (true {TRUE_ATT})')\n"
            "assert abs(did - TRUE_ATT) < 0.3, 'the 2x2 DiD should recover the effect'"},
        {"md": "The control group's change (~1.5) is our estimate of *what would "
            "have happened to the treated group anyway*. Subtracting it from the "
            "treated change leaves the effect — about 3.0. The different starting "
            "levels never mattered; they cancelled in the first difference."},
        {"md": "## 3 · The same number from a TWFE regression\n\n"
            "DiD is equivalently the **interaction coefficient** `treated:post` in "
            "a regression. With unit and time fixed effects (here, in the 2-period "
            "case, the `treated` and `post` main effects play that role), the "
            "`treated:post` term is the difference-in-differences. We also attach "
            "**cluster-robust standard errors at the unit level** — the right "
            "inference for panel data."},
        {"code": "fit = smf.ols('y ~ treated + post + treated:post', data=panel).fit(\n"
            "    cov_type='cluster', cov_kwds={'groups': panel['unit']})\n"
            "b  = fit.params['treated:post']\n"
            "se = fit.bse['treated:post']\n"
            "print(f'TWFE interaction = {b:.3f}   (true {TRUE_ATT})')\n"
            "print(f'cluster-robust SE = {se:.3f}   (clustered by unit)')\n"
            "assert abs(b - did) < 1e-8, 'the interaction coef IS the 2x2 DiD'\n"
            "assert abs(b - TRUE_ATT) < 0.3, 'TWFE should recover the effect'"},
        {"md": "The interaction coefficient is **numerically identical** to the "
            "hand-computed 2×2 DiD — the regression is just a convenient way to "
            "get the same number plus a standard error. Clustering by unit allows "
            "a unit's periods to be correlated; ignoring that would make the SE "
            "too small."},
        {"md": "### 🔧 Exercise 3.1 — break parallel trends, break DiD\n\n"
            "DiD is only as good as parallel trends. Re-simulate the panel but "
            "give the **treated** group an extra upward drift in the post period "
            "that has *nothing to do with treatment* (a differential trend). The "
            "true treatment effect is still `3.0`, but DiD will now **overstate** "
            "it, because it credits the differential trend to the treatment.\n\n"
            "Fill in the `# TODO`s: add a `bad_trend` only to treated-and-post "
            "cells, then recompute the 2×2 DiD."},
        {"code": "# TODO: rebuild the panel with a differential (non-parallel) trend.\n"
            "BAD = 2.0   # extra treated-only post drift, NOT a treatment effect\n"
            "rows_bad = []\n"
            "for i in range(N):\n"
            "    for t in (0, 1):\n"
            "        bad_trend = 0.0   # TODO: = BAD only when treated[i]==1 and t==1, else 0\n"
            "        y = (5 + unit_fe[i] + time_fe[t]\n"
            "             + TRUE_ATT * treated[i] * t\n"
            "             + bad_trend + RNG.normal(0, 1))\n"
            "        rows_bad.append((i, t, treated[i], t, y))\n"
            "# bad = pd.DataFrame(rows_bad, columns=['unit','time','treated','post','y'])\n"
            "# ... then compute the 2x2 DiD on `bad` and compare to TRUE_ATT\n"
            "print('fill in bad_trend, then compute the DiD (see the solution cell)')"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "BAD = 2.0\n"
            "rows_bad = []\n"
            "for i in range(N):\n"
            "    for t in (0, 1):\n"
            "        bad_trend = BAD if (treated[i] == 1 and t == 1) else 0.0\n"
            "        y = (5 + unit_fe[i] + time_fe[t]\n"
            "             + TRUE_ATT * treated[i] * t\n"
            "             + bad_trend + RNG.normal(0, 1))\n"
            "        rows_bad.append((i, t, treated[i], t, y))\n"
            "bad = pd.DataFrame(rows_bad, columns=['unit','time','treated','post','y'])\n\n"
            "cb = bad.groupby(['treated','post'])['y'].mean().unstack()\n"
            "did_bad = (cb.loc[1,1]-cb.loc[1,0]) - (cb.loc[0,1]-cb.loc[0,0])\n"
            "print(f'DiD under broken parallel trends = {did_bad:.3f}  (true {TRUE_ATT})')\n"
            "print(f'overstatement = {did_bad - TRUE_ATT:+.3f}  (≈ the differential trend, {BAD})')\n"
            "assert did_bad - TRUE_ATT > 1.0, 'broken parallel trends should bias DiD upward'"},
        {"md": "The estimate is now ~5 instead of 3: DiD blamed the treatment for "
            "a trend the treated group would have had anyway. **No amount of data "
            "fixes this** — it is an identification failure, not noise. That is "
            "why we probe parallel trends with an event study next."},
        {"md": "## 4 · Event-study: leads diagnose, lags describe\n\n"
            "With several pre- and post-periods we can estimate **one coefficient "
            "per period relative to adoption**, omitting the period just before "
            "treatment (`t = −1`) as the reference. The pre-period 'leads' should "
            "sit near zero (parallel trends); the post-period 'lags' trace the "
            "**dynamic** effect — here it ramps up and plateaus."},
        {"code": "# A richer panel: 8 periods, treated units adopt at g=4, dynamic effect.\n"
            "Tn, g, PEAK = 8, 4, 2.5\n"
            "u_fe = RNG.normal(0, 2, N)\n"
            "t_fe = np.linspace(0, 3, Tn)          # common trend, identical for both groups\n"
            "rows_es = []\n"
            "for i in range(N):\n"
            "    for t in range(Tn):\n"
            "        if treated[i] == 1 and t >= g:\n"
            "            eff = PEAK * min(1.0, 0.5 * (t - g + 1))   # ramps 1.25→2.5→plateau\n"
            "        else:\n"
            "            eff = 0.0\n"
            "        y = 5 + u_fe[i] + t_fe[t] + eff + RNG.normal(0, 1)\n"
            "        rows_es.append((i, t, treated[i], y))\n"
            "es = pd.DataFrame(rows_es, columns=['unit','time','treated','y'])\n"
            "es['evt'] = es['time'] - g            # event time (0 = adoption period)\n"
            "print(es.head())"},
        {"code": "def event_study(d):\n"
            "    \"\"\"OLS event-study: treated×(event-time==k) dummies + unit & time FE.\n"
            "    Omits k=-1 as the reference. Returns {event_time: (coef, se)}.\"\"\"\n"
            "    levels = [k for k in range(int(d['evt'].min()), int(d['evt'].max()) + 1)\n"
            "              if k != -1]\n"
            "    dummies = {f'ev{k:+d}': ((d['treated'] == 1) & (d['evt'] == k)).astype(float).values\n"
            "               for k in levels}\n"
            "    unit_d = pd.get_dummies(d['unit'], prefix='u', drop_first=True).astype(float)\n"
            "    time_d = pd.get_dummies(d['time'], prefix='t', drop_first=True).astype(float)\n"
            "    X = sm.add_constant(pd.concat(\n"
            "        [pd.DataFrame(dummies, index=d.index), unit_d, time_d], axis=1))\n"
            "    m = sm.OLS(d['y'].values, X.values).fit(\n"
            "        cov_type='cluster', cov_kwds={'groups': d['unit'].values})\n"
            "    coef = dict(zip(X.columns, m.params)); se = dict(zip(X.columns, m.bse))\n"
            "    return {k: (coef[f'ev{k:+d}'], se[f'ev{k:+d}']) for k in levels}\n\n"
            "pts = event_study(es)\n"
            "for k in sorted(pts):\n"
            "    c, s = pts[k]\n"
            "    print(f'event time {k:+d}:  coef {c:+.3f}  (SE {s:.3f})')"},
        {"code": "# Plot the event study: leads (k<0) near 0, lags (k>=0) trace the effect.\n"
            "ks  = sorted(pts)\n"
            "bs  = np.array([pts[k][0] for k in ks])\n"
            "ses = np.array([pts[k][1] for k in ks])\n\n"
            "fig, ax = plt.subplots()\n"
            "ax.errorbar(ks, bs, yerr=1.96 * ses, marker='o', capsize=3, color='#4C72B0')\n"
            "ax.axhline(0, color='grey', lw=1)\n"
            "ax.axvline(-0.5, color='crimson', ls='--', lw=1, label='adoption')\n"
            "ax.set_xlabel('event time (periods relative to adoption)')\n"
            "ax.set_ylabel('coefficient (vs t = -1)')\n"
            "ax.set_title('Event study: flat leads, rising lags'); ax.legend()\n"
            "None  # figure created; no blocking show()\n\n"
            "leads = np.array([pts[k][0] for k in ks if k < 0])\n"
            "print(f'max |lead| = {np.abs(leads).max():.3f}  (≈0 ⇒ parallel pre-trends)')\n"
            "assert np.abs(leads).max() < 0.4, 'pre-period leads should be ~0'"},
        {"md": "The leads hug zero — the visual parallel-trends check passes — and "
            "the lags climb from ~1.25 to ~2.5 and flatten, exactly the dynamic "
            "effect we built in. This single plot is both the diagnostic and the "
            "story of how the effect unfolds."},
        {"md": "### 🔧 Exercise 4.1 — make the pre-trends fail\n\n"
            "Add a treated-group drift that starts *before* adoption (a "
            "differential pre-trend). Re-run `event_study` and confirm the "
            "**leads are no longer flat** — the plot now warns you that the design "
            "is shaky.\n\n"
            "Fill in the `# TODO`: add `0.6 * es['evt']` worth of drift to treated "
            "units for *all* periods (so it bends the pre-period too)."},
        {"code": "# TODO: build a panel where treated units drift with event time everywhere.\n"
            "es_bad = es.copy()\n"
            "drift = ...   # TODO: 0.6 * es_bad['evt'] when treated==1, else 0\n"
            "# es_bad['y'] = es_bad['y'] + drift\n"
            "# pts_bad = event_study(es_bad)\n"
            "# leads_bad = [pts_bad[k][0] for k in pts_bad if k < 0]\n"
            "# print('pre-period leads:', [round(v,2) for v in leads_bad])\n"
            "print('fill in the drift and re-run the event study')"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "es_bad = es.copy()\n"
            "drift = np.where(es_bad['treated'] == 1, 0.6 * es_bad['evt'], 0.0)\n"
            "es_bad['y'] = es_bad['y'] + drift\n"
            "pts_bad = event_study(es_bad)\n"
            "leads_bad = np.array([pts_bad[k][0] for k in sorted(pts_bad) if k < 0])\n"
            "print('pre-period leads (should NOT be flat):',\n"
            "      [round(v, 2) for v in leads_bad])\n"
            "print(f'max |lead| now = {np.abs(leads_bad).max():.3f}  (was ~0)')\n"
            "assert np.abs(leads_bad).max() > 0.5, 'a differential pre-trend should bend the leads'"},
        {"md": "Now the leads slope away from zero: the event-study plot is "
            "*screaming* that treated and control were already diverging before "
            "treatment. This is exactly the red flag the diagnostic exists to "
            "raise — you would not trust a DiD effect read off this design."},
        {"md": "## 5 · Staggered adoption: TWFE breaks, group-time fixes it\n\n"
            "Now the hard case. Three cohorts adopt at **different times** with "
            "**heterogeneous, growing** effects: an early cohort with a big effect, "
            "a late cohort with a small one, and a never-treated group. The naive "
            "'currently treated' TWFE coefficient uses already-treated early "
            "adopters as 'controls' for the late adopters (forbidden comparisons) "
            "and gets the wrong answer. A clean **group-time** estimate "
            "(Callaway–Sant'Anna style) that compares each cohort only to the "
            "never-treated recovers the truth."},
        {"code": "# Three cohorts: early (g=3, big effect), late (g=8, small), never-treated.\n"
            "Tn = 12\n"
            "Np = 150\n"
            "g_of, ufe2 = {}, {}\n"
            "uid = 0\n"
            "for cohort_g in (3, 8, np.inf):           # inf = never treated\n"
            "    for _ in range(Np):\n"
            "        g_of[uid] = cohort_g\n"
            "        ufe2[uid] = RNG.normal(0, 2)\n"
            "        uid += 1\n"
            "Nstag = uid\n"
            "t_fe2 = np.linspace(0, 4, Tn)             # common trend\n\n"
            "def true_effect(i, t):\n"
            "    g = g_of[i]\n"
            "    if t < g:\n"
            "        return 0.0\n"
            "    base = {3: 4.0, 8: 1.0}[g]            # heterogeneous size by cohort\n"
            "    return base * (1.0 + 0.15 * (t - g))  # grows with time since adoption\n\n"
            "rows_s = []\n"
            "for i in range(Nstag):\n"
            "    for t in range(Tn):\n"
            "        y = 5 + ufe2[i] + t_fe2[t] + true_effect(i, t) + RNG.normal(0, 1)\n"
            "        rows_s.append((i, t, g_of[i], y))\n"
            "stag = pd.DataFrame(rows_s, columns=['unit','time','g','y'])\n"
            "stag['treated_now'] = (stag['time'] >= stag['g']).astype(float)\n"
            "print(stag.head())"},
        {"code": "# The TRUE answer: average effect over all actually-treated unit-periods.\n"
            "treated_cells = stag[stag['time'] >= stag['g']]\n"
            "TRUE_AVG_ATT = np.mean([true_effect(r.unit, r.time)\n"
            "                        for r in treated_cells.itertuples()])\n"
            "print(f'TRUE average ATT over treated cells = {TRUE_AVG_ATT:.3f}')\n\n"
            "# --- Naive TWFE: y ~ treated_now + unit FE + time FE (cluster by unit) ---\n"
            "unit_d = pd.get_dummies(stag['unit'], prefix='u', drop_first=True).astype(float)\n"
            "time_d = pd.get_dummies(stag['time'], prefix='t', drop_first=True).astype(float)\n"
            "X = sm.add_constant(pd.concat(\n"
            "    [stag[['treated_now']].reset_index(drop=True), unit_d, time_d], axis=1))\n"
            "mtwfe = sm.OLS(stag['y'].values, X.values).fit(\n"
            "    cov_type='cluster', cov_kwds={'groups': stag['unit'].values})\n"
            "twfe = mtwfe.params[list(X.columns).index('treated_now')]\n"
            "print(f'Naive TWFE coefficient = {twfe:.3f}')\n"
            "print(f'TWFE bias = {twfe - TRUE_AVG_ATT:+.3f}   (it misses the truth!)')\n"
            "assert abs(twfe - TRUE_AVG_ATT) > 0.5, 'naive TWFE should be visibly biased here'"},
        {"md": "The naive TWFE coefficient is well **below** the true average ATT. "
            "The culprit: when the late cohort switches on, the early cohort is "
            "already treated and its effect is still *growing* — using it as a "
            "'control' subtracts that growth, dragging the estimate down (the "
            "negative-weights / forbidden-comparison problem). Now the clean fix."},
        {"code": "# --- Clean group-time ATT(g,t): each cohort vs the NEVER-TREATED only. ---\n"
            "# For cohort g and post period t>=g, baseline is the period just before (g-1):\n"
            "#   ATT(g,t) = [ȳ_g(t) - ȳ_g(g-1)] - [ȳ_never(t) - ȳ_never(g-1)]\n"
            "ybar_never = stag[~np.isfinite(stag['g'])].groupby('time')['y'].mean()\n\n"
            "att_gt, weights = [], []\n"
            "for g in (3, 8):\n"
            "    cohort = stag[stag['g'] == g]\n"
            "    ybar_g = cohort.groupby('time')['y'].mean()\n"
            "    base = g - 1                       # last clean pre-period for this cohort\n"
            "    for t in range(g, Tn):\n"
            "        gt = (ybar_g[t] - ybar_g[base]) - (ybar_never[t] - ybar_never[base])\n"
            "        att_gt.append(gt)\n"
            "        weights.append((cohort['time'] == t).sum())   # # treated cells\n\n"
            "cs_att = np.average(att_gt, weights=weights)\n"
            "print(f'Clean group-time ATT = {cs_att:.3f}   (true {TRUE_AVG_ATT:.3f})')\n"
            "print(f'group-time bias = {cs_att - TRUE_AVG_ATT:+.3f}   (≈ 0 — recovered!)')\n"
            "assert abs(cs_att - TRUE_AVG_ATT) < 0.3, 'group-time should recover the true ATT'"},
        {"md": "Same data, same true effect — but the clean group-time estimator "
            "lands on the truth while naive TWFE does not. The only difference is "
            "**which comparisons are allowed**: the group-time method never uses "
            "an already-treated unit as a control. That is the entire insight "
            "behind Callaway–Sant'Anna and the modern DiD literature."},
        {"md": "### 🔧 Exercise 5.1 — never-treated vs not-yet-treated controls\n\n"
            "Our clean estimate used the **never-treated** as the comparison "
            "group. A valid alternative is the **not-yet-treated**: at period `t`, "
            "any unit with `g > t` is still a clean control. For the **early** "
            "cohort (`g = 3`) at period `t = 5`, the late cohort (`g = 8`) is "
            "not-yet-treated and usable. Compute `ATT(3, 5)` using the late cohort "
            "(plus never-treated) as the control, and check it recovers the true "
            "effect for that cell.\n\n"
            "Fill in the `# TODO`s."},
        {"code": "g_e, t_star = 3, 5\n"
            "base_e = g_e - 1\n"
            "early = stag[stag['g'] == g_e]\n"
            "# not-yet-treated at t_star: units whose adoption time g > t_star\n"
            "ctrl = stag[stag['g'] > t_star]      # late cohort (g=8) + never-treated\n\n"
            "# TODO: compute the clean 2x2 DiD for the early cohort at t_star using `ctrl`.\n"
            "ybar_e    = early.groupby('time')['y'].mean()\n"
            "ybar_ctrl = ctrl.groupby('time')['y'].mean()\n"
            "att_35 = ...   # TODO: (ybar_e[t_star]-ybar_e[base_e]) - (ctrl change over same periods)\n"
            "# truth = true_effect for an early-cohort unit at t_star\n"
            "# print(att_35, true_effect_for_early_at_t_star)"},
        {"md": "### ✅ Solution 5.1"},
        {"code": "ybar_e    = early.groupby('time')['y'].mean()\n"
            "ybar_ctrl = ctrl.groupby('time')['y'].mean()\n"
            "att_35 = (ybar_e[t_star] - ybar_e[base_e]) \\\n"
            "         - (ybar_ctrl[t_star] - ybar_ctrl[base_e])\n\n"
            "truth_35 = 4.0 * (1.0 + 0.15 * (t_star - g_e))   # true_effect for g=3 at t=5\n"
            "print(f'ATT(3, 5) via not-yet-treated controls = {att_35:.3f}')\n"
            "print(f'true effect for early cohort at t=5     = {truth_35:.3f}')\n"
            "assert abs(att_35 - truth_35) < 0.4, 'not-yet-treated control should also be clean'"},
        {"md": "Both control choices — never-treated and not-yet-treated — give a "
            "clean comparison, because in neither case is the control group's own "
            "treatment effect contaminating the contrast. The forbidden "
            "comparison only arises when you use an **already-treated** group as a "
            "control, which is exactly what naive TWFE does under the hood."},
        {"md": "## Wrap-up & self-check\n\n"
            "- **2×2 DiD** = (treated change) − (control change); the two "
            "differences remove the fixed level gap and the common trend, "
            "recovering the effect.\n"
            "- The TWFE **interaction coefficient** equals the 2×2 DiD, and we "
            "cluster standard errors at the unit because panel rows are serially "
            "correlated.\n"
            "- **Parallel trends** is the whole assumption. You broke it and "
            "watched DiD overstate the effect, then saw an **event study** flag a "
            "differential pre-trend through non-flat leads.\n"
            "- Under **staggered adoption** with heterogeneous, dynamic effects, "
            "naive TWFE is biased (forbidden comparisons / negative weights); a "
            "clean **group-time** estimate using never-treated (or "
            "not-yet-treated) controls recovers the true ATT.\n\n"
            "**You're ready for Week 11** if you can compute a 2×2 by hand, read "
            "an event-study plot, and explain why TWFE breaks under staggered "
            "adoption. Next week: **synthetic control** — when you have one "
            "treated unit and many candidate controls, build a bespoke comparison "
            "unit from a weighted blend of the others."},
    ],
}
