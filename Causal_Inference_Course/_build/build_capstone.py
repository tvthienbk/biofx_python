#!/usr/bin/env python3
"""Build the Week 15 capstone assessment materials.

Produces two .docx files in ``Causal_Inference_Course/Assessments/``:

  * ``Capstone_Project_Brief.docx``     — the full project brief + grading rubric
  * ``Capstone_Proposal_Template.docx`` — a fill-in proposal students submit

Both reuse the course's shared look (banner / headings / callouts / tables)
from ``coursegen.packet`` so the capstone pack looks like the weekly packets.

Run:  python Causal_Inference_Course/_build/build_capstone.py
"""
from __future__ import annotations

import os
import sys

# Make the in-repo ``coursegen`` package importable regardless of cwd.
_BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BUILD_DIR)

from coursegen import packet as P  # noqa: E402
from coursegen import theme  # noqa: E402
from docx import Document  # noqa: E402

# ---------------------------------------------------------------------------
# Output locations
# ---------------------------------------------------------------------------
_COURSE_DIR = os.path.dirname(_BUILD_DIR)
_ASSESS_DIR = os.path.join(_COURSE_DIR, "Assessments")

BRIEF_PATH = os.path.join(_ASSESS_DIR, "Capstone_Project_Brief.docx")
TEMPLATE_PATH = os.path.join(_ASSESS_DIR, "Capstone_Proposal_Template.docx")

# ---------------------------------------------------------------------------
# Grading rubric — single source of truth (also reported on the CLI)
# Each row: (criterion, weight %, excellent, adequate, weak)
# Weights MUST sum to 100.
# ---------------------------------------------------------------------------
RUBRIC = [
    (
        "Question & estimand",
        15,
        "A sharp, decision-relevant causal question; the target estimand "
        "(ATE / ATT / LATE / CATE) and the population are defined precisely, "
        "with units, treatment and outcome unambiguous.",
        "A reasonable question and a named estimand, but the population or "
        "the contrast is left somewhat vague.",
        "Question is associational or unclear; no explicit estimand; "
        "treatment/outcome/population not pinned down.",
    ),
    (
        "Identification strategy & assumptions",
        20,
        "Design fits the data structure; a DAG makes the strategy explicit; "
        "every identifying assumption (exchangeability, positivity, SUTVA, "
        "exclusion, parallel trends, continuity, …) is stated and justified "
        "for THIS problem.",
        "A defensible design with most assumptions stated, but one or two are "
        "asserted rather than argued, or the DAG is incomplete.",
        "No clear identification argument; assumptions missing, hand-waved, "
        "or plainly violated; confounding/selection ignored.",
    ),
    (
        "Estimation & uncertainty",
        15,
        "Estimator matches the design and estimand; uncertainty is quantified "
        "correctly (appropriate / clustered / bootstrap SEs); results read as "
        "effects with intervals, not just p-values.",
        "Sensible estimator and intervals, with minor mismatches in SE choice "
        "or interpretation.",
        "Estimator does not target the estimand; uncertainty missing or wrong; "
        "point estimates reported with false precision.",
    ),
    (
        "Robustness & sensitivity",
        15,
        "Pre-stated checks probe the key threats (placebo / negative controls, "
        "alternative specifications, E-value or Rosenbaum-style sensitivity, "
        "balance / overlap diagnostics); the headline result survives or the "
        "limits are stated honestly.",
        "Some robustness checks run, but they miss the most important threat "
        "or are reported without interpretation.",
        "No robustness or sensitivity analysis; conclusions presented as if "
        "the assumptions were known to hold.",
    ),
    (
        "Reproducibility",
        15,
        "One-command rebuild from a clean checkout; fixed seeds; environment "
        "logged (lockfile / session info); data acquisition scripted or "
        "documented; Git history is clean and the repo runs end-to-end.",
        "Repo runs with minor manual steps; seeds set; environment described "
        "but not fully pinned.",
        "Cannot be reproduced: missing code/data, no seeds, undocumented "
        "environment, or results that do not regenerate.",
    ),
    (
        "Communication / report",
        12,
        "Tight narrative through the 5-step workflow; figures and tables are "
        "self-explanatory; one honest, caveated sentence a decision-maker "
        "could act on; limitations stated plainly.",
        "Clear and mostly complete, but uneven in places or over-claims "
        "slightly in the conclusion.",
        "Disorganized or padded; figures unlabeled; conclusion overstates what "
        "the design can support.",
    ),
    (
        "Presentation & peer review",
        8,
        "Confident, well-paced talk that defends the design under questioning; "
        "submits substantive, constructive peer review of another project.",
        "Solid talk and a fair peer review, with some questions handled "
        "shakily.",
        "Talk does not convey the design or cannot answer basic questions; "
        "peer review absent or superficial.",
    ),
]

