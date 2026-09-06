"""CDT test: does the TIMING and AIM of the heartbeat kick matter? (user's insight)

The earlier implementations all kicked REACTIVELY -- only after the trajectory had
already relaxed into the lock-in basin (exact recurrence / period-<=2 detected). The
user's point: WHERE the kick enters the trajectory matters. Sec 5.9.2 asks for a
PREDICTIVE trigger (kick before basin entry, when dist/|flow| < horizon); Sec 5.9.4
asks for AIMED kicks (away from the attracting basin). We test both axes on the
emergent self-repelling walk (gamma=0 -> dead by lock-in).

WHEN (trigger):
  late  : kick only after an exact recurrence (site already seen)  [old behaviour]
  early : kick when the walker is SURROUNDED by seen sites (>=3 of 4 neighbours
          already visited) -- i.e. about to lock in, before the exact step
WHERE (aim), on kick:
  random: teleport to a random fresh site
  away  : teleport to the LEAST-visited fresh site (escape direction, away from basin)

Metrics: aliveFrac (new-site fraction, 2nd half), mean kicks, and max neighbours-
in-seen reached (how DEEP into the basin before rescue -- lower = earlier/better).
Predicted: early+away > late+random.
"""
import numpy as np
from emergent_walk import _neighborhood

D = 2
STEPS = 3000
TRIALS = 12
TELE = 25


def walk(trigger, aim, seed=0):
    rng = np.random.default_rng(seed)
    X = np.zeros((STEPS + 1, D), dtype=int)
    visits = {}
    seen = set()
    offsets = np.vstack([np.eye(D), -np.eye(D)])
    new_count = 0
    n_total = 0
    n_kicks = 0
    max_nbr = 0
    for t in range(1, STEPS + 1):
        base = X[t - 1]
        cands = base + offsets
        w = np.array([1.0 for _ in cands])          # gamma=0: uniform (dead)
        k = rng.choice(len(cands))
        X[t] = cands[k]
        key = tuple(X[t])
        nbr_seen = sum(1 for c in cands if tuple(c) in seen)
        max_nbr = max(max_nbr, nbr_seen)
        do = False
        if trigger == "late":
            if key in seen:
                do = True
        else:  # early: surrounded by seen sites -> about to lock in
            if nbr_seen >= 3:
                do = True
        if do:
            # choose teleport target
            if aim == "random":
                best = base
                for _ in range(20):
                    cand = base + rng.integers(-TELE, TELE + 1, D)
                    if tuple(cand) not in seen:
                        best = cand
                        break
            else:  # away: pick least-visited fresh site among samples
                best = None; bestv = 1e18
                for _ in range(30):
                    cand = base + rng.integers(-TELE, TELE + 1, D)
                    ck = tuple(cand)
                    if ck in seen:
                        continue
                    v = sum(visits.get(tuple(cand + o), 0) for o in _neighborhood(2, D))
                    if v < bestv:
                        bestv = v; best = cand
                if best is None:
                    best = base + rng.integers(-TELE, TELE + 1, D)
            X[t] = best
            key = tuple(X[t])
            n_kicks += 1
        if t > STEPS // 2:
            n_total += 1
            new_count += (1 if key not in seen else 0)
        seen.add(key)
        visits[key] = visits.get(key, 0) + 1
    return new_count / n_total, n_kicks, max_nbr


def summ(trigger, aim):
    af, nk, mx = [], [], []
    for i in range(TRIALS):
        a, n, m = walk(trigger, aim, 9000 + i * 13 + D)
        af.append(a); nk.append(n); mx.append(m)
    return float(np.mean(af)), float(np.mean(nk)), float(np.mean(mx))


if __name__ == "__main__":
    print(f"Emergent walk (gamma=0, dead) -- heartbeat TIMING x AIM (D={D}, {STEPS} steps)")
    print(f"{'trigger':8s} {'aim':8s} | aliveFrac | kicks | maxNbrSeen(lower=better)")
    for trg in ("late", "early"):
        for am in ("random", "away"):
            af, nk, mx = summ(trg, am)
            print(f"{trg:8s} {am:8s} | {af:8.3f}  | {nk:5.0f} | {mx:6.1f}")
    print("\nPrediction: early+away > late+random (kicks earlier, aimed away from basin).")
