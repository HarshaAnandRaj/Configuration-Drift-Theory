"""dimension_test.py
Decide the Configuration-Drift Hypothesis quantitatively.

CORRECTED (see theory Sec 5.5 caveat, Sec 16.1): the old version hardcoded the
explorer walk dimension w = 2 and used a saturation-including band. This version
(i) MEASURES beta from the process trajectory -> d_w = 2/beta (no assumed w),
(ii) uses the bias-reduced nu_local estimator with bootstrap CI, and (iii) gates
every verdict by the fix-2 floor N >= 100*10**(nu/2): below floor the verdict is
UNDECIDABLE, not transient.

Mathematical criterion: recurrent iff nu <= d_w, transient iff nu > d_w.
For static clouds the explorer is taken as Brownian (d_w = 2).

Pipeline:
  1. Validate the estimator on synthetic point clouds of KNOWN dimension.
  2. Measure nu for the human drawing (2-D centroids and full 4-D config),
     for both the fresh run and the v1 backup, with measured d_w.
"""

import csv
import numpy as np

from debias_nu import nu_local_ci, n_floor


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


def msd_beta_traj(P, taus=(1, 2, 3, 4, 6, 8, 12, 16)):
    """MSD exponent beta of a trajectory (stroke-ordered centroids). d_w = 2/beta."""
    P = np.asarray(P, dtype=float)
    n = len(P)
    taus = [t for t in taus if t < max(2, n // 2)]
    ms = []
    for t in taus:
        d = P[t:] - P[:-t]
        ms.append(float(np.mean((d ** 2).sum(1))))
    ms = np.array(ms)
    m = ms > 0
    if m.sum() < 3:
        return float("nan")
    slope, _ = np.polyfit(np.log(np.array(taus)[m]), np.log(ms[m]), 1)
    return float(slope)


def classify(E, label, dw=2.0):
    E = np.asarray(E, dtype=float)
    est, lo, hi = nu_local_ci(E, B=12, seed=11)
    fl = n_floor(hi)
    ok = len(E) >= fl
    v = "recurrent" if est <= dw else "transient"
    tag = v if ok else "UNDECIDABLE (below floor)"
    print(f"{label:<38} n={len(E):<5} nu={est:5.2f} CI=[{lo:5.2f},{hi:5.2f}] "
          f"floor={fl:<5} d_w={dw:4.2f} -> {tag}")
    return est, tag


if __name__ == "__main__":
    rng = np.random.default_rng(0)

    print("=== 1. Estimator validation (known-D synthetic clouds, d_w=2 Brownian explorer) ===")
    for D in [1, 2, 3, 4]:
        P = rng.random((1500, D))
        classify(P, f"uniform cube D={D} (expect {'rec' if D <= 2 else 'trans'})")
    P = rng.random((800, 1))
    P4 = np.hstack([P, rng.random((800, 1)) * 0.05,
                    rng.random((800, 1)) * 0.05, rng.random((800, 1)) * 0.05])
    classify(P4, "thin sheet (true D=2) in 4-D embed (expect rec)")

    print("\n=== 2. Human configuration manifolds (d_w MEASURED from stroke MSD) ===")
    for path, tag in [("drawing_data.csv", "human v2"), ("drawing_data_v1.csv", "human v1")]:
        F = load_configs(path)
        beta = msd_beta_traj(F[:, :2])
        dw = 2.0 / beta if beta and beta > 0 else float("nan")
        print(f"-- {tag}: stroke beta={beta:.2f} -> d_w={dw:.2f}")
        classify(F[:, :2], f"{tag}, centroids 2-D", dw=dw)
        classify(F, f"{tag}, full 4-D config", dw=dw)

    print("\nCriterion: nu <= d_w (measured) -> recurrent; nu > d_w -> transient;")
    print("below fix-2 floor -> UNDECIDABLE (no verdict from insufficient data).")
