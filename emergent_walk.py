"""emergent_walk.py
Simulation of the Configuration-Drift Hypothesis with the EMERGENT mechanism the
author actually describes: "realizing a state perturbs the configuration for the
next state, so the exact same state is improbable to re-realize" -- NOT an
external drift field.

We implement a self-repelling random walk on Z^D: at each step the walker picks a
neighbouring site with probability weighted by exp(-gamma * visits[site]). So a
site that has been realized even once becomes slightly LESS likely to be realized
again. gamma is tiny -> the per-step change is microscopic (the author's "change
of degree is so low"); accumulated over many states it makes exact recurrence
vanish while near/rhyme recurrence persists.

This is the property EMERGING from a local rule, which is what we want to test.

Metrics:
  exact  = return to the SAME site        (the author's "exact state")
  rhymeR = return within Chebyshev radius R of a previous site (perceived/coarse)
"""

import numpy as np
from collections import defaultdict


def emergent_walk(D, gamma, steps=4000, seed=0):
    rng = np.random.default_rng(seed)
    X = np.zeros((steps + 1, D), dtype=int)
    visits = defaultdict(int)
    visits[tuple(X[0])] = 1
    offsets = np.vstack([np.eye(D), -np.eye(D)])  # 2D nearest neighbours
    for t in range(1, steps + 1):
        base = X[t - 1]
        cands = base + offsets
        w = np.array([np.exp(-gamma * visits[tuple(c)]) for c in cands])
        w /= w.sum()
        k = rng.choice(len(cands), p=w)
        X[t] = cands[k]
        visits[tuple(X[t])] += 1
    return X


def _neighborhood(R, D):
    # all integer offsets with Chebyshev norm <= R
    rng = [range(-R, R + 1)] * D
    from itertools import product
    return [np.array(p) for p in product(*rng)]


def recurrence_rates(X, R, tau=8):
    seen = set()
    recent = set()
    history = []
    exact = np.zeros(len(X), dtype=bool)
    rhyme = np.zeros(len(X), dtype=bool)
    offs = _neighborhood(R, X.shape[1])
    for t in range(1, len(X)):
        key = tuple(X[t])
        if key in seen:
            exact[t] = True
        for o in offs:
            nk = tuple(np.asarray(key) + o)
            if nk in seen and nk not in recent:   # exclude adjacency (tau steps)
                rhyme[t] = True
                break
        seen.add(key)
        recent.add(key)
        history.append(key)
        if len(history) > tau:
            recent.discard(history[0])
            history.pop(0)
    h = len(X) // 2
    return float(exact[h:].mean()), float(rhyme[h:].mean())


if __name__ == "__main__":
    dims = [2, 3, 4]
    gammas = [0.0, 0.5, 1.0, 2.0]
    TRIALS = 12
    print(f"{'D':>3} {'gamma':>6} {'exact':>8} {'rhymeR1':>8} {'rhymeR2':>8}")
    for D in dims:
        for g in gammas:
            ex, r1, r2 = [], [], []
            for i in range(TRIALS):
                X = emergent_walk(D, g, 4000, 7000 + i * 13 + D)
                e, a1 = recurrence_rates(X, 1)
                _, a2 = recurrence_rates(X, 2)
                ex.append(e); r1.append(a1); r2.append(a2)
            print(f"{D:>3} {g:>6.2f} {np.mean(ex):>8.4f} {np.mean(r1):>8.4f} {np.mean(r2):>8.4f}")
        print()
