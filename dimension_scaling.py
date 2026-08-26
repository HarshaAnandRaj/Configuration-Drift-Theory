"""dimension_scaling.py  (rewrite)
Scan the effective dimension and locate the critical dimension where
recurrence collapses (the Pólya D_c = 2 transition), confirming the phase is
a property of dimension, not a tuning artefact.
"""

import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 40

print("Recurrence rate vs dimension (alpha = 0):")
for D in [1, 2, 3, 4, 5, 6, 7, 8]:
    r = float(np.mean([recurrence_rate(simulate_walk(D, 0.0, SIGMA, STEPS, 2000 + i * 7 + D), EPS, 0.5)
                       for i in range(TRIALS)]))
    print(f"  D={D}  rho={r:.4f}")
