"""scale_capacity.py -- finite untrained trajectory response across dimensions.

Untrained Elman reservoirs (spectral radius 0.4, lock-in-prone init, exactly
the training init of alive_reward_demo.py), FREE-RUN probe (x = 0, 300 steps),
aliveFrac with sqrt(H)-scaled cells, 6 seeds. No training: this measures the
response to a declared nonzero initial state. It cannot establish a universal
capacity floor or show that training cannot rescue a particular dimension.
"""
import numpy as np


def probe_alive(H, radius, seed, steps=300, initial_rms=0.1):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((H, H))
    W_h = W * (radius / max(abs(np.linalg.eigvals(W))))
    if not np.isfinite(initial_rms) or initial_rms < 0:
        raise ValueError('initial_rms must be finite and nonnegative')
    h = rng.standard_normal(H)
    h *= initial_rms * np.sqrt(H) / max(np.linalg.norm(h), 1e-30)
    Hs = []
    for _ in range(steps):
        h = np.tanh(W_h @ h)
        Hs.append(h.copy())
    Hs = np.array(Hs)
    cell = 0.5 * np.sqrt(H / 16.0)
    seen, n = set(), 0
    for s in Hs:
        key = tuple(np.round(s / cell).astype(int))
        n += key not in seen
        seen.add(key)
    return n / len(Hs)


if __name__ == "__main__":
    print("=== finite untrained response; initial state RMS=0.1 ===")
    print(f"{'H':>4s} | aliveFrac (radius 0.4) | aliveFrac (radius 1.5)")
    for H in (4, 8, 16, 32, 64):
        a = [probe_alive(H, 0.4, 500 + i) for i in range(6)]
        b = [probe_alive(H, 1.5, 900 + i) for i in range(6)]
        print(f"{H:>4d} | {np.mean(a):20.3f}  | {np.mean(b):21.3f}")
    print("\nFinite cell counts are not a capacity-floor theorem or functional recovery.")
