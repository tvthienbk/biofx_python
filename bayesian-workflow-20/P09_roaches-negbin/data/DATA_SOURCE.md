# Data source — roaches.csv (P09)

| Field | Value |
|---|---|
| **File** | `roaches.csv` |
| **Raw URL** | https://raw.githubusercontent.com/avehtari/ROS-Examples/master/Roaches/data/roaches.csv |
| **Source repo** | `avehtari/ROS-Examples` (Regression and Other Stories) |
| **Delimiter** | **`,` (comma)** — has an unnamed leading index column → `index_col=0` |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 262 × 5 after dropping the index (`y`, `roach1`, `treatment`, `senior`, `exposure2`) |
| **License** | BSD-3 / open (ROS-Examples repository); cached for teaching reproducibility |

## Primary-source publication
- **Gelman, A., & Hill, J. (2007).** *Data Analysis Using Regression and Multilevel/Hierarchical Models.* Cambridge University Press. (The roach integrated-pest-management example, Ch. 6 / 8.)
- **Gelman, A., Hill, J., & Vehtari, A. (2020).** *Regression and Other Stories.* Cambridge University Press, Ch. 15. https://doi.org/10.1017/9781139161879
*(Books — cited and linked, not redistributed, §8.)*

## Parsing notes (§7)
1. **Comma-delimited with an unnamed index column** → `pd.read_csv(url, index_col=0)`.
2. Use `log(exposure2)` as an **offset** (coefficient fixed at 1), not a free predictor.
3. Standardize `roach1` → roach_z; `treatment` and `senior` are already 0/1.
4. The outcome `y` is heavily **overdispersed** (variance 2576 ≫ mean 25.6) with 35.9% zeros.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `y` | roaches caught (outcome) | count |
| `roach1` | pre-treatment roach level | count/index |
| `treatment` | received pest treatment | 0/1 |
| `senior` | senior-only building | 0/1 |
| `exposure2` | trap-days (exposure) | days → offset |
