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

### P02 — A single proportion (Beta-Binomial)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| Beta-Binomial model | mô hình Beta-Nhị thức | A Binomial likelihood for a count with a Beta prior on the success probability. |
| conjugate prior | tiên nghiệm liên hợp | A prior whose posterior is in the same family (Beta+Binomial → Beta). |
| grid approximation | xấp xỉ lưới | Evaluating the posterior on a fixed grid of parameter values. |
| pooled estimate | ước lượng gộp | A single estimate that ignores group structure (can mislead). |
| Simpson's paradox | nghịch lý Simpson | A trend in pooled data that reverses within every subgroup. |

### P03 — Height ~ weight (linear regression)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| linear regression | hồi quy tuyến tính | Modelling the mean of an outcome as a linear function of predictors. |
| centering | căn giữa (trừ trung bình) | Subtracting the mean of a predictor so the intercept is interpretable. |
| slope coefficient | hệ số độ dốc | Change in the outcome per one-unit change in the predictor. |
| LogNormal prior | tiên nghiệm Log-chuẩn | A positive-only prior, here used to force a positive slope. |
| residual standard deviation | độ lệch chuẩn phần dư | Spread of the outcome around the regression line (σ). |

### P04 — Divorce ~ Marriage + Age (multiple linear regression)

| EN | VI | Definition |
|---|---|---|
| Standardization (z-score) | Chuẩn hóa (điểm z) | Rescaling a variable to mean 0 and sd 1 (`(x − x̄)/sd`), so coefficients read "sd of outcome per sd of predictor" and priors become portable across variables. |
| Multiple regression | Hồi quy bội | A linear model with two or more predictors entered simultaneously, e.g. `D = a + bM·M + bA·A`. |
| Confounding | Nhiễu (biến gây nhiễu) | A spurious association between predictor and outcome induced by a common cause; here age at marriage A causes both M and D, inflating the raw M–D link. |
| DAG (directed acyclic graph) | Đồ thị có hướng không chu trình | A graph of assumed causal arrows (here `A → M`, `A → D`, `M → D`) used to decide which variables to condition on. |
| Back-door path | Đường cửa sau | A non-causal path connecting predictor and outcome through a common cause; conditioning on the confounder (A) closes it. |

### P05 — Vote share ~ economic growth ("Bread and Peace")

| EN | VI | Definition |
|---|---|---|
| Posterior predictive interval | Khoảng dự báo hậu nghiệm | An interval for a *new* observation that combines parameter uncertainty and residual noise σ; wider than the interval for the mean. |
| Interval for the mean | Khoảng cho giá trị trung bình | An interval for the expected outcome `a + b·x`, reflecting only parameter uncertainty (not residual σ). |
| Slope coefficient | Hệ số độ dốc | The change in the outcome per one-unit change in the predictor; here vote points per +1% economic growth. |
| Small-sample inference | Suy luận mẫu nhỏ | Estimation with few data points (here n = 16), where priors matter more and cross-validation (LOO) is fragile. |
| Pareto k-hat (k̂) | Hệ số Pareto k-mũ | A per-point diagnostic for PSIS-LOO reliability; values above ≈ 0.7 flag observations whose leave-one-out estimate is untrustworthy. |

### P06 — Switching wells ~ arsenic + distance (logistic regression)

| EN | VI | Definition |
|---|---|---|
| Logistic regression | Hồi quy logistic | A GLM for a binary outcome modelling `logit(p) = a + Σ b·x`, with `p ∈ (0,1)` the success probability. |
| Logit link | Hàm liên kết logit | The transform `logit(p) = log(p/(1−p))` mapping a probability in (0,1) to the whole real line so a linear predictor can be used. |
| Odds ratio | Tỷ số chênh (OR) | `exp(coef)`: the multiplicative change in the odds of the outcome per one-unit increase in the predictor. |
| Probability-scale prior predictive | Kiểm tra tiên nghiệm trên thang xác suất | Pushing prior draws of the linear predictor through `invlogit` to verify implied probabilities spread over (0,1) rather than piling at 0/1. |
| Calibration plot | Biểu đồ hiệu chuẩn | A binary-model check plotting observed outcome frequency against predicted probability (by bin/decile); points on the 45° line mean good calibration. |

### P07 — UCBadmit Binomial GLM (Simpson's paradox)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| aggregated Binomial GLM | hồi quy nhị thức gộp ô | Modelling cell counts as Binomial(N, p) with a logit-linear predictor. |
| logit link | hàm liên kết logit | log(p/(1−p)); maps a probability to the real line for linear modelling. |
| odds ratio | tỷ số chênh | exp(coefficient); the multiplicative change in odds per unit predictor. |
| index variable | biến chỉ mục | A 0-based group code used to give each group its own intercept. |
| confounder | yếu tố gây nhiễu | A variable that distorts an association until it is conditioned on. |

