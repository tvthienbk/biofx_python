# Data source — Eight Schools (P11; hardcoded, Rubin 1981)

| Field | Value |
|---|---|
| **File** | none — **hardcoded** in the notebook |
| **Source** | Rubin, D. B. (1981), Table 1 |
| **Retrieved** | 2026-06-12 |
| **Rows / cols** | 8 schools × 2 (`y`, `sigma`) |
| **License** | public-domain summary statistics (published table) |

## The data
| School | y (estimated effect, SAT-V points) | sigma (SE) |
|---|---|---|
| A | 28 | 15 |
| B | 8 | 10 |
| C | −3 | 16 |
| D | 7 | 11 |
| E | −1 | 9 |
| F | 1 | 11 |
| G | 18 | 10 |
| H | 12 | 18 |

## Primary-source publication
- **Rubin, D. B. (1981).** Estimation in parallel randomized experiments. *Journal of Educational
  Statistics* 6(4), 377–401. https://doi.org/10.2307/1164617

These are the per-school estimated effects of an SAT-V coaching program and their standard errors,
analyzed as the canonical hierarchical-normal example (also Gelman et al., *BDA3*, Ch. 5).

## Parsing notes (§7)
1. **No file to download** — `y` and `sigma` are entered as NumPy arrays in the notebook (Data cell).
2. Each `sigma_j` is treated as **known** (a within-school standard error), not estimated.

## Variables
| Symbol | Meaning | Units |
|---|---|---|
| `y` | estimated coaching effect per school | SAT-V points |
| `sigma` | known standard error of the estimate | SAT-V points |
| `theta` | latent true school effect (estimated) | SAT-V points |
| `mu` | grand mean effect | SAT-V points |
| `tau` | between-school SD | SAT-V points |
