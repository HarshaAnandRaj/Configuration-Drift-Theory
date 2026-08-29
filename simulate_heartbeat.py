"""CDT simulation: virtual heartbeat (sustained interval perturbation) vs death-by-lock-in.

Minimal system: a self-avoiding walk on a bounded 2D manifold embedded in R^D.
  - exploration: random on-manifold unit step each tick
  - LIFE term (gamma>0): self-repulsion from recent history -> non-recurrent (alive)
  - DEATH drift: gamma decays to 0 by T_DEATH; after that an attraction-to-origin
    GROWS (basin deepens) -> system spirals into a fixed point (lock-in = DEAD).

Death signal = collapse to origin (radius -> 0, no motion). Alive = wanders the disk.

Scenarios:
  A  constant gamma            -> stays ALIVE  (control)
  B  death drift, no fix       -> DIES (lock-in) at ~T_DEATH
  C  death drift + one JUMPSTART-> RELAPSES (Conway result)
  D1 death drift + sustained ON-manifold interval kicks -> pacemaker (keeps d_s low)
  D2 death drift + sustained OFF-manifold interval kicks-> pacemaker (raises d_s)
  E  pacemaker only [T_DEATH, T_DEATH+800] then STOPS -> RELAPSE (life-support)

CDT measures:
  mean_radius  : typical distance from origin (alive ~ disk, dead ~ 0)
  median_mp    : median min-past-distance (dead ~ 0, alive larger)
  d_s          : correlation dimension of trajectory -> must stay <= 2 (outer wall)
  win_slope    : slope of alive-window (steps a kick stays away from origin) over time
                 <0 = life-support (basin deepening); relapse when kicks stop
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)

# ---- params ---------------------------------------------------------------
D = 8
ACTIVE = 2
STEP = 0.35
K0 = 0.6
T_TRAIN = 3000
T_DEATH = 1500
W = 25
P = 40
AMP = 1.2
R0 = 4.0
AMAX = 0.30
EPS = 1e-3


def krep(t, scenario):
    if scenario == "A":
        return K0
    return K0 if t < T_DEATH else 0.0


def attr(t, scenario):
    if scenario == "A":
        return 0.0
    f = max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH))
    return AMAX * f


def bound(t):
    if t < T_DEATH:
        return R0
    f = (t - T_DEATH) / (T_TRAIN - T_DEATH)
    return R0 * (1.0 - 0.7 * f)


def avoid(S, H):
    if not H:
        return np.zeros(D)
    H = np.asarray(H)
    d = S - H
    r = np.linalg.norm(d, axis=1)
    push = np.clip(1.0 / (r + EPS), 0, 10.0)
    return (d / (r + EPS)[:, None] * push[:, None]).sum(axis=0)


def kick_dir(on_manifold):
    u = rng.standard_normal(ACTIVE if on_manifold else D)
    if on_manifold and D > ACTIVE:
        v = np.zeros(D); v[:ACTIVE] = u
        u = v
    return u / np.linalg.norm(u)


def run(scenario, on_manifold=None):
    S = rng.standard_normal(ACTIVE); S = np.pad(S, (0, D - ACTIVE))
    S = S / np.linalg.norm(S) * 2.0
    H = []
    traj = []
    kicks_at = []
    for t in range(T_TRAIN):
        kr = krep(t, scenario)
        at = attr(t, scenario)
        dirv = np.zeros(D); d = rng.standard_normal(ACTIVE); dirv[:ACTIVE] = d / np.linalg.norm(d)
        S = S + STEP * dirv + kr * avoid(S, H) - at * S
        do = False
        if scenario == "C" and t == T_DEATH:
            S = S + AMP * kick_dir(True); do = True
        elif scenario in ("D1",) and on_manifold and t >= T_DEATH and t % P == 0:
            S = S + AMP * kick_dir(True); do = True
        elif scenario in ("D2",) and (not on_manifold) and t >= T_DEATH and t % P == 0:
            S = S + AMP * kick_dir(False); do = True
        elif scenario == "E" and on_manifold and T_DEATH <= t < T_DEATH + 800 and t % P == 0:
            S = S + AMP * kick_dir(True); do = True
        br = bound(t)
        nrm = np.linalg.norm(S)
        if nrm > br:
            S = S * br / nrm
        traj.append(S.copy()); H.append(S.copy())
        if len(H) > W:
            H.pop(0)
        if do:
            kicks_at.append(t)
    return np.asarray(traj), kicks_at


# ---- metrics --------------------------------------------------------------
def min_past(traj, k_lag=8):
    T = len(traj)
    d = np.linalg.norm(traj[:, None, :] - traj[None, :, :], axis=2)
    mp = np.full(T, np.inf)
    for t in range(k_lag + 1, T):
        mp[t] = d[t, :t - k_lag].min()
    return mp


def corr_dim(traj, n_ref=400, n_eps=24, band=(8, 16)):
    T = len(traj)
    idx = rng.choice(T, min(n_ref, T), replace=False)
    ref = traj[idx]
    dist = np.linalg.norm(ref[:, None, :] - traj[None, :, :], axis=2)
    lo = np.percentile(dist, 2); hi = np.percentile(dist, 98)
    eps = np.logspace(np.log10(max(lo, 1e-6)), np.log10(hi), n_eps)
    counts = np.array([(dist < e).sum(axis=1).mean() for e in eps])
    mask = counts > 1
    sl = slice(*band)
    if mask[sl].sum() < 2:
        sl = mask
    nu, _ = np.polyfit(np.log(eps[sl]), np.log(counts[sl]), 1)
    return float(nu)


def alive_windows_radius(traj, kicks_at, r_thresh=0.5):
    if len(kicks_at) < 2:
        return [], None
    pos = np.linalg.norm(traj, axis=1)
    wins = []
    for i, k in enumerate(kicks_at[:-1]):
        nxt = kicks_at[i + 1]
        seg = pos[k:nxt]
        dead = np.where(seg < r_thresh)[0]
        wins.append(int(dead[0]) if len(dead) else (nxt - k))
    slope = np.polyfit(np.arange(len(wins)), wins, 1)[0] if len(wins) >= 2 else None
    return wins, slope


# ---- run ------------------------------------------------------------------
scenarios = [("A_control", None), ("B_death", None), ("C_jumpstart", None),
             ("D1_pacemaker_on", True), ("D2_pacemaker_off", False),
             ("E_pacemaker_then_stop", True)]
results = {}; trajs = {}
for name, om in scenarios:
    traj, kicks = run(name.split("_")[0], om)
    pos = np.linalg.norm(traj, axis=1)
    mp = min_past(traj)
    mean_r = float(pos.mean())
    post = pos[T_DEATH + 50:] if len(pos) > T_DEATH + 50 else pos
    mean_r_post = float(post.mean())
    alive_frac = float((post > 1.0).mean())   # fraction of post-death time spent clearly away from origin
    ds = corr_dim(traj)
    wins, slope = alive_windows_radius(traj, kicks)
    results[name] = dict(mean_r=mean_r, mean_r_post=mean_r_post, alive_frac=alive_frac,
                         median_mp=float(np.median(mp[8:])), ds=ds,
                         slope=slope, kicks=len(kicks))
    trajs[name] = (traj, kicks, mp, pos)
    print(f"{name:22s} meanR={mean_r:4.2f}  meanR_post={mean_r_post:4.2f}  "
          f"aliveFrac={alive_frac:4.2f}  d_s={ds:.2f}  "
          f"win_slope={slope if slope is None else round(slope,2)}")

# ---- plots ----------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for ax, name in zip(axes.ravel()[:4], ["B_death", "C_jumpstart", "D1_pacemaker_on", "E_pacemaker_then_stop"]):
    traj, kicks, mp, pos = trajs[name]
    ax.plot(pos, lw=0.6)
    ax.axhline(0.5, color="g", ls=":", lw=0.8, label="collapse thresh")
    ax.axvline(T_DEATH, color="k", ls="--", lw=0.8, alpha=0.5)
    for k in kicks:
        ax.axvline(k, color="r", lw=0.3, alpha=0.4)
    ax.set_title(name); ax.set_ylabel("radius ||S||")
axes[1, 1].set_xlabel("step")
fig.suptitle("CDT virtual-heartbeat: radius collapses at death; pacemaker holds it up only while kicking")
fig.tight_layout(); fig.savefig("heartbeat_rho.png", dpi=110)

fig2, ax2 = plt.subplots(1, 1, figsize=(9, 3))
for name in ["A_control", "B_death", "D1_pacemaker_on", "E_pacemaker_then_stop"]:
    traj, kicks, mp, pos = trajs[name]
    ax2.plot(pos, lw=0.5, label=name)
ax2.axvline(T_DEATH, color="k", ls="--", lw=0.8, alpha=0.5)
ax2.axhline(0.5, color="g", ls=":", label="collapse thresh")
ax2.set_title("radius ||S|| over time (high = alive/wandering, ~0 = dead/locked)")
ax2.set_xlabel("step"); ax2.legend(fontsize=7)
fig2.tight_layout(); fig2.savefig("heartbeat_radius.png", dpi=110)
print("\nsaved heartbeat_rho.png and heartbeat_radius.png")
