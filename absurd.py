"""absurd.py
Two never-measured substrates, chosen for maximum disrespectability.

1. CONWAY'S LIFE -- a universe whose local rule knows neither attraction nor
   repulsion. Questions: does the death gait (exact periodic lock-in) emerge
   SPONTANEOUSLY from random soup? Does a mutation whisper-dose rescue it?
   PREDICTIONS:
     P1 every random-soup run reaches EXACT periodic lock-in (rho_exact -> 1)
     P2 lock time grows with world size
     P3 periodic cell-resurrection perturbation => new configurations keep
        appearing forever (sustained)
2. DIGITS OF PI -- determinism with no dynamics. Is pi's digit-stream alive
   (transient) or dead (periodic)? Control: 1/7 = 0.142857..., clockwork.
   PREDICTIONS:
     P4 pi block-recurrence matches the PURE-CHANCE expectation at every
        block length (no memory, no rhyme beyond chance)
     P5 1/7 shows TOTAL recurrence at its period (clockwork detected)
     P6 corr-dim of pi window-vectors ~ full dimension (fills space),
        indistinguishable from true RNG
"""

import hashlib
import sys
import numpy as np

sys.set_int_max_str_digits(100_000)


# ---------------- Conway ----------------

def life_step(g):
    n = sum(np.roll(np.roll(g, i, 0), j, 1)
            for i in (-1, 0, 1) for j in (-1, 0, 1)) - g
    return (((g == 1) & ((n == 2) | (n == 3))) |
            ((g == 0) & (n == 3))).astype(np.uint8)


def life_run(L, steps=400, seed=0, poke_every=None, poke_n=8):
    rng = np.random.default_rng(seed)
    g = (rng.random((L, L)) < 0.3).astype(np.uint8)
    seen = {}
    lock_gen, period = None, None
    new_hashes_late = 0
    h0_half = int(steps * 0.6)
    for t in range(steps):
        key = hashlib.md5(g.tobytes()).digest()
        if key in seen:
            if lock_gen is None:
                lock_gen, period = t, t - seen[key]
        else:
            seen[key] = t
            if t >= h0_half:
                new_hashes_late += 1
        if poke_every and t % poke_every == 0 and poke_every > 0:
            ys = rng.integers(0, L, poke_n)
            xs = rng.integers(0, L, poke_n)
            g[ys, xs] ^= 1
        g = life_step(g)
    frozen = float((g == life_step(g)).mean())
    return {"locked_gen": lock_gen, "period": period,
            "distinct_configs": len(seen),
            "new_configs_late": new_hashes_late,
            "frozen_frac": round(frozen, 3)}


# ---------------- pi ----------------

def pi_digits(D):
    def atan_inv(x, one):
        total, term, k, sign = 0, one // x, 1, 1
        while term:
            total += sign * (term // k)
            term //= x * x
            k += 2
            sign = -sign
        return total

    one = 10 ** (D + 15)
    pi = 4 * (4 * atan_inv(5, one) - atan_inv(239, one))
    s = str(pi // 10 ** 15)
    return [int(c) for c in s[1:D + 1]]


def rational_digits(block, D):
    s = (block * ((D // len(block)) + 1))[:D]
    return [int(c) for c in s]


def block_recurrence(digs, w):
    blocks = [tuple(digs[i:i + w]) for i in range(0, len(digs) - w + 1, w)]
    h = len(blocks) // 2
    occ = set(blocks[:h])
    hits = [b in occ for b in blocks[h:]]
    meas = float(np.mean(hits)) if hits else float("nan")
    expct = min(1.0, h / (10 ** w))
    return round(meas, 4), round(expct, 4)


if __name__ == "__main__":
    print("=========== REGISTERED PREDICTIONS ===========")
    print("LIFE: P1 spontaneous exact lock-in from soup; P2 lock time grows")
    print("      with size; P3 mutation dose sustains innovation forever")
    print("PI  : P4 block recurrence == chance at every length (no memory);")
    print("      P5 1/7 = total clockwork recurrence; P6 pi nu ~ full dim")

    print("\n=========== 1. CONWAY'S LIFE ===========")
    print(f"{'L':>4} {'locked_gen':>11} {'period':>7} {'configs':>8} "
          f"{'new_late':>9} {'frozen':>7}")
    for L in (32, 64, 128):
        r = life_run(L, steps=400, seed=L)
        lg = r["locked_gen"] if r["locked_gen"] is not None else -1
        pd = r["period"] if r["period"] is not None else -1
        print(f"{L:>4} {lg:>11} {pd:>7} {r['distinct_configs']:>8} "
              f"{r['new_configs_late']:>9} {r['frozen_frac']:>7}")

    print("\n--- with mutation dose (flip 8 cells every 25 gens) ---")
    print(f"{'L':>4} {'locked_gen':>11} {'period':>7} {'configs':>8} "
          f"{'new_late':>9} {'frozen':>7}")
    for L in (32, 64, 128):
        r = life_run(L, steps=400, seed=L, poke_every=25, poke_n=8)
        lg = r["locked_gen"] if r["locked_gen"] is not None else -1
        pd = r["period"] if r["period"] is not None else -1
        print(f"{L:>4} {lg:>11} {pd:>7} {r['distinct_configs']:>8} "
              f"{r['new_configs_late']:>9} {r['frozen_frac']:>7}")

    print("\n=========== 2. DIGITS OF PI (vs 1/7, vs RNG) ===========")
    D = 12000
    sources = {
        "pi": pi_digits(D),
        "1/7 (clockwork)": rational_digits("142857", D),
        "true RNG": list(np.random.default_rng(7).integers(0, 10, D)),
    }
    print(f"{'source':>17} " +
          " ".join(f"w={w}" for w in (2, 3, 4)))
    for name, digs in sources.items():
        row = []
        for w in (2, 3, 4):
            meas, exp = block_recurrence(digs, w)
            row.append(f"{meas:.3f}/{exp:.3f}")
        print(f"{name:>17} " + " ".join(row))
    print("(each cell: measured / chance-expectation)")

    print("\n--- corr-dim of 6-digit window vectors (space dim = 6) ---")
    for name, digs in sources.items():
        wins = np.array([digs[i:i + 6] for i in
                         range(0, len(digs) - 6, 12)], dtype=float) / 9.0
        diff = wins[:, None, :] - wins[None, :, :]
        d = np.sqrt((diff ** 2).sum(-1))
        iu = np.triu_indices(len(wins), 1)
        dp = d[iu[0], iu[1]]
        qs = np.geomspace(1, 99, 24)
        eps = np.percentile(dp, qs)
        C = np.array([(dp <= e).mean() for e in eps])
        m = (C > 0.02) & (C < 0.90)
        if dp.max() < 1e-9 or m.sum() < 5:
            print(f"{name:>17} nu = DEGENERATE (zero-spread -> periodic)")
            continue
        nu = np.polyfit(np.log(eps[m]), np.log(C[m]), 1)[0]
        print(f"{name:>17} nu = {float(nu):.2f}   (max possible 6)")
