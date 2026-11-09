"""Integrity and interpretation regressions for the completed application run."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from experiments.summarize_cdt_applications import sign_tail

ROOT = Path(__file__).parent
RESULTS = ROOT / 'results/application_20261109'


class ApplicationEvidenceTests(unittest.TestCase):
    def test_frozen_sources_and_plan_match_run_manifest(self):
        manifest = json.loads((RESULTS / 'manifest.json').read_text())
        for name, expected in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)
        self.assertFalse(manifest['smoke_only'])

    def test_all_registered_replicates_present_without_errors(self):
        for i in range(1, 13):
            data = json.loads((RESULTS / f'A{i}.json').read_text())
            expected = 1 if i in [9, 10] else (8 if i == 12 else 16)
            self.assertEqual(len(data['records']), expected)
            self.assertFalse(data['smoke_only'])
            self.assertTrue(all('error' not in r for r in data['records']))

    def test_sign_test_has_preregistered_tail_and_failure_behavior(self):
        self.assertEqual(sign_tail(16, 16), 1 / 65536)
        self.assertEqual(sign_tail(0, 16), 1)
        summary = json.loads((RESULTS / 'summary.json').read_text())
        for row in summary['primary']:
            self.assertEqual(row['bonferroni_p'], min(1, 8 * row['sign_p_one_sided']))

    def test_memory_functional_failure_and_constant_map_are_retained(self):
        data = json.loads((RESULTS / 'A4.json').read_text())['records']
        self.assertEqual([r['replicate'] for r in data if not r['functional_pass']], [10])
        for r in data:
            constant = next(a for a in r['arms'] if a['arm'] == 'constant')
            self.assertEqual(constant['negative_false_acceptance'], 1)

    def test_followup_archive_matches_original_recorded_hash(self):
        folder = ROOT / 'results/phenomena_followup_20261109'
        metadata = json.loads((folder / 'packaging.json').read_text())
        body = gzip.decompress((folder / metadata['archive']).read_bytes())
        self.assertEqual(hashlib.sha256(body).hexdigest(), metadata['original_sha256'])
        records = json.loads(body)
        self.assertEqual(len(records), 3 * 16 * 3)
        self.assertTrue(all(len(r['last_observed_visit']) == 512 for r in records))

    def test_bookkeeping_does_not_improve_the_behavior(self):
        data = json.loads((ROOT / 'results/phenomena_followup_20261109/bookkeeping.json').read_text())
        for case in ['constant', 'period_two']:
            rows = {r['representation']: r for r in data if r['case'] == case}
            self.assertEqual(rows['clock_augmented']['unique_states'], 257)
            self.assertEqual(rows['clock_augmented']['lag2_historical_fraction'], 0)
            self.assertEqual(rows['raw']['lag2_historical_fraction'], 1)
            self.assertEqual(rows['projected_without_clock']['lag2_historical_fraction'], 1)


if __name__ == '__main__':
    unittest.main()
