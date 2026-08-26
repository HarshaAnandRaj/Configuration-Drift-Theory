"""sensitivity.py  (rewrite)
Sensitivity check: delta scales the drift. At delta = 0 there is NO drift, so
recurrence must equal the unbiased baseline -- confirming that drift (not
noise) drives the decay. If delta = 0 still produced a transition, the effect
would be spurious.
"""

import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 30
BASE = float(np.mean([recurrence_rate(simulate_walk(2, 0.0, SIGMA, STEPS, 3000 + i), EPS, 0.5)
                      for i in range(TRIALS)]))
print(f"unbiased baseline rho(D=2, delta=0) = {BASE:.4f}")

for delta in [0.0, 0.25, 0.5, 1.0]:
    a = 0.2 * delta
    r = float(np.mean([recurrence_rate(simulate_walk(2, a, SIGMA, STEPS, 4000 + i), EPS, 0.5)
                       for i in range(TRIALS)]))
    print(f"  delta={delta:.2f}  (alpha={a:.3f})  rho={r:.4f}")
