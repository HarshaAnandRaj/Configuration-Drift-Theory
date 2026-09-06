"""Finite-horizon diagnostics for the Configuration-Drift Theorem.

This utility deliberately does not infer infinite-time recurrence from finite
data. It keeps four quantities separate:

* anchored visits to a ball around the initial full state;
* anchored visits after a predeclared coordinate projection;
* historical recurrence to states older than an exclusion lag;
* discovery of new epsilon-cells.

Input
-----
.npy: shape (T, D) for one path or (M, T, D) for M independent paths.
.csv: shape (T, D), one path. A single header row is tolerated.

Example
-------
python cdt_empirical_audit.py paths.npy --epsilon 0.05 --radius 0.5 \
    --lag 10 --projection 0,1

The radii, lag, and projection are required analysis choices, not quantities
optimized by this script.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np


def load_paths(path: str | Path) -> np.ndarray:
    """Return finite paths as an array with shape (M, T, D)."""
    p = Path(path)
    if p.suffix.lower() == ".npy":
        values = np.load(p)
    elif p.suffix.lower() in {".csv", ".txt"}:
        values = np.genfromtxt(p, delimiter=",", dtype=float)
        if values.ndim == 2:
            values = values[~np.all(~np.isfinite(values), axis=1)]
    else:
        raise ValueError("input must be .npy, .csv, or .txt")

    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    if values.ndim == 2:
        values = values[None, :, :]
    if values.ndim != 3:
        raise ValueError("expected shape (T,D) or (M,T,D)")
    if values.shape[1] < 2 or values.shape[2] < 1:
        raise ValueError("each path needs at least two times and one coordinate")
    if not np.all(np.isfinite(values)):
        raise ValueError("input contains NaN or infinite values")
    return values


def parse_projection(spec: str | None, dimension: int) -> np.ndarray:
    """Parse a comma-separated, predeclared coordinate projection."""
    if spec is None:
        return np.arange(dimension, dtype=int)
    try:
        columns = np.array([int(x.strip()) for x in spec.split(",")], dtype=int)
    except ValueError as exc:
        raise ValueError("projection must be comma-separated integer columns") from exc
    if len(columns) == 0 or len(set(columns.tolist())) != len(columns):
        raise ValueError("projection columns must be nonempty and unique")
    if np.any(columns < 0) or np.any(columns >= dimension):
        raise ValueError(f"projection columns must lie in [0,{dimension - 1}]")
    return columns


def _mean_or_none(values: np.ndarray) -> float | None:
    return float(np.mean(values)) if len(values) else None


def _rate_summary(flags: np.ndarray) -> dict[str, float | int | None]:
    flags = np.asarray(flags, dtype=float)
    cut = (len(flags) + 1) // 2
    return {
        "eligible_times": int(len(flags)),
        "all": _mean_or_none(flags),
        "first_half": _mean_or_none(flags[:cut]),
        "second_half": _mean_or_none(flags[cut:]),
    }


def historical_flags(path: np.ndarray, radius: float, lag: int) -> np.ndarray:
    """Whether X_n is within radius of a state at least `lag` steps old."""
    x = np.asarray(path, dtype=float)
    if radius <= 0:
        raise ValueError("radius must be positive")
    if lag < 1 or lag >= len(x):
        raise ValueError("lag must satisfy 1 <= lag < T")
    flags = []
    radius2 = radius * radius
    for n in range(lag, len(x)):
        old = x[: n - lag + 1]
        d2 = np.sum((old - x[n]) ** 2, axis=1)
        flags.append(bool(np.any(d2 <= radius2)))
    return np.asarray(flags, dtype=bool)


def historical_summary(paths: np.ndarray, radius: float, lag: int) -> dict:
    per_path = [historical_flags(path, radius, lag) for path in paths]
    return _rate_summary(np.concatenate(per_path))


def anchored_summary(paths: np.ndarray, radius: float, include_series: bool = False) -> dict:
    """Finite partial Green estimates from independent path restarts."""
    origin = paths[:, :1, :]
    distance = np.linalg.norm(paths - origin, axis=2)
    probabilities = np.mean(distance[:, 1:] <= radius, axis=0)
    n = len(probabilities)
    half = max(1, n // 2)
    result = {
        "independent_paths": int(len(paths)),
        "horizon_excluding_t0": int(n),
        "partial_green_G_N": float(np.sum(probabilities)),
        "partial_green_G_half": float(np.sum(probabilities[:half])),
        "tail_increment": float(np.sum(probabilities[half:])),
        "late_visit_probability_mean": _mean_or_none(probabilities[half:]),
    }
    if include_series:
        result["probabilities"] = probabilities.tolist()
    return result


def discovery_summary(paths: np.ndarray, epsilon: float) -> dict:
    """Count occupied epsilon-cells; coordinates are anchored at X_0."""
    rows = []
    for path in paths:
        cells = np.floor((path - path[0]) / epsilon).astype(np.int64)
        first = cells[: max(1, len(cells) // 2)]
        rows.append(
            {
                "occupied_cells": int(len({tuple(v) for v in cells})),
                "occupied_cells_first_half": int(len({tuple(v) for v in first})),
                "new_cell_fraction": float(len({tuple(v) for v in cells}) / len(cells)),
            }
        )
    return {
        "per_path": rows,
        "mean_new_cell_fraction": float(np.mean([r["new_cell_fraction"] for r in rows])),
    }


def audit(
    paths: np.ndarray,
    epsilon: float,
    radius: float,
    lag: int,
    projection: Iterable[int],
    include_series: bool = False,
) -> dict:
    if epsilon <= 0 or radius <= 0:
        raise ValueError("epsilon and radius must be positive")
    if radius <= epsilon:
        raise ValueError("radius must be larger than epsilon")
    if lag < 1 or lag >= paths.shape[1]:
        raise ValueError("lag must satisfy 1 <= lag < T")

    columns = np.asarray(list(projection), dtype=int)
    projected = paths[:, :, columns]
    result = {
        "contract": {
            "full_shape_M_T_D": list(map(int, paths.shape)),
            "metric": "Euclidean",
            "epsilon": float(epsilon),
            "radius": float(radius),
            "lag": int(lag),
            "projection_columns": columns.tolist(),
        },
        "anchored": {
            "full_at_epsilon": anchored_summary(paths, epsilon, include_series),
            "projected_at_radius": anchored_summary(projected, radius, include_series),
        },
        "historical": {
            "full_at_epsilon": historical_summary(paths, epsilon, lag),
            "projected_at_radius": historical_summary(projected, radius, lag),
        },
        "discovery": {
            "full_at_epsilon": discovery_summary(paths, epsilon),
            "projected_at_radius": discovery_summary(projected, radius),
        },
        "interpretation_guard": [
            "These are finite-horizon diagnostics, not a proof of recurrence or transience.",
            "Anchored and historical quantities answer different questions.",
            "A single path does not estimate transition probabilities across independent restarts.",
            "The projection, radii, and lag must be justified independently of the outcome.",
        ],
    }
    if len(paths) == 1:
        result["interpretation_guard"].append(
            "Only one path was supplied; anchored probability and Green estimates are descriptive only."
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help=".npy (T,D or M,T,D) or .csv (T,D)")
    parser.add_argument("--epsilon", type=float, required=True, help="fine full-state radius")
    parser.add_argument("--radius", type=float, required=True, help="coarse projected radius")
    parser.add_argument("--lag", type=int, required=True, help="historical exclusion lag")
    parser.add_argument(
        "--projection",
        help="comma-separated projected coordinate indices; default uses all coordinates",
    )
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation")
    parser.add_argument(
        "--include-series",
        action="store_true",
        help="include the full per-time anchored probability arrays",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    paths = load_paths(args.path)
    columns = parse_projection(args.projection, paths.shape[2])
    result = audit(
        paths,
        args.epsilon,
        args.radius,
        args.lag,
        columns,
        include_series=args.include_series,
    )
    print(json.dumps(result, indent=args.indent, allow_nan=False))


if __name__ == "__main__":
    main()
