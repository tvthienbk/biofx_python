# Data source — Hurricanes.csv (P15)

| Field | Value |
|---|---|
| **File** | `Hurricanes.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Hurricanes.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 92 × 8 (`name`, `year`, `deaths`, `category`, `min_pressure`, `damage_norm`, `female`, `femininity`) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Jung, K., Shavitt, S., Viswanathan, M., & Hilbe, J. M. (2014).** *Female hurricanes are deadlier than
  male hurricanes.* **PNAS 111(24), 8782–8787.** https://doi.org/10.1073/pnas.1402786111
- **Published critiques (cited in the manual):** Maley (2014); Malter (2014); Christensen & Christensen (2014)
  — all in *PNAS* letters — argue the effect is fragile to modeling choices and influential points.

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. `femininity` is a 1–11 crowd-rated scale; we **standardize** it (`fem_z`).
3. `deaths` is right-skewed with extreme storms (Camille 256, Diane 200) — these are influential; we refit
   without the deadliest storm to test robustness.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `name` | hurricane name | — |
| `year` | year of landfall | year |
| `deaths` | number of deaths | count (outcome) |
| `category` | Saffir-Simpson category | 1–5 |
| `min_pressure` | minimum central pressure | mb |
| `damage_norm` | normalized damage | million USD |
| `female` | name judged female | 0/1 |
| `femininity` | crowd-rated femininity of the name | 1–11 scale |
