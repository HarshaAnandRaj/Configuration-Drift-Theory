"""make_figures.py
Produces figures for the report:
  phase_diagram.png  -- recurrence rate vs drift across dimensions (the phase
                        transition), from phase_scan.csv.
  time_course.png    -- exact-recurrence density vs trial index for the
                        synthetic drifting drawing vs i.i.d. drawing
                        (the originally-requested time-course of the decay).
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from drift_walker import recurrence_events

# ---------- phase diagram ----------
D = []
A = []
R = []
with open("phase_scan.csv") as f:
    rd = csv.DictReader(f)
    for row in rd:
        D.append(int(row["D"])); A.append(float(row["alpha"])); R.append(float(row["rho_mean"]))
D = np.array(D); A = np.array(A); R = np.array(R)

plt.figure(figsize=(7, 4.5))
for d in sorted(set(D)):
    m = D == d
    plt.plot(A[m], R[m], marker="o", label=f"D={d}")
plt.axhline(0.5, color="grey", ls="--", lw=1, label="rho=0.5 (transition)")
plt.xlabel("drift  alpha")
plt.ylabel("late-window recurrence rate  rho_infty")
plt.title("Recurrence phase transition: drift vs dimension")
plt.legend()
plt.tight_layout()
plt.savefig("phase_diagram.png", dpi=130)
plt.close()

# ---------- time course (configuration / centroid recurrence) ----------
def binned_ts(X, eps, bins=30):
    r = recurrence_events(X, eps)
    n = len(r)
    b = np.array_split(r, bins)
    return np.array([x.mean() for x in b])

Xd = np.load("synthetic_drifting.npy")
Xi = np.load("synthetic_iid.npy")
td = binned_ts(Xd, 8.0)
ti = binned_ts(Xi, 8.0)
x = np.linspace(1, len(Xd), len(td))

plt.figure(figsize=(7, 4.5))
plt.plot(x, td, label="drifting configs (decay)")
plt.plot(x, ti, label="i.i.d. configs (no decay)")
plt.xlabel("configuration index (stroke order)")
plt.ylabel("configuration-recurrence density (binned)")
plt.title("Time-course of configuration-recurrence density")
plt.legend()
plt.tight_layout()
plt.savefig("time_course.png", dpi=130)
plt.close()
print("wrote phase_diagram.png, time_course.png")
