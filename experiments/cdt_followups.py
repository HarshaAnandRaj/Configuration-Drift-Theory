"""Registered follow-ups for weaknesses found by the CDT campaign."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "experiments" / "cdt_simulation_campaign.py"
SPEC = importlib.util.spec_from_file_location("cdt_campaign", CAMPAIGN_PATH)
campaign = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(campaign)

MASTER_SEED = 20260905
DRIFT_HORIZONS = np.array([256, 512, 1024, 2048, 4096, 8192], dtype=int)
SELF_HORIZONS = np.array([256, 512, 1024, 2048, 4096], dtype=int)
DRIFT_PATHS = 12000
SELF_PATHS = 160
BOOTSTRAPS = 500
LAG = 8


def summarize_block(block, horizons, rng):
    slope, slope_lo, slope_hi = campaign.slope_ci(
        block, horizons, rng, B=BOOTSTRAPS
    )
    rows = []
    for i, horizon in enumerate(horizons):
        estimate, lo, hi = campaign.mean_ci(block[i], rng, B=BOOTSTRAPS)
        rows.append(
            {
                "horizon": int(horizon),
                "estimate": estimate,
                "ci_lo": lo,
                "ci_hi": hi,
                "slope": slope,
                "slope_ci_lo": slope_lo,
                "slope_ci_hi": slope_hi,
            }
        )
    return rows


def run_f1(rng):
    arms = [("neutral", 0.0, None)]
    arms += [("hidden", d, 1) for d in [0.02, 0.05, 0.10]]
    arms += [("visible", d, 0) for d in [0.02, 0.05, 0.10]]
    rows = []
    raw = {}
    blocks = {}
    for i, (kind, delta, axis) in enumerate(arms):
        counts = campaign.lattice_tail_counts(
            2,
            DRIFT_PATHS,
            DRIFT_HORIZONS,
            MASTER_SEED + 71000 + i,
            delta=delta,
            drift_axis=axis,
        ).astype(float)
        blocks[(kind, delta)] = counts
        raw[f"{kind}_{delta:.2f}"] = {
            "full": counts[1].tolist(),
            "projected": counts[0].tolist(),
        }
        for observable, block in [("full", counts[1]), ("projected", counts[0])]:
            for row in summarize_block(block, DRIFT_HORIZONS, rng):
                row.update(
                    {
                        "suite": "F1_drift_causal",
                        "kind": kind,
                        "delta": delta,
                        "observable": observable,
                        "Pe": delta * math.sqrt(row["horizon"]) / math.sqrt(0.5),
                    }
                )
                rows.append(row)

    neutral = blocks[("neutral", 0.0)]
    for row in rows:
        h = int(np.where(DRIFT_HORIZONS == row["horizon"])[0][0])
        m = 1 if row["observable"] == "projected" else 2
        current = blocks[(row["kind"], row["delta"])][m - 1, h]
        base = neutral[m - 1, h]
        ratio, lo, hi = campaign.ratio_ci(current, base, rng, B=BOOTSTRAPS)
        row["ratio_to_neutral"] = ratio
        row["ratio_ci_lo"] = lo
        row["ratio_ci_hi"] = hi
    return rows, raw


def self_repelling_path(D, gamma, horizons, seed):
    rng = np.random.default_rng(seed)
    T = int(horizons[-1])
    pos = np.zeros(D, dtype=np.int32)
    offsets = np.vstack([np.eye(D, dtype=np.int32), -np.eye(D, dtype=np.int32)])
    visits = {}
    history = [tuple(pos)]
    old_full = set()
    old_proj = set()
    distinct = {tuple(pos)}
    full_counts = np.zeros(len(horizons), dtype=np.int32)
    projected_counts = np.zeros(len(horizons), dtype=np.int32)
    late_full_historical = 0
    late_projected_historical = 0

    for t in range(1, T + 1):
        candidates = pos + offsets
        local_times = np.array(
            [visits.get(tuple(candidate), 0) for candidate in candidates],
            dtype=float,
        )
        scores = -gamma * local_times
        weights = np.exp(scores - np.max(scores))
        weights /= np.sum(weights)
        pos = candidates[rng.choice(len(candidates), p=weights)]
        key = tuple(pos)
        projected = int(pos[0])
        if t >= LAG:
            old = history[t - LAG]
            old_full.add(old)
            old_proj.add(int(old[0]))
        if t > T // 2:
            late_full_historical += key in old_full
            late_projected_historical += projected in old_proj
        active = np.flatnonzero((t > horizons // 2) & (t <= horizons))
        for h in active:
            full_counts[h] += all(value == 0 for value in key)
            projected_counts[h] += projected == 0
        history.append(key)
        distinct.add(key)
        visits[key] = visits.get(key, 0) + 1

    return {
        "full_counts": full_counts,
        "projected_counts": projected_counts,
        "full_historical": late_full_historical / (T // 2),
        "projected_historical": late_projected_historical / (T // 2),
        "discovery_fraction": len(distinct) / (T + 1),
    }


def run_f2(rng):
    rows = []
    raw = {}
    for D in [2, 3]:
        for gi, gamma in enumerate([0.0, 0.5, 1.0, 2.0, 5.0, 10.0]):
            full = np.zeros((len(SELF_HORIZONS), SELF_PATHS), dtype=float)
            projected = np.zeros_like(full)
            historical_full = np.zeros(SELF_PATHS, dtype=float)
            historical_projected = np.zeros(SELF_PATHS, dtype=float)
            discovery = np.zeros(SELF_PATHS, dtype=float)
            for trial in range(SELF_PATHS):
                out = self_repelling_path(
                    D,
                    gamma,
                    SELF_HORIZONS,
                    MASTER_SEED + 720000 + D * 10000 + gi * 1000 + trial,
                )
                full[:, trial] = out["full_counts"]
                projected[:, trial] = out["projected_counts"]
                historical_full[trial] = out["full_historical"]
                historical_projected[trial] = out["projected_historical"]
                discovery[trial] = out["discovery_fraction"]

            full_summary = summarize_block(full, SELF_HORIZONS, rng)
            projected_summary = summarize_block(projected, SELF_HORIZONS, rng)
            ph, ph_lo, ph_hi = campaign.mean_ci(
                historical_projected, rng, B=BOOTSTRAPS
            )
            fh, fh_lo, fh_hi = campaign.mean_ci(
                historical_full, rng, B=BOOTSTRAPS
            )
            disc, disc_lo, disc_hi = campaign.mean_ci(discovery, rng, B=BOOTSTRAPS)
            slope = projected_summary[0]["slope"]
            if slope is None or not np.isfinite(slope):
                classification = "unestimable"
            elif slope >= -0.10:
                classification = "compatible with persistent anchored projection"
            else:
                classification = "finite-horizon decay warning"
            for i, horizon in enumerate(SELF_HORIZONS):
                rows.append(
                    {
                        "suite": "F2_self_repulsion_observable",
                        "D": D,
                        "gamma": gamma,
                        "horizon": int(horizon),
                        "full_anchored": full_summary[i],
                        "projected_anchored": projected_summary[i],
                        "full_historical": fh,
                        "full_historical_ci_lo": fh_lo,
                        "full_historical_ci_hi": fh_hi,
                        "projected_historical": ph,
                        "projected_historical_ci_lo": ph_lo,
                        "projected_historical_ci_hi": ph_hi,
                        "discovery_fraction": disc,
                        "discovery_ci_lo": disc_lo,
                        "discovery_ci_hi": disc_hi,
                        "classification": classification,
                    }
                )
            raw[f"D{D}_g{gamma:.1f}"] = {
                "full_counts": full.tolist(),
                "projected_counts": projected.tolist(),
                "full_historical": historical_full.tolist(),
                "projected_historical": historical_projected.tolist(),
                "discovery_fraction": discovery.tolist(),
            }
    return rows, raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(ROOT / "results"))
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(MASTER_SEED + 70000)
    print("Running F1 drift causal control...", flush=True)
    f1, raw1 = run_f1(rng)
    print("Running F2 self-repulsion observable check...", flush=True)
    f2, raw2 = run_f2(rng)
    payload = {
        "manifest": {
            "master_seed": MASTER_SEED,
            "drift_horizons": DRIFT_HORIZONS.tolist(),
            "self_horizons": SELF_HORIZONS.tolist(),
            "drift_paths": DRIFT_PATHS,
            "self_paths": SELF_PATHS,
            "bootstraps": BOOTSTRAPS,
        },
        "F1_drift_causal": f1,
        "F2_self_repulsion_observable": f2,
    }
    (output / "cdt_followups.json").write_text(
        json.dumps(campaign.json_safe(payload), indent=2), encoding="utf-8"
    )
    (output / "cdt_followups_raw.json").write_text(
        json.dumps(campaign.json_safe({"F1": raw1, "F2": raw2})), encoding="utf-8"
    )
    print("Wrote follow-up outputs.", flush=True)


if __name__ == "__main__":
    main()
