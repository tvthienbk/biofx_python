#!/usr/bin/env python3
"""Build the **Instructor Teaching Guide** (.docx) for the 15-week graduate
seminar *Causal Inference in Practice*.

This is a NEW, standalone deliverable. It does NOT modify any existing course
file: it only READS the per-week content modules (to keep the per-week sections
faithful to what the packets/decks actually teach) and reuses the shared course
look from ``coursegen.packet`` so the guide matches the rest of the course.

Run:
    python build_teaching_guide.py

Output:
    ../Assessments/Instructor_Teaching_Guide.docx
"""
from __future__ import annotations

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # Causal_Inference_Course/
sys.path.insert(0, HERE)

from coursegen import packet as P                 # noqa: E402
from coursegen import theme                       # noqa: E402
from docx import Document                         # noqa: E402

OUT_PATH = os.path.join(ROOT, "Assessments", "Instructor_Teaching_Guide.docx")


# ---------------------------------------------------------------------------
# Pull a few facts from the real content modules so the guide stays honest
# about titles / blocks / deliverables. Week 12 has no module yet, so we carry
# a hand-written stub for it (Double/Debiased ML).
# ---------------------------------------------------------------------------

def load_week_facts() -> dict[int, dict]:
    facts: dict[int, dict] = {}
    for n in range(1, 16):
        try:
            mod = importlib.import_module(f"coursegen.content.week{n:02d}")
        except ModuleNotFoundError:
            continue
        w = mod.WEEK
        ps = w.get("problem_set", {})
        lab = w.get("lab", {})
        facts[n] = {
            "title": w.get("title", ""),
            "block": w.get("block", ""),
            "subtitle": w.get("subtitle", ""),
            "one_sentence": w.get("one_sentence", ""),
            "ps_label": ps.get("label", ""),
            "lab_label": lab.get("label", ""),
            "lab_title": lab.get("title", ""),
        }
    return facts


WEEK_FACTS = load_week_facts()


def fact(n: int, key: str, default: str = "") -> str:
    return WEEK_FACTS.get(n, {}).get(key, default)


# ---------------------------------------------------------------------------
# A light heading helper for the document title page (the packet banner is
# week-shaped, so we draw a course-level banner inline using the same styling).
# ---------------------------------------------------------------------------

def guide_banner(doc, line1, title, tagline):
    from docx.shared import Pt
    p = doc.add_paragraph()
    P._no_space(p)
    P._runs(p, line1, size=11, color=theme.BLUE, bold=True)
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(2)
    h.paragraph_format.space_after = Pt(2)
    P._runs(h, title, size=24, color=theme.NAVY, bold=True, font=theme.FONT_HEAD)
    rule = doc.add_paragraph()
    P._no_space(rule)
    P._add_border(rule, theme.AMBER, size=24, where=("bottom",))
    P.body(doc, tagline, italic=True)


# ---------------------------------------------------------------------------
# Per-week teaching content. Each entry mirrors the assignment brief:
#   point        -> the one-sentence point
#   musts        -> 2-3 ideas students MUST leave with
#   stumbles     -> common misconceptions / where students stumble
#   prompts      -> 2-3 discussion prompts
#   slow_down    -> which lecture moments to slow down on
#   grading      -> grading-effort estimate for the deliverable
#   cut_keep     -> "if short on time, cut/keep" note
# The deliverable line is assembled from the real module labels at render time.
# ---------------------------------------------------------------------------

