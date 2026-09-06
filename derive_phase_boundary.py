"""Demonstrate the spectral boundary and a trajectory-dimension failure mode.

Theory (Barlow-Bass / Kumagai): a diffusion on a d_f-dimensional fractal with
walk dimension d_w has spectral dimension d_s = 2 d_f / d_w. The process is
recurrent iff d_s <= 2.

When the substrate volume dimension d_f is independently identified and the
required heat-kernel assumptions hold, the criterion becomes:

    recurrent  <=>  d_f <= d_w   <=>   d_f <= 2/beta

The first block deliberately estimates a correlation slope from the visited
trajectory cloud. That quantity need not equal d_f and in this script it
misclassifies BM d=3, BM d=4, and fBm H=0.7. It is a negative control, not a
verification. The second block inserts the known substrate dimension and checks
the analytic criterion on:
  1. Standard Brownian motion in d=1,2,3,4  (d_w = 2, expects recurrent iff d<=2)
  2. Fractional Brownian motion (anomalous) in d=2 with H=0.3 and H=0.7
     - H=0.3 -> subdiffusive,   d_w = 1/H = 3.33 -> d=2 manifold RECURRENT
     - H=0.7 -> superdiffusive, d_w = 1/H = 1.43 -> d=2 manifold TRANSIENT

See configuration_drift_theorem.md Sections 4 and 11.
"""

import numpy as np


def correlation_dimension(traj, eps_list=None, seed=0):
    """Estimate correlation dimension nu from pair-count scaling C(eps) ~ eps^nu."""
    rng = np.random.default_rng(seed)
    n = len(traj)
    # subsample for speed
    if n > 4000:
        idx = rng.choice(n, 4000, replace=False)
        traj = traj[idx]
    # random reference points
    m = min(500, len(traj))
    ref = traj[rng.choice(len(traj), m, replace=False)]
    if eps_list is None:
        # derive eps range from data scale
        scales = np.linalg.norm(traj - traj.mean(0), axis=1)
        lo, hi = np.percentile(scales, [5, 95])
        eps_list = np.logspace(np.log10(max(lo, 1e-3)), np.log10(hi), 12)
    counts = []
    for eps in eps_list:
        # count pairs within eps of each reference (vectorized over refs)
        d = np.linalg.norm(ref[:, None, :] - traj[None, :, :], axis=2)
        c = (d < eps).sum(axis=1).mean()
        counts.append(c)
    counts = np.array(counts)
    # linear fit in log-log, ignore zeros
    mask = counts > 1
    if mask.sum() < 2:
        return np.nan
    nu, _ = np.polyfit(np.log(eps_list[mask]), np.log(counts[mask]), 1)
    return nu


