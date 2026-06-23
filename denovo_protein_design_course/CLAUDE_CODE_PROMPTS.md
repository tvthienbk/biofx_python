# CLAUDE CODE PROMPTS — Driving the Generation

Use these in a Claude Code session opened at the repo root (where `MASTER_BLUEPRINT.md`, `PROJECT_CATALOG.md`, and `templates/` live). Generate **one project at a time**, review, then continue.

---

## STEP 1 — Standing instruction (paste once at the start of each session)

```
You are generating self-contained student capstone projects for a de novo protein
design course. Authoritative context lives in this repo:

- MASTER_BLUEPRINT.md  — the standards you MUST obey (file anatomy §1, the shared
  6-month timeline §2, compute reality §3, shared infrastructure §4, assessment §5,
  data policy §6, the MANDATORY biosecurity/responsible-research policy §7,
  reproducibility/writing §8, and the "must NOT do" list §9).
- PROJECT_CATALOG.md   — one full spec per project (01–25).
- templates/           — README_TEMPLATE.md, INSTRUCTIONS_TEMPLATE.md,
  MANUAL_TEMPLATE.md, setup_colab.ipynb, filtering_pipeline.py, download_data.py.
- projects/project_01_validation_harness/ — a fully worked EXAMPLE. Match its
  quality bar and structure exactly.

Rules:
1. Read MASTER_BLUEPRINT.md fully before generating anything. Re-read §9 each time.
2. Produce the EXACT folder anatomy from §1. Notebooks must be valid nbformat-4 JSON
   that runs top-to-bottom on Colab, each starting with a GPU check + minimal installs.
3. Instantiate the shared 6-month timeline (§2) with the project's catalog tasks,
   keeping the [core]/[extension]/[stretch] tags.
4. Be honest about compute (§3): never claim a binder/antibody/enzyme campaign runs
   free on Colab; state the realistic tier + fallback. Pin upstream repos and add a
   cell that verifies the current notebook/version exists.
5. ALWAYS include the Responsible Research section (§7). Default any ambiguous target
   to a neutralizing/diagnostic/inhibitory framing. Never include out-of-scope targets.
6. Never fabricate data or results. Synthetic teaching data must be labeled
   EXAMPLE_DATA and never presented as real findings. State realistic hit rates.
7. Copy/import shared code from templates/ rather than silently reinventing it.
8. After generating, print a short summary of what you created and any TODOs that
   need a human (e.g., "verify PDB 6M0J is current", "BindCraft needs A100").

Acknowledge you've read the blueprint and are ready. Do not generate yet.
```

---

## STEP 2 — Generate one project (paste, replacing N)

```
Generate Project N.

1. Open PROJECT_CATALOG.md and read the full entry for Project N.
2. Create projects/project_NN_shortname/ following MASTER_BLUEPRINT.md §1 exactly,
   where NN is the zero-padded number and shortname is a concise slug from the title.
3. Instantiate every required file:
   - README.md       from templates/README_TEMPLATE.md
   - INSTRUCTIONS.md  from templates/INSTRUCTIONS_TEMPLATE.md, filling all 24 weeks
     using the catalog's P0–P5 tasks (keep [core]/[extension]/[stretch] tags)
   - MANUAL.md        from templates/MANUAL_TEMPLATE.md (theory + exact tools/params
     + commands + troubleshooting specific to THIS project's tools)
   - TIMELINE.md      (Gantt-style table mapping weeks → tasks → deliverables D0–D5)
   - ASSESSMENT.md    (instantiate the §5 rubric with this project's deliverables)
   - notebooks/00_setup.ipynb .. 05_validation_plan.ipynb (valid ipynb; runnable;
     03 imports the shared filtering pipeline)
   - data/README.md + data/download_data.py + data/inputs/ (record exact accessions;
     mark them "verify on RCSB/UniProt"; never commit large data)
   - scripts/ , results/.gitkeep , env/requirements.txt (pinned, Colab-compatible)
   - references/reading_list.md (8–12 tiered papers with one-line "why read this")
4. Include the Responsible Research section in README.md and MANUAL.md (§7).
5. Match the quality and structure of projects/project_01_validation_harness/.
6. Print a creation summary + a human-review TODO list (accessions to verify, the
   realistic compute tier, anything that needs an A100 or paid platform).

Do NOT fabricate experimental results or affinities. Keep designs framed as
hypotheses with realistic success rates.
```

> Suggested generation order (so infrastructure exists first): **5, 1, 2, 3** (tooling) → then one per family (**6, 14, 18**) to set family templates → then the rest → **25 last** (it depends on cohort data).

---

## STEP 3 — Optional driver to generate several at once

Only after you've reviewed at least the worked example and a couple of generated projects:

```
Generate Projects A through B inclusive, one at a time, in ascending order. After EACH
project: (a) print the creation summary + review TODOs, (b) pause and wait for me to
type "continue" before starting the next. Obey the standing instruction and
MASTER_BLUEPRINT.md §9 for every project. Do not batch silently — I want to review
each before you proceed.
```

(Replace A and B, e.g., "6 through 13". The pause-for-"continue" keeps quality high and lets you catch drift early.)

---

## STEP 4 — QA / review checklist (run after generating any project)

```
Audit projects/project_NN_shortname/ against MASTER_BLUEPRINT.md. Report PASS/FAIL
with specifics for each:

[ ] Exact folder anatomy (§1) present; no large data committed
[ ] All 6 notebooks are valid nbformat-4 JSON and start with a GPU check + installs
[ ] 03_filter_and_rank.ipynb imports the shared filtering pipeline
[ ] INSTRUCTIONS.md covers all 24 weeks mapped to D0–D5 with task tags
[ ] MANUAL.md has exact tool versions/params + a troubleshooting table for THIS project
[ ] Compute claims are honest (§3); upstream repo pinned + a version-verify cell exists
[ ] Responsible Research section present (§7); no out-of-scope target
[ ] No fabricated data/results; synthetic data labeled EXAMPLE_DATA; realistic hit rates
[ ] data/README.md records exact accessions marked "verify"; download_data.py present
[ ] reading_list.md: 8–12 tiered papers with "why read this"
[ ] ASSESSMENT.md instantiates the §5 rubric

Then fix every FAIL.
```

---

## STEP 5 — Iterate / fix a generated project

```
In projects/project_NN_shortname/, do the following without touching unrelated files:
<your specific change, e.g. "swap the target PDB to the current RCSB entry and update
data/README.md + 01_define_and_explore.ipynb", or "the setup notebook fails on a free
T4 — add a graceful fallback that reduces num_designs and uses ESMFold for triage">.
Re-run the STEP 4 audit afterward and report results.
```

---

## Tips

- **Verify accessions yourself or have a student do it in Week 1** — PDB entries get superseded; the catalog deliberately marks them "verify."
- **Run `00_setup.ipynb` on Colab before handing a project to a student** to confirm the upstream tool/notebook still installs (these change frequently).
- **Keep a generation log** (`GENERATION_LOG.md`): which project, date, model, and review notes — useful when tools update and you regenerate.
- If Claude Code reports a TODO like "BindCraft needs A100," decide the compute plan (Colab Pro vs institutional GPU vs Tamarind/Neurosnap/Ariax) before the student starts P2.
