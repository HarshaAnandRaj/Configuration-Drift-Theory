"""market_nu_forecast.py
Does the nu-meter earn Seat 2? Walk-forward volatility duel:
  target    : forward 5-day realized vol RV5 = sqrt(sum r^2 over next 5 days)
  benchmark : HAR-RV [1, RVd_lag, RVw_lag, RVm_lag]
  contender : HAR + rolling nu of |r|-embedding (trailing 250d)

PRE-REGISTERED RULE: CDT earns Seat 2 only if BOTH assets show
R2_oos > 0 AND Diebold-Mariano p < 0.05 for HAR+nu over HAR.
"""

import json
import numpy as np


def load_binance(p):
    d = json.load(open(p))
    return np.array([float(k[4]) for k in d])


def load_yahoo(p):
    d = json.load(open(p))
    q = d["chart"]["result"][0]["indicators"]["quote"][0]
    return np.array([x for x in q["close"] if x is not None])


def lr(c):
    return np.diff(np.log(c))


def norm_box(P):
    lo = np.percentile(P, 1, axis=0)
    hi = np.percentile(P, 99, axis=0)
    return np.clip((P - lo) / (hi - lo + 1e-12), 0, 1)


def corr_dim(Q):
    diff = Q[:, None, :] - Q[None, :, :]
    dp = np.sqrt((diff ** 2).sum(-1))
    iu = np.triu_indices(len(Q), 1)
    dd = dp[iu[0], iu[1]]
    qs = np.geomspace(1, 99, 14)
    ee = np.percentile(dd, qs)
    C = np.array([(dd <= e).mean() for e in ee])
    m = (C > 0.02) & (C < 0.90)
    if m.sum() < 4:
        return np.nan
    return float(np.polyfit(np.log(ee[m]), np.log(C[m]), 1)[0])


def rolling_nu(a, dim=3, win=250):
    E = np.array([a[i:i + dim] for i in range(len(a) - dim + 1)])
    nu = np.full(len(a), np.nan)
    for t in range(win, len(a)):
        nu[t] = corr_dim(norm_box(E[t - win:t]))
    return nu


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def nw_tstat(X, y, lag=6):
    n, k = X.shape
    b = ols(X, y)
    e = y - X @ b
    XtX_inv = np.linalg.pinv(X.T @ X)
    S = np.zeros((k, k))
    for j in range(lag + 1):
        w = 1 - j / (lag + 1)
        g = (X[j:] * e[j:, None]).sum(0)
        h = (X[:n - j] * e[:n - j, None]).sum(0) if j else g
        if j == 0:
            S += w * np.outer(g, g)
        else:
            S += w * (np.outer(g, h) + np.outer(h, g))
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    return b, b / se


def dm_test(e1, e2, lag=6):
    d = e1 ** 2 - e2 ** 2
    dbar = d.mean()
    dc = d - d.mean()
    T = len(d)
    var = (dc ** 2).sum() / T
    for j in range(1, lag + 1):
        w = 1 - j / (lag + 1)
        cov = (dc[j:] * dc[:-j]).sum() / T
        var += 2 * w * cov
    stat = dbar / math.sqrt(max(var / T, 1e-18))
    from math import erf
    pval = 2 * (1 - 0.5 * (1 + math.erf(abs(stat) / math.sqrt(2))))
    return stat, pval


import math


def duel(r, name):
    a = np.abs(r)
    rv_d = r ** 2
    H = 5
    # predictors at time t use info up to t; target covers t+1..t+H
    T = len(r)
    rv5_lag = np.full(T, np.nan)
    rv22_lag = np.full(T, np.nan)
    for t in range(T):
        if t >= 5:
            rv5_lag[t] = rv_d[t - 5:t].mean()
        if t >= 22:
            rv22_lag[t] = rv_d[t - 22:t].mean()
    tgt = np.full(T, np.nan)
    for t in range(T - H):
        tgt[t] = rv_d[t + 1:t + 1 + H].mean()

    nu = rolling_nu(a)

    cols_y = ["t+1", "t+5", "t+22"]
    rows = []
    for t in range(T):
        ok = not any(np.isnan([rv5_lag[t], rv22_lag[t], nu[t], tgt[t]]))
        rows.append(ok)
    idx = np.where(rows)[0]

    start = idx[0] + max(400, 22)
    Xs, ys = [], []
    for t in idx:
        Xs.append([1.0, rv5_lag[t], rv22_lag[t]])
    X_har_all = np.array(Xs)
    y_all = tgt[idx]
    nu_all = nu[idx]

    # walk-forward
    preds_har, preds_aug, actual = [], [], []
    for i in range(start, len(idx)):
        tr = slice(0, i)
        bh = ols(X_har_all[tr], y_all[tr])
        xa = np.column_stack([X_har_all, nu_all])
        ba = ols(xa[tr], y_all[tr])
        t_i = idx[i]
        preds_har.append(X_har_all[i] @ bh)
        preds_aug.append(xa[i] @ ba)
        actual.append(y_all[i])
    ph, pa, ac = map(np.array, (preds_har, preds_aug, actual))

    mse_h = float(((ph - ac) ** 2).mean())
    mse_a = float(((pa - ac) ** 2).mean())
    r2oos = 1 - mse_a / mse_h
    dm, p = dm_test(ph - ac, pa - ac)

    # full-sample NW t-stat for nu coefficient on augmented regression
    Xa_full = np.column_stack([np.ones(len(idx)), rv5_lag[idx], rv22_lag[idx], nu_all])
    bfull, tstats = nw_tstat(Xa_full, y_all)
    t_nu = tstats[3]

    print(f"{name}: n_oos={len(ac)}")
    print(f"  MSE  HAR={mse_h:.3e}   HAR+nu={mse_a:.3e}")
    print(f"  R2_oos = {r2oos*100:+.2f}%")
    print(f"  DM stat={dm:+.2f}  p={p:.4f}")
    print(f"  full-sample nu coef={bfull[3]:+.4f}  NW t={t_nu:+.2f}")
    verdict = "SEAT EARNED" if (r2oos > 0 and p < 0.05) else "no seat"
    print(f"  => {verdict}\n")
    return r2oos > 0 and p < 0.05


if __name__ == "__main__":
    base = __file__.rsplit("\\", 1)[0] + "\\"
    wins = []
    wins.append(duel(lr(load_binance(base + "BTCUSDT.json")), "BTC (1000d)"))
    wins.append(duel(lr(load_yahoo(base + "spx_yahoo.json")), "S&P (10y)"))
    print("P3 rule: BOTH must earn the seat ->",
          "CDT EARNS SEAT 2" if all(wins) else "CDT = risk philosophy (for now)")
