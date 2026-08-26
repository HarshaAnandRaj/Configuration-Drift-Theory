"""survival.py
Does a SMALL CLOSED system eventually collapse into the two-point oscillation,
or does the emergent rule sustain it forever?

Setup: the minimal closed world -- a ring of S sites, walker steps to a
neighbour with probability weighted by exp(-gamma * visits[site]). Same local
rule as everything else; nothing imposed.

Theory prediction being tested:
  gamma > 0 : a locked pair carries huge counts, so its OUTSIDE neighbours
              look ever more attractive -> the 2-cycle is UNSTABLE ->
              spontaneous lock-in should never become permanent, at any S.
  gamma = 0 : pure diffusion -- wanders, never locks.
  gamma < 0 : attraction makes the 2-cycle STABLE -> rapid permanent lock.

A "lock episode" = >= W consecutive steps with x_t == x_{t-2} (the death gait).
We record whether the run ENDS locked (permanent), first lock time, and the
longest escape from any lock.
"""

import math
import random
import statistics


def ring_run(S, gamma, steps, seed, W=500):
    rng = random.Random(seed)
    counts = [0] * S
    late_counts = [0] * S
    x = 0
    counts[0] = 1
    xm1, xm2 = 0, 0
    run = 0
    max_run = 0
    first_lock = None
    episodes = 0
    t_late_start = int(steps * 0.9)

    for t in range(1, steps):
        ca = counts[(x - 1) % S]
        cb = counts[(x + 1) % S]
        arg = gamma * (cb - ca)
        if arg > 50.0:
            pb = 0.0
        elif arg < -50.0:
            pb = 1.0
        else:
            pb = 1.0 / (1.0 + math.exp(arg))
        x = (x + 1) % S if rng.random() < pb else (x - 1) % S
        counts[x] += 1
        if t >= t_late_start:
            late_counts[x] += 1

        if x == xm2:
            run += 1
            if run == W:
                episodes += 1
                if first_lock is None:
                    first_lock = t
        else:
            run = 0
        if run > max_run:
            max_run = run
        xm2 = xm1
        xm1 = x

    locked_at_end = run >= W
    vv = [c for c in late_counts if c > 0]
    tot = sum(vv)
    eff = sum((c / tot) ** 2 for c in vv)
    eff = 1.0 / eff if eff > 0 else float("inf")
    return {
        "locked": locked_at_end, "first": first_lock, "max_run": max_run,
        "episodes": episodes, "eff_late": eff,
    }


if __name__ == "__main__":
    STEPS = 150_000
    TRIALS = 4
    W = 500
    gammas = [-0.5, -0.2, -0.05, 0.0, 0.05, 0.25, 0.75]
    sizes = [4, 16, 64]

    print(f"ring world, steps={STEPS}, lock window W={W}, trials={TRIALS}")
    print(f"{'gamma':>6} {'S':>4} {'P(end locked)':>14} {'first lock':>11} "
          f"{'longest run':>12} {'eps':>5} {'late eff':>9}  verdict")
    for g in gammas:
        for S in sizes:
            res = [ring_run(S, g, STEPS, 900 + 101 * i + S) for i in range(TRIALS)]
            p_lock = sum(r["locked"] for r in res) / len(res)
            firsts = [r["first"] for r in res if r["first"] is not None]
            f_med = int(statistics.median(firsts)) if firsts else -1
            mx = max(r["max_run"] for r in res)
            eps_tot = sum(r["episodes"] for r in res)
            eff_m = sum(r["eff_late"] for r in res) / len(res)
            if p_lock == 1.0:
                v = "COLLAPSED"
            elif p_lock > 0:
                v = "metastable"
            else:
                v = "SUSTAINED"
            print(f"{g:>6.2f} {S:>4} {p_lock:>14.2f} {f_med:>11} "
                  f"{mx:>12} {eps_tot:>5} {eff_m:>9.1f}  {v}")
        print()
