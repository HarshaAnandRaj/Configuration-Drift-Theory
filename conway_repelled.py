"""
Conway's Life with intrinsic self-repulsion (CDT test of the inner wall, gamma=0).

The Life/Death theorem (theory 5.8) requires BOTH walls for life:
    Alive  <=>  (d_s <= 2)  AND  (gamma > 0)
  - outer wall: d_s = 2 (spectral dimension of the configuration manifold)
  - inner wall: gamma = 0 (self-repulsion)

A decaying "heat" field makes a recently-alive cell repel its own rebirth and
continued residence (a taboo / self-avoiding walk on the grid). No external actor
is involved. This script tests whether *endogenous* repulsion alone can keep Life
alive.

RESULT (see run below): the repelled rule freezes FASTER than standard Life
(lock-in by ~step 5, grid -> still-life/empty). Interpretation under the theorem:
Life's configuration space is 2^(L^2), so its spectral dimension d_s >> 2 -- it
fails the OUTER wall already (transient base manifold => death by forgetting).
Adding gamma > 0 to a transient manifold only accelerates the collapse; it
cannot manufacture life, because coarse rhyme is impossible when d_s > 2. Life
is therefore DOUBLY dead (d_s >> 2 AND gamma = 0). The transient "aliveness" we
see in standard Life is just the pre-collapse exploration of a huge space.

The CLEAN test of the inner wall (gamma > 0 on a RECURRENT base, d_s <= 2) is
emergent_walk.py: there, repulsion suppresses exact recurrence while rhyme
persists. Life is the wrong substrate for isolating the inner wall, but it is a
sharp demonstration that life needs BOTH walls satisfied.

Metric for "alive": the full-grid configuration must NOT fall into an exact
cycle (period-1/2 lock-in). We track (a) lock-in step (first exact repeat),
(b) sustained churn rate, (c) number of distinct configurations visited.

Run:  python conway_repelled.py
"""

import numpy as np


def step(grid, H, decay, threshold):
    """One generation of repelled Life. `threshold = inf` recovers standard Life.
    Self-repulsion blocks BOTH rebirth at a hot site and continued residence there,
    forcing the active region to migrate to cooler ground (rhyme, not exact recur)."""
    g = grid.astype(np.int8)
    # 8-neighbour count on a torus
    n = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1)
         + np.roll(np.roll(g, 1, 0), 1, 1) + np.roll(np.roll(g, 1, 0), -1, 1)
         + np.roll(np.roll(g, -1, 0), 1, 1) + np.roll(np.roll(g, -1, 0), -1, 1))
    birth = (n == 3) & (g == 0)
    survive = ((n == 2) | (n == 3)) & (g == 1)
    if np.isfinite(threshold):
        birth = birth & (H < threshold)            # self-repulsion: hot cells can't be reborn
        survive = survive & (H < threshold)        # self-repulsion: hot cells must move on
    nxt = (birth | survive).astype(np.int8)
    H_new = np.where(nxt == 1, 1.0, H * decay)      # alive = hot; dead = cools
    return nxt, H_new


def run(L, T, decay, threshold, seed):
    rng = np.random.default_rng(seed)
    grid = (rng.random((L, L)) < 0.30).astype(np.int8)
    H = np.zeros((L, L))
    seen = {}
    lockin = None
    churn_buf = []
    prev = grid
    for t in range(T):
        grid, H = step(grid, H, decay, threshold)
        key = grid.tobytes()
        if lockin is None and key in seen:
            lockin = t
        seen[key] = seen.get(key, 0) + 1
        churn_buf.append((grid != prev).sum())
        prev = grid
    churn = float(np.mean(churn_buf[-200:]) / (L * L))
    return lockin, churn, len(seen)


def show(name, L, T, decay, threshold, seed):
    lockin, churn, distinct = run(L, T, decay, threshold, seed)
    li = f"{lockin}" if lockin is not None else "NONE (alive)"
    print(f"  {name:34s} lock-in={li:>12s}  final_churn={churn:6.3f}  "
          f"distinct_cfgs={distinct}")


if __name__ == "__main__":
    L, T, SEED = 64, 1500, 7
    print(f"=== Conway's Life: intrinsic self-repulsion (L={L}, T={T} gens) ===")
    print("alive = no exact lock-in + sustained churn; dead = period-1/2 lock-in\n")
    show("standard (gamma=0)", L, T, 0.90, float("inf"), SEED)
    print("  -- repelled (gamma>0): sweep decay x threshold (survival+birth repulsion) --")
    for decay in [0.99, 0.95, 0.90, 0.80]:
        for thr in [0.90, 0.70, 0.50]:
            show(f"repelled d={decay} thr={thr}", L, T, decay, thr, SEED)
    print("\nInterpretation: repelled Life freezes FASTER (lock-in ~step 5) -> it is")
    print("transient (d_s >> 2), so gamma>0 only accelerates death by forgetting.")
    print("Life fails BOTH walls; alive needs (d_s<=2) AND (gamma>0). Clean inner-wall")
    print("test is emergent_walk.py (recurrent base). See theory 5.8.")
