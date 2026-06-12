# Data source — wells.csv (P06)

| Field | Value |
|---|---|
| **File** | `wells.csv` |
| **Raw URL** | https://raw.githubusercontent.com/avehtari/ROS-Examples/master/Arsenic/data/wells.csv |
| **Source repo** | `avehtari/ROS-Examples` (Regression and Other Stories) |
| **Delimiter** | **`,` (comma)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 3020 × 7 (one row per household) |
| **License** | data distributed with the ROS-Examples repo for teaching/reproducibility |

## Primary-source publication
- **Gelman, A., & Hill, J. (2007).** *Data Analysis Using Regression and Multilevel/Hierarchical Models*
  (Ch. 5). Cambridge University Press — the original switching-wells logistic example.
- **Gelman, A., Hill, J., & Vehtari, A. (2021).** *Regression and Other Stories* (Chs. 13–14).
  Cambridge University Press. **[textbook — cite + link]**
- **Field arsenic measurements:** van Geen, A., et al. (2003), "Spatial variability of arsenic in 6000
  tube wells in a 25 km² area of Bangladesh," *Water Resources Research* **39**(5).

## Parsing notes (§7)
1. **Comma-delimited** → `pd.read_csv(url)` (default).
2. `switch` is the binary outcome (1 = household switched wells).
3. This project **standardizes** `arsenic` and `dist` (distance in **metres**) to mean 0 / sd 1.
   `dist100` (= dist/100) and `educ4` (= educ/4) are pre-scaled alternatives, not used here.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `switch` | household switched to a safe well (1/0) | binary |
| `arsenic` | arsenic level of the household's well | 100 µg/L units |
| `dist` | distance to nearest safe well | metres |
| `dist100` | distance / 100 | hundreds of m |
| `assoc` | member of community association (1/0) | binary |
| `educ` | years of education (head of household) | years |
| `educ4` | educ / 4 | — |
