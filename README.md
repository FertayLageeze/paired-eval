# paired-eval

![Project overview](docs/overview.svg)

[![Tests](https://github.com/FertayLageeze/paired-eval/actions/workflows/tests.yml/badge.svg)](https://github.com/FertayLageeze/paired-eval/actions/workflows/tests.yml)
[中文说明](README.zh-CN.md) · [Methods and limitations](docs/METHODS.md) · [Example output](examples/report.json)

Compare two systems without losing the identity of paired experimental units.

A dependency-free reporting CLI for **one planned comparison** between two systems. It strictly aligns unit IDs, reports an effect and an approximate interval, and refuses duplicate or missing pairs. Optional cluster aggregation prevents repeated rows from being counted as independent experimental units.

## Why use it

Your baseline and candidate CSV files often have different row ordering, missing runs or multiple episodes per training seed. A comparison based only on two arrays can quietly lose pairing or overstate the sample size. This tool makes those choices explicit in its output.

## Quick start

Python 3.10+. Install from source (this package has not been published to PyPI):

```bash
git clone https://github.com/FertayLageeze/paired-eval.git
cd paired-eval
python -m pip install .
```

```bash
paired-eval examples/runs.csv --baseline baseline --candidate candidate --seed 7
paired-eval examples/runs.csv --baseline baseline --candidate candidate --seed 7 --format markdown
paired-eval examples/clustered.csv --baseline baseline --candidate candidate --cluster --resamples 2000
```

```csv
unit,model,score
seed-0,baseline,0.71
seed-0,candidate,0.73
seed-1,baseline,0.74
seed-1,candidate,0.72
```

An optional `cluster` column is used **only with `--cluster`**. Then paired scores are averaged within each cluster and clusters receive equal weight. This changes the estimand from an equal-row mean to an equal-cluster mean. Both models must have the same rows and cluster membership.

Output includes means, improvement (positive always means better), percentile bootstrap interval, two-sided sign-flip p-value, win/tie/loss counts, input hash, seed and resampling settings. Use `--direction lower` for losses; `--output report.json` saves the result.

```python
from paired_eval.core import compare
report = compare([0, 0, 0], [1, 2, 3], resamples=1000, seed=7)
assert report["improvement"] == 2
assert report["two_sided_sign_flip_p"] == 0.25
```

## Statistical scope

Independent units and sign-exchangeability under the null are required. The sign-flip test is exact for at most 16 nonzero differences, otherwise Monte Carlo with a plus-one correction. The percentile bootstrap is approximate and can be unstable for small samples. A narrow interval with three seeds is not strong evidence by itself.

This release does not implement hierarchical task-by-seed resampling, unpaired tests, multiple-comparison adjustment, optional-stopping correction or causal inference. For multi-task benchmark aggregation and IQM, use [rliable](https://github.com/google-research/rliable). For general hypothesis testing, use [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).

The contribution here is a strict data contract and reproducible reporting workflow, not a new statistical method. Exit code `0` means computation completed; it does not mean a candidate is better. Invalid input returns `2`.

## Development and citation

```bash
python -m unittest discover -s tests -v
```

Tests use only the Python standard library. CI installs the package and runs tests on Windows/Linux with Python 3.10/3.12.
See [CONTRIBUTING.md](CONTRIBUTING.md). The runtime has no third-party dependencies and sends no network requests.

If this software supports your work, cite [CITATION.cff](CITATION.cff) and record the exact commit.
This is version 0.1.0 of research software, not an associated peer-reviewed paper. No DOI has been assigned.
MIT license. Maintainer: [Yongjian Wang](https://github.com/FertayLageeze).

## Related tools in this collection

- [split-leakage-audit](https://github.com/FertayLageeze/split-leakage-audit): audit declared dataset splits.
- [paired-eval](https://github.com/FertayLageeze/paired-eval): compare paired outcomes.
- [selective-risk-audit](https://github.com/FertayLageeze/selective-risk-audit): inspect abstention trade-offs.
- [paper-evidence-audit](https://github.com/FertayLageeze/paper-evidence-audit): connect claims to files.
