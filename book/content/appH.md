# Appendix H · Solutions to Selected Problems

Worked solution keys for a representative set of Quantitative & Computational and
Challenge problems, plus one exemplar lab-report sketch. Each solution shows the
arithmetic and the reasoning, not just the answer — the point is to make the
method transferable to the problems left unsolved. Numbers are checked; where a
problem admits more than one defensible answer, the solution says so.

## H.1 Solution to Problem 1.2 (Quantitative) — Hit-rate binomial CI

**Problem.** A campaign tests 96 designs and finds 3 with activity above
background. Compute the tested hit rate and a 95% confidence interval, and comment
on precision.

**Solution.** Point estimate: p̂ = 3/96 = 0.03125 ≈ **3.1%**. Use the Wilson score
interval (reliable at small n and extreme p̂), with z = 1.96 and z² = 3.8416.

Center = (p̂ + z²/2n) / (1 + z²/n) = (0.03125 + 3.8416/192) / (1 + 3.8416/96)
= (0.03125 + 0.02001) / (1.04002) = 0.05126 / 1.04002 = 0.0493.

Margin = [ z·√( p̂(1−p̂)/n + z²/4n² ) ] / (1 + z²/n).
Inside the root: 0.03125·0.96875/96 + 3.8416/(4·9216)
= 0.0003154 + 0.0001042 = 0.0004196; √ = 0.02048.
Margin = 1.96·0.02048 / 1.04002 = 0.04014 / 1.04002 = 0.0386.

95% CI ≈ 0.0493 ± 0.0386 → **roughly 1.1% to 8.8%**.

**Comment.** The interval spans nearly an order of magnitude, so "3.1%" is a real
but imprecise estimate. With only 3 successes the data cannot distinguish a 1%
campaign from an 8% one. The remedy is more tested designs: precision improves
only as ~1/√n. This is exactly why Chapter 1 insists that a hit rate be reported
*with* the number tested.

## H.2 Solution to Problem 2.x (Quantitative) — Eyring: ΔG‡ ↔ rate

**Problem.** A designed enzyme has k_cat = 10 s⁻¹ at 25 °C. (a) What apparent
ΔG‡ does this imply via the Eyring equation? (b) If a redesign lowers ΔG‡ by
2 kcal/mol, what k_cat would you predict?

**Solution.** Eyring: k = (k_B·T / h)·e^(−ΔG‡/RT). At T = 298 K the prefactor
k_B·T/h ≈ (1.381×10⁻²³·298)/(6.626×10⁻³⁴) ≈ 6.2×10¹² s⁻¹.

(a) Solve for ΔG‡: ΔG‡ = −RT·ln(k·h / k_B·T) = RT·ln(k_B·T/h / k).
RT at 298 K = 1.987×10⁻³ kcal/(mol·K)·298 = 0.592 kcal/mol.
Ratio (prefactor / k) = 6.2×10¹² / 10 = 6.2×10¹¹; ln(6.2×10¹¹) = 27.15.
ΔG‡ = 0.592·27.15 = **16.1 kcal/mol**.

(b) Rate depends on ΔG‡ as e^(−ΔΔG‡/RT). Lowering ΔG‡ by ΔΔG‡ = 2 kcal/mol
multiplies the rate by e^(2/0.592) = e^(3.378) = **29.3**.
New k_cat ≈ 10·29.3 ≈ **293 s⁻¹**.

**Comment.** A 2 kcal/mol improvement in the barrier — a modest amount, within
reach of a single well-placed hydrogen bond — buys nearly 30-fold in rate. This
exponential leverage is why getting the transition-state-stabilizing geometry
right (the theozyme) matters so much more than minor backbone tweaks.

## H.3 Solution to Problem 14.x (Challenge) — Judging theozyme quality

**Problem.** A student proposes a serine-hydrolase theozyme: a Ser Oγ positioned
3.6 Å from the carbonyl carbon of the substrate ester, a His whose Nε2 is 3.4 Å
from Ser Oγ, an Asp 2.7 Å from His Nδ1, and an oxyanion hole of two backbone
amides ~3.5 Å from the carbonyl oxygen. The Ser–His angle (Oγ···Nε2–His ring
plane) is geometrically reasonable. Is this theozyme adequate? What would you fix?

**Solution.** Score it against the chemistry, not just the atom list.

- **Nucleophile–electrophile distance.** Ser Oγ to carbonyl C at 3.6 Å is too far
  for an incipient bond; a productive nucleophilic attack geometry wants the
  attacking oxygen ~3.0 Å from the carbon, approaching along the Bürgi–Dunitz
  angle (~105°) to the carbonyl. **Fix:** tighten to ~2.8–3.0 Å and specify the
  attack angle, not just the distance.
- **His–Ser proton transfer.** Nε2···Oγ at 3.4 Å is a reasonable hydrogen bond
  (target ~2.8–3.2 Å); slightly long but acceptable. The His must be oriented to
  *accept* the Ser proton — verify Nε2 lone pair points at Oγ.
- **Asp–His.** Nδ1···Asp at 2.7 Å is a good charged hydrogen bond that sets His
  tautomer/pKₐ; correct.
- **Oxyanion hole.** Two backbone amides ~3.5 Å from the carbonyl oxygen is on the
  long side; effective oxyanion stabilization wants N···O ~2.8–3.0 Å. **Fix:**
  bring the amides closer; this is often the difference between a binder and a
  catalyst.

**Verdict:** the *topology* is right (correct triad, oxyanion hole present) but the
*geometry* is uncatalytic — the nucleophile and oxyanion hole are too far. A
reviewer would reject it as "right pieces, wrong distances." Theozyme adequacy is
judged on distances and angles with catalytic tolerances, not on the presence of
the right residues. This is the most common Capstone error (Appendix E, Red
Flags).

