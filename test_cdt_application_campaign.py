import unittest

import numpy as np

from experiments import cdt_application_campaign as campaign


class ApplicationCampaignTests(unittest.TestCase):
    def test_gap_includes_both_window_edges(self):
        self.assertEqual(campaign.longest_miss([False, False, True, False]), 2)
        self.assertEqual(campaign.longest_miss([True, False, False, False]), 3)
        self.assertEqual(campaign.longest_miss([False] * 4), 4)
        self.assertEqual(campaign.longest_miss([True] * 4), 0)

    def test_shape_map_preserves_declared_invariances_and_direction(self):
        t = np.linspace(0, 2 * np.pi, 64, endpoint=False)
        x = np.column_stack([1.7 * np.cos(t), .6 * np.sin(t)])
        rotation = np.array([[.6, -.8], [.8, .6]])
        a = campaign.shape_features(x[None])[0]
        moved = np.roll(x @ rotation.T * 3 + [10, -7], 9, axis=0)
        b = campaign.shape_features(moved[None])[0]
        np.testing.assert_allclose(a, b, atol=1e-12)
        reversed_features = campaign.shape_features(x[None, ::-1])[0]
        np.testing.assert_allclose(a[:8], reversed_features[:8], atol=1e-12)
        self.assertAlmostEqual(a[-1], -reversed_features[-1])

    def test_closed_resampling_handles_duplicate_points(self):
        x = np.array([[0., 0.], [0., 0.], [1., 0.], [0., 1.]])
        self.assertEqual(campaign.resample_closed(x).shape, (64, 2))
        self.assertTrue(np.isfinite(campaign.resample_closed(x)).all())
        with self.assertRaises(ValueError):
            campaign.resample_closed(np.zeros((4, 2)))

    def test_fixed_gate_control_really_freezes_gates(self):
        toy = campaign.gate_toy
        old = toy.H, toy.T, toy.EPOCHS
        try:
            toy.H, toy.T, toy.EPOCHS = 3, 9, 2
            fixed, _, g = toy.train(17, .03, 'cap', learn_gates=False)
            np.testing.assert_array_equal(fixed['z'], np.zeros(3))
            np.testing.assert_array_equal(g, np.full(3, .5))
            adaptive, _, _ = toy.train(17, .03, 'cap')
            self.assertGreater(np.linalg.norm(adaptive['z']), 0)
        finally:
            toy.H, toy.T, toy.EPOCHS = old

    def test_exact_path_bound(self):
        row = campaign.a9(0, True)
        self.assertTrue(row['bound_holds'])
        self.assertEqual(row['enumerated_paths'], 64)


if __name__ == '__main__':
    unittest.main()
