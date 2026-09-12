"""zeus_probe_cdt.py -- CDT-corrected probe for a Zeus checkpoint (781-dim ready).

Runs OUTSIDE the Zeus repo (no edits there): imports ZeusCore read-only,
loads the checkpoint read-only, writes outputs only to the CDT folder.
Dim-agnostic: reads model.cfg.dim (768 or 781 alike); every operator runs on
the INTRINSIC (PCA) manifold, never raw ambient space.

Pipeline (corrected formula):
  beta = MSD exponent on PCA states -> d_w = 2/beta (measured, never assumed)
  alpha = Hill tail index on PCA increment norms (generalized iff alpha < 2)
  bound = alpha*d_w/2 if alpha < 2 else d_w
  nu = nu_local + CI on PCA states; floor N >= 100*10**(nu/2) else UNDECIDABLE
  ghat = gamma_probe inner-wall operator with 0.4 deadband (PCA states)
  alive <=> usable N AND nu <= bound AND ghat holds
Resilience upgrade: raw random kick vs ON-MANIFOLD (PCA-projected) kick --
Sec 5.9.4 predicts raw kicks risk outer-wall damage at high ambient dim.
Autonomy + reportability stay descriptive (not CDT-derived).

Run (from CDT folder, with the Zeus venv python for torch):
  C:\\...\\Zeus\\.venv\\Scripts\\python.exe zeus_probe_cdt.py
    --ckpt C:\\...\\Zeus\\runs\\proof_heartbeat\\zeus.pt --steps 1500
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
import torch.nn.functional as F
from core.model import ZeusCore

from debias_nu import nu_local_ci, n_floor
from gamma_probe import gamma_hat


def roll(model, steps, drive_ids=None, kick=None, seed=0):
    g = torch.Generator(device="cpu").manual_seed(seed)
    model.reset_state(noise=0.1, generator=g)
    traj, toks = [], []
    for t in range(steps):
        inp = int(drive_ids[t % len(drive_ids)]) if drive_ids is not None else None
        with torch.no_grad():
            logits, _ = model.step(inp)
        if kick is not None and t == kick[0]:
            with torch.no_grad():
                model.S = (model.S + kick[1].to(model.S.device)).clone()
        traj.append(model.S.detach().cpu().clone())
        toks.append(int(logits.argmax()))
    S = np.stack([s.numpy() if isinstance(s, torch.Tensor) else np.asarray(s)
                  for s in traj])
    return np.asarray(S, dtype=float), np.array(toks)


def pca_reduce(S, var_keep=0.90, cap=64):
    C = S - S.mean(0)
    _, Sv, Vt = np.linalg.svd(C, full_matrices=False)
    var = (Sv ** 2) / (Sv ** 2).sum()
    k = int(min(cap, np.searchsorted(np.cumsum(var), var_keep) + 1))
    return C @ Vt[:k].T, Vt, k


def msd_beta(P):
    n = len(P)
    lags = np.arange(1, min(n // 4, 400))
    msd = [np.mean(np.sum((P[l:] - P[:-l]) ** 2, 1)) for l in lags]
    slope, _ = np.polyfit(np.log(lags), np.log(np.maximum(msd, 1e-300)), 1)
    return float(slope)


def hill_alpha(v, frac=0.10):
    x = np.sort(np.abs(np.asarray(v, dtype=float)))[::-1]
    k = max(20, int(len(x) * frac))
    tail = x[:k]
    m = float(np.mean(np.log(tail / tail[-1])))
    return float(1.0 / m) if m > 0 else float("inf")


def token_entropy(toks):
    _, c = np.unique(toks, return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log(p)).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=os.path.join(
        _ZEUS, "runs", "proof_heartbeat", "zeus.pt"))
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--out", default=os.path.join(HERE, "zeus_probe_out.txt"))
    ap.add_argument("--kick_frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--null", default="steps", choices=["steps", "phase"])
    args = ap.parse_args()

    model = ZeusCore.load(args.ckpt, device="cpu")
    model.eval()
    dim = int(model.cfg.dim)
    print(f"model dim = {dim} (operators run on intrinsic manifold, never raw)")

    S_free, toks_free = roll(model, args.steps, seed=args.seed)
    P, Vt, k90 = pca_reduce(S_free)
    print(f"intrinsic dims to 90% var: {k90} (of {dim})")
    # nu_local's r_max band assumes O(1) clouds; PCA states are O(100).
    # Correlation dimension is scale-invariant, so normalize (beta/alpha/
    # gamma_hat are all scale-invariant too).
    P = P / float(np.sqrt((P ** 2).mean()))

    beta = msd_beta(P)
    dw = 2.0 / beta
    inc = np.linalg.norm(P[1:] - P[:-1], axis=1)
    alpha = hill_alpha(inc)
    bound = alpha * dw / 2.0 if alpha < 2 else dw
    est, lo, hi = nu_local_ci(P, B=12, seed=11)
    fl = n_floor(hi)
    usable = len(P) >= fl
    g = gamma_hat(P, null=args.null)
    g_ok = bool(g.get('calibrated_wall_verdict', False))
    outer = est <= bound
    alive = bool(usable and outer and g_ok)
    print(f"[outer] beta={beta:.2f} dw={dw:.2f} alpha={alpha:.2f} "
          f"bound={bound:.2f} nu={est:.2f} CI=[{lo:.2f},{hi:.2f}] "
          f"floor={fl} N={len(P)} -> {'USABLE' if usable else 'UNDECIDABLE'}; "
          f"heuristic inequality={outer}; not a recurrence proof")
    print(f"[inner] ghat={g['est']:+.3f} CI=[{g['lo']:+.3f},{g['hi']:+.3f}] "
          f"rhyme={g['rhyme']:.3f} -> EXPLORATORY")
    print('VERDICT: exploratory diagnostics; no calibrated CDT/aliveness verdict')

    drive = np.tile([12, 400, 7, 88], int(np.ceil(args.steps / 4)))[:args.steps]
    S_drv, _ = roll(model, args.steps, drive_ids=drive, seed=args.seed)
    div = float(np.mean(np.linalg.norm(S_free - S_drv, axis=1)))
    print(f"[autonomy, descriptive] mean||free-driven||={div:.1f}")

    kick_at = args.steps // 2
    norm0 = float(np.linalg.norm(S_free[kick_at]))
    rng = np.random.default_rng(7)
    raw = rng.standard_normal(dim)
    raw = raw / np.linalg.norm(raw) * (args.kick_frac * norm0)
    S_rk, _ = roll(model, args.steps,
                   kick=(kick_at, torch.from_numpy(raw).float()), seed=args.seed)
    proj = Vt[:k90].T @ (Vt[:k90] @ raw)
    proj = proj / np.linalg.norm(proj) * (args.kick_frac * norm0)
    S_mk, _ = roll(model, args.steps,
                   kick=(kick_at, torch.from_numpy(proj).float()), seed=args.seed)
    post_r = np.linalg.norm(S_rk[kick_at + 1:] - S_free[kick_at + 1:], axis=1)
    post_m = np.linalg.norm(S_mk[kick_at + 1:] - S_free[kick_at + 1:], axis=1)
    print(f"[resilience] raw-kick settle={float(post_r[len(post_r)//2]):.1f}  "
          f"manifold-kick settle={float(post_m[len(post_m)//2]):.1f} "
          f"(§5.9.4: raw risks off-manifold damage)")

    H_all = token_entropy(toks_free)
    words = [model.decode([toks_free[i]]).strip()
             for i in range(0, args.steps, 20)]
    print(f"[reportability, descriptive] token entropy={H_all:.2f}")
    print("MONOLOGUE:", " | ".join(words)[:160])

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(f"ckpt={args.ckpt} steps={args.steps} dim={dim} k90={k90}\n"
                 f"beta={beta:.3f} dw={dw:.3f} alpha={alpha:.3f} bound={bound:.3f}\n"
                 f"nu={est:.3f} CI=[{lo:.3f},{hi:.3f}] floor={fl} "
                 f"usable={usable} outer={outer}\n"
                 f"ghat={g['est']:+.3f} CI=[{g['lo']:+.3f},{g['hi']:+.3f}] "
                 f"g_ok={g_ok}\nVERDICT=EXPLORATORY_ONLY\n"
                 f"autonomy_div={div:.1f} "
                 f"raw_settle={float(post_r[len(post_r)//2]):.1f} "
                 f"manifold_settle={float(post_m[len(post_m)//2]):.1f} "
                 f"H_tokens={H_all:.2f}\nmonologue={' | '.join(words)[:400]}\n")
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
