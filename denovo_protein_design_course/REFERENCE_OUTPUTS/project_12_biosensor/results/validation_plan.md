# De Novo Binder->Biosensor Validation Plan (Project 12 — by <your name>, <date>)

## Analyte + readout
Analyte: <your chosen biomarker> (verify RCSB accession). Readout: <split-luciferase/NanoBiT
luminescence, or split-FP FRET>. Switch family/families carried: {'lockr': 9, 'split_reporter': 11}.

## Candidates
Top 20 integrated constructs carried forward; see results/top_constructs.csv. EVERY in-silico
number is a HYPOTHESIS: pae_interaction is binder confidence (not affinity); dynamic_range is a
MODELED proxy (not measured signal); there is NO measured LOD yet.

## Expression strategy
- Construct (binder + switch fusion): E. coli BL21(DE3), His-tagged, 16-18 C overnight; IMAC + SEC.
  For split-luciferase/NanoBiT, confirm the reporter folds and is active in the fusion context.
- Analyte/biomarker reagent: recombinant (mammalian/insect or commercial); confirm it is the right
  isoform/PTM state for your sensor.

## Functional assay (the point of the project): dose-response
1. Titrate the analyte across a wide concentration range (e.g. log-spaced, >= 8 points + blank).
2. Read the signal: luminescence (split-luciferase/NanoBiT) or FRET ratio (split-FP).
3. Fit signal vs [analyte] (e.g. 4-parameter logistic) -> EC50 + dynamic range (max/min, fold).
4. ESTIMATE the LOD from the fit: blank mean + 3*SD (or the lowest distinguishable dose). This is a
   MEASURED estimate from YOUR data — never a number copied from a model.

## Controls (MANDATORY)
- NO-ANALYTE / BLANK: buffer only -> defines the OFF/background signal and the LOD floor. The single
  most important control for a sensor (a leaky OFF state kills dynamic range).
- OFF-TARGET: a structurally-related but wrong analyte (or an unrelated protein) -> the sensor must
  NOT light up. This is the specificity control.
- POSITIVE: a known concentration of the true analyte (and, if available, an established sensor/ELISA)
  to confirm the assay works and to cross-calibrate.

## Realistic expectations
Coupling binding to a CLEAN ON/OFF signal is hard; dynamic range vs binder affinity is a real
trade-off; MOST integrated constructs need iteration (linker length/rigidity, latch redesign,
reporter placement). Report the dynamic range and LOD you MEASURE, honestly — including constructs
that don't switch. Do NOT imply a working sensor or fabricate an LOD.

## Multiplexing concept [stretch]
Sketch how to detect several analytes at once: orthogonal reporters (different luciferase colors /
FRET pairs), spatial separation (bead/array), or barcoded constructs. Note the cross-talk controls a
multiplex panel needs.

## Timeline + costed reagents (fill in)
- Gene synthesis (20 constructs + off-target/blank controls): $<...>, <...> weeks (IGSC-screened provider).
- Analyte reagent(s) + assay plates + luminometer/plate-reader time: $<...>.
- Personnel/instrument time: <...> weeks.

## Responsible research
Diagnostic / point-of-care sensing of a disease biomarker (in scope; low dual-use). Gene synthesis via
a biosecurity-screening provider; wet lab under institutional biosafety/ethics approval.
