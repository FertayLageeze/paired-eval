"""Equal-unit paired mean effects, percentile bootstrap and sign-flip testing."""
import csv
import hashlib
import io
import itertools
import math
import random
import statistics
from collections import defaultdict


def load_csv(path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not {'unit', 'model', 'score'} <= set(fields):
        raise ValueError('CSV needs unique columns including unit,model,score')
    rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('ragged CSV row')
    return rows, hashlib.sha256(raw).hexdigest()


def align(rows, baseline, candidate, cluster=False):
    if not baseline or not candidate or baseline == candidate:
        raise ValueError('baseline and candidate must be different nonempty names')
    models = {baseline: {}, candidate: {}}
    for row in rows:
        model = row.get('model')
        if model not in models:
            raise ValueError(f'unexpected model {model!r}; input must contain only the selected pair')
        unit = row.get('unit')
        if not isinstance(unit, str) or not unit.strip() or unit in models[model]:
            raise ValueError(f'invalid or duplicate unit for {model}: {unit!r}')
        try:
            score = float(row['score'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('score must be a finite number') from exc
        if not math.isfinite(score):
            raise ValueError('score must be finite')
        group = row.get('cluster') if cluster else unit
        if not isinstance(group, str) or not group.strip():
            raise ValueError('cluster must be a nonempty string when enabled')
        models[model][unit] = (score, group)
    a, b = models[baseline], models[candidate]
    if not a or set(a) != set(b):
        raise ValueError('pair IDs must match exactly; missing pairs are never silently dropped')
    groups = defaultdict(list)
    for unit in sorted(a):
        if a[unit][1] != b[unit][1]:
            raise ValueError(f'cluster differs across models for {unit}')
        groups[a[unit][1]].append((a[unit][0], b[unit][0]))
    left, right, sizes = [], [], []
    for group in sorted(groups):
        pairs = groups[group]
        left.append(statistics.fmean(x for x, _ in pairs))
        right.append(statistics.fmean(y for _, y in pairs))
        sizes.append(len(pairs))
    return left, right, sizes


def quantile(sorted_values, q):
    position = (len(sorted_values) - 1) * q
    lo = math.floor(position)
    hi = math.ceil(position)
    return sorted_values[lo] * (hi - position) + sorted_values[hi] * (position - lo) if hi != lo else sorted_values[lo]


def compare(left, right, *, direction='higher', resamples=10000, seed=0, confidence=0.95):
    if len(left) != len(right) or len(left) < 2:
        raise ValueError('need at least two independent paired units')
    if direction not in ('higher', 'lower') or not 0 < confidence < 1:
        raise ValueError('invalid direction or confidence')
    if type(resamples) is not int or resamples < 100:
        raise ValueError('resamples must be an integer >= 100')
    if any(not math.isfinite(v) for v in [*left, *right]):
        raise ValueError('all scores must be finite')
    sign = 1 if direction == 'higher' else -1
    differences = [sign * (y - x) for x, y in zip(left, right)]
    if any(not math.isfinite(v) for v in differences):
        raise ValueError('difference overflow; rescale the scores')
    n = len(differences)
    effect = statistics.fmean(differences)
    rng = random.Random(seed)
    boot = sorted(statistics.fmean(rng.choices(differences, k=n)) for _ in range(resamples))
    alpha = (1 - confidence) / 2
    interval = [quantile(boot, alpha), quantile(boot, 1 - alpha)]
    # Independent stream: changing bootstrap code must not change randomization tests.
    rng_test = random.Random(seed)
    nonzero = [d for d in differences if d != 0]
    observed = abs(math.fsum(differences))
    tolerance = 1e-12 * math.fsum(abs(x) for x in differences)
    exact = len(nonzero) <= 16
    if exact:
        total = 2 ** len(nonzero)
        extreme = sum(abs(math.fsum(s*d for s, d in zip(signs, nonzero))) >= observed - tolerance
                      for signs in itertools.product((-1, 1), repeat=len(nonzero)))
        pvalue = extreme / total
    else:
        total = resamples
        extreme = sum(abs(math.fsum(rng_test.choice((-1, 1))*d for d in nonzero)) >= observed - tolerance
                      for _ in range(resamples))
        pvalue = (extreme + 1) / (resamples + 1)
    warnings = []
    if n < 10:
        warnings.append('Fewer than 10 independent units: bootstrap intervals can be unstable or degenerate.')
    if len(set(differences)) == 1:
        warnings.append('All observed differences are identical; zero bootstrap width does not prove zero population uncertainty.')
    return {'schema_version': 1, 'tool_version': '0.1.0', 'n_independent_units': n,
            'baseline_mean': statistics.fmean(left), 'candidate_mean': statistics.fmean(right),
            'improvement': effect, 'direction': direction, 'confidence': confidence,
            'percentile_bootstrap_ci': interval, 'two_sided_sign_flip_p': pvalue,
            'test_mode': 'exact' if exact else 'monte_carlo_plus_one',
            'test_draws': total, 'bootstrap_resamples': resamples, 'seed': seed,
            'wins': sum(d > 0 for d in differences), 'ties': sum(d == 0 for d in differences),
            'losses': sum(d < 0 for d in differences), 'warnings': warnings,
            'assumptions': 'Independent units; sign exchangeability under the null. Percentile bootstrap is approximate. No multiplicity correction or causal claim.'}


def markdown(report):
    lo, hi = report['percentile_bootstrap_ci']
    return '\n'.join(['# Paired evaluation', '', '| Quantity | Value |', '|---|---:|',
        f"| Independent units | {report['n_independent_units']} |",
        f"| Baseline mean | {report['baseline_mean']:.6g} |",
        f"| Candidate mean | {report['candidate_mean']:.6g} |",
        f"| Improvement (positive = better) | {report['improvement']:.6g} |",
        f"| {report['confidence']:.0%} percentile interval | [{lo:.6g}, {hi:.6g}] |",
        f"| Two-sided sign-flip p | {report['two_sided_sign_flip_p']:.6g} |", '',
        report['assumptions'], '', *report['warnings'], ''])
