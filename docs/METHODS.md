# Estimand, resampling and test assumptions

For paired scores a_i, b_i define d_i = b_i-a_i for higher-is-better or a_i-b_i for lower-is-better. The effect is mean(d_i). Cluster mode first averages each model within a cluster, then gives each cluster equal weight. It does not approximate an equal-row estimand or resample within clusters.

The percentile bootstrap draws n independent-unit differences with replacement B times using Python random.Random(seed). The interval endpoints use linear interpolation of sorted bootstrap means at (1-confidence)/2 and its complement. These are approximate frequentist intervals, not posterior probabilities. Degenerate observed differences produce degenerate empirical bootstrap intervals and a warning.

For the sign-flip test, independently multiply each nonzero d_i by +1 or -1. Count |sum(s_i*d_i)| >= |sum(d_i)|, using relative tolerance 1e-12*sum(abs(d_i)) for floating-point equality. Enumerate all signs for <=16 nonzero differences. Otherwise draw B sign vectors from a separate seeded random stream and use (extreme+1)/(B+1). Zeros do not change the exact null distribution. This requires sign exchangeability under the null, not merely equal means under arbitrary skewed distributions. The two-sided convention is absolute-statistic extremeness.

Use independent participants, runs or clusters appropriate to the scientific question. Pairing seeds requires a meaningful matched design; seed numbers alone do not establish it. For crossed task/seed sampling, hierarchical bootstrap, multiple candidates or sequential peeking, use an appropriate richer analysis. No Holm/FDR or optional-stopping adjustment is included.

Verification includes the hand-computed 3-pair p=2/8 case, all-zero differences, direction reversal, strict ID equality, cluster weighting and Monte Carlo p-value bounds. Synthetic examples demonstrate software behavior, not method superiority.

References: SciPy permutation_test documentation https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html ; Agarwal et al., rliable https://github.com/google-research/rliable.
