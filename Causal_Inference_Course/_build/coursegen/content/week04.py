# -*- coding: utf-8 -*-
"""Week 4 — Causal Graphs (DAGs). Content module."""

WEEK = {
    "number": 4,
    "slug": "causal_graphs_dags",
    "title": "Causal Graphs (DAGs)",
    "block": "Block I — Foundations",
    "subtitle": "A visual algebra for assumptions: read confounders, colliders, "
                "and mediators directly off the graph.",
    "deliverable": "Problem Set 3 — d-separation & adjustment sets; "
                   "Lab 2 — encode a DAG, list its testable implications, and "
                   "read off a valid adjustment set.",

    # ------------------------------------------------------------------ packet
    "packet_intro": "Work through this after the lecture. Budget ~5–7 hours: "
                    "reading (2h), problem set (1.5–2h), lab (2–3h). Keep a pen "
                    "and paper next to you — you will draw a lot of small graphs.",
    "one_sentence": "A DAG turns your causal assumptions into a picture whose "
        "geometry you can read: paths carry association, three local shapes "
        "(chain, fork, collider) decide whether a path is open or blocked, and "
        "d-separation mechanically tells you what to adjust for.",
    "objectives_heading": "What you should be able to do by Sunday",
    "objectives": [
        "Translate a verbal causal story into a directed acyclic graph with "
        "explicit nodes, edges, and (where you suspect them) unobserved causes.",
        "Classify any segment of a path as a chain, a fork, or a collider, and "
        "state the d-separation rule that governs each.",
        "Apply d-separation to decide whether a given path is open or blocked "
        "given a conditioning set — and explain when conditioning OPENS a path.",
        "Use the back-door criterion to find a valid (and minimal) adjustment "
        "set, and recognize when no back-door set exists.",
        "Apply the front-door criterion to identify an effect through a mediator "
        "when an unmeasured confounder blocks every back-door route.",
        "Derive a DAG's testable conditional-independence implications and "
        "falsify a wrong DAG by checking them against data.",
    ],
    "reading_intro": "Read actively: for each item, write one sentence answering "
        "the 'what to look for' prompt. Bring those sentences to lab.",
    "readings": [
        {"text": "Pearl, Glymour & Jewell, Primer — Chapters 2–3.",
         "look_for": "the three path types (chain, fork, collider) and the exact "
                     "d-separation rule for each — especially the way a collider "
                     "reverses the usual logic."},
        {"text": "Hernán & Robins, Causal Inference: What If — Chapters 6–7.",
         "look_for": "the back-door criterion and how a valid adjustment set is "
                     "chosen — including why some sets are valid and others open "
                     "new biasing paths."},
    ],
    "optional_readings": [
        {"text": "Cunningham, The Mixtape — the DAG chapter.",
         "note": "An applied, code-first tour of back-door paths and collider "
                 "bias with worked examples you can run."},
        {"text": "Textor et al., 'Robust causal inference using DAGs: dagitty.'",
         "note": "The paper behind the dagitty tool you'll use in lab to list "
                 "implied independencies and minimal adjustment sets."},
    ],
    "concept_intro": "A compact recap of the lecture so the packet stands on its own.",
    "concept_sections": [
        {"heading": "The graph IS the assumption set",
         "body": "A DAG (directed acyclic graph) is a set of nodes — the "
            "variables — connected by arrows that mean 'direct cause.' Two things "
            "carry meaning: the arrows you draw (a claimed direct effect) and, "
            "just as importantly, the arrows you DON'T draw (a claimed absence of "
            "direct effect). 'Acyclic' means no variable causes itself through "
            "any loop, which encodes time order. The whole point is that once you "
            "commit to a graph, the right adjustment set is no longer a matter of "
            "taste — it is a mechanical consequence of the geometry."},
        {"heading": "Paths and the three local shapes",
         "body": "A path is any route between two nodes following edges, ignoring "
            "arrow direction. Association flows along paths — but only along OPEN "
            "ones. Every path is built from three elementary triples, and each "
            "behaves differently.",
         "bullets": [
            [("Chain  A → B → C. ", {"bold": True}),
             ("B is a mediator. The path is OPEN; conditioning on B BLOCKS it. "
              "Information flows A→C until you hold B fixed.", {})],
            [("Fork  A ← B → C. ", {"bold": True}),
             ("B is a common cause (confounder). The path is OPEN; conditioning "
              "on B BLOCKS it. This is the back-door path you must close.", {})],
            [("Collider  A → B ← C. ", {"bold": True}),
             ("B is a common effect. The path is BLOCKED by default; conditioning "
              "on B (or any descendant of B) OPENS it. The rule reverses.", {})],
         ],
         "callout": {"title": "The one rule that trips everyone up",
            "color": "RED",
            "lines": ["For chains and forks, conditioning CLOSES the path. For a "
                      "collider, conditioning OPENS it.",
                      "And conditioning on a descendant of a collider opens it "
                      "too — selection on a downstream variable counts."]}},
        {"heading": "d-separation: the master rule",
         "body": "A path is BLOCKED (given a conditioning set Z) if it contains "
            "at least one of: (i) a chain A→B→C or fork A←B→C whose middle node B "
            "is in Z, or (ii) a collider A→B←C whose middle node B is NOT in Z "
            "and no descendant of B is in Z. Two nodes X and Y are d-separated by "
            "Z if EVERY path between them is blocked — and then X ⊥ Y | Z in any "
            "distribution that factorizes over the graph. d-separation is what "
            "converts a drawing into a list of testable independencies.",
         "bullets": [
            [("Open path = a channel for association. ", {"bold": True}),
             ("Even with no causal effect, an open back-door path makes X and Y "
              "dependent.", {})],
            [("Blocked everywhere ⇒ independence. ", {"bold": True}),
             ("If all paths are blocked given Z, the variables are conditionally "
              "independent — a prediction you can check in data.", {})],
        ]},
        {"heading": "Back-door and front-door criteria",
         "body": "These are the two workhorse identification rules you read off a "
            "DAG.",
         "bullets": [
            [("Back-door criterion. ", {"bold": True}),
             ("A set Z is a valid adjustment set for X → Y if (a) no node in Z is "
              "a descendant of X, and (b) Z blocks every path from X to Y that "
              "starts with an arrow INTO X (every 'back-door' path). Then "
              "adjusting for Z identifies the causal effect.", {})],
            [("Front-door criterion. ", {"bold": True}),
             ("When an unmeasured confounder blocks every back-door route, you "
              "can still identify X → Y through a mediator M if X→M→Y is the only "
              "X→Y path, no unblocked back-door from X to M exists, and Y's "
              "back-doors from M are blocked by X. Chain two adjustments "
              "together.", {})],
            [("Minimal vs. valid. ", {"bold": True}),
             ("Many sets satisfy the back-door criterion; prefer a MINIMAL one "
              "(no redundant variables) and never include a collider or a "
              "descendant of X.", {})],
         ],
         "callout": {"title": "Why this matters",
            "color": "BLUE",
            "lines": ["The DAG separates two questions: 'CAN this effect be "
                      "identified?' (back-door/front-door) from 'how well can we "
                      "estimate it?' (next week's regression).",
                      "If no valid adjustment set exists, no regression — however "
                      "fancy — recovers the effect. You need a different design."]}},
        {"heading": "Testable implications: a DAG can be wrong",
         "body": "A DAG is a scientific model, and like any model it makes "
            "predictions you can refute. Each missing edge implies a conditional "
            "independence (via d-separation). If the data clearly violate one of "
            "those independencies, the DAG is falsified — at least one assumed "
            "missing arrow is actually present. This is the antidote to the "
            "complaint that DAGs are 'just opinion': you state the opinion, derive "
            "its consequences, and let the data vote on the ones it can see. "
            "(Note: many distinct DAGs imply the SAME independencies — they form a "
            "Markov-equivalence class — so passing the tests supports but never "
            "uniquely proves a graph.)"},
    ],
    "problem_set": {
        "label": "Problem Set 3",
        "title": "d-separation & adjustment sets",
        "intro": "For each scenario, work entirely from the stated DAG — do not "
            "appeal to the data. Draw the graph first. Where a problem asks for a "
            "path, list it node-by-node and label the middle node of each triple "
            "as chain / fork / collider. Try all five before you look at the "
            "solutions.",
        "problems": [
            {"title": "List and classify every path",
             "prompt": "Consider the DAG: Z → X, Z → Y, X → M → Y, and X → Y "
                "(a direct edge). List every path between X and Y. For the "
                "conditioning set Z = {Z}, classify each path as open or blocked, "
                "and name the triple type that decides each one.",
             "solution_title": "Three paths; given {Z} the back-door is blocked, "
                "the two causal paths stay open.",
             "solution": [
                "Path 1 (direct): X → Y. No intermediate node, so nothing can "
                "block it — OPEN.",
                "Path 2 (mediator): X → M → Y. A chain through M. We are NOT "
                "conditioning on M, so the chain is OPEN (this carries part of the "
                "true effect).",
                "Path 3 (back-door): X ← Z → Y. A fork at Z. Z IS in the "
                "conditioning set, so the fork is BLOCKED — confounding closed.",
                "Verdict: conditioning on {Z} leaves only the two genuine causal "
                "paths (direct + via M) open, exactly what we want for the total "
                "effect of X on Y."]},
            {"title": "Find a minimal valid back-door set",
             "prompt": "A DAG has measured confounders: A → X, A → Y, B → X, "
                "B → Y, and the effect of interest X → Y. There is also a "
                "post-treatment variable M with X → M → Y. Give a minimal set "
                "that satisfies the back-door criterion for X → Y, and say why M "
                "must be excluded.",
             "solution_title": "Adjust for {A, B}; never add M.",
             "solution": [
                "Back-door paths into X: X ← A → Y and X ← B → Y. Both are forks; "
                "blocking them requires conditioning on A and on B.",
                "{A, B} blocks both back-door paths and contains no descendant of "
                "X, so it satisfies the back-door criterion — and dropping either "
                "leaves a path open, so it is minimal.",
                "M is a descendant of X (a mediator on X → M → Y). Including it "
                "violates the criterion's first clause and would block part of "
                "the causal effect — a 'bad control.'",
                "Minimal valid adjustment set: {A, B}."]},
            {"title": "The collider you must not touch",
             "prompt": "In the DAG X → Y, plus X → K ← Y (so K is a common effect "
                "of X and Y), a colleague proposes adjusting for K 'to reduce "
                "noise.' X and Y are marginally associated only through the causal "
                "edge X → Y. Identify K's role and state what happens if you "
                "condition on it.",
             "solution_title": "K is a collider — conditioning on it opens a "
                "spurious X–Y path and biases the estimate.",
             "solution": [
                "The triple X → K ← Y is a collider at K. By default that path is "
                "BLOCKED, so it contributes no association.",
                "Conditioning on K (or any descendant of K) OPENS the collider, "
                "creating a non-causal association between X and Y on top of the "
                "real effect — classic collider / selection bias.",
                "Correct action: leave K out of the model entirely. The valid "
                "estimate of X → Y here needs NO adjustment at all (assuming no "
                "other back-door paths).",
                "Lesson: 'reduces noise' is a prediction instinct; for causal "
                "estimation a collider is poison."]},
            {"title": "When the back door is closed: front-door",
             "prompt": "You want the effect of Smoking (X) on Lung damage (Y), "
                "but an unmeasured genotype U causes both (U → X, U → Y), so no "
                "measured set blocks the back door. You DO measure Tar deposits "
                "(M) on the path X → M → Y, with no arrow from U to M. Can you "
                "identify X → Y, and how?",
             "solution_title": "Yes — use the front-door criterion via Tar (M).",
             "solution": [
                "Back-door fails: X ← U → Y is open and U is unmeasured, so no "
                "adjustment set closes it.",
                "Front-door conditions hold: X→M→Y is the only directed path; the "
                "X→M effect has no open back-door (U does not point to M); and "
                "M→Y's back-door (M ← X ← U → Y) is blocked by conditioning on X.",
                "Estimate in two stages: (1) the effect of X on M (clean, no "
                "confounding), and (2) the effect of M on Y adjusting for X; then "
                "combine them by summing over X.",
                "This recovers X → Y WITHOUT ever measuring U — the front-door's "
                "signature trick."]},
            {"title": "State a testable implication",
             "prompt": "A proposed DAG is: Z → X → Y, with Z → Y absent (no direct "
                "Z→Y edge). Z is a measured instrument-like cause of X only. State "
                "one conditional-independence implication of this DAG that you "
                "could test in data, and say what a violation would mean.",
             "solution_title": "The DAG implies Z ⊥ Y | X; a violation falsifies "
                "the 'no direct Z→Y edge' assumption.",
             "solution": [
                "The only path from Z to Y is Z → X → Y, a chain through X.",
                "Conditioning on X blocks that chain, so d-separation gives "
                "Z ⊥ Y | X — Z should carry no information about Y once X is held "
                "fixed.",
                "Test it: regress Y on X and Z; the coefficient on Z should be "
                "indistinguishable from zero (or use a partial-correlation / "
                "conditional-independence test).",
                "If Z still predicts Y given X, the assumed-missing Z → Y edge (or "
                "an unblocked back-door) is really there — the DAG is falsified."]},
        ],
    },
    "lab": {
        "label": "Lab 2",
        "title": "Encode a DAG",
        "goal": "encode a small DAG in code, enumerate the conditional "
            "independencies it implies, test one of them against simulated data, "
            "and read off a valid back-door adjustment set — proving you can move "
            "from a drawing to a defensible analysis plan.",
        "steps": [
            {"heading": "Step 1 · Encode the DAG as structure",
             "body": "Represent the graph by its directed edges. In Python a dict "
                "of parents (or an edge list) is enough to reason about; in R, "
                "dagitty gives you the same graph plus built-in queries. We will "
                "use the smoking → cardiovascular-disease graph from lecture: a "
                "confounder Age, a mediator Blood pressure, and a collider "
                "Hospitalized.",
             "code_python": "# Edge list: parent -> child. This is our entire 'model'.\n"
                "edges = [\n"
                "    ('Age', 'Smoking'), ('Age', 'CVD'),        # Age confounds\n"
                "    ('Smoking', 'BP'), ('BP', 'CVD'),          # mediator path\n"
                "    ('Smoking', 'CVD'),                        # direct effect\n"
                "    ('Smoking', 'Hosp'), ('CVD', 'Hosp'),      # collider\n"
                "]\n"
                "parents = {}\n"
                "for p, c in edges:\n"
                "    parents.setdefault(c, set()).add(p)\n"
                "    parents.setdefault(p, parents.get(p, set()))\n"
                "print('parents of CVD:', parents['CVD'])",
             "code_r": 'library(dagitty)\n'
                'g <- dagitty(\'dag {\n'
                '  Age -> Smoking  Age -> CVD\n'
                '  Smoking -> BP   BP -> CVD\n'
                '  Smoking -> CVD\n'
                '  Smoking -> Hosp CVD -> Hosp\n'
                '}\')\n'
                'plot(graphLayout(g))'},
            {"heading": "Step 2 · List the implied conditional independencies",
             "body": "Every missing edge is a testable claim. dagitty enumerates "
                "them for you; in Python we reason from d-separation. The key "
                "implication we'll test: Age ⊥ BP | Smoking (Age reaches BP only "
                "through Smoking).",
             "code_python": "# Age -> BP only via Smoking, so conditioning on\n"
                "# Smoking should d-separate Age from BP.\n"
                "implications = [\n"
                "    ('Age', 'BP', {'Smoking'}),    # chain blocked by Smoking\n"
                "    ('Age', 'Hosp', {'Smoking', 'CVD'}),  # all paths blocked\n"
                "]\n"
                "for x, y, z in implications:\n"
                "    print(f'{x} _||_ {y} | {sorted(z)}')",
             "code_r": '# dagitty derives every implied independence:\n'
                'print(impliedConditionalIndependencies(g))'},
            {"heading": "Step 3 · Test one implication against simulated data",
             "body": "Simulate from the graph (so the implication is TRUE by "
                "construction), then check Age ⊥ BP | Smoking by adding Age to a "
                "regression of BP on Smoking — its coefficient should be ~0.",
             "code_python": "import numpy as np, statsmodels.api as sm\n"
                "rng = np.random.default_rng(4)\nn = 5000\n"
                "Age = rng.normal(size=n)\n"
                "Smoking = 0.8*Age + rng.normal(size=n)\n"
                "BP = 1.0*Smoking + rng.normal(size=n)   # Age affects BP only via Smoking\n"
                "# Coefficient on Age, controlling for Smoking, should be ~0:\n"
                "X = sm.add_constant(np.c_[Smoking, Age])\n"
                "b = sm.OLS(BP, X).fit().params\n"
                'print(f"coef on Smoking={b[1]:.3f}  coef on Age={b[2]:.3f} (~0 expected)")',
             "code_r": '# In R, localTests() compares each implication to the data:\n'
                'df <- data.frame(Age, Smoking, BP)\n'
                'print(localTests(g, df, type = "cis"))'},
            {"heading": "Step 4 · Read off a valid adjustment set",
             "body": "For the TOTAL effect of Smoking on CVD, the only back-door "
                "path is Smoking ← Age → CVD, so {Age} closes it. Do NOT adjust "
                "for BP (mediator) or Hosp (collider). dagitty's adjustmentSets() "
                "confirms this automatically.",
             "code_python": "# Back-door paths into Smoking for Smoking -> CVD:\n"
                "#   Smoking <- Age -> CVD   (fork at Age)  => adjust for Age\n"
                "# BP is a mediator (on the causal path) -> exclude.\n"
                "# Hosp is a collider (common effect)      -> exclude.\n"
                "valid_set = {'Age'}\n"
                "print('Valid back-door adjustment set for Smoking -> CVD:', valid_set)",
             "code_r": 'print(adjustmentSets(g, exposure = "Smoking",\n'
                '                      outcome = "CVD", effect = "total"))'},
        ],
        "expected": "Step 3 prints a Smoking coefficient near 1.0 and an Age "
            "coefficient statistically indistinguishable from 0 — confirming "
            "Age ⊥ BP | Smoking, exactly as the DAG predicts. Step 4 returns "
            "{Age} as the (minimal) valid adjustment set. You have gone from a "
            "hand-drawn graph to a verified, defensible analysis plan without "
            "touching the outcome model itself.",
        "submit": [
            "Push your DAG encoding, the localTests / regression output, and the "
            "adjustment set to week04/ in your repository.",
            "In the README, write two sentences: which implication you tested and "
            "whether the data were consistent with the DAG.",
            "Bring one DAG from your own field (3–6 nodes) to lab, with the "
            "back-door set you'd use marked.",
        ],
    },
    "self_check": [
        "Given any triple, say instantly whether it is a chain, fork, or "
        "collider, and whether conditioning opens or closes it.",
        "State the d-separation rule for colliders from memory, including the "
        "descendant clause.",
        "Find a minimal valid back-door adjustment set for a 5-node DAG.",
        "Explain when the front-door criterion rescues you and why.",
        "Write down one testable conditional independence implied by a DAG and "
        "describe the regression that checks it.",
    ],
    "next_week": {
        "heading": "Coming up: Week 5 — Regression & adjustment",
        "teaser": "With the DAG telling us WHAT to adjust for, we turn to HOW. "
            "You'll see exactly what a regression coefficient estimates when the "
            "adjustment set is right, how functional-form mistakes and bad "
            "controls creep back in, and why 'controlling for' a variable is just "
            "one way to block a back-door path. Skim Hernán & Robins Chapter "
            "15 to get a head start.",
    },

    # -------------------------------------------------------------------- deck
    "deck": [
        {"type": "title"},
        {"type": "agenda", "title": "What we will cover in Week 4", "items": [
            {"t": "Nodes, edges, paths", "d": "The vocabulary of a causal graph "
             "and what an arrow claims."},
            {"t": "Three local shapes", "d": "Chain, fork, collider — and the way "
             "each transmits association."},
            {"t": "d-separation", "d": "The master rule for when a path is open or "
             "blocked."},
            {"t": "Back-door & front-door", "d": "Reading a valid adjustment set "
             "straight off the graph."},
            {"t": "Testable implications", "d": "How a DAG predicts independencies "
             "— and can be falsified."},
            {"t": "Build & apply a DAG", "d": "Smoking → CVD, end to end, from "
             "domain knowledge."},
        ]},
        {"type": "content", "kicker": "Why graphs",
         "title": "A DAG is your assumptions, made visible and arguable",
         "bullets": [
            "Last week: confounder / mediator / collider as a checklist. This "
            "week: the algebra that generates the checklist.",
            "A graph makes assumptions explicit — collaborators can point at an "
            "arrow and disagree.",
            ("Arrows present = claimed direct cause.", 1),
            ("Arrows absent = claimed NO direct cause (often the stronger claim).", 1),
            "From the picture alone, the right adjustment set becomes a "
            "mechanical read-off, not a judgment call.",
         ],
         "note": {"title": "The payoff",
            "body": "Draw the graph once; it answers 'what do I control for?' and "
            "'is the effect even identifiable?' for free."}},
        {"type": "content", "kicker": "Definitions",
         "title": "Nodes, edges, and what 'acyclic' buys us", "bullets": [
            "Nodes are variables; a directed edge X → Y means X is a DIRECT cause "
            "of Y.",
            "A path is any chain of edges between two nodes, ignoring arrow "
            "direction.",
            "Directed (arrows) + Acyclic (no loops) = a consistent time order; "
            "nothing causes itself.",
            "Unobserved variables get drawn too (dashed) — they're assumptions, "
            "not data.",
         ],
         "note": {"title": "Path ≠ causal path",
            "body": "A path can run against arrows. Only paths that follow arrows "
            "tip-to-tail are CAUSAL paths."}},

        {"type": "section", "kicker": "Part 1", "title": "The three local shapes",
         "subtitle": "Every path is built from chains, forks, and colliders. Learn "
            "these three triples and you can read any graph."},
        {"type": "compare", "kicker": "The building blocks",
         "title": "Chain, fork, collider", "columns": [
            {"head": "CHAIN", "sub": "A → B → C", "points": [
                "B is a mediator.",
                "Open by default.",
                "Condition on B → BLOCKS it.",
                "Carries causal flow A to C."]},
            {"head": "FORK", "sub": "A ← B → C", "points": [
                "B is a common cause.",
                "Open by default.",
                "Condition on B → BLOCKS it.",
                "The back-door / confounding path."]},
            {"head": "COLLIDER", "sub": "A → B ← C", "points": [
                "B is a common effect.",
                "BLOCKED by default.",
                "Condition on B → OPENS it.",
                "The rule reverses here."]},
         ]},
        {"type": "content", "kicker": "The reversal",
         "title": "Why a collider behaves backwards", "bullets": [
            "A → B ← C: A and C are two independent causes funneling into B.",
            "Learn B's value and the causes must 'trade off' to explain it — so "
            "they become dependent.",
            "Grass is wet (the collider): learning it rained makes the sprinkler "
            "less likely — one cause explains the effect away.",
            ("Conditioning on a DESCENDANT of B opens it too — selection counts.", 1),
         ],
         "note": {"title": "Intuition",
            "body": "Explaining away: given the common effect, evidence for one "
            "cause is evidence against the other."}},
        {"type": "statement",
         "quote": "Chains and forks: conditioning CLOSES. Colliders: conditioning "
            "OPENS.",
         "attribution": "This single asymmetry is the source of nearly every "
            "subtle mistake in applied causal work — and the reason 'control for "
            "everything' backfires."},

        {"type": "section", "kicker": "Part 2", "title": "d-separation",
         "subtitle": "The master rule that turns a graph into a list of "
            "conditional independencies you can test."},
        {"type": "content", "kicker": "The rule",
         "title": "When is a path blocked?", "bullets": [
            "A path is BLOCKED given Z if ANY triple on it is blocked.",
            "Chain A→B→C or fork A←B→C: blocked when B ∈ Z.",
            "Collider A→B←C: blocked when B ∉ Z AND no descendant of B is in Z.",
            "X and Y are d-separated by Z if EVERY path between them is blocked.",
         ],
         "note": {"title": "Payoff",
            "body": "d-separated by Z ⇒ X ⊥ Y | Z in any distribution that "
            "factorizes over the graph."}},
        {"type": "steps", "kicker": "How to check a path",
         "title": "Walk the path, triple by triple", "steps": [
            {"title": "List the path", "body": "— write the nodes in order from X "
             "to Y."},
            {"title": "Find each triple", "body": "— is the middle node a chain, "
             "fork, or collider?"},
            {"title": "Apply the rule", "body": "— chain/fork blocked if in Z; "
             "collider blocked if it (and its descendants) are out of Z."},
            {"title": "Verdict", "body": "— one blocked triple blocks the whole "
             "path."},
         ],
         "note": "Repeat for every path. All blocked ⇒ conditional independence."},
        {"type": "table", "kicker": "The rule on one slide",
         "title": "Open vs. blocked, by triple and conditioning",
         "headers": ["Triple", "Middle node", "Not in Z", "In Z"],
         "rows": [
            ["Chain  A→B→C", "mediator", "OPEN", "blocked"],
            ["Fork  A←B→C", "confounder", "OPEN", "blocked"],
            ["Collider  A→B←C", "common effect", "blocked", "OPEN"],
            ["…descendant of collider", "downstream", "blocked", "OPEN"],
         ],
         "note": {"title": "Read across",
            "body": "The collider rows are the mirror image of the others — that's "
            "the whole subtlety."}},

        {"type": "section", "kicker": "Part 3", "title": "Back-door criterion",
         "subtitle": "From d-separation to a recipe: which variables to adjust for "
            "so a regression estimates the causal effect."},
        {"type": "content", "kicker": "Back-door paths",
         "title": "Block every path that sneaks in through the back", "bullets": [
            "A back-door path from X to Y starts with an arrow INTO X "
            "(e.g. X ← Z → Y).",
            "These carry non-causal association — confounding — that biases X → Y.",
            "Adjustment set Z is valid if it blocks all back-door paths AND "
            "contains no descendant of X.",
            "Then adjusting for Z (stratify / regress / weight) identifies the "
            "effect.",
         ],
         "note": {"title": "Two clauses",
            "body": "(1) block every back-door path; (2) include no descendant of "
            "X. Both are required."}},
        {"type": "content", "kicker": "Choosing the set",
         "title": "Valid, minimal, and what to never include", "bullets": [
            "Often several sets are valid — prefer a MINIMAL one (no redundant "
            "variables).",
            "Never include a mediator (on the X→Y path): it blocks the effect you "
            "want.",
            "Never include a collider: conditioning opens a new biasing path.",
            "Pre-treatment ≠ safe — an M-bias collider can be pre-treatment.",
         ],
         "note": {"title": "Smaller is safer",
            "body": "Each extra control is a chance to accidentally open a path. "
            "Adjust for what the DAG requires, no more."}},
        {"type": "compare", "kicker": "The good, the bad",
         "title": "Adjust for these — not those", "columns": [
            {"head": "DO adjust for", "sub": "confounders", "points": [
                "Common causes of X and Y.",
                "Block open back-door forks.",
                "X ← Z → Y: condition on Z."]},
            {"head": "DON'T adjust for", "sub": "mediators", "points": [
                "Nodes on the X → Y path.",
                "Removes part of the effect.",
                "X → M → Y: leave M alone."]},
            {"head": "NEVER adjust for", "sub": "colliders", "points": [
                "Common effects of X and Y.",
                "Opens a spurious path.",
                "X → K ← Y: keep K out."]},
         ]},

        {"type": "section", "kicker": "Part 4", "title": "Front-door criterion",
         "subtitle": "When every back door is jammed by an unmeasured confounder, "
            "a clean mediator can still identify the effect."},
        {"type": "content", "kicker": "The setup",
         "title": "Identification when no back-door set exists", "bullets": [
            "Unmeasured U confounds X and Y, so NO measured set blocks the back "
            "door.",
            "But a measured mediator M sits on the only causal path X → M → Y.",
            "U does not touch M — so X → M is unconfounded, and M → Y is "
            "confounded only by X (which we measure).",
            "Chain the two clean sub-effects to recover X → Y.",
         ],
         "note": {"title": "Canonical case",
            "body": "Smoking → Tar → Lung damage, with a hidden genotype "
            "confounding smoking and damage but not tar."}},
        {"type": "steps", "kicker": "Two stages",
         "title": "How the front-door estimate is built", "steps": [
            {"title": "Stage 1", "body": "— estimate X → M (no back-door into M; "
             "clean)."},
            {"title": "Stage 2", "body": "— estimate M → Y adjusting for X (closes "
             "M's back-door)."},
            {"title": "Combine", "body": "— sum the chained effect over the "
             "distribution of X."},
         ],
         "note": "The effect is identified WITHOUT ever measuring the confounder U."},
        {"type": "compare", "kicker": "Two doors, two situations",
         "title": "Back-door vs. front-door", "columns": [
            {"head": "Back-door", "points": [
                "Block confounding paths directly.",
                "Needs the confounders MEASURED.",
                "The default, most common tool."]},
            {"head": "Front-door", "points": [
                "Route identification through a mediator.",
                "Works with the confounder UNMEASURED.",
                "Rare but powerful; strict assumptions."]},
         ]},

        {"type": "section", "kicker": "Part 5", "title": "Testable implications",
         "subtitle": "A DAG is a falsifiable model: every missing arrow is a "
            "prediction the data can refute."},
        {"type": "content", "kicker": "Falsifying a DAG",
         "title": "Missing edges make checkable claims", "bullets": [
            "Each absent edge ⇒ a conditional independence implied by "
            "d-separation.",
            "Test it: the relevant partial correlation / coefficient should be "
            "≈ 0.",
            "A clear violation means an assumed-missing arrow is actually present "
            "— the DAG is wrong.",
            ("Caveat: equivalent DAGs share implications, so tests support but "
             "never uniquely prove a graph.", 1),
         ],
         "note": {"title": "Honest modeling",
            "body": "DAGs aren't 'just opinion' — they state the opinion AND its "
            "refutable consequences."}},
        {"type": "table", "kicker": "Worked example",
         "title": "Implications of Z → X → Y (no Z→Y edge)",
         "headers": ["Question", "Path Z to Y", "Implication"],
         "rows": [
            ["Marginal", "Z → X → Y (open chain)", "Z and Y ASSOCIATED"],
            ["Given X", "chain blocked at X", "Z ⊥ Y | X  (test this)"],
            ["If it fails", "Z still predicts Y | X", "missing Z→Y edge exists"],
         ],
         "note": {"title": "The test",
            "body": "Regress Y on X and Z; coefficient on Z ≈ 0 supports the DAG, "
            "≠ 0 falsifies it."}},

        {"type": "section", "kicker": "Part 6",
         "title": "Building a DAG from domain knowledge",
         "subtitle": "A structured workflow: list variables, draw causes by time "
            "order, mark the unobserved, then read off the analysis."},
        {"type": "steps", "kicker": "From knowledge to graph",
         "title": "How to build a DAG you can defend", "steps": [
            {"title": "Enumerate", "body": "— list the exposure, outcome, and "
             "every plausibly relevant variable."},
            {"title": "Order in time", "body": "— earlier causes later; this rules "
             "out cycles."},
            {"title": "Draw causes", "body": "— add an arrow only for a DIRECT "
             "effect you'd defend."},
            {"title": "Mark unknowns", "body": "— include suspected unmeasured "
             "confounders (dashed)."},
            {"title": "Read off", "body": "— adjustment set + testable "
             "implications fall out."},
         ],
         "note": "Domain knowledge goes IN as arrows; identification comes OUT for "
            "free."},
        {"type": "content", "kicker": "Case study · epidemiology",
         "title": "Smoking → cardiovascular disease", "bullets": [
            "Exposure Smoking, outcome CVD. Age causes both (confounder: "
            "Smoking ← Age → CVD).",
            "Blood pressure is a mediator: Smoking → BP → CVD (plus a direct "
            "Smoking → CVD).",
            "Hospitalization is a collider: Smoking → Hosp ← CVD — never condition "
            "on it.",
            "Total effect ⇒ adjust for {Age} only; leave BP and Hosp out.",
         ],
         "note": {"title": "One graph, three lessons",
            "body": "A confounder to adjust, a mediator to leave, a collider to "
            "avoid — all in five nodes."}},
        {"type": "table", "kicker": "Reading the smoking DAG",
         "title": "Each node's role and the verdict",
         "headers": ["Node", "Role", "Adjust for it?"],
         "rows": [
            ["Age", "confounder (fork)", "YES — closes back door"],
            ["Blood pressure", "mediator (chain)", "No — it's the effect"],
            ["Hospitalized", "collider", "Never — opens bias"],
            ["Genotype (unobs.)", "possible confounder", "Can't — consider "
             "front-door"],
         ],
         "note": {"title": "Testable implication",
            "body": "Age ⊥ BP | Smoking — the lab tests exactly this on simulated "
            "data."}},

        {"type": "section", "kicker": "Part 7", "title": "This week's work",
         "subtitle": "Problem Set 3 trains your eye; Lab 2 takes a DAG all the way "
            "to a verified adjustment set."},
        {"type": "steps", "kicker": "Problem Set 3",
         "title": "d-separation & adjustment sets", "steps": [
            {"title": "Classify paths", "body": "— list and label every path as "
             "open or blocked."},
            {"title": "Find the set", "body": "— a minimal valid back-door "
             "adjustment set."},
            {"title": "Spot the collider", "body": "— the variable you must NOT "
             "condition on."},
            {"title": "Front-door", "body": "— identify an effect when the back "
             "door is closed."},
            {"title": "Falsify", "body": "— state a testable conditional "
             "independence."},
         ],
         "note": "Work from the DAG, not the data — that is the whole skill."},
        {"type": "steps", "kicker": "Lab 2 · Encode a DAG",
         "title": "From a drawing to a defensible plan", "steps": [
            {"title": "Encode", "body": "— the DAG as edges (Python) or dagitty "
             "(R)."},
            {"title": "List", "body": "— the conditional independencies it "
             "implies."},
            {"title": "Test", "body": "— one implication against simulated data."},
            {"title": "Read off", "body": "— the valid back-door adjustment set."},
         ],
         "note": "You'll verify Age ⊥ BP | Smoking and recover {Age} as the "
            "adjustment set."},
        {"type": "statement",
         "quote": "Draw the graph; the analysis follows.",
         "attribution": "Next week we cash in the adjustment set: regression and "
            "control, what a coefficient really estimates, and how bad controls "
            "sneak back in. See you in lab."},
    ],

    # ---------------------------------------------------------------- notebook
    "notebook": [
        {"md": "## 1 · A graph you can simulate\n\n"
            "A DAG is just a set of structural equations: each variable is a "
            "function of its parents plus noise. Because we *write* those "
            "equations, we know the true graph exactly — so we can check what "
            "d-separation predicts against what the data actually do.\n\n"
            "Throughout we use a simple test: **X and Y are (conditionally) "
            "independent iff the coefficient on X, when we regress Y on X (and the "
            "conditioning set), is ≈ 0.** A near-zero slope ⇒ independence; a "
            "clearly non-zero slope ⇒ dependence."},
        {"code": "import statsmodels.api as sm\n\n"
            "def slope(y, *cols):\n"
            "    \"\"\"OLS slope on the FIRST regressor, adjusting for the rest.\n"
            "    Returns (coef, p_value) — coef≈0 ⇔ (conditional) independence.\"\"\"\n"
            "    Xmat = sm.add_constant(np.column_stack(cols))\n"
            "    fit = sm.OLS(np.asarray(y), Xmat).fit()\n"
            "    return fit.params[1], fit.pvalues[1]\n\n"
            "n = 10_000\n"
            "print('Helper ready. We will read off (coef, p) to judge independence.')"},
        {"md": "## 2 · The fork (confounder):  X ← Z → Y\n\n"
            "Z is a common cause of X and Y, with **no** arrow X → Y. d-separation "
            "says the fork is OPEN marginally (so X and Y look associated) but "
            "BLOCKED given Z (so `X ⊥ Y | Z`). Adjusting for Z therefore removes "
            "the confounding entirely."},
        {"code": "# Fork: Z -> X, Z -> Y, and NO direct X->Y edge (true effect = 0).\n"
            "Z = RNG.normal(size=n)\n"
            "Xf = 1.0*Z + RNG.normal(size=n)\n"
            "Yf = 2.0*Z + RNG.normal(size=n)        # depends on Z only, not on X\n\n"
            "c_marg, p_marg = slope(Yf, Xf)         # X alone\n"
            "c_cond, p_cond = slope(Yf, Xf, Z)      # X adjusting for Z\n"
            "print(f'marginal   X->Y slope = {c_marg:+.3f}  (p={p_marg:.1e})  '\n"
            "      '<- spurious, fork is OPEN')\n"
            "print(f'given Z    X->Y slope = {c_cond:+.3f}  (p={p_cond:.2f})  '\n"
            "      '<- ~0, fork BLOCKED by Z')\n"
            "print('\\nTrue X->Y effect is 0. Adjusting for Z recovers it.')\n"
            "assert abs(c_marg) > 0.3,  'fork should look associated marginally'\n"
            "assert abs(c_cond) < 0.1,  'conditioning on Z should give independence'"},
        {"md": "The marginal slope is large and the conditional slope collapses to "
            "~0: exactly `X ⊥ Y | Z`. **This is why we adjust for confounders** — "
            "conditioning on the fork's middle node blocks the back-door path."},
        {"md": "## 3 · The chain (mediator):  X → M → Y\n\n"
            "Now X causes Y, but only *through* M. d-separation says the chain is "
            "OPEN marginally (X and Y associated) and BLOCKED given M "
            "(`X ⊥ Y | M`). Conditioning on a mediator removes the very effect we "
            "usually want — the mirror image of the fork's lesson."},
        {"code": "# Chain: X -> M -> Y. The TOTAL effect of X on Y is 1.0*1.0 = 1.0.\n"
            "Xc = RNG.normal(size=n)\n"
            "M  = 1.0*Xc + RNG.normal(size=n)\n"
            "Yc = 1.0*M  + RNG.normal(size=n)       # Y depends on X only via M\n\n"
            "c_tot,  p_tot  = slope(Yc, Xc)         # total effect\n"
            "c_cond, p_cond = slope(Yc, Xc, M)      # adjusting for the mediator\n"
            "print(f'marginal   X->Y slope = {c_tot:+.3f}  (p={p_tot:.1e})  '\n"
            "      '<- total effect ~1.0, chain OPEN')\n"
            "print(f'given M    X->Y slope = {c_cond:+.3f}  (p={p_cond:.2f})  '\n"
            "      '<- ~0, chain BLOCKED by M')\n"
            "assert abs(c_tot - 1.0) < 0.1, 'total effect should be ~1.0'\n"
            "assert abs(c_cond) < 0.1,      'conditioning on M should block the path'"},
        {"md": "Same arithmetic as the fork — conditioning on the middle node "
            "blocks the path — but here the path was the *causal* one. Adjusting "
            "for a mediator wrongly zeros out a real effect. The graph, not the "
            "regression, tells you which middle node is which."},
        {"md": "## 4 · The collider:  X → K ← Y  (the rule reverses)\n\n"
            "K is a common effect of X and Y, which are otherwise independent. "
            "d-separation says the collider is BLOCKED marginally (`X ⊥ Y`) but "
            "OPENS when we condition on K. So conditioning *creates* an "
            "association that was not there — collider bias."},
        {"code": "# Collider: X and Y independent; both cause K.\n"
            "Xk = RNG.normal(size=n)\n"
            "Yk = RNG.normal(size=n)                # independent of X by construction\n"
            "K  = 1.0*Xk + 1.0*Yk + RNG.normal(size=n)\n\n"
            "c_marg, p_marg = slope(Yk, Xk)         # X alone\n"
            "c_cond, p_cond = slope(Yk, Xk, K)      # conditioning on the collider\n"
            "print(f'marginal   X->Y slope = {c_marg:+.3f}  (p={p_marg:.2f})  '\n"
            "      '<- ~0, collider BLOCKED (true independence)')\n"
            "print(f'given K    X->Y slope = {c_cond:+.3f}  (p={p_cond:.1e})  '\n"
            "      '<- non-zero! conditioning OPENED the path')\n"
            "assert abs(c_marg) < 0.05,            'X and Y are truly independent'\n"
            "assert c_cond < -0.2,                 'conditioning on K induces (negative) assoc.'"},
        {"md": "Marginally `X ⊥ Y` (slope ≈ 0); conditioning on K induces a strong "
            "**negative** association out of thin air. This is the asymmetry that "
            "makes 'control for everything' dangerous: the collider's rule is the "
            "reverse of the chain's and fork's."},
        {"md": "### 🔧 Exercise 4.1 — open a collider through its DESCENDANT\n\n"
            "d-separation says conditioning on a *descendant* of a collider also "
            "opens it. Extend the collider world with `D = K + noise` (so D is a "
            "child of K), then show that conditioning on **D** — not K itself — "
            "still induces an X–Y association.\n\n"
            "Fill in the `# TODO`s. The skeleton runs as-is (it just prints "
            "`None`s) until you complete it."},
        {"code": "# TODO: build D as a descendant of the collider K, then condition on D.\n"
            "D = ...        # TODO: D = 1.0*K + RNG.normal(size=n)\n"
            "c_d = None     # TODO: c_d, _ = slope(Yk, Xk, D)\n"
            "# print(f'given D (descendant of K): X->Y slope = {c_d:+.3f}')"},
        {"md": "### ✅ Solution 4.1"},
        {"code": "D = 1.0*K + RNG.normal(size=n)        # D is a child of the collider K\n"
            "c_d, p_d = slope(Yk, Xk, D)\n"
            "print(f'given D (descendant of K): X->Y slope = {c_d:+.3f}  (p={p_d:.1e})')\n"
            "print('Conditioning on a descendant of a collider opens it too.')\n"
            "assert abs(c_d) > 0.1, 'descendant of a collider should still open the path'"},
        {"md": "## 5 · Back-door adjustment vs. over-adjustment\n\n"
            "Now a realistic graph with a **real** effect to recover and two ways "
            "to get it wrong. Confounder Z opens a back-door; collider K tempts "
            "you to over-adjust.\n\n"
            "```\n"
            "  Z → X ,  Z → Y        (back-door fork — must close)\n"
            "  X → Y                 (TRUE causal effect = 1.5)\n"
            "  X → K ← Y             (collider — must NOT touch)\n"
            "```\n"
            "The back-door criterion says: adjust for **{Z}**, and for nothing "
            "else."},
        {"code": "TRUE = 1.5\n"
            "Z = RNG.normal(size=n)\n"
            "X = 1.0*Z + RNG.normal(size=n)\n"
            "Y = TRUE*X + 2.0*Z + RNG.normal(size=n)     # true X->Y = 1.5\n"
            "K = 1.0*X + 1.0*Y + RNG.normal(size=n)       # collider (common effect)\n\n"
            "naive,   _ = slope(Y, X)              # back-door left OPEN\n"
            "correct, _ = slope(Y, X, Z)           # back-door CLOSED (valid set {Z})\n"
            "over,    _ = slope(Y, X, Z, K)        # also conditioning on collider K\n\n"
            "print(f'TRUE effect            = {TRUE:.3f}')\n"
            "print(f'naive  (no adjust)     = {naive:.3f}   <- confounded, too high')\n"
            "print(f'adjust {{Z}}            = {correct:.3f}   <- recovers the truth')\n"
            "print(f'adjust {{Z, K}}         = {over:.3f}   <- collider bias, wrong again')\n"
            "assert abs(correct - TRUE) < 0.1, 'back-door set {Z} should recover 1.5'\n"
            "assert abs(over - TRUE)    > 0.1, 'adding the collider K should bias it'"},
        {"md": "Three estimates from one dataset: only the **back-door set {Z}** "
            "lands on 1.5. Leaving Z out keeps confounding; adding the collider K "
            "*introduces* new bias. The valid adjustment set is the Goldilocks "
            "choice the DAG hands you — neither too few controls nor too many."},
        {"md": "### 🔧 Exercise 5.1 — find the valid set yourself\n\n"
            "New graph: two confounders `A` and `B` both cause `X` and `Y`; the "
            "true effect of `X` on `Y` is **0.8**; there is also a mediator "
            "`X → Mp → Y` and a collider `X → C ← Y`. Estimate X → Y four ways and "
            "decide which adjustment set is valid.\n\n"
            "Complete the `# TODO`s so all four estimates print."},
        {"code": "TRUE2 = 0.8\n"
            "A = RNG.normal(size=n)\n"
            "B = RNG.normal(size=n)\n"
            "X2 = 0.7*A + 0.7*B + RNG.normal(size=n)\n"
            "# Y2 below uses X2, A, B; build it so the DIRECT effect of X2 is 0.8:\n"
            "Mp = 0.0*X2 + RNG.normal(size=n)             # (kept off the path for simplicity)\n"
            "Y2 = TRUE2*X2 + 1.0*A + 1.0*B + RNG.normal(size=n)\n"
            "Cc = 1.0*X2 + 1.0*Y2 + RNG.normal(size=n)    # collider\n\n"
            "est_none = None   # TODO: slope(Y2, X2)\n"
            "est_AB   = None   # TODO: slope(Y2, X2, A, B)\n"
            "est_ABC  = None   # TODO: slope(Y2, X2, A, B, Cc)   # adds the collider\n"
            "# print(est_none, est_AB, est_ABC)"},
        {"md": "### ✅ Solution 5.1\n\n"
            "The valid set is **{A, B}** (both confounders, no collider, no "
            "mediator). Adjusting for the collider `Cc` on top of {A, B} "
            "re-introduces bias."},
        {"code": "est_none, _ = slope(Y2, X2)\n"
            "est_AB,   _ = slope(Y2, X2, A, B)\n"
            "est_ABC,  _ = slope(Y2, X2, A, B, Cc)\n"
            "print(f'TRUE              = {TRUE2:.3f}')\n"
            "print(f'no adjustment     = {est_none:.3f}   (confounded)')\n"
            "print(f'adjust {{A, B}}     = {est_AB:.3f}   (valid -> recovers truth)')\n"
            "print(f'adjust {{A,B,C}}    = {est_ABC:.3f}   (collider bias)')\n"
            "assert abs(est_AB - TRUE2) < 0.1, 'valid set {A,B} should recover 0.8'\n"
            "assert abs(est_ABC - TRUE2) > 0.05, 'adding collider C should bias the estimate'"},
        {"md": "## 6 · Falsifying a DAG with its testable implication\n\n"
            "A DAG predicts conditional independencies. Take the chain "
            "`Z → X → Y` (no direct Z→Y edge): it implies **`Z ⊥ Y | X`**. We "
            "simulate two worlds — one that obeys the DAG and one with a sneaky "
            "extra `Z → Y` edge — and let the test tell them apart."},
        {"code": "# World A obeys the DAG: Z -> X -> Y, no direct Z->Y.\n"
            "Zc  = RNG.normal(size=n)\n"
            "Xc2 = 1.0*Zc + RNG.normal(size=n)\n"
            "Ya  = 1.0*Xc2 + RNG.normal(size=n)            # no direct Z effect\n\n"
            "# World B violates it: a hidden direct Z -> Y edge sneaks in.\n"
            "Yb  = 1.0*Xc2 + 0.8*Zc + RNG.normal(size=n)   # direct Z->Y present\n\n"
            "cA, pA = slope(Ya, Zc, Xc2)   # coef on Z given X — should be ~0 if DAG holds\n"
            "cB, pB = slope(Yb, Zc, Xc2)\n"
            "print(f'World A: coef(Z | X) = {cA:+.3f}  (p={pA:.2f})  -> Z _||_ Y | X holds, DAG OK')\n"
            "print(f'World B: coef(Z | X) = {cB:+.3f}  (p={pB:.1e})  -> implication VIOLATED, DAG falsified')\n"
            "assert abs(cA) < 0.05,        'World A should satisfy Z _||_ Y | X'\n"
            "assert abs(cB) > 0.3,         'World B should violate the implication'"},
        {"md": "The same conditional-independence test that *holds* in World A "
            "*fails* in World B. That is a DAG earning its keep: it made a "
            "prediction, and the data in World B refuted the assumed-missing "
            "`Z → Y` edge. (Remember the caveat: passing such tests is necessary, "
            "not sufficient — Markov-equivalent DAGs share these implications.)"},
        {"md": "### 🔧 Exercise 6.1 — derive and test a different implication\n\n"
            "In the back-door world from section 5 (`Z → X`, `Z → Y`, `X → Y`), "
            "the graph implies **no** unconditional independence between X and Y "
            "(they're linked both directly and through Z). But it DOES imply that "
            "`Z` and `Y` are *dependent*. As a contrast, build a fresh variable "
            "`W` that causes **nothing** (`W ⊥ everything`) and confirm "
            "`W ⊥ Y` — a trivially true implication of 'W has no edges.'\n\n"
            "Complete the `# TODO`."},
        {"code": "# TODO: W is disconnected from the graph; it should be independent of Y.\n"
            "W = ...          # TODO: W = RNG.normal(size=n)\n"
            "c_w = None       # TODO: c_w, p_w = slope(Y, W)\n"
            "# print(f'coef(W -> Y) = {c_w:+.3f}  (expect ~0)')"},
        {"md": "### ✅ Solution 6.1"},
        {"code": "W = RNG.normal(size=n)\n"
            "c_w, p_w = slope(Y, W)\n"
            "print(f'coef(W -> Y) = {c_w:+.3f}  (p={p_w:.2f})  -> W _||_ Y, as a node with no edges must be')\n"
            "# The honest independence test is the p-value: no evidence of a W->Y link.\n"
            "assert p_w > 0.01, 'a disconnected node must be independent of Y'\n"
            "assert abs(c_w) < 0.1, 'the slope should be small (near zero)'"},
        {"md": "## 7 · Wrap-up & self-check\n\n"
            "- A DAG is structural equations you can simulate; **d-separation** "
            "predicts which (conditional) independencies hold.\n"
            "- **Fork** `X←Z→Y` and **chain** `X→M→Y`: conditioning on the middle "
            "node BLOCKS the path (`X ⊥ Y | middle`).\n"
            "- **Collider** `X→K←Y`: blocked by default, and conditioning on K "
            "(or a descendant of K) OPENS it — manufacturing association.\n"
            "- The **back-door criterion** hands you a valid adjustment set; too "
            "few controls leave confounding, a collider over-adjusts — only the "
            "right set recovers the truth.\n"
            "- A DAG is **falsifiable**: each missing edge implies a testable "
            "conditional independence.\n\n"
            "**You're ready for Week 5** if you can classify any triple on sight, "
            "read a minimal back-door set off a graph, and name one testable "
            "implication of a DAG. Next week: regression turns that adjustment set "
            "into an estimate."},
    ],
}
