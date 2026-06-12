# Data source — Howell1.csv (P03; same dataset as P01)

| Field | Value |
|---|---|
| **File** | `Howell1.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Howell1.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 544 × 4 (`height`, `weight`, `age`, `male`); **352** adults after `age >= 18` |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Howell, N. (1979/2000).** *Demography of the Dobe !Kung* (2nd ed.). Aldine de Gruyter.
- **Howell, N. (2010).** *Life Histories of the Dobe !Kung.* University of California Press.
*(Books — cited and linked, not redistributed, §8.)*

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
3. **Filter `age >= 18`** for P03 (adults only) — the height-weight line is straight only for adults.
- This project **centers** weight (`wc = weight − mean`) so the intercept is the mean height at average weight.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `height` | height | cm |
| `weight` | weight | kg |
| `age` | age | years |
| `male` | sex (1=male) | — |
