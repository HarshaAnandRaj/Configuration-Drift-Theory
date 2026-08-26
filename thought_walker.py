"""thought_walker.py  (rewrite)
The original 'thought space' walk: a 12-D configuration space. The original
noted numerical instability; here we show the physical point cleanly -- at
D = 12 the walk is DEEPLY transient (exact-recurrence rate ~ 0), which is the
"curse of dimensionality" that makes exact revisits vanish and only rhyming
configurations can recur.
"""

import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 20

for D in [12]:
    r = float(np.mean([recurrence_rate(simulate_walk(D, 0.0, SIGMA, STEPS, 5000 + i * 13 + D), EPS, 0.5)
                       for i in range(TRIALS)]))
    print(f"D={D} unbiased rho={r:.5f}   (deeply transient -> exact revisits vanish)")
