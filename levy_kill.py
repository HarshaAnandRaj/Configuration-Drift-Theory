"""levy_kill.py -- exploratory Brownian-shortcut test on market data.

The canonical theorem is in configuration_drift_theorem.md. A Brownian shortcut
uses d_w=2. When a walk dimension is independently identified, the generalized
power-law boundary is nu <= d_w. The earlier alpha*d_w/2 expression was wrong:
for an alpha-stable process d_w=alpha already, so it double-counted the tail
index. The Hill estimate below is now diagnostic only.

This script remains exploratory because a trajectory-cloud correlation dimension
need not equal the substrate volume exponent and market paths need not satisfy
the required stationary two-sided heat-kernel assumptions.

REGISTERED THRESHOLD (fixed before running):
  KILL = CDT-normal and generalized verdicts DISAGREE on at least one series,
         AND the observed recurrence (rho_fine vs 200-shuffle null, P1 machinery
         from market_cdt.py) matches the GENERALIZED verdict while contradicting
         normal.
  FAIL = verdicts agree, or observation matches normal, or data are UNDECIDABLE
         under the fix-2 floor rule (reported honestly either way).

Series: BTCUSDT, ETHUSDT (1000d), SPX (10y). Steps per series:
  alpha = Hill estimator on |log-returns| (top-10% tail)
  beta  = MSD exponent of cumulative returns -> d_w = 2/beta
  nu    = debias_nu nu_local + CI on delay-embedded returns (d=3, floor-checked)
  obs   = rho_fine vs shuffle null (recurrence present iff p < 0.05)

Run:  python levy_kill.py
"""
import os
import numpy as np

from market_cdt import load_binance, load_yahoo, logret, embed, shuffle_p
from debias_nu import nu_local, nu_local_ci, n_floor

HERE = os.path.dirname(os.path.abspath(__file__))


def hill_alpha(x, frac=0.10):
    x = np.sort(np.abs(np.asarray(x)))[::-1]
    k = max(20, int(len(x) * frac))
    tail = x[:k]
    return float(1.0 / np.mean(np.log(tail / tail[-1])))


def msd_beta(price, taus=(1, 2, 4, 8, 16, 32, 64)):
    price = np.asarray(price)
    msd = []
    for t in taus:
        d = price[t:] - price[:-t]
        msd.append(float(np.mean(d ** 2)))
    msd = np.array(msd)
    m = msd > 0
    slope, _ = np.polyfit(np.log(np.array(taus)[m]), np.log(msd[m]), 1)
    return float(slope)  # MSD ~ tau^beta


def verdict(nu, bound):
    return "recurrent" if nu <= bound else "transient"


if __name__ == "__main__":
    series = {
        "BTC/USD": logret(load_binance(os.path.join(HERE, "BTCUSDT.json"))),
        "ETH/USD": logret(load_binance(os.path.join(HERE, "ETHUSDT.json")),
        ),
        "S&P500": logret(load_yahoo(os.path.join(HERE, "spx_yahoo.json"))),
    }
    print("=== EXPLORATORY BROWNIAN-SHORTCUT TEST (not a theorem audit) ===\n")
    kills = 0
    for name, r in series.items():
        r = r[np.isfinite(r)]
        a = hill_alpha(r)
        cum = np.cumsum(r)
        b = msd_beta(cum)
        dw = 2.0 / b if b > 0 else float("nan")
        E = embed(r, 3)
        est, lo, hi = nu_local_ci(E, B=12, seed=7)
        fl = n_floor(hi)
        usable = len(E) >= fl
        bound_n = 2.0
        bound_g = dw
        v_n = verdict(est, bound_n)
        v_g = verdict(est, bound_g)
        obs, nm, p = shuffle_p(lambda x: embed(x, 3), r, n_perm=200, seed=3)
        o = "recurrent" if p < 0.05 else "transient"
        print(f"--- {name} (N={len(r)}) ---")
        print(f"  alpha(Hill)={a:.2f}  beta(MSD)={b:.2f}  d_w={dw:.2f}")
        print(f"  nu={est:.2f} CI=[{lo:.2f},{hi:.2f}] floor={fl} "
              f"-> {'USABLE' if usable else 'UNDECIDABLE (below floor)'}")
        print(f"  Brownian shortcut (nu<={bound_n:.2f}): {v_n} | "
              f"measured-d_w heuristic (nu<={bound_g:.2f}): {v_g} | "
              f"observed: {o} (p={p:.3f})")
        if usable and v_n != v_g:
            if o == v_g:
                print("  >>> KILL: observation matches GENERALIZED, contradicts normal")
                kills += 1
            else:
                print("  >>> no kill: observation matches normal")
        elif usable:
            print("  >>> no kill: verdicts agree")
        else:
            print("  >>> inconclusive: below fix-2 floor (need higher-frequency data)")
    print(f"\nRESULT: {kills} kill(s). "
          + ("Brownian shortcut contradicted within this exploratory pipeline."
             if kills else "No contradiction within this exploratory pipeline."))
