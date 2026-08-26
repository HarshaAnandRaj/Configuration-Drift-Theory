"""analyze_drawing.py
Analyze a REAL drawing collected by collect_draw.py.

Reads drawing_data.csv (columns: index, x, y, t_seconds), measures the exact-
recurrence density over time (ignoring sub-second adjacency along the pen
path), and runs the same shuffle-null test as shuffle_null.py:

    S = early_rate - late_rate        (recurrence density decay over time)
    p = P( S_null >= S_obs )          over 200 permutations

Usage:
    python analyze_drawing.py [drawing_data.csv] [--eps 8] [--tau 0.3]

Defaults are tuned for hand-drawn circles at ~15 ms sampling: eps=8 px counts
a revisit as "exact", tau=0.3 s excludes within-stroke adjacency. Adjust if
your drawing style differs. The verdict prints and a time-course PNG is saved.
"""

import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from drift_walker import recurrence_events_tgap, recurrence_events

EPS = 8.0
TAU = 0.3
TARGET_N = 900
N_SHUF = 200


def load(path):
    x, y, t, stroke = [], [], [], []
    with open(path) as f:
        rd = csv.DictReader(f)
        has_stroke = "stroke" in (rd.fieldnames or [])
        for row in rd:
            x.append(float(row["x"])); y.append(float(row["y"]))
            t.append(float(row["t_seconds"]))
            if has_stroke:
                stroke.append(int(row["stroke"]))
    if has_stroke and stroke:
        return np.array(x), np.array(y), np.array(t), np.array(stroke)
    return np.array(x), np.array(y), np.array(t), None


def stroke_analysis(X, t, stroke, eps):
    """Per-circle analysis: one configuration = the centroid of each stroke.
    Recurrence is between circle centroids (strokes are separate configs, so no
    tau adjacency exclusion is needed). Returns (n_circles, S_obs, p)."""
    ids = np.unique(stroke)
    cx, cy, ct = [], [], []
    for s in ids:
        m = stroke == s
        cx.append(X[m, 0].mean()); cy.append(X[m, 1].mean()); ct.append(t[m].mean())
    Xc = np.column_stack([cx, cy])
    n = len(Xc)
    r = recurrence_events(Xc, eps)
    e = max(1, n // 3)
    early = r[:e].mean()
    late = r[n - e:].mean()
    obs = early - late
    rng = np.random.default_rng(7)
    order = np.arange(n)
    null = np.empty(N_SHUF)
    for i in range(N_SHUF):
        p = rng.permutation(order)
        rp = recurrence_events(Xc[p], eps)
        null[i] = rp[:e].mean() - rp[n - e:].mean()
    p = float(np.mean(null >= obs))
    return n, float(obs), p


def prepare(x, y, t, stroke=None):
    n = len(x)
    if n > TARGET_N:
        keep = np.linspace(0, n - 1, TARGET_N).astype(int)
        x, y, t = x[keep], y[keep], t[keep]
        if stroke is not None:
            stroke = stroke[keep]
    X = np.column_stack([x, y])
    return X, t, stroke


def rates(X, t, eps, tau):
    r = recurrence_events_tgap(X, eps, t, tau)
    n = len(r)
    e = max(1, n // 3)
    early = r[:e].mean() if e else 0.0
    late = r[n - e:].mean() if e else 0.0
    return float(early), float(late)


def statistic(X, t, eps, tau):
    early, late = rates(X, t, eps, tau)
    return early - late


def p_value(X, t, eps, tau, n_shuf=N_SHUF, seed=2026):
    rng = np.random.default_rng(seed)
    obs = statistic(X, t, eps, tau)
    n = len(X)
    order = np.arange(n)
    null = np.empty(n_shuf)
    for i in range(n_shuf):
        p = rng.permutation(order)
        null[i] = statistic(X[p], t, eps, tau)
    p = float(np.mean(null >= obs))
    return obs, float(null.mean()), p


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "drawing_data.csv"
    eps = EPS
    tau = TAU
    i = 2
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith("--eps"):
            if "=" in a:
                eps = float(a.split("=")[1])
            else:
                i += 1
                eps = float(sys.argv[i])
        elif a.startswith("--tau"):
            if "=" in a:
                tau = float(a.split("=")[1])
            else:
                i += 1
                tau = float(sys.argv[i])
        i += 1

    x, y, t, stroke = load(path)
    X, t, stroke = prepare(x, y, t, stroke)
    print(f"loaded {len(x)} raw points; analyzing {len(X)} configurations "
          f"(eps={eps}, tau={tau})")
    if stroke is not None:
        nc = len(np.unique(stroke))
        print(f"  circles drawn (strokes): {nc}")

    early, late = rates(X, t, eps, tau)
    obs, null_mean, p = p_value(X, t, eps, tau)
    print(f"  [point-level] early_rate = {early:.4f}")
    print(f"  [point-level] late_rate  = {late:.4f}")
    print(f"  [point-level] S_obs = {obs:+.4f}   null_mean = {null_mean:+.4f}")
    print(f"  [point-level] p = {p:.4f}")
    if p < 0.05 and obs > 0:
        print("  [point-level] verdict: SUPPORTED (decay significant)")
    elif p < 0.05 and obs < 0:
        print("  [point-level] verdict: SIGNIFICANT INCREASE (opposite of prediction)")
    else:
        print("  [point-level] verdict: not significant")

    if stroke is not None and len(np.unique(stroke)) > 1:
        n_c, s_c, p_c = stroke_analysis(X, t, stroke, eps)
        print(f"  [circle-level] n_circles={n_c}  S_obs={s_c:+.4f}  p={p_c:.4f}")
        if p_c < 0.05 and s_c > 0:
            print("  [circle-level] verdict: SUPPORTED (decay significant)")
        elif p_c < 0.05 and s_c < 0:
            print("  [circle-level] verdict: SIGNIFICANT INCREASE (opposite of prediction)")
        else:
            print("  [circle-level] verdict: not significant")

    # time-course figure
    r = recurrence_events_tgap(X, eps, t, tau)
    nb = 30
    b = np.array_split(r, nb)
    ts = np.array([v.mean() for v in b])
    xx = np.linspace(1, len(r), len(ts))
    plt.figure(figsize=(7, 4.5))
    plt.plot(xx, ts, marker="o")
    plt.axhline(early, color="green", ls="--", lw=1, label="early")
    plt.axhline(late, color="red", ls="--", lw=1, label="late")
    plt.xlabel("configuration index (time order)")
    plt.ylabel("exact-recurrence density")
    plt.title("Real drawing: exact-recurrence density over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("time_course_real.png", dpi=130)
    plt.close()
    print("saved time_course_real.png")


if __name__ == "__main__":
    main()
