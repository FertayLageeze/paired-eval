import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublishedExampleTests(unittest.TestCase):
    def test_documented_cli_matches_saved_report(self):
        args = ['examples/runs.csv', '--baseline', 'baseline', '--candidate', 'candidate', '--seed', '7']
        args[0] = str(ROOT / args[0])
        run = subprocess.run([sys.executable, '-m', 'paired_eval', *args], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        expected = json.loads((ROOT/'examples/report.json').read_text(encoding='utf-8'))
        self.assertEqual(json.loads(run.stdout), expected)


if __name__ == '__main__':
    unittest.main()
