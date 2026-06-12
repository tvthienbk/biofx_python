### P11 — Eight Schools (hierarchical normal; centered vs non-centered)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| hierarchical (multilevel) model | mô hình phân cấp (đa tầng) | Group parameters drawn from a shared population distribution, enabling partial pooling. |
| partial pooling | gộp một phần | Shrinking each group's estimate toward the grand mean by an amount set by the between-group SD. |
| funnel | hình phễu | Sharp neck in the joint of a group effect and its scale that HMC cannot traverse at small scale. |
| non-centered parameterization | tham số hóa phi tâm | Rewriting `theta = mu + tau·z`, `z~Normal(0,1)`, to remove the funnel from the sampling geometry. |
| simulation-based calibration (SBC) | hiệu chuẩn dựa trên mô phỏng | Checking that posterior ranks of prior draws are uniform, certifying the inference is calibrated. |
