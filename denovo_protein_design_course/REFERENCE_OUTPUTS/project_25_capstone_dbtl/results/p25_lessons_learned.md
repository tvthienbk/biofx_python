# Capstone lessons-learned (fill from YOUR results; EXAMPLE_DATA placeholders)

1. Best single predictor on the cohort: <feature> (enrichment <x>, recall <y>).
2. Learned composite CV-AUC = <a +/- b>, N=<n>; enrichment <e> vs best single <s> -> <beats/does not>.
3. Confident-but-failed signature (failure forensics): <what false positives share>.
4. Proposed shared-filter change (PR): <new cutoffs / add learned score>; evidence: CV-AUC + N.
5. Active-learning next batch: <design_ids> (exploit) + <design_ids> (explore).
6. Caveats: small/biased N; multi-target; in-silico labels where experimental are missing.
