# Authoring a weekly content module

Each week is a single Python file `coursegen/content/weekNN.py` that defines one
dict named `WEEK`. The build system (`build_all.py`) turns it into three files:

* `WeekNN_<Title>_Self_Study_Packet.docx`
* `WeekNN_<Title>_Lecture.pptx`
* `WeekNN_<Title>_Practice.ipynb`

**The single source of truth for the exact structure is `coursegen/content/week01.py`.**
Open it and mirror it field-for-field. `coursegen/schema.py` is the validator;
your module must pass it. Below is the contract.

## Top-level keys (all required)

```python
WEEK = {
  "number": 2,                      # int 1..15
  "slug": "potential_outcomes",     # lowercase, underscores
  "title": "Potential Outcomes",    # short title (no week number)
  "block": "Block I — Foundations", # exact block string from the syllabus
  "subtitle": "...",                # one sentence describing the week
  "deliverable": "...",             # the graded deliverable (PS / Lab)

  # ---- packet ----
  "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: ...",
  "one_sentence": "...",            # 'this week in one sentence' (1–2 sentences)
  "objectives_heading": "What you should be able to do by Sunday",
  "objectives": [ "...", ... ],     # >= 4, each a full sentence, action verb first
  "reading_intro": "...",           # one italic sentence
  "readings": [ {"text": "<author, title — chapter>",
                 "look_for": "<what to look for>"}, ... ],   # >= 2
  "optional_readings": [ {"text": "...", "note": "..."}, ... ],  # optional
  "concept_intro": "...",           # one italic sentence
  "concept_sections": [             # >= 3 recommended; a mini-lecture in prose
     {"heading": "...",
      "body": "<paragraph>",                       # optional
      "bullets": [ seg, ... ],                     # optional, see 'seg' below
      "callout": {"title": "...", "color": "RED",  # optional highlight panel
                  "lines": [seg, ...]}},
     ...
  ],
  "problem_set": {
     "label": "Problem Set 2",      # or "Lab 1" etc. — matches the syllabus 'Due'
     "title": "...",
     "intro": "...",
     "problems": [                  # >= 5 strongly preferred (min 4)
        {"title": "<short scenario name>",
         "prompt": "<the question, 2–4 sentences>",
         "solution_title": "<one-line answer/verdict>",
         "solution": [ seg, seg, ... ]},   # 2–4 bullet points of reasoning
        ...
     ],
  },
  "lab": {
     "label": "Lab 1",
     "title": "...",
     "goal": "<one sentence>",
     "steps": [
        {"heading": "Step 1 · ...",
         "body": "...",                      # optional
         "bullets": [seg, ...],              # optional
         "code_r": "<R code>",               # optional
         "code_python": "<python code>"},    # optional
        ...
     ],
     "expected": "<what students should see>",   # optional but recommended
     "submit": [ "...", ... ],                    # optional
  },
  "self_check": [ "...", ... ],     # 3–5 short 'can you…' items
  "next_week": {"heading": "Coming up: Week 3 — ...", "teaser": "<2–3 sentences>"},

  "deck":     [ slide, slide, ... ],  # see 'Deck' below — aim for 34–40 slides
  "notebook": [ cell, cell, ... ],    # see 'Notebook' below — aim for 18–26 cells
}
```

### `seg` (rich text segment)

Anywhere the contract says `seg`, you may use **either**:

* a plain string `"hello"`, **or**
* a list of `(text, opts)` runs for inline styling, e.g.
  `[("Confounder: ", {"bold": True}), ("adjust for it.", {})]`

`opts` keys: `bold`, `italic`, `size`, `color` (hex string w/o `#`), `font`.
For a 2-level bullet in concept/lab bullets, a plain string is level-0; to make
a sub-bullet pass a tuple `(text, 1)` **only inside deck bullets** (see below).

## Deck (list of slide dicts)

