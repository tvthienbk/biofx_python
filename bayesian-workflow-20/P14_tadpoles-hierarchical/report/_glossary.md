### P14 — Tadpoles (hierarchical Binomial, shrinkage)

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| partial pooling | gộp một phần | Tying group estimates with an adaptive prior so each borrows strength from the others. |
| shrinkage | sự co rút | Pull of a group's estimate toward the population mean, strongest where data are scarce. |
| varying intercept | hệ số chặn thay đổi | A separate intercept per group drawn from a common hierarchical distribution. |
| non-centered parameterization | tham số hóa phi tâm | Writing `a = a_bar + z·sigma` (z~N(0,1)) to remove the funnel and stabilize sampling. |
| simulation-based calibration | hiệu chuẩn dựa trên mô phỏng | Checking sampler calibration by ranking prior-drawn truths among posterior draws (should be uniform). |
