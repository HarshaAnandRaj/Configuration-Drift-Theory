"""CDT test: where does the virtual heartbeat LAW break? (theoretical limits)

The heartbeat sustains a system only while certain conditions hold. We break each
in turn on the emergent self-repelling walk (gamma=0, dead by lock-in) and measure
the collapse of aliveFrac (new-site fraction, 2nd half). Three demonstrated limits:

  L1 REACH   : kick radius TELE too small to escape the visited region.
               Break when visited-region width W(t) > |xi|_max.
  L2 RATE    : refractory gap K between kicks (budget/cost cap). Break when
               recurrence is faster than 1/K (tau_relax < 1/R_max).
  L3 OBSERV  : death-proxy detected only with probability p (blind/degraded
               sensing). Break when p too low (controller misses lock-in).

Each limit, when crossed, drives aliveFrac -> ~0 (law fails). Confirms the formal
breakdown criteria in theory Sec 5.9 / Sec 5.10.
"""
import numpy as np

D = 2
STEPS = 3000
TRIALS = 10
BASE_TELE = 25


def _base_loop(gamma=0.0):
    offsets = np.vstack([np.eye(D), -np.eye(D)])
    return offsets


def walk(limit, param, seed=0):
    rng = np.random.default_rng(seed)
    offsets = _base_loop()
    X = np.zeros((STEPS + 1, D), dtype=int)
    visits = {}
    seen = set()
    new_count = 0
    n_total = 0
    n_kicks = 0
    last_kick = -10**9
    failed = 0
    for t in range(1, STEPS + 1):
        base = X[t - 1]
        cands = base + offsets
        k = rng.choice(len(cands))
        X[t] = cands[k]
        key = tuple(X[t])
        dead = key in seen
        do = False
        if limit == "reach":
            if dead:
                do = True
        elif limit == "rate":
            if dead and (t - last_kick) >= param:   # refractory gap K=param
                do = True
        elif limit == "observ":
            if dead and rng.random() < param:        # detect prob p=param
                do = True
        if do:
            tele = BASE_TELE if limit != "reach" else param
            found = None
            for _ in range(60):
                cand = base + rng.integers(-tele, tele + 1, D)
                if tuple(cand) not in seen:
                    found = cand; break
            if found is None:
                failed += 1
                cand = base + rng.integers(-tele, tele + 1, D)  # lands visited
            X[t] = cand
            key = tuple(X[t])
            last_kick = t
            n_kicks += 1
        if t > STEPS // 2:
            n_total += 1
            new_count += (1 if key not in seen else 0)
        seen.add(key)
        visits[key] = visits.get(key, 0) + 1
    return new_count / n_total, n_kicks, failed


def walk_bounded(G, TELE, seed=0):
    """Bounded GxG grid (non-wrapping). Confined manifold -> capacity limit L5/L1:
    when the grid fills, no fresh site exists within kick reach -> heartbeat fails."""
    rng = np.random.default_rng(seed)
    offsets = _base_loop()
    X = np.zeros((STEPS + 1, D), dtype=int)
    seen = set()
    new_count = 0
    n_total = 0
    n_kicks = 0
    failed = 0
    for t in range(1, STEPS + 1):
        base = X[t - 1]
        cands = base + offsets
        valid = [c for c in cands if 0 <= c[0] < G and 0 <= c[1] < G]
        if valid:
            k = rng.choice(len(valid))
            X[t] = valid[k]
        key = tuple(X[t])
        dead = key in seen
        if dead:
            found = None
            for _ in range(60):
                cand = base + rng.integers(-TELE, TELE + 1, D)
                if 0 <= cand[0] < G and 0 <= cand[1] < G and tuple(cand) not in seen:
                    found = cand; break
            if found is None:
                failed += 1
                # grid full: kick lands anywhere -> no novelty
                cand = np.array([rng.integers(0, G), rng.integers(0, G)])
            X[t] = cand
            key = tuple(X[t])
            n_kicks += 1
        if t > STEPS // 2:
            n_total += 1
            new_count += (1 if key not in seen else 0)
        seen.add(key)
    return new_count / n_total, n_kicks, failed


def scan(limit, params):
    print(f"\n{limit.upper()} limit  (aliveFrac | kicks | failed)  [baseline aliveFrac=1.000]")
    for p in params:
        af, nk, fl = [], [], []
        for i in range(TRIALS):
            if limit == "reachB":
                a, n, f = walk_bounded(G=p, TELE=25, seed=11000 + i * 7 + D)
            else:
                a, n, f = walk(limit, p, 11000 + i * 7 + D)
            af.append(a); nk.append(n); fl.append(f)
        print(f"  param={str(p):>4s} -> aliveFrac={np.mean(af):.3f}  kicks={np.mean(nk):.0f}  failed={np.mean(fl):.1f}")


if __name__ == "__main__":
    print("Virtual heartbeat: theoretical breakdown limits (emergent walk, gamma=0)")
    print("Each limit crossed should collapse aliveFrac toward 0.")
    scan("reach", [2, 4, 8, 15, 25])
    print("  (open lattice: W(t) stays small, so reach only bites when manifold is confined)")
    scan("reachB", [8, 12, 16, 24, 40])
    print("  ^ bounded grid (G): small G fills up -> capacity limit L5/L1 bites")
    scan("rate", [1, 2, 5, 10, 20])
    scan("observ", [1.0, 0.5, 0.2, 0.05, 0.0])
    print("\nL1 break: kick reach < basin/region width (confined space) -> no fresh site.")
    print("L2 break: gap K too large -> death faster than controller -> law fails.")
    print("L3 break: detect p too low -> blind controller misses lock-in -> law fails.")
