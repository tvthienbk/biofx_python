# Data source — hibbs.dat (P05)

| Field | Value |
|---|---|
| **File** | `hibbs.dat` |
| **Raw URL** | https://raw.githubusercontent.com/avehtari/ROS-Examples/master/ElectionsEconomy/data/hibbs.dat |
| **Source repo** | `avehtari/ROS-Examples` (Regression and Other Stories) |
| **Delimiter** | **whitespace** → `pd.read_csv(url, sep=r"\s+")` |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 16 × 5 (one row per US presidential election, 1952–2012) |
| **License** | data distributed with the ROS-Examples repo for teaching/reproducibility |

## Primary-source publication
- **Hibbs, D. A. (2000).** "Bread and Peace Voting in U.S. Presidential Elections." *Public Choice*
  **104**(1/2), 149–180. https://doi.org/10.1023/A:1005292312412

The dataset is the canonical "Bread and Peace" teaching example in:
- **Gelman, A., Hill, J., & Vehtari, A. (2021).** *Regression and Other Stories.* Cambridge University
  Press (Chapters 1, 7). **[textbook — cite + link]**

## Parsing notes (§7)
1. **Whitespace-delimited** (`.dat`, not `.csv`) → must use `sep=r"\s+"`, not the default comma.
2. The last two columns (`inc_party_candidate`, `other_candidate`) are **strings** (candidate names) —
   harmless, but do not feed them to the model.
3. **growth** is kept on its natural percentage scale so the slope reads directly as "vote points per +1% growth".

## Variables
| Column | Meaning | Units |
|---|---|---|
| `year` | election year | — |
| `growth` | economic growth (avg. weighted personal income growth) | % |
| `vote` | incumbent party share of the two-party vote | % |
| `inc_party_candidate` | incumbent-party candidate | name |
| `other_candidate` | challenger | name |
