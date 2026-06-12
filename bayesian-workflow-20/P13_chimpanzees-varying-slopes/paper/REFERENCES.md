# References — Project 13: Chimpanzees (correlated varying effects; LKJCholeskyCov)

## (a) Dataset primary source
- **Silk, J. B., et al. (2005).** Chimpanzees are indifferent to the welfare of unrelated group members.
  *Nature* 437, 1357–1359. https://doi.org/10.1038/nature04243
- **McElreath, R. (2020).** *Statistical Rethinking* (2nd ed.), Ch. 13–14. CRC Press. **[textbook — cite + link]** (the varying-slopes re-analysis)

Data distributed with McElreath's `rethinking` package (GPL-3).

## (b) Correlation prior
- **Lewandowski, D., Kurowicka, D., & Joe, H. (2009).** Generating random correlation matrices based on
  vines and extended onion method. *Journal of Multivariate Analysis* 100(9), 1989–2001.
  https://doi.org/10.1016/j.jmva.2009.04.008 (the LKJ prior)

## (c) Simulation-Based Calibration
- **Talts, S., Betancourt, M., Simpson, D., Vehtari, A., & Gelman, A. (2018).** Validating Bayesian
  inference algorithms with simulation-based calibration. arXiv:1804.06788.
- **Säilynoja, T., Bürkner, P.-C., & Vehtari, A. (2022).** Graphical test for discrete uniformity …
  *Statistics and Computing* 32, 32. https://doi.org/10.1007/s11222-022-10090-6

## (d) Master workflow references (§4.0)
- **Gelman, A., et al. (2020).** *Bayesian Workflow.* arXiv:2011.01808. https://arxiv.org/abs/2011.01808
- **Vehtari, A., et al. (2021).** *Rank-normalization … improved R̂.* Bayesian Analysis 16(2), 667–718. https://doi.org/10.1214/20-BA1221
- **Vehtari, A., Gelman, A., & Gabry, J. (2017).** *Practical Bayesian model evaluation using LOO-CV and WAIC.* Stat. Comput. 27(5), 1413–1432. https://doi.org/10.1007/s11222-016-9696-4

## Licensing note
The chimpanzees CSV is distributed under the `rethinking` GPL-3 license; the *Nature* article and McElreath's
textbook are cited and linked, never redistributed (§8).
