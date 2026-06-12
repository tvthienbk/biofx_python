### P04 — Divorce ~ Marriage + Age (multiple linear regression)

| EN | VI | Definition |
|---|---|---|
| Standardization (z-score) | Chuẩn hóa (điểm z) | Rescaling a variable to mean 0 and sd 1 (`(x − x̄)/sd`), so coefficients read "sd of outcome per sd of predictor" and priors become portable across variables. |
| Multiple regression | Hồi quy bội | A linear model with two or more predictors entered simultaneously, e.g. `D = a + bM·M + bA·A`. |
| Confounding | Nhiễu (biến gây nhiễu) | A spurious association between predictor and outcome induced by a common cause; here age at marriage A causes both M and D, inflating the raw M–D link. |
| DAG (directed acyclic graph) | Đồ thị có hướng không chu trình | A graph of assumed causal arrows (here `A → M`, `A → D`, `M → D`) used to decide which variables to condition on. |
| Back-door path | Đường cửa sau | A non-causal path connecting predictor and outcome through a common cause; conditioning on the confounder (A) closes it. |
