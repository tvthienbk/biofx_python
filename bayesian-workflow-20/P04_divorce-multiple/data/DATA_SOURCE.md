# Data source — WaffleDivorce.csv (P04)

| Field | Value |
|---|---|
| **File** | `WaffleDivorce.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/WaffleDivorce.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 50 × 13 (one row per US state) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
McElreath compiled this dataset from **US CDC / National Center for Health Statistics** divorce and
marriage statistics and **US Census** median-age-at-marriage figures. There is no single journal paper;
the worked analysis is **Statistical Rethinking (2nd ed.), Chapter 5** (the divorce/confounding example).
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press. **[textbook — cite + link]**

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. SE columns are named with **spaces** (`Marriage SE`, `Divorce SE`) — not used in P04 (they drive the
   measurement-error model in **P17**).
3. This project **standardizes** `Divorce`, `Marriage`, `MedianAgeMarriage` to mean 0 / sd 1 so the
   priors `Normal(0, 0.5)` are weakly-informative and comparable across predictors.

## Variables (used in P04)
| Column | Symbol | Meaning | Units |
|---|---|---|---|
| `Divorce` | D | divorces per 1000 adults | rate |
| `Marriage` | M | marriages per 1000 adults | rate |
| `MedianAgeMarriage` | A | median age at marriage | years |
| `Location` | — | US state name | — |
