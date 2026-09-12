"""alive_reward_demo.py -- reward the model for exploring alive dimensional states.

Elman RNN (numpy, manual BPTT + Adam) with LEARNED dimension gates:
  h_t = tanh(W_h (h_{t-1} . g) + W_x x_t + b), g = sigmoid(z), y_t = W_y (h_t . g)
Loss = task-MSE(teacher-forced) - lam * Novelty(FREE-RUN) + mu * mean(g).
Novelty = mean pairwise distance of hidden states on an AUTONOMOUS (x = 0)
branch (differentiable curiosity bonus); mu = sparsity price on open dims.
The bonus sits on the free branch deliberately: novelty on the driven branch
is gameable through input-driven variety (gates shut, stimulus-slave novelty).
The model must EARN its dimensionality with autonomous novelty.

Prediction (two walls): lam = 0 -> lock-in (dead); moderate lam -> alive +
task intact (gates open on useful units); huge lam -> novelty-max chaos, task
collapses (reward hacking THROUGH the outer wall into forgetting). Inverted-U.
Metrics: teacher-forced task MSE, FREE-RUN probe aliveFrac (x = 0, 300 steps),
effective open dims sum(g > 0.5), plus ghat on the probe (imported).
W_h init radius 0.4 (lock-in-prone). lam in {0, 0.01, 0.05, 0.2}, 3 seeds.
"""
import numpy as np
import sys

H, T, EPOCHS, LR = 16, 300, 120, 0.02
MU = 0.001
if "--H" in sys.argv:
    H = int(sys.argv[sys.argv.index("--H") + 1])
if "--mu" in sys.argv:
    MU = float(sys.argv[sys.argv.index("--mu") + 1])


def task_series(T, seed=0):
    t = np.arange(T)
    return (np.sin(0.10 * t) + 0.5 * np.sin(0.031 * t + seed)).astype(float)


def forward(W_h, W_x, b, Wy, z, xs, free=False):
    g = 1.0 / (1.0 + np.exp(-z))
    h = np.zeros(H)
    Hs, PRE, Y = [], [], []
    for t in range(len(xs)):
        x = 0.0 if free else xs[t]
        pre = W_h @ (h * g) + W_x * x + b
        h = np.tanh(pre)
        Hs.append(h.copy())
        PRE.append(pre.copy())
        Y.append(float(Wy @ (h * g)))
    return np.array(Hs), np.array(PRE), np.array(Y), g


def novelty(Hs):
    D = np.linalg.norm(Hs[:, None, :] - Hs[None, :, :], axis=2)
    iu, ju = np.triu_indices(len(Hs), 1)
    return float(D[iu, ju].mean())


def dnovelty(Hs):
    D = np.linalg.norm(Hs[:, None, :] - Hs[None, :, :], axis=2)
    iu, ju = np.triu_indices(len(Hs), 1)
    d = D[iu, ju]
    G = np.zeros_like(D)
    nz = d > 1e-9
    G[iu[nz], ju[nz]] = 1.0 / d[nz]
    G = G + G.T
    V = Hs[:, None, :] - Hs[None, :, :]
    return np.einsum("ij,ijk->ik", G, V) / (len(Hs) * (len(Hs) - 1) / 2) / 2.0 * 2.0


def drhymeshell(Hs, R=0.5, eps=0.05, tau=4):
    """FAILED IDEA, kept as a negative record: shell bonus pays perfectly for
    small periodic cycles (a chant, not a life) and its violent close-range
    repulsion teaches gate-shutdown evasion. Do not use; see capped spread."""
    n = len(Hs)
    D2 = ((Hs[:, None, :] - Hs[None, :, :]) ** 2).sum(-1)
    iu, ju = np.triu_indices(n, 1)
    keep = (ju - iu) > tau
    KR = np.zeros((n, n))
    KE = np.zeros((n, n))
    KR[iu[keep], ju[keep]] = np.exp(-D2[iu[keep], ju[keep]] / (2 * R ** 2))
    KE[iu[keep], ju[keep]] = np.exp(-D2[iu[keep], ju[keep]] / (2 * eps ** 2))
    KR = KR + KR.T
    KE = KE + KE.T
    V = Hs[:, None, :] - Hs[None, :, :]
    W = KE / eps ** 2 - KR / R ** 2  # dS/dh_t = mean_j W[t,j](h_t - h_j)
    return np.einsum("ij,ijk->ik", W, V) / max(1, keep.sum())


def dcapspread(Hs, R=None):
    """Gradient of capped spread: mean min(d_ij, R). Pays for separation only
    up to rhyme range R -- no chaos-direction pay beyond R, no close-range
    violence (unit direction, bounded). Same lag-free convention as raw.
    R scales as sqrt(H/16): pairwise distances grow as sqrt(H)."""
    if R is None:
        R = 1.0 * np.sqrt(H / 16.0)
    n = len(Hs)
    D = np.linalg.norm(Hs[:, None, :] - Hs[None, :, :], axis=2)
    iu, ju = np.triu_indices(n, 1)
    d = D[iu, ju]
    G = np.zeros_like(D)
    nz = (d > 1e-9) & (d < R)
    G[iu[nz], ju[nz]] = 1.0 / d[nz]
    G = G + G.T
    V = Hs[:, None, :] - Hs[None, :, :]
    P = n * (n - 1) / 2
    return np.einsum("ij,ijk->ik", G, V) / P