### P08 — Oceanic tool kits (Poisson regression)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| Poisson regression | hồi quy Poisson | A GLM for count outcomes with a log link on the rate λ. |
| log link | hàm liên kết log | log(λ) = linear predictor; coefficients act multiplicatively on counts. |
| interaction term | số hạng tương tác | A product predictor letting one variable's slope depend on another. |
| high-leverage point | điểm đòn bẩy cao | An extreme observation (e.g. Hawaii) that strongly influences the fit and LOO. |
| Pareto k-hat diagnostic | chẩn đoán Pareto k-mũ | Per-point reliability of PSIS-LOO; values > 0.7 flag unreliable estimates. |

### P09 — Roaches (Poisson + offset → NegativeBinomial)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| exposure / offset | phơi nhiễm / số hạng bù | A known log-scale term (coefficient fixed at 1) converting a count to a rate. |
| overdispersion | quá tản (phương sai vượt mức) | Outcome variance far exceeds the Poisson mean, breaking the Poisson assumption. |
| NegativeBinomial model | mô hình nhị thức âm | A count model with an extra dispersion parameter to absorb overdispersion. |
| dispersion parameter (alpha) | tham số tản (alpha) | Controls extra variance; the Poisson is the alpha→∞ limit. |
| proportion-of-zeros check | kiểm tra tỷ lệ giá trị 0 | A PPC discrepancy comparing predicted vs observed fraction of zero counts. |

### P10 — Kid IQ (linear regression with an interaction)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| interaction effect | hiệu ứng tương tác | When one predictor's slope depends on the value of another predictor. |
| main effect | hiệu ứng chính | A predictor's effect at the reference level of the variable it interacts with. |
| different slopes | độ dốc khác nhau | The visual signature of an interaction: non-parallel fitted lines per group. |
| standardized predictor | biến dự báo chuẩn hóa | A predictor rescaled to mean 0, sd 1, so coefficients are per-SD effects. |
| moderation | điều tiết | An interaction interpreted as one variable moderating another's effect. |

### P11 — Eight Schools (hierarchical normal; centered vs non-centered)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| hierarchical (multilevel) model | mô hình phân cấp (đa tầng) | Group parameters drawn from a shared population distribution, enabling partial pooling. |
| partial pooling | gộp một phần | Shrinking each group's estimate toward the grand mean by an amount set by the between-group SD. |
| funnel | hình phễu | Sharp neck in the joint of a group effect and its scale that HMC cannot traverse at small scale. |
| non-centered parameterization | tham số hóa phi tâm | Rewriting `theta = mu + tau·z`, `z~Normal(0,1)`, to remove the funnel from the sampling geometry. |
| simulation-based calibration (SBC) | hiệu chuẩn dựa trên mô phỏng | Checking that posterior ranks of prior draws are uniform, certifying the inference is calibrated. |

### P12 — Radon (varying-intercept multilevel) + LOGO-CV
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| varying intercept | hệ số chặn thay đổi theo nhóm | A per-group baseline drawn from a shared population distribution. |
| group-level predictor | biến dự báo cấp nhóm | A covariate constant within a group (e.g. county uranium) explaining group baselines. |
| shrinkage | co ngót (về trung bình) | Pulling small-sample group estimates toward the population mean. |
| leave-one-group-out CV (LOGO) | kiểm định chéo bỏ một nhóm | Holding out a whole group to estimate prediction for a genuinely new group. |
| pooling spectrum | dải gộp dữ liệu | The no-pooling / partial-pooling / complete-pooling continuum set by the between-group SD. |

### P13 — Chimpanzees (correlated varying intercepts + slopes; LKJCholeskyCov)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| varying slope | hệ số góc thay đổi theo nhóm | A per-group effect of a predictor drawn from a shared population distribution. |
| correlated random effects | hiệu ứng ngẫu nhiên tương quan | Group intercepts and slopes drawn jointly so their correlation is estimated. |
| LKJ prior | tiên nghiệm LKJ | A prior on correlation matrices; larger eta favours weaker correlations. |
| Cholesky factor | nhân tử Cholesky | Lower-triangular matrix L with LLᵀ = covariance, used for efficient sampling. |
| non-centered MvNormal | MvNormal phi tâm | Building correlated effects as mean + L·z with z~Normal(0,1) to ease sampling. |