## H.4 Solution to Problem 17.x (Computational) — scRMSD computation

**Problem.** You designed a 120-residue backbone, generated a sequence with
LigandMPNN, and folded that sequence with AlphaFold3. Outline and execute the
scRMSD computation, and state the pass/fail decision against a 2 Å threshold given
that the optimal Cα superposition yields RMSD = 1.4 Å.

**Solution.** scRMSD measures *self-consistency*: does the designed sequence fold
back to the structure it was designed for?

Procedure: (1) extract Cα coordinates of the design backbone and of the AF3
prediction for the same 120 residues, in register; (2) compute the optimal rigid
superposition (Kabsch) of prediction onto design; (3) report the Cα RMSD.

```python
import numpy as np
def kabsch_rmsd(P, Q):                 # P, Q: (N,3) Cα arrays, same order
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    U, S, Vt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    diff = (Pc @ R.T) - Qc
    return np.sqrt((diff*diff).sum() / len(P))
# scRMSD = kabsch_rmsd(design_CA, af3_CA)
```

Given the result, scRMSD = **1.4 Å < 2.0 Å → PASS**.

**Comment.** Passing scRMSD is *necessary but not sufficient*. It says the model
believes the sequence folds to the intended backbone; it says nothing about
whether the active-site geometry is catalytic, whether the protein expresses, or
whether it is stable in solvent (Chapter 20). Also check AF3 confidence (pLDDT
high across the active site, low PAE between catalytic residues) — a 1.4 Å scRMSD
on a low-confidence prediction is far weaker evidence than the same number on a
pLDDT-90 model.

## H.5 Solution to Problem 22.x (Quantitative) — Michaelis–Menten fit

**Problem.** Initial-rate data for a designed esterase (corrected for the
no-enzyme control):

| [S] (mM) | 0.25 | 0.5 | 1.0 | 2.0 | 4.0 | 8.0 |
|---|---|---|---|---|---|---|
| v (µM/s) | 0.91 | 1.55 | 2.35 | 3.08 | 3.64 | 3.95 |

Estimate V_max and K_M, then k_cat and k_cat/K_M given [E] = 0.10 µM.

**Solution.** The data saturate near ~4 µM/s, so V_max ≈ 4.4 µM/s and K_M is the
[S] giving half that (~2.2 µM/s) — between 0.5 and 1.0 mM. Confirm with a
linearization. Lineweaver–Burk plots 1/v vs 1/[S]; slope = K_M/V_max, intercept =
1/V_max:

| 1/[S] (mM⁻¹) | 4.0 | 2.0 | 1.0 | 0.5 | 0.25 | 0.125 |
|---|---|---|---|---|---|---|
| 1/v (s/µM) | 1.099 | 0.645 | 0.426 | 0.325 | 0.275 | 0.253 |

A linear fit gives intercept ≈ 0.227 s/µM → V_max = 1/0.227 ≈ **4.4 µM/s**, and
slope ≈ 0.218 (s/µM)/(mM⁻¹) → K_M = slope·V_max ≈ 0.218·4.4 ≈ **0.96 mM** (≈ 1.0
mM). (In practice fit with nonlinear least squares — `scipy.optimize.curve_fit` on
v = V_max·[S]/(K_M+[S]) — rather than Lineweaver–Burk, which distorts errors; the
linearization here is just to get defensible starting values.)

Now k_cat = V_max / [E] = 4.4 µM/s / 0.10 µM = **44 s⁻¹**.
k_cat/K_M = 44 s⁻¹ / 0.96×10⁻³ M = 4.4×10⁴ / 0.96 ≈ **4.6×10⁴ M⁻¹s⁻¹**.

**Comment.** A k_cat/K_M near 10⁴–10⁵ M⁻¹s⁻¹ is a respectable designed enzyme —
well above background but far below diffusion-limited natural enzymes (~10⁸). Two
discipline points: report the fit with confidence intervals (the curve_fit
covariance), and remember these rates are meaningless without the dead-mutant
control showing activity collapses to background — otherwise you may be fitting an
artifact.

## H.6 Exemplar Lab-Report Sketch (for Lab 22 / Capstone Phase 8)

A concise model for the structure graders expect:

1. **Aim.** One sentence: measure steady-state kinetics of designed esterase
   D-047 against p-nitrophenyl acetate and confirm activity is catalytic.
2. **Methods.** Expression/purification (IMAC → SEC), assay conditions (buffer,
   pH, T, [E], [S] series, detection wavelength), controls run (no-enzyme,
   Ser→Ala dead mutant, empty-vector lysate), and fitting method
   (nonlinear MM in `scipy`).
3. **Results.** The rate-vs-[S] curve with fitted MM line; a table of V_max, K_M,
   k_cat, k_cat/K_M with 95% CIs; the dead-mutant trace overlaid on background.
4. **Interpretation.** k_cat/K_M ≈ 4.6×10⁴ M⁻¹s⁻¹; dead mutant indistinguishable
   from no-enzyme background → activity is catalytic and triad-dependent. State
   limitations (single replicate? substrate scope untested?).
5. **Next step.** Tie back to the DBTL loop: what the Learn phase changes (e.g.,
   tighten the oxyanion hole in redesign, per H.3) and why.

::: {.reality data-title="Reality Check H.1 · The grade is in the controls"}
Across these solutions one theme recurs: the number (hit rate, k_cat, scRMSD) is
only as meaningful as the control or interval reported beside it. A k_cat without
a dead mutant, a hit rate without n, an scRMSD without a confidence metric — each
is a claim a reviewer will discount. Report the uncertainty, and report the
control.
:::
