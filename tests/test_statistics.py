import math
import unittest
from paired_eval.core import align, compare


class PairedTests(unittest.TestCase):
    def test_hand_computed_exact_test(self):
        r = compare([0, 0, 0], [1, 2, 3], resamples=500)
        self.assertEqual(r['improvement'], 2)
        self.assertEqual(r['two_sided_sign_flip_p'], 0.25)
        self.assertEqual(r['test_draws'], 8)
        self.assertEqual(r['wins'], 3)

    def test_all_zero(self):
        r = compare([1, 2], [1, 2], resamples=100)
        self.assertEqual(r['two_sided_sign_flip_p'], 1)
        self.assertEqual(r['percentile_bootstrap_ci'], [0, 0])

    def test_lower_is_better(self):
        r = compare([4, 5, 6], [1, 3, 5], direction='lower', resamples=100)
        self.assertEqual(r['improvement'], 2)

    def test_symmetry_and_determinism(self):
        a = compare([0, 1, 3], [2, 0, 6], resamples=300, seed=17)
        b = compare([2, 0, 6], [0, 1, 3], resamples=300, seed=17)
        self.assertEqual(a['two_sided_sign_flip_p'], b['two_sided_sign_flip_p'])
        self.assertEqual(a['improvement'], -b['improvement'])
        self.assertEqual(a, compare([0, 1, 3], [2, 0, 6], resamples=300, seed=17))

    def test_monte_carlo_never_zero(self):
        r = compare([0]*20, [1]*20, resamples=100, seed=0)
        self.assertEqual(r['test_mode'], 'monte_carlo_plus_one')
        self.assertGreaterEqual(r['two_sided_sign_flip_p'], 1/101)

    def test_strict_alignment(self):
        rows = [{'unit': 'x', 'model': 'a', 'score': '1'}, {'unit': 'y', 'model': 'b', 'score': '2'}]
        with self.assertRaises(ValueError):
            align(rows, 'a', 'b')
        with self.assertRaises(ValueError):
            align(rows + [rows[0]], 'a', 'b')
        with self.assertRaises(ValueError):
            align([{'unit': 'x', 'model': 'z', 'score': 1}], 'a', 'b')

    def test_cluster_weighting_and_reordering(self):
        rows = []
        # One cluster has 10 correlated rows; it must not get 10x the weight.
        for i in range(11):
            for model in ['a', 'b']:
                rows.append({'unit': str(i), 'model': model,
                             'cluster': 'large' if i < 10 else 'small',
                             'score': 0 if model == 'a' else (1 if i < 10 else -1)})
        left, right, sizes = align(list(reversed(rows)), 'a', 'b', cluster=True)
        self.assertEqual(sorted(sizes), [1, 10])
        self.assertEqual(compare(left, right, resamples=100)['improvement'], 0)

    def test_cluster_mismatch(self):
        with self.assertRaises(ValueError):
            align([{'unit': 'u', 'model': 'a', 'score': 0, 'cluster': 'x'},
                   {'unit': 'u', 'model': 'b', 'score': 1, 'cluster': 'y'}], 'a', 'b', True)

    def test_invalid_options(self):
        for left, right, opts in [([0], [1], {}), ([0, 1], [2], {}),
                ([0, math.nan], [1, 2], {}), ([0, 1], [1, 2], {'resamples': -1}),
                ([0, 1], [1, 2], {'confidence': 1}), ([0, 1], [1, 2], {'direction': 'wrong'})]:
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                compare(left, right, **opts)


if __name__ == '__main__':
    unittest.main()