assert sum(w for _, w, *_ in RUBRIC) == 100, "Rubric weights must sum to 100"


# ===========================================================================
# Brief
# ===========================================================================
def build_brief(out_path: str) -> str:
    doc = Document()
    P._setup(doc)
    P.banner(doc, "15", "Capstone Project")
    P.body(
        doc,
        "An original, end-to-end causal analysis — your chance to take a real "
        "question all the way from a clearly posed counterfactual to a "
        "defensible, reproducible answer you can stand behind. Worth 30% of the "
        "course grade.",
        italic=True,
    )

    P.h2(doc, "The capstone in one sentence")
    P.body(
        doc,
        "Pick a question that matters, earn a causal claim with a design rather "
        "than a regression, state your assumptions out loud, try hard to break "
        "your own result, and explain what you found in one honest sentence a "
        "decision-maker could act on.",
    )

    # --- Overview & goal ----------------------------------------------------
    P.h1(doc, "Overview & goal")
    P.body(
        doc,
        "The capstone is the final deliverable for Causal Inference in Practice. "
        "You will produce an original analysis that applies the course's "
        "five-step workflow from beginning to end. There is no single \"right\" "
        "answer; you are graded on whether the question, design, and evidence "
        "hang together and whether someone else could reproduce and trust your "
        "work.",
    )
    P.body(doc, [("The five-step workflow you are applying:", {"bold": True})])
    P.numbered(doc, 1, "Question",
               "State a precise causal question and the decision it informs.")
    P.numbered(doc, 2, "Assumptions",
               "Make the assumptions that would let data answer it explicit.")
    P.numbered(doc, 3, "Identification",
               "Choose a design that, under those assumptions, identifies the "
               "target estimand from observable data.")
    P.numbered(doc, 4, "Estimation",
               "Estimate the effect and quantify uncertainty honestly.")
    P.numbered(doc, 5, "Validation",
               "Stress-test the result with robustness and sensitivity checks, "
               "then communicate it with its caveats.")
    P.callout(
        doc,
        "What makes a capstone excellent",
        [
            "The design is chosen because of the data structure, not because "
            "it is familiar.",
            "Every identifying assumption is argued for THIS problem, not "
            "recited in general.",
            "You actively tried to overturn your own finding and reported what "
            "happened.",
            "A stranger can clone the repo and regenerate every number and "
            "figure with one command.",
        ],
        color=theme.TEAL,
    )

    # --- Deliverables -------------------------------------------------------
    P.h1(doc, "Deliverables")
    P.h2(doc, "1. A reproducible report (with code repository)")
    P.bullet(doc, [("Length: ", {"bold": True}),
                   ("roughly 8–15 pages (or equivalent in a rendered "
                    "notebook), excluding code appendices.", {})])
    P.bullet(doc, [("Structure: ", {"bold": True}),
                   ("follows the five-step workflow — question & estimand, "
                    "assumptions, identification (with a DAG), estimation & "
                    "uncertainty, robustness/sensitivity, and an honest "
                    "conclusion with limitations.", {})])
    P.bullet(doc, [("Code repository: ", {"bold": True}),
                   ("a public or instructor-shared Git repo containing all "
                    "code, a README, and either scripted data download or "
                    "clearly documented data provenance.", {})])
    P.h2(doc, "2. A presentation")
    P.bullet(doc, [("Format: ", {"bold": True}),
                   ("a 10–12 minute talk plus 5 minutes of questions, "
                    "delivered live or recorded.", {})])
    P.bullet(doc, [("Focus: ", {"bold": True}),
                   ("the design and why it is credible — not a tour of code. "
                    "Expect to defend your identifying assumptions under "
                    "questioning.", {})])
    P.bullet(doc, [("Peer review: ", {"bold": True}),
                   ("each student writes one structured review of another "
                    "team's project using this rubric.", {})])

    P.h2(doc, "Reproducibility requirements (non-negotiable)")
    P.bullet(doc, [("Fixed seeds ", {"bold": True}),
                   ("for every stochastic step (sampling, bootstrap, "
                    "cross-fitting, model init).", {})])
    P.bullet(doc, [("Logged environment ", {"bold": True}),
                   ("— a lockfile (requirements.txt / environment.yml / "
                    "renv.lock) and recorded session info / language "
                    "version.", {})])
    P.bullet(doc, [("One-command rebuild ", {"bold": True}),
                   ("— e.g. make all, quarto render, or a single run.sh / "
                    "Jupyter \"Run All\" that regenerates every figure and "
                    "number from raw data.", {})])
    P.bullet(doc, [("Versioned in Git ", {"bold": True}),
                   ("with a literate document (Quarto / R Markdown / Jupyter) "
                    "so prose, code, and outputs live together.", {})])
    P.callout(
        doc,
        "Reproducibility smoke test",
        [
            "Before you submit: clone your repo into a fresh directory, create "
            "the environment from the lockfile, run the one build command, and "
            "confirm the report regenerates with no manual fixes.",
            "If it does not run for a stranger, it does not run.",
        ],
        color=theme.AMBER,
    )

    # --- Timeline -----------------------------------------------------------
    P.h1(doc, "Timeline & milestones")
    P.body(
        doc,
        "Weeks are suggestions relative to the 15-week schedule — start early; "
        "data wrangling and getting a clean build always take longer than "
        "expected.",
        italic=True,
    )
    P.table(
        doc,
        ["Milestone", "Suggested week", "What is due"],
        [
            ["Topic + data identified",
             "~Week 11",
             "A one-paragraph question and a confirmed, accessible data "
             "source."],
            ["Proposal submitted & approved",
             "~Week 12",
             "The completed proposal template (see companion document); "
             "instructor sign-off on scope and design."],
            ["Mid-project check-in",
             "~Week 13",
             "Loaded data, a balance/overlap or design-validity diagnostic, "
             "and a first estimate; flag blockers."],
            ["Draft report",
             "~Week 14",
             "A full draft that already builds end-to-end, even if numbers "
             "are still moving."],
            ["Final report + presentation + peer review",
             "Week 15",
             "Final reproducible report and repo, the talk, and your written "
             "peer review of another project."],
        ],
    )

    # --- Choosing a design --------------------------------------------------
    P.h1(doc, "Choosing a design")
    P.body(
        doc,
        "The design should follow from how the data were generated and what "
        "variation in treatment you can credibly call as-good-as-random. Use "
        "this map as a starting point, then defend your choice in the "
        "proposal.",
    )
    P.table(
        doc,
        ["If your situation looks like…", "Consider", "Key assumption to defend"],
        [
            ["You control assignment and can randomize",
             "RCT / A-B test",
             "Successful randomization; no interference; complete adherence "
             "(or analyze as assigned)."],
            ["Rich observed confounders; overlap across treatment",
             "Regression adjustment, matching, or propensity weighting",
             "Conditional exchangeability (no unmeasured confounding) + "
             "positivity / overlap."],
            ["Confounders likely unobserved, but a valid instrument exists "
             "(incl. a genetic variant)",
             "Instrumental variables / Mendelian randomization",
             "Relevance, exclusion restriction, and independence of the "
             "instrument."],
            ["Treatment switches at a threshold of a running variable",
             "Regression discontinuity",
             "Continuity of potential outcomes at the cutoff; no manipulation "
             "of the running variable."],
            ["Panel data; a group is treated at a known time",
             "Difference-in-differences",
             "Parallel trends absent treatment; no anticipation; staggered-"
             "adoption bias addressed."],
            ["One (or few) treated units, many untreated, long pre-period",
             "Synthetic control",
             "A weighted donor pool reproduces the pre-treatment trajectory; "
             "no spillovers to donors."],
            ["Many covariates; flexible nuisance models needed",
             "Double / debiased machine learning (DML)",
             "Exchangeability + positivity, with cross-fitting and Neyman-"
             "orthogonal scores."],
            ["You need who-benefits, not just the average",
             "Causal forests / meta-learners (CATE)",
             "Same identification as the base design, plus honest estimation "
             "of heterogeneity."],
        ],
    )

    # --- Example project ideas ---------------------------------------------
    P.h1(doc, "Example project ideas")
    P.body(
        doc,
        "Concrete starting points across domains. Treat each as a prompt to "
        "sharpen into a precise question and estimand — not a finished design.",
        italic=True,
    )
    P.h2(doc, "Epidemiology / clinical")
    P.numbered(
        doc, 1,
        "Statins and cardiovascular events in observational EHR data",
        "Use propensity weighting or matching to estimate the ATT of statin "
        "initiation; defend overlap and no-unmeasured-confounding, and probe "
        "with negative-control outcomes.")
    P.numbered(
        doc, 2,
        "Effect of an ICU protocol change on length of stay",
        "Exploit a hospital that switched protocols on a known date "
        "(difference-in-differences) against comparable units; test parallel "
        "trends in the pre-period.")
    P.h2(doc, "Economics / policy")
    P.numbered(
        doc, 3,
        "Minimum-wage change on county-level employment",
        "Difference-in-differences or synthetic control across a state border "
        "or policy boundary; address staggered adoption and spillovers.")
    P.numbered(
        doc, 4,
        "A merit-scholarship cutoff on college enrollment",
        "Regression discontinuity at the eligibility test-score threshold; "
        "check for manipulation (density test) and covariate continuity.")
    P.h2(doc, "Tech experimentation")
    P.numbered(
        doc, 5,
        "A recommender or onboarding change on retention",
        "Analyze an A-B test (or an encouragement design if uptake is "
        "voluntary, estimating a LATE); handle interference and "
        "novelty/primacy effects.")
    P.numbered(
        doc, 6,
        "Heterogeneous treatment effects of a pricing experiment",
        "Use causal forests / a meta-learner on experiment data to estimate "
        "CATEs and target who benefits, with honest splitting.")
    P.h2(doc, "Genomics / Mendelian randomization")
    P.numbered(
        doc, 7,
        "A modifiable exposure (e.g. LDL cholesterol or BMI) on disease risk",
        "Two-sample Mendelian randomization using public GWAS summary "
        "statistics; assess pleiotropy with MR-Egger / weighted-median and a "
        "leave-one-out analysis.")
    P.numbered(
        doc, 8,
        "Effect of a biomarker on an outcome via a genetic instrument",
        "IV / MR with explicit defense of relevance, exclusion, and "
        "independence; report instrument strength (F-statistic).")

    # --- Scope & data -------------------------------------------------------
    P.h1(doc, "Scope guardrails & data sources")
    P.h2(doc, "Scope guardrails")
    P.bullet(doc, "One causal question, one primary estimand. Resist scope "
                  "creep into a second analysis.")
    P.bullet(doc, "Prefer a small, clean, well-understood dataset over a large "
                  "messy one — credibility beats size.")
    P.bullet(doc, "Confirm the data are accessible and the design is feasible "
                  "BEFORE the proposal is approved.")
    P.bullet(doc, "Simulated or semi-synthetic data with a known ground truth "
                  "is welcome, especially to validate your estimator.")
    P.bullet(doc, "Respect data licenses and privacy; never submit restricted "
                  "or identifiable data to a shared repo.")
    P.h2(doc, "Public dataset suggestions")
    P.bullet(doc, [("Health / epi: ", {"bold": True}),
                   ("NHANES, MIMIC (credentialed), SEER, CDC WONDER, UK "
                    "Biobank (approved access).", {})])
    P.bullet(doc, [("Economics / policy: ", {"bold": True}),
                   ("IPUMS / CPS, World Bank, FRED, OECD, Eurostat, "
                    "data.gov.", {})])
    P.bullet(doc, [("Genomics / MR: ", {"bold": True}),
                   ("GWAS Catalog, IEU OpenGWAS, MR-Base, GTEx.", {})])
    P.bullet(doc, [("Benchmarks / teaching: ", {"bold": True}),
                   ("LaLonde / NSW jobs data, IHDP, ACIC data-challenge "
                    "datasets, Lalonde-style replication sets.", {})])

    # --- AI & integrity -----------------------------------------------------
    P.h1(doc, "AI use & academic-integrity policy")
    P.body(
        doc,
        "AI assistants are permitted as an aid, with disclosure. They are good "
        "at scaffolding code, drafting prose, and surfacing methods — and bad "
        "at knowing whether YOUR assumptions hold. The intellectual "
        "responsibility is entirely yours.",
    )
    P.callout(
        doc,
        "The rule: you must be able to defend every line",
        [
            "Permitted: AI for boilerplate code, debugging, literature "
            "pointers, and prose polishing.",
            "Required: a short \"AI use\" note in the report stating what tools "
            "you used and for what.",
            "The bar: in the presentation and viva you must be able to explain "
            "and justify every assumption, estimator, and line of code as your "
            "own work.",
            "Not permitted: fabricated data or results, undisclosed "
            "AI-generated analysis you cannot defend, or copying another "
            "project's design.",
        ],
        color=theme.RED,
    )

    # --- Rubric -------------------------------------------------------------
    P.h1(doc, "Grading rubric")
    P.body(
        doc,
        "The capstone is worth 30% of the course grade. Each criterion is "
        "scored against the descriptions below; weights sum to 100%. The same "
        "rubric structures the peer review.",
    )
    P.table(
        doc,
        ["Criterion", "Weight", "Excellent", "Adequate", "Weak"],
        [
            [crit, f"{wt}%", exc, adq, wk]
            for (crit, wt, exc, adq, wk) in RUBRIC
        ],
    )
    P.body(
        doc,
        [("Total: 100%. ", {"bold": True}),
         ("A project that is brilliant but irreproducible, or reproducible but "
          "associational, cannot score well — credibility and reproducibility "
          "are weighted to matter.", {})],
        italic=True,
    )

    doc.save(out_path)
    return out_path


