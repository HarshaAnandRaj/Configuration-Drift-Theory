"""celestial.py
Configuration-Drift on HEAVENLY BODIES -- the domain Poincare built recurrence
theory for (1890, three-body problem).

Question: is the rhyme TRULY PREDICTABLE?

REGISTERED PREDICTIONS:
  A. REGULAR system (light planets, quasi-periodic, near-resonant periods):
     - exact recurrence: never (incommensurate frequencies)
     - near-recurrences arrive ON SCHEDULE: return intervals concentrate at
       commensurate beat periods (low CV) -> rhyme is PREDICTABLE
     - nu near the KAM-torus dimension ~ 2 (boundary!)
  B. CHAOTIC system (massive close pair):
     - rhymes still occur (bounded phase space) but intervals scatter
       (high CV) -> rhyme exists statistically, schedule does not

Metric: return-interval concentration = fraction of rhyme intervals falling
within +/-5% of the modal interval. Predictable <=> high concentration.
"""

import math
import numpy as np


def simulate(masses, pos0, vel0, T_years=150.0, dt=0.002, rec=20,
             Gc=4 * np.pi ** 2, soft=1e-3):
    n = len(masses)
    m = np.array(masses)
    x = np.array(pos0, dtype=float)
    v = np.array(vel0, dtype=float)

    def accel(p):
        d = p[None, :, :] - p[:, None, :]          # d[i,j] = r_j - r_i
        r2 = (d ** 2).sum(-1) + soft ** 2
        np.fill_diagonal(r2, 1.0)
        inv3 = r2 ** -1.5
        return (Gc * m[None, :, None] * inv3[:, :, None] * d).sum(1)

    def kick(p, v, h):
        v += accel(p) * h

    a = accel(x)
    out = []
    nsteps = int(T_years / dt)
    ejected = False
    for t in range(nsteps):
        kick(x, v, dt / 2)
        x = x + v * dt
        kick(x, v, dt / 2)
        if t % rec == 0:
            out.append(x[1:].ravel().copy())       # planets only, flattened
            if np.abs(x[1:]).max() > 400:
                ejected = True
                break
    return np.array(out), ejected                  # (Trec, 4)


def analyse(traj, eps_frac=0.15, min_gap=50):
    lo = np.percentile(traj, 1, axis=0)
    hi = np.percentile(traj, 99, axis=0)
    Pn = np.clip((traj - lo) / (hi - lo + 1e-12), 0, 1)

    diff = Pn[:, None, :] - Pn[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(len(Pn), k=min_gap)
    dp = d[iu[0], iu[1]]

    qs = np.geomspace(1, 99, 24)
    epsg = np.percentile(dp, qs)
    C = np.array([(dp <= e).mean() for e in epsg])
    mm = (C > 0.02) & (C < 0.90)
    if mm.sum() < 5:
        mm = np.ones(len(C), dtype=bool)
    nu = float(np.polyfit(np.log(epsg[mm]), np.log(C[mm]), 1)[0])

    h = len(Pn) // 2
    ladd = {}
    for B in (8, 16, 32, 64):
        occ = set(map(tuple, (Pn[:h] * B).astype(int)))
        hits = [c in occ for c in map(tuple, (Pn[h:] * B).astype(int))]
        ladd[B] = round(float(np.mean(hits)), 3)

    med = float(np.median(dp))
    eps = med * eps_frac
    T = len(Pn)
    intervals = []
    for t in range(h, T):
        row = d[t, :t - min_gap]
        j = int(row.argmin())
        if row[j] < eps:
            intervals.append(t - j)
    iv = np.array(intervals, dtype=float)
    if len(iv) == 0:
        return {"nu": round(nu, 3), "ladder": ladd,
                "n_rhymes": 0}
    hist, edges = np.histogram(iv, bins=60)
    mode = 0.5 * (edges[int(hist.argmax())] + edges[int(hist.argmax()) + 1])
    band = (iv > mode * 0.95) & (iv < mode * 1.05)
    conc = float(band.mean())
    cv = float(iv.std() / iv.mean()) if iv.mean() > 0 else float("nan")
    return {"nu": round(nu, 3), "ladder": ladd, "n_rhymes": int(len(iv)),
            "modal_interval": round(mode, 1), "concentration": round(conc, 3),
            "cv": round(cv, 3),
            "median_iv": round(float(np.median(iv)), 1)}


if __name__ == "__main__":
    print("=========== REGISTERED PREDICTIONS ===========")
    print("A regular : rhyme intervals CONCENTRATE (predictable), nu~boundary")
    print("B chaotic : rhymes present, intervals SCATTER (no schedule)")
    print()

    # A. light planets, near-2:1 resonance  (a=1 -> P~1yr; a=1.587 -> P~2.0yr)
    print("=== A. REGULAR (near 2:1, negligible masses) ===")
    tr, ej = simulate(
        masses=[1.0, 1e-6, 1e-6],
        pos0=[[0, 0], [1, 0], [1.5874, 0]],
        vel0=[[0, 0], [0, 2 * math.pi], [0, 2 * math.pi / math.sqrt(1.5874)]])
    resA = analyse(tr)
    print("ejected:", ej)
    for k, v in resA.items():
        print(f"  {k}: {v}")

    print("\n=== B. CHAOTIC (massive close pair) ===")
    tr, ej = simulate(
        masses=[1.0, 0.01, 0.01],
        pos0=[[0, 0], [1, 0], [1.25, 0]],
        vel0=[[0, 0], [0, 2 * math.pi], [0, 2 * math.pi / math.sqrt(1.25) * 1.03]])
    resB = analyse(tr)
    print("ejected:", ej)
    for k, v in resB.items():
        print(f"  {k}: {v}")
