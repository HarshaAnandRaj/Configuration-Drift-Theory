import importlib.util
import unittest
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).parent / "experiments" / "cdt_simulation_campaign.py"
SPEC = importlib.util.spec_from_file_location("cdt_campaign", MODULE_PATH)
campaign = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(campaign)


class CDTSimulationCampaignTests(unittest.TestCase):
    def test_drift_probabilities_are_valid_and_have_registered_mean(self):
        p = campaign.step_probabilities(4, delta=0.10, drift_axis=3)
        self.assertTrue(np.isclose(np.sum(p), 1.0))
        self.assertTrue(np.all(p >= 0))
        self.assertTrue(np.isclose(p[6] - p[7], 0.10))
        self.assertTrue(np.allclose(p[:6], 1.0 / 8.0))

    def test_projection_return_counts_are_nested_pathwise(self):
        horizons = np.array([32, 64, 128])
        counts = campaign.lattice_tail_counts(4, 64, horizons, seed=17)
        self.assertEqual(counts.shape, (4, 3, 64))
        self.assertTrue(np.all(counts[1:] <= counts[:-1]))
        self.assertTrue(np.all(counts >= 0))
        self.assertTrue(np.all(counts <= horizons[None, :, None] / 2))

    def test_self_repulsion_metrics_respect_bounds_and_are_reproducible(self):
        first = campaign.simulate_self_repelling_path(2, 0.5, 128, seed=23)
        second = campaign.simulate_self_repelling_path(2, 0.5, 128, seed=23)
        self.assertEqual(first, second)
        for metric in ["full_historical", "projected_historical", "discovery_fraction"]:
            self.assertTrue(0.0 <= first[metric] <= 1.0)
        self.assertLessEqual(first["full_historical"], first["projected_historical"])
        self.assertLessEqual(first["full_anchored_count"], first["projected_anchored_count"])

    def test_history_metrics_respect_bounds(self):
        result = campaign.simulate_history_path(3, 256, seed=29)
        for lag in [1, 8, 32]:
            self.assertTrue(0.0 <= result[f"historical_lag_{lag}"] <= 1.0)
        self.assertTrue(0.0 <= result["two_step_backtrack_rate"] <= 1.0)
        self.assertTrue(0.0 <= result["discovery_fraction"] <= 1.0)

    def test_torus_accounting_and_state_encoding(self):
        pos = np.array([[0, 0], [1, 0], [0, 1], [3, 3]], dtype=int)
        self.assertEqual(campaign.torus_state_ids(pos, 4).tolist(), [0, 1, 4, 15])
        horizons, returns, new, occupied = campaign.run_torus(2, 4, 6, seed=31)
        self.assertEqual(returns.shape, (4, 6))
        self.assertEqual(new.shape, (4, 6))
        self.assertEqual(occupied.shape, (4, 6))
        self.assertTrue(np.all(occupied >= 1))
        self.assertTrue(np.all(occupied <= 16))
        self.assertTrue(np.all(occupied[1:] >= occupied[:-1]))
        self.assertTrue(np.all(returns >= 0))
        self.assertTrue(np.all(new >= 0))
        self.assertTrue(np.all(returns <= horizons[:, None] / 2))
        self.assertTrue(np.all(new <= horizons[:, None] / 2))

    def test_counterexamples_are_nontrivial_and_reproducible(self):
        rows, _ = campaign.run_s6()
        by_model = {row["model"]: row for row in rows}
        self.assertEqual(by_model["irrational_rotation"]["exact_unique_fraction"], 1.0)
        self.assertTrue(0.08 <= by_model["irrational_rotation"]["coarse_anchored_rate"] <= 0.12)
        self.assertEqual(by_model["iid_unit_square"]["exact_unique_fraction"], 1.0)
        self.assertTrue(0.08 <= by_model["iid_unit_square"]["coarse_anchored_rate"] <= 0.12)
        self.assertEqual(by_model["constant_projection"]["coarse_anchored_rate"], 1.0)
        self.assertFalse(by_model["constant_projection"]["informative_projection"])


if __name__ == "__main__":
    unittest.main()
