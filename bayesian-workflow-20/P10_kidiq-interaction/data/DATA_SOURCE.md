# Data source — kidiq.csv (P10)

| Field | Value |
|---|---|
| **File** | `kidiq.csv` |
| **Raw URL** | https://raw.githubusercontent.com/avehtari/ROS-Examples/master/KidIQ/data/kidiq.csv |
| **Source repo** | `avehtari/ROS-Examples` (Regression and Other Stories) |
| **Delimiter** | **`,` (comma)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 434 × 5 (`kid_score`, `mom_hs`, `mom_iq`, `mom_work`, `mom_age`) |
| **License** | BSD-3 / open (ROS-Examples repository); cached for teaching reproducibility |

## Primary-source publication
- **Gelman, A., Hill, J., & Vehtari, A. (2020).** *Regression and Other Stories.* Cambridge University Press, Ch. 10. https://doi.org/10.1017/9781139161879
- Underlying data derived from the **National Longitudinal Survey of Youth (NLSY)** — children of the NLSY79 cohort.
*(Book + survey — cited and linked, not redistributed, §8.)*

## Parsing notes (§7)
1. **Comma-delimited** → `pd.read_csv(url)`.
2. Standardize `mom_iq` → mom_iq_z (mean 0, sd 1; 1 SD ≈ 15 IQ points).
3. `mom_hs` is already 0/1 — do **not** standardize it.
4. The interaction is `mom_hs × mom_iq_z`.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `kid_score` | child's cognitive-test score (outcome) | points |
| `mom_hs` | mother finished high school | 0/1 |
| `mom_iq` | mother's IQ | IQ points |
| `mom_work` | mother's work status | category 1–4 |
| `mom_age` | mother's age at birth | years |
