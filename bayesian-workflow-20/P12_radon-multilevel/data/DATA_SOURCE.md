# Data source — Minnesota radon (P12)

| Field | Value |
|---|---|
| **File** | `radon.csv` |
| **Raw URL** | https://raw.githubusercontent.com/pymc-devs/pymc-examples/main/examples/data/radon.csv |
| **Source repo** | `pymc-devs/pymc-examples` |
| **Delimiter** | **`,` (comma)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 919 × 30 (Minnesota subset); **85** counties |
| **License** | data distributed with pymc-examples (Apache-2.0 repo); original EPA/State Survey of Radon |

## Primary-source publication
- **Gelman, A., & Hill, J. (2007).** *Data Analysis Using Regression and Multilevel/Hierarchical Models.*
  Cambridge University Press. (the radon multilevel example, Ch. 12–13). **[textbook — cite + link]**
- **Price, P. N., Nero, A. V., & Gelman, A. (1996).** Bayesian prediction of mean indoor radon
  concentrations for Minnesota counties. *Health Physics* 71(6), 922–936.

The radon measurements come from the U.S. EPA / State Residential Radon Survey; the Minnesota subset is the
standard teaching dataset.

## Parsing notes (§7)
1. **`,`-delimited** → `pd.read_csv(url)`.
2. **No `log_uranium` column** in this CSV — derive it as `np.log(Uppm)`. `Uppm` is **constant within county**
   (a county-level soil-uranium covariate); standardize across counties.
3. Group index = `county_code` (0–84, 85 counties). `floor` is 0 (basement) / 1 (first floor).
4. Outcome `log_radon` has no missing values.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `log_radon` | log of measured radon (outcome) | log(pCi/L) |
| `floor` | measurement floor (0=basement, 1=first) | — |
| `county` / `county_code` | county name / 0-based index | — |
| `Uppm` | county soil uranium | ppm |
| `log_uranium` | `log(Uppm)` (derived group predictor) | log(ppm) |
