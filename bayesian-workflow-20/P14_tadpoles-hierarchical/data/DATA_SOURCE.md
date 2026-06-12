# Data source — reedfrogs.csv (P14)

| Field | Value |
|---|---|
| **File** | `reedfrogs.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/reedfrogs.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 48 × 5 (`density`, `pred`, `size`, `surv`, `propsurv`); a `tank` index 0–47 is added in-notebook |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Vonesh, J. R., & Bolker, B. M. (2005).** *Compensatory larval responses shift trade-offs associated with
  predator-induced hatching plasticity.* **Ecology 86(6), 1580–1591.** https://doi.org/10.1890/04-0535

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. Add a `tank` column = `np.arange(48)` to index the varying intercept.
3. The SE/measurement issues of other datasets do not apply here; `surv` and `density` are exact counts.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `density` | initial number of tadpoles in the tank | count (10/25/35) |
| `pred` | predation treatment | no / pred |
| `size` | tadpole size class | small / big |
| `surv` | number surviving | count |
| `propsurv` | raw survival proportion (`surv/density`) | — |
