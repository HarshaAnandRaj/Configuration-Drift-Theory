"""CDT simulation: ADAPTIVE (state-triggered) pacemaker vs fixed-interval pacemaker.

User's hunch: the system does not fall on a uniform clock -- collapse timing is
variable (fast sometimes, "forever" other times) and depends on system size
("number of cells and space"). So a fixed-interval kick is mistuned: under-drives
when collapse is fast (relapse between beats), over-drives when slow (wasteful).
An ADAPTIVE pacemaker triggers a kick only when the system nears lock-in
(radius -> origin), i.e. it reads the system's OWN state. Still exogenous energy,
but internally GATED -> closer to a reflex/homeostat than a blind metronome.

Tests:
  - Grid over system size R0 (space) and death speed AMAX (fast/slow fall)
  - Adaptive trigger: kick when radius < R_trig (near lock-in), safety cap max_interval
  - Compare fixed-interval vs adaptive on aliveFrac (post-death time spent away
    from origin) and number of kicks (efficiency).
  - Robustness across randomized death realizations (variable fall time).
"""
import numpy as np

# ---- params ---------------------------------------------------------------
D = 8
ACTIVE = 2
STEP = 0.35
K0 = 0.6
W = 25
AMP = 1.2
T_TRAIN = 2400
P_FIXED = 40
R_TRIG = 0.5           # kick when radius has fallen toward lock-in (near collapse)
MAX_INTERVAL = 200
MIN_GAP = 3


def run(R0, AMAX, T_DEATH, seed, mode):
    rng = np.random.default_rng(seed)
    S = rng.standard_normal(ACTIVE); S = np.pad(S, (0, D - ACTIVE))
    S = S / np.linalg.norm(S) * 1.5
    H = []
    last_kick = -10**9
    kicks = []
    radius = np.zeros(T_TRAIN)
    prevS = S.copy()
    for t in range(T_TRAIN):
        kr = K0 if t < T_DEATH else 0.0
        f = max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH))
        at = AMAX * f if t >= T_DEATH else 0.0
        dirv = np.zeros(D); d = rng.standard_normal(ACTIVE); dirv[:ACTIVE] = d / np.linalg.norm(d)
        S = S + STEP * dirv + kr * _avoid(S, H) - at * S
        do = False
        act = np.linalg.norm(S - prevS)
        if mode == "fixed" and t >= T_DEATH and t % P_FIXED == 0:
            do = True
        elif mode == "adaptive" and t >= T_DEATH:
            r = np.linalg.norm(S)
            if (r < R_TRIG and (t - last_kick) >= MIN_GAP) or (t - last_kick) >= MAX_INTERVAL:
                do = True
        if do:
            u = rng.standard_normal(ACTIVE); u = u / np.linalg.norm(u)
            S = S + AMP * np.pad(u, (0, D - ACTIVE))
            kicks.append(t); last_kick = t
        nrm = np.linalg.norm(S)
        br = R0 * (1.0 - 0.7 * max(0.0, (t - T_DEATH) / (T_TRAIN - T_DEATH)))
        if nrm > br:
            S = S * br / nrm
        radius[t] = np.linalg.norm(S)
        H.append(S.copy())
        if len(H) > W:
            H.pop(0)
    return radius, kicks


def _avoid(S, H):
    if not H:
        return np.zeros(D)
    H = np.asarray(H)
    d = S - H
    r = np.linalg.norm(d, axis=1)
    push = np.clip(1.0 / (r + 1e-3), 0, 10.0)
    return (d / (r + 1e-3)[:, None] * push[:, None]).sum(axis=0)


def alive_frac(radius, T_DEATH):
    post = radius[T_DEATH + 50:]
    return float((post > 1.0).mean())


# ---- grid: system size (space) x death speed (fall rate) -------------------
print("GRID  R0=space, AMAX=death-speed ; aliveFrac / n_kicks")
print(f"{'R0':>4} {'AMAX':>5} | {'fixed':>16} | {'adaptive':>18}")
for R0 in (2, 4, 8, 16):
    for AMAX in (0.15, 0.30, 0.60):
        T_DEATH = 1200
        rf, kf = run(R0, AMAX, T_DEATH, 1, "fixed")
        ra, ka = run(R0, AMAX, T_DEATH, 1, "adaptive")
        af, aa = alive_frac(rf, T_DEATH), alive_frac(ra, T_DEATH)
        print(f"{R0:>4} {AMAX:>5} | {af:5.2f}/{len(kf):3d}     | "
              f"{aa:5.2f}/{len(ka):3d}")

# ---- robustness: variable fall time across seeds ---------------------------
print("\nROBUSTNESS across randomized death realizations (R0=4 baseline)")
import statistics as st
fixed_af, adp_af, fixed_n, adp_n = [], [], [], []
for s in range(12):
    rng = np.random.default_rng(s + 100)
    T_DEATH = int(rng.integers(1000, 1600))
    AMAX = float(rng.uniform(0.15, 0.60))
    rf, kf = run(4, AMAX, T_DEATH, s, "fixed")
    ra, ka = run(4, AMAX, T_DEATH, s, "adaptive")
    fixed_af.append(alive_frac(rf, T_DEATH)); adp_af.append(alive_frac(ra, T_DEATH))
    fixed_n.append(len(kf)); adp_n.append(len(ka))
print(f"fixed    aliveFrac mean={st.mean(fixed_af):.2f} std={st.pstdev(fixed_af):.2f}  kicks={st.mean(fixed_n):.0f}")
print(f"adaptive aliveFrac mean={st.mean(adp_af):.2f} std={st.pstdev(adp_af):.2f}  kicks={st.mean(adp_n):.0f}")

# ---- show adaptive interval distribution (non-uniform, tracks death) -------
ra, ka = run(4, 0.30, 1200, 7, "adaptive")
inter = np.diff(ka)
print(f"\nadaptive inter-kick intervals (seed7, AMAX=0.30): "
      f"min={inter.min()} max={inter.max()} mean={inter.mean():.0f} "
      f"-> non-uniform, tracks variable collapse")
print(f"(fixed would be constant 40; adaptive fires {len(ka)} times, on demand)")
