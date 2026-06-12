# Data source — cherry_blossoms.csv (P18)

| Field | Value |
|---|---|
| **File** | `cherry_blossoms.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/cherry_blossoms.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 1215 × 5 (`year`, `doy`, `temp`, `temp_upper`, `temp_lower`); **827** rows have an observed `doy` |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
The Kyoto cherry phenology reconstruction:
- **Aono, Y., & Kazui, K. (2008).** "Phenological data series of cherry tree flowering in Kyoto, Japan,
  and its application to reconstruction of springtime temperatures since the 9th century."
  *International Journal of Climatology* 28: 905–914.
- **Aono, Y., & Saito, S. (2010).** *International Journal of Biometeorology* 54: 211–219.
*(Journal articles — cited and linked, not redistributed, §8. Exact volumes per the rethinking metadata.)*

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
7. **Do NOT fit an exact GP** on ~827 points (O(n³), exceeds runtime budget). Use **B-splines** as the main
   model; **`pm.gp.HSGP`** is the scalable optional path. The temperature series also has missing years.
- Drop rows with missing `doy` before modelling the bloom date.

## Variables
| Column | Meaning |
|---|---|
| `year` | calendar year |
| `doy` | day-of-year of first bloom (≈ March/April) |
| `temp`, `temp_upper`, `temp_lower` | reconstructed March temperature (°C) and bounds |
