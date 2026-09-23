import argparse
import json
from pathlib import Path
from .core import align, compare, load_csv, markdown


def main(argv=None):
    p = argparse.ArgumentParser(description='Strict paired model comparison from CSV.')
    p.add_argument('input', type=Path)
    p.add_argument('--baseline', required=True)
    p.add_argument('--candidate', required=True)
    p.add_argument('--direction', choices=['higher', 'lower'], default='higher')
    p.add_argument('--cluster', action='store_true', help='equal-weight cluster means, not equal-weight rows')
    p.add_argument('--resamples', type=int, default=10000)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--confidence', type=float, default=0.95)
    p.add_argument('--format', choices=['json', 'markdown'], default='json')
    p.add_argument('--output', type=Path)
    a = p.parse_args(argv)
    try:
        if a.output and a.output.resolve() == a.input.resolve():
            raise ValueError('output must not overwrite input')
        rows, digest = load_csv(a.input)
        left, right, sizes = align(rows, a.baseline, a.candidate, a.cluster)
        report = compare(left, right, direction=a.direction, resamples=a.resamples, seed=a.seed, confidence=a.confidence)
        report.update(input_sha256=digest, baseline=a.baseline, candidate=a.candidate,
                      estimand='equal-cluster mean improvement' if a.cluster else 'equal-unit mean improvement',
                      rows_per_independent_unit=sizes)
        result = markdown(report) if a.format == 'markdown' else json.dumps(report, indent=2, allow_nan=False) + '\n'
        if a.output:
            a.output.write_text(result, encoding='utf-8')
        else:
            print(result, end='')
        return 0
    except (ValueError, OSError, UnicodeError, OverflowError) as exc:
        p.error(str(exc))
