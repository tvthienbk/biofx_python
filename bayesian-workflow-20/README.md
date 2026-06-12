# Bayesian Workflow 20 — Hands-On Projects (End-to-End)

**Author:** Truong Van Thien, PhD (TS. Trương Văn Thiên) · **Model tag:** Opus48 · **V2 build**

Twenty runnable teaching projects that walk the **Bayesian workflow as an iterative loop over a
growing network of models** (Gelman et al. 2020), easy → advanced. Every dataset is real,
published, and fetched from GitHub. No Bayesian background is assumed at Project 01; by Project 20
you will be fluent in multilevel models, splines/HSGP, state-space changepoints, and
Simulation-Based Calibration.

> **How these are built:** one project at a time, with a review gate after each
> (spec §0). The diagnostics and manual prose are tailored per model and validated by **running
> the notebook end-to-end** — never batched blind.

## How to run
- **Colab (recommended):** click the *Open in Colab* badge at the top of any project notebook. The
  first cell installs pinned dependencies; data self-fetches with a local-cache fallback.
- **Local:** `pip install -r requirements.txt` (or `conda env create -f environment.yml`), then open
  the notebook. Each notebook pins versions, sets a per-project `RANDOM_SEED`, and saves its fitted
  `InferenceData` to `report/<P>_idata.nc` so graders need not re-run.

## Repository layout
```
bayesian-workflow-20/
├── README.md  requirements.txt  environment.yml  LICENSE  GLOSSARY_EN_VI.md
├── _templates/{notebook…, manual_template.md, lessons_template.md, rubric.md}
└── P01_gaussian-height/ … P20_capstone-milk/
    ├── <Name>_12-06-2026_Opus48.ipynb
    ├── manual/   data/{<dataset>.csv, DATA_SOURCE.md}
    ├── paper/REFERENCES.md   report/{<P>_lessons…md, <P>_idata.nc}
```

## The 20-project catalog
Difficulty rises strictly; each project adds **one** workflow capability.

### Tier 1 — Foundations
| # | Project | Data | Model | New skill | Status |
|---|---|---|---|---|---|
| 01 | Mean height | Howell1 (adults) | Gaussian (μ,σ) | Full loop incl. Stage 0; prior pred.; R̂/ESS | ✅ built & validated |
| 02 | A single proportion | UCBadmit (pooled) | Beta-Binomial | Grid vs MCMC; sets up §07 paradox | ✅ |
| 03 | Height ~ weight | Howell1 | Normal linear | Centering; prior pred. for slopes | ✅ |
| 04 | Divorce ~ marriage/age | WaffleDivorce | Multiple linear | Standardization; DAG / confounding | ✅ |
| 05 | Economy → elections | hibbs | Linear (tiny n) | Coefficient + predictive intervals | ✅ |

### Tier 2 — GLMs
| # | Project | Data | Model | New skill | Status |
|---|---|---|---|---|---|
| 06 | Arsenic well switching | wells | Logistic | logit interpretation; PPC for binary | ✅ |
| 07 | Berkeley admissions | UCBadmit | Binomial GLM | Simpson's paradox; condition on dept | ✅ |
| 08 | Oceanic tool counts | Kline | Poisson | log link; interaction on count scale | ✅ |
| 09 | Cockroach IPM | roaches | Poisson+offset → NegBin | exposure/offset; overdispersion | ✅ |
| 10 | Child test scores | kidiq | Linear + interaction | interaction interpretation | ✅ |

### Tier 3 — Multilevel
| # | Project | Data | Model | New skill | Status |
|---|---|---|---|---|---|
| 11 | Eight Schools | Rubin 1981 (hardcoded) | Hierarchical normal | partial pooling; centered vs non-centered + funnel; SBC | ✅ |
| 12 | Radon (Minnesota) | radon | Varying-intercept + group pred. | pooling spectrum; LOGO-CV | ✅ |
| 13 | Chimpanzee choices | chimpanzees | Varying intercepts + slopes | correlated effects; LKJ | ✅ |
| 14 | Tadpole survival | reedfrogs | Hierarchical binomial | shrinkage visualization | ✅ |
| 15 | Hurricane deaths | Hurricanes | Gamma-Poisson (hier.) | overdispersion + critical appraisal | ✅ |

### Tier 4 — Advanced
| # | Project | Data | Model | New skill | Status |
|---|---|---|---|---|---|
| 16 | Moral judgments | Trolley | Ordered-categorical | ordinal likelihood; category-freq PPC | ✅ |
| 17 | Divorce w/ measurement error | WaffleDivorce (SE cols) | Error-in-variables + Student-t | data uncertainty; robustness | ✅ |
| 18 | Cherry-blossom timing | cherry_blossoms | B-splines (+ optional HSGP) | smooth trends without O(n³) GP | ✅ |
| 19 | Coal-mining disasters | Jarrett 1979 (hardcoded) | Poisson changepoint | discrete latent; compound sampling | ✅ |
| 20 | **Capstone:** milk energy | milk | Multivariate + imputation + LOO + SBC | integrative capstone | ✅ |

## 10-week teaching sequence
| Week | Projects | Theme |
|---|---|---|
| 1 | 01, 02 | The loop; Stage 0; priors & prior predictive |
| 2 | 03, 04 | Linear regression; confounding/DAGs |
| 3 | 05, 06 | Prediction; first GLM (logistic) |
| 4 | 07, 08 | Binomial (paradox) & Poisson |
| 5 | 09, 10 | Overdispersion & interactions |
| 6 | 11, 12 | Hierarchy; non-centered + funnel; first SBC |
| 7 | 13, 14 | Varying slopes; shrinkage |
| 8 | 15, 16 | Contested results; ordinal |
| 9 | 17, 18 | Measurement error; splines/HSGP |
| 10 | 19, 20 | Changepoint; capstone (imputation + comparison + SBC) |

## Tech stack
PyMC ≥ 5.16 (NUTS) · Bambi ≥ 0.13 (formula GLMs) · ArviZ ≥ 0.18 (diagnostics/viz) ·
NumPyro/nutpie (optional Tier 3–4 speed) · pandas/numpy. See `requirements.txt`.

## License
Generated code/notebooks: **MIT** (`LICENSE`). Datasets retain their source licenses (see each
`data/DATA_SOURCE.md`). Papers are cited and linked; only open-access PDFs are ever bundled (§8).
