# References — Project 12: Radon (varying-intercept multilevel) + LOGO-CV

## (a) Dataset primary source
- **Gelman, A., & Hill, J. (2007).** *Data Analysis Using Regression and Multilevel/Hierarchical Models.*
  Cambridge University Press. (radon multilevel example). **[textbook — cite + link]**
- **Price, P. N., Nero, A. V., & Gelman, A. (1996).** Bayesian prediction of mean indoor radon
  concentrations for Minnesota counties. *Health Physics* 71(6), 922–936. https://doi.org/10.1097/00004032-199612000-00009

Data distributed with the `pymc-devs/pymc-examples` repository (Apache-2.0).

## (b) Group-level cross-validation (LOGO)
- **Vehtari, A., Gelman, A., & Gabry, J. (2017).** Practical Bayesian model evaluation using LOO-CV and WAIC.
  *Stat. Comput.* 27, 1413–1432. https://doi.org/10.1007/s11222-016-9696-4
- **Roberts, D. R., et al. (2017).** Cross-validation strategies for data with temporal, spatial,
  hierarchical, or phylogenetic structure. *Ecography* 40(8), 913–929. (motivates leave-group-out)

## (c) Simulation-Based Calibration
- **Talts, S., Betancourt, M., Simpson, D., Vehtari, A., & Gelman, A. (2018).** Validating Bayesian
  inference algorithms with simulation-based calibration. arXiv:1804.06788.
- **Säilynoja, T., Bürkner, P.-C., & Vehtari, A. (2022).** Graphical test for discrete uniformity …
  *Statistics and Computing* 32, 32. https://doi.org/10.1007/s11222-022-10090-6

## (d) Master workflow references (§4.0)
- **Gelman, A., et al. (2020).** *Bayesian Workflow.* arXiv:2011.01808. https://arxiv.org/abs/2011.01808
- **Vehtari, A., et al. (2021).** *Rank-normalization … improved R̂.* Bayesian Analysis 16(2), 667–718. https://doi.org/10.1214/20-BA1221

## Licensing note
The radon CSV is redistributed under the pymc-examples Apache-2.0 license; the Gelman & Hill textbook and
journal articles are cited and linked, never redistributed (§8).
