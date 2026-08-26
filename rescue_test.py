"""rescue_test.py
Can a system ALREADY locked into the two-point oscillation be rescued?

Protocol: establish the death gait (gamma = -0.5 until step t_switch -- by then
permanently locked per survival.py), THEN change the feedback sign and measure:
  escape_time   steps after switch until the gait is fully broken
                (consecutive x_t == x_{t-2} run falls back to 0)
  relocks       further lock episodes (>= W) before the run ends

Rescue signs tested: stay attracted (control), neutral, weak repulsion,
strong repulsion.
"""

import math
import random


def ring_rescue(S, g_lock, g_rescue, t_switch, steps, seed, W=200):
    rng = random.Random(seed)
    counts = [0] * S
    x = 0
    counts[0] = 1
    xm1 = xm2 = 0
    run = 0
    escaped_at = None
    relocks = 0

    for t in range(1, steps):
        g = g_lock if t < t_switch else g_rescue
        ca = counts[(x - 1) % S]
        cb = counts[(x + 1) % S]
        arg = gamma_clip(g * (cb - ca))
        pb = 0.0 if arg > 50 else 1.0 if arg < -50 else 1.0 / (1.0 + math.exp(arg))
        x = (x + 1) % S if rng.random() < pb else (x - 1) % S
        counts[x] += 1

        if x == xm2:
            run += 1
        else:
            if escaped_at is None and t >= t_switch and run >= W:
                escaped_at = t - t_switch
            if run >= W and t >= t_switch:
                pass
            run = 0
        xm2 = xm1
        xm1 = x
    return escaped_at


def gamma_clip(v):
    return 50.0 if v > 50 else -50.0 if v < -50 else v


def statistics_med(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


if __name__ == "__main__":
    S, STEPS, SWITCH, TRIALS = 32, 8000, 3000, 30
    print(f"ring S={S}: lock with gamma=-0.5 until t={SWITCH}, then rescue")
    print(f"{'rescue gamma':>13} {'escaped':>8} {'median escape':>14} {'max':>6}")
    for gr in [-0.5, 0.0, 0.05, 0.25, 0.75]:
        esc = []
        for i in range(TRIALS):
            e = ring_rescue(S, -0.5, gr, SWITCH, STEPS, 700 + i * 13)
            if e is not None:
                esc.append(e)
        n_esc = len(esc)
        med = int(statistics_med(esc)) if n_esc else -1
        mx = max(esc) if n_esc else -1
        print(f"{gr:>13.2f} {n_esc:>5}/{TRIALS} {med:>14} {mx:>6}")
