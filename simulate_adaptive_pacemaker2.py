"""CDT simulation: refining the virtual-heartbeat automation.

Ladder of resuscitation strategies (all on the same death-drifting system):
  fixed      : blind metronome, fixed interval + fixed magnitude  -> mistuned
  adaptive   : bang-bang external kick when radius < R_TRIG       -> tracks death, life-support
  refined    : PROPORTIONAL + PREDICTIVE external kick, outer-wall GUARDED
               (magnitude scales with deficit; fires before lock-in; on-manifold, capped)
  endogenous : no external kick; instead BOOST INTERNAL self-repulsion when near death
               -> the cure the automation is groping toward (Corollary 2 / pressure governor)

Compare on: aliveFrac (post-death time spent alive), external ENERGY (sum kick^2),
d_s (outer-wall safety), n_kicks.
"""
import numpy as np

D = 8
ACTIVE = 2
STEP = 0.35
K0 = 0.6
W = 25
T_TRAIN = 2400
P_FIXED = 40
R_TRIG = 0.5
R_TARGET = 1.5
GAIN = 1.5
AMP_MAX = 1.5
HORIZON = 6
K_BOOST = 0.6
EPS = 1e-3


def _avoid(S, H):
    if not H:
        return np.zeros(D)
    H = np.asarray(H)
    d = S - H
    r = np.linalg.norm(d, axis=1)
    push = np.clip(1.0 / (r + EPS), 0, 10.0)
    return (d / (r + EPS)[:, None] * push[:, None]).sum(axis=0)


def run(R0, AMAX, T_DEATH, seed, mode):
    rng = np.random.default_rng(seed)
    S = rng.standard_normal(ACTIVE); S = np.pad(S, (0, D - ACTIVE))
    S = S / np.linalg.norm(S) * 1.5
    H = []
    last_kick = -10**9
    kicks = 0
    energy = 0.0
    radius = np.zeros(T_TRAIN)
    traj = np.zeros((T_TRAIN, D))
    r_prev = np.linalg.norm(S)
    for t in range(T_TRAIN):
        kr = K0 if t < T_DEATH else 0.0
        f = max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH))
        at = AMAX * f if t >= T_DEATH else 0.0
        # endogenous boost: revive internal repulsion when near death
        if mode == "endogenous" and t >= T_DEATH and np.linalg.norm(S) < R_TARGET:
            kr = K0 + K_BOOST
        dirv = np.zeros(D); d = rng.standard_normal(ACTIVE); dirv[:ACTIVE] = d / np.linalg.norm(d)
        S = S + STEP * dirv + kr * _avoid(S, H) - at * S
        do = False; amp = 0.0
        if t >= T_DEATH:
            r = np.linalg.norm(S)
            slope = (r - r_prev) / max(1, 1)  # per-step
            ttl = (r - R_TRIG) / abs(slope) if slope < 0 else 1e9   # steps to lock-in
            if mode == "fixed":
                if t % P_FIXED == 0:
                    do = True; amp = 1.2
            elif mode == "adaptive":
                if r < R_TRIG and (t - last_kick) >= 3:
                    do = True; amp = 1.2
            elif mode == "refined":
                if r < R_TARGET or ttl < HORIZON:
                    deficit = max(R_TARGET - r, 0.0)
                    amp = min(GAIN * deficit, AMP_MAX)
                    if amp < 0.05:
                        amp = 0.05
                    do = True
            # endogenous: no external kick
        if do:
            out = S / (np.linalg.norm(S) + EPS)               # outward (restore radius)
            jit = rng.standard_normal(ACTIVE); jit = jit / np.linalg.norm(jit)
            v = out + 0.3 * np.pad(jit, (0, D - ACTIVE))
            S = S + amp * v / np.linalg.norm(v)
            kicks += 1; energy += amp * amp; last_kick = t
        nrm = np.linalg.norm(S)
        br = R0 * (1.0 - 0.7 * max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH)))
        if nrm > br:
            S = S * br / nrm
        radius[t] = np.linalg.norm(S)
        traj[t] = S
        r_prev = radius[t]
        H.append(S.copy())
        if len(H) > W:
            H.pop(0)
    return radius, kicks, energy, traj


def alive_frac(radius, T_DEATH):
    post = radius[T_DEATH + 50:]
    return float((post > 1.0).mean())


def corr_dim(traj, n_ref=400, n_eps=24, band=(8, 16)):
    T = len(traj)
    rng = np.random.default_rng(0)
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


print(f"{'mode':10s} | {'AMAX':>4} | {'aliveFrac':>9} {'kicks':>5} {'energy':>7} {'d_s':>5}")
for AMAX in (0.15, 0.30, 0.60):
    for mode in ("fixed", "adaptive", "refined", "endogenous"):
        rad, nk, en, traj = run(4, AMAX, 1200, 1, mode)
        af = alive_frac(rad, 1200)
        ds = corr_dim(traj)
        print(f"{mode:10s} | {AMAX:>4} | {af:9.2f} {nk:5d} {en:7.1f} {ds:5.2f}")

print("\nROBUSTNESS (R0=4, randomized death realizations):")
import statistics as st
for mode in ("fixed", "adaptive", "refined", "endogenous"):
    afs, ens = [], []
    for s in range(10):
        rng = np.random.default_rng(s + 50)
        TD = int(rng.integers(1000, 1600)); AM = float(rng.uniform(0.15, 0.60))
        rad, nk, en, traj = run(4, AM, TD, s, mode)
        afs.append(alive_frac(rad, TD)); ens.append(en)
    print(f"{mode:10s} aliveFrac={st.mean(afs):.2f}±{st.pstdev(afs):.2f}  energy={st.mean(ens):.0f}")
