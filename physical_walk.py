"""physical_walk.py
Configuration-Drift Hypothesis under REAL-WORLD constraints.

Not an abstract lattice rule any more -- a physical walker:

  inertia        velocity persists, forces accelerate (no teleport steps)
  bounds         a finite arena with soft walls (nobody walks forever)
  substrate      a deformable ground: every visit leaves a DENT
  mechanism      dents exert repulsive force on later steps -- the deformed
                 path literally pushes the next footstep aside (the author's
                 own footstep example, made dynamical)
  world memory   dents heal at rate tau_mem -- "subjected to the elements".
                 tau_mem -> infinity : scars never fade (fresh ground always)
                 tau_mem small      : ground resets fast (old spot as good
                                      as new -> expect exact revisits)

Question: to what extent must the world REMEMBER your passage before exact
recurrence dies and only rhyme survives? Is there a critical ground-memory?
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def simulate(tau_mem, L=100.0, N=128, steps=12000, rec=4, dt=0.1,
             damp=0.85, noise=3.0, k_dent=0.6, k_wall=8.0, margin=4.0,
             seed=0):
    rng = np.random.default_rng(seed)
    h = np.zeros((N, N))
    x = np.array([L / 2, L / 2])
    v = np.zeros(2)
    decay = 1.0 if np.isinf(tau_mem) else np.exp(-dt / tau_mem)
    P = []

    for t in range(steps):
        ix = min(max(int(x[0] / L * N), 1), N - 2)
        iy = min(max(int(x[1] / L * N), 1), N - 2)

        fx = k_dent * (h[ix - 1, iy] - h[ix + 1, iy])
        fy = k_dent * (h[ix, iy - 1] - h[ix, iy + 1])

        if x[0] < margin:
            fx += k_wall * (margin - x[0])
        if x[0] > L - margin:
            fx -= k_wall * (x[0] - (L - margin))
        if x[1] < margin:
            fy += k_wall * (margin - x[1])
        if x[1] > L - margin:
            fy -= k_wall * (x[1] - (L - margin))

        fx += noise * rng.standard_normal()
        fy += noise * rng.standard_normal()

        v = damp * v + np.array([fx, fy]) * dt
        spd = np.hypot(*v)
        if spd > 4.0:
            v *= 4.0 / spd
        x = x + v * dt * 10.0

        h[ix, iy] += 1.0
        h *= decay

        if t % rec == 0:
            P.append(x.copy())

    return np.array(P)


def analyse(P):
    n = len(P)
    h = n // 2
    early, late = P[:h], P[h:]

    rhos = []
    for B in (16, 32, 64):
        occ = {}
        for c in (early / 100.0 * B).astype(int):
            occ[tuple(c)] = True
        hits = [occ.get(tuple(c), False)
                for c in (late / 100.0 * B).astype(int)]
        rhos.append(float(np.mean(hits)))

    d2 = ((late[:, None, :] - early[None, :, :]) ** 2).sum(-1)
    nn = float(np.sqrt(d2.min(1)).mean())

    occ = {}
    for c in map(tuple, (late / 100.0 * 32).astype(int)):
        occ[c] = occ.get(c, 0) + 1
    vv = np.array(list(occ.values()), dtype=float)
    ppp = vv / vv.sum()
    eff = float(1.0 / (ppp ** 2).sum())
    rms = float(np.sqrt((late ** 2).sum(1).mean()))
    return rhos[0], rhos[1], rhos[2], nn, eff, rms


if __name__ == "__main__":
    taus = [np.inf, 4000.0, 1000.0, 300.0, 100.0, 30.0]
    TRIALS = 6
    rows = []
    print("real-world constrained walker: does GROUND MEMORY kill exact recurrence?")
    print(f"{'tau_mem':>9} {'rho_B16':>9} {'rho_B32':>9} {'rho_B64':>9} "
          f"{'nn_dist':>9} {'eff_st':>8} {'rms':>8}")
    for tau in taus:
        acc = np.zeros(6)
        for i in range(TRIALS):
            P = simulate(tau, seed=31000 + i * 37)
            acc += np.array(analyse(P))
        m = acc / TRIALS
        label = "inf" if np.isinf(tau) else f"{tau:.0f}"
        rows.append((label, *m))
        print(f"{label:>9} {m[0]:>9.3f} {m[1]:>9.3f} {m[2]:>9.3f} "
              f"{m[3]:>9.2f} {m[4]:>8.1f} {m[5]:>8.1f}")

    acc = np.zeros(6)
    for i in range(TRIALS):
        P = simulate(np.inf, seed=31000 + i * 37, k_dent=0.0)
        acc += np.array(analyse(P))
    m = acc / TRIALS
    rows.append(("no-dent", *m))
    print(f"{'no-dent':>9} {m[0]:>9.3f} {m[1]:>9.3f} {m[2]:>9.3f} "
          f"{m[3]:>9.2f} {m[4]:>8.1f} {m[5]:>8.1f}")

    with open("physical_walk.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tau_mem", "rho_B16", "rho_B32", "rho_B64",
                    "nn_dist_early", "eff_states", "rms"])
        w.writerows(rows)

    labels = [r[0] for r in rows]
    cols = np.array([r[1:] for r in rows])
    xx = np.arange(len(labels))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    ax[0].plot(xx, cols[:, 0], marker="o", label="coarse B=16 (rhyme)")
    ax[0].plot(xx, cols[:, 1], marker=".", label="mid B=32")
    ax[0].plot(xx, cols[:, 2], marker="s", label="fine B=64 (exact)")
    ax[0].set_xticks(xx, labels)
    ax[0].set_xlabel("ground-memory tau_mem (inf = scars never heal)")
    ax[0].set_ylabel("cell-recurrence rate")
    ax[0].legend()
    ax[1].plot(xx, cols[:, 3], marker="d", color="tab:green",
               label="mean nearest-old-footstep distance")
    ax[1].set_xticks(xx, labels)
    ax[1].set_xlabel("ground-memory tau_mem")
    ax[1].set_ylabel("nn distance to early path")
    ax[1].legend()
    fig.suptitle("Physical walker: world memory vs the exact/rhyme split")
    fig.tight_layout()
    fig.savefig("physical_walk.png", dpi=130)
    print("\nwrote physical_walk.csv, physical_walk.png")
