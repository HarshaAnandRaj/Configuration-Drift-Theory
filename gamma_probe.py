"""gamma_probe.py -- model-calibrated historical-recurrence diagnostic.

This score is not an estimator of a universal microscopic gamma and the 0.4
threshold is not transferable without recalibration. Step shuffling changes more
than memory in many processes. See configuration_drift_theorem.md, Sections 5,
8, and 12, before using this exploratory diagnostic.

Replaces raw mp-floor checks (e.g. "mp > 0.125"), which are trivially passed in
high-dimensional raw spaces where any two points are far apart. This operator is
scale-free and significance-tested:

  gamma_hat = 1 - rho_obs(eps) / rho_null(eps)

where rho_obs(eps) = fraction of temporally-DISTANT pairs (|i-j| > tau) with
||X_i - X_j|| < eps, eps = low quantile of the pairwise distance distribution
(scale-free, no raw floor), and rho_null(eps) = the same rate under K random
time-permutations (same point cloud, temporal recurrence structure destroyed).

  gamma_hat > 0.4 AND CI excludes 0 -> repulsion suppresses exact recurrence
                                    below chance: INNER WALL HOLDS (alive)
  gamma_hat <= 0.4               -> neutral or lock-in: wall NOT held (dead)
  gamma_hat < 0                  -> exact recurrence ABOVE chance: lock-in /
                                    attraction (gamma <= 0, dead)

Neutral deadband (est > 0.4 required): memoryless walks read gamma_hat ~ +0.2
(BM +0.20, emergent-0 +0.26, SPX +0.28) from surrogate mismatch, while true
repulsion reads +0.75. Without the deadband, neutral recurrent walks (Polya
exact recurrence = case-2 death) misread as alive. Calibrated in system_audit.py.

Rhyme is checked separately at a coarse quantile R: rho_obs(R) must stay
substantial (rhyme persists while exact vanishes -- Sec 5.8 case 3).

Run:  python gamma_probe.py   (demo on emergent_walk gamma = +0.8 / 0 / -0.8)
"""
import numpy as np

from emergent_walk import emergent_walk


def _capped_walk(D, gamma, steps=4000, seed=0, cap=30):
    """Demo-only mirror of emergent_walk with capped visits (avoids exp overflow
    for gamma < 0). Same dynamics as cdt_limits.attractive_walk; canonical
    emergent_walk.py is left untouched."""
    rng = np.random.default_rng(seed)
    X = np.zeros((steps + 1, D), dtype=int)
    visits = {}
    offsets = np.vstack([np.eye(D), -np.eye(D)])
    for t in range(1, steps + 1):
        base = X[t - 1]
        cands = base + offsets
        w = np.array([np.exp(-gamma * min(visits.get(tuple(c), 0), cap))
                      for c in cands])
        w /= w.sum()
        X[t] = cands[rng.choice(len(cands), p=w)]
        visits[tuple(X[t])] = visits.get(tuple(X[t]), 0) + 1
    return X


def _distant_rate(Y, eps, tau):
    """Fraction of temporally-distant pairs (|i-j| > tau) within eps."""
    m = len(Y)
    iu, ju = np.triu_indices(m, 1)
    mask = (ju - iu) > tau
    if mask.sum() == 0:
        return 0.0
    cnt = 0
    tot = 0
    for s in range(0, m, 400):
        b = Y[s:s + 400]
        D = np.linalg.norm(b[:, None, :] - Y[None, :, :], axis=2)
        for r in range(len(b)):
            i = s + r
            js = np.arange(i + 1, m)
            keep = (js - i) > tau
            if keep.sum():
                cnt += np.sum(D[r, js[keep]] < eps)
                tot += keep.sum()
    return cnt / tot if tot else 0.0


def _pairwise_quantiles(Y, qs):
    m = len(Y)
    vals = []
    for s in range(0, m, 400):
        b = Y[s:s + 400]
        D = np.linalg.norm(b[:, None, :] - Y[None, :, :], axis=2)
        iu, ju = np.triu_indices(m, 1)
        sel = (iu >= s) & (iu < s + len(b))
        vals.append(D[iu[sel] - s, ju[sel]])
    return np.quantile(np.concatenate(vals), qs)


