import unittest
import json

import numpy as np

from cdt_empirical_audit import (
    audit,
    historical_flags,
    load_paths,
    parse_projection,
)


class CDTEmpiricalAuditTests(unittest.TestCase):
    def test_strictly_new_path_has_no_fine_historical_recurrence(self):
        path = np.arange(8, dtype=float)[:, None]
        flags = historical_flags(path, radius=0.1, lag=1)
        self.assertFalse(np.any(flags))

    def test_constant_path_repeats(self):
        path = np.zeros((8, 2), dtype=float)
        flags = historical_flags(path, radius=0.1, lag=2)
        self.assertTrue(np.all(flags))

    def test_projection_can_separate_full_and_coarse_observables(self):
        path = np.column_stack([np.arange(10, dtype=float), np.zeros(10)])
        result = audit(
            path[None, :, :],
            epsilon=0.1,
            radius=0.5,
            lag=1,
            projection=[1],
        )
        self.assertEqual(result["historical"]["full_at_epsilon"]["all"], 0.0)
        self.assertEqual(result["historical"]["projected_at_radius"]["all"], 1.0)

    def test_projection_validation(self):
        np.testing.assert_array_equal(parse_projection("0,2", 3), [0, 2])
        with self.assertRaises(ValueError):
            parse_projection("0,0", 3)
        with self.assertRaises(ValueError):
            parse_projection("3", 3)

    def test_shortest_path_serializes_without_nan(self):
        path = np.array([[0.0], [1.0]])[None, :, :]
        result = audit(path, epsilon=0.1, radius=0.5, lag=1, projection=[0])
        json.dumps(result, allow_nan=False)

    def test_load_paths_rejects_wrong_suffix(self):
        with self.assertRaises(ValueError):
            load_paths("not_a_supported_file.json")


if __name__ == "__main__":
    unittest.main()
