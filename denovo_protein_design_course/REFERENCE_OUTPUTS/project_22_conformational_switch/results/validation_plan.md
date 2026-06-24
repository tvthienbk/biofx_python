# Validation Plan — Project 22 switch <your_top_switch_design_id>
# read-out: FRET | trigger: pH

## Construct & expression
- Gene: codon-optimized for E. coli; His6 tag (+ TEV); FRET-specific tags (e.g. CyPet/YPet for FRET).
- Strain: BL21(DE3); 16-18 C overnight induction; IMAC -> SEC purification; confirm monodisperse by SEC.

## Switch assay (FRET)
- label two sites that move apart/together between A and B; report %FRET change vs trigger.
- Trigger titration: a pH series spanning OFF and ON setpoints, >= 3 replicates per point.
- Primary metric: read-out change between the two trigger extremes (define a pass threshold a priori).

## Controls (run in the SAME plate/session)
- Positive: a known switch (e.g. a LOCKR variant or a natural two-state hinge) under the same trigger.
- Negative (locked): a single-state 'locked' design (no switch) — the always-OFF / always-ON control  <-- the decisive control.
- Unrelated: an unrelated, similarly sized protein with no expected trigger response.

## Timeline (indicative)
- Wk 1-2 cloning + expression test; Wk 3 purification + QC; Wk 4-5 assay + titration; Wk 6 analysis.

## Reagents / cost (fill from local prices)
- gene synthesis x(design + controls) ~ $?; expression/purification consumables ~ $?;
- FRET reagents (labels/protease/beamtime) ~ $?; total ~ $?.

## Go / no-go
- GO if the switch shows a trigger-dependent read-out change that the LOCKED negative does NOT.
