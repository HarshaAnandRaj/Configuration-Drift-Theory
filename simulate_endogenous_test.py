"""CDT test: can an ENDOGENOUS rescuer actually sustain / revive a dying system?

The honest test (not the earlier cheating version where the simulator flipped the
gain). Death = loss of self-repulsion. So we model the intrinsic repulsion CAPACITY
c(t) as a state variable:
  - death drive grows over time, pulling the system into a deep well
  - c regenerates ONLY when the system is already alive (radius > R_ALIVE)
    -> c is COUPLED to the very life it is meant to rescue
If the system collapses, c -> 0 and (because regeneration needs life) there is NO
internal path back: the rescuer dies with the system.

Mechanisms:
  ext_fixed / ext_adaptive : EXTERNAL pacemaker (baseline; c=K0 + kicks)
  endo_coupled    : c regenerates only when alive (coupled to death basin)
  endo_decoupled  : c relaxes to K0 AUTONOMOUSLY (independent of system) -> an
                    internal organ with its own pacemaker (heart's SA node)

Test A (start alive, death drift @1200): sustain?
Test B (start COLLAPSED, deep well ON): revive?  <- the decisive closed-loop test
"""
import numpy as np

D = 8
ACTIVE = 2
STEP = 0.35
W = 25
T_TRAIN = 2400
T_DEATH = 1200
R0 = 4.0
AMAX = 0.40
CMAX = 1.5           # deep-well pull magnitude (finite; organ can escape, zero-energy cannot)
K0 = 0.6
R_ALIVE = 1.2
P_FIXED = 40
R_TRIG = 0.5
EPS = 1e-3


def _avoid(S, H):
    if not H:
        return np.zeros(D)
    H = np.asarray(H)
    d = S - H
    r = np.linalg.norm(d, axis=1)
    push = np.clip(1.0 / (r + EPS), 0, 10.0)
    return (d / (r + EPS)[:, None] * push[:, None]).sum(axis=0)


def run(mode, dead_start=False, seed=1):
    rng = np.random.default_rng(seed)
    if dead_start:
        S = np.zeros(D)
    else:
        S = rng.standard_normal(ACTIVE); S = np.pad(S, (0, D - ACTIVE))
        S = S / np.linalg.norm(S) * 1.5
    H = []
    c = 0.0 if dead_start else K0   # dead start = no intrinsic repulsion at all
    last_kick = -10**9
    kicks = 0
    radius = np.zeros(T_TRAIN)
    traj = np.zeros((T_TRAIN, D))
    for t in range(T_TRAIN):
        r = np.linalg.norm(S)
        if mode in ("endo_coupled", "endo_decoupled"):
            if mode == "endo_coupled":
                c += 0.10 * ((K0 if r > R_ALIVE else 0.0) - c)   # coupled to life
            else:
                c += 0.10 * (K0 - c)                              # autonomous
            c = float(min(K0, max(0.0, c)))
        else:
            c = K0                                                # external: baseline alive
        f = 1.0 if dead_start else max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH))
        at = AMAX * f
        cw = CMAX * f
        dirv = np.zeros(D); d = rng.standard_normal(ACTIVE); dirv[:ACTIVE] = d / np.linalg.norm(d)
        well = cw * S / (np.linalg.norm(S) + 0.2)                # deep pull to origin
        S = S + STEP * dirv + c * _avoid(S, H) - at * S - well
        do = False; amp = 0.0
        if mode == "ext_fixed" and t >= T_DEATH and t % P_FIXED == 0:
            do = True; amp = 1.2
        elif mode == "ext_adaptive" and t >= T_DEATH:
            if r < R_TRIG and (t - last_kick) >= 3:
                do = True; amp = 1.2
        if do:
            u = rng.standard_normal(ACTIVE); u = u / np.linalg.norm(u)
            S = S + amp * np.pad(u, (0, D - ACTIVE))
            kicks += 1; last_kick = t
        nrm = np.linalg.norm(S)
        br = R0 * (1.0 - 0.7 * f)
        if nrm > br:
            S = S * br / nrm
        radius[t] = np.linalg.norm(S)
        traj[t] = S
        H.append(S.copy())
        if len(H) > W:
            H.pop(0)
    return radius, kicks, traj


def alive_frac(radius, T0=0):
    return float((radius[T0:] > 1.0).mean())


print("TEST A (start alive, death drift @1200): aliveFrac / n_kicks")
for mode in ("ext_fixed", "ext_adaptive", "endo_coupled", "endo_decoupled"):
    rad, nk, _ = run(mode, dead_start=False, seed=1)
    print(f"  {mode:14s} {alive_frac(rad, 1250):.2f} / {nk}")

print("\nTEST B (start COLLAPSED, deep well ON): can it revive? aliveFrac / n_kicks")
for mode in ("ext_adaptive", "endo_coupled", "endo_decoupled"):
    rad, nk, _ = run(mode, dead_start=True, seed=1)
    print(f"  {mode:14s} {alive_frac(rad, 0):.2f} / {nk}")

print("\nTEST B robust (5 seeds): revive aliveFrac")
for mode in ("ext_adaptive", "endo_coupled", "endo_decoupled"):
    afs = [alive_frac(run(mode, dead_start=True, seed=s)[0], 0) for s in range(5)]
    print(f"  {mode:14s} {sum(afs)/len(afs):.2f}")
