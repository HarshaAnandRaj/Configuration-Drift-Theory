"""shuffle_null.py  (CORRECTED, v2)
Validates the statistical pipeline that the human experiment actually uses:
a shuffle-null test on CONFIGURATION recurrence.

The real human analysis (analyze_drawing.stroke_analysis) works on circle
CENTROIDS, not raw points, because point-level recurrence is dominated by the
"early points have fewer older references" bias and by pen-path adjacency. So
we validate at the centroid level, where a decay signal is actually detectable.

Synthetic A (decaying): first third of centroids are drawn from a TIGHT cluster
(they rhyme -> recurrent); last third are scattered far away (rare repeats ->
not recurrent). This produces a genuine early->late decay.
Synthetic B (i.i.d.): all centroids scattered widely, no decay.

Statistic:  S = early_rate - late_rate     (S > 0  => recurrence decays)
Null:       shuffle centroid ORDER;  p = P(S_null >= S_obs)
"""

import numpy as np
from drift_walker import recurrence_events

EPS = 8.0
K = 120
N_SHUF = 200


def gen_centroids_drift(seed):
    rng = np.random.default_rng(seed)
    early = rng.standard_normal((K // 2, 2)) * 3.0
    late = np.array([300.0, 0.0]) + rng.standard_normal((K - K // 2, 2)) * 40.0
    return np.vstack([early, late])


def gen_centroids_iid(seed):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((K, 2)) * 40.0


def centroid_stat(C, eps):
    r = recurrence_events(C, eps)
    n = len(r)
    e = max(1, n // 3)
    return float(r[:e].mean()), float(r[n - e:].mean())


def statistic(C, eps):
    early, late = centroid_stat(C, eps)
    return early - late


def p_value(C, eps, n_shuf=N_SHUF, seed=12345):
    rng = np.random.default_rng(seed)
    obs = statistic(C, eps)
    n = len(C)
    order = np.arange(n)
    null = np.empty(n_shuf)
    for i in range(n_shuf):
        p = rng.permutation(order)
        null[i] = statistic(C[p], eps)
    return obs, float(null.mean()), float(np.mean(null >= obs))


C_drift = gen_centroids_drift(7)
obs_d, mean_d, p_d = p_value(C_drift, EPS)
e_d, l_d = centroid_stat(C_drift, EPS)
print("=== Synthetic DECAYING centroids (rhymes early, scattered late) ===")
print(f"  early_rate = {e_d:.3f}   late_rate = {l_d:.3f}   S_obs = {obs_d:+.3f}")
print(f"  null mean S = {mean_d:+.3f}   p-value = {p_d:.4f}")
print(f"  verdict: {'SUPPORTED (decay significant)' if p_d < 0.05 else 'not significant'}")

C_iid = gen_centroids_iid(99)
obs_i, mean_i, p_i = p_value(C_iid, EPS)
e_i, l_i = centroid_stat(C_iid, EPS)
print("\n=== Synthetic i.i.d. centroids (no decay) ===")
print(f"  early_rate = {e_i:.3f}   late_rate = {l_i:.3f}   S_obs = {obs_i:+.3f}")
print(f"  null mean S = {mean_i:+.3f}   p-value = {p_i:.4f}")
print(f"  verdict: {'SUPPORTED' if p_i < 0.05 else 'NOT significant (correct)'}")

np.save("synthetic_drifting.npy", C_drift)
np.save("synthetic_iid.npy", C_iid)
print("\nsaved synthetic_drifting.npy, synthetic_iid.npy")
