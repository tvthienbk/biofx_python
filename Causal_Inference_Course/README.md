# Causal Inference in Practice — Course Materials

*From "what is associated with what" to "what happens if we intervene."*

A complete 15-week graduate seminar. Every week is a self-contained folder with
three deliverables, all generated from a single reproducible source so the whole
course shares one look and one workflow:

| Deliverable | Format | Purpose |
|-------------|--------|---------|
| **Self-study packet** | `.docx` | Readings, concept refresher, a problem set **with full solutions**, the lab, and a self-check. ~5–7 h of guided work after each lecture. |
| **Lecture deck** | `.pptx` | The ~35-slide lecture: theory + assumptions + a real worked case. |
| **Practice notebook** | `.ipynb` | Runnable Jupyter notebook with worked examples and graded-style exercises (+ solutions). **Every dataset is simulated with a known ground truth**, so students can always check that their estimate recovered the right answer. |

## The fifteen weeks

| Wk | Topic | Folder |
|----|-------|--------|
| **Block I — Foundations** | | |
| 1 | The Causal Question | `Week01_The_Causal_Question/` |
| 2 | Potential Outcomes | `Week02_Potential_Outcomes/` |
| 3 | Randomized Experiments & A/B Testing | `Week03_Randomized_Experiments_AB_Testing/` |
| 4 | Causal Graphs (DAGs) | `Week04_Causal_Graphs_DAGs/` |
| **Block II — Adjustment for confounding** | | |
| 5 | Regression & Adjustment | `Week05_Regression_Adjustment/` |
| 6 | Matching & Propensity Scores | `Week06_Matching_Propensity_Scores/` |
| 7 | Weighting & Doubly Robust Estimation | `Week07_Weighting_Doubly_Robust_Estimation/` |
| **Block III — Quasi-experimental designs** | | |
| 8 | Instrumental Variables & Mendelian Randomization *(midterm)* | `Week08_Instrumental_Variables_Mendelian_Randomization/` |
| 9 | Regression Discontinuity | `Week09_Regression_Discontinuity/` |
| 10 | Difference-in-Differences & Panel Methods | `Week10_Difference_in_Differences_Panel_Methods/` |
| 11 | Synthetic Control | `Week11_Synthetic_Control/` |
| **Block IV — Modern methods & application** | | |
| 12 | Double / Debiased Machine Learning | `Week12_Double_Debiased_Machine_Learning/` |
| 13 | Heterogeneous Effects & Policy Learning | `Week13_Heterogeneous_Effects_Policy_Learning/` |
| 14 | Advanced Topics | `Week14_Advanced_Topics/` |
| 15 | Capstone, Reproducibility & Communication | `Week15_Capstone_Reproducibility_Communication/` |

The **midterm** (Week 8) covers Weeks 1–7. The **capstone** (Week 15) is the
final deliverable. Assessment: Problem sets 20% · Labs 25% · Midterm 20% ·
Capstone 30% · Participation 5%.

## Assessments & instructor materials

The `Assessments/` folder holds the course-wide graded artifacts and the
teaching guide (all generated, like the weekly materials):

| File | What it is |
|------|------------|
| `Midterm_Exam_Weeks_1-7.docx` | A 100-point, ~90-minute midterm covering Weeks 1–7 (concepts, a DAG problem, estimands, an A/B power/CUPED item, control classification, and a by-hand IPW computation). |
| `Midterm_Exam_Weeks_1-7_SOLUTIONS.docx` | Full instructor answer key with the point breakdown. |
| `Capstone_Project_Brief.docx` | The capstone assignment: deliverables, milestone timeline, a question→design selection guide, project ideas, and a 7-criterion grading rubric. |
| `Capstone_Proposal_Template.docx` | A fill-in proposal template (question, estimand, data, identification, assumptions, estimation & robustness plans). |
| `Instructor_Teaching_Guide.docx` | Per-week teaching notes (key ideas, common misconceptions, discussion prompts), a glossary, and a pacing/exam map. |

## Running the practice notebooks

```bash
pip install -r requirements.txt
jupyter lab            # then open any WeekNN_*_Practice.ipynb
```

Notebooks use only `numpy`, `pandas`, `scipy`, `matplotlib`, `statsmodels` and
`scikit-learn` — no internet, no data downloads, every method implemented from
standard tools with a known ground truth.

## Reproducing the documents

All `.docx` / `.pptx` / `.ipynb` files are **generated** from per-week content
modules — editing the course is editing data, not fighting Word and PowerPoint.

```bash
cd _build
python build_all.py            # rebuild every week
python build_all.py 4 7        # rebuild specific weeks
python validate.py             # open every doc + EXECUTE every notebook
```

- `_build/coursegen/` — the generator (theme, packet/deck/notebook builders).
- `_build/coursegen/content/weekNN.py` — one dict per week; the actual content.
- `_build/AUTHORING.md` — the content contract, if you want to add or edit a week.
- `_assets/source_materials/` — the original syllabus and the first-edition
  Week 1 packet/deck (kept for reference; the polished original Week 1 deck has
  extra hand-drawn diagrams you may prefer to the generated one).
