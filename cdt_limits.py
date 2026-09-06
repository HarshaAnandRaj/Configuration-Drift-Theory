"""CDT test: theoretical LIMITS OF THE HYPOTHESIS ITSELF (not just the heartbeat).

CDT assumes: (i) normal/Brownian diffusion on a fractal so d_s = 2nu/d_w and the Polya
criterion d_s<=2 hold; (ii) an UNBOUNDED configuration space; (iii) a REPULSIVE
realization->next-state perturbation (the inner-wall mechanism). We break each:

  LIMIT-1 NON-BROWNIAN SCALING: Levy-like flights (tail index a).
    A Brownian shortcut assumes d_w=2. For an isotropic a-stable process,
    d_w=a and the correct recurrence threshold is nu <= d_w = a. There is no
    extra factor a*d_w/2; that double-counts anomalous scaling. In 2D, a<2 is
    transient. This violates the Brownian shortcut, not the Green-kernel theorem.
    The capped Pareto simulator below is illustrative rather than an exact
    stable-process sampler.

  LIMIT-2 BOUNDED MANIFOLD: CDT's outer wall (d_s<=2) assumes UNBOUNDED exploration.
    A 3D walk (unbounded: d_s=3>2 => "death by forgetting") on a finite box of side L
    is confined and RECURS regardless of d_s. Show exact-recurrence rises as L shrinks.

  LIMIT-3 ATTRACTIVE DYNAMICS: CDT's inner wall needs REPULSIVE perturbation
    (realizing a state makes it LESS likely). If the law is ATTRACTIVE (gamma<0,
    positive feedback / mode collapse), exact recurrence is amplified -> faster
    lock-in. Show new-site fraction falls as gamma goes negative.

Crossing any assumption collapses CDT's verdict. Empirical anchor for theory Sec 7.
"""
import numpy as np

STEPS = 4000
TRIALS = 8


def levy_walk(a, seed=0, maxR=60.0):
    rng = np.random.default_rng(seed)
    pos = np.zeros(2)
    seen = set()
    ex = 0; ntotal = 0; new = 0
    for t in range(1, STEPS + 1):
        u = rng.random()
        r = min(maxR, u ** (-1.0 / a)) if a > 0 else 1.0
        theta = rng.random() * 2 * np.pi
        pos = pos + r * np.array([np.cos(theta), np.sin(theta)])
        key = tuple(np.round(pos).astype(int))
        is_new = key not in seen
        if t > STEPS // 2:
            ntotal += 1
            ex += (0 if is_new else 1)        # exact recurrence
            new += (1 if is_new else 0)
        seen.add(key)
    return ex / ntotal, new / ntotal


def bounded3d_walk(L, seed=0):
    rng = np.random.default_rng(seed)
    pos = np.array([L / 2, L / 2, L / 2])
    seen = set()
    ex = 0; ntotal = 0
    for t in range(1, STEPS + 1):
        pos = np.clip(pos + rng.integers(-1, 2, 3), 0, L - 1)
        key = tuple(pos.astype(int))
        is_new = key not in seen
        if t > STEPS // 2:
            ntotal += 1
            ex += (0 if is_new else 1)
        seen.add(key)
    return ex / ntotal


def attractive_walk(gamma, seed=0):
    rng = np.random.default_rng(seed)
    X = np.zeros((STEPS + 1, 2), dtype=int)
    visits = {}
    seen = set()
    offsets = np.vstack([np.eye(2), -np.eye(2)])
    new = 0; ntotal = 0
    for t in range(1, STEPS + 1):
        base = X[t - 1]
        cands = base + offsets
        w = np.array([np.exp(-gamma * min(visits.get(tuple(c), 0), 30)) for c in cands])
        w /= w.sum()
        k = rng.choice(len(cands), p=w)
        X[t] = cands[k]
        key = tuple(X[t])
        is_new = key not in seen
        if t > STEPS // 2:
            ntotal += 1
            new += (1 if is_new else 0)
        seen.add(key); visits[key] = visits.get(key, 0) + 1
    return new / ntotal


def scan(fn, params, label, fmt="{:.2f}"):
    print(f"\n{label}")
    for p in params:
        vals = [fn(p, 20000 + i * 11 + int(p * 7)) for i in range(TRIALS)]
        print(f"  {label.split()[0]}={fmt.format(p) if isinstance(p,(int,float)) else p:>6s} -> mean={np.mean(vals):.3f}")


if __name__ == "__main__":
    print("CDT exploratory limits (see configuration_drift_theorem.md for the theorem)")
    scan(lambda a, s: levy_walk(a, s)[0], [2.0, 1.8, 1.5, 1.2, 1.0],
         "LIMIT-1 Levy exact-recurrence (2D); CDT-normal predicts recurrent(~high)")
    scan(lambda a, s: levy_walk(a, s)[1], [2.0, 1.8, 1.5, 1.2, 1.0],
         "LIMIT-1 Levy new-site fraction")
    scan(lambda L, s: bounded3d_walk(int(L), s), [8, 16, 32, 64, 128],
         "LIMIT-2 3D box exact-recurrence; L small=>confined=>recurrent despite d_s=3>2")
    scan(lambda g, s: attractive_walk(g, s), [0.8, 0.0, -0.8, -2.0],
         "LIMIT-3 new-site fraction vs gamma (repulsive +0.8 / attractive -0.8)")
    print("\nThese are finite model demonstrations, not universal theorem tests.")
