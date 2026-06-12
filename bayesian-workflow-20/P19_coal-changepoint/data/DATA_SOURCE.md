# Data source — coal-mining disasters (P19, hardcoded)

| Field | Value |
|---|---|
| **File** | `coal_disasters.csv` (written by the notebook from a hardcoded array) |
| **Source** | Classic series of annual British coal-mining disasters, 1851–1961 (n=111) |
| **Why hardcoded** | Tiny and canonical (§7.4) — embedded directly and cached for completeness |
| **Retrieved / encoded** | 2026-06-12 |
| **License** | Public-domain historical counts; primary tabulation Jarrett (1979) |

## Primary-source publication
- **Jarrett, R. G. (1979).** "A note on the intervals between coal-mining disasters." *Biometrika* 66(1): 191–193.
  https://doi.org/10.1093/biomet/66.1.191

The series counts disasters causing ≥ 10 deaths. It is the canonical changepoint dataset (Carlin, Gelfand & Smith
1992; the PyMC "disaster model" example).

## Parsing notes (§7)
4. **Hardcode** tiny canonical series; cite Jarrett (1979).
8. The switchpoint is a **discrete** `pm.DiscreteUniform`; PyMC assigns a **compound step** (Metropolis for the
   switchpoint + NUTS for the rates). The divergence-count criterion does not apply; an optional **marginalized**
   formulation (sum over the switchpoint) restores full NUTS and clean diagnostics — both are provided.

## Variables
| Column | Meaning |
|---|---|
| `year` | calendar year, 1851–1961 |
| `disasters` | number of coal-mining disasters that year (≥10 deaths) |
