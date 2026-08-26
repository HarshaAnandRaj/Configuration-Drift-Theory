"""market_cdt.py
Configuration-Drift applied to REAL market data (Binance BTC/ETH 1000d,
Yahoo ^GSPC 10y -- all fetched live).

REGISTERED PREDICTIONS:
  P1  SIGNED return trajectories: no recurrence beyond shuffle-null at any
      resolution (direction is transient -- EMH anchor).
  P2  VOLATILITY rhymes persist: |r| autocorrelation >> 0 in both markets,
      stronger in crypto. The market's rhyme lives in magnitude, not direction.
  P3  nu(signed embed) ~ full dimension; nu(|r| embed) < that (clustering
      manifold = fear regimes are a low-dimensional rhyme).
"""

import json
import numpy as np


def load_binance(path):
    d = json.load(open(path))
    closes = np.array([float(k[4]) for k in d])
    return closes


def load_yahoo(path):
    d = json.load(open(path))
    q = d["chart"]["result"][0]["indicators"]["quote"][0]
    c = np.array([x for x in q["close"] if x is not None])
    return c


def logret(c):
    return np.diff(np.log(c))


def embed(r, d=5):
    return np.array([r[i:i + d] for i in range(len(r) - d + 1)])


def norm_box(P):
    lo, hi = np.percentile(P, 1, axis=0), np.percentile(P, 99, axis=0)
    return np.clip((P - lo) / (hi - lo + 1e-12), 0, 1)


def corr_dim(P):
    Q = norm_box(P)
    diff = Q[:, None, :] - Q[None, :, :]
    dp = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(len(Q), 1)
    dp = dp[iu[0], iu[1]]
    qs = np.geomspace(1, 99, 24)
    eps = np.percentile(dp, qs)
    C = np.array([(dp <= e).mean() for e in eps])
    m = (C > 0.02) & (C < 0.90)
    if m.sum() < 5 or dp.max() < 1e-9:
        return float("nan")
    return float(np.polyfit(np.log(eps[m]), np.log(C[m]), 1)[0])


def rho_fine(P, B=16, h_frac=0.5):
    Q = norm_box(P)
    h = int(len(Q) * h_frac)
    occ = set(map(tuple, (Q[:h] * B).astype(int)))
    hits = [c in occ for c in map(tuple, (Q[h:] * B).astype(int))]
    return float(np.mean(hits)) if hits else float("nan")


def shuffle_p(embed_fn, r, n_perm=200, seed=0):
    """p-value that observed fine recurrence EXCEEDS shuffled order."""
    rng = np.random.default_rng(seed)
    obs = rho_fine(embed_fn(r))
    null = []
    for i in range(n_perm):
        rr = r.copy()
        rng.shuffle(rr)
        null.append(rho_fine(embed_fn(rr)))
    null = np.array(null)
    p = float((null >= obs).mean())
    return obs, float(null.mean()), p


def acf_abs(r, lags=(1, 2, 3, 5)):
    a = np.abs(r)
    a = a - a.mean()
    den = float((a ** 2).sum())
    out = {}
    for L in lags:
        num = float((a[L:] * a[:-L]).sum())
        out[L] = round(num / den, 3)
    return out


if __name__ == "__main__":
    print("=========== REGISTERED PREDICTIONS ===========")
    print("P1 signed returns: no recurrence beyond shuffle (both markets)")
    print("P2 |r| autocorrelation >> 0 (volatility rhymes); crypto > equities")
    print("P3 nu signed ~ full dim; nu abs lower (fear manifold)")
    print()

    series = {
        "BTC/USD (1000d)": logret(load_binance(__file__.rsplit("\\", 1)[0] + "\\BTCUSDT.json")),
        "ETH/USD (1000d)": logret(load_binance(__file__.rsplit("\\", 1)[0] + "\\ETHUSDT.json")),
        "S&P 500 (10y)": logret(load_yahoo(__file__.rsplit("\\", 1)[0] + "\\spx_yahoo.json")),
    }

    d_embed = 5
    print(f"embedding dim d={d_embed}")
    for name, r in series.items():
        E_signed = embed(r, d_embed)
        E_abs = embed(np.abs(r), d_embed)
        obs, nm, p = shuffle_p(lambda x: embed(x, d_embed), r)
        ac = acf_abs(r)
        print(f"\n=== {name}  ({len(r)} returns) ===")
        print(f"  P1 signed : rho_fine obs={obs:.3f}  null_mean={nm:.3f}  "
              f"p={p:.3f}  {'RHYME BEYOND CHANCE' if p < 0.05 else 'transient (chance-level)'}")
        print(f"  P2 |r| acf:", ac,
              f"-> {'VOLATILITY RHYMES' if max(ac.values()) > 0.15 else 'weak'}")
        print(f"  P3 nu signed={corr_dim(E_signed):.2f}  "
              f"nu |r|={corr_dim(E_abs):.2f}  (embed dim {d_embed})")
