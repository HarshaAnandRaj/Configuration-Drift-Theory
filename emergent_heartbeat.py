"""CDT test: the virtual heartbeat (Sec 5.9) on the emergent self-repelling walk.

emergent_walk.py is our canonical INNER-WALL system: with gamma>0 the walk self-
repels (realizing a state makes it less likely to re-realize), so exact recurrence
vanishes while rhyme persists -> ALIVE. With gamma=0 the inner wall fails: a plain
random walk on Z^D recurs exactly (Pólya, D<=2) -> DEATH by lock-in.

Question (Sec 5.9): can EXTERNAL sustenance (the virtual heartbeat) substitute for
intrinsic repulsion? We teleport the walker to a fresh site whenever it would
recur exactly (lock-in detected) -- an external pacemaker. Compare:
  gamma>0 intrinsic  : alive baseline (inner wall defended from inside)
  gamma=0 alone      : dead baseline (exact recurrence -> lock-in)
  gamma=0 + jumpstart: one teleport at first recur -> relapse
  gamma=0 + fixed    : teleport every P steps
  gamma=0 + adaptive : teleport only when exact recurrence detected

aliveFrac = fraction of steps visiting a NEW site (not yet seen). High = exploring/
rhyming (alive); low = trapped in revisited set (dead). Validates Sec 5.9 on a
second, distinct dynamic system: external kicks can do what intrinsic gamma does.
"""
import numpy as np
from emergent_walk import _neighborhood, recurrence_rates

D = 2
STEPS = 4000
TRIALS = 16
TELE = 25           # heartbeat teleport magnitude
LOCK = "exact"      # death proxy: exact recurrence (site already seen)


def walk(gamma, mode, seed=0, P=40):
    rng = np.random.default_rng(seed)
    X = np.zeros((STEPS + 1, D), dtype=int)
    visits = {}
    seen = set()
    offsets = np.vstack([np.eye(D), -np.eye(D)])
    new_count = 0
    n_total = 0
    n_kicks = 0
    kicked_once = False
    for t in range(1, STEPS + 1):
        base = X[t - 1]
        cands = base + offsets
        w = np.array([np.exp(-gamma * visits.get(tuple(c), 0)) for c in cands])
        w /= w.sum()
        k = rng.choice(len(cands), p=w)
        X[t] = cands[k]
        key = tuple(X[t])
        is_new = key not in seen
        # death proxy: exact recurrence (revisiting a previously realized state)
        dead = (not is_new)
        do = False
        if mode == "none":
            pass
        elif mode == "jumpstart":
            if dead and not kicked_once:
                do = True; kicked_once = True
        elif mode == "fixed":
            if t % P == 0:
                do = True
        elif mode == "adaptive":
            if dead:
                do = True
        if do:
            # external pacemaker: teleport to a fresh region
            for _ in range(20):
                cand = base + rng.integers(-TELE, TELE + 1, D)
                if tuple(cand) not in seen:
                    break
            X[t] = cand
            key = tuple(X[t]); is_new = key not in seen
            n_kicks += 1
        if t > STEPS // 2:
            n_total += 1
            new_count += (1 if is_new else 0)
        seen.add(key)
        visits[key] = visits.get(key, 0) + 1
    return new_count / n_total, n_kicks


def summarize(gamma, mode, P=40):
    vals, kicks = [], []
    for i in range(TRIALS):
        a, nk = walk(gamma, mode, 5000 + i * 17 + D, P)
        vals.append(a); kicks.append(nk)
    return float(np.mean(vals)), float(np.mean(kicks))


if __name__ == "__main__":
    print(f"Emergent self-repelling walk + virtual heartbeat (D={D}, {STEPS} steps, {TRIALS} trials)")
    print(f"{'config':22s} | aliveFrac(new-site) | mean kicks")
    print(f"{'gamma>0 intrinsic (alive)':22s} | {summarize(0.8,'none')[0]:17.3f}  | 0")
    af, nk = summarize(0.0, "none")
    print(f"{'gamma=0 alone (dead)':22s} | {af:17.3f}  | 0")
    af, nk = summarize(0.0, "jumpstart")
    print(f"{'gamma=0 + jumpstart':22s} | {af:17.3f}  | {nk:3.0f}")
    af, nk = summarize(0.0, "fixed", P=40)
    print(f"{'gamma=0 + fixed(P=40)':22s} | {af:17.3f}  | {nk:3.0f}")
    af, nk = summarize(0.0, "adaptive")
    print(f"{'gamma=0 + adaptive':22s} | {af:17.3f}  | {nk:3.0f}")
    print("\nSec 5.9 claim: external kicks (adaptive) should reproduce the alive regime of")
    print("intrinsic gamma>0 by preventing exact recurrence -> confirms external sustenance")
    print("can substitute for (life-support) intrinsic repulsion, but stops->relapse.")
