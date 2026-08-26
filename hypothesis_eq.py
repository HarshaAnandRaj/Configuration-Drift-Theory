"""hypothesis_eq.py  (rewrite of the original equation-verification script)
Fits the proposed analytic recurrence law to simulated data and reports the
fitted coupling constant. The original session reported lambda = 0.0006, but
that artifact is lost/unverified; this reports a FRESH fit from the rebuild.
"""

import numpy as np
from drift_walker import simulate_walk, recurrence_rate

EPS = 0.5
SIGMA = 1.0
STEPS = 1500
TRIALS = 40
alphas = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]

rhos = []
for a in alphas:
    rs = [recurrence_rate(simulate_walk(2, a, SIGMA, STEPS, 9000 + i * 31 + 2), EPS, 0.5)
          for i in range(TRIALS)]
    rhos.append(float(np.mean(rs)))
rhos = np.array(rhos)

# proposed law:  rho(alpha) = rho0 * exp(-lambda * alpha)
logr = np.log(np.clip(rhos, 1e-6, None))
A = np.vstack([alphas, np.ones_like(alphas)]).T
neg_lam, ln_rho0 = np.linalg.lstsq(A, logr, rcond=None)[0]
lam = -neg_lam
pred = np.exp(ln_rho0) * np.exp(-lam * np.array(alphas))
mae = float(np.mean(np.abs(rhos - pred)))

print("Fitted recurrence law:  rho(alpha) = rho0 * exp(-lambda * alpha)")
print(f"  rho0    = {np.exp(ln_rho0):.4f}")
print(f"  lambda  = {lam:.4f}    (original UNVERIFIED report: 0.0006)")
print(f"  fit MAE = {mae:.4f}")
