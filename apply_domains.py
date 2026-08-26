"""apply_domains.py
Does the Configuration-Drift phenomenon persist outside our toy walkers?

Three alien substrates, one shared harness (normalized box, cell-occupancy
recurrence ladder, pairwise correlation dimension):

  A. CHAOS      -- Lorenz attractor (physical). Known attractor dim ~2.06.
                   PREDICTION: fine recurrence ~0, coarse high, nu near 2
                   (marginal transient -- right at the Polya boundary).
  B. PROSE      -- this project's own report (symbols). PREDICTION: ladder
                   INVERTS by representation scale: word/bigram states recur
                   heavily (tiny alphabet => low D_eff), sentence states never
                   repeat exactly yet rhyme in feature space.
  C. OPTIMIZATION -- minibatch SGD on linear regression. PREDICTION: pure
                   attraction-signed feedback => trajectory enters the
                   recurrent phase as it converges (fine recurrence rises,
                   effective states shrink).
"""

import math
import re
import numpy as np


def norm_box(P):
    lo = np.percentile(P, 1, axis=0)
    hi = np.percentile(P, 99, axis=0)
    return np.clip((P - lo) / (hi - lo + 1e-12), 0, 1)


def pair_dists(P):
    diff = P[:, None, :] - P[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(len(P), 1)
    return d[iu[0], iu[1]]


def corr_dim(P, min_pts=40):
    P = norm_box(P)
    if len(P) < min_pts:
        return float("nan")
    d = pair_dists(P)
    qs = np.geomspace(1, 99, 24)
    eps = np.percentile(d, qs)
    C = np.array([(d <= e).mean() for e in eps])
    m = (C > 0.02) & (C < 0.90)
    if m.sum() < 5:
        m = np.ones(len(C), dtype=bool)
    sl, _ = np.polyfit(np.log(eps[m]), np.log(C[m]), 1)
    return float(sl)


def rec_ladder(P, Bs=(8, 16, 32, 64)):
    Pn = norm_box(P)
    h = len(Pn) // 2
    out = {}
    for B in Bs:
        occ = set(map(tuple, (Pn[:h] * B).astype(int)))
        hits = [c in occ for c in map(tuple, (Pn[h:] * B).astype(int))]
        out[B] = round(float(np.mean(hits)), 3)
    return out


# ---------------- A. chaos ----------------

def lorenz(T=26000, rec=8, dt=0.004):
    st = np.array([1.0, 1.0, 20.0])

    def f(v):
        x, y, z = v
        return np.array([10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0 / 3.0) * z])

    out = []
    for t in range(T):
        k1 = f(st)
        k2 = f(st + dt / 2 * k1)
        k3 = f(st + dt / 2 * k2)
        k4 = f(st + dt * k3)
        st = st + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if t % rec == 0:
            out.append(st.copy())
    return np.array(out)


# ---------------- B. prose ----------------

def prose(path):
    txt = open(path, encoding="utf-8").read()
    raw = re.split(r"[.!?]+|\n+", txt)
    sents = []
    for s in raw:
        ws = re.findall(r"[a-z']+", s.lower())
        if len(ws) >= 4:
            sents.append(ws)
    feats, seen_sig, dup = [], set(), 0
    for ws in sents:
        feats.append([len(ws), float(np.mean([len(w) for w in ws])),
                      sum(1 for w in ws if w in ("the", "a", "an", "of")),
                      len(set(ws)) / len(ws)])
        sig = tuple(ws)
        if sig in seen_sig:
            dup += 1
        seen_sig.add(sig)
    toks = [w for ws in sents for w in ws]
    uni = [(t,) for t in toks]
    bi = list(zip(toks[:-1], toks[1:]))
    h = len(bi) // 2

    def past_rec(states):
        seen, hits = set(), []
        cut = len(states) // 2
        for i, s in enumerate(states):
            if i >= cut:
                hits.append(s in seen)
            else:
                seen.add(s)
        return round(float(np.mean(hits)), 3)

    return (np.array(feats, dtype=float),
            {"sentences": len(sents),
             "exact_sent_repeat_frac": round(dup / len(sents), 4),
             "unigram_rec": past_rec(uni),
             "bigram_rec": past_rec(bi)})


# ---------------- C. optimization ----------------

def sgd_traj(steps=7000, d=8, n=512, bs=16, lr=0.05, seed=0, decay=False):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    wstar = rng.standard_normal(d) * 3.0
    y = X @ wstar + 0.3 * rng.standard_normal(n)
    w = np.zeros(d)
    traj = []
    for t in range(steps):
        idx = rng.choice(n, bs, replace=False)
        g = X[idx].T @ (X[idx] @ w - y[idx]) / bs
        lr_t = lr * (0.999 ** t) if decay else lr
        w = w - lr_t * g
        if t % 3 == 0:
            traj.append(w.copy())
    return np.array(traj), w, wstar


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True)

    print("=========== REGISTERED PREDICTIONS ===========")
    print("A chaos : nu ~ 2 (marginal), fine->0, coarse high")
    print("B prose : micro RECURRENT, sentences never exact but rhyme")
    print("C optim : fine recurrence RISES over training (attraction)")
    print()

    print("=========== A. LORENZ CHAOS ===========")
    P = lorenz()
    print("points:", len(P))
    print("nu (attractor corr-dim; lit ~2.06):", round(corr_dim(P), 3))
    print("recurrence ladder {B: rho}:", rec_ladder(P))

    print("\n=========== B. ENGLISH PROSE (own report) ===========")
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    F, info = prose(os.path.join(base, "configuration_drift_full_report.md"))
    print(info)
    print("sentence-feature nu:", round(corr_dim(F), 3))
    print("sentence recurrence ladder:", rec_ladder(F))

    print("\n=========== C. SGD OPTIMIZATION ===========")
    Wt, _, _ = sgd_traj()
    h = len(Wt) // 2
    print("points:", len(Wt))
    print("nu early half:", round(corr_dim(Wt[:h]), 3),
          "| nu late half:", round(corr_dim(Wt[h:]), 3))

    print("\n--- C2. ANNEALED noise: attraction alone (theory: lock-in) ---")
    W2, w_f, w_star = sgd_traj(decay=True)
    Pn = norm_box(W2)
    Q = 4
    per = len(Pn) // Q
    print(f"{'quartile':>9} {'med dist to optimum':>20} {'distinct cells B=32':>20}")
    for q in range(Q):
        seg_n = Pn[q * per:(q + 1) * per]
        seg = W2[q * per:(q + 1) * per]
        dc = len(set(map(tuple, (seg_n * 32).astype(int))))
        md = float(np.median(np.linalg.norm(seg - w_star, axis=1)))
        print(f"{q + 1:>9} {md:>20.4f} {dc:>20}")
    fin = float(np.linalg.norm(w_f - w_star))
    print("final |w - w*| =", round(fin, 5))
