# Data source — Chimpanzees prosociality (P13)

| Field | Value |
|---|---|
| **File** | `chimpanzees.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/chimpanzees.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 504 × 8; **7** actors |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- **Silk, J. B., Brosnan, S. F., Vonk, J., Henrich, J., Povinelli, D. J., Richardson, A. S.,
  Lambeth, S. P., Mascaro, J., & Schapiro, S. J. (2005).** Chimpanzees are indifferent to the welfare of
  unrelated group members. *Nature* 437, 1357–1359. https://doi.org/10.1038/nature04243

Re-analyzed as the varying-effects example in *Statistical Rethinking* (2nd ed., Ch. 13–14).

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. `actor` is 1–7 → shift to 0–6 for indexing.
3. `prosoc_left` (0/1) is the slope predictor; `pulled_left` (0/1) is the outcome.
4. **Actor 2 always pulls left** (perfect separation); the hierarchical prior regularizes the estimate.

## Variables
| Column | Meaning | Units |
|---|---|---|
| `pulled_left` | chimp pulled the left lever (outcome) | 0/1 |
| `prosoc_left` | prosocial (partner-feeding) option on the left | 0/1 |
| `condition` | a partner was present | 0/1 |
| `actor` | individual chimpanzee | 1–7 |
| `block`, `trial`, `recipient`, `chose_prosoc` | design bookkeeping | — |