def train(seed, lam, mode="raw"):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((H, H))
    W_h = W * (0.4 / max(abs(np.linalg.eigvals(W))))
    W_x = rng.standard_normal(H) * 0.5
    b = np.zeros(H)
    Wy = rng.standard_normal(H) * 0.1
    z = np.zeros(H)
    P = {"W_h": W_h, "W_x": W_x, "b": b, "Wy": Wy, "z": z}
    M = {k: np.zeros_like(v) for k, v in P.items()}
    V = {k: np.zeros_like(v) for k, v in P.items()}
    xs = task_series(T, seed=seed)
    b1, b2, eps, step = 0.9, 0.999, 1e-8, 0
    for ep in range(EPOCHS):
        Hs, PRE, Y, g = forward(P["W_h"], P["W_x"], P["b"], P["Wy"], P["z"], xs)
        Hf, _, _, _ = forward(P["W_h"], P["W_x"], P["b"], P["Wy"], P["z"], xs,
                             free=True)
        err = Y - xs
        G = {k: np.zeros_like(v) for k, v in P.items()}
        G["Wy"] = (2.0 / T) * np.einsum("t,th->h", err, Hs * g)
        dh_next = np.zeros(H)
        for t in range(T - 1, -1, -1):
            dy = 2.0 * err[t] / T
            dh = P["Wy"] * dy * g + dh_next
            dpre = dh * (1.0 - Hs[t] ** 2)
            hm = Hs[t - 1] * g if t > 0 else np.zeros(H)
            G["W_h"] += np.outer(dpre, hm)
            G["W_x"] += dpre * xs[t]
            G["b"] += dpre
            dhg = P["W_h"].T @ dpre
            G["z"] += (dy * P["Wy"] * Hs[t] + dhg * (Hs[t - 1] if t > 0 else 0.0)) \
                * g * (1.0 - g)
            dh_next = dhg * g
        # free branch: curiosity bonus only (no task signal here).
        # raw = mean pairwise spread; cap = spread capped at rhyme range R
        # (no chaos-direction pay, no close-range violence); rhyme = FAILED
        # shell idea (kept for the record).
        dB = {"raw": dnovelty(Hf), "cap": dcapspread(Hf),
              "capS": dcapspread(Hf),
              "rhyme": drhymeshell(Hf)}[mode]
        dh_next = np.zeros(H)
        for t in range(T - 1, -1, -1):
            dh = -lam * dB[t] + dh_next
            dpre = dh * (1.0 - Hf[t] ** 2)
            hm = Hf[t - 1] * g if t > 0 else np.zeros(H)
            G["W_h"] += np.outer(dpre, hm)
            G["b"] += dpre  # x = 0: no W_x gradient on this branch
            dhg = P["W_h"].T @ dpre
            G["z"] += (dhg * (Hf[t - 1] if t > 0 else 0.0)) * g * (1.0 - g)
            dh_next = dhg * g
        G["z"] += MU / H * g * (1.0 - g)
        step += 1
        for k in P:
            G[k] = np.clip(G[k], -5, 5)
            M[k] = b1 * M[k] + (1 - b1) * G[k]
            V[k] = b2 * V[k] + (1 - b2) * G[k] ** 2
            P[k] -= LR * (M[k] / (1 - b1 ** step)) / \
                (np.sqrt(V[k] / (1 - b2 ** step)) + eps)
    Hs, _, Y, g = forward(P["W_h"], P["W_x"], P["b"], P["Wy"], P["z"], xs)
    return P, float(np.mean((Y - xs) ** 2)), g


def probe(P, seed):
    rng = np.random.default_rng(seed)
    g = 1.0 / (1.0 + np.exp(-P["z"]))
    h = np.zeros(H)
    Hs = []
    for _ in range(300):
        h = np.tanh(P["W_h"] @ (h * g) + P["b"])
        Hs.append((h * g).copy())
    Hs = np.array(Hs)
    cell = 0.5 * np.sqrt(H / 16.0)  # scale-invariant cells: distances ~ sqrt(H)
    seen, n = set(), 0
    for s in Hs:
        key = tuple(np.round(s / cell).astype(int))
        n += key not in seen
        seen.add(key)
    return n / len(Hs), float((g > 0.5).sum())


if __name__ == "__main__":
    import sys as _sys
    _only = None
    if "--rows" in _sys.argv:
        _only = _sys.argv[_sys.argv.index("--rows") + 1].split(",")
    print(f"=== intrinsic aliveness reward (H={H}) ===")
    print(f"{'(mode,lam)':14s} | task MSE | probe aliveFrac | open dims")
    rows = [("raw", 0.0), ("raw", 0.01), ("cap", 0.01),
            ("cap", 0.05), ("cap", 0.2), ("capS", 0.0)]
    if _only:
        rows = [r for r in rows if f"{r[0]}:{r[1]}" in _only]
    nseeds = int(_sys.argv[_sys.argv.index("--seeds") + 1]) \
        if "--seeds" in _sys.argv else 3
    for mode, lam in rows:
        tag = f"{mode}:{lam}"
        if mode == "capS":  # 1/sqrt(H)-scaled sweet-spot test: lam = 0.01*sqrt(16/H)
            lam = 0.01 * np.sqrt(16.0 / H)
            tag = f"capS(scaled {lam:.4f})"
        ms, af, od = [], [], []
        for s in range(nseeds):
            P, mse, g = train(1000 + s, lam, mode)
            a, o = probe(P, 7)
            ms.append(mse)
            af.append(a)
            od.append(o)
        print(f"({tag:<16s}) | {np.mean(ms):8.4f} | "
              f"{np.mean(af):13.3f}  | {np.mean(od):5.1f}/{H}")
    print("\nPenalty removed (lost to reward; see theory). Shell idea failed "
          "(pays for periodic cycles + teaches evasion; kept as negative "
          "record). Capped spread: pay for separation only up to rhyme range.")
