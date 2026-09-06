import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class CDTRegisteredResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = json.loads(
            (ROOT / "results" / "cdt_simulation_campaign.json").read_text()
        )
        cls.followups = json.loads(
            (ROOT / "results" / "cdt_followups.json").read_text()
        )

    def test_primary_manifest_is_evidential_not_smoke(self):
        manifest = self.campaign["manifest"]
        self.assertFalse(manifest["quick_smoke_test"])
        self.assertEqual(manifest["master_seed"], 20260905)
        self.assertEqual(manifest["base_paths"], 8000)
        self.assertEqual(manifest["bootstraps"], 500)

    def test_identifiable_low_projection_phase_map_matches(self):
        rows = self.campaign["suites"]["S1_projection"]
        unique = {(r["D"], r["m"]): r for r in rows}
        selected = [r for (D, m), r in unique.items() if m <= 3]
        self.assertEqual(len(selected), 15)
        self.assertTrue(all(r["quantitative_match"] for r in selected))

    def test_three_phase_cells_are_registered_estimator_failures(self):
        rows = self.campaign["suites"]["S1_projection"]
        unique = {(r["D"], r["m"]): r for r in rows}
        failures = {key for key, row in unique.items() if not row["quantitative_match"]}
        self.assertEqual(failures, {(5, 5), (6, 5), (6, 6)})

    def test_hidden_drift_preserves_projection_at_primary_horizon(self):
        rows = self.followups["F1_drift_causal"]
        selected = [
            r for r in rows
            if r["horizon"] == 8192
            and r["kind"] == "hidden"
            and r["observable"] == "projected"
        ]
        self.assertEqual(len(selected), 3)
        for row in selected:
            self.assertLessEqual(row["ratio_ci_lo"], 1.0)
            self.assertGreaterEqual(row["ratio_ci_hi"], 1.0)
            self.assertTrue(0.49 <= row["slope"] <= 0.51)

    def test_drift_location_controls_projected_suppression(self):
        rows = self.followups["F1_drift_causal"]
        hidden = [
            r for r in rows
            if r["horizon"] == 8192 and r["kind"] == "hidden"
            and r["observable"] == "full"
        ]
        visible = [
            r for r in rows
            if r["horizon"] == 8192 and r["kind"] == "visible"
            and r["observable"] == "projected"
        ]
        self.assertTrue(all(r["ratio_to_neutral"] < 0.12 for r in hidden))
        self.assertTrue(all(r["ratio_to_neutral"] < 0.10 for r in visible))

    def test_strong_self_repulsion_projection_is_finite_horizon_compatible(self):
        rows = self.followups["F2_self_repulsion_observable"]
        selected = [r for r in rows if r["horizon"] == 4096]
        self.assertEqual(len(selected), 12)
        for row in selected:
            self.assertEqual(
                row["classification"],
                "compatible with persistent anchored projection",
            )
            self.assertGreater(row["projected_anchored"]["slope_ci_lo"], 0.0)

    def test_finite_capacity_novelty_declines_and_occupancy_rises(self):
        rows = self.campaign["suites"]["S5_finite_capacity"]
        cases = {(r["D"], r["L"]) for r in rows}
        for case in cases:
            arm = sorted(
                [r for r in rows if (r["D"], r["L"]) == case],
                key=lambda r: r["horizon_per_state"],
            )
            self.assertTrue(
                all(a["new_state_rate"] > b["new_state_rate"]
                    for a, b in zip(arm, arm[1:]))
            )
            self.assertTrue(
                all(a["occupied_fraction"] < b["occupied_fraction"]
                    for a, b in zip(arm, arm[1:]))
            )


if __name__ == "__main__":
    unittest.main()
