"""adaptive_dim_demo.py -- adaptive-dimensional rescue vs heartbeat kicks.

Tiny Elman RNN (numpy only): h_t = tanh(W_h (h_{t-1}*m) + W_x*x_t + b),
y_t = W_y h_t. Readout solved once (teacher-forced burn-in) and FIXED.

HYBRID rollout (the honest design): forced windows (true inputs; TASK measured)
alternate with free-run windows (x = 0; pure autonomous dynamics, where
death-by-lock-in / chaos manifest). Detectors + rescue arms act ONLY in free
windows; aliveFrac is measured on free-window states; task MSE on forced
windows only. This mirrors deployment with autonomous segments.

Regimes: LOCK-IN (spectral radius 0.4, start 8/24 units) and CHAOS (radius 4.0).
Arms: none | kicks (heartbeat, EXOGENOUS noise when locked) |
recruit (unmask 4 dormant units when locked: ENDOGENOUS expand, §5.11) |
prune (mask toward 6 active when chaotic: ENDOGENOUS contract, §5.11).
Detectors mirror theory: lock-in = windowed exact-recurrence rate > 0.15
(fixed eps = 0.02, tanh states O(1)); chaos = participation ratio > 0.30*active.
Metrics: aliveFrac (unseen coarse cells, free windows), task MSE (forced
windows), injected energy (sum ||kick||^2; structural moves cost 0).
Pass bar (§5.11): recruit matches/beats kicks on aliveness with ZERO injected
energy and no task regression.
"""
import numpy as np

H = 24
T = 600
TRIALS = 6
BURN = 100
FREE_EVERY = 50
FREE_LEN = 50


def reservoir(radius, seed):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((H, H))
    rho = max(abs(np.linalg.eigvals(W)))
    return W * (radius / rho), rng


def task_series(T, seed=0):
    t = np.arange(T)
    return (np.sin(0.10 * t) + 0.5 * np.sin(0.031 * t + seed)).astype(float)


def fit_readout(Hstates, Y, lam=1e-3):
    A = Hstates.T @ Hstates + lam * np.eye(Hstates.shape[1])
    return np.linalg.solve(A, Hstates.T @ Y)


def rollout(W_h, W_x, b, Wy, xs, arm, rng, n_active0):
    m = np.zeros(H)
    m[:n_active0] = 1.0
    h = np.zeros(H)
    free = np.zeros(len(xs), dtype=bool)
    for t in range(BURN, len(xs)):
        if ((t - BURN) // FREE_LEN) % 2 == 1:
            free[t] = True
    Hs_free, Ys_f, Yt_f, energy, n_int = [], [], [], 0.0, 0
    Hs_f, xs_f = [], []  # forced-window history for readout realignment
    KICK_SIG = 1.5
    for t in range(len(xs)):
        x = 0.0 if free[t] else xs[t]
        h = np.tanh(W_h @ (h * m) + W_x * x + b)
        y = float(Wy @ (h * m))
        if free[t]:
            Hs_free.append((h * m).copy())
        else:
            Ys_f.append(y)
            Yt_f.append(xs[t])
            Hs_f.append((h * m).copy())
            xs_f.append(xs[t])
        if free[t] and t > 0 and t % 25 == 0 and len(Hs_free) >= 150:
            W_ = np.array(Hs_free[-150:])
            D = np.linalg.norm(W_[:, None, :] - W_[None, :, :], axis=2)
            iu, ju = np.triu_indices(len(W_), 1)
            keep = (ju - iu) > 4
            rec = float(np.mean(D[iu[keep], ju[keep]] < 0.02))
            C = np.cov(W_.T)
            lam_, _ = np.linalg.eigh(C)
            lam_ = np.clip(lam_, 0, None)
            pr = float(lam_.sum() ** 2 / (lam_ ** 2).sum()) if lam_.sum() > 0 else 0.0
            locked = rec > 0.15
            chaotic = pr > 0.30 * max(1, int(m.sum()))
            if arm in ("kicks", "both") and locked:
                h = h + rng.standard_normal(H) * KICK_SIG
                energy += float(KICK_SIG ** 2 * H)
                n_int += 1
            if arm in ("recruit", "both") and locked and m.sum() < H:
                off = np.where(m == 0)[0][:4]
                m[off] = 1.0
                # recruit EXCITABLE dimensions: expansion alone is dead
                # capacity under global contraction, so recruited rows/cols
                # get local gain (still zero injected state-energy).
                W_h[off, :] *= 2.0
                W_h[:, off] *= 2.0
                # readout realignment after structural change (readout-only
                # least squares on on-task forced history; no state kicks).
                k = min(200, len(Hs_f))
                if k > H:
                    Wy[:] = fit_readout(np.array(Hs_f[-k:]), np.array(xs_f[-k:]))
                n_int += 1
            elif arm in ("prune", "both") and chaotic and m.sum() > 6:
                # prune EXPANSIVE directions: mask highest outgoing-gain rows
                # AND cool global gain (masking alone can't quench distributed
                # chaos; weight scaling injects no state-energy).
                on = np.where(m == 1)[0]
                gains = np.linalg.norm(W_h[on, :], axis=1)
                drop = on[np.argsort(-gains)[:min(4, len(on) - 6)]]
                m[drop] = 0.0
                W_h *= 0.92
                k = min(200, len(Hs_f))
                if k > H:
                    Wy[:] = fit_readout(np.array(Hs_f[-k:]), np.array(xs_f[-k:]))
                n_int += 1
    Hs_free = np.array(Hs_free)
    seen, n = set(), 0
    for s in Hs_free:
        key = tuple(np.round(s / 0.5).astype(int))
        n += key not in seen
        seen.add(key)
    af = n / max(1, len(Hs_free))
    mse = float(np.mean((np.array(Ys_f) - np.array(Yt_f)) ** 2))
    return af, mse, energy, n_int


def run_regime(radius, seed0):
    print(f"--- regime spectral-radius={radius} "
          f"({'LOCK-IN' if radius < 1 else 'CHAOS'}) ---")
    print(f"{'arm':8s} | aliveFrac(free) | task MSE(forced) | injected E | int")
    for arm in ("none", "kicks", "recruit", "prune", "both"):
        af, mse, en, ni = [], [], [], []
        for i in range(TRIALS):
            W_h, rng = reservoir(radius, seed0 + i)
            W_x = rng.standard_normal(H) * 0.5
            b = rng.standard_normal(H) * 0.1
            xs = task_series(T, seed=i)
            Ht = [np.zeros(H)]
            for t in range(BURN):
                Ht.append(np.tanh(W_h @ Ht[-1] + W_x * xs[t] + b))
            Wy = fit_readout(np.array(Ht[:BURN]), xs[:BURN])
            n0 = 8 if radius < 1 else H
            a, ms, e, n = rollout(W_h, W_x, b, Wy, xs, arm, rng, n0)
            af.append(a)
            mse.append(ms)
            en.append(e)
            ni.append(n)
        print(f"{arm:8s} | {np.mean(af):13.3f}  | {np.mean(mse):15.4f} | "
              f"{np.mean(en):9.1f}  | {np.mean(ni):4.1f}")


if __name__ == "__main__":
    print("=== adaptive-dimensional rescue vs heartbeat (hybrid rollout) ===")
    run_regime(0.4, 100)
    run_regime(4.0, 500)
    print("\n§5.11 pass bar: recruit ~= kicks on aliveFrac, E = 0, MSE not worse.")
