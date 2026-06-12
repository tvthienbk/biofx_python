# Data source — UCBadmit.csv (P02 / also used by P07)

| Field | Value |
|---|---|
| **File** | `UCBadmit.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/UCBadmit.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 12 rows × 5 cols (`dept`, `applicant.gender`, `admit`, `reject`, `applications`) |
| **License** | distributed with the GPL-3 `rethinking` package; cached for teaching reproducibility |

## Primary-source publication
- **Bickel, P. J., Hammel, E. A., & O'Connell, J. W. (1975).** "Sex Bias in Graduate Admissions:
  Data from Berkeley." *Science* 187(4175): 398–404.

This is the original analysis that introduced the Berkeley admissions data as the canonical example
of **Simpson's paradox**. Cited and linked, not redistributed (§8).

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
- The `applicant.gender` column name contains a dot; reference it as `df["applicant.gender"]`.

## Variables
| Column | Meaning |
|---|---|
| `dept` | department code (A–F) |
| `applicant.gender` | `male` / `female` |
| `admit` | number admitted |
| `reject` | number rejected |
| `applications` | total applications (= admit + reject) |
