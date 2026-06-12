# Bilingual Glossary (EN ↔ VI) — Bayesian Workflow 20

Each project appends 5–10 key terms here: **EN term · VI term · one-line definition.**
Author: Truong Van Thien, PhD / TS. Trương Văn Thiên.

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| Bayesian workflow | quy trình Bayes | Iterative loop over a growing network of models, not a one-way pipeline. |
| prior distribution | phân phối tiên nghiệm | Belief about parameters before seeing the data. |
| posterior distribution | phân phối hậu nghiệm | Updated belief about parameters after conditioning on the data. |
| likelihood | hàm hợp lý | Probability of the observed data given the parameters. |
| prior predictive check | kiểm tra dự báo tiên nghiệm | Simulating data from the prior to check it implies plausible outcomes. |
| posterior predictive check | kiểm tra dự báo hậu nghiệm | Comparing data simulated from the posterior against the observed data. |
| parameter recovery | phục hồi tham số | Fitting to data simulated from known parameters to confirm the truth is recovered. |
| credible interval | khoảng tin cậy (Bayes) | An interval containing the parameter with stated posterior probability. |
| highest density interval (HDI) | khoảng mật độ cao nhất | The shortest interval containing a given posterior probability mass. |
| effective sample size (ESS) | cỡ mẫu hiệu dụng | Number of effectively independent draws from the MCMC chain. |
| R-hat (potential scale reduction) | hệ số R-hat | Between- vs within-chain variance ratio; ~1.00 signals convergence. |
| divergence | phân kỳ (HMC) | A failed Hamiltonian trajectory flagging biased exploration. |
| standardization | chuẩn hóa | Rescaling a variable to mean 0, standard deviation 1. |

<!-- Projects append their terms below this line, grouped by project. -->

### P01 — Mean height (Gaussian)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| Gaussian (normal) likelihood | hàm hợp lý Gauss (chuẩn) | Models a continuous outcome with mean μ and standard deviation σ. |
| weakly-informative prior | tiên nghiệm thông tin yếu | A prior that gently constrains values to a plausible range without dominating the data. |
| HalfNormal prior | tiên nghiệm nửa-chuẩn | A positive-only prior used for scale parameters such as σ. |
| trace plot | đồ thị vết (trace) | Per-chain draws over iterations; should look like a fuzzy caterpillar. |
| BFMI (Bayesian fraction of missing information) | BFMI | Energy-based diagnostic; values > 0.3 indicate healthy momentum resampling. |