TEACHING = {
1: {
    "point": "Prediction answers 'what goes with what'; causal inference answers "
             "'what happens if we intervene' — and confounding, reverse causation, "
             "and selection are what pry the two apart.",
    "musts": [
        "P(Y | do(X)) is a different object from P(Y | X); the do-operator means "
        "'set X', not 'observe X'.",
        "A third variable is a confounder, a collider, or a mediator — and the "
        "label, not the data, decides whether you adjust for it.",
        "Adjusting for a confounder removes bias; adjusting for a collider or "
        "mediator manufactures it.",
    ],
    "stumbles": [
        "Students reflexively 'control for everything available' — the habit this "
        "whole course exists to break. Plant the flag here.",
        "Collider bias is the least intuitive of the three; the hospitalized-"
        "patients example lands better than an abstract DAG.",
        "Some arrive expecting a coding course and underweight the conceptual "
        "vocabulary — stress that the vocabulary is the deliverable.",
    ],
    "prompts": [
        "Name a prediction your phone makes daily that would be useless as an "
        "intervention. Why does it still work as a prediction?",
        "Give a real headline where reverse causation is the more plausible story "
        "than the one reported.",
        "When could adjusting for MORE variables make an estimate worse?",
    ],
    "slow_down": [
        "The do-operator vs. conditioning distinction — write both expressions on "
        "the board and intervene on the same toy graph.",
        "The collider example: walk the open path that conditioning OPENS, slowly.",
    ],
    "grading": "Light. PS1 is conceptual classification (confounder/collider/"
               "mediator) — answers are short and largely right/wrong; ~5 min/student. "
               "Lab 0 is pass/fail: does the repo exist, is there a first commit, does "
               "the confounded-vs-adjusted estimate run? ~3 min/student.",
    "cut_keep": "KEEP the three-structures taxonomy and the do vs. conditioning "
                "split — everything downstream leans on them. CUT the longer history-"
                "of-the-field digression if time is tight.",
},
2: {
    "point": "Every causal claim is a statement about the unobservable pair Y(1), "
             "Y(0); an effect is identified only when stated assumptions let an "
             "observed comparison stand in for the missing counterfactual.",
    "musts": [
        "The fundamental problem of causal inference: you never see both potential "
        "outcomes for the same unit.",
        "State the estimand FIRST (ATE / ATT / CATE) — it fixes 'for whom' before "
        "any estimation begins.",
        "SUTVA, consistency, conditional exchangeability, and positivity are the "
        "four assumptions, and each one is used at a specific step.",
    ],
    "stumbles": [
        "Students conflate identification (an assumptions problem) with estimation "
        "(a data/variance problem) — separate them explicitly and keep them "
        "separate all term.",
        "Positivity feels like a technicality until they see a subgroup with zero "
        "treated units; use that picture.",
        "ATT vs. ATE is treated as interchangeable; force them to say which one a "
        "given question actually asks.",
    ],
    "prompts": [
        "Pick a policy you care about and write its effect in Y(1)/Y(0) notation. "
        "Which estimand does the decision-maker actually need?",
        "Which of the four assumptions is hardest to defend for an observational "
        "study you have read?",
        "Why does randomization buy exchangeability 'for free'?",
    ],
    "slow_down": [
        "The science-table picture (rows = units, two potential-outcome columns, "
        "one always missing) — this single image anchors the whole course.",
        "Walking each assumption to the exact line of an estimator where it is "
        "invoked.",
    ],
    "grading": "Moderate. PS2 asks students to name specific violations, not just "
               "label them — partial credit means reading reasoning, ~8 min/student. "
               "Workshop 2 is checkable against a known true ATE, so grading is fast "
               "if you spot-check the recovered number.",
    "cut_keep": "KEEP 'state the estimand first' and the four assumptions — they are "
                "the backbone of Weeks 5-8. CUT the finite- vs. super-population "
                "variance aside unless your cohort is theory-strong.",
},
3: {
    "point": "Random assignment turns a difference in means into a causal effect; at "
             "scale, power, variance, compliance, interference, and peeking decide "
             "whether you can actually trust the number.",
    "musts": [
        "Randomization makes treatment independent of the potential outcomes — "
        "that independence, not the sample size, is what licenses causality.",
        "Sample size follows from baseline rate, minimum detectable effect, and "
        "target power; variance reduction (CUPED) buys precision for free.",
        "ITT and per-protocol answer different questions under noncompliance; "
        "peeking, SRM, and interference are the real-world failure modes.",
    ],
    "stumbles": [
        "Students treat a non-significant test as 'no effect' rather than 'under-"
        "powered' — tie this back to MDE.",
        "Peeking feels harmless ('I just looked early'); the simulated false-"
        "positive inflation is the moment that convinces them.",
        "ITT vs. per-protocol confusion: per-protocol feels 'more honest' but "
        "reintroduces confounding. Make that explicit.",
    ],
    "prompts": [
        "Your test is flat after a week. List three reasons before concluding 'no "
        "effect'.",
        "When is per-protocol the WRONG analysis even though everyone in it "
        "actually took the treatment?",
        "Give a product feature whose A/B test would violate SUTVA through "
        "interference.",
    ],
    "slow_down": [
        "The power / MDE / sample-size triangle — derive one, then verify by "
        "simulation so they see the formula and the experiment agree.",
        "The peeking simulation: run it live if you can; the inflated false-positive "
        "rate is the lesson.",
    ],
    "grading": "Moderate-to-heavy. Lab 1 is the first full end-to-end build (size, "
               "simulate, estimate, CUPED, ITT vs PP). Budget ~12-15 min/student; a "
               "rubric over the five stages keeps it tractable.",
    "cut_keep": "KEEP power/MDE and the peeking demo. CUT the deeper sequential-"
                "testing / always-valid-inference material to a pointer for the "
                "capstone if pressed for time.",
},
4: {
    "point": "A DAG turns assumptions into a picture you can read: three local "
             "shapes (chain, fork, collider) decide whether a path carries "
             "association, and d-separation tells you mechanically what to adjust for.",
    "musts": [
        "The graph IS the assumption set — drawing it commits you to a testable "
        "story.",
        "Chain / fork / collider behave oppositely under conditioning; the "
        "collider is the one that OPENS when you condition.",
        "The back-door criterion finds a valid (and minimal) adjustment set; the "
        "front-door identifies through a mediator when back doors are all blocked.",
    ],
    "stumbles": [
        "The collider rule reversal is THE sticking point of the week — that "
        "conditioning on a collider opens rather than closes a path.",
        "Students hunt for the 'biggest' adjustment set; push them toward minimal, "
        "sufficient sets.",
        "The front-door criterion feels like magic; ground it in the explicit "
        "mediator example before the algebra.",
    ],
    "prompts": [
        "Draw the DAG for a claim in your own field. Which edge are you least sure "
        "about, and what would it take to test it?",
        "Construct a graph where adjusting for a variable HELPS on one path and "
        "HURTS on another.",
        "What conditional independence would falsify your DAG, and do you have the "
        "data to check it?",
    ],
    "slow_down": [
        "d-separation worked on one path at a time — narrate 'open' / 'blocked' for "
        "each segment out loud.",
        "Conditioning on a collider: animate the path opening; this is the moment "
        "that pays off all term.",
    ],
    "grading": "Moderate. PS3 (d-separation & adjustment sets) is mechanical once "
               "understood, so grading is mostly checking the path enumeration and the "
               "minimal set; ~8 min/student. Lab 2 is verifiable by the independence "
               "test it runs.",
    "cut_keep": "KEEP back-door + collider rule. CUT or assign-as-reading the full "
                "front-door derivation and the testable-implications section if the "
                "cohort is struggling with d-separation itself.",
},
5: {
    "point": "OLS recovers a causal effect only when you condition on the right "
             "covariate set — and 'the right set' is dictated by the graph, because "
             "adjusting for a mediator or collider manufactures bias.",
    "musts": [
        "Regression is a covariate-adjusted, weighted-average comparison — not a "
        "magic causal machine.",
        "Good controls (confounders) remove bias; bad controls (mediators, "
        "colliders, M-bias traps) add it. Improving fit is NOT the criterion.",
        "The Table 2 fallacy: a coefficient on a covariate is not, in general, that "
        "covariate's own causal effect.",
    ],
    "stumbles": [
        "'But it raised my R-squared / lowered my p-value' — students keep using "
        "fit as a control-selection rule. Confront it head-on.",
        "Every coefficient in the table gets a causal reading (Table 2 fallacy); "
        "the birth-weight paradox makes the danger concrete.",
        "Mediators feel like 'good controls' because they are pre-outcome and "
        "predictive — clarify why adjusting for them is wrong for the total effect.",
    ],
    "prompts": [
        "You add a control and the treatment coefficient moves a lot. Name two "
        "graph structures that would each produce that, with opposite implications.",
        "Take a published regression table — which coefficients can be read "
        "causally, and which fall to the Table 2 fallacy?",
        "When is a neutral control (pure outcome predictor) worth adding anyway?",
    ],
    "slow_down": [
        "The good-control / bad-control catalog tied to a single DAG, one case at a "
        "time.",
        "The Table 2 fallacy demonstration on a single fitted model.",
    ],
    "grading": "Moderate. PS4 is a classification grid (good/bad/collider/neutral/"
               "M-bias) with justifications — read the reasoning, ~8 min/student. "
               "Workshop 5 compares each estimate to a known truth, so it self-checks.",
    "cut_keep": "KEEP good-vs-bad controls and Table 2. CUT the CEF formalism to a "
                "footnote if your students are not coming from an econometrics "
                "background.",
},
6: {
    "point": "Matching and the propensity score recover a randomized comparison "
             "from observational data by making treated and control groups share a "
             "covariate distribution within the analysis sample.",
    "musts": [
        "The propensity score e(X)=P(D=1|X) is a balancing score: conditioning on "
        "that one number removes covariate-induced confounding.",
        "Balance is the thing you check (SMD, love-plot) — model fit of the "
        "propensity score is not the goal.",
        "Common support / overlap determines who you can compare; trimming changes "
        "the estimand.",
    ],
    "stumbles": [
        "Students chase a high-AUC propensity model; remind them the score is a "
        "means to balance, and a perfectly predictive score destroys overlap.",
        "They report naive post-matching standard errors; flag that matching "
        "induces dependence the naive SE ignores.",
        "ATT vs ATE under matching gets blurred — matching on treated units "
        "targets the ATT by construction.",
    ],
    "prompts": [
        "Your propensity model has near-perfect AUC. Is that good news? What does "
        "it imply about overlap?",
        "After trimming non-overlapping units, whose effect are you now "
        "estimating, and to whom does it generalize?",
        "Two matched analyses report the same point estimate but different SEs — "
        "what could explain it?",
    ],
    "slow_down": [
        "The balancing-score argument: why one scalar can substitute for the whole "
        "covariate vector.",
        "Reading a love-plot — before/after SMDs — as the diagnostic that earns the "
        "design.",
    ],
    "grading": "Moderate. Concept Set 6 is short-answer conceptual. Lab 3 (estimate "
               "PS, match, check balance, report ATT) is the graded centerpiece — "
               "~12 min/student; require the love-plot as evidence.",
    "cut_keep": "KEEP balancing score + balance diagnostics + ATT. CUT coarsened "
                "exact matching to a brief mention if you must compress.",
},
7: {
    "point": "Inverse-probability weighting rebuilds a pseudo-population where "
             "treatment is unconfounded; augmenting it with an outcome model gives "
             "the doubly robust estimator — you only need to win ONE of two bets.",
    "musts": [
        "A weight is 1 / P(observed treatment | X); weighting creates a pseudo-"
        "population in which treatment is independent of measured confounders.",
        "Stabilized (Hajek) weights and truncation tame extreme weights, which are "
        "a symptom of near-positivity violations.",
        "The doubly robust / AIPW estimator stays consistent if EITHER the "
        "propensity model OR the outcome model is correct.",
    ],
    "stumbles": [
        "Extreme weights are seen as a nuisance to be clipped, not a warning about "
        "positivity — make the diagnosis, not just the fix.",
        "'Doubly robust = twice as accurate' is a misread; it is a robustness "
        "property (one-of-two), not a precision boost.",
        "Truncation feels like cheating; frame it explicitly as trading a little "
        "bias for a lot of variance.",
    ],
    "prompts": [
        "Your weights range up to 400. What is that telling you about your data, "
        "before you reach for truncation?",
        "Construct a scenario where the propensity model is wrong but AIPW still "
        "recovers the truth — which model is carrying you?",
        "When would you rather redefine the estimand than truncate weights?",
    ],
    "slow_down": [
        "The pseudo-population picture: show the reweighted sample and why it is "
        "balanced.",
        "The AIPW double-robustness demo — break one model at a time and watch the "
        "estimate hold.",
    ],
    "grading": "Moderate-to-heavy. PS5 includes a derivation (IPW estimator) and a "
               "which-model-may-be-wrong argument — read carefully, ~10 min/student. "
               "Lab 4 (IPW then AIPW) self-checks against the known effect.",
    "cut_keep": "KEEP IPW intuition + double robustness (this is the capstone of "
                "Block II and shows up again in DML). CUT the marginal-structural-"
                "model framing to a forward pointer if time-pressed.",
},
8: {
    "point": "An instrument moves treatment but reaches the outcome only through "
             "treatment; if that holds, it identifies an effect even with an "
             "unmeasured confounder — but only for the compliers it actually moves.",
    "musts": [
        "The four IV assumptions — relevance, exclusion, independence, monotonicity "
        "— and which ones the data can and cannot test.",
        "2SLS is literally two OLS regressions; the fitted first stage strips out "
        "the confounding.",
        "IV identifies the LATE (the compliers' effect), which can differ from the "
        "ATE or ATT; weak instruments bias IV toward OLS.",
    ],
    "stumbles": [
        "Students believe the exclusion restriction can be 'tested' — stress it is "
        "an assumption defended by argument, not a statistic.",
        "LATE is read as 'the effect' rather than 'the compliers' effect'; keep "
        "naming whose effect it is.",
        "Weak instruments are underestimated — the first-stage F is treated as a "
        "formality until they see the variance blow up.",
    ],
    "prompts": [
        "Propose an instrument from your field. Argue the exclusion restriction — "
        "and then argue against yourself.",
        "Why can two valid instruments for the same treatment give different LATEs, "
        "and is that a contradiction?",
        "In Mendelian randomization, how exactly does pleiotropy threaten "
        "exclusion?",
    ],
    "slow_down": [
        "Exclusion vs. independence — students routinely merge them; separate with "
        "a graph.",
        "Building 2SLS by hand so the 'fitted first stage = as-good-as-random part "
        "of treatment' clicks.",
    ],
    "grading": "Heavy week — it carries the MIDTERM (Weeks 1-7) plus Lab 5. Budget "
               "midterm grading separately (plan a rubric and possibly a TA pass). "
               "Lab 5 (2SLS + MR pleiotropy check) is ~12 min/student.",
    "cut_keep": "KEEP the four assumptions, 2SLS-by-hand, and LATE. CUT MR-Egger "
                "details to a demonstration-only if the midterm has eaten the week.",
},
9: {
    "point": "When a known cutoff on a running variable decides treatment, units "
             "just above and below are comparable, so the jump at the cutoff is a "
             "local causal effect — if nothing else jumps and no one can manipulate "
             "their side.",
    "musts": [
        "Sharp RD (deterministic step) vs. fuzzy RD (probability shift) identify "
        "different things; both estimate a LOCAL effect at the cutoff.",
        "The continuity assumption and the local-randomization intuition are what "
        "license the design.",
        "Validity checks earn the design: McCrary density (manipulation), placebo "
        "cutoffs, donut-hole, and a defensible bandwidth.",
    ],
    "stumbles": [
        "RD's effect is read as global rather than LOCAL to the cutoff — keep "
        "saying 'at the cutoff'.",
        "Bandwidth choice is treated as arbitrary; frame it as an explicit bias-"
        "variance tradeoff and require a sweep.",
        "Students forget the manipulation check — without the density test the "
        "design is just an assertion.",
    ],
    "prompts": [
        "A scholarship is awarded at a test-score cutoff. What would make you "
        "suspect manipulation, and how would you detect it?",
        "Your estimate halves when you widen the bandwidth. Which number do you "
        "report, and why?",
        "To whom does an RD estimate generalize — and to whom does it NOT?",
    ],
    "slow_down": [
        "The local-randomization intuition: why being just above vs. just below is "
        "almost a coin flip.",
        "The fuzzy-RD Wald ratio (reduced form over first stage) — connect it back "
        "to Week 8 IV.",
    ],
    "grading": "Moderate. No problem set is graded separately this week beyond the "
               "concept set; Lab 6 is the deliverable (sharp RD + full validity "
               "suite, then fuzzy). ~12 min/student; check that the validity battery "
               "is actually run, not just the point estimate.",
    "cut_keep": "KEEP sharp RD + the validity battery (it is the whole credibility "
                "argument). CUT the fuzzy-RD extension to optional if behind.",
},
10: {
    "point": "Difference-in-differences compares the treated group's before/after "
             "change to an untreated group's, so any common trend cancels — leaving "
             "the effect under a parallel-trends assumption.",
    "musts": [
        "The second difference removes both fixed group gaps and the common time "
        "trend; that cancellation IS the method.",
        "Parallel trends is the whole identifying assumption; a pre-trend test is "
        "suggestive evidence, not proof.",
        "Two-way fixed effects with staggered adoption and heterogeneous effects "
        "can be biased ('forbidden comparisons', negative weights).",
    ],
    "stumbles": [
        "A passing pre-trend test is taken as proof of parallel trends — it "
        "concerns the unobservable counterfactual trend and cannot be verified.",
        "Students assume TWFE 'just works' for staggered timing; the negative-"
        "weights result genuinely surprises them.",
        "Clustering is skipped; explain why standard errors must cluster at the "
        "unit.",
    ],
    "prompts": [
        "Your pre-trends are flat. Name something that could still break parallel "
        "trends in the post-period.",
        "Why can adding more treated cohorts at different times make a TWFE "
        "estimate WORSE, not better?",
        "Read this event-study plot aloud: what do the leads tell you and what do "
        "the lags tell you?",
    ],
    "slow_down": [
        "The 2x2 table by hand before any regression — make the double difference "
        "concrete.",
        "Why TWFE breaks under staggered adoption: the forbidden already-treated-as-"
        "control comparison.",
    ],
    "grading": "Moderate-to-heavy. PS6 plus Lab 7 (2x2, TWFE with clustering, event "
               "study, staggered-bias demo, group-time fix) is a substantial build — "
               "~15 min/student. A staged rubric helps.",
    "cut_keep": "KEEP 2x2 + parallel trends + event study. CUT the modern group-time "
                "estimator (Callaway-Sant'Anna style) to a demo if time is short, but "
                "keep the negative-weights warning.",
},
11: {
    "point": "With one treated unit and a pool of untreated donors, synthetic "
             "control builds a weighted donor blend that tracks the treated unit "
             "pre-treatment and uses its continuation as the counterfactual.",
    "musts": [
        "Donor weights are non-negative and sum to one (a convex combination) — no "
        "extrapolation outside the donors' hull.",
        "Pre-treatment fit is the whole argument: a good pre-period match is the "
        "precondition that makes the post-period gap interpretable.",
        "Placebo / permutation (in-space) inference puts the real unit's gap inside "
        "a distribution of donor-as-treated gaps.",
    ],
    "stumbles": [
        "Students read a post-period gap as an effect even with poor pre-fit — no "
        "pre-fit, no claim.",
        "Negative or >1 weights creep in from an unconstrained solver; emphasize "
        "the convexity constraint and why it matters.",
        "They expect classical p-values; the permutation logic of inference here is "
        "new and worth dwelling on.",
    ],
    "prompts": [
        "When is synthetic control clearly better than DiD, and when is it clearly "
        "worse?",
        "Your treated unit sits outside the donors' convex hull. What does that do "
        "to the method, and what should you do about it?",
        "How does in-space placebo inference substitute for a large sample?",
    ],
    "slow_down": [
        "The constrained-weights optimization (non-negative, sum-to-one) and WHY "
        "those constraints exist.",
        "Reading a placebo / permutation plot to get a p-value.",
    ],
    "grading": "Moderate. Concept Set 11 is short-answer; Lab 8 (code SC from "
               "scratch + in-space placebo) is the deliverable, ~12 min/student. The "
               "permutation p-value is the thing to verify.",
    "cut_keep": "KEEP convex weights + pre-fit + placebo inference. CUT a deep dive "
                "into the matrix-completion / generalized-SC variants unless the "
                "cohort is strong.",
},
12: {
    "point": "Double/debiased ML lets you use flexible learners for the nuisance "
             "functions while still getting a valid, root-n confidence interval for "
             "the treatment effect — by combining Neyman-orthogonal scores with "
             "cross-fitting.",
    "musts": [
        "Neyman orthogonality: build a score whose error is first-order insensitive "
        "to small nuisance-estimation mistakes, so ML bias does not contaminate the "
        "effect.",
        "Cross-fitting (sample splitting) removes the overfitting bias of using the "
        "same data to fit nuisances and the effect.",
        "In the partially linear model, DML estimates the ATE by partialling out "
        "X from both treatment and outcome with ML, then regressing the residuals.",
    ],
    "stumbles": [
        "Students think 'use a fancier model' is the whole idea — the orthogonal "
        "moment and cross-fitting are what make it valid, not the ML.",
        "Plugging ML predictions into a naive estimator (no orthogonalization, no "
        "cross-fit) and trusting the SE — show why that interval is wrong.",
        "Regularization bias is invisible until you contrast naive plug-in with the "
        "orthogonalized residual-on-residual fit.",
    ],
    "prompts": [
        "Why does a great predictive model NOT automatically give a good treatment-"
        "effect estimate?",
        "What exactly does cross-fitting protect you from, and why can't you just "
        "use all the data twice?",
        "Where does the doubly robust / AIPW score from Week 7 reappear inside DML?",
    ],
    "slow_down": [
        "The residual-on-residual (Frisch-Waugh) picture of the partially linear "
        "model — it makes orthogonality tangible.",
        "Cross-fitting mechanics: fit nuisances on fold A, score on fold B, swap, "
        "average.",
    ],
    "grading": "Moderate. (Note: this week's content module may still be in "
               "progress.) If a lab ships, expect it to mirror the AIPW lab in effort "
               "(~12 min/student); the partialling-out estimate self-checks against a "
               "known ATE.",
    "cut_keep": "KEEP orthogonality + cross-fitting + the partially linear ATE. CUT "
                "the heterogeneous-effect DML (DML for CATE) since Week 13 covers "
                "heterogeneity directly.",
},
13: {
    "point": "The ATE can hide huge variation; this week estimates the conditional "
             "effect tau(x) with meta-learners and causal forests, evaluates it "
             "without ground truth, and turns it into a targeting policy.",
    "musts": [
        "CATE tau(x)=E[Y(1)-Y(0)|X=x] differs from the ATE; an ATE of zero is "
        "compatible with large, offsetting individual effects.",
        "Meta-learners (S/T/X/R) build CATE from off-the-shelf regressors; the "
        "X-learner helps under imbalanced treatment groups.",
        "Evaluate CATE WITHOUT ground truth via calibration and uplift/Qini "
        "curves; then turn tau-hat into a policy pi(x)=1{tau-hat(x)>c} and value it.",
    ],
    "stumbles": [
        "Naive subgroup-hunting (slice until something is significant) overfits — "
        "the canonical sin this week inoculates against.",
        "Students want an accuracy metric for CATE but have no per-unit ground "
        "truth; the move to calibration/uplift is the key mental shift.",
        "A policy that 'treats the high-tau group' is assumed optimal without "
        "comparing to treat-all / treat-none baselines.",
    ],
    "prompts": [
        "Your ATE is zero. Argue for still running the program, using CATE.",
        "Without ground-truth individual effects, how would you convince a skeptic "
        "your CATE model is any good?",
        "When is a 'treat everyone' policy actually the right call despite "
        "heterogeneity?",
    ],
    "slow_down": [
        "Why you cannot score a CATE model the way you score a classifier — and "
        "what uplift/Qini curves do instead.",
        "Honest splitting in causal forests and why it buys valid intervals.",
    ],
    "grading": "Moderate-to-heavy. PS7 plus Lab 10 (meta-learners, uplift curves, "
               "an optimal rule) with a known tau(x) — self-checking but multi-part; "
               "~15 min/student.",
    "cut_keep": "KEEP CATE-vs-ATE, one meta-learner end-to-end, and policy value. "
                "CUT the full S/T/X/R comparison to a table if you only have time for "
                "one learner.",
},
14: {
    "point": "Four questions modern causal inference takes seriously: how an effect "
             "flows through a mediator, how fragile it is to unmeasured confounding, "
             "how to handle time-varying treatment, and how to learn structure.",
    "musts": [
        "A total effect splits into a natural direct (NDE) and natural indirect "
        "(NIE) effect — under assumptions stronger than for a total effect.",
        "An E-value says how strong an unmeasured confounder must be to explain a "
        "result away — a plain-language fragility statement.",
        "When a confounder is itself affected by prior treatment, ordinary "
        "regression fails and the g-formula repairs it by standardization; "
        "discovery (PC/GES) recovers only an equivalence class.",
    ],
    "stumbles": [
        "Mediation assumptions are heavier than students expect; resist treating "
        "NDE/NIE as 'just two more regressions'.",
        "The E-value is misread as a p-value; it answers 'how strong a confounder', "
        "not 'how surprising the data'.",
        "Causal discovery is oversold by students as 'learning the true DAG' — "
        "stress the Markov-equivalence-class ceiling.",
    ],
    "prompts": [
        "For a finding you trust, compute (roughly) the E-value. Does a confounder "
        "that strong plausibly exist?",
        "Give a time-varying-treatment story where adjusting for the intermediate "
        "confounder is exactly the wrong move.",
        "If discovery only returns an equivalence class, what extra knowledge "
        "breaks the tie?",
    ],
    "slow_down": [
        "Why an intermediate confounder affected by prior treatment defeats "
        "regression — draw the time-indexed DAG.",
        "Reading an E-value as a sensitivity statement, not a significance test.",
    ],
    "grading": "Moderate but broad. PS8 and Workshop 14 each span four mini-topics; "
               "grade for one-correct-idea-per-topic rather than depth. ~12 min/"
               "student. This is a survey week — calibrate expectations accordingly.",
    "cut_keep": "KEEP E-values (cheap, high-leverage for the capstone) and the "
                "g-formula intuition. CUT or skim NOTEARS / detailed discovery if you "
                "need to protect capstone-prep time.",
},
15: {
    "point": "A causal claim is only as good as the design that earns it, the "
             "assumptions stated out loud, the robustness checks that fail to "
             "overturn it, and the honest sentence you can tell a decision-maker.",
    "musts": [
        "Let the question and the data choose the design (RCT/matching/IV/RD/DiD/SC/"
        "DML), and justify it against the alternatives.",
        "A pre-analysis plan closes the garden of forking paths before you touch "
        "the outcome; robustness/multiverse + sensitivity report what would "
        "overturn the result.",
        "Reproducibility (one command, fixed seed, logged environment) and honest "
        "three-sentence communication are deliverables, not afterthoughts.",
    ],
    "stumbles": [
        "Students reach for the fanciest method instead of the one the data "
        "actually supports — reward fit-to-question over sophistication.",
        "Pre-analysis plans get written AFTER peeking at outcomes; enforce timing.",
        "Communication over- or under-claims; drill the three-honest-sentences "
        "format.",
    ],
    "prompts": [
        "Pitch your capstone design in 60 seconds, then name the single assumption "
        "most likely to sink it.",
        "What result, if you saw it, would force you to retract your headline "
        "finding?",
        "State your effect and its uncertainty to a non-technical stakeholder in "
        "exactly three sentences.",
    ],
    "slow_down": [
        "The design-selection decision (which method, given which data) — workshop "
        "it live on students' own projects.",
        "The reproducible-pipeline demo: one command rebuilds the whole report.",
    ],
    "grading": "Heaviest of the term — the CAPSTONE (30%) is report + presentation. "
               "Budget 30-45 min/student across the written report, the pipeline "
               "reproducibility check (clone and run one command), and the talk. Use a "
               "published rubric and reserve a grading window.",
    "cut_keep": "KEEP design justification, the pre-analysis plan, and the "
                "reproducibility check. Nothing here is safe to cut — instead, move "
                "robustness/multiverse depth into the rubric weighting.",
},
}


