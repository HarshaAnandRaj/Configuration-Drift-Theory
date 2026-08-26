"""lattice_walk.py
CORRECTED recurrence model for the Configuration-Drift Hypothesis.

The earlier `drift_walker` used an eps-ball ("point reference") recurrence:
"x_t within eps of some previous point". That fails in D >= 4 because the
eps-ball volume ~ eps^D vanishes -- exact/near recurrences read ~0 and the
temporal-decay signature cannot be measured (curse of dimensionality).

The hypothesis is about EXACT recurrences. Those are only well-defined on a
DISCRETE lattice: a return to the *same site*. This script implements a drifted
lattice random walk on Z^D and measures exact site recurrence
(r[t] = 1 iff x_t equals a previously visited lattice site). This works in any
dimension and is the proper setting for the Pólya recurrence/transience
transition and for testing the drift-induced decay.
"""

import numpy as np


def lattice_walk(D, alpha, sigma=1.0, steps=4000, seed=None):
    """Drifted walk rounded to the integer lattice Z^D."""
    rng = np.random.default_rng(seed)
    d = rng.standard_normal(D)
    d /= np.linalg.norm(d)
    X = np.zeros((steps + 1, D))
    for t in range(1, steps + 1):
        X[t] = np.round(X[t - 1] + alpha * d + sigma * rng.standard_normal(D))
    return X.astype(int)


def exact_recurrence(X):
    """r[t] = 1 iff the lattice site x_t was visited before time t."""
    seen = set()
    r = np.zeros(len(X), dtype=bool)
    for t in range(1, len(X)):
        key = tuple(X[t])
        if key in seen:
            r[t] = True
        else:
            seen.add(key)
    return r


def recurrence_rate(X, window=0.5):
    r = exact_recurrence(X)
    n = len(r)
    start = int(n * (1.0 - window))
    return float(r[start:].mean()) if n - start else 0.0


if __name__ == "__main__":
    dims = [1, 2, 3, 4, 5]
    alphas = [0.0, 0.1, 0.3, 0.6]
    TRIALS = 20
    print(f"{'D':>3} {'alpha':>6} {'rho_exact':>10}")
    for D in dims:
        for a in alphas:
            rs = [recurrence_rate(lattice_walk(D, a, 1.0, 4000, 5000 + i * 17 + D))
                  for i in range(TRIALS)]
            print(f"{D:>3} {a:>6.2f} {np.mean(rs):>10.4f}")
        print()
