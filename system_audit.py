"""system_audit.py -- LEGACY exploratory whole-system heuristic.

This is not the canonical theorem audit. Use configuration_drift_theorem.md and
cdt_empirical_audit.py for new work. In particular, the combined "alive"
classification and gamma-hat threshold below are model-calibrated diagnostics,
not a universal equivalence.

Applies ONE corrected pipeline to every formula-sensitive system and prints
old verdict vs corrected verdict:
  beta  = MSD exponent of the trajectory -> d_w = 2/beta (measured, never assumed)
  alpha = Hill tail index of increments (generalized boundary iff alpha < 2)
  bound = d_w (alpha is diagnostic; multiplying by alpha again is incorrect)
  nu    = nu_local + CI; floor N >= 100*10**(nu/2) at upper bound -> else UNDECIDABLE
  ghat  = gamma_probe inner-wall operator (trajectories only)
  alive <=> (nu <= bound) AND (ghat CI excludes 0 below) AND usable N

Heartbeat/conway rows use aliveFrac (unaffected by the formula change) and are
listed as such without re-running. Slow rows (celestial/Lorenz) cite
recheck_domains.py. Run: python system_audit.py
"""
import os
import numpy as np

from debias_nu import nu_local_ci, n_floor
from gamma_probe import gamma_hat, _capped_walk
from emergent_walk import emergent_walk
from market_cdt import load_binance, load_yahoo, logret
from dimension_test import load_configs, msd_beta_traj

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(0)
ROWS = []


def hill_alpha(x, frac=0.10):
    x = np.sort(np.abs(np.asarray(x, dtype=float)))[::-1]
    k = max(20, int(len(x) * frac))
    tail = x[:k]
    try:
        m = float(np.mean(np.log(tail / tail[-1])))
        return float(1.0 / m) if m > 0 else float("inf")
    except Exception:
        return float("inf")  # degenerate/thin-tailed -> normal boundary


def msd_beta(P, taus=(1, 2, 4, 8, 16, 32, 64)):
    P = np.asarray(P, dtype=float)
    n = len(P)
    taus = [t for t in taus if t < max(2, n // 2)]
    ms = []
    for t in taus:
        d = P[t:] - P[:-t]
        ms.append(float(np.mean((d ** 2).sum(1))))
    ms = np.array(ms)
    m = ms > 0
    if m.sum() < 3:
        return float("nan")
    s, _ = np.polyfit(np.log(np.array(taus)[m]), np.log(ms[m]), 1)
    return float(s)


def audit_traj(X, label, old):
    X = np.asarray(X, dtype=float)
    beta = msd_beta(X)
    dw = 2.0 / beta
    inc = X[1:] - X[:-1]
    alpha = hill_alpha(np.linalg.norm(inc, axis=1))
    bound = dw
    g = gamma_hat(X)
    g_ok = (g["est"] > 0.4 and g["lo"] > 0)  # neutral deadband, see gamma_probe
    if g["note"].startswith("degenerate"):
        ROWS.append((label, old, f"ghat={g['est']:+.2f} (lock-in, cloud collapsed)",
                     "lock-in diagnostic"))
        return
    est, lo, hi = nu_local_ci(X, B=12, seed=11)
    if not np.isfinite(est):
        ROWS.append((label, old, "nu estimator failed (degenerate)", "UNDECIDABLE"))
        return
    fl = n_floor(hi)
    usable = len(X) >= fl
    if not usable:
        new = "UNDECIDABLE"
    else:
        new = "candidate split" if (est <= bound and g_ok) else "no candidate split"
    ROWS.append((label, old,
                 f"b={beta:.2f} dw={dw:.2f} a={alpha:.2f} nu={est:.2f} "
                 f"CI=[{lo:.2f},{hi:.2f}] ghat={g['est']:+.2f} "
                 f"CI=[{g['lo']:+.2f},{g['hi']:+.2f}]", new))


def audit_cloud(P, label, old, dw=2.0):
    P = np.asarray(P, dtype=float)
    est, lo, hi = nu_local_ci(P, B=12, seed=11)
    fl = n_floor(hi)
    usable = len(P) >= fl
    new = ("recurrent" if est <= dw else "transient") if usable else "UNDECIDABLE"
    ROWS.append((label, old,
                 f"nu={est:.2f} CI=[{lo:.2f},{hi:.2f}] floor={fl} N={len(P)}",
                 new))


if __name__ == "__main__":
    print("=== LEGACY EXPLORATORY HEURISTIC (not a theorem audit) ===\n")
    for D in (1, 2, 3, 4):
        audit_cloud(rng.random((1500, D)), f"uniform cube D={D}", "old-band nu")
    X = np.cumsum(rng.standard_normal((4000, 2)), axis=0)
    audit_traj(X, "BM 2D walk", "recurrent")
    for g, lab in ((0.8, "emergent gamma=+0.8"), (0.0, "emergent gamma=0.0")):
        audit_traj(emergent_walk(2, g, 4000, seed=7000 + int(g * 10)), lab,
                   "alive" if g > 0 else "dead")
    audit_traj(_capped_walk(2, -0.8, 4000, seed=7011), "emergent gamma=-0.8",
               "dead")
    for name, path, loader in (("BTC returns", "BTCUSDT.json", load_binance),
                               ("SPX returns", "spx_yahoo.json", load_yahoo)):
        r = logret(loader(os.path.join(HERE, path)))
        r = r[np.isfinite(r)]
        audit_traj(np.vstack([np.cumsum(r), np.zeros_like(r)]).T, name,
                   "transient(P1)/levy inconclusive")
    F = load_configs(os.path.join(HERE, "drawing_data.csv"))
    audit_traj(F[:, :2], "drawing v2 centroids", "recurrent (WITHDRAWN)")
    print(f"{'system':<24} {'prior label':<28} exploratory diagnostics")
    print(f"{'':<24} {'':<28} heuristic output")
    def cls(s):
        s = s.lower()
        if s.startswith("undecidable"):
            return "U"
        if s.startswith("alive") or s.startswith("recurrent"):
            return "A"
        if s.startswith("dead") or s.startswith("transient"):
            return "D"
        return "?"

    for lab, old, nums, new in ROWS:
        co, cn = cls(old), cls(new)
        flag = ""
        print(f"{lab:<24} {old:<28} {nums}\n{'':<24} {'':<28} {new}{flag}")
    print("\nHeartbeat/conway rows: aliveFrac-based, unaffected by formula change.")
    print("Celestial/Lorenz/prose/SGD/conversation: see recheck_domains.py.")
