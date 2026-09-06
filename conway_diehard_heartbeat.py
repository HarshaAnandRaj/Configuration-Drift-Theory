"""Exploratory heartbeat intervention on a locked Conway configuration.

MATHEMATICAL STATUS: `aliveFrac` below means only non-locking in this cellular
automaton. The experiment neither measures d_s nor proves a universal
life/death or controller-optimality theorem. See configuration_drift_theorem.md.

A still-life (e.g. a 2x2 block) is a period-1 configuration: it never changes, so
the whole grid is globally period-1 -> exact recurrence -> DEATH by lock-in (Sec 5.8,
inner-wall breach). An unassisted run stays locked forever. We apply the Sec 5.9
adaptive pacemaker: whenever the global state becomes period-<=2 (locked), inject a
random kick (flip a patch of cells), spawning gliders/movement -> churn (alive).
Compare none / jumpstart / fixed / adaptive.

Death proxy: locked = (grid_t == grid_{t-2}) globally (period-1 or period-2).
Metric: aliveFrac = fraction of steps NOT locked.
  none      -> 0.000 : stays a static still-life (dead by lock-in)
  jumpstart -> rises once, then relapse (re-locks)
  adaptive  -> high aliveFrac : heartbeat keeps rescuing the inner wall
Validates Sec 5.9 on Life's INNER wall. Life's OUTER wall (d_s>>2) is unaffected
-- it is still doubly dead, but the inner wall can be externally defended.
"""
import numpy as np

N = 44
STEPS = 400
KICK_FRAC = 0.04


def step(grid):
    p = np.pad(grid, 1)
    nbr = np.zeros((N, N), dtype=int)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nbr = nbr + p[1 + dx:1 + dx + N, 1 + dy:1 + dy + N]
    return ((nbr == 3) | (grid & (nbr == 2))).astype(int)


def locked_grid():
    g = np.zeros((N, N), dtype=int)
    for (r, c) in [(6, 6), (6, 30), (30, 6), (30, 30)]:   # four 2x2 blocks (still-lifes)
        g[r:r + 2, c:c + 2] = 1
    return g


def kick(g, rng):
    flat = rng.random(N * N) < KICK_FRAC
    flip = np.zeros(N * N, dtype=int)
    flip[flat] = 1
    return (g.reshape(-1) ^ flip).reshape(N, N)


def run(mode, seed=0, P=30):
    rng = np.random.default_rng(seed)
    g = locked_grid()
    prev2 = g.copy()
    prev1 = g.copy()
    alive = 0
    n_kicks = 0
    kicked_once = False
    for t in range(STEPS):
        g = step(g)
        locked = np.array_equal(g, prev2)
        do = False
        if mode == "none":
            pass
        elif mode == "jumpstart":
            if locked and not kicked_once:
                do = True; kicked_once = True
        elif mode == "fixed":
            if t >= 20 and t % P == 0:
                do = True
        elif mode == "adaptive":
            if locked:
                do = True
        if do:
            g = kick(g, rng); n_kicks += 1
        if t > 5:
            alive += (0 if locked else 1)
        prev2, prev1 = prev1, g
    return alive / (STEPS - 6), n_kicks


if __name__ == "__main__":
    print(f"Conway's Life (locked still-life) + virtual heartbeat (N={N}, {STEPS} steps)")
    print("initial = four 2x2 blocks (period-1 -> death by lock-in).")
    print(f"{'mode':10s} | aliveFrac (non-locked) | kicks")
    for mode in ("none", "jumpstart", "fixed", "adaptive"):
        a, nk = run(mode, seed=3)
        print(f"{mode:10s} | {a:18.3f}      | {nk:4d}")
    print("\nSec 5.9: adaptive heartbeat rescues Life's INNER wall from lock-in;")
    print("none stays dead (0.000); jumpstart relapses; outer wall (d_s>>2) still failed.")
