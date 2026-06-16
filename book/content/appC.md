# Appendix C · Mathematical and Statistical Background

This appendix gives the minimum mathematics behind the generative models
(Chapters 7, 9, 10) and the filtering and characterization statistics (Chapters
13, 17, 22). It is conceptual and worked-example driven rather than a formal
treatment: the aim is that when a chapter says "the model learns the score
function" or "report a 95% binomial confidence interval," you know exactly what
is meant and can compute it. Equations are written in Unicode on their own line,
per the book's convention.

## C.1 Probability Essentials

A **random variable** takes values with associated probabilities; its
**expectation** (mean) and **variance** summarize center and spread:

<p class="eqn">E[X] = Σ xᵢ·p(xᵢ)   Var[X] = E[(X − E[X])²]</p>

The **Gaussian (normal)** distribution, written N(μ, σ²), is central to
diffusion models because the noise added during training is Gaussian:

<p class="eqn">p(x) = (1 / √(2πσ²))·exp(−(x − μ)² / (2σ²))</p>

Two facts used repeatedly: (i) a sum of independent Gaussians is Gaussian, with
variances adding; (ii) **conditional probability** p(A | B) = p(A, B) / p(B) and
**Bayes' rule** p(A | B) = p(B | A)·p(A) / p(B), which underlies how a model
turns a learned prior over structures into a sample conditioned on a motif.

## C.2 Diffusion and Score Matching (Conceptual)

Generative diffusion models — the engine of RFdiffusion — work by learning to
*reverse* a gradual corruption of data. There are two processes.

**Forward (noising).** Start from a real protein backbone x₀ and add small
Gaussian noise over many steps t = 1 … T until, at t = T, the structure is
indistinguishable from random noise. A single step:

<p class="eqn">xₜ = √(1 − βₜ)·xₜ₋₁ + √βₜ·ε,   ε ~ N(0, I)</p>

where βₜ is a small, scheduled variance. Because Gaussian noise composes, you can
jump directly to any time t from x₀:

<p class="eqn">xₜ = √(ᾱₜ)·x₀ + √(1 − ᾱₜ)·ε,   ᾱₜ = Πₛ₌₁ᵗ (1 − βₛ)</p>

**Reverse (denoising).** A neural network learns to undo one noising step: given
the noisy xₜ and the timestep t, predict the noise (or equivalently a cleaner
structure), then take a small step back toward the data. Iterating from pure
noise at t = T down to t = 0 *generates* a new backbone.

**The score function.** The quantity the network effectively learns is the
**score** — the gradient of the log-probability of the noisy data with respect to
the coordinates:

<p class="eqn">s(xₜ, t) = ∇ₓ log p(xₜ)</p>

The score points "uphill" toward more probable (more protein-like)
configurations. Denoising is following the score. **Conditioning** (motif
scaffolding, functional-group placement) works by fixing certain coordinates
during the reverse process so every sample is pulled toward protein-like
structures *that also satisfy the constraint* — this is why a theozyme geometry
can be held while the rest of the backbone is generated around it.

::: {.method data-title="Method C.1 · Reading a diffusion trajectory"}
1. Early steps (t near T): output looks like a featureless blob — ignore detail.
2. Middle steps: secondary structure (helices, sheets) emerges; topology decided.
3. Late steps (t near 0): side-chain-scale geometry refines; the motif locks in.
If conditioning fails, the constraint usually "tears loose" in the middle steps —
inspect there, not at the end.
:::

## C.3 SE(3) and Equivariance (Conceptual)

A protein structure has no privileged position or orientation: rotating or
translating the whole molecule does not change the protein. The group of all
rigid motions in 3D — rotations and translations — is called **SE(3)** (the
special Euclidean group; rotations alone form SO(3)).

A function f is **SE(3)-equivariant** if transforming the input transforms the
output the same way:

<p class="eqn">f(R·x + t) = R·f(x) + t,   for any rotation R, translation t</p>

It is **invariant** if the output does not change at all: f(R·x + t) = f(x)
(energies and distances are invariant; predicted coordinates should be
equivariant). Building equivariance into the network means it does not have to
*learn* that physics is the same in every frame — a major reason structure
models generalize from limited data. RFdiffusion's backbone is represented as a
set of rigid frames (a translation plus a rotation per residue), and the network
operates equivariantly on those frames.

## C.4 RMSD: Definition and Computation

