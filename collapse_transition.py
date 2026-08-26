"""collapse_transition.py
How far must a system degrade before it falls into EXACT RECURRENCE -- and
what does the fall look like?

We sweep the self-perturbation strength gamma through zero into attraction
(visited configurations become MORE likely to recur) and track:

Order parameters of collapse:
  eff_states  1/sum(p_i^2) over visit fractions -- effective # of configs lived in
  rho_exact   same-site recurrence (late window)
  rms         RMS displacement (is the trajectory going anywhere?)

Early-warning signals (do we SEE the fall coming?):
  ac1         lag-1 autocorrelation of position (critical slowing down)
  osc2        P(x_t == x_{t-2}) -- period-2 locking, the death gait

Everything is emergent: no imposed drift, no imposed schedule. The walker only
knows the local rule w(site) = exp(-gamma * visits[site]).
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ablation_study import walk


def collapse_metrics(X):
    n = len(X)
    h = n // 2
    late = X[h:]

    seen = set()
    exact = np.zeros(n, dtype=bool)
    osc2 = np.zeros(n, dtype=bool)
    for t in range(1, n):
        key = tuple(X[t])
        if key in seen:
            exact[t] = True
        if t >= 2 and key == tuple(X[t - 2]):
            osc2[t] = True
        seen.add(key)

    late_counts = {}
    for x in late:
        k = tuple(x)
        late_counts[k] = late_counts.get(k, 0) + 1
    v = np.array(list(late_counts.values()), dtype=float)
    p = v / v.sum()
    eff = float(1.0 / (p ** 2).sum())

    x = late[:, 1].astype(float)                              # one coordinate
    xc = x - x.mean()
    denom = (xc[:-1] ** 2).sum() * (xc[1:] ** 2).sum()
    ac1 = float((xc[:-1] * xc[1:]).sum() / denom) if denom > 0 else 1.0

    return (
        float(exact[h:].mean()),
        eff,
        float(np.sqrt((late ** 2).sum(1).mean())),
        ac1,
        float(osc2[h:].mean()),
    )


if __name__ == "__main__":
    D, STEPS, TRIALS = 3, 4000, 10
    gammas = np.linspace(-1.25, 0.75, 27)

    rows = []
    print(f"D={D} steps={STEPS} trials={TRIALS}")
    print(f"{'gamma':>7} {'rho_ex':>7} {'eff_st':>9} {'rms':>8} "
          f"{'ac1':>7} {'osc2':>7}")
    for g in gammas:
        acc = np.zeros(5)
        for i in range(TRIALS):
            X, _ = walk(D, float(g), STEPS, 42000 + i * 23 + int(abs(g) * 100))
            acc += np.array(collapse_metrics(X))
        m = acc / TRIALS
        rows.append((float(g), *m))
        print(f"{g:>7.3f} {m[0]:>7.3f} {m[1]:>9.1f} {m[2]:>8.1f} "
              f"{m[3]:>7.3f} {m[4]:>7.3f}")

    with open("collapse_transition.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gamma", "rho_exact", "eff_states", "rms", "ac1", "osc2"])
        w.writerows(rows)

    r = {k: np.array([row[j] for row in rows])
         for j, k in enumerate(["g", "rho", "eff", "rms", "ac1", "osc2"])}

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].semilogy(r["g"], r["eff"], marker="o", ms=3, color="tab:blue")
    ax[0].set_ylabel("effective states lived in (log)")
    ax[0].set_xlabel("self-perturbation  gamma")
    ax[0].axvline(0.0, color="grey", ls=":", lw=1)
    ax2 = ax[0].twinx()
    ax2.plot(r["g"], r["rho"], marker="s", ms=3, color="tab:red")
    ax2.set_ylabel("exact-recurrence rate", color="tab:red")

    ax[1].plot(r["g"], r["ac1"], marker="o", ms=3, label="autocorr ac1")
    ax[1].plot(r["g"], r["osc2"], marker="^", ms=3, label="P(period-2 lock)")
    ax[1].set_xlabel("self-perturbation  gamma")
    ax[1].legend()
    ax[1].set_title("early-warning signals")

    fig.suptitle("Fall into exact recurrence: emergent collapse transition (D=3)")
    fig.tight_layout()
    fig.savefig("collapse_transition.png", dpi=130)
    print("\nwrote collapse_transition.csv, collapse_transition.png")
