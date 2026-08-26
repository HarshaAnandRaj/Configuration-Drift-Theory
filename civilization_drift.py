"""civilization_drift.py
The mutation-rate equivalent for a CIVILIZATION.

Mapping:
  carrier (G)      = a mind / book / institution that holds one practice
  practice         = a configuration in cultural space (effectively infinite)
  inheritance      = copying from another carrier (rhyme preservation)
  gamma > 0        = INNOVATION: minting a practice never held before
  implicit g < 0   = ORTHODOXY-GRIND: reversion toward one canonical practice
                     (Life's dissipation wearing institutions)

Dynamics per generation: copy (w.p. c) -> innovate (w.p. eps) -> grind
(revert to canonical, w.p. delta).

REGISTERED PREDICTIONS:
  P1  eps=delta=0 => pure haploid Wright-Fisher: time-to-monoculture linear
      in G (external anchor against published math).
  P2  collapse/sustain boundary in (eps, delta) space sits near eps ~ delta.
  P3  idea-burst injected into a collapsed HIGH-delta civilization dies;
      the same burst with delta lowered survives -> flip the grind, not just
      add ideas.
  P4  under pure conformity, practice-diversity decays exponentially
      (civilizational heterozygosity law).
"""

import numpy as np


def diversity(prac):
    s = np.sort(prac, axis=1)
    return (s[:, 1:] != s[:, :-1]).sum(1) + 1


def civ_run(G=400, reps=60, gens=2000, c=0.8, eps=0.0, delta=0.0,
            seed=0, init_half=False, record="late_div"):
    rng = np.random.default_rng(seed)
    if init_half:
        prac = np.zeros((reps, G), dtype=np.int64)
        prac[:, G // 2:] = 1
    else:
        prac = rng.integers(1, 1000, size=(reps, G))
    next_id = 1000
    lock_t = np.full(reps, -1)
    recs = []
    for t in range(gens):
        # 1. inheritance: w.p. c adopt a random donor's practice
        don = rng.integers(0, G, size=(reps, G))
        src = prac[np.arange(reps)[:, None], don]
        cm = rng.random((reps, G)) < c
        prac = np.where(cm, src, prac)
        # 2. innovation: mint never-held practices
        im = rng.random((reps, G)) < eps
        n = int(im.sum())
        if n:
            prac[im] = np.arange(next_id, next_id + n)
            next_id += n
        # 3. orthodoxy grind: revert to canonical 0
        gm = rng.random((reps, G)) < delta
        prac[gm] = 0

        dvs = diversity(prac)
        if record == "lock" and np.any((dvs <= 1) & (lock_t < 0)):
            lock_t[(dvs <= 1) & (lock_t < 0)] = t
        if record == "late_div" and t >= gens // 2:
            recs.append(dvs.copy())
    if record == "lock":
        return lock_t
    return np.array(recs).mean(axis=0)


if __name__ == "__main__":
    import math

    print("=========== REGISTERED PREDICTIONS ===========")
    print("P1 pure-copying monoculture time linear in G (Wright-Fisher anchor)")
    print("P2 collapse/sustain boundary near eps ~ delta")
    print("P3 idea-burst into collapsed+orthodox civ dies; with grind")
    print("   lowered, it survives")
    print("P4 exponential diversity decay under pure conformity")
    print()

    print("--- P1: pure copying, half-half start, time to monoculture ---")
    print(f"{'G':>5} {'theory 2Gln2':>13} {'median sim':>11} {'ratio':>7}")
    for G in (100, 200, 400):
        lt = civ_run(G=G, reps=120, gens=int(6 * G), c=1.0,
                     init_half=True, record="lock", seed=G)
        fin = np.where(lt < 0, 6 * G, lt)
        med = float(np.median(fin))
        th = 2 * G * math.log(2)
        print(f"{G:>5} {th:>13.1f} {med:>11.1f} {med/th:>7.3f}")

    print("\n--- P2/P4: phase grid, G=400 (late diversity, mean over reps) ---")
    deltas = [0.0, 0.001, 0.003, 0.01, 0.03]
    epss = [0.0003, 0.001, 0.003, 0.01, 0.03]
    hdr = "delta\\eps " + "".join(f"{e:>9}" for e in epss)
    print(hdr)
    for dl in deltas:
        row = []
        for e in epss:
            dv = civ_run(G=400, reps=60, gens=2000, c=0.8,
                         eps=e, delta=dl, seed=100 + int(dl * 1e6) + int(e * 1e6))
            row.append(float(dv.mean()))
        tag = "*" if dl == 0.0 else f"{dl:.3f}"
        print(f"{tag:>9} " + "".join(f"{v:>9.1f}" for v in row))
    print("(rows: grind delta; cols: innovation eps; '*' = no grind)")
    print("boundary: sustained side = diversity >> 2")

    print("\n--- P3: idea-burst rescue test ---")
    # establish collapsed orthodox civilization
    base = []
    for r in range(20):
        p = civ_run(G=400, reps=1, gens=2500, c=0.8, eps=0.0002,
                    delta=0.03, seed=900 + r)
        base.append(p[0])
    print(f"pre-burst diversity (should be ~collapsed): "
          f"{float(np.mean([b.mean() for b in base])):.2f}")

    def rescue(delta_after, label):
        finals = []
        for r in range(20):
            rng = np.random.default_rng(2000 + r)
            prac = np.full((1, 400), 0, dtype=np.int64)
            prac[0, :50] = np.arange(5000, 5050)          # the burst
            nxt = 6000
            for t in range(800):
                don = rng.integers(0, 400, size=(1, 400))
                src = prac[0, don[0]].reshape(1, 400)
                cm = rng.random((1, 400)) < 0.8
                prac = np.where(cm, src, prac)
                im = rng.random((1, 400)) < 0.003          # modest ongoing eps
                n = int(im.sum())
                if n:
                    prac[im] = np.arange(nxt, nxt + n)
                    nxt += n
                gm = rng.random((1, 400)) < delta_after
                prac[gm] = 0
            finals.append(int(diversity(prac)[0]))
        print(f"{label}: final diversity mean "
              f"{float(np.mean(finals)):.1f} (of 400 carriers)")

    rescue(0.03, "burst + grind kept (delta=.03)")
    rescue(0.001, "burst + grind lowered (delta=.001)")

    print("\n--- P4: diversity decay under PURE conformity (eps=0, delta=.01) ---")
    G = 400
    rng = np.random.default_rng(55)
    prac = rng.integers(1, 10000, size=(60, G))
    marks = [0, 50, 150, 400, 1000, 2000]
    outs = []
    t = 0
    for target in marks[1:]:
        while t < target:
            don = rng.integers(0, G, size=(60, G))
            src = prac[np.arange(60)[:, None], don]
            cm = rng.random((60, G)) < 0.8
            prac = np.where(cm, src, prac)
            gm = rng.random((60, G)) < 0.01
            prac[gm] = 0
            t += 1
        outs.append(round(float(diversity(prac).mean()), 1))
    print("gen:", marks)
    print("diversity:", outs)
