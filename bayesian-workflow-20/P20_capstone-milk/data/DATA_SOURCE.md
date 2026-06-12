# Data source — milk.csv (P20 capstone)

| Field | Value |
|---|---|
| **File** | `milk.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/milk.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 29 × 8 (`clade`, `species`, `kcal.per.g`, `perc.fat`, `perc.protein`, `perc.lactose`, `mass`, `neocortex.perc`) |
| **Missingness** | **`neocortex.perc` missing for 12 of 29 species** (the imputation target) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Hinde, K., & Milligan, L. A. (2011).** "Primate milk: Proximate mechanisms and ultimate perspectives."
  *Evolutionary Anthropology* 20(1): 9–23. https://doi.org/10.1002/evan.20289
*(Journal article — cited and linked, not redistributed, §8. Exact pages per the rethinking metadata; verify if quoting.)*

Used throughout *Statistical Rethinking* (2nd ed., Ch. 5 & Ch. 15) for multivariate regression and imputation.
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press. **[textbook — cite + link]**

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`. Column names contain dots → use `df["kcal.per.g"]`.
- Standardize all variables; **mass enters as log(mass)**. Impute missing `neocortex.perc` *inside* the model
  (masked array → PyMC auto-imputes); do not drop rows or mean-fill.

## Variables
| Column | Meaning |
|---|---|
| `clade` / `species` | taxonomic group / species name |
| `kcal.per.g` | milk energy density (kcal/g) — the outcome |
| `perc.fat` / `perc.protein` / `perc.lactose` | milk composition (%) |
| `mass` | female body mass (kg) |
| `neocortex.perc` | neocortex % of total brain mass (12 missing) |
