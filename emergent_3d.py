"""emergent_3d.py  (rewrite)
Shows the recurrence phase transition on a 3-D TORUS substrate, demonstrating
the transition is substrate-independent (not an artefact of an unbounded walk).
Periodic boundaries => finite volume, so any persistent recurrence must come
from the dynamics, not from filling space.
"""

import numpy as np
from drift_walker import recurrence_rate

L = 20.0
EPS = 0.5
SIGMA = 0.6
STEPS = 1500
TRIALS = 30


def torus_walk(alpha, seed):
    rng = np.random.default_rng(seed)
    d = rng.standard_normal(3)
    d /= np.linalg.norm(d)
    X = np.zeros((STEPS + 1, 3))
    for t in range(1, STEPS + 1):
        X[t] = (X[t - 1] + alpha * d + SIGMA * rng.standard_normal(3)) % L
    return X


print("3-D torus substrate: recurrence rate vs drift")
for a in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]:
    r = float(np.mean([recurrence_rate(torus_walk(a, 7000 + i * 17), EPS, 0.5)
                       for i in range(TRIALS)]))
    print(f"  alpha={a:.2f}  rho={r:.4f}")
