# Data source — Howell1.csv (P01 / also used by P03)

| Field | Value |
|---|---|
| **File** | `Howell1.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Howell1.csv |
| **Source repo** | `rmcelreath/rethinking` (the *Statistical Rethinking* companion R package) |
| **Delimiter** | **`;` (semicolon)** — see Gotcha 1 |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 544 rows × 4 cols (`height`, `weight`, `age`, `male`); **352** adults after `age >= 18` |
| **License** | Distributed with the open-source `rethinking` package (GPL-3). Cached here for teaching reproducibility only. |

## Primary-source publication
The data are partial census records of the **Dobe area !Kung San**, collected by
**Nancy Howell** in the 1960s.

- Howell, N. (2010). *Life Histories of the Dobe !Kung: Food, Fatness, and Well-being over the Life-span.* University of California Press.
- Howell, N. (1979/2000). *Demography of the Dobe !Kung.* (2nd ed.). Aldine de Gruyter.

*(Books — cited and linked, not redistributed, per §8.)*

## Parsing notes (§7 gotchas that apply)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`. A comma-delimited mirror exists at the
   `RTpy` base (`Statistical-Rethinking-with-Python-and-PyMC3/master/Data/`) if needed.
3. **Howell1 → filter `age >= 18`** for P01 (and P03): the full sample includes children, making
   height bimodal; the single-Gaussian model is only valid for adults.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `height` | individual height | cm |
| `weight` | individual weight | kg |
| `age` | age | years |
| `male` | sex indicator | 1 = male, 0 = female |