# ---------------------------------------------------------------------------
# Glossary (~25 terms)
# ---------------------------------------------------------------------------

GLOSSARY = [
    ("do-operator do(X)=x", "An intervention that SETS X to x, severing X's incoming "
     "causes. P(Y|do(X)) (what happens if we intervene) differs from P(Y|X) (what we "
     "observe) whenever confounding is present. Introduced Week 1.", 1),
    ("Confounder", "A common cause of treatment and outcome; an open back-door path. "
     "You SHOULD adjust for it. Weeks 1, 4, 5.", 1),
    ("Collider", "A common effect of two variables. Conditioning on it OPENS a "
     "spurious path — so you should NOT adjust for it (selection/M-bias). Weeks 1, 4.", 4),
    ("Mediator", "A variable on the causal path from treatment to outcome. Adjusting "
     "for it blocks the indirect effect and biases the TOTAL effect. Weeks 1, 5, 14.", 1),
    ("SUTVA", "Stable Unit Treatment Value Assumption: one unit's outcome is "
     "unaffected by others' treatment (no interference) and there is a single version "
     "of treatment. Week 2; violated by interference, Week 3.", 2),
    ("Consistency", "The observed outcome under the treatment actually received equals "
     "that unit's potential outcome for that treatment. Needs a well-defined "
     "intervention. Week 2.", 2),
    ("Exchangeability", "(Conditional) independence of treatment and the potential "
     "outcomes given covariates: no unmeasured confounding. Randomization buys it "
     "unconditionally. Week 2.", 2),
    ("Positivity / overlap", "Every covariate stratum has a nonzero probability of "
     "each treatment, so comparisons exist. Near-violations show up as extreme "
     "weights. Weeks 2, 6, 7.", 2),
    ("ATE", "Average Treatment Effect, E[Y(1)-Y(0)] over the whole population. Week 2.", 2),
    ("ATT", "Average Treatment effect on the Treated, E[Y(1)-Y(0)|D=1]. The natural "
     "target of matching. Weeks 2, 6.", 2),
    ("CATE", "Conditional Average Treatment Effect tau(x)=E[Y(1)-Y(0)|X=x] — the "
     "effect 'for whom'. Weeks 2, 13.", 13),
    ("LATE", "Local Average Treatment Effect: the effect for COMPLIERS — units an "
     "instrument actually moves. What IV (and fuzzy RD) identify. Weeks 8, 9.", 8),
    ("Propensity score e(X)", "P(D=1|X), the probability of treatment given "
     "covariates. A balancing score: conditioning on it removes covariate-induced "
     "confounding. Weeks 6, 7.", 6),
    ("IPW", "Inverse-Probability Weighting: weight units by 1/P(observed treatment|X) "
     "to build a pseudo-population in which treatment is unconfounded. Week 7.", 7),
    ("Doubly robust (AIPW)", "An estimator combining a propensity model and an outcome "
     "model that is consistent if EITHER one is correct. Weeks 7, 12.", 7),
    ("Instrument", "A variable that moves treatment but affects the outcome only "
     "through treatment, even under unmeasured confounding. Week 8.", 8),
    ("Exclusion restriction", "The IV assumption that the instrument affects the "
     "outcome ONLY through treatment. Untestable; defended by argument. Threatened by "
     "pleiotropy in MR. Week 8.", 8),
    ("Compliers", "Units whose treatment status responds to the instrument (under "
     "monotonicity). LATE is their effect. Week 8.", 8),
    ("Regression discontinuity (RD)", "A design where treatment switches at a cutoff "
     "on a running variable; the jump in the outcome at the cutoff is a LOCAL effect. "
     "Week 9.", 9),
    ("Parallel trends", "The DiD identifying assumption: absent treatment, treated and "
     "control groups would have moved on the same trend. Untestable for the "
     "counterfactual; pre-trends are only suggestive. Week 10.", 10),
    ("TWFE", "Two-Way Fixed Effects regression (unit + time dummies). Equivalent to "
     "DiD in the 2x2 case but biased under staggered adoption with heterogeneous "
     "effects (negative weights). Week 10.", 10),
    ("Synthetic control", "A weighted (convex) blend of untreated donor units chosen "
     "to match a single treated unit's pre-treatment path; its continuation is the "
     "counterfactual. Week 11.", 11),
    ("Neyman orthogonality", "A score whose estimating equation is first-order "
     "insensitive to small nuisance-estimation errors, so ML/regularization bias does "
     "not leak into the effect estimate. Week 12.", 12),
    ("Cross-fitting", "Sample-splitting in DML: estimate nuisance functions on one "
     "fold and the effect on another (then swap and average) to remove overfitting "
     "bias. Week 12.", 12),
    ("E-value", "The minimum strength of association an unmeasured confounder would "
     "need (with both treatment and outcome) to fully explain away an observed effect "
     "— a sensitivity statement. Week 14.", 14),
    ("g-formula", "Standardization over the covariate distribution to identify an "
     "effect; the repair for time-varying confounding affected by prior treatment, "
     "where ordinary regression fails. Week 14.", 14),
    ("Transportability", "The conditions under which an effect estimated in one "
     "population carries over to a different target population. Week 14.", 14),
]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(out_path: str = OUT_PATH) -> str:
    doc = Document()
    P._setup(doc)

    # --- title -------------------------------------------------------------
    guide_banner(
        doc,
        f"{theme.COURSE_TITLE}  ·  Instructor Teaching Guide",
        "Instructor Teaching Guide",
        "A 15-week graduate seminar. How to teach each week, where students "
        "stumble, what to grade, and what to cut when the clock runs out. "
        "Companion to the self-study packets, lecture decks, and practice "
        "notebooks — read it alongside them, not instead of them.",
    )

    # --- 1. Intro ----------------------------------------------------------
    P.h1(doc, "How this course is built")
    P.body(doc, "This seminar has one organizing idea: a causal estimate is an "
                "ASSUMPTION paired with an ESTIMATOR. Each week names an assumption "
                "you are willing to defend, then hands you the estimator that "
                "assumption licenses. Students who internalize that pairing can place "
                "any new method; students who memorize estimators cannot.")

    P.callout(doc, "The five-step workflow (repeat it every week)", [
        "1. Question -> estimand. Write the effect in potential-outcomes terms and "
        "say for whom (ATE / ATT / CATE / LATE).",
        "2. Assumptions -> identification. Draw the DAG; name what must hold "
        "(exchangeability, positivity, exclusion, parallel trends, ...).",
        "3. Estimator. Choose the method the assumptions license, not the fanciest "
        "one available.",
        "4. Estimate + diagnose. Fit it; check the diagnostics that earn it "
        "(balance, overlap, first-stage F, pre-trends, placebo tests).",
        "5. Sensitivity + honest sentence. Say what would overturn the result and "
        "state it to a decision-maker without over- or under-claiming.",
    ], color=theme.TEAL)

    P.h2(doc, "How each week is structured")
    P.body(doc, "Every week ships three coordinated, fully generated deliverables, "
                "all driven from one content module so the whole course shares one "
                "look and one workflow:")
    P.bullet(doc, [("Self-study packet (.docx). ", {"bold": True}),
                   ("Readings, a concept refresher, a problem set WITH full "
                    "solutions, the lab, and a self-check. ~5-7 h after lecture.", {})])
    P.bullet(doc, [("Lecture deck (.pptx). ", {"bold": True}),
                   ("The ~35-slide lecture: theory, the assumptions, and a real "
                    "worked case.", {})])
    P.bullet(doc, [("Practice notebook (.ipynb). ", {"bold": True}),
                   ("Runnable worked examples and graded-style exercises. Every "
                    "dataset is simulated with a KNOWN ground truth, so a student can "
                    "always confirm their estimate recovered the right answer — and "
                    "so can you when grading.", {})])
    P.body(doc, [("Teaching consequence: ", {"bold": True}),
                 ("because the truth is known, labs are fast to grade — you check "
                  "whether the recovered estimate matches the planted effect and "
                  "whether the required diagnostics were actually run.", {})])

    P.h2(doc, "Assessment at a glance")
    P.table(doc,
            ["Component", "Weight", "When", "What it tests"],
            [
                ["Problem sets", "20%", "Weeks 1-14", "Conceptual fluency: estimands, "
                 "assumptions, good vs. bad controls."],
                ["Labs", "25%", "Weeks 1-14", "End-to-end execution against a known "
                 "ground truth; correct diagnostics."],
                ["Midterm", "20%", "Week 8", "Cumulative over Weeks 1-7 (Foundations "
                 "+ adjustment for confounding)."],
                ["Capstone", "30%", "Week 15", "A defensible, reproducible analysis: "
                 "report + presentation."],
                ["Participation", "5%", "Throughout", "Discussion, peer feedback, "
                 "office-hours engagement."],
            ])
    P.body(doc, "The four course blocks: I Foundations (Wk 1-4), II Adjustment for "
                "confounding (Wk 5-7), III Quasi-experimental designs (Wk 8-11), "
                "IV Modern methods & application (Wk 12-15).", italic=True)

    # --- 2. Per-week teaching sections ------------------------------------
    P.h1(doc, "Teaching the weeks")
    P.body(doc, "Each section below gives: the one-sentence point, the ideas "
                "students MUST leave with, where they stumble, discussion prompts, "
                "lecture moments to slow down on, the deliverable with a grading-"
                "effort estimate, and a cut/keep note for tight weeks.", italic=True)

    for n in range(1, 16):
        title = fact(n, "title") or {12: "Double / Debiased Machine Learning"}.get(n, f"Week {n}")
        block = fact(n, "block") or "Block IV — Modern methods & application"
        t = TEACHING[n]

        P.h2(doc, f"Week {n} — {title}")
        if n == 12 and 12 not in WEEK_FACTS:
            P.body(doc, [(block + ". ", {"italic": True, "color": theme.GREY}),
                         ("Content module in progress at time of writing — this "
                          "section is written from the topic list (Neyman "
                          "orthogonality, cross-fitting, the partially linear model, "
                          "DML for the ATE, and the pitfalls).",
                          {"italic": True, "color": theme.GREY})])
        else:
            P.body(doc, [(block, {"italic": True, "color": theme.GREY})])

        P.body(doc, [("The point.  ", {"bold": True, "color": theme.BLUE}),
                     (t["point"], {})])

        P.body(doc, [("Students must leave with:", {"bold": True})])
        for m in t["musts"]:
            P.bullet(doc, m)

        P.body(doc, [("Where they stumble:", {"bold": True, "color": theme.RED})])
        for s in t["stumbles"]:
            P.bullet(doc, s)

        P.body(doc, [("Discussion prompts:", {"bold": True})])
        for i, d in enumerate(t["prompts"], 1):
            P.bullet(doc, [(f"{i}. ", {"bold": True}), (d, {})])

        P.body(doc, [("Slow down on:", {"bold": True})])
        for sd in t["slow_down"]:
            P.bullet(doc, sd)

        # deliverable line built from the real module labels where available
        ps_label = fact(n, "ps_label")
        lab_label = fact(n, "lab_label")
        lab_title = fact(n, "lab_title")
        deliv_bits = []
        if n == 8:
            deliv_bits.append("MIDTERM (Weeks 1-7)")
        if n == 15:
            deliv_bits.append("Capstone report + presentation (30%)")
        if ps_label and not (n == 15):
            deliv_bits.append(ps_label)
        if lab_label:
            deliv_bits.append(f"{lab_label}: {lab_title}".strip().rstrip(":"))
        if n == 12 and 12 not in WEEK_FACTS:
            deliv_bits = ["Problem set + lab (per the in-progress module)"]
        deliv = "; ".join(deliv_bits) if deliv_bits else "(see week folder)"

        P.callout(doc, "Deliverable & grading effort", [
            "Deliverable: " + deliv + ".",
            "Grading: " + t["grading"],
        ], color=theme.AMBER)

        P.body(doc, [("If short on time:  ", {"bold": True, "color": theme.GREEN}),
                     (t["cut_keep"], {})])

    # --- 3. Glossary -------------------------------------------------------
    P.h1(doc, "Course-wide glossary")
    P.body(doc, "About 25 load-bearing terms, with the week each is introduced. "
                "Hand it out in Week 1 and tell students to expect every term to "
                "return.", italic=True)
    P.table(doc,
            ["Term", "Definition (and where it lives)"],
            [[term, definition] for (term, definition, _wk) in GLOSSARY])

    # --- 4. Pacing / exam map ---------------------------------------------
    P.h1(doc, "Pacing & exam map")

    P.h2(doc, "What the assessments draw on")
    P.callout(doc, "Midterm (Week 8) — covers Weeks 1-7", [
        "Foundations (Wk 1-4): the causal question, potential outcomes & estimands, "
        "randomized experiments, DAGs / d-separation.",
        "Adjustment for confounding (Wk 5-7): regression & good-vs-bad controls, "
        "matching & propensity scores, IPW & doubly robust estimation.",
        "Skills tested: write an estimand; pick a valid adjustment set off a DAG; "
        "classify controls; reason about positivity and double robustness.",
        "Not on it: IV/RD/DiD/SC/DML/CATE — those belong to Blocks III-IV and the "
        "capstone.",
    ], color=theme.BLUE)
    P.callout(doc, "Capstone (Week 15) — can draw on any week, but leans on", [
        "Design selection across the whole menu (RCT, matching, IV, RD, DiD, "
        "synthetic control, DML) — Weeks 3, 6-12.",
        "Identification & assumptions discipline — Weeks 2, 4.",
        "Sensitivity / robustness (E-values, multiverse) — Weeks 7, 14.",
        "Reproducibility & communication — Week 15 itself.",
    ], color=theme.TEAL)

    P.h2(doc, "Suggested due dates")
    P.body(doc, "Assumes one 3-hour seminar per week; problem sets are due the "
                "evening before the next lecture, labs one extra day later so students "
                "can use the practice notebook first. Adjust to your calendar.",
                italic=True)
    P.table(doc,
            ["Wk", "Topic", "Problem set due", "Lab due", "Notes"],
            [
                ["1", "The Causal Question", "Wk 2, pre-lecture", "Wk 2 +1 day", "Lab 0: get the toolchain + repo live."],
                ["2", "Potential Outcomes", "Wk 3, pre-lecture", "Wk 3 +1 day", ""],
                ["3", "Randomized Experiments", "Wk 4, pre-lecture", "Wk 4 +1 day", "First full end-to-end lab."],
                ["4", "Causal Graphs (DAGs)", "Wk 5, pre-lecture", "Wk 5 +1 day", ""],
                ["5", "Regression & Adjustment", "Wk 6, pre-lecture", "Wk 6 +1 day", ""],
                ["6", "Matching & Propensity", "Wk 7, pre-lecture", "Wk 7 +1 day", ""],
                ["7", "Weighting & Doubly Robust", "Wk 8, pre-lecture", "Wk 8 +1 day", "Last topic on the midterm."],
                ["8", "IV & Mendelian Rand.", "MIDTERM in class", "Wk 9 +2 days", "Midterm covers Wk 1-7; give Lab 5 extra time."],
                ["9", "Regression Discontinuity", "Wk 10, pre-lecture", "Wk 10 +1 day", ""],
                ["10", "Diff-in-Diff & Panel", "Wk 11, pre-lecture", "Wk 11 +1 day", ""],
                ["11", "Synthetic Control", "Wk 12, pre-lecture", "Wk 12 +1 day", ""],
                ["12", "Double / Debiased ML", "Wk 13, pre-lecture", "Wk 13 +1 day", "Module may be in progress; confirm scope."],
                ["13", "Heterogeneous Effects", "Wk 14, pre-lecture", "Wk 14 +1 day", "Capstone proposals due alongside."],
                ["14", "Advanced Topics", "Wk 15, pre-lecture", "Wk 15 +1 day", "Survey week — grade for breadth, not depth."],
                ["15", "Capstone", "Pre-analysis plan, Wk 15", "Capstone report + talk", "Reserve a grading window (30%)."],
            ])

    P.callout(doc, "Pacing pressure points (build slack here)", [
        "Week 4 (DAGs): the collider rule reversal is the hardest single idea in "
        "Block I — do not compress it.",
        "Week 8: the midterm eats lecture time; either trim Lab 5 or push its due "
        "date out (reflected above).",
        "Week 10: Lab 7 is the heaviest non-capstone build (2x2, TWFE, event study, "
        "staggered-bias demo) — give two days.",
        "Week 12: if the module is still in progress, lock its scope early so "
        "Week 13 (which reuses orthogonal scores) is not blocked.",
        "Week 15: the capstone dominates end-of-term load; seed proposals in Week 13 "
        "and require the pre-analysis plan before any outcome analysis.",
    ], color=theme.AMBER)

    P.h1(doc, "A closing note for the instructor")
    P.body(doc, "If students leave able to do just one thing, make it this: state "
                "the estimand and the identifying assumption out loud BEFORE running "
                "anything, and name the one assumption most likely to be wrong. Every "
                "method in this course is a different answer to 'what would make this "
                "comparison fair?' — keep returning to that question and the fifteen "
                "weeks hold together as one argument.")

    doc.save(out_path)
    return out_path


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