def msd_exponent(traj, max_lag=None):
    """Estimate beta from <|x_t - x_0|^2> ~ t^beta (so d_w = 2/beta)."""
    n = len(traj)
    if max_lag is None:
        max_lag = min(n // 4, 400)
    lags = np.arange(1, max_lag)
    msd = []
    for lag in lags:
        disp = traj[lag:] - traj[:-lag]
        msd.append(np.mean(np.sum(disp**2, axis=1)))
    msd = np.array(msd)
    mask = msd > 0
    beta, _ = np.polyfit(np.log(lags[mask]), np.log(msd[mask]), 1)
    return beta


def simulate_bm(d, steps=20000, seed=0):
    rng = np.random.default_rng(seed)
    inc = rng.normal(0, 1, size=(steps, d))
    return np.cumsum(inc, axis=0)


def simulate_fgn(n, H, seed):
    """Fractional Gaussian noise via Davies-Harte circulant embedding.

    fGn has autocovariance gamma(k) = 0.5*(|k+1|^{2H} - 2|k|^{2H} + |k-1|^{2H}).
    MSD of its cumsum (fBm) scales as t^{2H}  =>  beta = 2H  =>  d_w = 1/H.
    """
    rng = np.random.default_rng(seed)
    g = np.zeros(n)
    for k in range(n):
        g[k] = 0.5 * (abs(k + 1) ** (2 * H) - 2 * abs(k) ** (2 * H) +
                      abs(k - 1) ** (2 * H))
    m = 2 * n
    c = np.zeros(m)
    c[0] = g[0]
    c[1:n] = g[1:n]
    c[n:2 * n - 1] = g[n - 1:0:-1]  # symmetric tail: g[n-1]..g[1]
    eig = np.fft.fft(c).real
    eig = np.maximum(eig, 0.0)
    w = rng.normal(0, 1, m) + 1j * rng.normal(0, 1, m)
    z = np.sqrt(eig) * w / np.sqrt(2.0)
    return np.fft.ifft(z).real[:n]


def simulate_fbm(d, H, steps=6000, seed=0):
    """fBm = cumsum of d independent fGn streams (Davies-Harte, exact)."""
    rng = np.random.default_rng(seed)
    base = 1000 + seed
    out = np.zeros((steps, d))
    for j in range(d):
        fgn = simulate_fgn(steps, H, seed=base + j)
        out[:, j] = np.cumsum(fgn) - np.cumsum(fgn).mean()
    return out


def evaluate(name, traj, expected):
    nu = correlation_dimension(traj)
    beta = msd_exponent(traj)
    d_w = 2.0 / beta if beta > 0 else np.nan
    d_s = 2 * nu / d_w if d_w and beta > 0 else np.nan
    recurrent_pred = (d_s <= 2.0) if not np.isnan(d_s) else None
    print(f"  {name:22s} cloud_nu={nu:5.2f}  beta={beta:4.2f}  d_w={d_w:5.2f}  "
          f"plug-in d_s={d_s:5.2f}  raw_pred={recurrent_pred}  expected={expected}")
    return d_s, recurrent_pred, expected


print("=== NEGATIVE CONTROL: trajectory-cloud nu is not substrate d_f ===")
for d in [1, 2, 3, 4]:
    traj = simulate_bm(d, steps=20000, seed=42 + d)
    evaluate(f"BM d={d}", traj, d <= 2)

print("\n=== NEGATIVE CONTROL: same plug-in on fractional Brownian paths ===")
# H=0.3 -> subdiffusive -> d_w = 1/0.3 = 3.33 -> d=2 RECURRENT
traj = simulate_fbm(2, H=0.3, steps=6000, seed=7)
evaluate("fBm d=2 H=0.3", traj, True)
# H=0.7 -> superdiffusive -> d_w = 1/0.7 = 1.43 -> d=2 TRANSIENT
traj = simulate_fbm(2, H=0.7, steps=6000, seed=9)
evaluate("fBm d=2 H=0.7", traj, False)

print("\n=== VALID MODEL CHECK: use independently known substrate d_f=d ===")
print("This checks the heat-kernel criterion without substituting path-cloud dimension.")
def ground_truth(name, true_nu, beta, expected):
    d_w = 2.0 / beta
    d_s = 2 * true_nu / d_w
    pred = d_s <= 2.0
    print(f"  {name:22s} nu={true_nu}  beta={beta:.2f}  d_w={d_w:.2f}  "
          f"d_s={d_s:.2f}  pred={pred}  expected={expected}")

for d in [1, 2, 3, 4]:
    ground_truth(f"BM d={d} (nu={d})", d, 1.0, d <= 2)
ground_truth("fBm d=2 H=0.3 (nu=2)", 2, 0.62, True)   # subdiffusive
ground_truth("fBm d=2 H=0.7 (nu=2)", 2, 1.35, False)  # superdiffusive

print("\nConditional criterion: recurrent iff d_s <= 2, equivalently d_f <= d_w,")
print("under the two-sided heat-kernel hypotheses in configuration_drift_theorem.md.")
