# Data source — UCBadmit.csv (P07; same dataset as P02)

| Field | Value |
|---|---|
| **File** | `UCBadmit.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/UCBadmit.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 12 × 5 (`dept`, `applicant.gender`, `admit`, `reject`, `applications`); 6 departments × 2 genders |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Bickel, P. J., Hammel, E. A., & O'Connell, J. W. (1975).** *Sex Bias in Graduate Admissions: Data from Berkeley.* **Science** 187(4175), 398–404. https://doi.org/10.1126/science.187.4175.398
*(Journal article — cited and linked, not redistributed, §8.)*

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. Code `male = 1` for `applicant.gender == "male"`, else 0.
3. Index departments A–F as 0–5 via `pd.Categorical(df["dept"]).codes` (an **index variable**, not dummy contrasts).
4. The outcome is **aggregated**: `admit ~ Binomial(applications, p)` per dept×gender cell.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `dept` | department A–F | category |
| `applicant.gender` | male / female | category |
| `admit` | number admitted in the cell | count |
| `reject` | number rejected in the cell | count |
| `applications` | total applicants in the cell (= admit + reject) | count |