def _surrogate_rate(inc, x0, eps, tau, rng):
    """Step-shuffled surrogate: same steps, no memory (correct no-recurrence null)."""
    perm = rng.permutation(len(inc))
    Y = np.vstack([x0, x0 + np.cumsum(inc[perm], axis=0)])
    return _distant_rate(Y, eps, tau)


def gamma_hat(X, tau=8, q_eps=0.01, q_R=0.10, M=1000, K=15, B=25,
              nblocks=10, seed=0):
    rng = np.random.default_rng(seed)
    X = np.asarray(X, dtype=float)
    N = len(X)
    idx = np.linspace(0, N - 1, min(M, N)).astype(int)
    Y = X[idx]
    eps, R = _pairwise_quantiles(Y, [q_eps, q_R])
    eps, R = float(eps), float(R)
    if eps <= 0:
        return dict(est=-1.0, lo=-1.0, hi=-1.0, rho_obs=1.0, rho_null=1.0,
                    rhyme=1.0, note="degenerate cloud (lock-in)")
    rho_obs = _distant_rate(Y, eps, tau)
    rhyme = _distant_rate(Y, R, tau)
    inc = Y[1:] - Y[:-1]
    nulls = np.array([_surrogate_rate(inc, Y[0], eps, tau, rng) for _ in range(K)])
    rho_null = float(np.mean(nulls))
    if rho_null <= 0:
        return dict(est=-1.0, lo=-1.0, hi=-1.0, rho_obs=rho_obs,
                    rho_null=rho_null, rhyme=rhyme, note="null has no pairs")
    est = 1.0 - rho_obs / rho_null
    # segment-based CI: gamma_hat per contiguous segment (global eps), SE across
    # segments. No resampling-with-replacement (that would manufacture duplicates).
    edges = np.linspace(0, len(Y), nblocks + 1).astype(int)
    segs = []
    for b in range(nblocks):
        Yb = Y[edges[b]:edges[b + 1]]
        if len(Yb) < tau + 2:
            continue
        rb = _distant_rate(Yb, eps, tau)
        ib = Yb[1:] - Yb[:-1]
        nb = float(np.mean([_surrogate_rate(ib, Yb[0], eps, tau, rng)
                            for _ in range(10)]))
        if nb > 0:
            segs.append(1.0 - rb / nb)
    if len(segs) >= 5:
        se = float(np.std(segs, ddof=1) / np.sqrt(len(segs)))
        lo, hi = est - 1.96 * se, est + 1.96 * se
        note = "ok"
    else:
        lo, hi, note = est, est, "CI unavailable (too few informative segments)"
    return dict(est=est, lo=lo, hi=hi, rho_obs=rho_obs, rho_null=rho_null,
                rhyme=rhyme, note=note)


if __name__ == "__main__":
    print("=== gamma_probe calibration (D=2 walks, 4000 steps) ===")
    print("expect: gamma=+0.8 -> hat>0 | 0 -> ~0 | -0.8 -> <0\n")
    cases = [("emergent", 0.8), ("emergent", 0.0), ("attractive", -0.8)]
    for kind, g in cases:
        if kind == "emergent":
            X = emergent_walk(2, g, 4000, seed=7000 + int(g * 10))
        else:
            X = _capped_walk(2, g, 4000, seed=7011)
        r = gamma_hat(X)
        verdict = "HOLDS (alive)" if (r["est"] > 0.4 and r["lo"] > 0) else \
            ("VIOLATED (dead)" if r["hi"] < 0 else "neutral/dead")
        print(f"  gamma={g:+.1f}: hat={r['est']:+.3f}  CI=[{r['lo']:+.3f},{r['hi']:+.3f}]  "
              f"rhyme={r['rhyme']:.3f}  -> {verdict}")
