"""Registered simulation campaign for the Configuration-Drift Theorem.

Read cdt_simulation_preregistration.md before interpreting results. The script
writes raw/summary data only; theorem corrections are made in a separate report
after the frozen suites have run.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np


MASTER_SEED = 20260905
HORIZONS = np.array([256, 512, 1024, 2048, 4096], dtype=int)
BASE_PATHS = 8000
SELF_REPEL_PATHS = 240
HISTORY_PATHS = 400
FINITE_PATHS = 240
BOOTSTRAPS = 500
HISTORY_LAG = 8
QUICK = False
BOOTSTRAP_BATCH = 25


def bootstrap_means(x: np.ndarray, rng: np.random.Generator, B: int):
    """Draw ordinary path-bootstrap means in memory-bounded batches."""
    values = np.asarray(x, dtype=float)
    draws = np.empty(B, dtype=float)
    for start in range(0, B, BOOTSTRAP_BATCH):
        stop = min(start + BOOTSTRAP_BATCH, B)
        indices = rng.integers(0, len(values), size=(stop - start, len(values)))
        draws[start:stop] = np.mean(values[indices], axis=1)
    return draws


def mean_ci(values: np.ndarray, rng: np.random.Generator, B: int | None = None):
    """Path-bootstrap mean and percentile interval."""
    if B is None:
        B = BOOTSTRAPS
    x = np.asarray(values, dtype=float)
    est = float(np.mean(x))
    if len(x) < 2:
        return est, est, est
    draws = bootstrap_means(x, rng, B)
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return est, float(lo), float(hi)


def ratio_ci(
    numerator: np.ndarray,
    denominator: np.ndarray,
    rng: np.random.Generator,
    B: int | None = None,
):
    """Independent-arm bootstrap ratio of means."""
    if B is None:
        B = BOOTSTRAPS
    a = np.asarray(numerator, dtype=float)
    b = np.asarray(denominator, dtype=float)
    denom = float(np.mean(b))
    if denom == 0:
        return float("inf"), float("nan"), float("nan")
    est = float(np.mean(a) / denom)
    a_draws = bootstrap_means(a, rng, B)
    b_draws = bootstrap_means(b, rng, B)
    with np.errstate(divide="ignore", invalid="ignore"):
        draws = a_draws / b_draws
    draws = draws[np.isfinite(draws)]
    if len(draws) == 0:
        return est, float("nan"), float("nan")
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return est, float(lo), float(hi)


def slope_ci(
    counts_by_horizon: np.ndarray,
    horizons: np.ndarray,
    rng: np.random.Generator,
    B: int | None = None,
):
    """Bootstrap the log-log slope of tail Green increments."""
    if B is None:
        B = BOOTSTRAPS
    counts = np.asarray(counts_by_horizon, dtype=float)

    def fit(sample):
        means = np.mean(sample, axis=1)
        mask = means > 0
        if np.sum(mask) < 3:
            return np.nan
        return float(np.polyfit(np.log(horizons[mask]), np.log(means[mask]), 1)[0])

    est = fit(counts)
    if not np.isfinite(est):
        return est, float("nan"), float("nan")
    draws = []
    M = counts.shape[1]
    for start in range(0, B, BOOTSTRAP_BATCH):
        stop = min(start + BOOTSTRAP_BATCH, B)
        indices = rng.integers(0, M, size=(stop - start, M))
        boot_means = np.mean(counts[:, indices], axis=2)
        for sample_means in boot_means.T:
            mask = sample_means > 0
            if np.sum(mask) >= 3:
                s = np.polyfit(
                    np.log(horizons[mask]), np.log(sample_means[mask]), 1
                )[0]
                if np.isfinite(s):
                    draws.append(float(s))
    if len(draws) == 0:
        return est, float("nan"), float("nan")
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return est, float(lo), float(hi)


def expected_tail_slope(dimension: int) -> float:
    if dimension == 1:
        return 0.5
    if dimension == 2:
        return 0.0
    return 1.0 - dimension / 2.0


def step_probabilities(D: int, delta: float = 0.0, drift_axis: int | None = None):
    p = np.full(2 * D, 1.0 / (2 * D), dtype=float)
    if drift_axis is not None and delta != 0:
        if abs(delta) >= 1.0 / D:
            raise ValueError("abs(delta) must be smaller than 1/D")
        p[2 * drift_axis] += delta / 2.0
        p[2 * drift_axis + 1] -= delta / 2.0
    return p


def lattice_tail_counts(
    D: int,
    M: int,
    horizons: np.ndarray,
    seed: int,
    delta: float = 0.0,
    drift_axis: int | None = None,
):
    """Return tail-window anchored counts for every coordinate projection m."""
    rng = np.random.default_rng(seed)
    max_t = int(np.max(horizons))
    counts = np.zeros((D, len(horizons), M), dtype=np.int16)
    p = step_probabilities(D, delta, drift_axis)
    use_uniform = np.allclose(p, 1.0 / (2 * D))
    path_batch = 1000

    for start in range(0, M, path_batch):
        stop = min(start + path_batch, M)
        width = stop - start
        if use_uniform:
            directions = rng.integers(
                0, 2 * D, size=(max_t, width), dtype=np.int8
            )
        else:
            directions = rng.choice(
                2 * D, size=(max_t, width), p=p
            ).astype(np.int8)
        zero_prefix = np.ones((max_t, width), dtype=bool)
        for m in range(D):
            increments = (
                (directions == 2 * m).astype(np.int8)
                - (directions == 2 * m + 1).astype(np.int8)
            )
            coordinate = np.cumsum(increments, axis=0, dtype=np.int16)
            zero_prefix &= coordinate == 0
            for h, H in enumerate(horizons):
                counts[m, h, start:stop] = np.count_nonzero(
                    zero_prefix[H // 2:H], axis=0
                )
    return counts


def summarize_projection_counts(counts, D, rng):
    rows = []
    raw = {}
    for m in range(1, D + 1):
        block = counts[m - 1].astype(float)
        slope, slo, shi = slope_ci(block, HORIZONS, rng)
        expected = expected_tail_slope(m)
        within = bool(np.isfinite(slope) and (slo <= expected <= shi or abs(slope - expected) <= 0.15))
        key = f"D{D}_m{m}"
        raw[key] = block.tolist()
        for i, H in enumerate(HORIZONS):
            est, lo, hi = mean_ci(block[i], rng)
            rows.append(
                {
                    "suite": "S1_projection",
                    "D": D,
                    "m": m,
                    "horizon": int(H),
                    "estimate": est,
                    "ci_lo": lo,
                    "ci_hi": hi,
                    "metric": "tail_green_increment",
                    "predicted_recurrent": m <= 2,
                    "predicted_cdt_separation": m <= 2 < D,
                    "slope": slope,
                    "slope_ci_lo": slo,
                    "slope_ci_hi": shi,
                    "expected_slope": expected,
                    "quantitative_match": within,
                }
            )
    return rows, raw


def run_s1(rng):
    rows = []
    raw = {}
    for D in range(1, 7):
        counts = lattice_tail_counts(
            D, BASE_PATHS, HORIZONS, MASTER_SEED + 1000 + D
        )
        r, x = summarize_projection_counts(counts, D, rng)
        rows.extend(r)
        raw.update(x)
    return rows, raw


def run_s2(rng):
    rows = []
    raw = {}
    D = 4
    deltas = [0.0, 0.02, 0.05, 0.10, 0.20]
    arms = [("neutral", 0.0, None)]
    arms += [("hidden", d, 3) for d in deltas[1:]]
    arms += [("visible", d, 0) for d in deltas[1:]]
    neutral = None

    for i, (kind, delta, axis) in enumerate(arms):
        counts = lattice_tail_counts(
            D,
            BASE_PATHS,
            HORIZONS,
            MASTER_SEED + 2000 + i,
            delta=delta,
            drift_axis=axis,
        )
        full = counts[D - 1].astype(float)
        proj = counts[1].astype(float)
        if kind == "neutral":
            neutral = (full.copy(), proj.copy())
        raw[f"{kind}_{delta:.2f}"] = {"full": full.tolist(), "projected": proj.tolist()}
        for h, H in enumerate(HORIZONS):
            f_est, f_lo, f_hi = mean_ci(full[h], rng)
            p_est, p_lo, p_hi = mean_ci(proj[h], rng)
            sigma_axis = math.sqrt(1.0 / D)
            pe = delta * math.sqrt(H) / sigma_axis
            rows.append(
                {
                    "suite": "S2_drift",
                    "kind": kind,
                    "delta": delta,
                    "horizon": int(H),
                    "Pe": pe,
                    "full_tail": f_est,
                    "full_ci_lo": f_lo,
                    "full_ci_hi": f_hi,
                    "projected_tail": p_est,
                    "projected_ci_lo": p_lo,
                    "projected_ci_hi": p_hi,
                }
            )

    assert neutral is not None
    nf, npj = neutral
    for row in rows:
        idx = int(np.where(HORIZONS == row["horizon"])[0][0])
        key = f"{row['kind']}_{row['delta']:.2f}"
        f = np.asarray(raw[key]["full"], dtype=float)[idx]
        p = np.asarray(raw[key]["projected"], dtype=float)[idx]
        row["full_ratio_to_neutral"], row["full_ratio_ci_lo"], row["full_ratio_ci_hi"] = ratio_ci(
            f, nf[idx], rng
        )
        row["projected_ratio_to_neutral"], row["projected_ratio_ci_lo"], row["projected_ratio_ci_hi"] = ratio_ci(
            p, npj[idx], rng
        )
    return rows, raw


def simulate_self_repelling_path(D: int, gamma: float, T: int, seed: int):
    rng = np.random.default_rng(seed)
    pos = np.zeros(D, dtype=np.int32)
    offsets = np.vstack([np.eye(D, dtype=np.int32), -np.eye(D, dtype=np.int32)])
    visits = {}
    history = [tuple(pos)]
    old_full = set()
    old_proj = set()
    distinct = {tuple(pos)}
    late_full_hist = 0
    late_proj_hist = 0
    late_full_anchor = 0
    late_proj_anchor = 0
    eligible = 0

    for t in range(1, T + 1):
        cands = pos + offsets
        counts = np.array([visits.get(tuple(c), 0) for c in cands], dtype=float)
        scores = -gamma * counts
        weights = np.exp(scores - np.max(scores))
        weights /= np.sum(weights)
        pos = cands[rng.choice(len(cands), p=weights)]
        key = tuple(pos)
        proj = int(pos[0])
        if t >= HISTORY_LAG:
            old_key = history[t - HISTORY_LAG]
            old_full.add(old_key)
            old_proj.add(int(old_key[0]))
        if t > T // 2:
            eligible += 1
            late_full_hist += key in old_full
            late_proj_hist += proj in old_proj
            late_full_anchor += all(v == 0 for v in key)
            late_proj_anchor += proj == 0
        history.append(key)
        distinct.add(key)
        visits[key] = visits.get(key, 0) + 1

    return {
        "full_historical": late_full_hist / eligible,
        "projected_historical": late_proj_hist / eligible,
        "full_anchored_count": late_full_anchor,
        "projected_anchored_count": late_proj_anchor,
        "discovery_fraction": len(distinct) / (T + 1),
        "endpoint_r2": float(np.dot(pos, pos)),
    }


def run_s3(rng):
    rows = []
    raw = {}
    gammas = [0.0, 0.1, 0.5, 1.0, 2.0]
    metrics = [
        "full_historical",
        "projected_historical",
        "full_anchored_count",
        "projected_anchored_count",
        "discovery_fraction",
        "endpoint_r2",
    ]
    for D in [1, 2, 3]:
        arms = {}
        for gi, gamma in enumerate(gammas):
            values = {metric: [] for metric in metrics}
            for trial in range(SELF_REPEL_PATHS):
                out = simulate_self_repelling_path(
                    D,
                    gamma,
                    int(HORIZONS[-1]),
                    MASTER_SEED + 300000 + D * 10000 + gi * 1000 + trial,
                )
                for metric in metrics:
                    values[metric].append(out[metric])
            arms[gamma] = {k: np.asarray(v, dtype=float) for k, v in values.items()}
            raw[f"D{D}_g{gamma:.1f}"] = {k: v.tolist() for k, v in arms[gamma].items()}

        neutral = arms[0.0]
        for gamma in gammas:
            current = arms[gamma]
            summary = {"suite": "S3_self_repulsion", "D": D, "gamma": gamma}
            for metric in metrics:
                est, lo, hi = mean_ci(current[metric], rng)
                summary[metric] = est
                summary[f"{metric}_ci_lo"] = lo
                summary[f"{metric}_ci_hi"] = hi
            for metric in ["full_historical", "projected_historical", "discovery_fraction"]:
                est, lo, hi = ratio_ci(current[metric], neutral[metric], rng)
                summary[f"{metric}_ratio"] = est
                summary[f"{metric}_ratio_ci_lo"] = lo
                summary[f"{metric}_ratio_ci_hi"] = hi

            f_ratio = summary["full_historical_ratio"]
            p_ratio = summary["projected_historical_ratio"]
            d_ratio = summary["discovery_fraction_ratio"]
            if gamma == 0:
                label = "neutral reference"
            elif p_ratio < 0.50:
                label = "over-repulsive"
            elif f_ratio <= 0.75 and p_ratio >= 0.75 and d_ratio >= 1.25:
                label = "beneficial window"
            else:
                label = "mixed/no material separation"
            summary["registered_label"] = label
            rows.append(summary)
    return rows, raw


def simulate_history_path(D: int, T: int, seed: int, lags=(1, 8, 32)):
    rng = np.random.default_rng(seed)
    pos = np.zeros(D, dtype=np.int32)
    history = [tuple(pos)]
    old = {lag: set() for lag in lags}
    repeats = {lag: 0 for lag in lags}
    eligible = {lag: 0 for lag in lags}
    distinct = {tuple(pos)}
    anchored = 0
    backtracks = 0
    for t in range(1, T + 1):
        axis = int(rng.integers(D))
        pos[axis] += 1 if rng.random() < 0.5 else -1
        key = tuple(pos)
        for lag in lags:
            if t >= lag:
                old[lag].add(history[t - lag])
            if t > T // 2 and t >= lag:
                eligible[lag] += 1
                repeats[lag] += key in old[lag]
        if t > T // 2:
            anchored += all(v == 0 for v in key)
            if t >= 2:
                backtracks += key == history[t - 2]
        history.append(key)
        distinct.add(key)
    return {
        **{f"historical_lag_{lag}": repeats[lag] / eligible[lag] for lag in lags},
        "anchored_tail_count": anchored,
        "two_step_backtrack_rate": backtracks / (T // 2),
        "discovery_fraction": len(distinct) / (T + 1),
    }


def run_s4(rng):
    rows = []
    raw = {}
    T = int(HORIZONS[-1])
    metrics = ["historical_lag_1", "historical_lag_8", "historical_lag_32",
               "anchored_tail_count", "two_step_backtrack_rate", "discovery_fraction"]
    for D in range(1, 7):
        values = {m: [] for m in metrics}
        for trial in range(HISTORY_PATHS):
            out = simulate_history_path(D, T, MASTER_SEED + 400000 + D * 1000 + trial)
            for metric in metrics:
                values[metric].append(out[metric])
        row = {"suite": "S4_historical", "D": D}
        raw[f"D{D}"] = {}
        for metric in metrics:
            x = np.asarray(values[metric], dtype=float)
            raw[f"D{D}"][metric] = x.tolist()
            est, lo, hi = mean_ci(x, rng)
            row[metric] = est
            row[f"{metric}_ci_lo"] = lo
            row[f"{metric}_ci_hi"] = hi
        row["predicted_anchored_recurrent"] = D <= 2
        row["expected_backtrack_rate"] = 1.0 / (2 * D)
        rows.append(row)
    return rows, raw


def torus_state_ids(pos: np.ndarray, L: int):
    weights = (L ** np.arange(pos.shape[1], dtype=np.int64))[None, :]
    return np.sum(pos.astype(np.int64) * weights, axis=1)


def run_torus(D: int, L: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    states = L ** D
    multiples = np.array([1, 2, 4, 8], dtype=int)
    horizons = multiples * states
    T = int(horizons[-1])
    pos = np.zeros((M, D), dtype=np.int16)
    visited = np.zeros((M, states), dtype=bool)
    visited[:, 0] = True
    occupied = np.ones(M, dtype=np.int32)
    return_tail = np.zeros((len(horizons), M), dtype=np.int32)
    new_tail = np.zeros((len(horizons), M), dtype=np.int32)
    snapshots = np.zeros((len(horizons), M), dtype=np.int32)

    for t in range(1, T + 1):
        axis = rng.integers(D, size=M)
        sign = np.where(rng.random(M) < 0.5, 1, -1).astype(np.int16)
        pos[np.arange(M), axis] = (pos[np.arange(M), axis] + sign) % L
        ids = torus_state_ids(pos, L)
        is_new = ~visited[np.arange(M), ids]
        occupied += is_new
        visited[np.arange(M), ids] = True
        is_return = ids == 0
        active = np.flatnonzero((t > horizons // 2) & (t <= horizons))
        for h in active:
            return_tail[h] += is_return
            new_tail[h] += is_new
        exact = np.flatnonzero(t == horizons)
        for h in exact:
            snapshots[h] = occupied
    return horizons, return_tail, new_tail, snapshots


def run_s5(rng):
    rows = []
    raw = {}
    cases = [(2, 8), (3, 4)] if QUICK else [(2, 16), (2, 32), (3, 8), (3, 12)]
    for ci, (D, L) in enumerate(cases):
        horizons, returns, new, occupied = run_torus(
            D, L, FINITE_PATHS, MASTER_SEED + 5000 + ci
        )
        states = L ** D
        raw[f"D{D}_L{L}"] = {
            "return_tail": returns.tolist(),
            "new_tail": new.tolist(),
            "occupied": occupied.tolist(),
        }
        for i, H in enumerate(horizons):
            r_est, r_lo, r_hi = mean_ci(returns[i] / (H / 2), rng)
            n_est, n_lo, n_hi = mean_ci(new[i] / (H / 2), rng)
            o_est, o_lo, o_hi = mean_ci(occupied[i] / states, rng)
            rows.append(
                {
                    "suite": "S5_finite_capacity",
                    "D": D,
                    "L": L,
                    "states": states,
                    "horizon": int(H),
                    "horizon_per_state": H / states,
                    "anchored_return_rate": r_est,
                    "anchored_return_ci_lo": r_lo,
                    "anchored_return_ci_hi": r_hi,
                    "new_state_rate": n_est,
                    "new_state_ci_lo": n_lo,
                    "new_state_ci_hi": n_hi,
                    "occupied_fraction": o_est,
                    "occupied_ci_lo": o_lo,
                    "occupied_ci_hi": o_hi,
                }
            )
    return rows, raw


def run_s6():
    T = 10000
    theta = math.sqrt(2.0) - 1.0
    rotation = np.mod(np.arange(T + 1) * theta, 1.0)
    rotation_exact = len(np.unique(rotation)) / len(rotation)
    rotation_coarse = float(np.mean(np.minimum(rotation, 1.0 - rotation) <= 0.05))

    rng = np.random.default_rng(MASTER_SEED + 6000)
    iid = rng.random((T + 1, 2))
    iid_exact_unique = len({tuple(x) for x in iid}) / len(iid)
    iid_distance = np.abs(iid[:, 0] - iid[0, 0])
    iid_projected_coarse = float(
        np.mean(np.minimum(iid_distance, 1.0 - iid_distance) <= 0.05)
    )

    rows = [
        {
            "suite": "S6_counterexample",
            "model": "irrational_rotation",
            "exact_unique_fraction": rotation_exact,
            "coarse_anchored_rate": rotation_coarse,
            "self_repulsion": False,
            "high_dimension": False,
            "informative_projection": True,
        },
        {
            "suite": "S6_counterexample",
            "model": "iid_unit_square",
            "exact_unique_fraction": iid_exact_unique,
            "coarse_anchored_rate": iid_projected_coarse,
            "self_repulsion": False,
            "high_dimension": False,
            "informative_projection": True,
        },
        {
            "suite": "S6_counterexample",
            "model": "constant_projection",
            "exact_unique_fraction": iid_exact_unique,
            "coarse_anchored_rate": 1.0,
            "self_repulsion": False,
            "high_dimension": False,
            "informative_projection": False,
        },
    ]
    return rows, {"rotation": rotation.tolist(), "iid": iid.tolist()}


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    return value


def write_csv(path: Path, suites: dict):
    rows = []
    for suite_rows in suites.values():
        rows.extend(suite_rows)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(json_safe(row))


def main():
    global HORIZONS, BASE_PATHS, SELF_REPEL_PATHS
    global HISTORY_PATHS, FINITE_PATHS, BOOTSTRAPS, QUICK

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "results"),
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a non-evidential smoke test with reduced horizons and paths.",
    )
    args = parser.parse_args()
    if args.quick:
        QUICK = True
        HORIZONS = np.array([32, 64, 128], dtype=int)
        BASE_PATHS = 200
        SELF_REPEL_PATHS = 4
        HISTORY_PATHS = 8
        FINITE_PATHS = 8
        BOOTSTRAPS = 20
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    analysis_rng = np.random.default_rng(MASTER_SEED + 99)
    started = time.time()

    suites = {}
    raw = {}
    runners = [
        ("S1_projection", lambda: run_s1(analysis_rng)),
        ("S2_drift", lambda: run_s2(analysis_rng)),
        ("S3_self_repulsion", lambda: run_s3(analysis_rng)),
        ("S4_historical", lambda: run_s4(analysis_rng)),
        ("S5_finite_capacity", lambda: run_s5(analysis_rng)),
        ("S6_counterexample", run_s6),
    ]
    for name, runner in runners:
        t0 = time.time()
        print(f"Running {name}...", flush=True)
        suites[name], raw[name] = runner()
        print(f"  completed in {time.time() - t0:.1f}s", flush=True)

    manifest = {
        "master_seed": MASTER_SEED,
        "horizons": HORIZONS.tolist(),
        "base_paths": BASE_PATHS,
        "self_repel_paths": SELF_REPEL_PATHS,
        "history_paths": HISTORY_PATHS,
        "finite_paths": FINITE_PATHS,
        "bootstraps": BOOTSTRAPS,
        "historical_lag": HISTORY_LAG,
        "quick_smoke_test": QUICK,
        "elapsed_seconds": time.time() - started,
    }
    summary_path = output / "cdt_simulation_campaign.json"
    raw_path = output / "cdt_simulation_campaign_raw.json"
    csv_path = output / "cdt_simulation_campaign.csv"
    summary_path.write_text(
        json.dumps(json_safe({"manifest": manifest, "suites": suites}), indent=2),
        encoding="utf-8",
    )
    raw_path.write_text(json.dumps(json_safe(raw)), encoding="utf-8")
    write_csv(csv_path, suites)
    print(f"Wrote {summary_path}")
    print(f"Wrote {raw_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
