# Data source — WaffleDivorce.csv (P17)

| Field | Value |
|---|---|
| **File** | `WaffleDivorce.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/WaffleDivorce.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 50 × 13 (US states + DC) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- Compiled by R. McElreath from **US CDC** (divorce, marriage rates) and **US Census** (median age at
  marriage, population). The worked measurement-error example of *Statistical Rethinking* (2nd ed., Ch. 15).
  No single primary journal article.
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press. **[textbook — cite + link]**

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. **The SE columns are named with SPACES: `Divorce SE`, `Marriage SE`** — rename to `Divorce_SE`,
   `Marriage_SE` before use (a silent KeyError otherwise).
3. Standardize `Divorce`, `MedianAgeMarriage`, `Marriage`; put `Divorce_SE` on the standardized D scale by
   dividing by `Divorce.std()`.

## Variables (used)
| Column | Meaning | Units |
|---|---|---|
| `Divorce` | divorce rate (outcome, measured with error) | per 1000 adults |
| `Divorce SE` → `Divorce_SE` | standard error of the divorce estimate | per 1000 |
| `Marriage` | marriage rate | per 1000 adults |
| `Marriage SE` → `Marriage_SE` | standard error of the marriage estimate | per 1000 |
| `MedianAgeMarriage` | median age at first marriage | years |
| `Population` | state population | millions |
