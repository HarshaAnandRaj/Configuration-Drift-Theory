"""analyze_exact.py
Apply the CORRECTED exact-recurrence method to the human drawing.

The 2-D pixel eps-ball in analyze_drawing.py is a "point reference" and, as
noted, ceases to be meaningful in a 4-D configuration space. Here each drawn
circle (stroke) is mapped to a 4-D configuration vector

    C = (centroid_x, centroid_y, radius, stroke_speed)

each normalized to [0,1] and coarse-binned into B levels. An EXACT recurrence
is a later circle landing in the SAME 4-D bin as an earlier one -- the
lattice-site return, in the human configuration space. We then test whether
the exact-recurrence density decays over the session (early vs late) with a
shuffle null, mirroring lattice_walk.py.
"""

import csv
import numpy as np

CSV = "drawing_data.csv"
B = 5          # levels per dimension -> B^4 = 625 cells
N_PERM = 2000


def load():
    strokes = {}
    with open(CSV, newline="") as f:
        for row in csv.DictReader(f):
            s = int(row["stroke"])
            strokes.setdefault(s, []).append(
                (float(row["x"]), float(row["y"]), float(row["t_seconds"]))
            )
    return strokes


def config_of(pts):
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    ts = np.array([p[2] for p in pts])
    cx, cy = xs.mean(), ys.mean()
    r = np.mean(np.hypot(xs - cx, ys - cy))
    # path length / duration = stroke speed
    dxy = np.hypot(np.diff(xs), np.diff(ys))
    dur = ts[-1] - ts[0]
    speed = dxy.sum() / dur if dur > 0 else 0.0
    return np.array([cx, cy, r, speed])


def to_bins(C, B):
    C = (C - C.min(0)) / (C.max(0) - C.min(0) + 1e-12)
    return tuple(np.minimum((C * B).astype(int), B - 1))


def exact_rate(bin_seq):
    seen = set()
    r = np.zeros(len(bin_seq), dtype=bool)
    for i, b in enumerate(bin_seq):
        if b in seen:
            r[i] = True
        else:
            seen.add(b)
    return r


def stat(bin_seq):
    r = exact_rate(bin_seq)
    n = len(r)
    half = n // 2
    return r[half:].mean() - r[:half].mean()


def main():
    import sys
    Bs = [int(x) for x in sys.argv[1:]] or [B]
    strokes = load()
    order = sorted(strokes)
    Cf = np.array([config_of(strokes[s]) for s in order], dtype=float)
    print(f"circles analysed : {len(order)}")
    print(f"4-D config       : (centroid_x, centroid_y, radius, stroke_speed)")
    print(f"{'B':>3} {'cells':>7} {'%exact':>8} {'early':>7} {'late':>7} "
          f"{'T':>7} {'p':>6}  verdict")
    for Bv in Bs:
        bins = [to_bins(Cf[i], Bv) for i in range(len(Cf))]
        r = exact_rate(bins)
        early, late = r[:len(r)//2].mean(), r[len(r)//2:].mean()
        T = late - early
        rng = np.random.default_rng(7)
        Ts = np.empty(N_PERM)
        for k in range(N_PERM):
            idx = rng.permutation(len(bins))
            Ts[k] = stat([bins[i] for i in idx])
        p = np.mean(np.abs(Ts) >= abs(T))
        verdict = "SUPPORTED" if p < 0.05 else "n.s."
        print(f"{Bv:>3} {Bv**4:>7} {100*r.mean():>7.1f}% {early:>7.3f} "
              f"{late:>7.3f} {T:>+7.3f} {p:>6.3f}  {verdict}")


if __name__ == "__main__":
    main()
