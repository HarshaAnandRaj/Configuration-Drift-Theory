"""dimension_test.py
Decide the Configuration-Drift Hypothesis quantitatively.

Mathematical criterion: a diffusive explorer (walk dimension w = 2) on a
configuration manifold of correlation dimension nu is RECURRENT (exact repeats
persist) iff nu <= w, TRANSIENT (exact recurrence vanishes, rhymes persist)
iff nu > w. This generalizes Polya (nu = D, threshold 2) to arbitrary manifolds.

We measure nu via the pair-correlation integral C(eps) = fraction of
configuration pairs within distance eps; C(eps) ~ eps^nu in the scaling region.

Pipeline:
  1. Validate the estimator on synthetic point clouds of KNOWN dimension.
  2. Measure nu for the human drawing (2-D centroids and full 4-D config),
     for both the fresh run and the v1 backup.
"""

import csv
import numpy as np


def load_configs(path):
    strokes = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            s = int(row["stroke"])
            strokes.setdefault(s, []).append(
                (float(row["x"]), float(row["y"]), float(row["t_seconds"]))
            )
    feats = []
    for s in sorted(strokes):
        p = np.array(sorted(strokes[s]))
        cx, cy = p[:, 0].mean(), p[:, 1].mean()
        r = float(np.mean(np.hypot(p[:, 0] - cx, p[:, 1] - cy)))
        seg = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
        dur = p[-1, 2] - p[0, 2]
        sp = float(seg.sum() / dur) if dur > 0 else 0.0
        feats.append([cx, cy, r, sp])
    F = np.array(feats, dtype=float)
    lo, hi = np.percentile(F, 1, axis=0), np.percentile(F, 99, axis=0)
    F = np.clip((F - lo) / (hi - lo + 1e-12), 0, 1)
    return F


def pair_distances(P):
    n = len(P)
    diff = P[:, None, :] - P[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(n, 1)
    return d[iu]


def corr_integral(d):
    qs = np.geomspace(0.5, 99.0, 40)
    eps = np.percentile(d, qs)
    C = np.array([(d <= e).mean() for e in eps])
    return eps, C


def fit_nu(eps, C, lo=0.02, hi=0.90):
    m = (C > lo) & (C < hi)
    if m.sum() < 5:
        m = np.ones(len(C), dtype=bool)
    slope, ic = np.polyfit(np.log(eps[m]), np.log(C[m]), 1)
    return float(slope), int(m.sum())


def measure_cloud(P, label):
    d = pair_distances(P)
    eps, C = corr_integral(d)
    nu, k = fit_nu(eps, C)
    print(f"{label:<38} n={len(P):<5} nu = {nu:.3f}   ({k} scaling pts)")
    return nu


if __name__ == "__main__":
    rng = np.random.default_rng(0)

    print("=== 1. Estimator validation (known-D synthetic clouds) ===")
    for D in [1, 2, 3, 4]:
        P = rng.random((1500, D))
        measure_cloud(P, f"uniform cube D={D}")
    P = rng.random((800, 1))
    P4 = np.hstack([P, rng.random((800, 1)) * 0.05,
                    rng.random((800, 1)) * 0.05, rng.random((800, 1)) * 0.05])
    measure_cloud(P4, "thin sheet (true D=2) in 4-D embed")

    print("\n=== 2. Human configuration manifolds ===")
    F2 = load_configs("drawing_data.csv")[:, :2]
    F4 = load_configs("drawing_data.csv")
    measure_cloud(F2, "human v2 (203 circles), centroids 2-D")
    measure_cloud(F4, "human v2, full 4-D config")
    F1b = load_configs("drawing_data_v1.csv")
    measure_cloud(F1b[:, :2], "human v1 (142 circles), centroids 2-D")
    measure_cloud(F1b, "human v1, full 4-D config")

    print("\nCriterion: nu > w = 2  ->  transient -> exact vanishes, rhyme persists")
    print("            nu <= 2     ->  recurrent -> exact repeats persist")
