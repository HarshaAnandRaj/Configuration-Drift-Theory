"""zeus_adaptive_dim.py -- adaptive-dimensional rescue on a real 768-dim model.

Subject: fresh-5000 Zeus checkpoint (9/768 dims active -- huge dormant
reserve). Question (§5.11): does recruiting dormant dimensions restore novelty
with zero injected energy, beating heartbeat kicks?

Three free-roll arms (1500 steps, CPU), all intervention via model.S assignment
(read-only model, nothing written inside Zeus):
  none    : free rollout (baseline)
  recruit : each step, amplify the DORMANT-subspace component (PCs beyond k90
            from a baseline PCA) by GAIN (endogenous-geometry-flavored: no
            noise injected, E = 0); clamp ||S|| at 40 (training norm_bound)
  kicks   : heartbeat -- raw Gaussian kick (1/2 ||S||) when the windowed
            exact-recurrence rate on PCA states exceeds 0.15 (EXOGENOUS, E > 0)
Metrics: richness k90, aliveFrac (unseen coarse cells on PCA states),
gamma_hat (phase null, deadband 0.4), injected energy, readout entropy
(task axis void: mouth already collapsed -- stated honestly).
Prediction (§5.11): recruit raises novelty/richness with E = 0; kicks add
novelty at energy cost.
Run with the Zeus venv python; outputs to the CDT folder only.
"""
import argparse
import os
import pathlib
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_ZEUS = r"C:\Users\Anand\Desktop\Projects\Zeus"
sys.path.insert(0, _ZEUS)

import torch
from core.model import ZeusCore

from gamma_probe import gamma_hat

GAIN = 2.0
NORM_CAP = 40.0


def roll(model, steps, seed=0, intervene=None, S_hist=None):
    g = torch.Generator(device="cpu").manual_seed(seed)
    model.reset_state(noise=0.1, generator=g)
    traj, toks, energy, n_int = [], [], 0.0, 0
    for t in range(steps):
        with torch.no_grad():
            logits, _ = model.step(None)
        if intervene is not None:
            model.S, e, n = intervene(model.S, t, traj)
            energy += e
            n_int += n
        traj.append(model.S.detach().cpu().clone())
        toks.append(int(logits.argmax()))
    S = np.stack([np.asarray(s) for s in traj]).astype(float)
    return S, np.array(toks), energy, n_int


def pca_of(S, var_keep=0.90):
    C = S - S.mean(0)
    _, Sv, Vt = np.linalg.svd(C, full_matrices=False)
    v = (Sv ** 2) / (Sv ** 2).sum()
    k = int(min(64, np.searchsorted(np.cumsum(v), var_keep) + 1))
    return C @ Vt[:k].T, Vt, k


def alive_frac(P, cell=0.5):
    Q = P / (float(np.sqrt((P ** 2).mean())) + 1e-12)
    seen, n = set(), 0
    for s in Q:
        key = tuple(np.round(s / cell).astype(int))
        n += key not in seen
        seen.add(key)
    return n / len(Q)


def lock_rate(hist, eps_rel=0.05, win=150, lag=4):
    if len(hist) < win:
        return 0.0
    W = np.stack([np.asarray(h).ravel() for h in hist[-win:]])
    mu = W.mean(0)
    C = W - mu
    _, Sv, Vt = np.linalg.svd(C, full_matrices=False)
    v = (Sv ** 2) / (Sv ** 2).sum()
    k = int(max(2, np.searchsorted(np.cumsum(v), 0.90) + 1))
    P = C @ Vt[:k].T
    Rp = float(np.sqrt((P ** 2).mean()))
    D = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    iu, ju = np.triu_indices(len(P), 1)
    keep = (ju - iu) > lag
    return float(np.mean(D[iu[keep], ju[keep]] < eps_rel * Rp))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=r"C:\Users\Anand\AppData\Local\Temp\opencode\zeus_fresh5000\zeus_step5000.pt")
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--out", default=os.path.join(HERE, "zeus_adaptive_dim_out.txt"))
    args = ap.parse_args()

    model = ZeusCore.load(args.ckpt, device="cpu")
    model.eval()
    dim = int(model.cfg.dim)
    print(f"model dim = {dim}")

    S0, _, _, _ = roll(model, args.steps, seed=1)
    P0, Vt0, k0 = pca_of(S0)
    mu0 = S0.mean(0)
    Vd = Vt0[k0:].T  # dormant subspace projector basis
    print(f"baseline richness k90 = {k0}")

    def recruit_fn(S_t, t, hist):
        d = (S_t.detach().cpu().numpy().ravel() - mu0) @ Vd
        kick = torch.from_numpy((Vd @ ((GAIN - 1.0) * d)).astype(np.float32))
        Sn = (S_t + kick.to(S_t.device)).clone()
        nrm = float(Sn.norm())
        if nrm > NORM_CAP:
            Sn = Sn * (NORM_CAP / nrm)
        return Sn, 0.0, 1

    def kicks_fn(S_t, t, hist):
        if t % 25 != 0 or len(hist) < 150:
            return S_t, 0.0, 0
        if lock_rate(hist) > 0.15:
            n0 = float(S_t.norm())
            kv = torch.randn_like(S_t) * (0.5 * n0 / dim ** 0.5)
            e = float((kv ** 2).sum())
            return (S_t + kv).clone(), e, 1
        return S_t, 0.0, 0

    rows = {}
    S, _, _, _ = roll(model, args.steps, seed=1)
    rows["none"] = (S, 0.0, 0)
    S, _, e, n = roll(model, args.steps, seed=1, intervene=recruit_fn)
    rows["recruit"] = (S, e, n)
    S, _, e, n = roll(model, args.steps, seed=1, intervene=kicks_fn)
    rows["kicks"] = (S, e, n)

    print(f"{'arm':8s} | k90 | aliveFrac | ghat(phase)      | E       | n_int")
    lines = []
    for arm, (S, e, n) in rows.items():
        P, _, k = pca_of(S)
        Pn = P / (float(np.sqrt((P ** 2).mean())) + 1e-12)
        af = alive_frac(P)
        g = gamma_hat(Pn, null="phase")
        line = (f"{arm:8s} | {k:3d} | {af:9.3f} | {g['est']:+.3f} "
                f"[{g['lo']:+.2f},{g['hi']:+.2f}] EXPLORATORY | "
                f"{e:7.1f} | {n:5d}")
        print(line)
        lines.append(line)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(f"ckpt={args.ckpt} steps={args.steps} baseline_k90={k0}\n")
        fh.write("\n".join(lines) + "\n")
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
