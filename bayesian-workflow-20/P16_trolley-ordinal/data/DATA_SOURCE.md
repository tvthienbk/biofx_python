# Data source — Trolley.csv (P16)

| Field | Value |
|---|---|
| **File** | `Trolley.csv` |
| **Raw URL** | https://raw.githubusercontent.com/rmcelreath/rethinking/master/data/Trolley.csv |
| **Source repo** | `rmcelreath/rethinking` |
| **Delimiter** | **`;` (semicolon)** |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 9930 × 12 (`case`, `response`, `order`, `id`, `age`, `male`, `edu`, `action`, `intention`, `contact`, `story`, `action2`) |
| **License** | GPL-3 (`rethinking` package); cached for teaching reproducibility |

## Primary-source publication
- Moral-dilemma rating data compiled by R. McElreath; the worked ordered-categorical example of
  *Statistical Rethinking* (2nd ed., Ch. 12). **Source: verify** (no single primary journal article; the
  trolley-problem paradigm traces to Foot 1967 and Greene et al. 2001, but this specific dataset is the
  textbook's).
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press. **[textbook — cite + link]**

## Parsing notes (§7)
1. **`;`-delimited** → `pd.read_csv(url, sep=";")`.
2. **`response` is 1–7** ordinal → pass **`response − 1` (0–6)** to `pm.OrderedLogistic`.
3. The ordered cutpoint prior needs an ordered starting value: supply it via `pm.sample(initvals={"cut": ...})`,
   **not** as a variable `initval` (the latter breaks `sample_prior_predictive` in PyMC 5.28).
4. The full model fits all 9930 rows in ~249 s; no subsampling was required.

## Variables (used)
| Column | Meaning | Units |
|---|---|---|
| `response` | permissibility rating (outcome) | 1–7 ordinal |
| `action` | the harmful act is performed | 0/1 |
| `intention` | the harm is intended | 0/1 |
| `contact` | physical contact is involved | 0/1 |
| `id` | participant identifier | — |
