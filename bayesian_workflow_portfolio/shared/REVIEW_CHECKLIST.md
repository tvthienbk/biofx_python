# Review & correctness checklist (apply to every project you own)

You are auditing finished projects for ERRORS, INCORRECTNESS, BUGS, and quality.
Read EVERY file in each assigned project critically (not skim) and FIX problems.
Environment: only `python3` / `python3 -m pytest` has numpy/pymc. Models use
`cores=1` (multiprocess hangs without a linked BLAS here).

For each project check and fix:

1. STATISTICAL/MATH CORRECTNESS — README.md, SBC_REPORT.md, PRIOR_SENSITIVITY.md,
   lessons.md, summary_onepager.md. Are all probabilistic statements correct?
   (likelihood, priors, link functions, conjugacy claims, LOO/WAIC interpretation,
   divergence/Rhat/ESS explanations, SBC rank-uniformity logic). No hand-wavy or
   wrong claims. Fix any incorrect statement.
2. CONSISTENCY across files — the model in model.py must match the math in
   README.md and the model in notebook.ipynb (same likelihood, same priors, same
   parameter names). The true parameters in data/generate_data.py must match what
   README/notebook claim and must be the ones test_recovery.py checks.
3. RECOVERY TEST QUALITY — test_recovery.py must assert something real (HDI covers
   truth AND a sensible z/tolerance). It must target IDENTIFIABLE parameters. Make
   sure it actually passes and isn't trivially loose or trivially tight.
4. SBC CORRECTNESS — sbc.py must: draw params from the SAME prior the model uses,
   simulate data the SAME way the likelihood implies, refit, rank correctly. The
   numbers quoted in SBC_REPORT.md must match a real run (re-run and update if
   stale). Ranks should be ~uniform; if not, the model/sim is mismatched — fix it.
5. PRIOR SENSITIVITY — the 2-3 priors must be genuinely different and the reported
   conclusions must match a real run.
6. BROKEN-NOTEBOOK INTEGRITY — open notebook_broken.ipynb and confirm EACH bug
   described in BROKEN_BUGS.md is actually present in the broken notebook, that the
   stated symptom/diagnostic/fix is accurate, and that the clean notebook.ipynb does
   NOT contain those bugs. The broken notebook should still be runnable enough to
   exhibit the pathology (it may warn/diverge, but should not crash on a trivial
   typo unless that crash IS the lesson). Fix mismatches.
7. NOTEBOOK TEACHING QUALITY — markdown explains purpose+rationale+how-to-read each
   step; no contradictions; all 8 workflow steps present; figures labeled.
8. CODE QUALITY — no dead code, no misleading comments, no unused imports that
   break, consistent style with project_01, deterministic seeds everywhere.
9. NUMERICAL/RUNTIME BUGS — wrong reduction axes in PPC, off-by-one indexing,
   deprecated kwargs (use draws= not samples= for predictive sampling), colorbar+
   tight_layout conflicts (drop tight_layout after a colorbar), az.compare across
   models with different #observations (must match), label-switching guards present
   where needed.

AFTER fixing a project, RE-VERIFY it (run sequentially, one project at a time to
avoid CPU contention) from its directory — ALL must succeed:
  python3 data/generate_data.py
  python3 model.py
  python3 build_notebook.py
  python3 ../shared/validate_notebooks.py notebook.ipynb notebook_broken.ipynb
  python3 -m pytest test_recovery.py -q
  python3 sbc.py
  python3 prior_sensitivity.py
  jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=420 \
      --output /tmp/chk_$(basename $PWD).ipynb notebook.ipynb
Keep sampling light so each step stays under budget (reduce draws/sims if needed,
but never so far that recovery/SBC become meaningless). Do NOT increase chains in a
way that triggers multiprocess; keep cores=1.

Report: per project, the concrete issues you found and fixed (or "no issues found"
with what you verified), plus the final PASS confirmation including the nbconvert
execution line.