### P14 — Tadpoles (hierarchical Binomial, shrinkage)

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| partial pooling | gộp một phần | Tying group estimates with an adaptive prior so each borrows strength from the others. |
| shrinkage | sự co rút | Pull of a group's estimate toward the population mean, strongest where data are scarce. |
| varying intercept | hệ số chặn thay đổi | A separate intercept per group drawn from a common hierarchical distribution. |
| non-centered parameterization | tham số hóa phi tâm | Writing `a = a_bar + z·sigma` (z~N(0,1)) to remove the funnel and stabilize sampling. |
| simulation-based calibration | hiệu chuẩn dựa trên mô phỏng | Checking sampler calibration by ranking prior-drawn truths among posterior draws (should be uniform). |

### P15 — Hurricanes (Gamma-Poisson; critical appraisal)

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| overdispersion | quá phân tán | Variance exceeding what a Poisson allows; modeled with a dispersion parameter. |
| negative binomial (Gamma-Poisson) | nhị thức âm (Gamma-Poisson) | A Poisson whose rate is Gamma-distributed, absorbing extra-Poisson variance. |
| influential point | điểm ảnh hưởng | An observation whose removal substantially changes the estimates. |
| critical appraisal | thẩm định phản biện | Systematically testing whether a claimed effect is robust and credible. |
| effect fragility | tính mong manh của hiệu ứng | An effect that vanishes under reasonable changes to model or data. |

### P16 — Trolley (ordered-categorical / OrderedLogistic)

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| ordered-categorical outcome | biến phân loại có thứ tự | A response with ordered levels but unequal, unknown gaps (e.g. a 1–7 rating). |
| ordered logistic regression | hồi quy logistic có thứ tự | A model placing ordered cutpoints on a latent logistic scale to predict ordinal levels. |
| cutpoint | điểm cắt | A threshold on the latent scale separating adjacent ordinal categories. |
| proportional odds | tỷ lệ odds cân xứng | The assumption that a predictor shifts the odds of all cutpoints by the same amount. |
| category-frequency PPC | kiểm tra dự báo theo tần suất mức | Comparing predicted vs observed frequency of each ordinal level. |

### P17 — Divorce (error-in-variables + Student-t)

| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| measurement error | sai số đo lường | Difference between an observed value and the latent true value it estimates. |
| error-in-variables model | mô hình sai số trong biến | A model treating an observed variable as a noisy reading of a latent parameter. |
| latent variable | biến tiềm ẩn | An unobserved quantity inferred from noisy observations. |
| measurement-error shrinkage | co rút do sai số đo | Pulling noisy (high-SE) observations toward the model's fitted line. |
| Student-t robustness | tính bền vững Student-t | Using heavy-tailed Student-t errors so outliers exert less influence than under Normal errors. |

### P18 — Cherry-blossom timing (B-splines / HSGP)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| B-spline basis | cơ sở B-spline | Local piecewise-polynomial functions summed to build a smooth curve. |
| knot | nút (knot) | A location where spline basis functions join. |
| basis expansion | khai triển cơ sở | Representing a non-linear function as a weighted sum of basis functions. |
| Gaussian process (GP) | quá trình Gauss | A prior over functions; exact inference is O(n³). |
| HSGP (Hilbert-space approximate GP) | GP xấp xỉ không gian Hilbert | A low-rank, scalable approximation to a GP. |

### P19 — Coal-mining disasters (Poisson changepoint)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| changepoint / switchpoint | điểm chuyển | A time at which a process's parameters change abruptly. |
| discrete latent variable | biến ẩn rời rạc | An unobserved variable taking discrete values (here, the switch year). |
| compound step | bước hỗn hợp | An MCMC scheme mixing samplers (Metropolis for discrete + NUTS for continuous). |
| marginalization | tích phân biên (loại biến) | Summing a latent variable out of the likelihood to enable full NUTS. |
| Poisson rate | tốc độ Poisson | The expected count per unit time in a Poisson process. |

### P20 — Capstone: primate milk energy (imputation)
| English | Tiếng Việt | Definition (EN) |
|---|---|---|
| missing-data imputation | nội suy dữ liệu khuyết | Estimating missing values as parameters jointly with the model. |
| masking / suppression | hiệu ứng che lấp | Two predictors each appear weak alone but emerge when modelled jointly. |
| multivariate regression | hồi quy đa biến | Regression with two or more predictors. |
| model stacking (LOO) | xếp chồng mô hình | Combining models by predictive weights from cross-validation. |
| latent variable | biến ẩn | An unobserved quantity inferred from the data (e.g. an imputed value). |
