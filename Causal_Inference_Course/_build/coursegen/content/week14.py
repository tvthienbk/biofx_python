# -*- coding: utf-8 -*-
"""Week 14 — Advanced Topics. Modern methods & application block."""

WEEK = {
    "number": 14,
    "slug": "advanced_topics",
    "title": "Advanced Topics",
    "block": "Block IV — Modern methods & application",
    "subtitle": "Mediation, sensitivity analysis, time-varying treatments, and "
                "discovering structure from data.",
    "deliverable": "Problem Set 8 — mediation, sensitivity & discovery; "
                   "Workshop 14 — estimate NDE/NIE, compute an E-value, run a "
                   "tiny g-formula, and sketch PC-style discovery.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5h), workshop (2–3h). This is a "
                    "survey week — breadth over depth. Each topic is a doorway to "
                    "its own literature; the goal is to know what each tool does, "
                    "what it assumes, and when to reach for it.",
    "one_sentence": "Beyond the average effect lie four questions modern causal "
        "inference takes seriously: how an effect flows through a mediator, how "
        "fragile it is to unmeasured confounding, how to handle treatments that "
        "evolve over time, and how to learn the causal structure itself from data.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Decompose a total effect into a natural direct effect (NDE) and a "
        "natural indirect effect (NIE), and state the assumptions that license "
        "the decomposition.",
        "Compute an E-value from a risk ratio and explain, in plain language, how "
        "strong an unmeasured confounder would need to be to explain the result "
        "away.",
        "Explain why ordinary regression fails when a confounder is itself "
        "affected by prior treatment, and how the g-formula repairs it by "
        "standardization.",
        "Describe what the PC and GES algorithms can recover (a Markov "
        "equivalence class) and what they cannot, and where NOTEARS fits in.",
        "State the conditions under which a causal effect estimated in one "
        "population transports to a different target population.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to the workshop.",
    "readings": [
        {"text": "VanderWeele, Explanation in Causal Inference — on mediation & "
                 "E-values.",
         "look_for": "the definitions of the natural direct and indirect effects "
                     "(NDE/NIE), and how an E-value quantifies the unmeasured "
                     "confounding that would be needed to explain away an effect."},
        {"text": "Hernán & Robins, Causal Inference: What If — Part III "
                 "(g-methods).",
         "look_for": "why standard adjustment fails for time-varying treatments "
                     "when a confounder is affected by prior treatment, and how "
                     "the g-formula fixes it by simulating the intervention."},
    ],
    "optional_readings": [
        {"text": "Glymour, Zhang & Spirtes, 'Review of Causal Discovery Methods "
                 "Based on Graphical Models' (2019).",
         "note": "A readable survey of constraint-based (PC), score-based (GES) "
                 "and continuous-optimization (NOTEARS) discovery."},
        {"text": "Bareinboim & Pearl, 'Causal inference and the data-fusion "
                 "problem' (PNAS 2016).",
         "note": "The selection-diagram machinery behind transportability — skim "
                 "for the big picture, not the proofs."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its "
        "own. Four tools, four questions that go beyond the average effect.",
    "concept_sections": [
        {"heading": "Mediation: splitting an effect into direct and indirect",
         "body": "The total effect of X on Y often travels two routes: a direct "
            "path X → Y and an indirect path X → M → Y through a mediator M. "
            "Mediation analysis asks how much of the effect flows through each. "
            "In modern (counterfactual) language we define the natural direct "
            "effect (NDE) — the effect of X holding the mediator at the value it "
            "would naturally take under no treatment — and the natural indirect "
            "effect (NIE) — the effect of moving the mediator from its untreated "
            "to its treated value while holding X fixed. Under no-unmeasured-"
            "confounding (of X→Y, X→M, and M→Y) and no X-by-M interaction in the "
            "simplest case, the total effect decomposes cleanly as TE = NDE + NIE.",
         "bullets": [
            [("Direct effect:  ", {"bold": True}),
             ("the part of X's influence that does NOT go through M (e.g. a drug's "
              "effect on stroke that is not via blood pressure).", {})],
            [("Indirect effect:  ", {"bold": True}),
             ("the part that flows through the mediator (drug → blood pressure → "
              "stroke). NIE = 0 means M is not on the causal path.", {})],
            [("Product & difference methods:  ", {"bold": True}),
             ("with linear models, NIE = (X→M coefficient)·(M→Y coefficient), and "
              "NDE = the X coefficient in the Y model that includes M. They agree "
              "and sum to the total effect.", {})],
         ],
         "callout": {"title": "The fourth confounding assumption people forget",
            "color": "RED",
            "lines": ["Mediation needs no unmeasured confounding of the "
                      "MEDIATOR–OUTCOME relationship — even in a randomized trial "
                      "where X is randomized, M is not.",
                      "A mediator–outcome confounder affected by treatment makes "
                      "the NDE/NIE non-identified by simple regression; that is "
                      "exactly the time-varying problem g-methods were built for."]}},
        {"heading": "Sensitivity analysis: how fragile is the result?",
         "body": "Every observational estimate rests on 'no unmeasured "
            "confounding,' which is never guaranteed. Sensitivity analysis asks: "
            "how strong would an unmeasured confounder have to be to overturn the "
            "conclusion? The E-value answers this for a risk ratio with no extra "
            "assumptions: it is the minimum strength of association (on the risk-"
            "ratio scale) that an unmeasured confounder would need with BOTH the "
            "treatment and the outcome to fully explain away the observed effect. "
            "Rosenbaum bounds play the same role for matched designs, asking how "
            "much hidden bias in treatment assignment would be needed to change a "
            "test's verdict.",
         "bullets": [
            [("E-value formula:  ", {"bold": True}),
             ("for an observed risk ratio RR ≥ 1, E = RR + √(RR·(RR−1)). For RR "
              "below 1, first take 1/RR. A larger E-value means a more robust "
              "finding.", {})],
            [("Interpretation:  ", {"bold": True}),
             ("an E-value of 2 says a confounder would need to roughly double both "
              "the chance of treatment and the chance of the outcome — beyond all "
              "measured covariates — to nullify the effect.", {})],
            [("Rosenbaum bounds (Γ):  ", {"bold": True}),
             ("for matched pairs, report the smallest Γ (odds of differential "
              "treatment within a pair) at which significance is lost. Small Γ = "
              "fragile.", {})],
         ]},
        {"heading": "g-methods: treatments that change over time",
         "body": "When treatment is given repeatedly, a covariate measured between "
            "doses can be simultaneously a confounder of later treatment and a "
            "consequence of earlier treatment — a 'time-varying confounder "
            "affected by prior treatment.' Such a variable is a mediator AND a "
            "confounder at once. Adjusting for it (ordinary regression) blocks "
            "part of the effect you want and opens collider paths; NOT adjusting "
            "leaves later treatment confounded. There is no single regression that "
            "is right. The g-formula sidesteps the trap by standardization: model "
            "how covariates and outcomes evolve, then SIMULATE the world under each "
            "treatment plan and average the outcome.",
         "bullets": [
            [("The trap:  ", {"bold": True}),
             ("L1 ← A0 and L1 → A1, L1 → Y. Regress on L1 → over-control bias; "
              "omit L1 → A1 is confounded. Both biased.", {})],
            [("g-formula:  ", {"bold": True}),
             ("E[Y under plan a] = average over the simulated covariate history of "
              "E[Y | history, treatment set to a]. Recovers the truth.", {})],
            [("Cousins:  ", {"bold": True}),
             ("inverse-probability-of-treatment weighting (marginal structural "
              "models) and g-estimation of structural nested models solve the same "
              "problem by different routes.", {})],
         ],
         "callout": {"title": "Why this is the hardest idea in the course",
            "color": "AMBER",
            "lines": ["The variable you are most tempted to 'control for' is the "
                      "one that destroys your estimate. Timing and structure, not "
                      "a covariate list, decide the analysis.",
                      "If you take one thing from Week 14: a confounder affected by "
                      "treatment needs g-methods, not regression."]}},
        {"heading": "Causal discovery & transportability",
         "body": "Causal discovery flips the usual workflow: instead of assuming a "
            "graph, it tries to learn graph structure from data. Constraint-based "
            "methods (PC) test conditional independences to prune edges and orient "
            "some of them; score-based methods (GES) search over graphs to "
            "optimize a fit score; NOTEARS recasts the search as continuous "
            "optimization with a smooth acyclicity penalty. All of them are "
            "limited: from observational data alone you can usually recover only a "
            "Markov equivalence class — a set of graphs sharing the same "
            "independences — not a unique DAG. Transportability is the mirror-image "
            "question: given an effect learned in one population, when does it carry "
            "to a new one? The answer depends on which mechanisms differ, encoded "
            "in a selection diagram.",
         "bullets": [
            [("PC algorithm:  ", {"bold": True}),
             ("start from a complete graph; remove an edge X–Y whenever X ⫫ Y given "
              "some set; then orient colliders and propagate. Output: a CPDAG.", {})],
            [("Equivalence class:  ", {"bold": True}),
             ("X→Y→Z, X←Y←Z and X←Y→Z all imply X ⫫ Z | Y — indistinguishable "
              "without intervention or extra assumptions.", {})],
            [("Transportability:  ", {"bold": True}),
             ("an effect transports when the differing mechanisms (the "
              "'S-nodes') do not sit on the paths that identify it; otherwise it "
              "must be re-weighted or re-estimated.", {})],
         ]},
    ],
    "problem_set": {
        "label": "Problem Set 8",
        "title": "Mediation, sensitivity & discovery",
        "intro": "Five short problems spanning the week's four tools. Work each "
            "before looking at the solution. Where a number is asked for, show the "
            "formula; where a graph is asked for, name the relevant paths.",
        "problems": [
            {"title": "Decompose a total effect (NDE + NIE)",
             "prompt": "In a linear system, X → M with coefficient a = 0.6, "
                "M → Y with coefficient b = 0.5, and a direct path X → Y with "
                "coefficient c′ = 0.3. Assuming no X–M interaction and no "
                "unmeasured confounding, compute the natural indirect effect, the "
                "natural direct effect, and the total effect. Confirm the "
                "decomposition.",
             "solution_title": "NIE = 0.30, NDE = 0.30, TE = 0.60 = NDE + NIE.",
             "solution": [
                "Indirect (through M): NIE = a·b = 0.6 × 0.5 = 0.30. This is the "
                "product-method estimate — the effect that flows X → M → Y.",
                "Direct (not through M): NDE = c′ = 0.30, the coefficient on X in "
                "the outcome model that already includes M.",
                "Total: TE = NDE + NIE = 0.30 + 0.30 = 0.60, which equals the X "
                "coefficient from regressing Y on X alone. The proportion mediated "
                "is NIE/TE = 50%.",
                "Caveat: the clean sum requires no X-by-M interaction and no "
                "mediator–outcome confounding; with interaction you must report "
                "NDE and NIE at specified levels."]},
            {"title": "Compute and interpret an E-value",
             "prompt": "An observational study reports a risk ratio of RR = 2.0 "
                "for an exposure–disease association, adjusted for all measured "
                "confounders. Compute the E-value and state, in one sentence, what "
                "an unmeasured confounder would have to look like to explain the "
                "result away.",
             "solution_title": "E-value ≈ 3.41 — a strong unmeasured confounder is "
                "needed.",
             "solution": [
                "Formula: E = RR + √(RR·(RR−1)) = 2 + √(2·1) = 2 + √2 ≈ 3.41.",
                "Meaning: an unmeasured confounder would need to be associated with "
                "BOTH the exposure and the outcome by a risk ratio of at least 3.41 "
                "each — above and beyond every measured covariate — to fully "
                "explain away the observed RR of 2.",
                "A weaker confounder (say RR 1.5 with each) could not nullify the "
                "effect, though it could shift it. Larger E-values signal more "
                "robust findings; an E-value near 1 means the result is fragile.",
                "The E-value makes no assumption about the confounder's prevalence "
                "or direction — that simplicity is exactly why it is widely "
                "reported."]},
            {"title": "Why time-varying confounding defeats regression",
             "prompt": "A patient receives treatment at two times, A0 then A1. "
                "Between them, a biomarker L1 is measured. L1 is influenced by A0 "
                "(treatment changes the biomarker), and L1 influences both A1 (the "
                "clinician reacts to it) and the final outcome Y. Explain why "
                "fitting Y ~ A0 + A1 + L1 by ordinary least squares does not "
                "recover the effect of the treatment plan.",
             "solution_title": "L1 is a confounder of A1 AND a mediator of A0 — no "
                "single regression is right.",
             "solution": [
                "For A1 you must adjust for L1: it is a common cause of A1 and Y, "
                "so omitting it leaves A1's effect confounded.",
                "But L1 lies on the path A0 → L1 → Y, so it is a mediator of A0. "
                "Conditioning on it BLOCKS part of A0's effect (over-control "
                "bias) and, because L1 is a collider on A0 → L1 ← (causes of L1), "
                "can open spurious paths.",
                "So adjusting for L1 biases the A0 effect downward while omitting "
                "it biases the A1 effect upward — the same coefficient cannot be "
                "both adjusted and unadjusted for L1.",
                "The fix is the g-formula (or IPW / g-estimation): model L1's "
                "dependence on A0 and Y's dependence on the full history, then "
                "standardize by simulating each treatment plan."]},
            {"title": "What the PC algorithm can and cannot recover",
             "prompt": "You run the PC algorithm on observational data generated "
                "by the chain X → Y → Z. What skeleton does PC recover, which edges "
                "can it orient, and why might it fail to return the exact "
                "data-generating DAG?",
             "solution_title": "PC recovers the skeleton X–Y–Z and the Markov "
                "equivalence class, not necessarily the unique DAG.",
             "solution": [
                "Skeleton: PC keeps the edges X–Y and Y–Z and removes X–Z, because "
                "the test finds X ⫫ Z given Y (the conditional independence implied "
                "by a chain).",
                "Orientation: with no unshielded collider at Y (the data show "
                "X ⫫ Z | Y, not the marginal independence a collider would give), "
                "PC cannot orient the edges and returns an undirected chain — a "
                "CPDAG.",
                "X → Y → Z, X ← Y ← Z and X ← Y → Z all share the single "
                "independence X ⫫ Z | Y, so they form one Markov equivalence class "
                "that observational data cannot tell apart.",
                "To pin down the direction you need an intervention, a time "
                "ordering, or extra assumptions (e.g. non-Gaussian noise as in "
                "LiNGAM, or the functional-form assumptions NOTEARS leans on)."]},
            {"title": "Transportability to a new population",
             "prompt": "You estimate the effect of a job-training program in City A "
                "and want to apply the number to City B. Under what conditions does "
                "the City A effect transport to City B, and what would block it? "
                "Give one concrete example of a difference that does NOT threaten "
                "transport and one that does.",
             "solution_title": "It transports when the differing mechanisms don't "
                "lie on the paths that identify the effect.",
             "solution": [
                "Transport holds if the causal mechanism linking training to "
                "earnings is the same in both cities and the populations differ "
                "only in the DISTRIBUTION of variables that the effect is already "
                "conditioned on (e.g. age mix) — then re-weight by those covariates.",
                "Safe difference: City B simply has more young workers. If the "
                "effect is homogeneous across age (or we report age-specific "
                "effects), re-weighting to City B's age distribution gives a valid "
                "transported estimate.",
                "Blocking difference: City B's labour market changes how training "
                "translates into jobs (the training → employment mechanism itself "
                "differs). That is a difference on the causal path — an 'S-node' on "
                "an identifying path — and the raw effect does not carry over.",
                "Formally, transportability is decided by a selection diagram: mark "
                "where the populations differ, then check whether the effect is "
                "still identifiable using both populations' data."]},
        ],
    },
    "lab": {
        "label": "Workshop 14",
        "title": "Mediation, E-values & discovery",
        "goal": "in one sitting, estimate a natural direct and indirect effect, "
            "compute an E-value for an observed association, run a tiny g-formula "
            "on a two-timepoint example, and sketch the PC algorithm's first move "
            "— each on simulated data with a known answer. Python or R; both shown.",
        "steps": [
            {"heading": "Step 1 · Simulate a mediator and estimate NDE/NIE",
             "body": "Generate X → M → Y plus a direct X → Y path with known "
                "coefficients. Estimate the indirect effect by the product method "
                "and the direct effect from the outcome model, and confirm they sum "
                "to the total effect.",
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(1)\nn = 40_000\n"
                "a, b, cp = 0.6, 0.5, 0.3        # X->M, M->Y, direct X->Y\n"
                "X = rng.normal(size=n)\n"
                "M = a*X + rng.normal(size=n)\n"
                "Y = cp*X + b*M + rng.normal(size=n)\n"
                "a_hat  = sm.OLS(M, sm.add_constant(X)).fit().params[1]\n"
                "mY     = sm.OLS(Y, sm.add_constant(np.c_[X, M])).fit().params\n"
                "NDE, b_hat = mY[1], mY[2]\n"
                "NIE = a_hat * b_hat\n"
                "TE  = sm.OLS(Y, sm.add_constant(X)).fit().params[1]\n"
                "print(f'NDE={NDE:.3f} NIE={NIE:.3f} sum={NDE+NIE:.3f} TE={TE:.3f}')",
             "code_r": "set.seed(1); n <- 40000\n"
                "a <- 0.6; b <- 0.5; cp <- 0.3\n"
                "X <- rnorm(n); M <- a*X + rnorm(n); Y <- cp*X + b*M + rnorm(n)\n"
                'a_hat <- coef(lm(M ~ X))["X"]\n'
                "mY <- coef(lm(Y ~ X + M))\n"
                'NDE <- mY["X"]; NIE <- a_hat * mY["M"]\n'
                'cat(sprintf("NDE=%.3f NIE=%.3f sum=%.3f\\n", NDE, NIE, NDE+NIE))'},
            {"heading": "Step 2 · Compute an E-value",
             "body": "Implement the E-value for a risk ratio and apply it to an "
                "observed association. Note how the required confounder strength "
                "grows with the effect size.",
             "code_python": "import numpy as np\n"
                "def evalue_rr(rr):\n"
                "    rr = rr if rr >= 1 else 1.0/rr\n"
                "    return rr + np.sqrt(rr*(rr - 1))\n"
                "for rr in (1.2, 2.0, 3.9):\n"
                "    print(f'RR={rr}:  E-value={evalue_rr(rr):.2f}')",
             "code_r": "evalue_rr <- function(rr) {\n"
                "  if (rr < 1) rr <- 1/rr\n"
                "  rr + sqrt(rr * (rr - 1))\n}\n"
                'for (rr in c(1.2, 2.0, 3.9)) cat(sprintf("RR=%.1f E=%.2f\\n", rr, evalue_rr(rr)))'},
            {"heading": "Step 3 · A tiny g-formula (2 timepoints)",
             "body": "Build the time-varying-confounding trap: A0 affects L1; L1 "
                "affects A1 and Y. Show ordinary regression on L1 is biased, then "
                "recover the truth by standardization (simulate the intervention).",
             "code_python": "rng = np.random.default_rng(2); n = 200_000\n"
                "A0 = rng.binomial(1, 0.5, n)\n"
                "L1 = rng.normal(1.0*A0, 1.0)               # A0 -> L1\n"
                "A1 = rng.binomial(1, 1/(1+np.exp(-(L1-0.5))))\n"
                "Y  = 1.0*A0 + 1.0*A1 + 1.0*L1 + rng.normal(size=n)   # truth: 3\n"
                "pf = sm.OLS(Y, sm.add_constant(np.c_[A0,A1,L1])).fit().params\n"
                "print('naive adjust-L1:', round(pf[1]+pf[2], 3))   # biased\n"
                "pL = sm.OLS(L1, sm.add_constant(A0)).fit().params\n"
                "pY = sm.OLS(Y,  sm.add_constant(np.c_[A0,A1,L1])).fit().params\n"
                "g  = lambda a0,a1: pY[0]+pY[1]*a0+pY[2]*a1+pY[3]*(pL[0]+pL[1]*a0)\n"
                "print('g-formula:', round(g(1,1)-g(0,0), 3))       # ~3",
             "code_r": "set.seed(2); n <- 200000\n"
                "A0 <- rbinom(n,1,0.5)\nL1 <- rnorm(n, A0, 1)\n"
                "A1 <- rbinom(n,1, 1/(1+exp(-(L1-0.5))))\n"
                "Y  <- A0 + A1 + L1 + rnorm(n)\n"
                "pL <- coef(lm(L1 ~ A0)); pY <- coef(lm(Y ~ A0 + A1 + L1))\n"
                "g <- function(a0,a1) pY[1]+pY[2]*a0+pY[3]*a1+pY[4]*(pL[1]+pL[2]*a0)\n"
                'cat(sprintf("g-formula=%.3f\\n", g(1,1)-g(0,0)))'},
            {"heading": "Step 4 · (Sketch) PC-style independence tests",
             "body": "Generate a chain X → Y → Z and use partial correlations as "
                "the conditional-independence test PC relies on. The X–Z edge "
                "should drop out once you condition on Y — the first move of "
                "skeleton discovery.",
             "code_python": "rng = np.random.default_rng(3); n = 4000\n"
                "X = rng.normal(size=n)\nY = X + rng.normal(size=n)\n"
                "Z = Y + rng.normal(size=n)\n"
                "def pcorr(u, v, w=None):\n"
                "    if w is None: return np.corrcoef(u, v)[0,1]\n"
                "    Wc = sm.add_constant(w)\n"
                "    ru = u - Wc @ np.linalg.lstsq(Wc, u, rcond=None)[0]\n"
                "    rv = v - Wc @ np.linalg.lstsq(Wc, v, rcond=None)[0]\n"
                "    return np.corrcoef(ru, rv)[0,1]\n"
                "print('X,Z marginal :', round(pcorr(X, Z), 3))\n"
                "print('X,Z given Y  :', round(pcorr(X, Z, Y), 3), '-> drop edge')",
             "code_r": "set.seed(3); n <- 4000\n"
                "X <- rnorm(n); Y <- X + rnorm(n); Z <- Y + rnorm(n)\n"
                'cat("X,Z marginal:", round(cor(X,Z),3), "\\n")\n'
                'rx <- resid(lm(X ~ Y)); rz <- resid(lm(Z ~ Y))\n'
                'cat("X,Z given Y :", round(cor(rx,rz),3), "-> drop edge\\n")'},
        ],
        "expected": "Step 1: NDE ≈ 0.30, NIE ≈ 0.30, and they sum to the total "
            "effect ≈ 0.60. Step 2: E-values of about 1.69, 3.41, and 7.26 — "
            "bigger effects demand stronger confounders. Step 3: the naive "
            "L1-adjusted estimate lands near 2.0, well below the true 3.0, while "
            "the g-formula returns ≈ 3.0. Step 4: X and Z are correlated "
            "marginally but their partial correlation given Y is ≈ 0, so PC "
            "removes the X–Z edge and recovers the chain skeleton.",
        "submit": [
            "Push a notebook or script reproducing all four steps with the "
            "printed numbers and a one-line interpretation of each.",
            "In two sentences, explain why the g-formula beats the regression in "
            "Step 3 — name the role L1 plays for A0 versus A1.",
            "State the E-value for your own field's typical 'interesting' risk "
            "ratio and say whether you would call such a finding robust.",
        ],
    },
    "self_check": [
        "Decompose a linear total effect into NDE and NIE and explain the "
        "product method without notes.",
        "Compute an E-value for a given risk ratio and interpret it for a "
        "non-technical colleague.",
        "Explain why a confounder affected by prior treatment breaks ordinary "
        "regression, and what the g-formula does instead.",
        "Say what a Markov equivalence class is and why observational discovery "
        "stops there.",
        "State one condition under which an effect transports to a new population "
        "and one that blocks it.",
    ],
    "next_week": {
        "heading": "Coming up: Week 15 — Capstone, reproducibility & communication",
        "teaser": "The term lands. You'll assemble the full workflow — question, "
            "assumptions, identification, estimation, validation — into a single "
            "reproducible capstone, and learn to communicate a causal claim "
            "honestly: stating assumptions out loud, reporting sensitivity, and "
            "knowing when the data simply cannot answer the question. Bring a "
            "dataset and a question you care about.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 14", "items": [
            {"t": "Beyond the ATE", "d": "Four questions modern causal inference "
             "takes seriously."},
            {"t": "Mediation", "d": "Splitting a total effect into direct and "
             "indirect (NDE / NIE)."},
            {"t": "Sensitivity analysis", "d": "E-values and Rosenbaum bounds — how "
             "fragile is the result?"},
            {"t": "g-methods", "d": "Time-varying treatments and the g-formula."},
            {"t": "Causal discovery", "d": "PC, GES and NOTEARS — learning the "
             "graph from data."},
            {"t": "Transportability", "d": "When an effect carries to a new "
             "population."},
        ]},
        {"type": "content", "kicker": "Where we are",
         "title": "The average effect was only the beginning", "bullets": [
            "Most of the term estimated one number: the average treatment effect "
            "under a fixed treatment.",
            "Real questions push further: through what mechanism? how fragile? what "
            "if treatment evolves? what is the graph?",
            ("This week is a survey — breadth over depth.", 1),
            ("Each topic is a doorway to its own literature and its own course.", 1),
            "Goal: know what each tool does, what it assumes, and when to reach "
            "for it.",
         ],
         "note": {"title": "Theme",
            "body": "Four advanced questions, four tools. None replaces the "
            "workflow — each extends it."}},
        {"type": "statement",
         "quote": "An average effect tells you that something works. It does not "
            "tell you how, how sure, or for whom.",
         "attribution": "Mediation answers 'how', sensitivity analysis answers "
            "'how sure', g-methods handle 'over time', and discovery asks what the "
            "structure even is."},

        {"type": "section", "kicker": "Part 1", "title": "Mediation",
         "subtitle": "Decomposing a total effect into the part that flows through "
            "a mediator and the part that does not."},
        {"type": "content", "kicker": "The question",
         "title": "Through what mechanism does X affect Y?", "bullets": [
            "A drug lowers stroke risk. How much is via blood pressure, and how "
            "much by some other route?",
            "Total effect splits into a DIRECT path X → Y and an INDIRECT path "
            "X → M → Y.",
            "Mediation analysis quantifies each — central to understanding "
            "mechanism, not just impact.",
            "The modern, counterfactual definitions are the natural direct and "
            "indirect effects.",
         ],
         "note": {"title": "Why it matters",
            "body": "If most of the effect is indirect, intervene on the mediator. "
            "If direct, the mediator is a red herring."}},
        {"type": "compare", "kicker": "The two natural effects",
         "title": "Natural direct vs. natural indirect effect", "columns": [
            {"head": "NDE — direct", "sub": "hold M at its untreated value",
             "points": [
                "Effect of X with M frozen at M(0).",
                "The route that does NOT go through M.",
                "In linear models: the X coefficient when M is in the model."]},
            {"head": "NIE — indirect", "sub": "move M from M(0) to M(1)", "points": [
                "Effect of shifting M as X would, holding X fixed.",
                "The route X → M → Y.",
                "In linear models: (X→M) × (M→Y), the product method."]},
            {"head": "Together", "sub": "TE = NDE + NIE", "points": [
                "They sum to the total effect (no interaction).",
                "Proportion mediated = NIE / TE.",
                "Difference and product methods agree."]},
        ]},
        {"type": "content", "kicker": "The catch",
         "title": "Mediation needs a fourth no-confounding assumption", "bullets": [
            "Even if X is randomized, the mediator M is NOT randomized.",
            "You need no unmeasured confounding of the M → Y relationship — easy "
            "to forget.",
            "Worse: a mediator–outcome confounder AFFECTED by treatment breaks "
            "simple regression.",
            ("That exact structure is the time-varying problem in Part 3.", 1),
         ],
         "note": {"title": "Honesty",
            "body": "Mediation is the most assumption-hungry tool of the week. "
            "Report the assumptions, not just the percentages."}},

        {"type": "section", "kicker": "Part 2", "title": "Sensitivity analysis",
         "subtitle": "Every observational estimate assumes no unmeasured "
            "confounding. Sensitivity analysis asks how fragile that assumption "
            "makes the conclusion."},
        {"type": "content", "kicker": "The idea",
         "title": "How strong would a hidden confounder have to be?", "bullets": [
            "We can never prove 'no unmeasured confounding.' We CAN ask what it "
            "would take to overturn the result.",
            "A robust finding survives plausible hidden confounding; a fragile one "
            "does not.",
            "Two workhorses: the E-value (for risk ratios) and Rosenbaum bounds "
            "(for matched designs).",
            "This turns an unfalsifiable worry into a reportable number.",
         ],
         "note": {"title": "Reframe",
            "body": "Don't ask 'is there unmeasured confounding?' Ask 'how much "
            "would be needed to change my answer?'"}},
        {"type": "content", "kicker": "The E-value",
         "title": "One number for the strength of confounding needed", "bullets": [
            ("For an observed risk ratio RR ≥ 1:  E = RR + √(RR·(RR−1)).", 0),
            ("(If RR < 1, first take 1/RR.)", 1),
            "It is the minimum association a confounder must have with BOTH "
            "treatment and outcome to explain the effect away.",
            "RR = 2 gives E ≈ 3.41: a confounder would need to roughly triple both "
            "odds, beyond every measured covariate.",
            "No assumption about the confounder's prevalence — its simplicity is "
            "why it is everywhere.",
         ],
         "note": {"title": "Read it",
            "body": "Bigger E-value = more robust. An E-value near 1 means a whiff "
            "of confounding could erase the finding."}},
        {"type": "table", "kicker": "E-value grows with effect size",
         "title": "Risk ratio vs. confounding needed to nullify it",
         "headers": ["Observed RR", "E-value", "Reading"],
         "rows": [
            ["1.2", "1.69", "Modest effect — a moderate confounder could explain it."],
            ["2.0", "3.41", "Needs a strong confounder on both arms."],
            ["3.9", "7.26", "Very robust — implausibly strong confounding required."],
            ["1.0", "1.00", "No effect, nothing to explain away."],
         ],
         "note": {"title": "Rosenbaum bounds",
            "body": "The matched-design cousin: report the smallest Γ (hidden bias "
            "in assignment) at which significance is lost."}},

        {"type": "section", "kicker": "Part 3", "title": "g-methods",
         "subtitle": "When treatment changes over time and a confounder is itself "
            "affected by prior treatment, ordinary regression has no right answer."},
        {"type": "content", "kicker": "The setup",
         "title": "Time-varying treatment, time-varying confounding", "bullets": [
            "Treatment is given repeatedly: A0 then A1, with a covariate L1 "
            "measured in between.",
            "L1 is a confounder of A1 (clinicians react to it) AND a consequence "
            "of A0 (treatment moved it).",
            "So L1 is a confounder and a mediator at the same time.",
            "This is the rule, not the exception, in longitudinal and clinical "
            "data.",
         ],
         "note": {"title": "Picture",
            "body": "A0 → L1 → A1, with L1 → Y and A0 → Y. The arrow A0 → L1 is "
            "what causes the trouble."}},
        {"type": "compare", "kicker": "Why regression fails",
         "title": "Every single regression is wrong", "columns": [
            {"head": "Adjust for L1", "sub": "Y ~ A0 + A1 + L1", "points": [
                "Correct for A1 (L1 confounds it).",
                "But L1 is on the A0 → L1 → Y path.",
                "Over-control: blocks part of A0's effect."]},
            {"head": "Omit L1", "sub": "Y ~ A0 + A1", "points": [
                "Avoids blocking A0's path.",
                "But now A1 is confounded by L1.",
                "Bias the other way."]},
            {"head": "The verdict", "sub": "no fixed coefficient", "points": [
                "L1 must be both in and out.",
                "Impossible for one regression.",
                "Need standardization — the g-formula."]},
        ]},
        {"type": "steps", "kicker": "The g-formula",
         "title": "Standardize by simulating the intervention", "steps": [
            {"title": "Model the history", "body": "— how L1 responds to A0, and "
             "how Y responds to A0, A1, L1."},
            {"title": "Fix a plan", "body": "— e.g. always-treat (A0=A1=1) vs "
             "never-treat (A0=A1=0)."},
            {"title": "Simulate forward", "body": "— draw L1 under the plan, then "
             "the outcome, breaking L1's link to assignment."},
            {"title": "Average & contrast", "body": "— the mean outcome under each "
             "plan; their difference is the effect."},
         ],
         "note": "Cousins: IPW / marginal structural models and g-estimation solve "
            "the same problem by re-weighting or by structural nested models."},
        {"type": "statement",
         "quote": "The variable you are most tempted to control for is the one "
            "that destroys your estimate.",
         "attribution": "A confounder affected by prior treatment needs g-methods, "
            "not regression. Timing and structure decide the analysis — never a "
            "covariate checklist."},

        {"type": "section", "kicker": "Part 4", "title": "Causal discovery",
         "subtitle": "Flip the workflow: instead of assuming a graph, try to learn "
            "its structure from the data itself."},
        {"type": "content", "kicker": "The ambition",
         "title": "Can the data tell us the graph?", "bullets": [
            "All term we ASSUMED a DAG. Discovery asks whether we can LEARN one.",
            "Constraint-based (PC): test conditional independences, prune and "
            "orient edges.",
            "Score-based (GES): search over graphs to optimize a fit score.",
            "Continuous (NOTEARS): recast the search as smooth optimization with "
            "an acyclicity penalty.",
         ],
         "note": {"title": "Use with care",
            "body": "Discovery proposes hypotheses to test and refine — it does "
            "not hand you a proven causal model."}},
        {"type": "steps", "kicker": "How PC works",
         "title": "The PC algorithm, in four moves", "steps": [
            {"title": "Start complete", "body": "— connect every pair of variables."},
            {"title": "Prune edges", "body": "— remove X–Y whenever X ⫫ Y given "
             "some conditioning set."},
            {"title": "Orient colliders", "body": "— find unshielded X → K ← Y "
             "patterns from the independences."},
            {"title": "Propagate", "body": "— apply orientation rules; return a "
             "CPDAG (a partly-directed graph)."},
        ]},
        {"type": "content", "kicker": "The hard limit",
         "title": "You recover an equivalence class, not a unique DAG", "bullets": [
            "X → Y → Z, X ← Y ← Z and X ← Y → Z all imply the same independence: "
            "X ⫫ Z | Y.",
            "Observational data cannot tell these three apart — they are Markov "
            "equivalent.",
            "PC therefore returns a CPDAG: some edges directed, some left "
            "undirected.",
            "To orient the rest you need interventions, a time order, or extra "
            "assumptions (non-Gaussian noise, etc.).",
         ],
         "note": {"title": "Honest output",
            "body": "Discovery narrows the candidates; domain knowledge and "
            "experiments finish the job."}},

        {"type": "section", "kicker": "Part 5", "title": "Transportability",
         "subtitle": "An effect learned in one population is not automatically the "
            "effect in another. When does it carry over?"},
        {"type": "content", "kicker": "The question",
         "title": "Does a City-A effect apply to City B?", "bullets": [
            "You estimated a clean effect in one population. A decision-maker wants "
            "the number for a different one.",
            "Naively reusing it assumes the two worlds are causally identical — "
            "they rarely are.",
            "Transportability formalizes which differences are harmless and which "
            "are fatal.",
            "Encoded in a selection diagram: mark the nodes whose mechanisms "
            "differ between populations.",
         ],
         "note": {"title": "Data fusion",
            "body": "The broader programme: combine experimental and observational "
            "data across settings to answer a target question."}},
        {"type": "compare", "kicker": "Which differences matter?",
         "title": "Harmless vs. fatal population differences", "columns": [
            {"head": "Transports", "sub": "re-weight and go", "points": [
                "Differ only in the mix of covariates the effect conditions on.",
                "e.g. City B is simply younger.",
                "Re-weight to the target's covariate distribution."]},
            {"head": "Does not transport", "sub": "re-estimate", "points": [
                "A mechanism on the identifying path differs.",
                "e.g. training → jobs works differently in City B.",
                "The raw effect cannot be carried over."]},
        ]},

        {"type": "section", "kicker": "Part 6", "title": "Pulling it together",
         "subtitle": "Four tools, one discipline: state assumptions, estimate "
            "honestly, stress-test the answer."},
        {"type": "table", "kicker": "The week on one slide",
         "title": "Four questions, four tools",
         "headers": ["Question", "Tool", "Key idea / limit"],
         "rows": [
            ["Through what mechanism?", "Mediation (NDE/NIE)",
             "Split TE = direct + indirect; needs M–Y confounding control."],
            ["How fragile?", "E-value / Rosenbaum",
             "Strength of unmeasured confounding needed to explain it away."],
            ["Treatment over time?", "g-formula / IPW",
             "Standardize by simulating the plan; regression alone fails."],
            ["What is the graph?", "PC / GES / NOTEARS",
             "Learn structure — but only up to a Markov equivalence class."],
         ],
         "note": {"title": "Plus",
            "body": "Transportability decides when any of these answers carries to "
            "a new population."}},
        {"type": "content", "kicker": "Practical guidance",
         "title": "When to reach for each tool", "bullets": [
            "Reviewer asks 'how robust?' → report an E-value alongside the "
            "estimate.",
            "Stakeholder asks 'why does it work?' → mediation, with its "
            "assumptions stated.",
            "Longitudinal treatment with feedback → g-methods, full stop.",
            "No credible graph and many variables → discovery to generate "
            "hypotheses, then test them.",
            "Applying a result elsewhere → check transportability before you "
            "quote the number.",
         ],
         "note": {"title": "Capstone preview",
            "body": "Next week you assemble the whole workflow into one "
            "reproducible analysis — and communicate it honestly."}},
        {"type": "statement",
         "quote": "Beyond the average effect: how, how sure, over time, and what "
            "structure.",
         "attribution": "These are survey tools — each a doorway. Next week we "
            "close the loop: reproducibility, communication, and the capstone. "
            "See you in the workshop."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · Mediation — natural direct & indirect effects\n\n"
            "We simulate the canonical mediation structure: a treatment `X` affects "
            "a mediator `M`, and both `X` and `M` affect the outcome `Y`. With "
            "**known** coefficients we can check that our estimates recover the "
            "true direct and indirect effects — and that they sum to the total "
            "effect.\n\n"
            "Truth:  `X → M` has slope `a`, `M → Y` has slope `b`, and the direct "
            "path `X → Y` has slope `c'`. Then\n\n"
            "- **NIE** (natural indirect effect) `= a · b`  — the route `X → M → Y`,\n"
            "- **NDE** (natural direct effect) `= c'`  — the route that skips `M`,\n"
            "- **Total effect** `= NDE + NIE = c' + a·b`."},
        {"code": "import statsmodels.api as sm\n\n"
            "# --- ground truth ---\n"
            "a, b, cprime = 0.6, 0.5, 0.3        # X->M, M->Y, direct X->Y\n"
            "n = 40_000\n"
            "X = RNG.normal(size=n)\n"
            "M = a * X + RNG.normal(size=n)\n"
            "Y = cprime * X + b * M + RNG.normal(size=n)\n\n"
            "# --- product / difference method with linear models ---\n"
            "a_hat = sm.OLS(M, sm.add_constant(X)).fit().params[1]      # X -> M\n"
            "outcome = sm.OLS(Y, sm.add_constant(np.c_[X, M])).fit().params\n"
            "NDE, b_hat = outcome[1], outcome[2]                        # direct, M -> Y\n"
            "NIE = a_hat * b_hat                                        # indirect\n"
            "TE_direct = sm.OLS(Y, sm.add_constant(X)).fit().params[1]  # total, X alone\n\n"
            "print(f'a (X->M) : est={a_hat:.3f}  true={a}')\n"
            "print(f'b (M->Y) : est={b_hat:.3f}  true={b}')\n"
            "print(f'NDE      : est={NDE:.3f}   true={cprime}')\n"
            "print(f'NIE      : est={NIE:.3f}   true={a*b:.3f}')\n"
            "print(f'NDE+NIE  : {NDE + NIE:.3f}   total (Y~X): {TE_direct:.3f}'\n"
            "      f'   true total: {cprime + a*b:.3f}')"},
        {"md": "The decomposition holds: `NDE + NIE` equals the total effect, and "
            "each piece recovers its true coefficient. Let's make that a hard check."},
        {"code": "assert abs(NDE - cprime) < 0.05,         'NDE should recover c'\n"
            "assert abs(NIE - a * b) < 0.05,          'NIE should recover a*b'\n"
            "assert abs((NDE + NIE) - TE_direct) < 0.05, 'NDE+NIE should equal TE'\n"
            "print('OK — mediation decomposition recovered within tolerance.')\n"
            "print(f'Proportion mediated = NIE/TE = {NIE / (NDE + NIE):.1%}')"},
        {"md": "### 🔧 Exercise 1.1 — a mediator that does nothing\n\n"
            "Suppose `M` is influenced by `X` but does **not** affect `Y` (set "
            "`b = 0`). Predict the NIE *before* you run it, then estimate NDE and "
            "NIE and confirm the indirect effect is ~0 while the direct effect "
            "equals the (now total) `X → Y` slope.\n\n"
            "Fill in the `# TODO`s. The skeleton still runs as-is."},
        {"code": "# TODO: simulate X -> M, but M -> Y has slope 0; keep a direct X -> Y = 0.4\n"
            "a2, b2, cprime2 = 0.6, 0.0, 0.4\n"
            "X2 = RNG.normal(size=n)\n"
            "M2 = ...        # TODO: a2 * X2 + noise\n"
            "Y2 = ...        # TODO: cprime2 * X2 + b2 * M2 + noise\n"
            "# a2_hat = ...  # slope of M2 on X2\n"
            "# out2   = ...  # OLS of Y2 on [X2, M2]; params\n"
            "# NDE2, NIE2 = ..., ...\n"
            "# print(NDE2, NIE2)"},
        {"md": "### ✅ Solution 1.1"},
        {"code": "a2, b2, cprime2 = 0.6, 0.0, 0.4\n"
            "X2 = RNG.normal(size=n)\n"
            "M2 = a2 * X2 + RNG.normal(size=n)\n"
            "Y2 = cprime2 * X2 + b2 * M2 + RNG.normal(size=n)\n"
            "a2_hat = sm.OLS(M2, sm.add_constant(X2)).fit().params[1]\n"
            "out2   = sm.OLS(Y2, sm.add_constant(np.c_[X2, M2])).fit().params\n"
            "NDE2, NIE2 = out2[1], a2_hat * out2[2]\n"
            "print(f'NDE2={NDE2:.3f} (true {cprime2})   NIE2={NIE2:.3f} (true 0.0)')\n"
            "assert abs(NIE2) < 0.05,            'no M->Y means NIE ~ 0'\n"
            "assert abs(NDE2 - cprime2) < 0.05,  'direct effect = total here'\n"
            "print('OK — a mediator off the outcome path carries no indirect effect.')"},
        {"md": "## 2 · Sensitivity analysis — the E-value\n\n"
            "An observational estimate always assumes *no unmeasured confounding*. "
            "The **E-value** quantifies how strong an unmeasured confounder would "
            "have to be — associated with **both** treatment and outcome — to fully "
            "explain away an observed risk ratio.\n\n"
            "For an observed risk ratio `RR ≥ 1`:\n\n"
            "$$E = RR + \\sqrt{RR\\,(RR - 1)}$$\n\n"
            "(if `RR < 1`, apply the formula to `1/RR`). A bigger E-value means a "
            "more robust finding."},
        {"code": "def evalue_rr(rr):\n"
            "    \"\"\"E-value for an observed risk ratio (point estimate).\"\"\"\n"
            "    rr = rr if rr >= 1 else 1.0 / rr\n"
            "    return rr + np.sqrt(rr * (rr - 1.0))\n\n"
            "for rr in (1.0, 1.2, 2.0, 3.9):\n"
            "    print(f'RR = {rr:>3}  ->  E-value = {evalue_rr(rr):.2f}')\n\n"
            "# sanity: RR=1 (no effect) gives E=1; RR=3.9 is VanderWeele's classic ~7.26\n"
            "assert abs(evalue_rr(1.0) - 1.0) < 1e-9\n"
            "assert abs(evalue_rr(3.9) - 7.26) < 0.01\n"
            "print('OK — E-value formula matches known values.')"},
        {"md": "Now connect the E-value to a **simulated confounded estimate**. We "
            "build a binary world with a confounder `U` of known strength, compute "
            "the *crude* (confounded) risk ratio, and show its E-value tells us how "
            "strong a hidden `U` would need to be to produce it from nothing."},
        {"code": "# A confounded world: U raises both treatment T and outcome D.\n"
            "# The TRUE causal effect of T on D is zero (D does not depend on T).\n"
            "n = 50_000\n"
            "U  = RNG.binomial(1, 0.5, n)                       # hidden confounder\n"
            "T  = RNG.binomial(1, 0.2 + 0.6 * U)                # U -> T\n"
            "D  = RNG.binomial(1, 0.1 + 0.5 * U)                # U -> D, NOT T -> D\n\n"
            "p1 = D[T == 1].mean()      # crude risk in treated\n"
            "p0 = D[T == 0].mean()      # crude risk in untreated\n"
            "crude_rr = p1 / p0\n"
            "print(f'crude (confounded) RR = {crude_rr:.2f}  '\n"
            "      f'(true causal RR = 1.00)')\n"
            "print(f'E-value of the crude RR = {evalue_rr(crude_rr):.2f}')\n"
            "print('Reading: a confounder this strong on BOTH arms is exactly what U is.')"},
        {"md": "### 🔧 Exercise 2.1 — what E-value would you need?\n\n"
            "A colleague reports an adjusted risk ratio of **RR = 1.5** and calls "
            "it 'solid evidence.' Compute its E-value. Then decide: if every "
            "measured confounder in the field has associations no stronger than "
            "~1.4 with treatment and outcome, is this result robust?\n\n"
            "Fill in the `# TODO`."},
        {"code": "# TODO: compute the E-value for RR = 1.5 and compare to 1.4\n"
            "rr_obs = 1.5\n"
            "ev = ...                 # TODO: use evalue_rr\n"
            "# robust = ...           # TODO: is ev comfortably above 1.4?\n"
            "# print(ev, robust)"},
        {"md": "### ✅ Solution 2.1"},
        {"code": "rr_obs = 1.5\n"
            "ev = evalue_rr(rr_obs)\n"
            "robust = ev > 1.4\n"
            "print(f'E-value for RR={rr_obs}: {ev:.2f}')\n"
            "print(f'Above the ~1.4 ceiling of measured confounders? {robust}')\n"
            "assert abs(ev - (1.5 + np.sqrt(1.5 * 0.5))) < 1e-9\n"
            "print('A confounder of strength ~2.37 on both arms would be needed — '\n"
            "      'stronger than anything measured, so the finding is fairly robust\\n'\n"
            "      'but NOT immune: the margin over 1.4 is not huge.')"},
        {"md": "## 3 · g-formula — time-varying confounding\n\n"
            "The hardest idea of the week. Treatment is given at two times, `A0` "
            "then `A1`, with a covariate `L1` measured in between. The trap:\n\n"
            "- `A0 → L1`  (treatment moves the biomarker),\n"
            "- `L1 → A1`  (the clinician reacts to it),\n"
            "- `L1 → Y` and `A0, A1 → Y`.\n\n"
            "So `L1` is a **confounder of `A1`** and a **mediator of `A0`** at once. "
            "We compare the always-treat plan `(A0=A1=1)` to never-treat `(A0=A1=0)`; "
            "with these coefficients the **true** contrast is `1 + 1 + 1·(1−0) = 3`."},
        {"code": "n = 200_000\n"
            "A0 = RNG.binomial(1, 0.5, n)\n"
            "L1 = RNG.normal(1.0 * A0, 1.0)                     # A0 -> L1\n"
            "A1 = RNG.binomial(1, 1.0 / (1.0 + np.exp(-(L1 - 0.5))))  # L1 -> A1\n"
            "Y  = 1.0 * A0 + 1.0 * A1 + 1.0 * L1 + RNG.normal(size=n) # truth: 3\n"
            "TRUE = 3.0\n\n"
            "# --- ordinary regressions: both wrong ---\n"
            "adj = sm.OLS(Y, sm.add_constant(np.c_[A0, A1, L1])).fit().params\n"
            "omit = sm.OLS(Y, sm.add_constant(np.c_[A0, A1])).fit().params\n"
            "print(f'TRUE effect (always vs never)      : {TRUE:.2f}')\n"
            "print(f'regression ADJUSTING for L1 (A0+A1): {adj[1] + adj[2]:.2f}  '\n"
            "      f'(biased DOWN: blocks A0->L1->Y)')\n"
            "print(f'regression OMITTING  L1 (A0+A1)    : {omit[1] + omit[2]:.2f}  '\n"
            "      f'(biased UP: A1 left confounded)')"},
        {"md": "Neither regression is right — one over-controls `A0`, the other "
            "leaves `A1` confounded. The **g-formula** fixes this by "
            "*standardization*: model how `L1` responds to `A0`, model `Y` from the "
            "full history, then **simulate** each treatment plan and average."},
        {"code": "# g-formula by standardization (g-computation)\n"
            "pL = sm.OLS(L1, sm.add_constant(A0)).fit().params           # E[L1 | A0]\n"
            "pY = sm.OLS(Y,  sm.add_constant(np.c_[A0, A1, L1])).fit().params\n\n"
            "def g_mean(a0, a1):\n"
            "    L1_sim = pL[0] + pL[1] * a0          # simulate L1 under do(A0=a0)\n"
            "    return pY[0] + pY[1]*a0 + pY[2]*a1 + pY[3]*L1_sim\n\n"
            "g_effect = g_mean(1, 1) - g_mean(0, 0)\n"
            "print(f'g-formula (always vs never): {g_effect:.2f}   true: {TRUE:.2f}')\n"
            "assert abs(g_effect - TRUE) < 0.1,        'g-formula should recover ~3'\n"
            "assert abs((adj[1] + adj[2]) - TRUE) > 0.5, 'adjusting for L1 is biased'\n"
            "print('OK — the g-formula recovers the truth where regression cannot.')"},
        {"md": "### 🔧 Exercise 3.1 — turn off the feedback\n\n"
            "If `A0` did **not** affect `L1` (no `A0 → L1` arrow), then `L1` is an "
            "ordinary confounder and plain regression adjusting for `L1` should be "
            "fine. Re-simulate with `L1` independent of `A0` and confirm the "
            "adjusted regression now matches the g-formula.\n\n"
            "Fill in the `# TODO`s."},
        {"code": "# TODO: same world but break A0 -> L1 (make L1 not depend on A0)\n"
            "A0b = RNG.binomial(1, 0.5, n)\n"
            "L1b = ...        # TODO: RNG.normal(0.0, 1.0, n)  — no dependence on A0b\n"
            "# TODO: uncomment once L1b is real:\n"
            "# A1b = RNG.binomial(1, 1.0 / (1.0 + np.exp(-(L1b - 0.5))))\n"
            "# Yb  = 1.0 * A0b + 1.0 * A1b + 1.0 * L1b + RNG.normal(size=n)\n"
            "# now the true effect is just 1 + 1 = 2 (L1 no longer carries A0's effect)\n"
            "# adjb = ...     # OLS of Yb on [A0b, A1b, L1b]; params\n"
            "# print(adjb[1] + adjb[2])"},
        {"md": "### ✅ Solution 3.1"},
        {"code": "A0b = RNG.binomial(1, 0.5, n)\n"
            "L1b = RNG.normal(0.0, 1.0, n)                      # NO A0 -> L1 arrow\n"
            "A1b = RNG.binomial(1, 1.0 / (1.0 + np.exp(-(L1b - 0.5))))\n"
            "Yb  = 1.0 * A0b + 1.0 * A1b + 1.0 * L1b + RNG.normal(size=n)\n"
            "TRUE_b = 2.0                                       # 1 (A0) + 1 (A1)\n"
            "adjb = sm.OLS(Yb, sm.add_constant(np.c_[A0b, A1b, L1b])).fit().params\n"
            "print(f'adjusting for L1 now: {adjb[1] + adjb[2]:.2f}   true: {TRUE_b}')\n"
            "assert abs((adjb[1] + adjb[2]) - TRUE_b) < 0.1\n"
            "print('OK — with no treatment->confounder feedback, regression is fine.')\n"
            "print('That feedback arrow is the whole reason g-methods exist.')"},
        {"md": "## 4 · Causal discovery — a PC-style skeleton test\n\n"
            "Causal discovery learns graph structure from data. The first move of "
            "the **PC algorithm** is to delete an edge `X–Y` whenever `X` and `Y` "
            "are independent given some conditioning set. For continuous Gaussian "
            "data, a **partial correlation** is the conditional-independence test.\n\n"
            "We generate the chain `X → Y → Z`. The truth: `X` and `Z` are "
            "correlated *marginally* but **independent given `Y`** — so PC should "
            "remove the `X–Z` edge and keep the chain skeleton `X – Y – Z`."},
        {"code": "n = 4000\n"
            "Xc = RNG.normal(size=n)\n"
            "Yc = Xc + RNG.normal(size=n)         # X -> Y\n"
            "Zc = Yc + RNG.normal(size=n)         # Y -> Z   (chain)\n\n"
            "def pcorr(u, v, given=None):\n"
            "    \"\"\"(Partial) correlation of u and v, optionally given `given`.\"\"\"\n"
            "    if given is None:\n"
            "        return np.corrcoef(u, v)[0, 1]\n"
            "    W = sm.add_constant(given)\n"
            "    ru = u - W @ np.linalg.lstsq(W, u, rcond=None)[0]\n"
            "    rv = v - W @ np.linalg.lstsq(W, v, rcond=None)[0]\n"
            "    return np.corrcoef(ru, rv)[0, 1]\n\n"
            "print(f'corr(X, Z)        = {pcorr(Xc, Zc):+.3f}   (marginally linked)')\n"
            "print(f'corr(X, Z | Y)    = {pcorr(Xc, Zc, Yc):+.3f}   (vanishes -> drop edge)')\n"
            "print(f'corr(X, Y | Z)    = {pcorr(Xc, Yc, Zc):+.3f}   (stays -> keep edge)')\n"
            "print(f'corr(Y, Z | X)    = {pcorr(Yc, Zc, Xc):+.3f}   (stays -> keep edge)')"},
        {"code": "# Build the skeleton: keep an edge iff some test does NOT vanish.\n"
            "thr = 0.05\n"
            "edges = {}\n"
            "edges['X-Z'] = abs(pcorr(Xc, Zc, Yc)) > thr   # conditioned on Y\n"
            "edges['X-Y'] = abs(pcorr(Xc, Yc, Zc)) > thr   # conditioned on Z\n"
            "edges['Y-Z'] = abs(pcorr(Yc, Zc, Xc)) > thr   # conditioned on X\n"
            "kept = [e for e, keep in edges.items() if keep]\n"
            "print('skeleton edges kept:', kept)\n"
            "assert edges['X-Y'] and edges['Y-Z'] and not edges['X-Z'], \\\n"
            "    'PC should recover the chain skeleton X-Y-Z'\n"
            "print('OK — recovered the chain skeleton; the X-Z edge was correctly removed.')"},
        {"md": "**The limit, in one line.** The chain `X→Y→Z`, the reversed chain "
            "`X←Y←Z`, and the fork `X←Y→Z` all imply the *same* independence "
            "`X ⫫ Z | Y`. Observational data alone cannot tell them apart — they "
            "form one **Markov equivalence class**. PC returns the skeleton (and "
            "any colliders it can orient), not a unique DAG. Orienting the rest "
            "needs interventions, time order, or extra assumptions (the territory "
            "of GES and NOTEARS)."},
        {"md": "## 5 · Wrap-up & self-check\n\n"
            "- **Mediation** splits a total effect into NDE + NIE; the product "
            "method gives `NIE = a·b`, and the pieces sum to the total — *if* the "
            "mediator–outcome relationship is unconfounded.\n"
            "- **E-values** turn 'what about unmeasured confounding?' into a number: "
            "`E = RR + √(RR(RR−1))`. Bigger = more robust.\n"
            "- **g-formula**: when a confounder is affected by prior treatment, no "
            "single regression is right; standardize by simulating the "
            "intervention. You saw both regressions fail and the g-formula recover "
            "the truth.\n"
            "- **Causal discovery** (PC) recovers a skeleton and a Markov "
            "equivalence class — not a unique DAG — from independence tests alone.\n\n"
            "**You're ready for Week 15** if you can decompose a total effect, "
            "compute and read an E-value, explain why time-varying confounding "
            "defeats regression, and say what an equivalence class is. Next week: "
            "the capstone — assembling the full workflow, reproducibly, and "
            "communicating a causal claim honestly."},
    ],
}
