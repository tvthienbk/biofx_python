# Data source — Kline.csv (P08)

| Field | Value |
|---|---|
| **File** | `Kline.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Kline.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 10 × 5 (`culture`, `population`, `contact`, `total_tools`, `mean_TU`) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Kline, M. A., & Boyd, R. (2010).** *Population size predicts technological complexity in Oceania.* **Proceedings of the Royal Society B** 277(1693), 2559–2564. https://doi.org/10.1098/rspb.2010.0452
*(Journal article — cited and linked, not redistributed, §8.)*

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. Standardize `log(population)` → P (mean 0, sd 1).
3. Code `contact` as `high = 1 / low = 0`.
4. **Hawaii** (population 275,000, P = +2.32) is a high-leverage outlier — it dominates LOO Pareto-k̂.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `culture` | society name | category |
| `population` | population size | persons |
| `contact` | inter-island contact level | high / low |
| `total_tools` | number of tool types | count (outcome) |
| `mean_TU` | mean tool-use frequency | — |
