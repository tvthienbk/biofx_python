### P06 — Switching wells ~ arsenic + distance (logistic regression)

| EN | VI | Definition |
|---|---|---|
| Logistic regression | Hồi quy logistic | A GLM for a binary outcome modelling `logit(p) = a + Σ b·x`, with `p ∈ (0,1)` the success probability. |
| Logit link | Hàm liên kết logit | The transform `logit(p) = log(p/(1−p))` mapping a probability in (0,1) to the whole real line so a linear predictor can be used. |
| Odds ratio | Tỷ số chênh (OR) | `exp(coef)`: the multiplicative change in the odds of the outcome per one-unit increase in the predictor. |
| Probability-scale prior predictive | Kiểm tra tiên nghiệm trên thang xác suất | Pushing prior draws of the linear predictor through `invlogit` to verify implied probabilities spread over (0,1) rather than piling at 0/1. |
| Calibration plot | Biểu đồ hiệu chuẩn | A binary-model check plotting observed outcome frequency against predicted probability (by bin/decile); points on the 45° line mean good calibration. |