**Root-mean-square deviation** measures how far two structures' matched atoms are
after optimal superposition. For N matched atoms with coordinates Pᵢ and Qᵢ:

<p class="eqn">RMSD = √( (1/N)·Σᵢ ‖Pᵢ − Qᵢ‖² )</p>

The superposition that minimizes RMSD is found by the **Kabsch algorithm** (an
SVD of the cross-covariance matrix; see Appendix B for code). Conventions that
matter: which atoms (Cα only, all backbone, all heavy atoms), and over which
residues (a local motif RMSD can be tight while the global RMSD is loose).

**Self-consistency RMSD (scRMSD)** is the workhorse filter of de novo design
(Chapter 17): design a sequence for a generated backbone, fold that sequence
independently (e.g., with AlphaFold), and compute the Cα RMSD between the folded
prediction and the original design. A low scRMSD (commonly < 2 Å) means the
sequence is predicted to fold to the structure it was designed for — a necessary,
though not sufficient, condition for success.

::: {.worked data-title="Worked Example C.1 · Computing an RMSD by hand"}
**Problem.** Three matched Cα atoms, already superposed, have deviations of 1.0,
2.0, and 2.0 Å. What is the RMSD?

**Solution.** Square the deviations: 1, 4, 4. Mean of squares: (1 + 4 + 4)/3 = 3.
RMSD = √3 ≈ 1.73 Å. Note this exceeds the simple mean deviation (1.67 Å): RMSD
penalizes the larger deviations more heavily, which is why a single bad residue
can fail an otherwise good design's scRMSD filter.
:::

## C.5 Statistics for Filtering and Hit Rates

**Z-scores and percentiles.** To compare a design's metric against a population
(e.g., Rosetta energy across 5,000 designs), standardize:

<p class="eqn">z = (x − μ) / σ</p>

A z-score of −2 means the value is two standard deviations below the mean
(favorable for energy). Equivalently, rank designs and keep a top percentile;
percentile is more robust than z when the distribution is skewed, which design
metrics usually are.

**Binomial confidence interval for hit rates.** A campaign tests n designs and
finds k hits. The point estimate is p̂ = k/n, but with small n this is
imprecise. The **Wilson score interval** is the recommended 95% CI (far better
than the textbook "normal approximation" at small n or extreme p̂):

<p class="eqn">CI = ( p̂ + z²/2n ± z·√( p̂(1−p̂)/n + z²/4n² ) ) / ( 1 + z²/n )</p>

with z = 1.96 for 95% confidence.

::: {.worked data-title="Worked Example C.2 · A 95% CI for a 3/96 hit rate"}
**Problem.** You test n = 96 designs and find k = 3 hits. Report the hit rate and
its 95% Wilson interval.

**Solution.** p̂ = 3/96 = 0.0313 (3.1%). With z = 1.96, z² = 3.84:
center = (0.0313 + 3.84/192) / (1 + 3.84/96) = (0.0313 + 0.0200) / 1.0400 = 0.0493.
margin = 1.96·√(0.0313·0.9687/96 + 3.84/(4·96²)) / 1.0400
= 1.96·√(0.000316 + 0.000104) / 1.0400 = 1.96·0.0205 / 1.0400 = 0.0386.
So the 95% CI is roughly **1.1% to 8.8%** (0.0493 ± 0.0386). The estimate "3.1%"
is real but imprecise — the interval spans nearly an order of magnitude. Testing
more designs is the only way to tighten it; this is why campaigns report n
alongside the rate.
:::

**Multiple-testing awareness.** When you screen thousands of designs against many
metrics, some will look good by chance. Two habits guard against fooling
yourself: (i) decide filter thresholds *before* looking at the activity data
(pre-registration in spirit; Chapter 13), and (ii) when computing many p-values
(e.g., comparing each variant to a control), control the false-discovery rate
(Benjamini–Hochberg) rather than using a raw p < 0.05 per test. A "significant"
result that survives FDR correction is far more likely to replicate.

::: {.reality data-title="Reality Check C.1 · Filters are correlated, not independent"}
pLDDT, PAE, pTM, and scRMSD are not independent measurements — they are different
views of the same underlying confidence. Passing four correlated filters is *not*
four independent pieces of evidence, and stacking them does not multiply your
odds the way independent tests would. Treat the in-silico filter battery as one
combined predictor with a real-world enrichment factor (Chapter 1's "25-fold"),
not as a chain of independent screens.
:::
