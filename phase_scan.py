"""phase_scan.py
Sweep dimension D and drift alpha to map the recurrence phase transition.
Reports the late-window recurrence rate rho_infty (the order parameter) over a
grid, and writes phase_scan.csv for the report.

Recurrent phase:  rho_infty stays high (walk returns to old configs).
Transient phase:  rho_infty -> ~0  (configuration drift carries the walk away;
                 exact/near revisits vanish, only "rhymes" could remain).
"""

import csv
import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 40
SEED0 = 1000

# (D, alpha) grid
dims = [1, 2, 3, 4, 5]
alphas = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]


def mean_rate(D, alpha):
    rates = []
    for i in range(TRIALS):
        X = simulate_walk(D, alpha, sigma=SIGMA, steps=STEPS, seed=SEED0 + i * 100 + D)
        rates.append(recurrence_rate(X, eps=EPS, window=0.5))
    return float(np.mean(rates)), float(np.std(rates))


rows = []
print(f"{'D':>3} {'alpha':>6} {'rho_mean':>9} {'rho_std':>8}")
for D in dims:
    for a in alphas:
        rm, rs = mean_rate(D, a)
        rows.append((D, a, rm, rs))
        print(f"{D:>3} {a:>6.2f} {rm:>9.4f} {rs:>8.4f}")

with open("phase_scan.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["D", "alpha", "rho_mean", "rho_std"])
    for r in rows:
        w.writerow(r)
print("\nwrote phase_scan.csv")