# ===========================================================================
# Proposal template
# ===========================================================================
def _field(doc, label, prompt):
    """A labelled fill-in field: bold label + italic guidance + a blank line."""
    P.body(doc, [(label, {"bold": True, "color": theme.BLUE})], space=2)
    P.body(doc, [(prompt, {"italic": True, "color": theme.GREY})], space=2)
    P.body(doc, [("[ Your answer here ]", {"color": theme.GREY})], space=8)


def build_template(out_path: str) -> str:
    doc = Document()
    P._setup(doc)
    P.banner(doc, "15", "Capstone Proposal Template")
    P.body(
        doc,
        "Fill in every section below and submit for approval (~Week 12) before "
        "you begin the analysis. Keep it to 2–3 pages — this is a plan, not the "
        "report. Replace each prompt and the [ Your answer here ] placeholder "
        "with your own content.",
        italic=True,
    )
    P.callout(
        doc,
        "How this is reviewed",
        [
            "The instructor signs off on the QUESTION, the DESIGN, and the "
            "FEASIBILITY of the data.",
            "Approval means the design can, in principle, identify your "
            "estimand — not that the result will come out any particular way.",
        ],
        color=theme.TEAL,
    )

    P.h1(doc, "1. Title & team")
    _field(doc, "Project title",
           "A short, specific title naming the treatment, outcome, and "
           "population.")
    _field(doc, "Author(s)",
           "Names; note any division of labour if this is a team project.")

    P.h1(doc, "2. The causal question")
    _field(doc, "Causal question",
           "State it as an intervention: \"What is the effect of [doing X vs "
           "not] on [outcome Y] in [population P]?\" Name the decision it "
           "informs.")

    P.h1(doc, "3. Target estimand & population")
    _field(doc, "Estimand",
           "Which causal contrast? ATE, ATT, LATE, CATE, …? Define treatment, "
           "the comparison condition, and the outcome scale (risk difference, "
           "risk ratio, mean difference).")
    _field(doc, "Population / units",
           "Who or what are the units, and over what population does the "
           "estimand generalize?")

    P.h1(doc, "4. Data source")
    _field(doc, "Dataset(s)",
           "Name, source, link, and license. Number of units, time span, and "
           "key variables (treatment, outcome, covariates, running variable / "
           "instrument as relevant).")
    _field(doc, "Access & provenance",
           "How will you obtain it (scripted download? credentialed access?), "
           "and any privacy or licensing constraints.")

    P.h1(doc, "5. Identification strategy & DAG")
    _field(doc, "Proposed design",
           "Which design (RCT, matching/weighting, IV/MR, RD, DiD, synthetic "
           "control, DML, causal forest) and why it fits THIS data-generating "
           "process.")
    _field(doc, "DAG sketch",
           "Insert a directed acyclic graph showing treatment, outcome, "
           "confounders, and any instrument / running variable. Describe which "
           "paths you are blocking and which you are leaving open.")
    P.body(
        doc,
        [("[ Paste or embed your DAG image here — or describe nodes and "
          "edges in text if drawing later ]", {"color": theme.GREY})],
        space=8,
    )

    P.h1(doc, "6. Key assumptions & how each is defended")
    P.body(
        doc,
        "List each identifying assumption your design needs and how you will "
        "argue or test it. Add rows as needed.",
        italic=True,
    )
    P.table(
        doc,
        ["Assumption", "Why it is plausible here", "How you will check / defend it"],
        [
            ["e.g. Conditional exchangeability",
             "[ argument for this dataset ]",
             "[ covariate set, negative controls, sensitivity analysis ]"],
            ["e.g. Positivity / overlap",
             "[ … ]",
             "[ propensity overlap plot, trimming rule ]"],
            ["[ assumption 3 ]", "[ … ]", "[ … ]"],
        ],
    )

    P.h1(doc, "7. Estimation plan")
    _field(doc, "Estimator",
           "Which estimator targets your estimand (e.g. IPW, AIPW/TMLE, 2SLS, "
           "local-linear RD, DiD with two-way FE or a modern estimator, "
           "synthetic-control weights, DML)?")
    _field(doc, "Uncertainty",
           "How will you quantify uncertainty (robust / clustered SEs, "
           "bootstrap, cross-fitting)? At what level is variation clustered?")

    P.h1(doc, "8. Planned robustness & sensitivity checks")
    _field(doc, "Robustness checks",
           "Pre-state the checks: placebo / negative controls, alternative "
           "specifications, alternative samples, falsification tests.")
    _field(doc, "Sensitivity analysis",
           "How will you probe the assumption most likely to fail (E-value, "
           "Rosenbaum bounds, pleiotropy-robust MR, leave-one-out)?")

    P.h1(doc, "9. Reproducibility plan")
    _field(doc, "Repository & build",
           "Where the repo lives; the one command that rebuilds the report; "
           "literate-document tool (Quarto / R Markdown / Jupyter).")
    _field(doc, "Environment & seeds",
           "How the environment is pinned (lockfile + session info) and which "
           "seeds you will fix.")

    P.h1(doc, "10. Risks & contingencies")
    _field(doc, "Risks",
           "What could derail this (data access, weak overlap, weak "
           "instrument, no parallel trends)? What is your fallback question or "
           "design if a key assumption fails?")

    P.callout(
        doc,
        "Before you submit",
        [
            "Could a skeptic name the assumption you are most worried about? "
            "Have you said how you will defend it?",
            "Is the dataset confirmed accessible, not just hoped-for?",
            "Can the design, in principle, identify the estimand you named in "
            "section 3?",
        ],
        color=theme.AMBER,
    )

    doc.save(out_path)
    return out_path


# ===========================================================================
# Entry point
# ===========================================================================
def main() -> None:
    os.makedirs(_ASSESS_DIR, exist_ok=True)
    brief = build_brief(BRIEF_PATH)
    template = build_template(TEMPLATE_PATH)
    print(f"wrote {brief}")
    print(f"wrote {template}")
    print(f"rubric criteria: {len(RUBRIC)}  weights sum to "
          f"{sum(w for _, w, *_ in RUBRIC)}%")


if __name__ == "__main__":
    main()
