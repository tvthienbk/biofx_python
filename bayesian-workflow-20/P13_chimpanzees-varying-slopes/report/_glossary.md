### P13 — Chimpanzees (correlated varying intercepts + slopes; LKJCholeskyCov)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| varying slope | hệ số góc thay đổi theo nhóm | A per-group effect of a predictor drawn from a shared population distribution. |
| correlated random effects | hiệu ứng ngẫu nhiên tương quan | Group intercepts and slopes drawn jointly so their correlation is estimated. |
| LKJ prior | tiên nghiệm LKJ | A prior on correlation matrices; larger eta favours weaker correlations. |
| Cholesky factor | nhân tử Cholesky | Lower-triangular matrix L with LLᵀ = covariance, used for efficient sampling. |
| non-centered MvNormal | MvNormal phi tâm | Building correlated effects as mean + L·z with z~Normal(0,1) to ease sampling. |
