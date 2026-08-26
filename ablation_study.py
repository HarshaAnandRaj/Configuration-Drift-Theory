"""ablation_study.py
Ablate the LOSS OF EXACT RECURRENCE and watch how the system reacts.

Mechanism under study (emergent_walk.py): a realized configuration becomes
slightly less likely to recur -- weight exp(-gamma * visits). Here we sweep
gamma across THREE regimes:

  gamma > 0   hypothesis regime: realization perturbs -> exact recurrence dies
  gamma = 0   ablation (neutral): no perturbation either way
  gamma < 0   FULL ABLATION of the loss: visited configs ATTRACT -- exact
              recurrence is forced to persist

System-reaction metrics (late half of trajectory):
  exact     return to the SAME site
  rhyme     return within Chebyshev R=2 of an earlier NON-adjacent site
  explore   distinct sites visited (novelty)
  radius    RMS displacement from origin (is the system still going anywhere?)
  entropy   normalized occupancy entropy over visited sites (1 = spread out,
            0 = collapsed onto a few states)
"""

import numpy as np
from collections import defaultdict
from itertools import product


def walk(D, gamma, steps, seed):
    rng = np.random.default_rng(seed)
    X = np.zeros((steps + 1, D), dtype=int)
    visits = defaultdict(int)
    visits[tuple(X[0])] = 1
    offs = np.vstack([np.eye(D), -np.eye(D)])
    for t in range(1, steps + 1):
        cands = X[t - 1] + offs
        v = np.array([visits[tuple(c)] for c in cands], dtype=float)
        logits = -gamma * v
        logits -= logits.max()          # stabilized softmax (safe for gamma<0)
        w = np.exp(logits)
        w /= w.sum()
        k = rng.choice(len(cands), p=w)
        X[t] = cands[k]
        visits[tuple(X[t])] += 1
    return X, visits


def neighborhood(R, D):
    return [np.array(p) for p in product(*([range(-R, R + 1)] * D))]


def metrics(X, visits, R=2, tau=8):
    seen, recent, history = set(), set(), []
    exact = np.zeros(len(X), dtype=bool)
    rhyme = np.zeros(len(X), dtype=bool)
    offs = neighborhood(R, X.shape[1])
    for t in range(1, len(X)):
        key = tuple(X[t])
        if key in seen:
            exact[t] = True
        for o in offs:
            nk = tuple(np.asarray(key) + o)
            if nk in seen and nk not in recent:
                rhyme[t] = True
                break
        seen.add(key)
        recent.add(key)
        history.append(key)
        if len(history) > tau:
            recent.discard(history[0])
            history.pop(0)
    h = len(X) // 2
    late = X[h:]
    distinct = len({tuple(x) for x in late})
    radius = float(np.sqrt((late ** 2).sum(1).mean()))
    v = np.array([c for c in visits.values() if c > 0], dtype=float)
    p = v / v.sum()
    ent = float(-(p * np.log(p)).sum() / np.log(len(v)))
    return (float(exact[h:].mean()), float(rhyme[h:].mean()),
            distinct, radius, ent)


if __name__ == "__main__":
    D, STEPS, TRIALS = 3, 4000, 12
    gammas = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
    print(f"D={D}  steps={STEPS}  trials={TRIALS}")
    print(f"{'gamma':>6} {'regime':<28} {'exact':>7} {'rhyme':>7} "
          f"{'explore':>8} {'radius':>7} {'entropy':>8}")
    for g in gammas:
        if g > 0:
            reg = "hypothesis (perturb)"
        elif g == 0:
            reg = "ABLATION (neutral)"
        else:
            reg = "FULL ABLATION (attract)"
        ex, rh, di, ra, en = [], [], [], [], []
        for i in range(TRIALS):
            X, vis = walk(D, g, STEPS, 9000 + i * 17 + D)
            a, b, c, d, e = metrics(X, vis)
            ex.append(a); rh.append(b); di.append(c); ra.append(d); en.append(e)
        print(f"{g:>6.1f} {reg:<28} {np.mean(ex):>7.3f} {np.mean(rh):>7.3f} "
              f"{np.mean(di):>8.0f} {np.mean(ra):>7.1f} {np.mean(en):>8.3f}")
