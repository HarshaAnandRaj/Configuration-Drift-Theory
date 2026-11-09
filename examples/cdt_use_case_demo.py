"""Illustrate positive-rate, sparse, and lost structural recurrence.

All three full chains X=(Y,Z) are transient because the independent nuisance
coordinate Z has mean increment 1/4. The structural projection retains Y.
Its three laws are specified analytically, not classified from sample paths.
The output is a finite model illustration, not registered application evidence.
Counts exclude time zero; observed gaps include both window edges.

Run from the repository root:
    python examples/cdt_use_case_demo.py --steps 8192 --paths 128
"""

from __future__ import annotations

import argparse
import json

import numpy as np


MODES = ("restoring", "free", "visible_drift")
ANALYTIC = {
    "restoring": {
        "structural_class": "positive recurrent",
        "limiting_structural_frequency": 1 / 3,
        "mean_return_to_zero": 3,
    },
    "free": {
        "structural_class": "null recurrent",
        "limiting_structural_frequency": 0,
        "mean_return_to_zero": "infinite",
    },
    "visible_drift": {
        "structural_class": "transient",
        "limiting_structural_frequency": 0,
        "mean_return_to_zero": "infinite (unconditional; return can fail)",
    },
}


def structural_probabilities(mode: str, position: np.ndarray):
    """Return probabilities for increments (-1, +1); remaining mass stays.

    Restoring law: p=1/2 toward zero, q=1/4 away; at zero, q in each
    direction. Its invariant mass is nu(y)=(1/3)*(1/2)**abs(y).
    """
    y = np.asarray(position)
    if mode == "restoring":
        return np.where(y > 0, 0.5, 0.25), np.where(y < 0, 0.5, 0.25)
    if mode == "free":
        return np.full(y.shape, 0.25), np.full(y.shape, 0.25)
    if mode == "visible_drift":
        return np.full(y.shape, 0.125), np.full(y.shape, 0.375)
    raise ValueError(f"unknown structural law: {mode}")


def _step(uniforms, minus, plus):
    return np.where(uniforms < minus, -1, np.where(uniforms < minus + plus, 1, 0))


def simulate(steps: int = 8192, paths: int = 128, seed: int = 20261109) -> dict:
    if steps < 1 or paths < 1:
        raise ValueError("steps and paths must be positive")
    # Separate Y and Z streams preserve their model independence. Sharing Y
    # uniforms across arms pairs the illustration without changing arm laws.
    y_seed, z_seed = np.random.SeedSequence(seed).spawn(2)
    y_rng, z_rng = np.random.default_rng(y_seed), np.random.default_rng(z_seed)
    horizons = sorted({min(steps, n) for n in (256, 1024, 4096, 16384)} | {steps})
    halfway = {n // 2 for n in horizons}
    y = np.zeros((len(MODES), paths), dtype=np.int64)
    z = np.zeros(paths, dtype=np.int64)
    fine_count = np.zeros_like(y)
    coarse_count = np.zeros_like(y)
    current_gap = np.zeros_like(y)
    max_gap = np.zeros_like(y)
    last_observed_fine = np.zeros_like(y)  # The initial full state is a visit.
    halves = {0: (fine_count.copy(), coarse_count.copy())}
    records = []

    for n in range(1, steps + 1):
        u = y_rng.random(paths)
        z += _step(z_rng.random(paths), 0.125, 0.375)
        for arm, mode in enumerate(MODES):
            minus, plus = structural_probabilities(mode, y[arm])
            y[arm] += _step(u, minus, plus)

        coarse = y == 0
        fine = coarse & (z[None, :] == 0)
        fine_count += fine
        coarse_count += coarse
        current_gap = np.where(coarse, 0, current_gap + 1)
        max_gap = np.maximum(max_gap, current_gap)
        last_observed_fine = np.where(fine, n, last_observed_fine)
        if n in halfway:
            halves[n] = (fine_count.copy(), coarse_count.copy())
        if n in horizons:
            half_fine, half_coarse = halves[n // 2]
            for arm, mode in enumerate(MODES):
                records.append({
                    "mode": mode,
                    "horizon": n,
                    "fine_visits_mean": float(fine_count[arm].mean()),
                    "structural_visits_mean": float(coarse_count[arm].mean()),
                    "structural_frequency_mean": float(coarse_count[arm].mean() / n),
                    "fine_tail_visits_mean": float((fine_count - half_fine)[arm].mean()),
                    "structural_tail_frequency_mean": float(
                        (coarse_count - half_coarse)[arm].mean() / (n - n // 2)
                    ),
                    "longest_structural_miss_run_mean": float(max_gap[arm].mean()),
                    "last_observed_fine_visit_mean": float(last_observed_fine[arm].mean()),
                })

    return {
        "status": "illustrative finite simulation; no asymptotic inference from data",
        "seed": seed,
        "numpy_version": np.__version__,
        "independent_paths_per_arm": paths,
        "arms_share_random_numbers": True,
        "targets": {"fine": "(Y,Z)=(0,0)", "structural": "Y=0"},
        "analytic_full_class_all_arms": "transient (Z_n/n tends to 1/4)",
        "analytic_structural_laws": ANALYTIC,
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=8192)
    parser.add_argument("--paths", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20261109)
    args = parser.parse_args()
    if args.steps < 1 or args.paths < 1 or args.seed < 0:
        parser.error("steps/paths must be positive and seed must be nonnegative")
    print(json.dumps(simulate(args.steps, args.paths, args.seed), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