First slide MUST be `{"type": "title"}` (it auto-fills from the top-level
`title/block/subtitle/number`). Then alternate **section dividers** and
**content** slides so the deck has a clear narrative. Use 6–8 sections.

Slide types and their fields (copy patterns from `week01.py`):

* `{"type": "title"}` — exactly once, first.
* `{"type": "section", "kicker": "Part 2", "title": "...", "subtitle": "..."}`
* `{"type": "agenda", "title": "...", "items": [{"t": "...", "d": "..."}, ... 6]}`
* `{"type": "content", "kicker": "...", "title": "...",
   "bullets": [ "text", ("sub-bullet text", 1), ... ],   # 4–6 top bullets max
   "note": {"title": "...", "body": "..."}}`              # optional side panel
* `{"type": "compare", "kicker": "...", "title": "...",
   "columns": [ {"head": "...", "sub": "...", "points": ["...", ...]}, ... 2–3 ]}`
* `{"type": "table", "kicker": "...", "title": "...",
   "headers": ["...", ...], "rows": [["...", ...], ...],  # <= 6 rows, <= 4 cols
   "note": {"title": "...", "body": "..."}}`
* `{"type": "statement", "quote": "...", "attribution": "..."}`
* `{"type": "steps", "kicker": "...", "title": "...",
   "steps": [{"title": "...", "body": "..."}, ... 3–5], "note": "..."}`

**Keep text short on slides.** Content bullets ≤ ~14 words. Tables ≤ 6 rows.
This keeps everything inside the slide. Decks must have ≥ 20 slides (target 36).

## Notebook (list of cells) — THE MOST IMPORTANT ARTIFACT

A banner cell and an environment/setup cell are added automatically. The setup
cell defines `RNG = np.random.default_rng(7)` and imports `numpy as np`,
`pandas as pd`, `matplotlib.pyplot as plt`. **Reuse `RNG`**; do not reseed.

Each cell is `{"md": "<markdown>"}` or `{"code": "<python>"}`.

**Hard requirements (these make it "perfect"):**

1. **It must run top-to-bottom with no errors** using only
   `numpy, pandas, statsmodels, scikit-learn, matplotlib`. No internet, no file
   downloads, no exotic packages (no `dowhy/econml/linearmodels/grf`).
2. **Every dataset is simulated with a KNOWN ground-truth effect**, and the code
   **prints the estimate next to the truth** and `assert`s recovery within a
   tolerance (e.g. `assert abs(est - TRUE) < 0.15`). This is how students know
   they got it right.
3. Include **2–3 `🔧 Exercise` cells**. Each exercise is: a markdown cell
   explaining the task, then a code cell containing a `# TODO` skeleton **that
   still runs** (use `...` Ellipsis assignments or fully-commented lines so the
   notebook executes), then a `### ✅ Solution` markdown cell, then a working
   solution code cell with an `assert`.
4. Use clear section headers (`## 1 · ...`). Open with a worked example, build to
   the week's main estimator, end with a `## Wrap-up & self-check` markdown cell.
5. Plots are fine (`plt`), but never call `plt.show()` in a way that blocks; just
   create the figure. Keep每 `n` modest (≤ 50_000) so it runs fast.

Implement the week's actual method from scratch with standard tools, e.g.:
IPW via `LogisticRegression` propensity + weighted mean; matching via
`NearestNeighbors`; IV via 2SLS done as two `sm.OLS` stages; RD via local linear
regression on each side of a cutoff; DiD via an interaction term in `sm.OLS`;
DML via cross-fitted residual-on-residual regression; causal forest via
honest splitting approximated with `RandomForestRegressor` T-learner; etc.

## Before you finish — VALIDATE

Run, from `Causal_Inference_Course/_build/`:

```bash
python build_all.py NN     # NN = your week number; must print "✓ Week NN"
python validate.py NN      # must print "ALL GOOD" (this EXECUTES your notebook)
```

Fix everything until both pass. Do not hand back a module that fails either.
