"""drift_walker.py
Core simulation for the Configuration-Drift Hypothesis.

We model the exploration of an abstract "configuration space" as a drifted
random walk in D dimensions:

    x_0 = 0
    x_t = x_{t-1} + alpha * d + sigma * eta_t ,   eta_t ~ N(0, I_D)

where d is a fixed unit drift direction. The drift alpha is the "configuration
drift" -- a systematic tendency to move into new configurations rather than
return to old ones.

The hypothesis: exact/near recurrence (returning within `eps` of a previously
visited point) shows a *phase transition*. In low effective dimension with
small drift the walk is RECURRENT (recurrence density stays non-zero); above a
critical drift / dimension it becomes TRANSIENT (recurrence density decays to
zero). This is the Pólya recurrence/transience transition of random walks,
driven here by the drift parameter -- the formal substrate of the
"exact revisits vanish, only rhymes persist" observation from the drawing
experiment.
"""

import numpy as np


def simulate_walk(D, alpha, sigma=1.0, steps=2000, seed=None):
    """Return the trajectory X of shape (steps+1, D)."""
    rng = np.random.default_rng(seed)
    d = rng.standard_normal(D)
    d /= np.linalg.norm(d)
    X = np.empty((steps + 1, D))
    X[0] = 0.0
    for t in range(1, steps + 1):
        X[t] = X[t - 1] + alpha * d + sigma * rng.standard_normal(D)
    return X


def recurrence_events(X, eps):
    """Boolean array r[t]; r[t]=True if x_t lies within `eps` of any x_s, s<t.

    Brute force O(N^2 D); fine for N up to a few thousand points.
    """
    n = X.shape[0]
    r = np.zeros(n, dtype=bool)
    # cumulative squared-norm of points for speed
    for t in range(1, n):
        diff = X[:t] - X[t]
        dist2 = np.einsum('ij,ij->i', diff, diff)
        if np.min(dist2) < eps * eps:
            r[t] = True
    return r


def recurrence_rate(X, eps, window=0.5):
    """Late-window recurrence rate: fraction of points in the last `window`
    fraction of the trajectory that are near-recurrent. Serves as the
    steady-state order parameter rho_infty."""
    r = recurrence_events(X, eps)
    n = len(r)
    start = int(n * (1.0 - window))
    if n - start == 0:
        return 0.0
    return float(r[start:].mean())


def recurrence_events_tgap(X, eps, t, tau):
    """Like recurrence_events, but a point x_t only counts as recurrent if it
    lies within `eps` of a PREVIOUS point at least `tau` seconds earlier
    (t_t - t_s > tau). This removes the trivial adjacency along a continuous
    pen path so that only genuine revisits of an earlier configuration count.
    """
    n = X.shape[0]
    r = np.zeros(n, dtype=bool)
    eps2 = eps * eps
    for i in range(1, n):
        ti = t[i]
        mask = t[:i] < ti - tau          # j < i AND gap > tau
        if not mask.any():
            continue
        diff = X[:i][mask] - X[i]
        d2 = np.einsum('ij,ij->i', diff, diff)
        if d2.min() < eps2:
            r[i] = True
    return r


def time_series(X, eps, bin_size=50):
    """Recurrence density as a function of time, binned, for plotting/decay
    analysis."""
    r = recurrence_events(X, eps)
    n = len(r)
    nb = max(1, n // bin_size)
    out = np.empty(nb)
    for b in range(nb):
        seg = r[b * bin_size:(b + 1) * bin_size]
        out[b] = seg.mean() if len(seg) else 0.0
    return out


if __name__ == "__main__":
    for D in [1, 2, 3]:
        X = simulate_walk(D, alpha=0.0, sigma=1.0, steps=1500, seed=D)
        rho = recurrence_rate(X, eps=0.5, window=0.5)
        print(f"D={D} alpha=0.0  rho_infty={rho:.3f}")
    for a in [0.0, 0.1, 0.3, 0.6]:
        X = simulate_walk(2, alpha=a, sigma=1.0, steps=1500, seed=10)
        rho = recurrence_rate(X, eps=0.5, window=0.5)
        print(f"D=2 alpha={a:.1f}  rho_infty={rho:.3f}")
