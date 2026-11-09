"""Run the frozen 2026-11 application campaign; keep September evidence intact.

Each suite writes independent-replicate records and metadata. Synthetic suites
are model tests, not deployment validation. --smoke is implementation-only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from examples.cdt_use_case_demo import simulate as rate_demo
from gamma_probe import gamma_hat
from experiments.cdt_simulation_campaign import simulate_self_repelling_path
import alive_reward_demo as gate_toy

MASTER = 20261110
PLAN = ROOT / "experiments/cdt_application_preregistration_20261109.md"
PLAN_COMMIT = "9e9f307ef55376b0cb0d079d11feeef562092eac"
EXPECTED_PLAN_HASH = "81c3ef25517094012ae5c137769a477ebda1663e9f9c0613c68338bee6da8bb1"


def seed_for(suite, replicate):
    return MASTER + suite * 10000 + replicate


def rng_for(suite, replicate):
    return np.random.default_rng(seed_for(suite, replicate))


def rms(a):
    return float(np.sqrt(np.mean(np.asarray(a) ** 2)))


def longest_miss(flags):
    run = best = 0
    for flag in flags:
        run = 0 if flag else run + 1
        best = max(best, run)
    return int(best)


def orthogonal(rng, n):
    return np.linalg.qr(rng.normal(size=(n, n)))[0]


def nearest(q, bank):
    return np.argmin(np.sum((q[:, None, :] - bank[None, :, :]) ** 2, axis=2), axis=1)


def a1(rep, smoke):
    r = rate_demo(steps=256 if smoke else 4096, paths=8 if smoke else 64,
                  seed=seed_for(1, rep))
    final = [x for x in r["records"] if x["horizon"] == (256 if smoke else 4096)]
    by = {x["mode"]: x for x in final}
    return {"primary_effect": by["restoring"]["structural_tail_frequency_mean"] -
            by["free"]["structural_tail_frequency_mean"], "arms": r["records"]}


def a2(rep, smoke):
    rng = rng_for(2, rep)
    npaths, T = (64, 256) if smoke else (2048, 4096)
    horizons = [256] if smoke else [256, 1024, 4096]
    cutpoints = set(horizons + [h // 2 for h in horizons])
    position = np.zeros((3, npaths, 2))
    drift = np.array([[0, 0], [0, .08], [.08, 0]])
    counts = np.zeros((3, npaths, 2), dtype=int)
    snapshots = {}
    for n in range(1, T + 1):
        position += rng.normal(size=(1, npaths, 2)) + drift[:, None, :]
        counts[:, :, 0] += np.linalg.norm(position, axis=2) <= .5
        counts[:, :, 1] += np.abs(position[:, :, 0]) <= .5
        if n in cutpoints:
            snapshots[n] = counts.copy()
    rows = []
    for h in horizons:
        tails = snapshots[h] - snapshots[h // 2]
        for i, mode in enumerate(["neutral", "hidden", "visible"]):
            rows.append({"arm": mode, "horizon": h, "paths": npaths,
                         "full_tail_mean": float(tails[i, :, 0].mean()),
                         "structural_tail_mean": float(tails[i, :, 1].mean()),
                         "full_affected_paths": int(np.sum(tails[i, :, 0] > 0)),
                         "structural_affected_paths": int(np.sum(tails[i, :, 1] > 0))})
    final = {r["arm"]: r for r in rows if r["horizon"] == T}
    return {"primary_effect": final["hidden"]["structural_tail_mean"] -
            final["visible"]["structural_tail_mean"],
            "cutoff_steps": 2 / .08 ** 2, "arms": rows}


def a3(rep, smoke):
    rng = rng_for(3, rep)
    d, T, paths, ntrain = 8, (96 if smoke else 384), 16, 1024
    theta = 2 * np.pi / 48
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    O = orthogonal(rng, d)
    trueW = np.eye(d) * .7
    trueW[:2, :2] = R
    latent = rng.normal(size=(ntrain, d))
    train = latent @ O.T
    targets = latent @ trueW.T @ O.T
    W = np.linalg.lstsq(train, targets, rcond=None)[0].T
    decoder = np.linalg.lstsq(train, latent[:, :2], rcond=None)[0]
    phase = rng.uniform(0, 2 * np.pi, paths)
    initial = np.column_stack([np.cos(phase), np.sin(phase)])
    h0 = np.column_stack([initial, np.zeros((paths, d - 2))]) @ O.T
    states = np.tile(h0[None, :, :], (3, 1, 1))
    target = initial.copy()
    loss = np.zeros(3)
    cadence_hits, raw_hits = np.zeros(3), np.zeros(3)
    for n in range(1, T + 1):
        noise = rng.normal(scale=.2, size=(paths, 2))
        states = states @ W.T
        states[1] += noise @ O[:, 2:4].T
        states[2] += noise @ O[:, :2].T
        target = target @ R.T
        decoded = states @ decoder
        loss += np.mean((decoded - target[None, :, :]) ** 2, axis=(1, 2))
        if n % 48 == 0:
            cadence_hits += np.mean(np.linalg.norm(decoded - initial, axis=2) <= .18, axis=1)
            raw_hits += np.mean(np.linalg.norm(states - h0, axis=2) <= .12, axis=1)
    arms = [{"arm": mode, "waveform_mse": float(loss[i] / T),
             "structural_cadence_hit_fraction": float(cadence_hits[i] / (T // 48)),
             "full_cadence_hit_fraction": float(raw_hits[i] / (T // 48))}
            for i, mode in enumerate(["baseline", "hidden_noise", "visible_noise"])]
    hidden = arms[1]
    return {"primary_effect": arms[2]["waveform_mse"] - hidden["waveform_mse"],
            "functional_pass": hidden["waveform_mse"] < .01 and
            hidden["structural_cadence_hit_fraction"] >= .9,
            "decoder_nullspace_residual": float(np.max(np.abs(O[:, 2:4].T @ decoder))),
            "arms": arms}


def a4(rep, smoke):
    rng = rng_for(4, rep)
    O = orthogonal(rng, 16)
    eye = np.eye(8)
    def make(labels, shifted=False):
        labels = np.asarray(labels)
        content = eye[labels] + rng.normal(scale=.03, size=(len(labels), 8))
        context = rng.normal(size=(len(labels), 8)) + (4 if shifted else 0)
        return np.column_stack([content, context]) @ O.T
    trlabels = rng.integers(0, 8, 1024)
    tr = make(trlabels)
    D = np.linalg.lstsq(tr, eye[trlabels], rcond=None)[0]
    random_map = orthogonal(rng, 16)[:, :8]
    maps = {"raw": np.eye(16), "structure": D, "random8": random_map,
            "constant": np.zeros((16, 1))}
    bank = make(np.arange(8))
    labels = np.tile(np.arange(8), 8 if smoke else 64)
    queries = make(labels, True)
    positives = make(labels)
    negatives = make((labels + 1) % 8)
    cal_labels = rng.integers(0, 8, 256)
    ca, cb = make(cal_labels), make(cal_labels)
    rows = []
    for mode, matrix in maps.items():
        threshold = float(np.quantile(np.linalg.norm((ca - cb) @ matrix, axis=1), .95))
        pred = nearest(queries @ matrix, bank @ matrix)
        rows.append({"arm": mode, "accuracy": float(np.mean(pred == labels)),
                     "positive_acceptance": float(np.mean(np.linalg.norm(
                         (queries - positives) @ matrix, axis=1) <= threshold)),
                     "negative_false_acceptance": float(np.mean(np.linalg.norm(
                         (queries - negatives) @ matrix, axis=1) <= threshold)),
                     "calibrated_distance_threshold": threshold,
                     "stored_dimensions": matrix.shape[1]})
    by = {r["arm"]: r for r in rows}
    s = by["structure"]
    return {"primary_effect": s["accuracy"] - by["raw"]["accuracy"],
            "functional_pass": s["accuracy"] >= .9 and s["positive_acceptance"] >= .9
            and s["negative_false_acceptance"] <= .1, "arms": rows}


def a5(rep, smoke):
    rng = rng_for(5, rep)
    T = 384 if smoke else 2048
    n = np.arange(1, T + 1)
    phase0 = rng.uniform(0, 2 * np.pi)
    noise = rng.normal(scale=.003, size=(T, 2))
    pause_start = (T // 2 // 48) * 48 + 12
    expected_phase = phase0 + 2 * np.pi * n / 48
    reference = np.column_stack([np.cos(expected_phase), np.sin(expected_phase)])
    rows = []
    for mode in ["baseline", "translated", "faster", "pause", "reverse", "constant"]:
        steps = n.copy()
        if mode == "pause":
            steps = n - np.clip(n - pause_start, 0, 96)
        if mode == "reverse":
            steps = -n
        phase = phase0 + 2 * np.pi * steps / 48
        features = np.column_stack([np.cos(phase), np.sin(phase)]) + noise
        if mode == "constant":
            features[:] = [np.cos(phase0), np.sin(phase0)]
        origin = 100 if mode == "translated" else 0
        world = origin + n * (.04 if mode == "faster" else .02)
        anchor = np.array([np.cos(phase0), np.sin(phase0)])
        hit = np.linalg.norm(features - anchor, axis=1) <= .18
        raw_hit = np.sqrt(np.sum((features - anchor) ** 2, axis=1) +
                           (world - origin) ** 2) <= .12
        angles = (np.arctan2(features[:, 1], features[:, 0]) - phase0) % (2 * np.pi)
        bins = np.floor(angles * 4 / (2 * np.pi)).astype(int)
        changed = bins[1:] != bins[:-1]
        ordered = ((bins[1:] - bins[:-1]) % 4)[changed] == 1
        rows.append({"arm": mode, "structural_fraction": float(hit.mean()),
                     "full_fraction": float(raw_hit.mean()), "longest_miss": longest_miss(hit),
                     "phase_tracking_mse": float(np.mean((features - reference) ** 2)),
                     "phase_coverage": len(np.unique(bins)) / 4,
                     "ordered_transition_fraction": float(ordered.mean()) if len(ordered) else None,
                     "deadline_pass": longest_miss(hit) <= 64})
    by = {r["arm"]: r for r in rows}
    return {"primary_effect": by["pause"]["longest_miss"] - by["baseline"]["longest_miss"],
            "arms": rows, "scope": "kinematic model only; no falls or energy model"}


def a6(rep, smoke):
    rng = rng_for(6, rep)
    O = orthogonal(rng, 4)
    latent = rng.normal(size=(1024, 4))
    X = latent @ O.T + rng.normal(scale=.01, size=latent.shape)
    maps = {"full": np.linalg.lstsq(X, latent[:, :2], rcond=None)[0],
            "restricted": np.vstack([np.linalg.lstsq(X[:, :2], latent[:, :2], rcond=None)[0],
                                      np.zeros((2, 2))]), "constant": np.zeros((4, 2))}
    count = 64 if smoke else 512
    signal = np.column_stack([rng.choice([-1., 1.], count), rng.uniform(-1, 1, count)])
    nuisance = rng.normal(size=(count, 2))
    observation_noise = rng.normal(scale=.01, size=(count, 4))
    rows = []
    for shift in [0, 4]:
        for changed in [False, True]:
            truth = signal.copy()
            if changed:
                truth[:, 0] *= -1
            Xtest = np.column_stack([truth, nuisance + shift]) @ O.T + observation_noise
            for mode, D in maps.items():
                predicted = Xtest @ D
                rows.append({"arm": mode, "nuisance_shift": shift, "signal_changed": changed,
                             "rmse": rms(predicted - truth),
                             "sign_accuracy": float(np.mean((predicted[:, 0] > 0) ==
                                                            (truth[:, 0] > 0)))})
    by = {r["arm"]: r for r in rows if r["nuisance_shift"] == 4 and not r["signal_changed"]}
    return {"primary_effect": by["restricted"]["rmse"] - by["full"]["rmse"],
            "functional_pass": all(r["rmse"] < .1 and r["sign_accuracy"] >= .9
                                   for r in rows if r["arm"] == "full"), "arms": rows}


def resample_closed(points, count=64):
    points = np.asarray(points, dtype=float)
    points = np.vstack([points, points[0]])
    distances = np.r_[0., np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    keep = np.r_[True, np.diff(distances) > 0]
    points, distances = points[keep], distances[keep]
    if distances[-1] <= 0:
        raise ValueError("zero-length stroke")
    t = np.linspace(0, distances[-1], count, endpoint=False)
    return np.column_stack([np.interp(t, distances, points[:, i]) for i in range(2)])


def shape_features(strokes):
    x = np.asarray(strokes) - np.mean(strokes, axis=1, keepdims=True)
    scale = np.sqrt(np.mean(np.sum(x * x, axis=2), axis=1))
    if np.any(scale <= 0):
        raise ValueError("zero-scale stroke")
    x = x / scale[:, None, None]
    fft = np.abs(np.fft.fft(x[:, :, 0] + 1j * x[:, :, 1], axis=1)) / x.shape[1]
    paired = fft[:, 1:9] + fft[:, -1:-9:-1]
    y = np.roll(x, -1, axis=1)
    area = np.sum(x[:, :, 0] * y[:, :, 1] - x[:, :, 1] * y[:, :, 0], axis=1) / (2 * np.pi)
    return np.column_stack([paired, area])


def gesture_set(rng, per_class, shifted=False):
    t = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    circle = np.column_stack([np.cos(t), np.sin(t)])
    ellipse = circle * [1.7, .6]
    v = np.column_stack([np.cos(np.arange(3) * 2 * np.pi / 3),
                         np.sin(np.arange(3) * 2 * np.pi / 3)])
    triangle = resample_closed(v)
    strokes, labels = [], []
    for label in range(6):
        shape, direction = label % 3, label // 3
        template = [circle, ellipse, triangle][shape]
        for _ in range(per_class):
            p = template[::-1] if direction else template
            p = np.roll(p, rng.integers(64), axis=0)
            angle = rng.uniform(0, 2 * np.pi)
            R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
            p = p @ R.T * rng.uniform(.5, 2)
            p = p + rng.normal(size=2) + (4 if shifted else 0)
            p = p + rng.normal(scale=.005, size=p.shape)
            strokes.append(p)
            labels.append(label)
    return np.array(strokes), np.array(labels)


def a7(rep, smoke):
    rng = rng_for(7, rep)
    train, labels = gesture_set(rng, 16)
    calibration, _ = gesture_set(rng, 8)
    test, truth = gesture_set(rng, 4 if smoke else 32, True)
    random_map = np.linalg.qr(rng.normal(size=(128, 9)))[0]
    features = {"raw": lambda x: x.reshape(len(x), -1),
                "structure": shape_features, "shape_only": lambda x: shape_features(x)[:, :8],
                "random9": lambda x: x.reshape(len(x), -1) @ random_map,
                "constant": lambda x: np.zeros((len(x), 1))}
    rows = []
    for mode, transform in features.items():
        tr = transform(train)
        bank = np.array([tr[labels == k].mean(axis=0) for k in range(6)])
        predicted = nearest(transform(test), bank)
        rows.append({"arm": mode, "accuracy": float(np.mean(predicted == truth)),
                     "dimensions": tr.shape[1]})
    bank = np.array([shape_features(train)[labels == k].mean(axis=0) for k in range(6)])
    permuted = np.array([p[rng.permutation(64)] for p in test])
    rows.append({"arm": "structure_point_order_permuted",
                 "accuracy": float(np.mean(nearest(shape_features(permuted), bank) == truth)),
                 "dimensions": 9})
    # Calibration descriptors are computed separately, without test fitting.
    cal_features = shape_features(calibration)
    by = {r["arm"]: r for r in rows}
    return {"primary_effect": by["structure"]["accuracy"] - by["random9"]["accuracy"],
            "functional_pass": by["structure"]["accuracy"] >= .9,
            "calibration_descriptor_rms": rms(cal_features), "arms": rows}


def a8(rep, smoke):
    rows = []
    for D in [2, 3]:
        for i, gamma in enumerate([-.5, 0, .5, 2, 10]):
            seed = seed_for(8, rep) + D * 100000 + i * 1000
            row = simulate_self_repelling_path(D, gamma, 128 if smoke else 2048, seed)
            rows.append({"D": D, "gamma": gamma, "seed": seed, **row})
    by = {r["gamma"]: r for r in rows if r["D"] == 2}
    return {"primary_effect": by[0]["full_historical"] - by[2]["full_historical"], "arms": rows}


def a9(rep, smoke):
    Q = [[Fraction(3, 4), Fraction(1, 4)], [Fraction(1, 4), Fraction(3, 4)]]
    delta = [Fraction(1, 32) * Fraction(1, 2) ** n for n in range(6)]
    tv = Fraction(0)
    for tail in product([0, 1], repeat=6):
        p = q = Fraction(1)
        current = 0
        for n, nxt in enumerate(tail):
            p *= Q[current][nxt] + (delta[n] if nxt else -delta[n])
            q *= Q[current][nxt]
            current = nxt
        tv += abs(p - q) / 2
    return {"exact_path_TV": str(tv), "exact_sum_bound": str(sum(delta)),
            "bound_holds": tv <= sum(delta), "enumerated_paths": 64}


def a10(rep, smoke):
    rng = rng_for(10, rep)
    rows = []
    for name in ["drawing_data.csv", "drawing_data_v1.csv"]:
        data = np.genfromtxt(ROOT / name, delimiter=",", names=True)
        strokes, skipped = [], []
        for s in np.unique(data["stroke"]):
            points = np.column_stack([data["x"][data["stroke"] == s],
                                      data["y"][data["stroke"] == s]])
            try:
                strokes.append(resample_closed(points))
            except ValueError as error:
                skipped.append({"stroke": int(s), "reason": str(error)})
        strokes = np.array(strokes)
        actual = shape_features(strokes)
        permuted = shape_features(np.array([p[rng.permutation(64)] for p in strokes]))
        raw = np.sqrt(np.mean(np.sum((strokes - strokes[0]) ** 2, axis=2), axis=1))
        desc = np.linalg.norm(actual - actual[0], axis=1)
        shuffled_desc = np.linalg.norm(permuted - actual[0], axis=1)
        historical = [bool(np.min(np.linalg.norm(actual[:n] - actual[n], axis=1)) <= .15)
                      for n in range(1, len(actual))]
        rows.append({"file": name, "sha256": sha(ROOT / name), "strokes": len(strokes),
                     "skipped": skipped, "raw_anchor_fraction_excluding_first": float(np.mean(raw[1:] <= 8)),
                     "structural_anchor_fraction_excluding_first": float(np.mean(desc[1:] <= .15)),
                     "structural_historical_fraction": float(np.mean(historical)),
                     "permuted_anchor_fraction": float(np.mean(shuffled_desc[1:] <= .15)),
                     "ordered_anchor_distances": desc.tolist(),
                     "permuted_anchor_distances": shuffled_desc.tolist(),
                     "scope": "unlabeled recordings; no subject independence or task discrimination claim"})
    return {"recordings": rows}


def a11(rep, smoke):
    rng = rng_for(11, rep)
    n = 128 if smoke else 256
    innovations = rng.normal(size=(n, 2))
    ar = np.empty_like(innovations)
    ar[0] = innovations[0] / np.sqrt(1 - .8 ** 2)
    for i in range(1, n):
        ar[i] = .8 * ar[i - 1] + innovations[i]
    paths = {"iid": innovations, "AR08": ar, "walk": np.cumsum(innovations, axis=0),
             "drift": np.cumsum(innovations + [.1, 0], axis=0)}
    rows = []
    for case, path in paths.items():
        for null in ["phase", "steps"]:
            r = gamma_hat(path, tau=4, M=256, K=3 if smoke else 7,
                          nblocks=8, seed=seed_for(11, rep), null=null)
            rows.append({"case": case, "null": null, **r,
                         "obsolete_rule_positive": bool(r["est"] > .4 and r["lo"] > 0)})
    return {"arms": rows}


def a12(rep, smoke):
    old = gate_toy.H, gate_toy.T, gate_toy.EPOCHS
    gate_toy.H, gate_toy.T, gate_toy.EPOCHS = 8, 96, (3 if smoke else 60)
    rows = []
    try:
        arms = [(lam, True) for lam in [0, .01, .05, .2]] + [(0, False), (.05, False)]
        for lam, learned in arms:
            P, train_loss, gates = gate_toy.train(seed_for(12, rep), lam, "cap", learn_gates=learned)
            novel, opened = gate_toy.probe(P, seed_for(12, rep))
            losses = []
            for phase in [.7, 1.9, 2.6]:
                t = np.arange(192)
                xs = np.sin(.10 * t + phase) + .5 * np.sin(.031 * t + phase / 2)
                _, _, predicted, _ = gate_toy.forward(P["W_h"], P["W_x"], P["b"],
                                                      P["Wy"], P["z"], xs)
                losses.append(float(np.mean((predicted[24:] - xs[24:]) ** 2)))
            rows.append({"lambda": lam, "learned_gates": learned, "training_mse": train_loss,
                         "heldout_driven_mse": float(np.mean(losses)),
                         "free_run_new_cell_fraction": novel, "open_gate_count": opened,
                         "gate_sum": float(gates.sum()), "gates": gates.tolist(),
                         "scope": "driven identity task; free-run novelty is not autonomous task recovery"})
    finally:
        gate_toy.H, gate_toy.T, gate_toy.EPOCHS = old
    return {"arms": rows}


SUITES = {f"A{i}": globals()[f"a{i}"] for i in range(1, 13)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--suites", default=",".join(SUITES))
    args = parser.parse_args()
    selected = args.suites.split(",")
    if any(s not in SUITES for s in selected):
        parser.error("unknown suite")
    if sha(PLAN) != EXPECTED_PLAN_HASH:
        parser.error("frozen plan hash changed; record an explicit amendment")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    if any((out / (suite + ".json")).exists() for suite in selected):
        parser.error("refusing to overwrite suite evidence; choose another output directory")
    sources = [Path(__file__), PLAN, ROOT / "examples/cdt_use_case_demo.py",
               ROOT / "alive_reward_demo.py", ROOT / "gamma_probe.py",
               ROOT / "experiments/cdt_simulation_campaign.py"]
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(), "smoke_only": args.smoke,
                "plan_commit": PLAN_COMMIT, "master_seed": MASTER,
                "python": platform.python_version(), "numpy": np.__version__,
                "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
                "suites": selected, "torch_available": importlib.util.find_spec("torch") is not None}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for suite in selected:
        count = 1 if suite in ["A9", "A10"] else (2 if args.smoke else (8 if suite == "A12" else 16))
        start = time.monotonic()
        records = []
        print(f"Starting {suite}, {count} independent replicates", flush=True)
        for rep in range(count):
            try:
                records.append({"replicate": rep, "seed": seed_for(int(suite[1:]), rep),
                                **SUITES[suite](rep, args.smoke)})
            except Exception as error:
                records.append({"replicate": rep, "error_type": type(error).__name__, "error": str(error)})
                print(f"ERROR {suite} replicate {rep}: {error!r}", flush=True)
        result = {"suite": suite, "smoke_only": args.smoke,
                  "elapsed_seconds": time.monotonic() - start, "records": records}
        (out / (suite + ".json")).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(f"Finished {suite}: {result['elapsed_seconds']:.2f}s", flush=True)
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
