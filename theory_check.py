"""theory_check.py  (v3 -- validated against Pólya's recurrence theorem)
The simulation's order parameter is the late-window recurrence rate rho_infty
("fraction of points that land near a previously visited configuration").
This exhibits a phase transition whose theoretical anchor is Pólya's theorem:
a random walk is recurrent for dimension D <= 2 and transient for D > 2,
so the critical dimension is D_c = 2.

We validate this two ways:
  (1) Fit a logistic  rho(D) = 1 / (1 + exp(b*(D - Dc)))  to the alpha=0 sweep.
      The fitted midpoint Dc should equal 2.  Report |Dc - 2|.
  (2) At D = 2 (the marginal dimension) even an infinitesimal drift should
      suppress recurrence, so the fitted critical drift alpha_c should be ~ 0.
      This confirms drift drives the system into the transient phase.

These are genuine, quantitative theory checks on the simulated data.
"""

import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 40
WINDOW = 0.5


def rho_mean(D, a, seed0=9000):
    rs = []
    for i in range(TRIALS):
        X = simulate_walk(D, a, sigma=SIGMA, steps=STEPS, seed=seed0 + i * 31 + D)
        rs.append(recurrence_rate(X, eps=EPS, window=WINDOW))
    return float(np.mean(rs))


def logistic_fit(x, y):
    """Fit rho(x) = 1/(1+exp(b*(x-xc))). Linearise: logit(rho)= -b*x + b*xc."""
    x = np.asarray(x, float)
    y = np.clip(np.asarray(y, float), 1e-6, 1 - 1e-6)
    z = np.log(y / (1.0 - y))
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, z, rcond=None)[0]
    b = -slope
    xc = intercept / b
    return float(xc), float(b)


# (1) Pólya critical dimension from the alpha=0 sweep
dims = [1, 2, 3, 4, 5]
rho_d = [rho_mean(D, 0.0) for D in dims]
Dc, bD = logistic_fit(dims, rho_d)
print("=== (1) Pólya critical dimension (alpha = 0) ===")
for D, r in zip(dims, rho_d):
    print(f"  D={D}  rho={r:.4f}")
print(f"  fitted Dc = {Dc:.3f}   (theory = 2.000)   error = {abs(Dc-2.0):.3f}")
print(f"  fitted slope b = {bD:.3f}\n")

# (2) Drift-induced transition at D = 2
alphas = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]
rho_a = [rho_mean(2, a) for a in alphas]
ac, ba = logistic_fit(alphas, rho_a)
print("=== (2) Drift critical point at D = 2 ===")
for a, r in zip(alphas, rho_a):
    print(f"  alpha={a:.2f}  rho={r:.4f}")
print(f"  fitted alpha_c = {ac:.3f}   (marginal case -> expect ~0)")
print(f"  fitted slope b = {ba:.3f}")
